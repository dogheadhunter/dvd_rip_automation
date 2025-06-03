#!/usr/bin/env python3
"""
🎮 Phase 4 Anti-Throttling ROM Downloader with cloudscraper
===========================================================

This ROM downloader uses cloudscraper to bypass advanced anti-bot protection
that causes throttling after initial fast downloads. cloudscraper automatically
handles Cloudflare challenges and provides perfect browser impersonation.

Features:
- ✅ cloudscraper for advanced anti-bot bypass
- ✅ Session rotation to prevent fingerprinting
- ✅ Perfect browser impersonation
- ✅ Automatic challenge solving
- ✅ Built-in rate limiting intelligence
"""

import os
import sys
import time
import asyncio
import aiofiles
import logging
import ssl
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse, unquote
import random
from tqdm.asyncio import tqdm
import json

# Advanced anti-detection imports
try:
    import cloudscraper
    print("✅ cloudscraper available - Advanced anti-bot protection enabled")
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    print("⚠️  cloudscraper not available. Install with: pip install cloudscraper")
    print("    Falling back to standard requests")
    import requests
    CLOUDSCRAPER_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase4_rom_downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Phase4AntiThrottlingDownloader:
    """Phase 4 ROM downloader with advanced anti-throttling using cloudscraper"""
    
    def __init__(self, session_rotation_interval: int = 3):
        """
        Initialize the Phase 4 downloader
        
        Args:
            session_rotation_interval: Rotate session every N downloads (prevents fingerprinting)
        """
        self.session_rotation_interval = session_rotation_interval
        self.downloads_count = 0
        self.session = None
        self.download_stats = {
            'successful': 0,
            'failed': 0,
            'sessions_created': 0,
            'total_size': 0
        }
        
        # Initialize first session
        self._create_new_session()
        
        logger.info("🚀 Phase 4 Anti-Throttling ROM Downloader initialized")
    
    def _create_new_session(self):
        """Create a new browser session with randomized fingerprint"""
        if CLOUDSCRAPER_AVAILABLE:
            # cloudscraper automatically handles browser impersonation
            browser_choice = random.choice(['chrome', 'firefox'])
            
            if browser_choice == 'chrome':
                self.session = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': random.choice(['windows', 'darwin', 'linux']),
                        'mobile': False
                    }
                )
            else:
                self.session = cloudscraper.create_scraper(
                    browser={
                        'browser': 'firefox',
                        'platform': random.choice(['windows', 'darwin', 'linux']),
                        'mobile': False
                    }
                )
            
            logger.info(f"🌐 Created new cloudscraper session (browser: {browser_choice})")
        else:
            # Fallback to requests with enhanced headers
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            })
            logger.info("🔄 Created new requests session with enhanced headers")
        
        self.download_stats['sessions_created'] += 1
    
    def _get_random_user_agent(self):
        """Get a random modern user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        return random.choice(user_agents)
    
    def _should_rotate_session(self):
        """Check if we should rotate to a new session"""
        return self.downloads_count % self.session_rotation_interval == 0 and self.downloads_count > 0
    
    async def download_rom(self, rom: Dict, output_dir: Path, pbar: tqdm = None) -> bool:
        """Download a single ROM with Phase 4 anti-throttling"""
        
        # Check if we should rotate session
        if self._should_rotate_session():
            logger.info(f"🔄 Rotating session after {self.downloads_count} downloads")
            self._create_new_session()
            # Add small delay after session rotation
            await asyncio.sleep(random.uniform(2, 5))
        
        name = rom['name']
        url = rom['url']
        
        # Get download path
        download_path = output_dir / name
        
        # Skip if already exists
        if download_path.exists():
            if pbar:
                pbar.set_description(f"⏭️ Skipping: {name[:30]}...")
            logger.info(f"⏭️ Skipping existing file: {name}")
            return True
        
        try:
            if pbar:
                pbar.set_description(f"📥 Downloading: {name[:30]}...")
            
            logger.info(f"🚀 Starting download: {name}")
            logger.info(f"🔗 URL: {url}")
            
            # Add pre-download delay (human-like behavior)
            await asyncio.sleep(random.uniform(1, 3))
            
            # Make request with cloudscraper (it handles challenges automatically)
            start_time = time.time()
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.session.get(url, stream=True, timeout=60)
            )
            
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                logger.warning(f"⚠️ Received HTML instead of ROM file for {name}")
                self.download_stats['failed'] += 1
                return False
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size < 1024 * 1024:  # Less than 1MB is suspicious
                logger.warning(f"⚠️ Suspiciously small file size ({total_size} bytes) for {name}")
            
            # Download with progress
            downloaded = 0
            chunk_size = 8192
            
            async with aiofiles.open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        await f.write(chunk)
                        downloaded += len(chunk)
            
            download_time = time.time() - start_time
            speed_mbps = (downloaded / (1024 * 1024)) / download_time if download_time > 0 else 0
            
            logger.info(f"✅ Downloaded {name}: {downloaded / (1024*1024):.2f} MB in {download_time:.1f}s ({speed_mbps:.2f} MB/s)")
            
            self.download_stats['successful'] += 1
            self.download_stats['total_size'] += downloaded
            self.downloads_count += 1
            
            # Add post-download delay (varies based on success)
            post_delay = random.uniform(3, 8)  # Longer delays to avoid detection
            await asyncio.sleep(post_delay)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error downloading {name}: {e}")
            self.download_stats['failed'] += 1
            
            # Longer delay after failure
            await asyncio.sleep(random.uniform(5, 15))
            return False
    
    async def download_roms(self, roms: List[Dict], output_dir: Path):
        """Download multiple ROMs with advanced anti-throttling"""
        
        # Create output directory
        output_dir.mkdir(exist_ok=True)
        
        total_roms = len(roms)
        logger.info(f"🎮 Starting download of {total_roms} ROMs with Phase 4 anti-throttling")
        
        # Shuffle download order to avoid predictable patterns
        shuffled_roms = roms.copy()
        random.shuffle(shuffled_roms)
        logger.info("🔀 Shuffled ROM order for unpredictable download pattern")
        
        # Progress bar
        with tqdm(total=total_roms, desc="📥 Downloading ROMs", unit="ROM") as pbar:
            for i, rom in enumerate(shuffled_roms, 1):
                success = await self.download_rom(rom, output_dir, pbar)
                
                if success:
                    pbar.update(1)
                
                # Log progress every 5 downloads
                if i % 5 == 0:
                    self._log_stats()
                
                # Extra long delay every 10 downloads to appear more human-like
                if i % 10 == 0:
                    extra_delay = random.uniform(30, 60)
                    logger.info(f"😴 Taking extended break: {extra_delay:.1f}s (after {i} downloads)")
                    await asyncio.sleep(extra_delay)
        
        # Final stats
        self._log_final_stats()
    
    def _log_stats(self):
        """Log current download statistics"""
        stats = self.download_stats
        total_mb = stats['total_size'] / (1024 * 1024)
        success_rate = (stats['successful'] / (stats['successful'] + stats['failed']) * 100) if (stats['successful'] + stats['failed']) > 0 else 0
        
        logger.info(f"📊 Stats: {stats['successful']} successful, {stats['failed']} failed, {total_mb:.1f} MB downloaded, {success_rate:.1f}% success rate")
    
    def _log_final_stats(self):
        """Log final download statistics"""
        stats = self.download_stats
        total_mb = stats['total_size'] / (1024 * 1024)
        total_gb = total_mb / 1024
        
        logger.info("🏁 DOWNLOAD COMPLETE!")
        logger.info(f"📊 Final Stats:")
        logger.info(f"   ✅ Successful downloads: {stats['successful']}")
        logger.info(f"   ❌ Failed downloads: {stats['failed']}")
        logger.info(f"   📁 Total data downloaded: {total_gb:.2f} GB")
        logger.info(f"   🔄 Sessions created: {stats['sessions_created']}")
        logger.info(f"   📈 Success rate: {(stats['successful'] / (stats['successful'] + stats['failed']) * 100):.1f}%")

def load_roms_from_file(file_path: str) -> List[Dict]:
    """Load ROM URLs from a text file"""
    roms = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        # Extract name from URL
                        name = unquote(line.split('/')[-1])
                        if not name.endswith(('.zip', '.7z', '.rar')):
                            name += '.zip'  # Default extension
                        
                        roms.append({
                            'name': name,
                            'url': line
                        })
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing line {line_num}: {e}")
                        
    except FileNotFoundError:
        logger.error(f"❌ ROM file not found: {file_path}")
        return []
    
    logger.info(f"📋 Loaded {len(roms)} ROMs from {file_path}")
    return roms

async def main():
    """Main function to run the Phase 4 ROM downloader"""
    
    print("🎮 Phase 4 Anti-Throttling ROM Downloader")
    print("=" * 50)
    print("This downloader uses cloudscraper to bypass advanced throttling")
    print("that occurs after initial fast downloads.\n")
    
    # Check if cloudscraper is available
    if not CLOUDSCRAPER_AVAILABLE:
        print("⚠️  WARNING: cloudscraper not installed!")
        print("   Install with: pip install cloudscraper")
        print("   Continuing with basic anti-throttling...\n")
    
    # ROM file path
    rom_file = Path("../rom_website_scraper/scraped_data/GameCube/Zelda_Roms.txt")
    if not rom_file.exists():
        rom_file = Path("sample_data/test_roms.txt")
        if not rom_file.exists():
            logger.error("❌ No ROM file found. Please provide Zelda_Roms.txt or create sample_data/test_roms.txt")
            return
    
    # Load ROMs
    roms = load_roms_from_file(str(rom_file))
    if not roms:
        logger.error("❌ No ROMs loaded. Check your ROM file.")
        return
    
    # Output directory
    output_dir = Path("ROM_Downloads_Phase4")
    
    # Create downloader with session rotation every 3 downloads
    downloader = Phase4AntiThrottlingDownloader(session_rotation_interval=3)
    
    print(f"📁 Output directory: {output_dir}")
    print(f"🔄 Session rotation: Every {downloader.session_rotation_interval} downloads")
    print(f"🎯 Target ROMs: {len(roms)}")
    print("\n🚀 Starting downloads...\n")
    
    # Start downloads
    await downloader.download_roms(roms, output_dir)

if __name__ == "__main__":
    asyncio.run(main())
