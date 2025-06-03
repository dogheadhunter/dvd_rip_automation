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
# Phase 3: Behavioral Randomization imports
from datetime import datetime, timedelta
import hashlib
import json

# Add the working_scrapers directory to path to import our proxy tools
sys.path.append(str(Path(__file__).parent / "working_scrapers"))

try:
    from modern_proxy_scraper_enhanced import EnhancedModernProxyRotator
    print("✅ Using enhanced proxy scraper with Phase 2 headers")
except ImportError:
    try:
        from modern_proxy_scraper import ModernProxyRotator
        print("⚠️  Using basic proxy scraper - Phase 2 features not available")
    except ImportError:
        print("❌ Error: Could not import any proxy scraper")
        print("Make sure you're running this from the Web_Scrapers directory")
        sys.exit(1)

class BehavioralRandomizer:
    """
    Phase 3: Behavioral Randomization for Human-like Download Patterns
    =================================================================
    
    This class implements realistic human-like behaviors to avoid detection:
    - Variable timing patterns between downloads
    - Random download order shuffling
    - Session rotation and cleanup
    - Realistic retry patterns with exponential backoff
    """
    
    def __init__(self):
        self.session_start_time = datetime.now()
        self.downloads_this_session = 0
        self.session_rotation_interval = random.randint(15, 25)  # Downloads per session
        self.last_download_time = None
        self.consecutive_failures = 0
        
        # Behavioral patterns
        self.timing_patterns = {
            'quick_burst': (1, 3),      # Fast downloads (excited user)
            'normal_browse': (3, 8),    # Normal browsing speed
            'careful_browse': (8, 15),  # Cautious user, reading descriptions
            'distracted': (15, 45)      # User gets distracted, longer pauses
        }
        
        self.current_pattern = 'normal_browse'
        self.pattern_change_probability = 0.15  # 15% chance to change pattern
        
    def get_human_like_delay(self) -> float:
        """Generate human-like delay between downloads"""
        # Occasionally change behavioral patterns
        if random.random() < self.pattern_change_probability:
            self.current_pattern = random.choice(list(self.timing_patterns.keys()))
            
        base_delay = random.uniform(*self.timing_patterns[self.current_pattern])
        
        # Add micro-variations (humans aren't perfectly consistent)
        variation = random.uniform(0.8, 1.2)
        delay = base_delay * variation
        
        # Slightly longer delays at the start of sessions (user orientation)
        if self.downloads_this_session < 3:
            delay *= random.uniform(1.2, 1.8)
            
        # Slightly shorter delays in the middle of sessions (user in flow)
        elif 5 <= self.downloads_this_session <= 15:
            delay *= random.uniform(0.7, 0.9)
            
        return max(1.0, delay)  # Minimum 1 second delay
        
    def should_rotate_session(self) -> bool:
        """Determine if we should start a new session"""
        return self.downloads_this_session >= self.session_rotation_interval
        
    def rotate_session(self):
        """Reset session counters and generate new parameters"""
        self.session_start_time = datetime.now()
        self.downloads_this_session = 0
        self.session_rotation_interval = random.randint(15, 25)
        self.consecutive_failures = 0
        print(f"🔄 Starting new session (session rotation)")
        
    def get_retry_delay(self, attempt: int) -> float:
        """Get delay for retry attempts with exponential backoff + jitter"""
        # Exponential backoff: 2^attempt + jitter
        base_delay = 2 ** attempt
        jitter = random.uniform(0.5, 1.5)
        human_factor = random.uniform(0.8, 1.3)  # Humans aren't perfectly exponential
        
        return min(60, base_delay * jitter * human_factor)  # Cap at 60 seconds
        
    def randomize_download_order(self, downloads: List[Dict]) -> List[Dict]:
        """Shuffle download order with human-like patterns"""
        # Don't always fully randomize - humans have some method to their madness
        shuffle_strategies = [
            'full_random',      # Complete randomization
            'chunk_shuffle',    # Shuffle in chunks
            'reverse_some',     # Reverse portions
            'priority_first'    # Keep some high-priority items first
        ]
        
        strategy = random.choice(shuffle_strategies)
        result = downloads.copy()
        
        if strategy == 'full_random':
            random.shuffle(result)
        elif strategy == 'chunk_shuffle':
            # Shuffle in chunks of 3-7 items
            chunk_size = random.randint(3, 7)
            for i in range(0, len(result), chunk_size):
                chunk = result[i:i+chunk_size]
                random.shuffle(chunk)
                result[i:i+chunk_size] = chunk
        elif strategy == 'reverse_some':
            # Reverse random sections
            for _ in range(random.randint(1, 3)):
                start = random.randint(0, len(result) - 2)
                end = random.randint(start + 1, min(start + 8, len(result)))
                result[start:end] = reversed(result[start:end])
        elif strategy == 'priority_first':
            # Keep first few items, shuffle the rest
            keep_first = random.randint(1, min(3, len(result)))
            shuffled_portion = result[keep_first:]
            random.shuffle(shuffled_portion)
            result = result[:keep_first] + shuffled_portion
            
        return result
        
    def record_download_attempt(self, success: bool):
        """Record download attempt for behavioral tracking"""
        self.downloads_this_session += 1
        self.last_download_time = datetime.now()
        
        if success:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            
        # If too many failures, change pattern to be more cautious
        if self.consecutive_failures >= 3:
            self.current_pattern = 'careful_browse'
            
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        session_duration = datetime.now() - self.session_start_time
        return {
            'session_duration': str(session_duration),
            'downloads_this_session': self.downloads_this_session,
            'current_pattern': self.current_pattern,
            'consecutive_failures': self.consecutive_failures
        }

