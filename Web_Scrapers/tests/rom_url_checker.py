#!/usr/bin/env python3
"""
ROM URL Checker and Alternative Source Finder
============================================

This tool helps find alternative download sources for ROMs
when the primary source is not working.
"""

import requests
import sys
from urllib.parse import unquote, quote
import re
import time

def test_url(url, show_headers=False):
    """Test if a URL is accessible and what type of content it returns"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://myrient.erista.me/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        content_type = response.headers.get('content-type', 'unknown')
        
        if show_headers:
            print("\nResponse Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
        
        is_html = 'text/html' in content_type
        
        # Read a small chunk to check content
        content_preview = next(response.iter_content(chunk_size=1024), b"").decode('utf-8', errors='ignore')
        
        return {
            'status': response.status_code,
            'content_type': content_type,
            'is_html': is_html,
            'content_preview': content_preview if is_html else "[BINARY DATA]",
            'success': response.status_code == 200 and not is_html
        }
    
    except Exception as e:
        return {
            'status': 0,
            'content_type': 'error',
            'is_html': False,
            'content_preview': str(e),
            'success': False
        }

def find_alternative_sources(rom_name):
    """Try to find alternative sources for the ROM"""
    # List of ROM sites to check
    alt_domains = [
        # Note: We're only using well-known public ROM archival sites
        "archive.org",
        "wowroms.com",
        "romsgames.net"
    ]
    
    search_term = rom_name.replace('.zip', '').replace('(USA)', '').strip()
    
    print(f"\n🔍 Searching for alternative sources for: {search_term}")
    
    for domain in alt_domains:
        if domain == "archive.org":
            # For archive.org, we'll check the Internet Archive's ROM collections
            search_url = f"https://archive.org/search?query={quote(search_term)}+gamecube"
            print(f"\nChecking {domain}...")
            
            try:
                response = requests.get(search_url)
                if "No results matched your criteria" not in response.text:
                    print(f"✅ Potential matches found on {domain}.")
                    print(f"🔗 Search URL: {search_url}")
                else:
                    print(f"❌ No matches found on {domain}.")
            except Exception as e:
                print(f"❌ Error searching {domain}: {e}")
        
        else:
            # For other ROM sites
            print(f"\nChecking {domain}...")
            print(f"🔗 Visit {domain} and search for \"{search_term}\"")
    
    print("\n⚠️ IMPORTANT LEGAL NOTICE:")
    print("This tool only helps identify if ROMs are available. Please ensure you")
    print("only download ROMs that you legally own and are entitled to use.")

def check_rom_url_format(url):
    """Check if the ROM URL format is correct and suggest fixes if not"""
    print(f"\n🔍 Analyzing URL format: {unquote(url)}")
    
    # Common issues with ROM URLs
    issues = []
    
    # Check for proper encoding
    if ' ' in url:
        issues.append("URL contains spaces which should be encoded as %20")
    
    # Check for correct protocol
    if not url.startswith('https://'):
        issues.append("URL should use HTTPS protocol")
    
    # Check for common domain typos
    common_domains = ['myrient.erista.me', 'archive.org', 'wowroms.com']
    domain_match = re.search(r'https?://([^/]+)', url)
    if domain_match:
        domain = domain_match.group(1)
        if domain not in common_domains and any(d in domain for d in common_domains):
            issues.append(f"Domain {domain} might have a typo")
    
    # Check file extension
    if not url.endswith('.zip') and not url.endswith('.7z') and not url.endswith('.rar'):
        issues.append("URL doesn't end with a common ROM archive extension (.zip, .7z, .rar)")
    
    if issues:
        print("⚠️ Found potential issues with the URL:")
        for issue in issues:
            print(f"  - {issue}")
        
        # Suggest a fixed URL if spaces need encoding
        if ' ' in url:
            fixed_url = url.replace(' ', '%20')
            print(f"\n✅ Suggested fixed URL: {fixed_url}")
    else:
        print("✅ URL format appears to be correct")

def main():
    if len(sys.argv) < 2:
        # Default test URL for Legend of Zelda Wind Waker
        url = "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Legend%20of%20Zelda%2C%20The%20-%20The%20Wind%20Waker%20%28USA%29.zip"
        rom_name = "Legend of Zelda, The - The Wind Waker (USA).zip"
    else:
        url = sys.argv[1]
        rom_name = url.split('/')[-1].replace('%20', ' ')
    
    print("🎮 ROM URL Checker and Alternative Source Finder")
    print("================================================")
    print(f"ROM: {unquote(rom_name)}")
    
    # Check URL format
    check_rom_url_format(url)
    
    # Test the URL
    print("\n🔍 Testing direct access to URL...")
    result = test_url(url, show_headers=True)
    
    if result['success']:
        print(f"✅ URL is accessible and returns binary content!")
        print(f"📊 Status Code: {result['status']}")
        print(f"📝 Content Type: {result['content_type']}")
    else:
        print(f"❌ URL is not accessible or returns HTML content")
        print(f"📊 Status Code: {result['status']}")
        print(f"📝 Content Type: {result['content_type']}")
        
        if result['is_html']:
            print("\n📄 HTML Content Preview:")
            print(result['content_preview'][:200] + "...")
            
            # Extract title if present
            title_match = re.search(r'<title>(.*?)</title>', result['content_preview'], re.IGNORECASE)
            if title_match:
                print(f"\n📑 Page Title: {title_match.group(1)}")
        
        # Find alternative sources
        find_alternative_sources(rom_name)
    
    print("\n📝 Recommendations:")
    print("1. Check if the website is still operational")
    print("2. Try using a different browser or device")
    print("3. Try at a different time (the site might be overloaded)")
    print("4. Check for alternative ROM sources")
    print("5. Make sure you have proper referrer headers in your requests")

if __name__ == "__main__":
    main()
