#!/usr/bin/env python3
"""
ROM Downloader URL Validator and Repair Module

This module provides functionality to validate and repair ROM download URLs.
It's designed to be imported by the main ROM downloader to help handle problematic URLs.
"""

import requests
import logging
from urllib.parse import urlparse, unquote, quote
import re
import os
import time
import random

logger = logging.getLogger(__name__)

class RomUrlValidator:
    """URL validation and repair for ROM downloader"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/octet-stream,application/zip,application/x-zip-compressed,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        
        # Known ROM hosting domains and their alternatives
        self.alternative_domains = {
            "myrient.erista.me": ["archive.org/download/nintendo-gamecube-romset", 
                                  "wowroms.com/en/roms",
                                  "romsgames.net/roms"],
            "www.myrient.erista.me": ["archive.org/download/nintendo-gamecube-romset",
                                     "wowroms.com/en/roms",
                                     "romsgames.net/roms"]
        }
        
        # URL path transformations to try
        self.path_transformations = [
            # Original path
            lambda path: path,
            # Remove complex folder structure
            lambda path: "/" + os.path.basename(path),
            # Try removing encoding in the path
            lambda path: unquote(path)
        ]
    
    def validate_url(self, url, rom_name):
        """
        Validate a ROM URL and check if it's accessible
        Returns dict with validation status and info
        """
        logger.info(f"Validating URL: {url}")
        
        try:
            # First try with the original URL
            headers = self.headers.copy()
            # Add proper referrer
            url_parts = urlparse(url)
            base_url = f"{url_parts.scheme}://{url_parts.netloc}"
            headers['Referer'] = base_url
            
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            
            # Log the details
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Content type: {response.headers.get('content-type', 'unknown')}")
            
            # Check if it's accessible and likely a valid binary file
            content_type = response.headers.get('content-type', '').lower()
            is_html = 'text/html' in content_type or 'text/plain' in content_type
            
            if response.status_code == 200 and not is_html:
                # Looks like a good URL
                return {
                    'valid': True,
                    'url': url,
                    'status_code': response.status_code,
                    'content_type': content_type
                }
            else:
                # URL doesn't seem valid, generate alternatives
                return {
                    'valid': False,
                    'url': url,
                    'status_code': response.status_code,
                    'content_type': content_type,
                    'is_html': is_html
                }
                
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return {
                'valid': False,
                'url': url,
                'error': str(e)
            }
    
    def generate_alternative_urls(self, url, rom_name):
        """
        Generate alternative URLs for a ROM
        Returns a list of alternative URLs to try
        """
        logger.info(f"Generating alternative URLs for: {rom_name}")
        
        url_parts = urlparse(url)
        original_domain = url_parts.netloc
        original_path = url_parts.path
        scheme = url_parts.scheme
        
        alternatives = []
        
        # Try domain alternatives
        if original_domain in self.alternative_domains:
            for alt_domain in self.alternative_domains[original_domain]:
                # Try different path transformations with each domain
                for transform in self.path_transformations:
                    transformed_path = transform(original_path)
                    
                    # Handle archive.org specially
                    if "archive.org" in alt_domain:
                        # Extract console from path if possible
                        console = "gamecube"  # Default
                        console_match = re.search(r'Nintendo\s*-\s*(\w+)', original_path, re.IGNORECASE)
                        if console_match:
                            console = console_match.group(1).lower()
                        
                        alt_url = f"https://{alt_domain}/{quote(rom_name)}"
                    else:
                        # For other domains
                        alt_url = f"{scheme}://{alt_domain}{transformed_path}"
                    
                    alternatives.append(alt_url)
        
        # Try www / non-www variants
        if original_domain.startswith('www.'):
            no_www_domain = original_domain[4:]
            alt_url = f"{scheme}://{no_www_domain}{original_path}"
            alternatives.append(alt_url)
        else:
            www_domain = f"www.{original_domain}"
            alt_url = f"{scheme}://{www_domain}{original_path}"
            alternatives.append(alt_url)
        
        # Try HTTPS if using HTTP
        if scheme == 'http':
            alt_url = f"https://{original_domain}{original_path}"
            alternatives.append(alt_url)
        
        # Remove duplicates
        unique_alternatives = list(dict.fromkeys(alternatives))
        
        if self.debug:
            logger.info(f"Generated {len(unique_alternatives)} alternative URLs")
            for i, alt in enumerate(unique_alternatives, 1):
                logger.info(f"Alternative {i}: {alt}")
        
        return unique_alternatives
    
    def find_working_url(self, original_url, rom_name, max_attempts=3):
        """
        Try to find a working URL for a ROM
        Returns a working URL or the original URL if none work
        """
        logger.info(f"Finding working URL for: {rom_name}")
        
        # First validate the original URL
        validation = self.validate_url(original_url, rom_name)
        if validation.get('valid', False):
            logger.info(f"Original URL is valid: {original_url}")
            return original_url
        
        # Generate alternatives
        alternatives = self.generate_alternative_urls(original_url, rom_name)
        
        # Try each alternative
        for i, alt_url in enumerate(alternatives):
            logger.info(f"Trying alternative URL {i+1}/{len(alternatives)}: {alt_url}")
            
            # Add some delay to avoid rate limiting
            time.sleep(random.uniform(1, 2))
            
            validation = self.validate_url(alt_url, rom_name)
            if validation.get('valid', False):
                logger.info(f"Found working alternative URL: {alt_url}")
                return alt_url
        
        # If we get here, no alternatives worked
        logger.warning(f"No working URLs found for: {rom_name}")
        return original_url

# Test function if run directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test URL validation
    validator = RomUrlValidator(debug=True)
    
    test_url = "https://myrient.erista.me/files/Redump/Nintendo%20-%20GameCube%20-%20NKit%20RVZ%20%5Bzstd-19-128k%5D/Legend%20of%20Zelda%2C%20The%20-%20The%20Wind%20Waker%20%28USA%29.zip"
    test_rom = "Legend of Zelda, The - The Wind Waker (USA).zip"
    
    print("Testing URL validation...")
    validation = validator.validate_url(test_url, test_rom)
    print(f"Validation result: {validation}")
    
    print("\nGenerating alternative URLs...")
    alternatives = validator.generate_alternative_urls(test_url, test_rom)
    for i, alt in enumerate(alternatives, 1):
        print(f"{i}. {alt}")
    
    print("\nFinding working URL...")
    working_url = validator.find_working_url(test_url, test_rom)
    print(f"Working URL: {working_url}")
