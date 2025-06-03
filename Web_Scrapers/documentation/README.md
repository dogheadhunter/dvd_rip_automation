# 🎮 ROM Downloader & Web Scrapers

A comprehensive collection of tools for downloading ROM files with beautiful progress bars, proxy support, and advanced scraping capabilities.

## 🚀 Quick Start

### Main ROM Downloader
```bash
python rom_downloader.py
```

**Features:**
- ✨ Beautiful progress bars with download speeds and ETAs
- 🌐 Proxy rotation to avoid being blocked
- 🔒 SSL certificate handling for self-signed certificates  
- 📁 Organizes downloads by console
- ⏸️ Resume capability for interrupted downloads
- 🐌 Sequential & concurrent download modes
- 📊 Real-time statistics and logging

### Scraper Launcher
```bash
python scraper_launcher.py
```

Launch various web scraping tools with an interactive menu.

## 📁 Directory Structure

```
Web_Scrapers/
├── rom_downloader.py          # Main ROM downloader with progress bars
├── scraper_launcher.py        # Interactive launcher for scraping tools
├── requirements.txt           # Python dependencies
├── rom_downloader.log         # Download logs
├── working_scrapers/          # Scraper modules
│   ├── modern_proxy_scraper.py
│   ├── free_proxy_scraper.py
│   └── simple_web_scraper.py
├── documentation/             # User guides and documentation
├── sample_data/              # Sample data files
├── tests/                    # Test files
├── archive/                  # Old/backup files
└── ROM_Downloads_Test/       # Test download directory
```

## 🔧 Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

**Main dependencies:**
- `aiohttp>=3.8.0` - Async HTTP client
- `aiofiles>=23.0.0` - Async file operations
- `tqdm>=4.65.0` - Progress bars
- `requests>=2.28.0` - HTTP requests
- `beautifulsoup4>=4.11.0` - HTML parsing

## 📊 Download Statistics

The ROM downloader tracks:
- ✅ Completed downloads
- ❌ Failed downloads  
- 📦 Total downloaded size
- ⏱️ Download speeds and ETAs
- 🕐 Session duration

## 🌐 Proxy Support

The downloader includes advanced proxy capabilities:
- 🔄 Automatic proxy rotation
- 🌍 Multiple proxy sources (13 GitHub sources)
- ✅ Proxy validation and testing
- 🔀 Random user-agent rotation
- 🛡️ Anti-detection measures

## 🎯 ROM Collections Supported

The system can download ROMs for:
- 🎮 GameCube (~3,877 ROMs)
- 🕹️ PlayStation 1 (~10,745 ROMs)
- 🎯 PlayStation 2 (~11,300 ROMs)
- 📱 Xbox (~2,586 ROMs)

**Total: ~28,508 ROMs across 4 consoles**

## ⚙️ Configuration

### Download Modes
1. **Sequential (Recommended)** - Downloads one ROM at a time with polite delays
2. **Concurrent (Legacy)** - Multiple downloads (may trigger throttling)

### Delay Settings
- Default: 2-8 seconds between downloads
- Customizable based on site responsiveness
- Helps avoid rate limiting

### SSL Configuration
- Disabled certificate verification for ROM hosting sites
- Handles self-signed certificates automatically

## 📝 Logging

All download activity is logged to `rom_downloader.log`:
- Download start/completion times
- Error messages and troubleshooting info
- Proxy usage and rotation
- Speed and performance metrics

## 🧪 Testing

Run tests with:
```bash
cd tests
python test_progress_bars.py
python test_rom_finder.py
python test_single_download.py
```

## 📚 Documentation

See the `documentation/` folder for:
- Detailed user guides
- API documentation
- Troubleshooting guides
- Advanced configuration options

## 🎮 Getting Started

1. **Find ROM files**: The downloader looks for ROM txt files in `../rom_website_scraper/scraped_data/`
2. **Select console**: Choose from GameCube, PS1, PS2, or Xbox
3. **Choose download mode**: Sequential (recommended) or concurrent
4. **Configure proxies**: Optional proxy support for enhanced privacy
5. **Start downloading**: Watch beautiful progress bars in action!

## 🛡️ Legal Notice

This tool is for educational purposes and personal backups only. Ensure you own the original games before downloading ROMs. Respect copyright laws and website terms of service.

---
*Enhanced with beautiful progress bars and advanced proxy support* ✨
