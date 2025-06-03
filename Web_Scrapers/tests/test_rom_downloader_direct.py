#!/usr/bin/env python3
"""
ROM Downloader Direct Test
==========================

This script tests the ROM downloader without using proxies to determine
if the issue is with the proxies rather than the URLs themselves.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path so we can import rom_downloader_enhanced
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rom_downloader_enhanced import EnhancedRomDownloader
    print("✅ Successfully imported EnhancedRomDownloader")
except ImportError as e:
    print(f"❌ Error importing EnhancedRomDownloader: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rom_downloader_direct_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("direct-test")

async def test_direct_download():
    """Test downloading a ROM directly without proxies"""
    print("\n🧪 ROM DOWNLOADER DIRECT TEST")
    print("============================")
    print("Testing download without proxies to check if proxy is the issue\n")
    
    # Create downloader with proxies disabled
    downloader = EnhancedRomDownloader(
        sequential_mode=True,
        proxy_count=0,  # No proxies
        timeout=60,
        enable_behavioral_randomization=False,
        debug=True  # Enable debug mode for verbose logging
    )
    
    # Output directory for test downloads
    output_dir = Path("ROM_Downloads_Direct_Test")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir}\n")
    
    # Define test ROMs from the Zelda_Roms.txt file
    test_roms = [
        {
            'name': 'Legend of Zelda, The - The Wind Waker (USA).zip',
            'url': 'https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Legend%20of%20Zelda%2C%20The%20-%20The%20Wind%20Waker%20%28USA%29.zip'
        }
    ]
    
    print(f"🎮 Testing download for: {test_roms[0]['name']}")
    print(f"🔗 URL: {test_roms[0]['url']}")
    print("\n🚀 Starting direct download test...\n")
    
    # Run downloads
    await downloader.download_roms_sequential(test_roms, output_dir)
    
    # Check results
    download_path = downloader.get_download_path(test_roms[0], output_dir)
    if download_path.exists():
        size = download_path.stat().st_size
        print(f"\n✅ Download successful! File size: {size / (1024*1024):.2f} MB")
        
        # Check if it's an HTML file by looking at the first few bytes
        with open(download_path, 'rb') as f:
            content_start = f.read(1024).decode('utf-8', errors='ignore').lower()
            if '<html' in content_start or '<!doctype html' in content_start:
                print(f"⚠️ WARNING: Downloaded file appears to be HTML, not a ROM!")
                print(f"Preview of content: {content_start[:200]}...")
    else:
        print(f"❌ Download failed. File not found at: {download_path}")
    
    print("\n📝 Test completed")

if __name__ == "__main__":
    asyncio.run(test_direct_download())
