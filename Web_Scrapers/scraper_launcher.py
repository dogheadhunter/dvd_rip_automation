#!/usr/bin/env python3
"""
🕷️ Web Scraper Launcher - Simple & User Friendly
=================================================

This script provides an easy-to-use menu system for all web scraping tools.
Just run this file and choose what you want to do!

Requirements: Run 'pip install -r requirements.txt' first
"""

import os
import sys
import subprocess
from pathlib import Path

class WebScraperLauncher:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.working_dir = self.script_dir / "working_scrapers"
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Print a nice header"""
        print("=" * 60)
        print("🕷️  WEB SCRAPER TOOLKIT - Main Menu")
        print("=" * 60)
        print("Choose your scraping tool:\n")
        
    def print_menu(self):
        """Print the main menu options"""
        print("📋 AVAILABLE SCRAPERS:")
        print("  1️⃣  Simple Web Scraper     - No proxies, just header rotation")
        print("  2️⃣  Free Proxy Scraper     - With free proxy rotation")
        print("  3️⃣  Modern Async Scraper   - Advanced async proxy handling")
        print("  4️⃣  ROM Downloader         - Download ROM files with proxy support")
        print()
        print("📖 HELP & INFO:")
        print("  5️⃣  View Documentation     - How to use the scrapers")
        print("  6️⃣  Install Requirements   - Install needed packages")
        print("  7️⃣  Check Sample URLs      - View/edit test URLs")
        print()
        print("🔧 UTILITIES:")
        print("  8️⃣  Clean Up Files         - Remove old logs and test data")
        print("  9️⃣  View Recent Results    - Check your last scraping results")
        print()
        print("  0️⃣  Exit")
        print()
        
    def get_user_choice(self):
        """Get user's menu choice"""
        try:
            choice = input("Enter your choice (0-9): ").strip()
            return choice
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return "0"
            
    def run_scraper(self, script_name, description):
        """Run a specific scraper script"""
        script_path = self.working_dir / script_name
        
        if not script_path.exists():
            print(f"❌ Error: {script_name} not found!")
            print(f"Expected location: {script_path}")
            input("Press Enter to continue...")
            return
            
        print(f"\n🚀 Starting {description}...")
        print(f"Script: {script_path}")
        print("=" * 50)
        
        try:
            # Run the script
            result = subprocess.run([sys.executable, str(script_path)], 
                                  cwd=str(script_path.parent))
            print("=" * 50)
            if result.returncode == 0:
                print("✅ Scraper completed successfully!")
            else:
                print("⚠️  Scraper finished with warnings/errors")
        except Exception as e:
            print(f"❌ Error running scraper: {e}")
            
        input("\nPress Enter to return to menu...")
        
    def run_rom_downloader(self):
        """Run the ROM downloader"""
        rom_script = self.script_dir / "rom_downloader.py"
        
        if not rom_script.exists():
            print(f"❌ Error: rom_downloader.py not found!")
            print(f"Expected location: {rom_script}")
            input("Press Enter to continue...")
            return
            
        print(f"\n🎮 Starting ROM Downloader...")
        print(f"Script: {rom_script}")
        print("=" * 50)
        
        try:
            # Run the ROM downloader
            result = subprocess.run([sys.executable, str(rom_script)], 
                                  cwd=str(rom_script.parent))
            print("=" * 50)
            if result.returncode == 0:
                print("✅ ROM Downloader completed successfully!")
            else:
                print("⚠️  ROM Downloader finished with warnings/errors")
        except Exception as e:
            print(f"❌ Error running ROM downloader: {e}")
            
        input("\nPress Enter to return to menu...")
        
    def view_documentation(self):
        """Show available documentation"""
        doc_dir = self.script_dir / "documentation"
        
        print("\n📖 DOCUMENTATION:")
        print("=" * 40)
        
        if doc_dir.exists():
            docs = list(doc_dir.glob("*.md")) + list(doc_dir.glob("*.txt"))
            if docs:
                for i, doc in enumerate(docs, 1):
                    print(f"  {i}. {doc.name}")
                print()
                
                try:
                    choice = int(input("View document (number): "))
                    if 1 <= choice <= len(docs):
                        self.show_file(docs[choice-1])
                except (ValueError, IndexError):
                    print("Invalid choice")
            else:
                print("No documentation files found")
        else:
            print("Documentation folder not found")
            
        input("\nPress Enter to continue...")
        
    def install_requirements(self):
        """Install required packages"""
        req_file = self.script_dir / "requirements.txt"
        
        print("\n🔧 INSTALLING REQUIREMENTS:")
        print("=" * 40)
        
        if req_file.exists():
            print(f"Installing from: {req_file}")
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
                if result.returncode == 0:
                    print("✅ Requirements installed successfully!")
                else:
                    print("⚠️  Some packages may have failed to install")
            except Exception as e:
                print(f"❌ Error installing requirements: {e}")
        else:
            print("❌ requirements.txt not found")
            print("Installing basic packages...")
            packages = ["beautifulsoup4", "requests", "fake-useragent", "aiohttp", "aiofiles", "lxml"]
            for package in packages:
                print(f"Installing {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package])
                
        input("\nPress Enter to continue...")
        
    def view_sample_urls(self):
        """View and edit sample URLs"""
        sample_file = self.script_dir / "sample_data" / "urls.txt"
        
        print("\n📝 SAMPLE URLs:")
        print("=" * 40)
        
        if sample_file.exists():
            print("Current URLs:")
            self.show_file(sample_file, max_lines=20)
            
            edit = input("\nEdit this file? (y/n): ").lower().strip()
            if edit == 'y':
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(str(sample_file))
                    else:  # Unix/Linux/Mac
                        subprocess.run(['nano', str(sample_file)])
                except Exception as e:
                    print(f"Could not open editor: {e}")
                    print(f"Edit this file manually: {sample_file}")
        else:
            print("❌ Sample URL file not found")
            print("Creating a new one...")
            self.create_sample_urls(sample_file)
            
        input("\nPress Enter to continue...")
        
    def create_sample_urls(self, file_path):
        """Create a sample URLs file"""
        sample_content = """# Sample URLs for Web Scraping
# Lines starting with # are comments
# Add one URL per line

# Test URLs (safe for testing)
https://httpbin.org/ip
https://httpbin.org/user-agent
https://httpbin.org/headers

# Example sites (uncomment to use)
# https://example.com
# https://quotes.toscrape.com
# https://books.toscrape.com

# Add your URLs here:
"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(sample_content)
        print(f"✅ Created sample URL file: {file_path}")
        
    def clean_up_files(self):
        """Clean up old logs and test files"""
        print("\n🧹 CLEANING UP FILES:")
        print("=" * 40)
        
        # Files to clean up
        cleanup_patterns = [
            "*.log",
            "test_*",
            "__pycache__",
            "*.pyc"
        ]
        
        cleaned = 0
        for pattern in cleanup_patterns:
            for item in self.script_dir.rglob(pattern):
                try:
                    if item.is_file():
                        item.unlink()
                        print(f"Deleted: {item.name}")
                        cleaned += 1
                    elif item.is_dir():
                        import shutil
                        shutil.rmtree(item)
                        print(f"Deleted folder: {item.name}")
                        cleaned += 1
                except Exception as e:
                    print(f"Could not delete {item}: {e}")
                    
        print(f"\n✅ Cleaned up {cleaned} items")
        input("Press Enter to continue...")
        
    def view_recent_results(self):
        """Show recent scraping results"""
        print("\n📊 RECENT RESULTS:")
        print("=" * 40)
        
        # Look for result folders
        result_dirs = []
        for item in self.script_dir.iterdir():
            if item.is_dir() and any(x in item.name.lower() for x in ['download', 'output', 'result']):
                result_dirs.append(item)
                
        if result_dirs:
            for i, dir_path in enumerate(result_dirs, 1):
                files = list(dir_path.glob("*"))
                print(f"{i}. {dir_path.name} ({len(files)} files)")
                
            try:
                choice = int(input("\nView folder contents (number): "))
                if 1 <= choice <= len(result_dirs):
                    self.show_folder_contents(result_dirs[choice-1])
            except (ValueError, IndexError):
                print("Invalid choice")
        else:
            print("No result folders found")
            
        input("\nPress Enter to continue...")
        
    def show_file(self, file_path, max_lines=50):
        """Display file contents"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines[:max_lines]):
                print(f"{i+1:3}: {line}")
                
            if len(lines) > max_lines:
                print(f"... ({len(lines) - max_lines} more lines)")
                
        except Exception as e:
            print(f"Error reading file: {e}")
            
    def show_folder_contents(self, folder_path):
        """Show contents of a folder"""
        print(f"\nContents of {folder_path.name}:")
        print("-" * 30)
        
        files = list(folder_path.glob("*"))
        for file_path in files:
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"📄 {file_path.name} ({size} bytes)")
            else:
                print(f"📁 {file_path.name}/")
                
        if files:
            view = input("\nView a file? Enter filename (or Enter to skip): ").strip()
            if view:
                file_to_view = folder_path / view
                if file_to_view.exists():
                    print(f"\n--- {view} ---")
                    self.show_file(file_to_view, max_lines=20)
                else:
                    print("File not found")
        
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            choice = self.get_user_choice()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                self.run_scraper("simple_web_scraper.py", "Simple Web Scraper")
            elif choice == "2":
                self.run_scraper("free_proxy_scraper.py", "Free Proxy Scraper")
            elif choice == "3":
                self.run_scraper("modern_proxy_scraper.py", "Modern Async Scraper")
            elif choice == "4":
                self.run_rom_downloader()
            elif choice == "5":
                self.view_documentation()
            elif choice == "6":
                self.install_requirements()
            elif choice == "7":
                self.view_sample_urls()
            elif choice == "8":
                self.clean_up_files()
            elif choice == "9":
                self.view_recent_results()
            else:
                print("\n❌ Invalid choice. Please try again.")
                input("Press Enter to continue...")

if __name__ == "__main__":
    launcher = WebScraperLauncher()
    launcher.run()
