#!/usr/bin/env python3
"""
Web Scraper with Free Proxy List Support

This script uses free proxy lists instead of ProxyBroker to avoid compatibility issues.
It downloads content from URLs with proxy rotation and header randomization.
"""

import os
import sys
import time
import random
import logging
import json
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class FreeProxyRotator:
    """Manages proxy rotation using free proxy sources"""
    
    def __init__(self, proxy_count: int = 50, timeout: int = 10):
        self.proxy_count = proxy_count
        self.timeout = timeout
        self.proxies = []
        self.current_index = 0
        self.ua = UserAgent()
        
    def fetch_free_proxies(self):
        """Fetch proxies from free proxy sources"""
        print(f"Fetching up to {self.proxy_count} free proxies...")
        
        # Multiple free proxy sources
        proxy_sources = [
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        ]
        
        all_proxies = []
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    proxy_list = response.text.strip().split('\n')
                    for proxy in proxy_list:
                        if ':' in proxy and len(proxy.split(':')) == 2:
                            host, port = proxy.strip().split(':')
                            if host and port.isdigit():
                                proxy_dict = {
                                    'http': f'http://{host}:{port}',
                                    'https': f'http://{host}:{port}'
                                }
                                all_proxies.append(proxy_dict)
                                
                    print(f"Found {len(proxy_list)} proxies from {source}")
                    
            except Exception as e:
                print(f"Error fetching from {source}: {e}")
                continue
                
        # Remove duplicates and limit count
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            proxy_str = proxy['http']
            if proxy_str not in seen:
                seen.add(proxy_str)
                unique_proxies.append(proxy)
                if len(unique_proxies) >= self.proxy_count:
                    break
                    
        self.proxies = unique_proxies
        print(f"Collected {len(self.proxies)} unique proxies")
        
        # Test a few proxies
        if self.proxies:
            self.test_proxies()
            
    def test_proxies(self, test_count: int = 5):
        """Test a sample of proxies to verify they work"""
        print("Testing sample proxies...")
        working_proxies = []
        
        test_proxies = random.sample(self.proxies, min(test_count, len(self.proxies)))
        
        for proxy in test_proxies:
            try:
                response = requests.get(
                    'https://httpbin.org/ip',
                    proxies=proxy,
                    timeout=self.timeout,
                    headers={'User-Agent': self.ua.random}
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"✓ Working proxy: {proxy['http']} -> IP: {result.get('origin', 'Unknown')}")
                    working_proxies.append(proxy)
                else:
                    print(f"✗ Failed proxy: {proxy['http']} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"✗ Failed proxy: {proxy['http']} (Error: {str(e)[:50]}...)")
                
        print(f"Tested {len(test_proxies)} proxies, {len(working_proxies)} working")
        
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


class WebScraperWithFreeProxies:
    """Web scraper that rotates free proxies and headers"""
    
    def __init__(self, 
                 proxy_count: int = 20,
                 delay_range: Tuple[float, float] = (1.0, 3.0),
                 max_retries: int = 3,
                 timeout: int = 15,
                 use_proxies: bool = True):
        self.proxy_rotator = FreeProxyRotator(proxy_count) if use_proxies else None
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.timeout = timeout
        self.use_proxies = use_proxies
        self.session = requests.Session()
        self.ua = UserAgent()
        
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
        
    def initialize(self):
        """Initialize the scraper by finding proxies"""
        if self.use_proxies and self.proxy_rotator:
            self.proxy_rotator.fetch_free_proxies()
        else:
            print("Running without proxy support")
            
    def get_random_headers(self) -> Dict[str, str]:
        """Generate random headers (fallback if no proxy rotator)"""
        if self.proxy_rotator:
            return self.proxy_rotator.get_random_headers()
            
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1'
        }
        
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
                proxy = None
                if self.use_proxies and self.proxy_rotator:
                    proxy = self.proxy_rotator.get_next_proxy()
                    
                headers = self.get_random_headers()
                
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


def main():
    """Main function to run the scraper"""
    print("=== Web Scraper with Free Proxy Support ===")
    
    # Get input file
    url_file = input("Enter path to URL file (default: sample_urls.txt): ").strip()
    if not url_file:
        url_file = "sample_urls.txt"
        
    # Get output directory
    output_dir = input("Enter output directory (default: downloads): ").strip()
    if not output_dir:
        output_dir = "downloads"
        
    # Ask about proxy usage
    use_proxies_input = input("Use proxies? (y/n, default: n): ").strip().lower()
    use_proxies = use_proxies_input == 'y'
    
    proxy_count = 0
    if use_proxies:
        try:
            proxy_count = int(input("Number of proxies to fetch (default: 20): ").strip() or "20")
        except ValueError:
            proxy_count = 20
        
    # Initialize scraper
    scraper = WebScraperWithFreeProxies(
        proxy_count=proxy_count,
        use_proxies=use_proxies
    )
    
    try:
        # Initialize proxies if needed
        scraper.initialize()
        
        # Load URLs
        urls = scraper.load_urls_from_file(url_file)
        
        if not urls:
            print("No URLs found in the file.")
            return
            
        print(f"\nFound {len(urls)} URLs to scrape")
        if use_proxies:
            proxy_count = len(scraper.proxy_rotator.proxies) if scraper.proxy_rotator else 0
            print(f"Using {proxy_count} proxies for rotation")
        else:
            print("Running without proxies (direct connection)")
            
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
    main()
