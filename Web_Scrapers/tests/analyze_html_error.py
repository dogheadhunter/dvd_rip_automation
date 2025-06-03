#!/usr/bin/env python3
"""
HTML Error Page Analyzer
=======================

This script analyzes HTML error pages from failed ROM downloads
to help diagnose the issue.
"""

import os
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
import argparse

def analyze_html_file(file_path):
    """Analyze an HTML file to extract useful information about the error"""
    print(f"\n🔍 Analyzing HTML file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # Use BeautifulSoup to parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract key information
        title = soup.title.text if soup.title else "No title found"
        print(f"📄 Page Title: {title}")
        
        # Look for common error messages
        error_patterns = [
            r'access denied',
            r'forbidden',
            r'not found',
            r'error',
            r'blocked',
            r'captcha',
            r'cloudflare',
            r'sorry',
            r'unavailable',
            r'throttl',
            r'limit',
            r'protect'
        ]
        
        print("\n🔎 Searching for error indicators:")
        found_patterns = set()
        for pattern in error_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"✓ Found '{pattern}' ({len(matches)} occurrences)")
                found_patterns.add(pattern)
        
        if not found_patterns:
            print("No common error patterns found")
        
        # Check for redirects
        meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'refresh', re.I)})
        if meta_refresh:
            print(f"\n↪️ Found meta refresh redirect: {meta_refresh.get('content')}")
        
        # Check for JavaScript redirects
        js_redirects = re.search(r'window\.location', html_content)
        if js_redirects:
            print("\n↪️ Found JavaScript redirect (window.location)")
        
        # Extract potential error messages
        print("\n📝 Potential error messages:")
        error_containers = soup.find_all(['div', 'p', 'span', 'h1', 'h2', 'h3', 'h4'], 
                                        class_=re.compile(r'error|alert|message|notification', re.I))
        
        if error_containers:
            for container in error_containers[:5]:  # Limit to first 5 to avoid too much output
                text = container.get_text(strip=True)
                if text and len(text) > 10:  # Skip very short texts
                    print(f"- {text[:100]}...")
        else:
            print("No specific error messages found in common error containers")
        
        # Provide diagnosis
        print("\n🔬 Diagnosis:")
        if any(p in found_patterns for p in ['forbidden', 'access denied']):
            print("🚫 Access is being DENIED - The site is likely blocking your request")
        elif 'not found' in found_patterns:
            print("❓ Resource NOT FOUND - The URL may be incorrect or the file removed")
        elif any(p in found_patterns for p in ['cloudflare', 'captcha', 'protect']):
            print("🛡️ Protection mechanisms detected - The site is using anti-scraping measures")
        elif any(p in found_patterns for p in ['throttl', 'limit']):
            print("⏱️ Rate limiting detected - The site is throttling your requests")
        else:
            print("⚠️ General error page - Unable to determine specific cause")
            
        # Recommendations
        print("\n💡 Recommendations:")
        if 'cloudflare' in found_patterns or 'captcha' in found_patterns:
            print("- Try accessing the site normally in a browser first, solve any CAPTCHAs")
            print("- Add proper browser fingerprinting to your requests")
        if any(p in found_patterns for p in ['forbidden', 'access denied', 'blocked']):
            print("- Check and modify the referer header")
            print("- Try adding more authentic browser headers")
            print("- Use a VPN or different IP address")
        if 'throttl' in found_patterns or 'limit' in found_patterns:
            print("- Implement longer delays between requests")
            print("- Randomize request timing to appear more human-like")
        
        print("\n✅ Analysis complete")
        
    except Exception as e:
        print(f"❌ Error analyzing HTML file: {e}")

def main():
    parser = argparse.ArgumentParser(description='Analyze HTML error pages from failed ROM downloads')
    parser.add_argument('html_file', nargs='?', help='HTML file to analyze')
    
    args = parser.parse_args()
    
    if not args.html_file:
        # Look for HTML error files in debug directory
        debug_dir = Path("debug_errors")
        if debug_dir.exists():
            html_files = list(debug_dir.glob("*.html"))
            if html_files:
                print(f"📁 Found {len(html_files)} HTML error files in debug_errors directory")
                for i, file in enumerate(html_files, 1):
                    print(f"{i}. {file.name}")
                
                try:
                    choice = int(input("\nSelect a file number to analyze (or 0 to quit): "))
                    if 1 <= choice <= len(html_files):
                        analyze_html_file(html_files[choice-1])
                    elif choice == 0:
                        print("Exiting...")
                except ValueError:
                    print("Invalid choice")
            else:
                print("No HTML error files found in debug_errors directory")
        else:
            print("No HTML file specified and no debug_errors directory found")
    else:
        html_path = Path(args.html_file)
        if html_path.exists():
            analyze_html_file(html_path)
        else:
            print(f"File not found: {args.html_file}")

if __name__ == "__main__":
    main()
