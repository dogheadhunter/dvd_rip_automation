#!/usr/bin/env python3
"""
Web Scraper with Proxy and Header Rotation

This script downloads content from URLs listed in a text file using:
- Beautiful Soup for HTML parsing
- Rotating proxies from ProxyBroker
- Rotating user agents and headers
- Error handling and retry logic
- Rate limiting to avoid overwhelming servers

Requirements:
pip install beautifulsoup4 requests proxybroker fake-useragent
"""

import os
import sys
import time
import random
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import proxybroker


class ProxyRotator:
    """Manages proxy rotation using ProxyBroker"""
    
    def __init__(self, proxy_count: int = 50, timeout: int = 10):
        self.proxy_count = proxy_count
        self.timeout = timeout
        self.proxies = []
        self.current_index = 0
        self.ua = UserAgent()
        
    async def find_proxies(self):
        """Find working proxies using ProxyBroker"""
        print(f"Finding {self.proxy_count} working proxies...")
        
        proxies = []
        
        async def save_proxy(proxy):
            """Callback to save found proxies"""
            if len(proxies) < self.proxy_count:
                proxy_dict = {
                    'http': f'http://{proxy.host}:{proxy.port}',
                    'https': f'http://{proxy.host}:{proxy.port}'
                }
                proxies.append(proxy_dict)
                print(f"Found proxy: {proxy.host}:{proxy.port} ({len(proxies)}/{self.proxy_count})")
        
        # Find proxies with specific criteria
        broker = proxybroker.Broker(
            judges=['http://httpbin.org/ip'],
            providers=['free-proxy-list.net', 'proxy-list.download'],
            max_conn=200,
            max_tries=3,
            timeout=self.timeout
        )
        
        await broker.find(
            types=['HTTP', 'HTTPS'],
            strict=True,
            limit=self.proxy_count,
            callback=save_proxy
        )
        
        self.proxies = proxies
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


class WebScraperWithProxies:
    """Web scraper that rotates proxies and headers"""
    
    def __init__(self, 
                 proxy_count: int = 20,
                 delay_range: Tuple[float, float] = (1.0, 3.0),
                 max_retries: int = 3,
                 timeout: int = 15):
        self.proxy_rotator = ProxyRotator(proxy_count)
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the scraper by finding proxies"""
        await self.proxy_rotator.find_proxies()
        
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
                proxy_info = f"{list(proxy.values())[0]}" if proxy else "No proxy"
                self.logger.info(f"Attempt {attempt + 1} for {url} using {proxy_info}")
                
                # Make request
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=proxy,
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
    """Main function to run the scraper"""
    print("=== Web Scraper with Proxy Rotation ===")
    
    # Get input file
    url_file = input("Enter path to URL file (default: urls.txt): ").strip()
    if not url_file:
        url_file = "urls.txt"
        
    # Get output directory
    output_dir = input("Enter output directory (default: downloads): ").strip()
    if not output_dir:
        output_dir = "downloads"
        
    # Get number of proxies
    try:
        proxy_count = int(input("Number of proxies to find (default: 20): ").strip() or "20")
    except ValueError:
        proxy_count = 20
        
    # Initialize scraper
    scraper = WebScraperWithProxies(proxy_count=proxy_count)
    
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
            
        # Start scraping
        scraper.scrape_urls(urls, output_dir)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        

if __name__ == "__main__":
    # Create sample URL file if it doesn't exist
    if not os.path.exists("urls.txt"):
        with open("urls.txt", 'w') as f:
            f.write("# Sample URLs to scrape\n")
            f.write("https://httpbin.org/ip\n")
            f.write("https://httpbin.org/user-agent\n")
            f.write("https://httpbin.org/headers\n")
        print("Created sample urls.txt file")
    
    # Run the scraper
    asyncio.run(main())
