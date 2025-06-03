#!/usr/bin/env python3
"""
Enhanced Modern Proxy Scraper - Phase 2: Advanced Header Randomization
======================================================================

This enhanced version includes:
- Comprehensive browser-specific header sets
- Realistic user-agent rotation with version randomization
- Advanced header fingerprint randomization
- Browser-specific behavior patterns
"""

import asyncio
import aiohttp
import time
import random
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class EnhancedModernProxyRotator:
    """Enhanced proxy rotator with advanced anti-detection features"""
    
    def __init__(self, proxy_count: int = 50, timeout: int = 10):
        self.proxy_count = proxy_count
        self.timeout = timeout
        self.proxies = []
        self.current_index = 0
        self.ua = UserAgent()
        
        # Enhanced browser profiles for realistic behavior
        self.browser_profiles = {
            'chrome': {
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ],
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept_encoding': 'gzip, deflate, br',
                'accept_language': [
                    'en-US,en;q=0.9',
                    'en-GB,en-US;q=0.9,en;q=0.8',
                    'en-US,en;q=0.9,es;q=0.8'
                ],
                'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec_ch_ua_mobile': '?0',
                'sec_ch_ua_platform': '"Windows"',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1'
            },
            'firefox': {
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'
                ],
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'accept_encoding': 'gzip, deflate, br',
                'accept_language': [
                    'en-US,en;q=0.5',
                    'en-GB,en;q=0.5',
                    'en-US,en;q=0.5,es;q=0.3'
                ],
                'upgrade_insecure_requests': '1'
            },
            'safari': {
                'user_agents': [
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
                ],
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept_encoding': 'gzip, deflate, br',
                'accept_language': [
                    'en-US,en;q=0.9',
                    'en-GB,en-US;q=0.9,en;q=0.8'
                ]
            },
            'edge': {
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
                ],
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept_encoding': 'gzip, deflate, br',
                'accept_language': [
                    'en-US,en;q=0.9',
                    'en-GB,en-US;q=0.9,en;q=0.8'
                ]
            }
        }
        
    async def fetch_proxy_list_async(self, url: str, session: aiohttp.ClientSession) -> List[str]:
        """Fetch proxy list from a URL using aiohttp"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    text = await response.text()
                    return [line.strip() for line in text.split('\n') if ':' in line]
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
        return []
    
    async def test_proxy_async(self, proxy: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        """Test if a proxy works using aiohttp"""
        try:
            proxy_url = f"http://{proxy}"
            async with session.get(
                'http://httpbin.org/ip',
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'http': proxy_url,
                        'https': proxy_url,
                        'ip': result.get('origin', 'Unknown')
                    }
        except Exception:
            pass
        return None
    
    async def find_proxies_async(self):
        """Find working proxies using modern async methods"""
        print(f"Finding {self.proxy_count} working proxies with enhanced sources...")
        
        # Enhanced proxy sources
        proxy_sources = [
            # API-based sources
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all",
            
            # GitHub-based sources (most reliable)
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
            "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt"
        ]
        
        all_proxy_candidates = []
        
        async with aiohttp.ClientSession() as session:
            # Fetch proxy lists concurrently
            tasks = [self.fetch_proxy_list_async(url, session) for url in proxy_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, list):
                    all_proxy_candidates.extend(result)
                    print(f"Fetched {len(result)} candidates from source {i+1}")
                elif isinstance(result, Exception):
                    print(f"Source {i+1} failed: {result}")
            
            # Clean and deduplicate
            clean_candidates = []
            seen = set()
            for candidate in all_proxy_candidates:
                if ':' in candidate and len(candidate.split(':')) == 2:
                    host, port = candidate.strip().split(':')
                    if host and port.isdigit() and candidate not in seen:
                        seen.add(candidate)
                        clean_candidates.append(candidate)
            
            print(f"Found {len(clean_candidates)} unique proxy candidates")
            
            # Test proxies in batches
            working_proxies = []
            batch_size = 20
            
            for i in range(0, len(clean_candidates), batch_size):
                if len(working_proxies) >= self.proxy_count:
                    break
                    
                batch = clean_candidates[i:i + batch_size]
                print(f"Testing batch {i//batch_size + 1}: {len(batch)} proxies...")
                
                tasks = [self.test_proxy_async(proxy, session) for proxy in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(results):
                    if isinstance(result, dict):
                        working_proxies.append(result)
                        print(f"✓ Working proxy: {batch[j]} -> IP: {result['ip']}")
                        
                        if len(working_proxies) >= self.proxy_count:
                            break
                
                await asyncio.sleep(1)
        
        self.proxies = working_proxies
        print(f"Successfully found {len(self.proxies)} working proxies")
        
    def get_next_proxy(self) -> Optional[Dict]:
        """Get the next proxy in rotation"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_enhanced_random_headers(self) -> Dict[str, str]:
        """PHASE 2: Enhanced header randomization with browser-specific patterns"""
        # Choose a random browser profile
        browser = random.choice(list(self.browser_profiles.keys()))
        profile = self.browser_profiles[browser]
        
        # Base headers from browser profile
        headers = {
            'User-Agent': random.choice(profile['user_agents']),
            'Accept': profile['accept'],
            'Accept-Encoding': profile['accept_encoding'],
            'Accept-Language': random.choice(profile['accept_language']),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Add browser-specific headers
        if browser == 'chrome':
            headers.update({
                'sec-ch-ua': profile['sec_ch_ua'],
                'sec-ch-ua-mobile': profile['sec_ch_ua_mobile'],
                'sec-ch-ua-platform': profile['sec_ch_ua_platform'],
                'Sec-Fetch-Dest': profile['sec_fetch_dest'],
                'Sec-Fetch-Mode': profile['sec_fetch_mode'],
                'Sec-Fetch-Site': profile['sec_fetch_site'],
                'Sec-Fetch-User': profile['sec_fetch_user']
            })
        elif browser == 'firefox':
            if 'upgrade_insecure_requests' in profile:
                headers['Upgrade-Insecure-Requests'] = profile['upgrade_insecure_requests']
        
        # Randomize additional optional headers
        optional_headers = {}
        
        # Cache control (50% chance)
        if random.choice([True, False]):
            optional_headers['Cache-Control'] = random.choice([
                'no-cache',
                'max-age=0',
                'no-cache, no-store, must-revalidate'
            ])
        
        # DNT header (70% chance)
        if random.random() < 0.7:
            optional_headers['DNT'] = '1'
        
        # Referer (60% chance)
        if random.random() < 0.6:
            optional_headers['Referer'] = random.choice([
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                'https://www.google.co.uk/',
                'https://search.yahoo.com/'
            ])
        
        # Pragma (30% chance)
        if random.random() < 0.3:
            optional_headers['Pragma'] = 'no-cache'
        
        # Add selected optional headers
        headers.update(optional_headers)
        
        return headers
    
    def get_random_headers(self) -> Dict[str, str]:
        """Backward compatibility - use enhanced headers"""
        return self.get_enhanced_random_headers()


# Keep the original class for backward compatibility
class ModernProxyRotator(EnhancedModernProxyRotator):
    """Backward compatible class name"""
    pass