class EnhancedROMDownloader:
    """Enhanced ROM downloader with anti-throttling improvements"""
    
    def __init__(self, 
                 proxy_count: int = 15,
                 sequential_mode: bool = True,
                 delay_range: tuple = (2, 8),
                 timeout: int = 300,
                 enable_behavioral_randomization: bool = True):
        self.proxy_count = proxy_count
        self.sequential_mode = sequential_mode
        self.delay_range = delay_range
        self.timeout = timeout
        self.proxy_rotator = None
        
        # Phase 3: Initialize Behavioral Randomizer
        self.behavioral_randomizer = BehavioralRandomizer() if enable_behavioral_randomization else None
        self.enable_behavioral_randomization = enable_behavioral_randomization
        
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
    
    async def download_roms_sequential(self, roms: List[Dict], output_dir: Path):
        """Download ROMs one at a time with Phase 3 behavioral randomization"""
        print(f"🤖 Using sequential downloads with Phase 3 behavioral randomization")
        
        # Phase 3: Shuffle download order for randomization
        if self.enable_behavioral_randomization:
            shuffled_roms = self.behavioral_randomizer.randomize_download_order(roms.copy())
            print(f"🎲 Applied randomized download order")
        else:
            shuffled_roms = roms
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
            total=len(shuffled_roms),
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
            
            for i, rom in enumerate(shuffled_roms, 1):
                print(f"\n📥 [{i}/{len(shuffled_roms)}] Processing: {rom['name']}")
                
                # Phase 3: Apply retry logic with behavioral delays
                success = False
                max_retries = 3
                for attempt in range(max_retries):
                    if attempt > 0:
                        if self.enable_behavioral_randomization:
                            retry_delay = self.behavioral_randomizer.get_retry_delay(attempt)
                            print(f"🔄 Retry {attempt}/{max_retries-1} after {retry_delay:.1f}s...")
                            await asyncio.sleep(retry_delay)
                        else:
                            retry_delay = random.uniform(2, 5)
                            print(f"🔄 Retry {attempt}/{max_retries-1} after {retry_delay:.1f}s...")
                            await asyncio.sleep(retry_delay)
                    
                    success = await self.download_rom_enhanced(rom, output_dir, session, overall_pbar)
                    if success:
                        break
                        
                if not success:
                    self.download_stats['failed'] += 1
                
                # Phase 3: Record download attempt for behavioral tracking
                if self.enable_behavioral_randomization:
                    self.behavioral_randomizer.record_download_attempt(success)
                
                # Update overall progress (ROM completed)
                overall_pbar.set_postfix({
                    'completed': self.download_stats['completed'],
                    'failed': self.download_stats['failed'],
                    'size': f"{self.download_stats['total_size']/(1024*1024*1024):.2f}GB"
                })
                
                # Phase 3: Behavioral delay between downloads
                if i < len(shuffled_roms):
                    if self.enable_behavioral_randomization:
                        delay = self.behavioral_randomizer.get_human_like_delay()
                        print(f"⏳ Behavioral delay ({self.behavioral_randomizer.current_pattern}): {delay:.1f}s")
                        await asyncio.sleep(delay)
                        
                        # Check for session rotation
                        if self.behavioral_randomizer.should_rotate_session():
                            print("🔄 Rotating session for behavioral randomization...")
                            self.behavioral_randomizer.rotate_session()
                            await session.close()
                            connector = aiohttp.TCPConnector(
                                limit=10,
                                limit_per_host=3,
                                ssl=ssl_context
                            )
                            session = aiohttp.ClientSession(connector=connector, timeout=timeout)
                    else:
                        delay = random.uniform(self.delay_range[0], self.delay_range[1])
                        print(f"⏳ Waiting {delay:.1f}s before next download...")
                        await asyncio.sleep(delay)
        
        overall_pbar.close()
        
        if self.enable_behavioral_randomization:
            behavior_stats = self.behavioral_randomizer.get_session_stats()
            print(f"\n🎲 Behavioral Randomization Stats:")
            for key, value in behavior_stats.items():
                print(f"   • {key}: {value}")
        
        print("\n✨ Sequential downloads completed!")
    
    async def download_roms_batch(self, roms: List[Dict], output_dir: Path):
        """Download ROMs - use sequential mode with behavioral randomization by default"""
        if self.sequential_mode:
            await self.download_roms_sequential(roms, output_dir)
        else:
            # Legacy concurrent mode (may trigger throttling)
            await self.download_roms_concurrent(roms, output_dir)
    
    async def download_roms_concurrent(self, roms: List[Dict], output_dir: Path):
        """Download ROMs in batches with concurrency control (legacy mode)"""
        concurrent_downloads = 2  # Reduced from 3 to be more polite
        semaphore = asyncio.Semaphore(concurrent_downloads)
        
        print("⚠️  Using legacy concurrent mode - Phase 3 behavioral randomization not fully applicable")
          # Phase 3: Still apply download order randomization in concurrent mode
        if self.enable_behavioral_randomization:
            shuffled_roms = self.behavioral_randomizer.randomize_download_order(roms.copy())
            print(f"🎲 Applied randomized download order")
        else:
            shuffled_roms = roms
        
        # Create overall progress bar for concurrent mode
        overall_pbar = tqdm(
            total=len(shuffled_roms),
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
                    success = await self.download_rom_enhanced(rom, output_dir, session, overall_pbar)
                    if not success:
                        self.download_stats['failed'] += 1
                    
                    # Update overall progress
                    overall_pbar.set_postfix({
                        'completed': self.download_stats['completed'],
                        'failed': self.download_stats['failed'],
                        'size': f"{self.download_stats['total_size']/(1024*1024*1024):.2f}GB"
                    })
                      # Phase 3: Basic behavioral delay in concurrent mode
                    if self.enable_behavioral_randomization:
                        delay = self.behavioral_randomizer.get_human_like_delay()
                        await asyncio.sleep(delay)
                    else:
                        # Random delay between downloads
                        await asyncio.sleep(random.uniform(2, 5))  # Increased delay
        
        # Execute downloads
        tasks = [download_with_semaphore(rom) for rom in shuffled_roms]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        overall_pbar.close()
        print("\n✨ Concurrent downloads completed!")

    async def run_interactive(self):
        """Interactive ROM downloader interface with Phase 3 behavioral randomization"""
        print("🎮 ENHANCED ROM DOWNLOADER - Phase 1, 2 & 3 Complete")
        print("="*70)
        print("Features:")
        print("- ✅ Phase 1: Enhanced proxy rotation and logging")
        print("- ✅ Phase 2: Advanced header randomization")
        print("- ✅ Phase 3: Behavioral randomization (human-like patterns)")
        print("- Beautiful progress bars with download speeds and ETAs")
        print("- SSL certificate handling for self-signed certificates")
        print("- Resume capability for interrupted downloads")
        print("="*70)
        
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
        output_dir = Path("ROM_Downloads_Enhanced")
        output_dir.mkdir(exist_ok=True)
        print(f"📁 Downloads will be saved to: {output_dir.absolute()}")
          # Phase 3: Configure behavioral randomization
        if self.enable_behavioral_randomization:
            print("\n🎲 Behavioral Randomization Options:")
            print("1. Quick Burst (fast downloads, short pauses)")
            print("2. Normal Browse (balanced timing)")
            print("3. Careful Browse (longer pauses, methodical)")
            print("4. Distracted (random long pauses)")
            print("5. Adaptive (learns from failures)")
            while True:
                pattern_choice = input("Select behavioral pattern (1-5) or press Enter for adaptive: ").strip()
                if pattern_choice == '' or pattern_choice == '5':
                    self.behavioral_randomizer.current_pattern = 'normal_browse'  # Default to normal browse
                    break
                elif pattern_choice in ['1', '2', '3', '4']:
                    patterns = ['quick_burst', 'normal_browse', 'careful_browse', 'distracted']
                    self.behavioral_randomizer.current_pattern = patterns[int(pattern_choice) - 1]
                    break
                else:
                    print("Please enter 1-5 or press Enter")
            
            print(f"✅ Using {self.behavioral_randomizer.current_pattern} behavioral pattern")
        
        # Ask about proxy usage
        while True:
            use_proxies = input("\nUse proxy rotation? (y/N): ").strip().lower()
            if use_proxies in ['y', 'yes']:
                use_proxies = True
                break
            elif use_proxies in ['n', 'no', '']:
                use_proxies = False
                break
            else:
                print("Please enter 'y' for yes or 'n' for no")
        
        if use_proxies:
            print(f"🔍 Finding working proxies (enhanced with 13 GitHub sources)...")
            try:
                # Use existing proxy rotator or create new one
                if not self.proxy_rotator:
                    from working_scrapers.modern_proxy_scraper_enhanced import ModernProxyRotator
                    self.proxy_rotator = ModernProxyRotator(proxy_count=self.proxy_count, timeout=10)
                
                working_proxies = await self.proxy_rotator.find_proxies_async()
                
                if working_proxies:
                    print(f"✅ Found {len(working_proxies)} working proxies")
                else:
                    print("⚠️  No working proxies found, continuing with direct connections")
                    self.proxy_rotator = None
            except Exception as e:
                print(f"❌ Proxy discovery failed: {e}")
                print("⚠️  Continuing with direct connections")
                self.proxy_rotator = None
        
        # Start downloads
        print(f"\n🚀 Starting enhanced downloads with Phase 1-3 improvements...")
        if self.enable_behavioral_randomization:
            print(f"🤖 Behavioral randomization: {self.behavioral_randomizer.current_pattern}")
        print("📡 SSL Certificate verification disabled for ROM hosting sites")
        print("📊 You'll see beautiful progress bars with speeds and ETAs!")
        
        start_time = time.time()
        await self.download_roms_batch(all_roms, output_dir)
        end_time = time.time()
        
        # Print final statistics
        self.print_enhanced_stats()
        print(f"⏱️  Total Time: {end_time - start_time:.1f} seconds")

async def main():
    """Main entry point"""
    downloader = EnhancedROMDownloader(
        proxy_count=10, 
        sequential_mode=True, 
        delay_range=(2, 8),
        enable_behavioral_randomization=True  # Phase 3: Enable by default
    )
    
    # Check command line args for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        await downloader.run_quick_test()
    else:
        await downloader.run_interactive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Download cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
