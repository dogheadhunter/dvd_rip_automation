#!/usr/bin/env python3
"""
Test script to verify content validation is working correctly.
This script attempts to download a ROM file and checks if content validation prevents
HTML error pages from being saved as ROM files.
"""

import asyncio
import aiohttp
from pathlib import Path
import sys
import os

# Add the parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from rom_downloader_enhanced import EnhancedROMDownloader
    print("✅ Using enhanced ROM downloader")
except ImportError:
    print("❌ Error: Could not import EnhancedROMDownloader")
    sys.exit(1)

async def test_content_validation():
    """Test content validation by downloading a ROM and checking for HTML detection"""
    print("🧪 Testing content validation...")
    
    # Initialize downloader with test settings
    downloader = EnhancedROMDownloader(debug=True)
    
    # Create test ROM entry
    test_rom = {
        'name': 'Test_ROM_Content_Validation.zip',
        'url': 'https://httpbin.org/html',  # This will return HTML content
        'size': '1MB'
    }
    
    # Set up output directory
    output_dir = Path('tests/content_validation_test')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create test session
    async with aiohttp.ClientSession() as session:
        # Try to download the "ROM" (which is actually HTML)
        print("⬇️ Attempting to download HTML content as ROM...")
        result = await downloader.download_rom_enhanced(test_rom, output_dir, session)
        
        # Check result
        if result:
            print("❌ TEST FAILED: Downloaded HTML content as ROM file")
        else:
            print("✅ TEST PASSED: Content validation prevented saving HTML as ROM")
        
        # Check if file exists
        output_path = output_dir / test_rom['name']
        if output_path.exists():
            print(f"❌ Warning: File was created: {output_path}")
            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(200)
                print(f"File content preview: {content}...")
            # Clean up the file
            os.remove(output_path)
        else:
            print("✅ No file was created, as expected")
    
    print("🧪 Content validation test complete")

if __name__ == "__main__":
    asyncio.run(test_content_validation())
