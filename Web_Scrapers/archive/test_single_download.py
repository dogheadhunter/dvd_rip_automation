#!/usr/bin/env python3
"""
Test ROM Downloader with just one ROM
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from rom_downloader import ROMDownloader

async def test_single_rom_download():
    """Test downloading a single ROM"""
    print("🎮 ROM DOWNLOADER TEST")
    print("=" * 50)
    
    # Create a minimal ROM entry for testing
    test_rom = {
        'name': 'Burnout (USA).zip',
        'url': 'https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Burnout%20%28USA%29.zip',
        'console': 'GameCube',
        'local_filename': 'Burnout_(USA).zip'
    }
    
    # Setup output directory
    output_dir = Path(__file__).parent.parent / "ROM_Downloads_Test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎯 Test ROM: {test_rom['name']}")
    print(f"📁 Output: {output_dir}")
    print(f"🌐 URL: {test_rom['url']}")
    
    # Initialize downloader with minimal settings
    downloader = ROMDownloader(proxy_count=5, concurrent_downloads=1, timeout=60)
    
    print("\n🔄 Initializing proxies...")
    await downloader.initialize_proxies()
    
    proxy_count = len(downloader.proxy_rotator.proxies) if downloader.proxy_rotator else 0
    print(f"✅ Found {proxy_count} working proxies")
    
    print("\n⬇️  Starting download...")
    await downloader.download_roms_batch([test_rom], output_dir)
    
    print("\n📊 Download Complete!")
    downloader.print_stats()
    
    # Check if file was created
    expected_file = output_dir / "GameCube" / "Burnout_(USA).zip"
    if expected_file.exists():
        size_mb = expected_file.stat().st_size / (1024 * 1024)
        print(f"🎉 Success! Downloaded file: {size_mb:.1f} MB")
    else:
        print("❌ File not found after download")

if __name__ == "__main__":
    asyncio.run(test_single_rom_download())
