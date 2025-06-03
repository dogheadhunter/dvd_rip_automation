#!/usr/bin/env python3
"""
Simple ROM URL test script
==========================

Tests a ROM URL using direct access and prints detailed diagnostics.
"""

import requests
from urllib.parse import unquote

def test_url(url):
    """Test a URL with a standard browser-like request"""
    print(f"Testing URL: {unquote(url)}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://myrient.erista.me/',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'unknown')}")
        
        if 'text/html' in response.headers.get('content-type', ''):
            content = response.text[:500]
            print(f"\nHTML Content Preview:\n{content}...\n")
            
            if '<title>' in content and '</title>' in content:
                title_start = content.find('<title>') + 7
                title_end = content.find('</title>')
                page_title = content[title_start:title_end].strip()
                print(f"Page Title: {page_title}")
        else:
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                print(f"Binary Content - Size: {size_mb:.2f} MB")
            else:
                # Read first chunk to estimate size
                chunk = next(response.iter_content(chunk_size=8192), b"")
                print(f"Binary Content - First Chunk Size: {len(chunk)} bytes")
                
        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test URL for Legend of Zelda - Wind Waker
    url = "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Legend%20of%20Zelda%2C%20The%20-%20The%20Wind%20Waker%20%28USA%29.zip"
    
    print("ROM URL Simple Test")
    print("==================")
    test_url(url)
