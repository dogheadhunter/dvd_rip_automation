#!/usr/bin/env python3
"""
Simple Direct ROM Download Test
==============================

This script tests direct ROM downloads without proxies to verify
if the issue is with proxies rather than URLs.
"""

import aiohttp
import asyncio
import sys
from pathlib import Path
import logging
import os
from urllib.parse import urlparse, unquote
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('direct_rom_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("direct-test")

async def download_rom_direct(url, output_dir):
    """Test downloading a ROM directly without proxies"""
    print(f"\n⬇️ Testing direct download from: {url}")
    
    # Parse the URL to get the filename
    url_parts = urlparse(url)
    rom_name = os.path.basename(unquote(url_parts.path))
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Path to save the file
    output_path = output_dir / rom_name
    
    # Headers with browser-like settings
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/octet-stream,application/zip,application/x-zip-compressed,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': f"{url_parts.scheme}://{url_parts.netloc}/",
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📥 Downloading: {rom_name}")
            
            # Download the ROM
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                print(f"📊 Status: {response.status}")
                print(f"📝 Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                # Check if we got redirected
                if response.history:
                    print(f"⤴️ Redirected from: {response.history[0].url} to {response.url}")
                
                # Check if we got HTML instead of ROM data
                first_chunk = await response.content.read(1024)
                first_chunk_text = first_chunk.decode('utf-8', errors='ignore').lower()
                
                if '<html' in first_chunk_text or '<!doctype html' in first_chunk_text:
                    print(f"❌ Received HTML content instead of ROM file")
                    
                    # Extract title if present
                    if '<title>' in first_chunk_text and '</title>' in first_chunk_text:
                        title_start = first_chunk_text.find('<title>') + 7
                        title_end = first_chunk_text.find('</title>')
                        page_title = first_chunk_text[title_start:title_end].strip()
                        print(f"📄 Error page title: {page_title}")
                    
                    # Save the HTML for debugging
                    debug_path = Path("debug_html")
                    debug_path.mkdir(exist_ok=True)
                    error_path = debug_path / f"error_{rom_name}.html"
                    
                    with open(error_path, 'wb') as f:
                        f.write(first_chunk)
                        # Read and write the rest of the content
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    print(f"💾 Saved error HTML to: {error_path}")
                    return False
                
                # Valid ROM content, save to file
                with open(output_path, 'wb') as f:
                    f.write(first_chunk)  # Write the first chunk we already read
                    
                    # Then download the rest
                    start_time = time.time()
                    downloaded = len(first_chunk)
                    
                    async for chunk in response.content.iter_chunked(1024*1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Calculate and display download speed
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed = downloaded / elapsed / (1024*1024)
                            print(f"\r📥 Downloaded: {downloaded/(1024*1024):.2f} MB ({speed:.2f} MB/s)", end="")
                
                # Complete
                file_size = output_path.stat().st_size
                print(f"\n✅ Download complete: {rom_name} ({file_size/(1024*1024):.2f} MB)")
                return True
                
    except Exception as e:
        print(f"❌ Error downloading ROM: {e}")
        logger.exception(f"Error downloading ROM: {e}")
        return False

async def main():
    """Main function to run the test"""
    print("🧪 DIRECT ROM DOWNLOAD TEST")
    print("===========================")
    print("Testing downloads without proxies to check if proxies are the issue")
    
    # Test URLs from the Zelda ROM list
    test_urls = [
        "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Legend%20of%20Zelda%2C%20The%20-%20The%20Wind%20Waker%20%28USA%29.zip"
    ]
    
    output_dir = "ROM_Downloads_Direct_Test"
    
    success_count = 0
    for url in test_urls:
        print(f"\n🔍 Testing URL: {url}")
        result = await download_rom_direct(url, output_dir)
        if result:
            success_count += 1
    
    print(f"\n🎮 Test Results: {success_count}/{len(test_urls)} downloads successful")
    
    if success_count == 0:
        print("\n❌ All direct downloads failed")
        print("This likely indicates that:")
        print("1. The ROM site may be blocking direct downloads")
        print("2. VPN or different IP might be needed")
        print("3. The URLs themselves may be incorrect or files removed")
    elif success_count < len(test_urls):
        print("\n⚠️ Some downloads succeeded while others failed")
        print("This may indicate selective blocking or throttling")
    else:
        print("\n✅ All direct downloads succeeded!")
        print("This suggests the issue is with proxy configuration:")
        print("1. Proxies may be detected/blocked by the ROM site")
        print("2. Proxy headers may need adjustment")
        print("3. Consider disabling proxies or finding higher quality ones")

if __name__ == "__main__":
    asyncio.run(main())
