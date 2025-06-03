#!/usr/bin/env python3
"""
🧪 Phase 1 & 2 Verification Script
=================================

This script tests the proxy rotation and header randomization
features implemented in Phase 1 and Phase 2.
"""

import sys
import asyncio
import aiohttp
import ssl
from pathlib import Path

# Add the working_scrapers directory to path
sys.path.append(str(Path(__file__).parent.parent / "working_scrapers"))

try:
    from modern_proxy_scraper_enhanced import EnhancedModernProxyRotator
except ImportError:
    print("❌ Error: Could not import enhanced proxy scraper")
    print("Checking if original proxy scraper exists...")
    try:
        from modern_proxy_scraper import ModernProxyRotator
        print("✅ Found original proxy scraper, will use that for testing")
        USE_ENHANCED = False
    except ImportError:
        print("❌ No proxy scrapers found!")
        sys.exit(1)
else:
    print("✅ Found enhanced proxy scraper")
    USE_ENHANCED = True

async def test_proxy_discovery():
    """Test proxy discovery functionality"""
    print("\n🔍 Testing Proxy Discovery (Phase 1)")
    print("="*50)
    
    if USE_ENHANCED:
        rotator = EnhancedModernProxyRotator(proxy_count=5, timeout=8)
    else:
        rotator = ModernProxyRotator(proxy_count=5, timeout=8)
    
    try:
        await rotator.find_proxies_async()
        
        if rotator.proxies:
            print(f"✅ Found {len(rotator.proxies)} working proxies")
            for i, proxy in enumerate(rotator.proxies[:3], 1):
                print(f"   {i}. {proxy.get('http', 'Unknown')} -> IP: {proxy.get('ip', 'Unknown')}")
            return True
        else:
            print("❌ No working proxies found")
            return False
            
    except Exception as e:
        print(f"❌ Proxy discovery failed: {e}")
        return False

def test_header_randomization():
    """Test header randomization functionality"""
    print("\n🎭 Testing Header Randomization (Phase 2)")
    print("="*50)
    
    if USE_ENHANCED:
        rotator = EnhancedModernProxyRotator()
        
        # Test multiple header generations
        print("✅ Enhanced header randomization available")
        for i in range(3):
            headers = rotator.get_enhanced_random_headers()
            user_agent = headers.get('User-Agent', 'Unknown')
            browser = "Chrome" if "Chrome" in user_agent else "Firefox" if "Firefox" in user_agent else "Other"
            print(f"   Test {i+1}: {browser} - {user_agent[:50]}...")
            
        return True
    else:
        print("⚠️  Enhanced headers not available, using basic randomization")
        return False

async def test_http_requests():
    """Test actual HTTP requests with proxy and headers"""
    print("\n🌐 Testing HTTP Requests with Proxy & Headers")
    print("="*50)
    
    if USE_ENHANCED:
        rotator = EnhancedModernProxyRotator(proxy_count=3, timeout=10)
    else:
        rotator = ModernProxyRotator(proxy_count=3, timeout=10)
    
    # Find proxies first
    await rotator.find_proxies_async()
    
    if not rotator.proxies:
        print("❌ No proxies available for testing")
        return False
    
    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(limit=5, ssl=ssl_context)
    timeout = aiohttp.ClientTimeout(total=15)
    
    success_count = 0
    test_count = 3
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        for i in range(test_count):
            try:
                # Get proxy and headers
                proxy_info = rotator.get_next_proxy()
                proxy = proxy_info.get('http') if proxy_info else None
                
                if USE_ENHANCED:
                    headers = rotator.get_enhanced_random_headers()
                else:
                    headers = rotator.get_random_headers()
                
                # Test with httpbin.org/ip to see our IP
                async with session.get(
                    'http://httpbin.org/ip',
                    headers=headers,
                    proxy=proxy
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        ip = data.get('origin', 'Unknown')
                        connection_type = "Proxy" if proxy else "Direct"
                        user_agent = headers.get('User-Agent', 'Unknown')[:40]
                        print(f"   ✅ Test {i+1}: {connection_type} - IP: {ip} - UA: {user_agent}...")
                        success_count += 1
                    else:
                        print(f"   ❌ Test {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                print(f"   ❌ Test {i+1}: {e}")
                
    print(f"\n📊 Success Rate: {success_count}/{test_count} ({success_count/test_count*100:.1f}%)")
    return success_count > 0

async def main():
    """Main verification function"""
    print("🧪 ROM Downloader Phase 1 & 2 Verification")
    print("="*60)
    
    results = {}
    
    # Test proxy discovery
    results['proxy_discovery'] = await test_proxy_discovery()
    
    # Test header randomization
    results['header_randomization'] = test_header_randomization()
    
    # Test HTTP requests
    results['http_requests'] = await test_http_requests()
    
    # Summary
    print("\n📋 VERIFICATION SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("\n🎉 Phase 1 & 2 verification SUCCESSFUL!")
        print("Ready to proceed with Phase 3 (Behavioral Randomization)")
    else:
        print("\n⚠️  Some tests failed - Phase 1 & 2 need attention before Phase 3")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Verification cancelled by user")
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
