#!/usr/bin/env python3
"""
Test script to reproduce the ProxyBroker error
"""
import asyncio
import proxybroker

async def test_proxybroker():
    """Test ProxyBroker to reproduce the error"""
    print("Testing ProxyBroker...")
    
    try:
        # This should trigger the error
        broker = proxybroker.Broker(
            judges=['http://httpbin.org/ip'],
            providers=['free-proxy-list.net'],
            max_conn=10,
            max_tries=1,
            timeout=5
        )
        
        proxies = []
        
        async def save_proxy(proxy):
            proxies.append(proxy)
            print(f"Found proxy: {proxy.host}:{proxy.port}")
        
        await broker.find(
            types=['HTTP'],
            strict=True,
            limit=2,
            callback=save_proxy
        )
        
        print(f"Successfully found {len(proxies)} proxies")
        
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_proxybroker())
