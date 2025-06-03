#!/usr/bin/env python3
"""
Simple Web Scraper with Header Rotation (No Proxy Dependency)

This is a simplified version that works without ProxyBroker for testing.
It still rotates headers and user agents for better anonymity.
"""

import os
import sys
import time
import random
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class SimpleWebScraper:
    """Web scraper with header rotation (no proxy requirement)"""
    
    def __init__(self, 
                 delay_range: Tuple[float, float] = (1.0, 3.0),
                 max_retries: int = 3,
                 timeout: int = 15):
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.timeout = timeout
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
        """Download a single page with header rotation"""
        for attempt in range(self.max_retries):
            try:
                # Get random headers
                headers = self.get_random_headers()
                
                # Log attempt
                self.logger.info(f"Attempt {attempt + 1} for {url}")
                
                # Make request
                response = self.session.get(
                    url,
                    headers=headers,
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
        """Scrape multiple URLs with delay and header rotation"""
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
    print("=== Simple Web Scraper with Header Rotation ===")
    
    # Get input file
    url_file = input("Enter path to URL file (default: sample_urls.txt): ").strip()
    if not url_file:
        url_file = "sample_urls.txt"
        
    # Get output directory
    output_dir = input("Enter output directory (default: downloads): ").strip()
    if not output_dir:
        output_dir = "downloads"
        
    # Initialize scraper
    scraper = SimpleWebScraper()
    
    try:
        # Load URLs
        urls = scraper.load_urls_from_file(url_file)
        
        if not urls:
            print("No URLs found in the file.")
            return
            
        print(f"Found {len(urls)} URLs to scrape")
        proceed = input("Proceed with scraping? (y/n): ").strip().lower()
        
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
