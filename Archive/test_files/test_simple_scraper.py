#!/usr/bin/env python3
"""
Test script to run the simple web scraper with hardcoded inputs
"""

from simple_web_scraper import SimpleWebScraper
import os

def test_scraper():
    print("=== Testing Simple Web Scraper ===")
    
    # Create scraper instance
    scraper = SimpleWebScraper(delay_range=(1.0, 2.0))
    
    # Use sample URLs
    url_file = "sample_urls.txt"
    output_dir = "test_downloads"
    
    try:
        # Load URLs
        urls = scraper.load_urls_from_file(url_file)
        print(f"Loaded {len(urls)} URLs")
        
        if urls:
            print("URLs to scrape:")
            for i, url in enumerate(urls, 1):
                print(f"  {i}. {url}")
            
            # Start scraping
            scraper.scrape_urls(urls, output_dir)
            print(f"\nScraping completed! Check '{output_dir}' folder for results.")
            
            # List created files
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                print(f"\nCreated {len(files)} files:")
                for file in files:
                    print(f"  - {file}")
        else:
            print("No URLs found to scrape")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scraper()
