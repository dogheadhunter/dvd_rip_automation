#!/usr/bin/env python3
"""
Test script to isolate the ProxyBroker issue
"""

import asyncio
import proxybroker

async def test_proxybroker():
    """Test ProxyBroker functionality"""
    print("Testing ProxyBroker...")
    
    try:
        # Create broker
        broker = proxybroker.Broker(
            judges=['http://httpbin.org/ip'],
            providers=['free-proxy-list.net'],
            max_conn=10,
            max_tries=2,
            timeout=5
        )
        
        proxies = []
        
        async def save_proxy(proxy):
            proxies.append(proxy)
            print(f"Found proxy: {proxy.host}:{proxy.port}")
            if len(proxies) >= 3:  # Stop after finding 3 proxies
                return
        
        print("Starting proxy search...")
        await broker.find(
            types=['HTTP'],
            strict=True,
            limit=3,
            callback=save_proxy
        )
        
        print(f"Found {len(proxies)} proxies successfully")
        
    except Exception as e:
        print(f"ProxyBroker error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_proxybroker())
