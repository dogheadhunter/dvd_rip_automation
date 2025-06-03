#!/usr/bin/env python3
"""
Fixed ProxyBroker Integration for Modern Python

This script works around the ProxyBroker compatibility issues by:
1. Using alternative proxy discovery methods
2. Implementing modern asyncio patterns
3. Providing the same functionality without ProxyBroker dependency
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


class ModernProxyRotator:
    """Modern proxy rotator that works with current Python versions"""
    
    def __init__(self, proxy_count: int = 50, timeout: int = 10):
        self.proxy_count = proxy_count
        self.timeout = timeout
        self.proxies = []
        self.current_index = 0
        self.ua = UserAgent()
        
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
        print(f"Finding {self.proxy_count} working proxies using modern async methods...")
          # Multiple proxy sources - expanded with more GitHub sources for better coverage
        proxy_sources = [
            # API-based sources
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all",
            
            # GitHub-based sources (tend to be more reliable)
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
            "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
            
            # Additional backup sources
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
            
            # Clean and deduplicate proxy candidates
            clean_candidates = []
            seen = set()
            for candidate in all_proxy_candidates:
                if ':' in candidate and len(candidate.split(':')) == 2:
                    host, port = candidate.strip().split(':')
                    if host and port.isdigit() and candidate not in seen:
                        seen.add(candidate)
                        clean_candidates.append(candidate)
            
            print(f"Found {len(clean_candidates)} unique proxy candidates")
            
            # Test proxies concurrently (in batches to avoid overwhelming)
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
                
                # Small delay between batches
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
    
    def get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.5',
                'en-GB,en;q=0.5',
                'es-ES,es;q=0.9',
                'fr-FR,fr;q=0.9',
                'de-DE,de;q=0.9'
            ]),
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': random.choice(['no-cache', 'max-age=0']),
            'DNT': '1'
        }
        
        # Sometimes add additional headers
        if random.choice([True, False]):
            headers['Referer'] = random.choice([
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/'
            ])
            
        return headers


class ModernWebScraperWithProxies:
    """Modern web scraper that works with current Python versions"""
    
    def __init__(self, 
                 proxy_count: int = 20,
                 delay_range: Tuple[float, float] = (1.0, 3.0),
                 max_retries: int = 3,
                 timeout: int = 15):
        self.proxy_rotator = ModernProxyRotator(proxy_count)
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('modern_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the scraper by finding proxies"""
        await self.proxy_rotator.find_proxies_async()
        
    def load_urls_from_file(self, file_path: str) -> List[str]:
        """Load URLs from a text file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"URL file not found: {file_path}")
            
        urls = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # Skip empty lines and comments
                    urls.append(url)
                    
        self.logger.info(f"Loaded {len(urls)} URLs from {file_path}")
        return urls
    
    def download_page(self, url: str) -> Optional[BeautifulSoup]:
        """Download a single page with proxy and header rotation"""
        for attempt in range(self.max_retries):
            try:
                # Get proxy and headers
                proxy = self.proxy_rotator.get_next_proxy()
                headers = self.proxy_rotator.get_random_headers()
                
                # Log attempt
                proxy_info = f"{proxy['http']}" if proxy else "No proxy"
                self.logger.info(f"Attempt {attempt + 1} for {url} using {proxy_info}")
                
                # Make request
                proxies = {'http': proxy['http'], 'https': proxy['https']} if proxy else None
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=proxies,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # Parse with Beautiful Soup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                self.logger.info(f"Successfully downloaded: {url}")
                return soup
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Error downloading {url} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    # Wait before retry
                    wait_time = random.uniform(2, 5)
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed to download {url} after {self.max_retries} attempts")
                    
        return None
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract content from the parsed HTML"""
        if not soup:
            return {'url': url, 'error': 'Failed to parse HTML'}
            
        content = {
            'url': url,
            'title': '',
            'text': '',
            'links': [],
            'images': []
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = title_tag.get_text().strip()
            
        # Extract main text (remove script and style content)
        for script in soup(["script", "style"]):
            script.decompose()
        content['text'] = soup.get_text().strip()
        
        # Extract links
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            content['links'].append({
                'url': full_url,
                'text': link.get_text().strip()
            })
            
        # Extract images
        for img in soup.find_all('img', src=True):
            full_url = urljoin(url, img['src'])
            content['images'].append({
                'url': full_url,
                'alt': img.get('alt', '').strip()
            })
            
        return content
    
    def save_content(self, content: Dict, output_dir: str = 'downloads'):
        """Save extracted content to files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Create filename from URL
        parsed = urlparse(content['url'])
        filename = f"{parsed.netloc}_{parsed.path.replace('/', '_')}"
        filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
        
        if not filename or filename == '_':
            filename = f"page_{hash(content['url']) % 10000}"
            
        # Save as text file
        text_file = os.path.join(output_dir, f"{filename}.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"URL: {content['url']}\n")
            f.write(f"Title: {content['title']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(content['text'])
            
        # Save links as separate file
        links_file = os.path.join(output_dir, f"{filename}_links.txt")
        with open(links_file, 'w', encoding='utf-8') as f:
            for link in content['links']:
                f.write(f"{link['url']}\t{link['text']}\n")
                
        self.logger.info(f"Saved content to {text_file}")
    
    def scrape_urls(self, urls: List[str], output_dir: str = 'downloads'):
        """Scrape multiple URLs with delay and proxy rotation"""
        total_urls = len(urls)
        successful = 0
        failed = 0
        
        self.logger.info(f"Starting to scrape {total_urls} URLs")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing {i}/{total_urls}: {url}")
            
            # Download page
            soup = self.download_page(url)
            
            if soup:
                # Extract content
                content = self.extract_content(soup, url)
                
                # Save content
                self.save_content(content, output_dir)
                successful += 1
            else:
                failed += 1
                
            # Random delay between requests
            if i < total_urls:  # Don't delay after the last URL
                delay = random.uniform(*self.delay_range)
                self.logger.info(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)
                
        self.logger.info(f"Scraping completed. Success: {successful}, Failed: {failed}")


async def main():
    """Main function to run the modern scraper"""
    print("=== Modern Web Scraper with Fixed Proxy Support ===")
    
    # Get input file
    url_file = input("Enter path to URL file (default: sample_urls.txt): ").strip()
    if not url_file:
        url_file = "sample_urls.txt"
        
    # Get output directory
    output_dir = input("Enter output directory (default: modern_downloads): ").strip()
    if not output_dir:
        output_dir = "modern_downloads"
        
    # Get number of proxies
    try:
        proxy_count = int(input("Number of proxies to find (default: 20): ").strip() or "20")
    except ValueError:
        proxy_count = 20
        
    # Initialize scraper
    scraper = ModernWebScraperWithProxies(proxy_count=proxy_count)
    
    try:
        # Initialize proxies
        await scraper.initialize()
        
        if not scraper.proxy_rotator.proxies:
            print("Warning: No proxies found. Continuing without proxies...")
            
        # Load URLs
        urls = scraper.load_urls_from_file(url_file)
        
        if not urls:
            print("No URLs found in the file.")
            return
            
        print(f"\nFound {len(urls)} URLs to scrape")
        proxy_count = len(scraper.proxy_rotator.proxies)
        print(f"Using {proxy_count} working proxies for rotation")
        
        proceed = input("\nProceed with scraping? (y/n): ").strip().lower()
        
        if proceed == 'y':
            # Start scraping
            scraper.scrape_urls(urls, output_dir)
            print(f"\nScraping completed! Check the '{output_dir}' folder for results.")
        else:
            print("Scraping cancelled.")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        

if __name__ == "__main__":
    # Add missing import
    import os
    
    # Install aiohttp if not present
    try:
        import aiohttp
    except ImportError:
        print("Installing aiohttp...")
        import subprocess
        subprocess.run(['pip', 'install', 'aiohttp'])
        import aiohttp
    
    # Only run the scraper if directly executed, not imported
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Scraper cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
