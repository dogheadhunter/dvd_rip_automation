#!/usr/bin/env python3
"""
Quick SSL Test for ROM Downloads
"""
import asyncio
import ssl
import aiohttp

async def test_ssl():
    print("🔒 Testing SSL certificate handling...")
    
    # Create SSL context that ignores certificate errors
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            # Test with a sample ROM URL
            test_url = "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube/Animal%20Crossing%20(USA).zip"
            print(f"🌐 Testing connection to: {test_url}")
            
            async with session.head(test_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"✅ SSL Test Success!")
                print(f"📊 Status Code: {response.status}")
                print(f"📦 Content-Length: {response.headers.get('content-length', 'Unknown')} bytes")
                
                if response.headers.get('content-length'):
                    size_mb = int(response.headers['content-length']) / (1024 * 1024)
                    print(f"📦 File Size: {size_mb:.1f} MB")
                
                return True
                
        except Exception as e:
            print(f"❌ SSL Test Failed: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(test_ssl())
