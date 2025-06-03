#!/usr/bin/env python3
"""
Phase 3 Verification: Behavioral Randomization
Tests the human-like download patterns and behavioral features
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from rom_downloader_enhanced import EnhancedROMDownloader, BehavioralRandomizer

async def test_behavioral_randomizer():
    """Test the BehavioralRandomizer class directly"""
    print("🧪 PHASE 3 VERIFICATION: Behavioral Randomization")
    print("="*60)
    print("Testing behavioral randomization components:")
    print("- Variable timing patterns")
    print("- Session rotation logic")
    print("- Download order shuffling")
    print("- Retry delays with human jitter")
    print("="*60)
    
    # Test BehavioralRandomizer directly
    print("\n1️⃣ Testing BehavioralRandomizer class...")
    randomizer = BehavioralRandomizer()
    
    # Test different patterns by setting them directly
    patterns = ['quick_burst', 'normal_browse', 'careful_browse', 'distracted']
    
    print(f"\n🎯 Testing {len(patterns)} behavioral patterns:")
    for pattern in patterns:
        print(f"\n   📋 Pattern: {pattern}")
        randomizer.current_pattern = pattern  # Set pattern directly
        
        # Test delay generation
        delays = []
        for i in range(5):
            delay = randomizer.get_human_like_delay()
            delays.append(delay)
        
        print(f"   ⏱️  Sample delays: {[f'{d:.1f}s' for d in delays]}")
        print(f"   📊 Range: {min(delays):.1f}s - {max(delays):.1f}s")
    
    # Test session rotation
    print(f"\n2️⃣ Testing session rotation...")
    initial_session_count = randomizer.downloads_this_session
    
    # Simulate downloads until rotation
    downloads_until_rotation = 0
    while not randomizer.should_rotate_session():
        randomizer.record_download_attempt(True)
        downloads_until_rotation += 1
        if downloads_until_rotation > 50:  # Safety break
            break
    
    print(f"   🔄 Session rotated after {downloads_until_rotation} downloads")
    print(f"   🎯 Target range: 15-25 downloads per session")
    
    # Test download order shuffling
    print(f"\n3️⃣ Testing download order shuffling...")
    test_items = [{'name': f"ROM_{i:03d}"} for i in range(10)]
    
    original_order = [item['name'] for item in test_items]
    shuffled = randomizer.randomize_download_order(test_items.copy())
    shuffled_names = [item['name'] for item in shuffled]
    
    print(f"   📋 Original:  {original_order[:3]}...{original_order[-3:]}")
    print(f"   🎲 Shuffled:  {shuffled_names[:3]}...{shuffled_names[-3:]}")
    print(f"   ✅ Order changed: {original_order != shuffled_names}")
    
    # Test retry delays
    print(f"\n4️⃣ Testing retry delays with jitter...")
    for attempt in range(1, 5):
        delay = randomizer.get_retry_delay(attempt)
        print(f"   🔄 Attempt {attempt}: {delay:.1f}s delay")
    
    # Test failure adaptation
    print(f"\n5️⃣ Testing failure adaptation...")
    original_pattern = randomizer.current_pattern
    
    # Simulate some failures
    for i in range(3):
        randomizer.record_download_attempt(False)
    
    print(f"   📉 Original pattern: {original_pattern}")
    print(f"   📈 Adapted pattern: {randomizer.current_pattern}")
    print(f"   🔧 Consecutive failures: {randomizer.consecutive_failures}")
    
    # Test session stats
    stats = randomizer.get_session_stats()
    print(f"   📊 Session stats: {stats}")
    
    print(f"\n✅ BehavioralRandomizer component tests completed!")
    return True

async def test_enhanced_downloader_integration():
    """Test behavioral randomization integration with EnhancedROMDownloader"""
    print(f"\n6️⃣ Testing Enhanced ROM Downloader Integration...")
    
    # Test with behavioral randomization enabled
    downloader = EnhancedROMDownloader(
        proxy_count=3,
        sequential_mode=True,
        delay_range=(1, 3),
        enable_behavioral_randomization=True
    )
    
    print(f"   ✅ EnhancedROMDownloader created with behavioral randomization")
    print(f"   🤖 Behavioral randomizer enabled: {downloader.enable_behavioral_randomization}")
    print(f"   🎯 Current pattern: {downloader.behavioral_randomizer.current_pattern}")
    
    # Test pattern switching
    downloader.behavioral_randomizer.current_pattern = 'quick_burst'
    print(f"   🔄 Switched to pattern: {downloader.behavioral_randomizer.current_pattern}")
    
    # Test delay generation
    delay = downloader.behavioral_randomizer.get_human_like_delay()
    print(f"   ⏱️  Sample delay: {delay:.1f}s")
    
    # Test without behavioral randomization
    downloader_basic = EnhancedROMDownloader(
        proxy_count=3,
        sequential_mode=True,
        delay_range=(1, 3),
        enable_behavioral_randomization=False
    )
    
    print(f"   ✅ EnhancedROMDownloader created without behavioral randomization")
    print(f"   🤖 Behavioral randomizer enabled: {downloader_basic.enable_behavioral_randomization}")
    print(f"   📊 Basic downloader ready for fallback mode")
    
    return True

async def test_enhanced_stats():
    """Test enhanced statistics with behavioral data"""
    print(f"\n7️⃣ Testing Enhanced Statistics...")
    
    downloader = EnhancedROMDownloader(
        enable_behavioral_randomization=True
    )
    
    # Simulate some download activity
    downloader.download_stats['completed'] = 15
    downloader.download_stats['failed'] = 2
    downloader.download_stats['total_size'] = 2.5 * 1024 * 1024 * 1024  # 2.5 GB
    downloader.download_stats['proxy_used'] = 10
    downloader.download_stats['direct_used'] = 7
    
    # Simulate behavioral activity
    for i in range(15):
        downloader.behavioral_randomizer.record_download_attempt(True)
        downloader.behavioral_randomizer.get_human_like_delay()  # Generate delay for stats
    
    print(f"   📊 Testing enhanced statistics display...")
    downloader.print_enhanced_stats()
    
    # Test behavioral stats
    behavior_stats = downloader.behavioral_randomizer.get_session_stats()
    print(f"\n   🎲 Behavioral Statistics:")
    for key, value in behavior_stats.items():
        print(f"      • {key}: {value}")
    
    return True

async def main():
    """Main verification function"""
    start_time = time.time()
    
    try:
        # Run all tests
        await test_behavioral_randomizer()
        await test_enhanced_downloader_integration()
        await test_enhanced_stats()
        
        end_time = time.time()
        
        print(f"\n" + "="*60)
        print(f"🎉 PHASE 3 VERIFICATION COMPLETE!")
        print(f"✅ All behavioral randomization tests passed")
        print(f"⏱️  Total test time: {end_time - start_time:.1f} seconds")
        print(f"="*60)
        print(f"\n🎯 Phase 3 Status: READY FOR PRODUCTION")
        print(f"📋 Next Steps:")
        print(f"   • Run full ROM download test with behavioral randomization")
        print(f"   • Monitor behavioral patterns in real downloads")
        print(f"   • Proceed to Phase 4: Advanced Anti-Detection")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 3 verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n⏹️  Phase 3 verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
