#!/usr/bin/env python3
"""
Quick test to verify ROM downloader proxy logging and rotation
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to path to import rom_downloader
sys.path.append(str(Path(__file__).parent.parent))

from rom_downloader import ROMDownloader

async def test_proxy_logging():
    """Test proxy logging and rotation"""
    print("🧪 Testing ROM Downloader Proxy Logging")
    print("="*50)
    
    # Create downloader with just a few proxies for quick testing
    downloader = ROMDownloader(proxy_count=3, sequential_mode=True, delay_range=(1, 2))
    
    # Check if ROM files exist
    rom_files = downloader.find_rom_files()
    if not rom_files:
        print("❌ No ROM files found. Please ensure rom_website_scraper has scraped data.")
        return
    
    print(f"📁 Found ROM files for: {list(rom_files.keys())}")
    
    # Test proxy initialization
    print("\n🔍 Testing proxy discovery...")
    from working_scrapers.modern_proxy_scraper import ModernProxyRotator
    
    proxy_rotator = ModernProxyRotator(proxy_count=3, timeout=5)
    downloader.proxy_rotator = proxy_rotator
    
    try:
        # Find a few proxies quickly
        proxies = await proxy_rotator.find_proxies_async()
        print(f"✅ Found {len(proxies)} working proxies")
        
        if proxies:
            for i, proxy in enumerate(proxies[:2]):
                print(f"   Proxy {i+1}: {proxy['http']} -> IP: {proxy.get('ip', 'Unknown')}")
        else:
            print("⚠️  No working proxies found - will test direct connections")
            
    except Exception as e:
        print(f"❌ Error finding proxies: {e}")
        print("⚠️  Will test direct connections only")
    
    # Test proxy rotation logic (without actual downloads)
    print("\n🔄 Testing proxy rotation logic...")
    for i in range(5):
        if downloader.proxy_rotator and downloader.proxy_rotator.proxies:
            proxy_dict = downloader.proxy_rotator.get_next_proxy()
            if proxy_dict:
                proxy = proxy_dict.get('http', 'None')
                print(f"   Rotation {i+1}: {proxy}")
            else:
                print(f"   Rotation {i+1}: No proxy returned")
        else:
            print(f"   Rotation {i+1}: No proxy rotator or proxies available")
    
    print("\n🎯 Proxy logging test complete!")
    print("Next: Run actual ROM downloader to test full proxy usage in downloads")

if __name__ == "__main__":
    asyncio.run(test_proxy_logging())
