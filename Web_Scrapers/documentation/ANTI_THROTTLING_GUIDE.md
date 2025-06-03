# 🛡️ ROM Downloader Anti-Throttling Guide

> **Purpose:** This guide explains the anti-throttling technologies implemented in the Enhanced ROM Downloader to avoid detection and prevent throttling or blocking from ROM hosting websites.

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [Phase 1: Proxy Rotation](#phase-1-proxy-rotation)
3. [Phase 2: Header Randomization](#phase-2-header-randomization)
4. [Phase 3: Behavioral Randomization](#phase-3-behavioral-randomization)
5. [Usage Guide](#usage-guide)
6. [Configuration Options](#configuration-options)
7. [Troubleshooting](#troubleshooting)
8. [Future Improvements](#future-improvements)

## Introduction

ROM hosting websites often implement measures to detect and block automated downloaders or scrapers. These measures can include:
- IP-based rate limiting
- Header and user-agent analysis
- Behavioral pattern detection
- Session fingerprinting
- Serving HTML error pages instead of ROM files

The Enhanced ROM Downloader implements a comprehensive anti-throttling strategy across three phases to mimic human-like browsing behavior and avoid detection, plus content validation to ensure downloaded files are actually ROMs.

## Content Validation

### Features
- **Content-Type Checking:** Validates that responses are not HTML or plain text
- **HTML Detection:** Analyzes the first bytes of a response to detect HTML content
- **Error Logging:** Provides detailed logs when error pages are detected
- **File Integrity:** Prevents saving HTML error pages as ROM files

### Implementation
```python
# CONTENT VALIDATION: Check if we're getting HTML instead of a ROM file
content_type = response.headers.get('content-type', '')
self.logger.info(f"Content type: {content_type} for {rom['name']}")

# Check for common HTML content types that would indicate an error page
if 'text/html' in content_type or 'text/plain' in content_type:
    # Peek at the first few bytes to confirm it's HTML
    first_chunk = await response.content.read(1024)
    first_chunk_text = first_chunk.decode('utf-8', errors='ignore').lower()
    
    # Check for HTML signatures
    if '<html' in first_chunk_text or '<!doctype html' in first_chunk_text:
        self.logger.error(f"❌ Received HTML content instead of ROM file for {rom['name']}")
        return False
```

## Phase 1: Proxy Rotation

### Features
- **Enhanced Proxy Scraper:** Collects working proxies from 13 different GitHub sources
- **Advanced Proxy Validation:** Tests proxies for speed, reliability, and anonymity
- **Smart Rotation Logic:** Intelligently rotates proxies to distribute requests
- **Fallback Mechanism:** Automatically falls back to direct connection if no working proxies
- **Detailed Logging:** Tracks which proxy is used for each download

### Implementation Details
```python
# Example of proxy rotation logic
proxy_dict = self.proxy_rotator.get_next_proxy()
if proxy_dict and 'http' in proxy_dict:
    proxy = proxy_dict['http']
    proxy_used = proxy
    connection_type = "proxy"
    self.download_stats['proxy_used'] += 1
else:
    # Fallback to direct connection
    self.download_stats['direct_used'] += 1
```

## Phase 2: Header Randomization

### Features
- **Dynamic User-Agent Rotation:** Randomizes browser identification
- **Browser-Specific Headers:** Generates consistent header sets for Chrome, Firefox, Safari, Edge
- **Language and Encoding Variation:** Randomizes accept-language and accept-encoding headers
- **Cookie Management:** Properly handles cookies and session data
- **Referer Handling:** Provides realistic referer information

### Implementation Details
```python
# Browser-specific header generation
headers = self.proxy_rotator.get_enhanced_random_headers()
# Headers include:
# - User-Agent (browser-specific)
# - Accept (content types)
# - Accept-Language (varies by locale)
# - Accept-Encoding (compression options)
# - Connection (keep-alive settings)
# - Upgrade-Insecure-Requests
# - Sec-Fetch headers for modern browsers
```

## Phase 3: Behavioral Randomization

### Features
- **Variable Timing Patterns:** Four distinct behavioral patterns
  - `quick_burst`: Fast downloads with short pauses (1-3s base)
  - `normal_browse`: Balanced timing for general browsing (3-8s base)
  - `careful_browse`: Longer pauses for careful browsing (8-15s base)
  - `distracted`: Random long pauses simulating user distraction (15-45s base)
- **Human-Like Timing Variations:**
  - Micro-variations between downloads (humans aren't perfectly consistent)
  - Longer delays at the start of sessions (orientation period)
  - Shorter delays in the middle of sessions (user in flow state)
- **Download Order Randomization:** Multiple shuffling strategies
  - Full random shuffling
  - Chunk-based shuffling
  - Partial reversals
  - Priority-first ordering
- **Session Rotation:**
  - Rotates sessions after 15-25 downloads
  - Resets connection parameters
  - Creates new browser-like fingerprints
- **Adaptive Behavior:**
  - Adapts behavior based on download success/failure
  - Switches to more cautious patterns after failures
  - Implements exponential backoff with human jitter for retries

### Implementation Details
```python
# Human-like delay generation
def get_human_like_delay(self) -> float:
    # Occasionally change behavioral patterns
    if random.random() < self.pattern_change_probability:
        self.current_pattern = random.choice(list(self.timing_patterns.keys()))
        
    base_delay = random.uniform(*self.timing_patterns[self.current_pattern])
    
    # Add micro-variations (humans aren't perfectly consistent)
    variation = random.uniform(0.8, 1.2)
    delay = base_delay * variation
    
    # Slightly longer delays at the start of sessions (user orientation)
    if self.downloads_this_session < 3:
        delay *= random.uniform(1.2, 1.8)
        
    # Slightly shorter delays in the middle of sessions (user in flow)
    elif 5 <= self.downloads_this_session <= 15:
        delay *= random.uniform(0.7, 0.9)
        
    return max(1.0, delay)  # Minimum 1 second delay
```

## Usage Guide

### Basic Usage
To use the Enhanced ROM Downloader with anti-throttling features:

```bash
python rom_downloader_enhanced.py
```

Follow the interactive prompts to select console, ROMs, and behavioral pattern.

### Interactive Mode Options
1. Select console (e.g., GameCube, PlayStation, Xbox)
2. Choose ROM file(s)
3. Select behavioral pattern:
   - Quick Burst: Fast downloads with short pauses
   - Normal Browse: Balanced timing (default)
   - Careful Browse: Longer pauses, methodical
   - Distracted: Random long pauses
   - Adaptive: Learns from failures
4. Enable/disable proxy rotation

## Configuration Options

### Behavioral Patterns
You can modify the timing patterns in the code:

```python
self.timing_patterns = {
    'quick_burst': (1, 3),      # Fast downloads (excited user)
    'normal_browse': (3, 8),    # Normal browsing speed
    'careful_browse': (8, 15),  # Cautious user, reading descriptions
    'distracted': (15, 45)      # User gets distracted, longer pauses
}
```

### Proxy Settings
- `proxy_count`: Number of proxies to fetch (default: 15)
- `timeout`: Connection timeout in seconds (default: 300)

### Download Modes
- `sequential_mode`: Set to True for sequential downloads (default and recommended)
- `enable_behavioral_randomization`: Set to True to enable behavioral features (default)

## Troubleshooting

### Common Issues
1. **No working proxies found**
   - Solution: The script will fall back to direct connection
   - Try running again later when more proxies might be available

2. **Slow downloads**
   - Solution: Adjust the timeout value or disable proxies
   - Try using the 'quick_burst' behavioral pattern

3. **High failure rate**
   - Solution: Switch to 'careful_browse' pattern
   - Check if site is actively blocking downloaders
   - Try enabling session rotation more frequently

### Logs
Check the `rom_downloader_enhanced.log` file for detailed information about:
- Proxy selection and usage
- Download attempts and failures
- Behavioral pattern changes
- Session rotations

## Future Improvements

### Phase 4: Advanced Anti-Detection (Planned)
1. **TLS Fingerprint Randomization**
   - Implement browser-like TLS fingerprints
   - Vary cipher suites and extensions

2. **Realistic Browser Connections**
   - Implement browser-like connection patterns
   - Add proper connection pooling and reuse

3. **Fake Browsing Behavior**
   - Occasional non-ROM requests
   - Randomized image and resource loading

4. **Adaptive Throttling Detection**
   - Monitor response codes and adjust behavior
   - Implement smart backoff strategies

5. **Geolocation-Aware Proxy Selection**
   - Select proxies based on geographic location
   - Match language headers with proxy location

---

*Documentation last updated: June 3, 2025*
