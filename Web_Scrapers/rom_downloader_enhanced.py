#!/usr/bin/env python3
"""
🎮 ROM Downloader with Enhanced Anti-Throttling - Phase 1 Complete
==================================================================

This is the enhanced ROM downloader with Phase 1 improvements:
- Better proxy rotation and logging
- Enhanced header randomization 
- Improved error handling and debugging

Features:
- Beautiful progress bars with download speeds and ETAs
- Enhanced proxy rotation with detailed logging
- Better fallback handling when proxies fail
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

class EnhancedROMDownloader:
    """Enhanced ROM downloader with anti-throttling improvements"""
    
    def __init__(self, 
                 proxy_count: int = 15,
                 sequential_mode: bool = True,
                 delay_range: tuple = (2, 8),
                 timeout: int = 300):
        self.proxy_count = proxy_count
        self.sequential_mode = sequential_mode
        self.delay_range = delay_range
        self.timeout = timeout
        self.proxy_rotator = None
        self.download_stats = {
            'completed': 0,
            'failed': 0,
            'total_size': 0,
            'proxy_used': 0,
            'direct_used': 0
        }
        
        # Set up enhanced logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rom_downloader_enhanced.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced ROM Downloader initialized")
    
    def find_rom_files(self, scraped_data_dir: Path = None) -> Dict[str, List[Path]]:
        """Find all ROM txt files in the scraped_data directory"""
        if scraped_data_dir is None:
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
                    if file.stat().st_size > 0:
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
                
                if not line or line.startswith('Search:') or line.startswith('Total matches:') or line.startswith('Generated:'):
                    continue
                    
                if line.endswith('.zip') and not line.startswith('http'):
                    current_name = line
                    
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
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def get_download_path(self, rom: Dict, output_dir: Path) -> Path:
        """Get the full download path for a ROM"""
        console_dir = output_dir / rom['console']
        console_dir.mkdir(parents=True, exist_ok=True)
        return console_dir / rom['local_filename']
    
    async def download_rom_enhanced(self, rom: Dict, output_dir: Path, session: aiohttp.ClientSession, overall_pbar: tqdm = None) -> bool:
        """Enhanced ROM download with improved proxy handling and logging"""
        download_path = self.get_download_path(rom, output_dir)
        
        # Check for existing partial download
        resume_pos = 0
        if download_path.exists():
            resume_pos = download_path.stat().st_size
            print(f"📁 Found partial download: {rom['name']} ({resume_pos:,} bytes)")
        
        try:
            # PHASE 1 ENHANCEMENT: Better proxy selection and logging
            proxy = None
            proxy_used = "direct"
            connection_type = "direct"
            
            if self.proxy_rotator and self.proxy_rotator.proxies:
                proxy_dict = self.proxy_rotator.get_next_proxy()
                if proxy_dict and 'http' in proxy_dict:
                    proxy = proxy_dict['http']
                    proxy_used = proxy
                    connection_type = "proxy"
                    self.logger.info(f"✓ Selected proxy: {proxy} for {rom['name']}")
                    self.download_stats['proxy_used'] += 1
                else:
                    self.logger.warning(f"⚠ Proxy rotator returned invalid proxy for {rom['name']}")
                    self.download_stats['direct_used'] += 1
            else:
                if not self.proxy_rotator:
                    self.logger.info(f"ℹ No proxy rotator configured for {rom['name']}")
                elif not self.proxy_rotator.proxies:
                    self.logger.warning(f"⚠ Proxy rotator has no working proxies for {rom['name']}")
                self.download_stats['direct_used'] += 1
            
            # Enhanced headers with fallback
            headers = {}
            if self.proxy_rotator:
                headers = self.proxy_rotator.get_enhanced_random_headers()
                self.logger.debug(f"Using randomized headers: {list(headers.keys())}")
            else:
                # Fallback realistic headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'
            
            # Enhanced display showing actual connection info
            proxy_display = f" via {proxy_used}" if connection_type == "proxy" else " direct"
            print(f"⬇️  Downloading: {rom['name']}{proxy_display}")
            self.logger.info(f"Starting download: {rom['name']} using {connection_type}: {proxy_used}")
            
            # Prepare request with proper proxy handling
            request_kwargs = {
                'headers': headers,
                'timeout': aiohttp.ClientTimeout(total=self.timeout)
            }
            
            if proxy and connection_type == "proxy":
                request_kwargs['proxy'] = proxy
            
            async with session.get(rom['url'], **request_kwargs) as response:
                self.logger.info(f"Response: {response.status} for {rom['name']} via {connection_type}")
                
                if response.status not in [200, 206]:
                    self.logger.warning(f"HTTP {response.status} for {rom['name']}")
                    return False
                
                # File size calculation
                content_length = response.headers.get('content-length')
                total_size = None
                if content_length:
                    total_size = int(content_length)
                    if resume_pos > 0:
                        total_size += resume_pos
                    size_mb = total_size / (1024 * 1024)
                    print(f"📦 Size: {size_mb:.1f} MB")
                
                # Progress bar for individual download
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
                
                # Download with progress tracking
                mode = 'ab' if resume_pos > 0 else 'wb'
                async with aiofiles.open(download_path, mode) as f:
                    downloaded = resume_pos
                    chunk_size = 1024 * 1024  # 1MB chunks
                    last_update_time = time.time()
                    last_downloaded = downloaded
                    
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        chunk_len = len(chunk)
                        file_pbar.update(chunk_len)
                        
                        # Speed calculation
                        current_time = time.time()
                        if current_time - last_update_time >= 1.0:
                            speed = (downloaded - last_downloaded) / (current_time - last_update_time)
                            file_pbar.set_postfix({
                                'speed': f"{speed/(1024*1024):.1f}MB/s",
                                'eta': f"{((total_size - downloaded) / speed):.0f}s" if total_size and speed > 0 else "?"
                            })
                            last_update_time = current_time
                            last_downloaded = downloaded
                
                file_pbar.close()
                self.download_stats['completed'] += 1
                self.download_stats['total_size'] += downloaded
                
                if overall_pbar:
                    overall_pbar.update(1)
                
                # Enhanced completion message
                print(f"✅ Completed: {rom['name']} ({downloaded:,} bytes via {connection_type})")
                self.logger.info(f"Successfully downloaded {rom['name']} ({downloaded:,} bytes via {connection_type})")
                return True
                
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout downloading {rom['name']}")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading {rom['name']}: {e}")
            return False
    
    def print_enhanced_stats(self):
        """Print enhanced download statistics"""
        print("\n" + "="*60)
        print("📊 ENHANCED DOWNLOAD STATISTICS")
        print("="*60)
        print(f"✅ Completed: {self.download_stats['completed']}")
        print(f"❌ Failed: {self.download_stats['failed']}")
        print(f"📦 Total Downloaded: {self.download_stats['total_size']/(1024*1024*1024):.2f} GB")
        print(f"🌐 Proxy Downloads: {self.download_stats['proxy_used']}")
        print(f"🔗 Direct Downloads: {self.download_stats['direct_used']}")
        
        if self.download_stats['proxy_used'] + self.download_stats['direct_used'] > 0:
            proxy_percentage = (self.download_stats['proxy_used'] / (self.download_stats['proxy_used'] + self.download_stats['direct_used'])) * 100
            print(f"📈 Proxy Usage Rate: {proxy_percentage:.1f}%")
        
        print("="*60)
    
    async def run_quick_test(self, max_roms: int = 3):
        """Quick test mode for Phase 1 verification"""
        print("🧪 ENHANCED ROM DOWNLOADER - PHASE 1 TEST MODE")
        print("="*60)
        print("Features tested:")
        print("- Enhanced proxy selection and logging")
        print("- Better connection type tracking")
        print("- Improved error handling")
        print("="*60)
        
        # Find ROM files
        rom_files = self.find_rom_files()
        if not rom_files:
            print("❌ No ROM files found")
            return
        
        # Get first few ROMs for testing
        all_roms = []
        for console, files in rom_files.items():
            for file_path in files[:1]:  # One file per console
                roms = self.parse_rom_file(file_path)
                all_roms.extend(roms[:2])  # Max 2 ROMs per file
                if len(all_roms) >= max_roms:
                    break
            if len(all_roms) >= max_roms:
                break
        
        all_roms = all_roms[:max_roms]
        print(f"\n🎯 Testing with {len(all_roms)} ROMs")
        
        # Initialize proxies
        print("\n🔍 Finding working proxies...")
        self.proxy_rotator = ModernProxyRotator(proxy_count=5, timeout=8)
        try:
            working_proxies = await self.proxy_rotator.find_proxies_async()
            if working_proxies:
                print(f"✅ Found {len(working_proxies)} working proxies")
            else:
                print("⚠️  No working proxies found, testing direct connections only")
        except Exception as e:
            print(f"❌ Proxy discovery failed: {e}")
            
        # Test downloads
        output_dir = Path("ROM_Downloads_Test_Phase1")
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n🚀 Starting test downloads...")
        print(f"📁 Output directory: {output_dir.absolute()}")
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=3, ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        overall_pbar = tqdm(
            total=len(all_roms),
            desc="🎮 Test Progress",
            unit=" ROMs",
            ascii=True,
            colour='blue'
        )
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i, rom in enumerate(all_roms, 1):
                print(f"\n📥 [{i}/{len(all_roms)}] Testing: {rom['name']}")
                
                success = await self.download_rom_enhanced(rom, output_dir, session, overall_pbar)
                if not success:
                    self.download_stats['failed'] += 1
                
                # Update progress
                overall_pbar.set_postfix({
                    'completed': self.download_stats['completed'],
                    'failed': self.download_stats['failed'],
                    'proxy_used': self.download_stats['proxy_used'],
                    'direct_used': self.download_stats['direct_used']
                })
                
                # Short delay between test downloads
                if i < len(all_roms):
                    delay = random.uniform(1, 3)
                    print(f"⏳ Test delay: {delay:.1f}s")
                    await asyncio.sleep(delay)
        
        overall_pbar.close()
        self.print_enhanced_stats()
        print("\n🎉 Phase 1 test complete!")

async def main():
    """Main entry point"""
    downloader = EnhancedROMDownloader(proxy_count=10, sequential_mode=True, delay_range=(2, 8))
    
    # Check command line args for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        await downloader.run_quick_test()
    else:
        print("🎮 Enhanced ROM Downloader - Phase 1")
        print("Run with --test for quick verification")
        print("Full implementation coming in subsequent phases...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Download cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
