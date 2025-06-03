# Web Scraper with Proxy Rotation

A Python script that downloads and parses web content from URLs listed in a text file, using proxy rotation and header randomization to avoid detection and rate limits.

## Features

- **Proxy Rotation**: Automatically finds and rotates through working proxies using ProxyBroker
- **Header Randomization**: Randomizes User-Agent and other headers to avoid detection
- **Beautiful Soup Integration**: Parses HTML content and extracts text, links, and images
- **Error Handling**: Robust retry logic with fallback mechanisms
- **Rate Limiting**: Configurable delays between requests
- **Logging**: Comprehensive logging to file and console
- **Content Extraction**: Saves page content, links, and metadata

## Installation

1. Install Python dependencies:
```powershell
pip install -r scraper_requirements.txt
```

## Usage

1. Create a text file with URLs to scrape (one per line):
```
https://example.com
https://another-site.com
# Comments start with #
```

2. Run the scraper:
```powershell
python web_scraper_with_proxies.py
```

3. Follow the prompts:
   - Enter path to URL file (default: sample_urls.txt)
   - Enter output directory (default: downloads)
   - Enter number of proxies to find (default: 20)

## Configuration

You can modify the scraper behavior by editing the main() function parameters:

- `proxy_count`: Number of proxies to find and rotate through
- `delay_range`: Min/max seconds to wait between requests
- `max_retries`: Number of retry attempts per URL
- `timeout`: Request timeout in seconds

## Output

The scraper creates the following files in the output directory:

- `{domain}_{path}.txt`: Main page content (title + text)
- `{domain}_{path}_links.txt`: All links found on the page
- `scraper.log`: Detailed log of scraping activity

## Proxy Sources

The scraper automatically finds proxies from:
- free-proxy-list.net
- proxy-list.download
- Other ProxyBroker sources

## Error Handling

- Failed requests are retried with different proxies
- Network errors are logged but don't stop the scraping process
- Progress is shown for each URL processed

## Legal Notice

⚠️ **Important**: Always respect websites' robots.txt files and terms of service. Use reasonable delays between requests and don't overwhelm servers. This tool is for educational purposes and legitimate web scraping only.

## Example URL File Format

```
# Gaming websites
https://example-rom-site.com/gamecube
https://another-gaming-site.com/roms

# News sites
https://news-site.com/tech
https://blog-site.com/articles

# E-commerce
https://shop-site.com/products
```

## Troubleshooting

### No Proxies Found
- Check your internet connection
- Some proxy sources may be temporarily unavailable
- The scraper will continue without proxies if none are found

### Connection Errors
- Increase timeout value
- Reduce the number of concurrent connections
- Check if target sites are blocking your IP range

### Rate Limiting
- Increase delay between requests
- Use fewer concurrent connections
- Respect the target site's rate limits
