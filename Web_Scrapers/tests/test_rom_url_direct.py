#!/usr/bin/env python3
"""
ROM URL Tester - Direct Access Test Tool
========================================

This tool tests direct access to ROM URLs to determine if
the issue is with proxies or with the website itself.
"""

import aiohttp
import asyncio
import sys
from urllib.parse import unquote
import argparse

async def test_url_direct(url, show_content=False):
    """Test direct access to a URL without proxies"""
    print(f"\n🔍 Testing direct access to URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://myrient.erista.me/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                print(f"📊 Status Code: {response.status}")
                print(f"📝 Content Type: {response.headers.get('content-type', 'unknown')}")
                
                # Check for redirects
                if response.history:
                    print(f"⤴️  Redirected from: {response.history[0].url} to {response.url}")
                
                # Get content and check if it's HTML
                content = await response.read()
                content_start = content[:500].decode('utf-8', errors='ignore')
                
                is_html = '<html' in content_start.lower() or '<!doctype html' in content_start.lower()
                
                if is_html:
                    print(f"❌ Received HTML content instead of a file")
                    if show_content:
                        print(f"\nContent Preview:\n{content_start}...\n")
                else:
                    content_length = response.headers.get('content-length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        print(f"✅ Received binary content - Size: {size_mb:.2f} MB")
                    else:
                        print(f"✅ Received binary content - Size: {len(content)} bytes")
    
    except Exception as e:
        print(f"❌ Error accessing URL: {e}")

async def test_with_multiple_user_agents(url):
    """Test URL with multiple user agents to see if site is blocking based on UA"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',  # Testing if blocking based on bots
    ]
    
    print("\n🧪 Testing URL with multiple user agents:")
    
    for ua in user_agents:
        try:
            headers = {
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://myrient.erista.me/',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    content_type = response.headers.get('content-type', 'unknown')
                    is_html = 'text/html' in content_type
                    
                    print(f"🔍 UA: {ua[:30]}... | Status: {response.status} | HTML: {'Yes' if is_html else 'No'}")
        
        except Exception as e:
            print(f"❌ Error with UA '{ua[:30]}...': {e}")

async def main():
    parser = argparse.ArgumentParser(description='Test direct access to ROM URLs')
    parser.add_argument('url', nargs='?', help='URL to test')
    parser.add_argument('--show-content', action='store_true', help='Show content preview')
    parser.add_argument('--multiple-ua', action='store_true', help='Test with multiple user agents')
    
    args = parser.parse_args()
    
    if not args.url:
        # Default test URL
        url = "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Legend%20of%20Zelda%2C%20The%20-%20The%20Wind%20Waker%20%28USA%29.zip"
    else:
        url = args.url
    
    print("🛠️  ROM URL Direct Access Tester")
    print("================================")
    print(f"Testing URL: {unquote(url)}")
    
    await test_url_direct(url, args.show_content)
    
    if args.multiple_ua:
        await test_with_multiple_user_agents(url)
    
    print("\n📝 Conclusions:")
    print("1. If you received HTML instead of binary content, the website may be:")
    print("   - Blocking direct downloads (needs referrer)")
    print("   - Requiring authentication")
    print("   - Blocking based on IP/geolocation")
    print("   - Serving error pages due to high traffic")
    print("2. If direct access works but proxies fail, your proxies may be:")
    print("   - Blocked by the website")
    print("   - Not configured properly")
    print("   - Not forwarding necessary headers")

if __name__ == "__main__":
    asyncio.run(main())
