#!/usr/bin/env python3
"""
Quick test of the updated ROM downloader with sequential downloads
"""

import asyncio
from rom_downloader import ROMDownloader

async def test_rom_downloader():
    print("🎮 Testing ROM Downloader - Sequential Mode")
    print("=" * 50)
    
    # Create downloader with sequential mode and short delays for testing
    downloader = ROMDownloader(
        proxy_count=5,
        sequential_mode=True,
        delay_range=(1, 3),  # Short delays for testing
        timeout=60
    )
    
    print(f"✅ ROMDownloader created successfully!")
    print(f"📝 Sequential mode: {downloader.sequential_mode}")
    print(f"⏳ Delay range: {downloader.delay_range[0]}-{downloader.delay_range[1]} seconds")
    print(f"🔍 Proxy count: {downloader.proxy_count}")
    
    # Find ROM files
    rom_files = downloader.find_rom_files()
    if rom_files:
        print(f"\n📁 Found ROM collections:")
        for console, files in rom_files.items():
            total_roms = 0
            for file_path in files:
                roms = downloader.parse_rom_file(file_path)
                total_roms += len(roms)
            print(f"  🎯 {console}: {len(files)} files, ~{total_roms} ROMs")
    else:
        print("❌ No ROM files found")
    
    print("\n🚀 Sequential download system ready!")
    print("💡 Key improvements:")
    print("   - One ROM at a time to avoid throttling")
    print("   - Configurable delays between downloads") 
    print("   - Better progress tracking with ROM names")
    print("   - Legacy concurrent mode still available")

if __name__ == "__main__":
    asyncio.run(test_rom_downloader())
