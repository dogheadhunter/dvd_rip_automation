#!/usr/bin/env python3
"""
🎮 ROM Downloader with Progress Bars & Proxy Support - ENHANCED VERSION
=====================================================================

This script downloads ROM files from your scraped ROM lists using the modern proxy scraper.
It's specifically designed to work with your ROM website scraper output files.

Features:
- Beautiful progress bars with download speeds and ETAs
- Parses your ROM txt files from scraped_data folder
- Downloads actual ROM files (not just web pages)  
- Uses proxy rotation to avoid being blocked
- SSL certificate handling for self-signed certificates
- Organizes downloads by console
- Resume capability for interrupted downloads
- Sequential & concurrent download modes
"""

import os
import sys
import time
import asyncio
import aiohttp
import aiofiles
import logging
import ssl
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse, unquote
import random
from tqdm.asyncio import tqdm

# Add the working_scrapers directory to path to import our proxy tools
sys.path.append(str(Path(__file__).parent / "working_scrapers"))

try:
    from modern_proxy_scraper import ModernProxyRotator
except ImportError:
    print("❌ Error: Could not import modern proxy scraper")
    print("Make sure you're running this from the Web_Scrapers directory")
    sys.exit(1)

class ROMDownloader:
    """Downloads ROM files with proxy support and resume capability"""
    
    def __init__(self, 
                 proxy_count: int = 10,
                 sequential_mode: bool = True,  # New: Sequential downloads by default
                 delay_range: tuple = (2, 8),  # New: Delay between downloads (min, max) seconds
                 timeout: int = 300):  # 5 minutes timeout for large files
        self.proxy_count = proxy_count
        self.sequential_mode = sequential_mode
        self.delay_range = delay_range
        self.timeout = timeout
        self.proxy_rotator = None
        self.download_stats = {
            'completed': 0,
            'failed': 0,
            'total_size': 0
        }
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rom_downloader.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def find_rom_files(self, scraped_data_dir: Path = None) -> Dict[str, List[Path]]:
        """Find all ROM txt files in the scraped_data directory"""
        if scraped_data_dir is None:
            # Look for scraped_data directory in parent directories
            current_dir = Path(__file__).parent
            scraped_data_dir = current_dir.parent / "rom_website_scraper" / "scraped_data"
        
        rom_files = {}
        
        if not scraped_data_dir.exists():
            print(f"❌ Scraped data directory not found: {scraped_data_dir}")
            return rom_files
        
        for console_dir in scraped_data_dir.iterdir():
            if console_dir.is_dir():
                console_files = []
                for file in console_dir.glob("*.txt"):
                    if file.stat().st_size > 0:  # Only non-empty files
                        console_files.append(file)
                
                if console_files:
                    rom_files[console_dir.name] = console_files
                    print(f"📁 Found {len(console_files)} ROM files for {console_dir.name}")
        
        return rom_files
    
    def parse_rom_file(self, file_path: Path) -> List[Dict]:
        """Parse a ROM txt file and extract download information"""
        roms = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            current_name = None
            for line in lines:
                line = line.strip()
                
                # Skip headers and empty lines
                if not line or line.startswith('Search:') or line.startswith('Total matches:') or line.startswith('Generated:'):
                    continue
                    
                # Check if this is a filename line (ends with .zip)
                if line.endswith('.zip') and not line.startswith('http'):
                    current_name = line
                    
                # Check if this is a URL line
                elif line.startswith('http') and current_name:
                    roms.append({
                        'name': current_name,
                        'url': line,
                        'console': file_path.parent.name,
                        'local_filename': self.sanitize_filename(current_name)
                    })
                    current_name = None
                    
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            
        return roms
    
    def sanitize_filename(self, filename: str) -> str:
        """Clean filename for safe storage"""
        # Remove/replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def get_download_path(self, rom: Dict, output_dir: Path) -> Path:
        """Get the full download path for a ROM"""
        console_dir = output_dir / rom['console']
        console_dir.mkdir(parents=True, exist_ok=True)
        return console_dir / rom['local_filename']
    
    async def download_rom(self, rom: Dict, output_dir: Path, session: aiohttp.ClientSession, overall_pbar: tqdm = None) -> bool:
        """Download a single ROM file with resume capability and progress bar"""
        download_path = self.get_download_path(rom, output_dir)
        
        # Check if file already exists and get size
        resume_pos = 0
        if download_path.exists():
            resume_pos = download_path.stat().st_size
            print(f"📁 Found partial download: {rom['name']} ({resume_pos:,} bytes)")
          try:
            # Get proxy for this download - ENHANCED: Better proxy selection and logging
            proxy = None
            proxy_used = "direct"
            if self.proxy_rotator and self.proxy_rotator.proxies:
                proxy_dict = self.proxy_rotator.get_next_proxy()
                if proxy_dict and 'http' in proxy_dict:
                    proxy = proxy_dict['http']
                    proxy_used = proxy
                    self.logger.info(f"Selected proxy: {proxy} for {rom['name']}")
                else:
                    self.logger.warning(f"Proxy rotator returned invalid proxy for {rom['name']}")
            else:
                if not self.proxy_rotator:
                    self.logger.info(f"No proxy rotator configured for {rom['name']}")
                elif not self.proxy_rotator.proxies:
                    self.logger.warning(f"Proxy rotator has no working proxies for {rom['name']}")
            
            # Set up headers for resume
            headers = self.proxy_rotator.get_random_headers() if self.proxy_rotator else {}
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'
            
            # Enhanced display with actual proxy info
            proxy_info = f" via {proxy_used}" if proxy_used != "direct" else " direct"
            print(f"⬇️  Downloading: {rom['name']}{proxy_info}")
            self.logger.info(f"Starting download: {rom['name']} using connection: {proxy_used}")
            
            async with session.get(
                rom['url'], 
                headers=headers, 
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                
                if response.status not in [200, 206]:  # 206 = Partial Content for resume
                    self.logger.warning(f"HTTP {response.status} for {rom['name']}")
                    return False
                
                # Get file size info
                content_length = response.headers.get('content-length')
                total_size = None
                if content_length:
                    total_size = int(content_length)
                    if resume_pos > 0:
                        total_size += resume_pos
                    size_mb = total_size / (1024 * 1024)
                    print(f"📦 Size: {size_mb:.1f} MB")
                
                # Create progress bar for this specific download
                file_pbar = tqdm(
                    total=total_size,
                    initial=resume_pos,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"📥 {rom['name'][:30]}...",
                    leave=False,
                    ascii=True,
                    colour='green'
                )
                
                # Download with progress
                mode = 'ab' if resume_pos > 0 else 'wb'
                async with aiofiles.open(download_path, mode) as f:
                    downloaded = resume_pos
                    chunk_size = 1024 * 1024  # 1MB chunks
                    last_update_time = time.time()
                    last_downloaded = downloaded
                    
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        downloaded += len(chunk)
                          # Update progress bars
                        chunk_len = len(chunk)
                        file_pbar.update(chunk_len)
                        # Note: overall_pbar will be updated per ROM completion, not per chunk
                        
                        # Update speed calculation every second
                        current_time = time.time()
                        if current_time - last_update_time >= 1.0:
                            speed = (downloaded - last_downloaded) / (current_time - last_update_time)
                            file_pbar.set_postfix({
                                'speed': f"{speed/(1024*1024):.1f}MB/s",                            'eta': f"{((total_size - downloaded) / speed):.0f}s" if total_size and speed > 0 else "?"
                            })
                            last_update_time = current_time
                            last_downloaded = downloaded
                
                file_pbar.close()
                self.download_stats['completed'] += 1
                self.download_stats['total_size'] += downloaded
                
                # Update overall progress bar for ROM completion
                if overall_pbar:
                    overall_pbar.update(1)
                  print(f"✅ Completed: {rom['name']} (via {proxy_used})")
                self.logger.info(f"Successfully downloaded {rom['name']} using {proxy_used}")
                return True
                
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout downloading {rom['name']}")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading {rom['name']}: {e}")
            return False
    
    async def download_roms_sequential(self, roms: List[Dict], output_dir: Path):
        """Download ROMs one at a time with polite delays to avoid throttling"""
        print(f"🐌 Using sequential downloads with {self.delay_range[0]}-{self.delay_range[1]}s delays")
        
        # Create SSL context that allows self-signed certificates  
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(
            limit=10,  # Reduced connection limit
            limit_per_host=3,  # Much lower per-host limit
            ssl=ssl_context
        )
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        # Create overall progress bar
        overall_pbar = tqdm(
            total=len(roms),
            desc="🎮 Overall Progress",
            unit=" ROMs",
            position=0,
            leave=True,
            ascii=True,
            colour='blue'
        )
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            
            for i, rom in enumerate(roms, 1):
                print(f"\n📥 [{i}/{len(roms)}] Processing: {rom['name']}")
                
                success = await self.download_rom(rom, output_dir, session, overall_pbar)
                if not success:
                    self.download_stats['failed'] += 1
                
                # Update overall progress (ROM completed)
                overall_pbar.set_postfix({
                    'completed': self.download_stats['completed'],
                    'failed': self.download_stats['failed'],
                    'size': f"{self.download_stats['total_size']/(1024*1024*1024):.2f}GB"
                })
                
                # Polite delay between downloads (except for the last one)
                if i < len(roms):
                    delay = random.uniform(self.delay_range[0], self.delay_range[1])
                    print(f"⏳ Waiting {delay:.1f}s before next download...")
                    await asyncio.sleep(delay)
        
        overall_pbar.close()
        print("\n✨ Sequential downloads completed!")

    async def download_roms_batch(self, roms: List[Dict], output_dir: Path):
        """Download ROMs - use sequential mode by default to avoid throttling"""
        if self.sequential_mode:
            await self.download_roms_sequential(roms, output_dir)
        else:
            # Legacy concurrent mode (may trigger throttling)
            await self.download_roms_concurrent(roms, output_dir)
    
    async def download_roms_concurrent(self, roms: List[Dict], output_dir: Path):
        """Download ROMs in batches with concurrency control (legacy mode)"""
        concurrent_downloads = 2  # Reduced from 3 to be more polite
        semaphore = asyncio.Semaphore(concurrent_downloads)
        
        # Create overall progress bar for concurrent mode
        overall_pbar = tqdm(
            total=len(roms),
            desc="🎮 Overall Progress (Concurrent)",
            unit=" ROMs",
            position=0,
            leave=True,
            ascii=True,
            colour='yellow'
        )
        
        async def download_with_semaphore(rom):
            async with semaphore:
                # Create SSL context that allows self-signed certificates  
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                connector = aiohttp.TCPConnector(
                    limit=100, 
                    limit_per_host=10,
                    ssl=ssl_context  # Use our custom SSL context
                )
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout
                ) as session:
                    success = await self.download_rom(rom, output_dir, session, overall_pbar)
                    if not success:
                        self.download_stats['failed'] += 1
                    
                    # Update overall progress
                    overall_pbar.set_postfix({
                        'completed': self.download_stats['completed'],
                        'failed': self.download_stats['failed'],
                        'size': f"{self.download_stats['total_size']/(1024*1024*1024):.2f}GB"
                    })
                    
                    # Random delay between downloads
                    await asyncio.sleep(random.uniform(2, 5))  # Increased delay
        
        # Execute downloads
        tasks = [download_with_semaphore(rom) for rom in roms]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        overall_pbar.close()
        print("\n✨ Concurrent downloads completed!")
    
    def print_stats(self):
        """Print download statistics"""
        print("\n" + "="*50)
        print("📊 DOWNLOAD STATISTICS")
        print("="*50)
        print(f"✅ Completed: {self.download_stats['completed']}")
        print(f"❌ Failed: {self.download_stats['failed']}")
        print(f"📦 Total Downloaded: {self.download_stats['total_size']/(1024*1024*1024):.2f} GB")
        print("="*50)
    
    async def run_interactive(self):
        """Interactive ROM downloader interface"""
        print("🎮 ROM DOWNLOADER - Enhanced with Progress Bars & SSL Support")
        print("="*65)
        print("Features:")
        print("- Beautiful progress bars with download speeds and ETAs")
        print("- SSL certificate handling for self-signed certificates")
        print("- Enhanced proxy sources (13 GitHub sources)")
        print("- Resume capability for interrupted downloads")
        print("- Sequential & concurrent download modes")
        print("="*65)
        
        # Find ROM files
        rom_files = self.find_rom_files()
        if not rom_files:
            print("❌ No ROM files found in scraped_data directory")
            return
        
        print(f"\n📁 Found ROM collections for {len(rom_files)} consoles:")
        console_list = list(rom_files.keys())
        for i, console in enumerate(console_list, 1):
            file_count = len(rom_files[console])
            # Count total ROMs in all files for this console
            total_roms = 0
            for file_path in rom_files[console]:
                roms = self.parse_rom_file(file_path)
                total_roms += len(roms)
            print(f"{i}. {console} ({file_count} files, ~{total_roms} ROMs)")
        
        # Get console choice
        while True:
            try:
                choice = input(f"\nSelect console (1-{len(console_list)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    return
                
                console_idx = int(choice) - 1
                if 0 <= console_idx < len(console_list):
                    selected_console = console_list[console_idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(console_list)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
        
        # Show files for selected console
        selected_files = rom_files[selected_console]
        print(f"\n📂 ROM files for {selected_console}:")
        for i, file_path in enumerate(selected_files, 1):
            roms = self.parse_rom_file(file_path)
            print(f"{i}. {file_path.name} ({len(roms)} ROMs)")
        
        # Get file choice
        while True:
            try:
                choice = input(f"\nSelect ROM file (1-{len(selected_files)}) or 'all' for all files: ").strip()
                if choice.lower() == 'all':
                    files_to_process = selected_files
                    break
                
                file_idx = int(choice) - 1
                if 0 <= file_idx < len(selected_files):
                    files_to_process = [selected_files[file_idx]]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(selected_files)} or 'all'")
            except ValueError:
                print("Please enter a valid number or 'all'")
        
        # Parse selected files
        all_roms = []
        for file_path in files_to_process:
            roms = self.parse_rom_file(file_path)
            all_roms.extend(roms)
            print(f"📝 Parsed {len(roms)} ROMs from {file_path.name}")
        
        if not all_roms:
            print("❌ No ROMs found in selected files")
            return
        
        print(f"\n🎯 Total ROMs to download: {len(all_roms)}")
        
        # Set up output directory
        output_dir = Path("ROM_Downloads_Test")
        output_dir.mkdir(exist_ok=True)
        print(f"📁 Downloads will be saved to: {output_dir.absolute()}")
        
        # Ask about download mode
        print("\n⚡ Download Mode Options:")
        print("1. Sequential (Recommended) - One ROM at a time with polite delays")
        print("2. Concurrent (Legacy) - Multiple downloads at once (may trigger throttling)")
        
        while True:
            mode_choice = input("Select download mode (1-2): ").strip()
            if mode_choice == '1':
                self.sequential_mode = True
                break
            elif mode_choice == '2':
                self.sequential_mode = False
                print("⚠️  Warning: Concurrent mode may trigger heavy throttling!")
                break
            else:
                print("Please enter 1 or 2")
        
        if self.sequential_mode:
            # Ask about delay settings
            print(f"\n⏳ Current delay between downloads: {self.delay_range[0]}-{self.delay_range[1]} seconds")
            custom_delay = input("Use custom delay range? (y/n): ").strip().lower() == 'y'
            
            if custom_delay:
                while True:
                    try:
                        min_delay = float(input("Minimum delay (seconds): "))
                        max_delay = float(input("Maximum delay (seconds): "))
                        if min_delay >= 0 and max_delay >= min_delay:
                            self.delay_range = (min_delay, max_delay)
                            break
                        else:
                            print("Invalid range. Max must be >= min and both >= 0")
                    except ValueError:
                        print("Please enter valid numbers")
        
        # Ask about proxy usage
        use_proxies = input("\n🌐 Use proxies for downloading? (y/n): ").strip().lower() == 'y'
        
        if use_proxies:
            print(f"🔍 Finding working proxies (enhanced with 13 GitHub sources)...")
            self.proxy_rotator = ModernProxyRotator(proxy_count=self.proxy_count, timeout=10)
            working_proxies = await self.proxy_rotator.find_proxies_async()
            
            if working_proxies:
                print(f"✅ Found {len(working_proxies)} working proxies")
            else:
                print("⚠️  No working proxies found, continuing with direct connections")
                self.proxy_rotator = None
        
        # Start downloads
        if self.sequential_mode:
            print(f"\n🚀 Starting sequential downloads with {self.delay_range[0]}-{self.delay_range[1]}s delays...")
        else:
            print(f"\n🚀 Starting concurrent downloads (legacy mode)...")
        print("📡 SSL Certificate verification disabled for ROM hosting sites")
        print("📊 You'll see beautiful progress bars with speeds and ETAs!")
        
        start_time = time.time()
        await self.download_roms_batch(all_roms, output_dir)
        end_time = time.time()
        
        # Print final statistics
        self.print_stats()
        print(f"⏱️  Total Time: {end_time - start_time:.1f} seconds")


async def main():
    """Main entry point"""
    downloader = ROMDownloader(proxy_count=15, sequential_mode=True, delay_range=(2, 8), timeout=300)
    await downloader.run_interactive()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Download cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
