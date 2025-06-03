#!/usr/bin/env python3
"""
🚀 Quick Functionality Test - Focus on Implementation Verification
================================================================

Tests Phase 1 & 2 implementations without relying on finding working proxies.
"""

import sys
import requests
from pathlib import Path

# Add the working_scrapers directory to path
sys.path.append(str(Path(__file__).parent.parent / "working_scrapers"))

try:
    from modern_proxy_scraper_enhanced import EnhancedModernProxyRotator
    print("✅ Enhanced proxy scraper imported successfully")
except ImportError as e:
    print(f"❌ Enhanced proxy scraper import failed: {e}")
    sys.exit(1)

def test_header_randomization():
    """Test that different browser headers are generated"""
    print("\n🧪 Testing Header Randomization (Phase 2)")
    print("=" * 50)
    
    rotator = EnhancedModernProxyRotator()
    
    # Generate 5 different header sets
    header_sets = []
    for i in range(5):
        headers = rotator.get_enhanced_random_headers()
        header_sets.append(headers)
        print(f"Header Set {i+1}:")
        print(f"  User-Agent: {headers.get('User-Agent', 'None')[:60]}...")
        print(f"  Accept: {headers.get('Accept', 'None')[:40]}...")
        print(f"  Browser: {headers.get('Sec-Ch-Ua', 'None')[:30]}...")
        print()
    
    # Verify we got different user agents
    user_agents = [h.get('User-Agent') for h in header_sets]
    unique_agents = set(user_agents)
    
    if len(unique_agents) > 1:
        print(f"✅ Header randomization working: {len(unique_agents)} unique user agents generated")
    else:
        print("⚠️  Warning: All user agents were identical")
    
    return len(unique_agents) > 1

def test_proxy_discovery():
    """Test proxy discovery without requiring working proxies"""
    print("\n🧪 Testing Proxy Discovery (Phase 1)")
    print("=" * 50)
    
    rotator = EnhancedModernProxyRotator()
    
    # Test proxy source fetching
    print("Testing proxy source fetching...")
    try:
        # Get proxy candidates (don't need them to work)
        all_proxies = rotator.get_proxy_candidates()
        print(f"✅ Proxy discovery working: Found {len(all_proxies)} proxy candidates")
        
        if len(all_proxies) > 0:
            print(f"   Sample proxies: {list(all_proxies)[:3]}")
            return True
        else:
            print("⚠️  No proxy candidates found")
            return False
            
    except Exception as e:
        print(f"❌ Proxy discovery failed: {e}")
        return False

def test_direct_connection():
    """Test that we can make HTTP requests (baseline functionality)"""
    print("\n🧪 Testing Direct HTTP Connection")
    print("=" * 50)
    
    try:
        # Test with httpbin to see our current IP
        response = requests.get('http://httpbin.org/ip', timeout=10)
        if response.status_code == 200:
            data = response.json()
            ip = data.get('origin', 'Unknown')
            print(f"✅ Direct connection working. Current IP: {ip}")
            return True
        else:
            print(f"❌ Direct connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return False

def test_rom_downloader_integration():
    """Check if ROM downloader has Phase 1 & 2 features integrated"""
    print("\n🧪 Testing ROM Downloader Integration")
    print("=" * 50)
    
    try:
        rom_path = Path(__file__).parent.parent / 'rom_downloader_enhanced.py'
        with open(rom_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Phase 1 features
        phase1_features = [
            'get_working_proxies',
            'proxy_stats',
            'current_proxy_ip'
        ]
        
        # Check for Phase 2 features  
        phase2_features = [
            'get_enhanced_random_headers',
            'browser_headers',
            'randomize'
        ]
        
        phase1_found = sum(1 for feature in phase1_features if feature in content)
        phase2_found = sum(1 for feature in phase2_features if feature in content)
        
        print(f"Phase 1 integration: {phase1_found}/{len(phase1_features)} features found")
        print(f"Phase 2 integration: {phase2_found}/{len(phase2_features)} features found")
        
        if phase1_found >= 2 and phase2_found >= 2:
            print("✅ ROM downloader integration looks good")
            return True
        else:
            print("⚠️  ROM downloader integration may be incomplete")
            return False
            
    except Exception as e:
        print(f"❌ ROM downloader integration check failed: {e}")
        return False

def main():
    print("🚀 Quick Functionality Test - Phase 1 & 2")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Header Randomization", test_header_randomization()))
    results.append(("Proxy Discovery", test_proxy_discovery()))
    results.append(("Direct Connection", test_direct_connection()))
    results.append(("ROM Downloader Integration", test_rom_downloader_integration()))
    
    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎯 Phase 1 & 2 Verification: SUCCESS!")
        print("Ready to proceed with Phase 3 implementation.")
    elif passed >= len(results) - 1:
        print("\n⚠️  Phase 1 & 2 Verification: MOSTLY SUCCESSFUL")
        print("Minor issues detected but core functionality is working.")
    else:
        print("\n❌ Phase 1 & 2 Verification: ISSUES DETECTED")
        print("Please review failed tests before proceeding.")

if __name__ == "__main__":
    main()
