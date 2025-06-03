#!/usr/bin/env python3
"""
🧪 Test Progress Bars for ROM Downloader
==========================================

Quick test to verify our new progress bar implementation works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add the working_scrapers directory to path to import our tools
sys.path.append(str(Path(__file__).parent / "working_scrapers"))

from rom_downloader import ROMDownloader

async def test_progress_bars():
    """Test the progress bar functionality with a small ROM collection"""
    print("🧪 Testing Progress Bar Implementation")
    print("="*50)
    
    # Create downloader with shorter delays for testing
    downloader = ROMDownloader(
        proxy_count=5,
        sequential_mode=True,
        delay_range=(1, 3),  # Shorter delays for testing
        timeout=120  # 2 minute timeout for testing
    )
    
    # Find ROM files
    rom_files = downloader.find_rom_files()
    if not rom_files:
        print("❌ No ROM files found for testing")
        return
    
    # Get GameCube ROMs if available
    if 'GameCube' in rom_files:
        console = 'GameCube'
        selected_files = rom_files[console][:1]  # Just test with one file
        print(f"🎯 Testing with {console} collection")
    else:
        # Use the first available console
        console = list(rom_files.keys())[0]
        selected_files = rom_files[console][:1]
        print(f"🎯 Testing with {console} collection")
    
    # Parse ROMs (limit to first 3 for testing)
    all_roms = []
    for file_path in selected_files:
        roms = downloader.parse_rom_file(file_path)
        all_roms.extend(roms[:3])  # Only first 3 ROMs for testing
        break
    
    if not all_roms:
        print("❌ No ROMs found for testing")
        return
    
    print(f"📊 Testing with {len(all_roms)} ROMs")
    
    # Set up test output directory
    output_dir = Path("ROM_Downloads_Test")
    output_dir.mkdir(exist_ok=True)
    
    print("\n🚀 Starting progress bar test...")
    print("📈 You should see:")
    print("   - Overall progress bar (blue)")
    print("   - Individual ROM progress bars (green)")
    print("   - Download speeds and ETAs")
    print("   - Clean formatting with no text spam")
    
    # Start downloads
    await downloader.download_roms_batch(all_roms, output_dir)
    
    # Print results
    downloader.print_stats()
    print("\n✅ Progress bar test completed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_progress_bars())
    except KeyboardInterrupt:
        print("\n⏹️  Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
