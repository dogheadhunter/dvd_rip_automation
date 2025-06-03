#!/usr/bin/env python3
"""
🧹 Cleanup Script for Web_Scrapers Directory
============================================

This script helps maintain a clean workspace by removing temporary files,
organizing downloads, and clearing cache files.
"""

import os
import shutil
from pathlib import Path
import time

def cleanup_cache_files():
    """Remove Python cache files and temporary files"""
    print("🗑️  Cleaning up cache files...")
    
    cache_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        '*.log.old',
        '*.tmp'
    ]
    
    cleaned_count = 0
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_dir)
                print(f"  ✅ Removed: {cache_dir}")
                cleaned_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {cache_dir}: {e}")
        
        # Remove .pyc files
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd', '.tmp')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"  ✅ Removed: {file_path}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to remove {file_path}: {e}")
    
    print(f"🎉 Cleaned {cleaned_count} cache files/directories")

def organize_log_files():
    """Organize and archive old log files"""
    print("📋 Organizing log files...")
    
    log_files = list(Path('.').glob('*.log'))
    if not log_files:
        print("  ℹ️  No log files found")
        return
    
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    moved_count = 0
    for log_file in log_files:
        # Keep current log file, move old ones
        if log_file.stat().st_mtime < time.time() - (24 * 3600):  # Older than 1 day
            try:
                timestamp = time.strftime('%Y%m%d_%H%M%S', time.gmtime(log_file.stat().st_mtime))
                new_name = f"{log_file.stem}_{timestamp}.log"
                new_path = logs_dir / new_name
                shutil.move(str(log_file), str(new_path))
                print(f"  ✅ Archived: {log_file} -> {new_path}")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ Failed to archive {log_file}: {e}")
    
    print(f"📁 Archived {moved_count} log files")

def cleanup_empty_directories():
    """Remove empty directories"""
    print("📂 Cleaning up empty directories...")
    
    removed_count = 0
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                # Skip important directories
                if dir_name in ['archive', 'tests', 'documentation', 'working_scrapers']:
                    continue
                    
                if not os.listdir(dir_path):  # Directory is empty
                    os.rmdir(dir_path)
                    print(f"  ✅ Removed empty directory: {dir_path}")
                    removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {dir_path}: {e}")
    
    print(f"🗂️  Removed {removed_count} empty directories")

def show_directory_stats():
    """Show current directory statistics"""
    print("📊 Directory Statistics:")
    print("="*50)
    
    stats = {
        'Python files': 0,
        'Test files': 0,
        'Log files': 0,
        'Archive files': 0,
        'Total files': 0,
        'Directories': 0
    }
    
    for root, dirs, files in os.walk('.'):
        stats['Directories'] += len(dirs)
        stats['Total files'] += len(files)
        
        for file in files:
            if file.endswith('.py'):
                if file.startswith('test_'):
                    stats['Test files'] += 1
                else:
                    stats['Python files'] += 1
            elif file.endswith('.log'):
                stats['Log files'] += 1
            elif 'archive' in root:
                stats['Archive files'] += 1
    
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("="*50)

def main():
    """Main cleanup function"""
    print("🧹 ROM Downloader Workspace Cleanup")
    print("="*40)
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🕐 Cleanup started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Show initial stats
        show_directory_stats()
        print()
        
        # Perform cleanup operations
        cleanup_cache_files()
        print()
        
        organize_log_files()
        print()
        
        cleanup_empty_directories()
        print()
        
        # Show final stats
        print("📊 Final Statistics:")
        show_directory_stats()
        
        print("✨ Cleanup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
