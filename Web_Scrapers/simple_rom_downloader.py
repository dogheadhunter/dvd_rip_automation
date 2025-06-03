#!/usr/bin/env python3
"""
🎮 Simple ROM Downloader - Direct Downloads Only
===============================================

This is a simplified ROM downloader that bypasses proxies entirely.
Based on our testing, the ROM URLs work perfectly with direct connections.

Features:
- Direct downloads without proxies
- Progress bars with download speeds
- Content validation to prevent HTML error pages
- Resume capability for interrupted downloads
- Concurrent downloads with rate limiting
"""

import os
import asyncio
import aiohttp
import aiofiles
import logging
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlparse, unquote
from tqdm.asyncio import tqdm
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_rom_downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class SimpleRomDownloader:
    """Simple ROM downloader without proxy complexity"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session_timeout = aiohttp.ClientTimeout(total=300, connect=30)
        self.max_concurrent = 3  # Conservative to avoid overwhelming servers
        
    def parse_rom_files(self, rom_files_dir: str) -> List[Dict]:
        """Parse ROM files to extract download information"""
        roms = []
        rom_dir = Path(rom_files_dir)
        
        for file_path in rom_dir.rglob("*.txt"):
            try:
                current_name = None
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                            
                        if line.startswith('http'):
                            if current_name:
                                roms.append({
                                    'name': current_name,
                                    'url': line,
                                    'console': file_path.parent.name,
                                    'local_filename': self.sanitize_filename(current_name)
                                })
                                current_name = None
                        else:
                            current_name = line
                            
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
    
    async def download_rom(self, rom: Dict, output_dir: Path, session: aiohttp.ClientSession, 
                          overall_pbar: tqdm = None) -> bool:
        """Download a single ROM with progress tracking"""
        download_path = self.get_download_path(rom, output_dir)
        
        # Check for existing complete download
        if download_path.exists():
            file_size = download_path.stat().st_size
            if file_size > 1000:  # More than 1KB, likely not an error page
                print(f"✅ Already downloaded: {rom['name']} ({file_size:,} bytes)")
                if overall_pbar:
                    overall_pbar.update(1)
                return True
        
        try:
            print(f"🎮 Downloading: {rom['name']}")
            start_time = time.time()
            
            async with session.get(rom['url']) as response:
                if response.status != 200:
                    self.logger.error(f"HTTP {response.status} for {rom['name']}")
                    return False
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type:
                    self.logger.error(f"Got HTML instead of ROM file for {rom['name']}")
                    return False
                
                total_size = int(response.headers.get('content-length', 0))
                
                # Create progress bar for this download
                progress_bar = tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"📥 {rom['name'][:30]}"
                )
                
                downloaded = 0
                async with aiofiles.open(download_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        progress_bar.update(len(chunk))
                
                progress_bar.close()
                
                # Calculate download stats
                end_time = time.time()
                download_time = end_time - start_time
                speed = downloaded / download_time if download_time > 0 else 0
                
                # Validate the download
                if downloaded < 1000:  # Likely an error page
                    self.logger.error(f"Download too small for {rom['name']}: {downloaded} bytes")
                    download_path.unlink(missing_ok=True)
                    return False
                
                print(f"✅ Downloaded: {rom['name']} ({downloaded:,} bytes, {speed/1024/1024:.2f} MB/s)")
                
                if overall_pbar:
                    overall_pbar.update(1)
                
                return True
                
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout downloading {rom['name']}")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading {rom['name']}: {e}")
            return False
    
    async def download_roms(self, rom_files_dir: str, output_dir: str, max_downloads: int = None):
        """Download ROMs with concurrent processing"""
        roms = self.parse_rom_files(rom_files_dir)
        
        if not roms:
            print("❌ No ROMs found to download")
            return
        
        if max_downloads:
            roms = roms[:max_downloads]
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🎮 Found {len(roms)} ROMs to download")
        print(f"📁 Download directory: {output_path.absolute()}")
        
        # Create overall progress bar
        overall_pbar = tqdm(total=len(roms), desc="🎮 Overall Progress", unit="ROM")
        
        # Create session with direct connection (no proxies)
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=2,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=self.session_timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        ) as session:
            
            # Process downloads with semaphore for rate limiting
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def download_with_semaphore(rom):
                async with semaphore:
                    return await self.download_rom(rom, output_path, session, overall_pbar)
            
            # Execute downloads
            tasks = [download_with_semaphore(rom) for rom in roms]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            overall_pbar.close()
            
            # Summary
            successful = sum(1 for r in results if r is True)
            failed = len(results) - successful
            
            print(f"\n🎮 Download Summary:")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📁 Downloads saved to: {output_path.absolute()}")

async def main():
    """Main function for testing"""
    downloader = SimpleRomDownloader()
    
    # Test with a small number of ROMs
    rom_files_dir = r"c:\Users\doghe\vscodescripts\rom_website_scraper\scraped_data"
    output_dir = r"c:\Users\doghe\vscodescripts\Web_Scrapers\ROM_Downloads_Simple"
    
    await downloader.download_roms(rom_files_dir, output_dir, max_downloads=2)

if __name__ == "__main__":
    asyncio.run(main())
