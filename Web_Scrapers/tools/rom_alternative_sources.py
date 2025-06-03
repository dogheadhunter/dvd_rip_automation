#!/usr/bin/env python3
"""
ROM Archive Alternative Source Scanner

This script helps find alternative sources for ROMs when the primary source isn't working.
It takes a ROM URL as input and provides recommendations and alternative sources.
"""

import requests
import argparse
import os
import sys
from urllib.parse import urlparse, unquote, quote
import re
import json
from pathlib import Path

def check_url_accessibility(url, timeout=10, show_headers=False):
    """Check if a URL is accessible and what content it returns"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/octet-stream,application/zip,application/x-zip-compressed,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://myrient.erista.me/',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        content_size = response.headers.get('content-length')
        if content_size:
            print(f"Size: {int(content_size)/1024/1024:.2f} MB")
        
        if show_headers:
            print("\nResponse Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            # Read a sample of the content to confirm it's HTML
            content_preview = next(response.iter_content(chunk_size=1024), b"").decode('utf-8', errors='ignore')
            
            print("\nHTML Content Preview:")
            print(content_preview[:200] + "...")
            
            # Try to extract the title
            title_match = re.search(r'<title>(.*?)</title>', content_preview, re.IGNORECASE)
            if title_match:
                print(f"\nPage Title: {title_match.group(1)}")
            
            return {
                'accessible': response.status_code == 200,
                'is_html': True,
                'content_type': content_type,
                'status_code': response.status_code,
                'title': title_match.group(1) if title_match else None,
                'is_binary': False
            }
        else:
            return {
                'accessible': response.status_code == 200,
                'is_html': False,
                'content_type': content_type,
                'status_code': response.status_code,
                'is_binary': True,
                'size': content_size
            }
            
    except Exception as e:
        print(f"Error: {e}")
        return {
            'accessible': False,
            'error': str(e),
            'is_html': False,
            'is_binary': False
        }

def generate_alternative_urls(url, rom_name):
    """Generate alternative URLs for the ROM"""
    print(f"\n🔍 Generating alternative URLs for: {rom_name}")
    
    # Extract components from the URL
    url_parts = urlparse(url)
    domain = url_parts.netloc
    path = url_parts.path
    scheme = url_parts.scheme
    
    # Extract console from path if possible
    console = None
    console_match = re.search(r'Nintendo\s*-\s*(\w+)', path, re.IGNORECASE)
    if console_match:
        console = console_match.group(1).lower()
    
    alternatives = []
    
    # Alternative 1: Archive.org
    if console:
        archive_url = f"https://archive.org/download/nintendo-{console.lower()}-romset/{quote(rom_name)}"
        alternatives.append({
            'source': 'Archive.org',
            'url': archive_url,
            'description': f"Internet Archive Nintendo {console} ROM collection"
        })
    
    # Alternative 2: Try a different path format
    if 'myrient.erista.me' in domain:
        simpler_path = f"/{os.path.basename(path)}"
        simple_url = f"{scheme}://{domain}{simpler_path}"
        alternatives.append({
            'source': 'Simplified Path',
            'url': simple_url,
            'description': "Same site but with a simplified path"
        })
    
    # Alternative 3: Try adding/removing www
    if domain.startswith('www.'):
        no_www_domain = domain[4:]
        no_www_url = f"{scheme}://{no_www_domain}{path}"
        alternatives.append({
            'source': 'No www',
            'url': no_www_url,
            'description': "Same site without www prefix"
        })
    else:
        www_domain = f"www.{domain}"
        www_url = f"{scheme}://{www_domain}{path}"
        alternatives.append({
            'source': 'With www',
            'url': www_url,
            'description': "Same site with www prefix"
        })
    
    # Alternative 4: Try HTTPS if using HTTP
    if scheme == 'http':
        https_url = f"https://{domain}{path}"
        alternatives.append({
            'source': 'HTTPS',
            'url': https_url,
            'description': "Same URL with HTTPS instead of HTTP"
        })
    
    return alternatives

def check_alternatives(alternatives):
    """Check all alternative URLs and return results"""
    results = []
    
    for alt in alternatives:
        print(f"\n🔍 Checking {alt['source']}: {alt['url']}")
        result = check_url_accessibility(alt['url'])
        alt['result'] = result
        results.append(alt)
        
        if result.get('accessible', False) and result.get('is_binary', False):
            print(f"✅ Success! This alternative URL works!")
        else:
            print(f"❌ Alternative URL failed or returned HTML")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='ROM Archive Alternative Source Scanner')
    parser.add_argument('--url', '-u', help='URL of the ROM file that is failing')
    parser.add_argument('--rom', '-r', help='Name of the ROM file')
    parser.add_argument('--save', '-s', action='store_true', help='Save working alternatives to a file')
    parser.add_argument('--check-all', '-c', action='store_true', help='Check all alternative URLs')
    
    args = parser.parse_args()
    
    # Default URL and ROM name if not provided
    if not args.url:
        args.url = "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Legend%20of%20Zelda%2C%20The%20-%20The%20Wind%20Waker%20%28USA%29.zip"
    
    if not args.rom:
        # Extract ROM name from URL
        args.rom = os.path.basename(unquote(args.url))
    
    # Print header
    print("🎮 ROM Archive Alternative Source Scanner")
    print("=========================================")
    print(f"Checking: {args.rom}")
    print(f"URL: {args.url}")
    
    # First check the original URL
    print("\n🔍 Checking original URL...")
    original_result = check_url_accessibility(args.url, show_headers=True)
    
    # Generate alternatives
    alternatives = generate_alternative_urls(args.url, args.rom)
    
    # Print alternatives
    print("\n🔄 Alternative URLs:")
    for i, alt in enumerate(alternatives, 1):
        print(f"{i}. {alt['source']}: {alt['url']}")
        print(f"   {alt['description']}")
    
    # Check all alternatives if requested
    if args.check_all:
        results = check_alternatives(alternatives)
        
        # Display summary
        print("\n📊 Summary:")
        working_alternatives = [alt for alt in results if alt['result'].get('accessible', False) and alt['result'].get('is_binary', False)]
        
        if working_alternatives:
            print(f"✅ Found {len(working_alternatives)} working alternatives:")
            for alt in working_alternatives:
                print(f"  - {alt['source']}: {alt['url']}")
            
            if args.save:
                # Save working alternatives to a file
                save_path = Path("working_rom_alternatives.json")
                with open(save_path, 'w') as f:
                    json.dump(working_alternatives, f, indent=2)
                print(f"\n💾 Saved working alternatives to {save_path}")
        else:
            print("❌ No working alternatives found.")
            print("\n💡 Suggestions:")
            print("1. Check if the site is currently down for maintenance")
            print("2. Try using a VPN or proxy to access the site")
            print("3. Check for alternative ROM sources online")
    else:
        print("\nUse --check-all to test all alternative URLs")

if __name__ == "__main__":
    main()
