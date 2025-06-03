#!/usr/bin/env python3
"""
Test script for the free proxy scraper
"""

from free_proxy_scraper import WebScraperWithFreeProxies
import os

def test_proxy_scraper():
    print("=== Testing Free Proxy Scraper ===")
    
    # Test without proxies first
    print("\n1. Testing WITHOUT proxies:")
    scraper_no_proxy = WebScraperWithFreeProxies(use_proxies=False, delay_range=(0.5, 1.0))
    scraper_no_proxy.initialize()
    
    urls = scraper_no_proxy.load_urls_from_file("sample_urls.txt")
    scraper_no_proxy.scrape_urls(urls, "test_no_proxy")
    
    # Test with proxies
    print("\n2. Testing WITH proxies:")
    scraper_with_proxy = WebScraperWithFreeProxies(
        use_proxies=True, 
        proxy_count=5,  # Small number for testing
        delay_range=(0.5, 1.0)
    )
    scraper_with_proxy.initialize()
    
    if scraper_with_proxy.proxy_rotator and scraper_with_proxy.proxy_rotator.proxies:
        print(f"Found {len(scraper_with_proxy.proxy_rotator.proxies)} proxies")
        urls = scraper_with_proxy.load_urls_from_file("sample_urls.txt")
        scraper_with_proxy.scrape_urls(urls, "test_with_proxy")
    else:
        print("No working proxies found, skipping proxy test")

if __name__ == "__main__":
    test_proxy_scraper()
