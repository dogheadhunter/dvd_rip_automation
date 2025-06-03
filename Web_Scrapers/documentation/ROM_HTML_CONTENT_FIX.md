# ROM Downloader HTML Content Fix

## Issue
The ROM downloader was downloading HTML error pages instead of actual ROM files. This was happening because:

1. The websites may be blocking access to the ROM files
2. The proxy connections were being redirected to captive portals
3. There was no content validation to check if we're getting HTML instead of a ROM file

## Solution

We've implemented a comprehensive fix that:

1. **Content Validation**: Adds validation to check if the response is HTML instead of a ROM file
   - Checks Content-Type headers for 'text/html' or 'text/plain'
   - Examines the first few bytes of the response to detect HTML tags
   - Extracts and logs the page title from HTML for better error messages

2. **Alternative URL Finding**: Adds functionality to find alternative sources when a URL fails
   - Tries different domain alternatives (Archive.org, etc.)
   - Tests different URL formats and paths
   - Automatically retries download with working alternative URLs

3. **Improved Referrer Headers**: Adds proper referrer headers to bypass website restrictions
   - Sets the referrer to the base domain of the ROM site
   - Helps bypass basic anti-hotlinking measures

## How to Use

1. Run the fix script to patch the ROM downloader:
   ```
   python fix_rom_downloader.py
   ```

2. Use the enhanced ROM downloader as usual:
   ```
   python rom_downloader_enhanced.py
   ```

3. When a ROM fails to download because it returns HTML, the downloader will now:
   - Log an error with details about the HTML content
   - Automatically try alternative URLs if available
   - Show which error page was received

## Restoring from Backup

If the fix causes any issues, you can restore from the backup that was created:

```
copy [backup_file] rom_downloader_enhanced.py
```

The backup file is named `rom_downloader_enhanced.py.bak.[timestamp]`

## Technical Details

The fix adds:

1. A new module `rom_url_validator.py` in the `tools` directory
2. Content validation in the `download_rom_enhanced` method
3. Referrer headers to all requests
4. Automatic retrying with alternative URLs

## Future Improvements

1. Add more alternative ROM sources
2. Implement a cache of working URLs
3. Add a UI for manually selecting alternative sources
4. Implement more sophisticated detection of blocking/throttling

## Troubleshooting

If you encounter issues:

1. Check the log file (`rom_downloader_enhanced.log`) for details
2. Look for "Error page detected" messages in the console output
3. Try running with the `--debug` flag for more detailed logging
4. Try using a VPN or different proxies
