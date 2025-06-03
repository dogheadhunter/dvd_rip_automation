#!/usr/bin/env python3
"""
Quick test script to verify ROM downloader can find ROM files
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from rom_downloader import find_rom_files

def test_rom_finder():
    """Test if we can find ROM files"""
    script_dir = Path(__file__).parent
    rom_scraper_dir = script_dir.parent / "rom_website_scraper"
    scraped_data_dir = rom_scraper_dir / "scraped_data"
    
    print(f"Looking for ROM files in: {scraped_data_dir}")
    
    if not scraped_data_dir.exists():
        print("❌ scraped_data directory not found")
        return
        
    rom_files = find_rom_files(scraped_data_dir)
    
    print(f"Found {len(rom_files)} ROM files:")
    for rom_file in rom_files:
        console = rom_file.parent.name
        name = rom_file.stem
        
        # Count ROMs in file
        try:
            content = rom_file.read_text()
            rom_count = content.count('http')
        except:
            rom_count = "?"
            
        print(f"  - {console}/{name} ({rom_count} ROMs)")

if __name__ == "__main__":
    test_rom_finder()
