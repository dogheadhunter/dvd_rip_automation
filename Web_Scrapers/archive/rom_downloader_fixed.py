#!/usr/bin/env python3
"""
🎮 ROM Downloader with Proxy Support - FIXED VERSION
===================================================

This script downloads ROM files from your scraped ROM lists using the modern proxy scraper.
It's specifically designed to work with your ROM website scraper output files.

Features:
- Parses your ROM txt files from scraped_data folder
- Downloads actual ROM files (not just web pages)  
- Uses proxy rotation to avoid being blocked
- SSL certificate handling for self-signed certificates
- Organizes downloads by console
- Resume capability for interrupted downloads
- Progress tracking and size estimates
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
                 concurrent_downloads: int = 3,
                 timeout: int = 300):  # 5 minutes timeout for large files
        self.proxy_count = proxy_count
        self.concurrent_downloads = concurrent_downloads
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
    
    async def download_rom(self, rom: Dict, output_dir: Path, session: aiohttp.ClientSession) -> bool:
        """Download a single ROM file with resume capability"""
        download_path = self.get_download_path(rom, output_dir)
        
        # Check if file already exists and get size
        resume_pos = 0
        if download_path.exists():
            resume_pos = download_path.stat().st_size
            print(f"📁 Found partial download: {rom['name']} ({resume_pos} bytes)")
        
        try:
            # Get proxy for this download
            proxy = None
            if self.proxy_rotator and self.proxy_rotator.proxies:
                proxy_dict = self.proxy_rotator.get_next_proxy()
                if proxy_dict:
                    proxy = proxy_dict['http']
            
            # Set up headers for resume
            headers = self.proxy_rotator.get_random_headers() if self.proxy_rotator else {}
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'
            
            proxy_info = f" via {proxy}" if proxy else " direct"
            print(f"⬇️  Downloading: {rom['name']}{proxy_info}")
            
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
                if content_length:
                    total_size = int(content_length)
                    if resume_pos > 0:
                        total_size += resume_pos
                    size_mb = total_size / (1024 * 1024)
                    print(f"📦 Size: {size_mb:.1f} MB")
                
                # Download with progress
                mode = 'ab' if resume_pos > 0 else 'wb'
                async with aiofiles.open(download_path, mode) as f:
                    downloaded = resume_pos
                    chunk_size = 1024 * 1024  # 1MB chunks
                    
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress every 10MB
                        if downloaded % (10 * 1024 * 1024) < chunk_size:
                            if content_length:
                                progress = (downloaded / total_size) * 100
                                print(f"  📊 Progress: {downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB ({progress:.1f}%)")
                            else:
                                print(f"  📊 Downloaded: {downloaded/(1024*1024):.1f} MB")
                
                self.download_stats['completed'] += 1
                self.download_stats['total_size'] += downloaded
                print(f"✅ Completed: {rom['name']}")
                return True
                
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout downloading {rom['name']}")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading {rom['name']}: {e}")
            return False
    
    async def download_roms_batch(self, roms: List[Dict], output_dir: Path):
        """Download ROMs in batches with concurrency control"""
        semaphore = asyncio.Semaphore(self.concurrent_downloads)
        
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
                    success = await self.download_rom(rom, output_dir, session)
                    if not success:
                        self.download_stats['failed'] += 1
                    
                    # Random delay between downloads
                    await asyncio.sleep(random.uniform(1, 3))
        
        # Execute downloads
        tasks = [download_with_semaphore(rom) for rom in roms]
        await asyncio.gather(*tasks, return_exceptions=True)
    
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
        print("🎮 ROM DOWNLOADER - Enhanced with SSL Certificate Support")
        print("="*60)
        print("Features:")
        print("- SSL certificate handling for self-signed certificates")
        print("- Enhanced proxy sources (13 GitHub sources)")
        print("- Resume capability for interrupted downloads")
        print("- Progress tracking and concurrent downloads")
        print("="*60)
        
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
        print(f"\n🚀 Starting downloads with {self.concurrent_downloads} concurrent connections...")
        print("📡 SSL Certificate verification disabled for ROM hosting sites")
        
        start_time = time.time()
        await self.download_roms_batch(all_roms, output_dir)
        end_time = time.time()
        
        # Print final statistics
        self.print_stats()
        print(f"⏱️  Total Time: {end_time - start_time:.1f} seconds")


async def main():
    """Main entry point"""
    downloader = ROMDownloader(proxy_count=15, concurrent_downloads=3, timeout=300)
    await downloader.run_interactive()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Download cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
