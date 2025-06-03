# 🎮 ROM Downloader Guide

## Overview
The ROM Downloader toolkit includes two versions: the enhanced version with advanced anti-throttling technology and the original basic version. Both use modern proxy scraping to download ROM files from your scraped ROM lists with features like proxy rotation, resume capability, and progress tracking.

## 🚀 Quick Start

### Enhanced Version (Recommended)
```bash
python rom_downloader_enhanced.py
```

### Legacy Version
```bash
python rom_downloader.py
```

### Using the Launcher Menu
1. Run the main launcher: `python scraper_launcher.py` or double-click `START_HERE.bat`
2. Choose option **4️⃣ ROM Downloader**
3. Select which ROM file to download from the available options
4. Configure download settings and start

## 📋 Available ROM Collections

Your ROM downloader can access **14 ROM files** with thousands of games:

### GameCube (8 files)
- `GC_games_final.txt` - 46 curated ROMs (Mario, Sonic, Zelda, etc.)
- `GC_Roms.txt` - 1,985 complete GameCube collection
- `GC_USA_Roms.txt` - 680 USA region ROMs
- `Mario_Roms.txt` - 6 Mario games
- `Sonic_Roms.txt` - 6 Sonic games  
- `Zelda_Roms.txt` - 5 Zelda games
- And more...

### Other Consoles
- **PS1**: 10,739+ games
- **PS2**: 11,211+ games
- **Xbox**: 2,597+ games

## 🔧 Features

### Enhanced Version (Anti-Throttling)
- **Three-Phase Anti-Throttling Technology**:
  - **Phase 1: Proxy Rotation** - Advanced proxy handling with 13 sources
  - **Phase 2: Header Randomization** - Browser-specific headers and user-agents
  - **Phase 3: Behavioral Randomization** - Human-like download patterns
- **Behavioral Patterns**:
  - Quick Burst - Fast downloads with short pauses
  - Normal Browse - Balanced timing
  - Careful Browse - Longer pauses, methodical approach
  - Distracted - Random long pauses simulating user distraction
- **Advanced Session Management**:
  - Session rotation after 15-25 downloads
  - Adaptive behavior based on download success/failure
  - Human-like timing variations
- **Download Order Randomization**:
  - Multiple shuffling strategies to avoid predictable patterns

### Basic Features (Both Versions)
- **Proxy Support**:
  - Automatic proxy rotation
  - Modern async proxy handling
  - Anti-detection with random headers
- **Download Management**:  
  - Resume capability for interrupted downloads
  - Real-time progress tracking with ETAs
  - Concurrent or sequential download modes
  - Organized storage by console type
- **Safety Features**:
  - Timeout protection
  - Error handling with retries
  - File validation

## 📁 File Organization

Downloads are organized in this structure:
```
ROM_Downloads/
├── GameCube/
│   ├── Burnout_(USA).zip
│   ├── Mario_Kart_Double_Dash_(USA).zip
│   └── ...
├── PS1/
│   └── ...
├── PS2/
│   └── ...
└── Xbox/
    └── ...
```

## ⚙️ Configuration Options

### Enhanced Version Options
When running the enhanced downloader, you can configure:

- **Behavioral Pattern**:
  - Quick Burst: Fast downloads, short pauses (1-3s base)
  - Normal Browse: Balanced timing (3-8s base)
  - Careful Browse: Longer pauses (8-15s base)
  - Distracted: Random long pauses (15-45s base)
  - Adaptive: Learns from failures
- **Proxy Usage**: Enable/disable proxy rotation
- **Output Directory**: Where to save downloads (default: `ROM_Downloads_Enhanced`)

### Basic Version Options
When running the basic downloader, you can configure:

- **Proxy Count**: Number of proxies to test (default: 15)
- **Download Mode**: Sequential or concurrent
- **Timeout**: Per-file timeout in seconds (default: 300)
- **Output Directory**: Where to save downloads (default: `ROM_Downloads`)

## 🎯 Recommended Usage

### For Testing
Start with the **GameCube/GC_games_final.txt** file (46 ROMs) - it's a curated collection that's perfect for testing the system.

### For Large Collections
The system can handle massive downloads:
- **PS1**: 10,739 games (several TB)
- **PS2**: 11,211 games (several TB)
- **GameCube**: 1,985 games (hundreds of GB)

**⚠️ Warning**: Large collections require significant disk space and bandwidth!

## 🛠️ Troubleshooting

### Common Issues

**"No ROM files found"**
- Make sure you've run the ROM website scraper first
- Check that `rom_website_scraper/scraped_data/` exists

**"Timeout errors"**
- Large files may need longer timeouts
- Check your internet connection
- Try with the "careful_browse" behavioral pattern (enhanced version)
- Reduce concurrent downloads (basic version)

**"Proxy errors"**
- The system will find working proxies automatically
- If all proxies fail, it will attempt direct downloads

**"High failure rate"**
- Enhanced version: Switch to 'careful_browse' pattern
- Try enabling session rotation more frequently
- Check if the site is actively blocking downloaders

### Performance Tips

1. **Start small**: Test with `GC_games_final.txt` first
2. **Choose the right pattern**: Use "normal_browse" for balance between speed and stealth
3. **Monitor disk space**: Large collections need TB of storage  
4. **Use good internet**: Stable connection recommended
5. **Be patient**: The enhanced version intentionally adds delays to mimic human behavior

## 📊 Statistics and Logging

### Enhanced Statistics
The enhanced downloader provides detailed information:
- ✅ Completed downloads
- ❌ Failed downloads
- 📦 Total data downloaded
- 🌐 Proxy vs direct connection usage
- 📈 Proxy usage rate
- 🎲 Behavioral pattern statistics
- 🔄 Session rotation data

### Basic Statistics
The basic version tracks:
- ✅ Completed downloads
- ❌ Failed downloads
- ⏭️ Skipped files (already exist)
- 📦 Total data downloaded

### Logging
Both versions log activity to their respective log files:
- `rom_downloader_enhanced.log` - Enhanced version log
- `rom_downloader.log` - Basic version log

## 📚 Additional Documentation

For more detailed information, see these additional documents:
- **[ANTI_THROTTLING_GUIDE.md](ANTI_THROTTLING_GUIDE.md)** - Complete guide to the anti-throttling technology
- **[ENHANCED_ROM_DOWNLOADER.md](ENHANCED_ROM_DOWNLOADER.md)** - Technical details about the enhanced implementation
- **[PHASE_VERIFICATION_RESULTS.md](PHASE_VERIFICATION_RESULTS.md)** - Test results for each implementation phase

---

## Next Steps

1. **Try the enhanced version**: The enhanced version with behavioral randomization provides the best protection against throttling
2. **Test different patterns**: Experiment with different behavioral patterns to find the optimal balance
3. **Monitor download success**: Check the statistics to see which settings work best
4. **Check for updates**: Phase 4 (Advanced Anti-Detection) is coming soon!
5. **Enjoy your ROMs**: Games are ready to use!
