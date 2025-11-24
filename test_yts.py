#!/usr/bin/env python3
"""
Simple test script for YTS library
"""

import sys
import asyncio
from yts import YouTubeSearchClient, SearchError

def test_search():
    """Test basic search functionality."""
    print("Testing YTS YouTube Search Library...")
    
    client = YouTubeSearchClient(max_results=5)
    
    try:
        print("\n1. Testing video search:")
        print("Searching for 'python tutorial'...")
        results = client.search("python tutorial", result_type="video")
        
        if results:
            print(f"Found {len(results)} videos:")
            for i, video in enumerate(results[:3], 1):
                print(f"  {i}. {video.title}")
                print(f"     Channel: {video.channel_title}")
                print(f"     URL: {video.url}")
                if video.duration:
                    print(f"     Duration: {video.duration}")
        else:
            print("No video results found")
            
        print("\n2. Testing channel search:")
        print("Searching for 'programming channels'...")
        channel_results = client.search("programming", result_type="channel", max_results=3)
        
        if channel_results:
            print(f"Found {len(channel_results)} channels:")
            for i, channel in enumerate(channel_results, 1):
                print(f"  {i}. {channel.name}")
                print(f"     URL: {channel.url}")
                if channel.subscriber_count:
                    print(f"     Subscribers: {channel.subscriber_count}")
        else:
            print("No channel results found")
            
        print("\n3. Testing playlist search:")
        print("Searching for 'python playlist'...")
        playlist_results = client.search("python playlist", result_type="playlist", max_results=3)
        
        if playlist_results:
            print(f"Found {len(playlist_results)} playlists:")
            for i, playlist in enumerate(playlist_results, 1):
                print(f"  {i}. {playlist.title}")
                print(f"     Channel: {playlist.channel_title}")
                print(f"     URL: {playlist.url}")
                if playlist.video_count:
                    print(f"     Videos: {playlist.video_count}")
        else:
            print("No playlist results found")
            
        print("\n✅ Test completed successfully!")
        return True
        
    except SearchError as e:
        print(f"❌ Search error: {e.message}")
        if e.response_code:
            print(f"HTTP Status: {e.response_code}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_cli_imports():
    """Test that CLI components import correctly."""
    try:
        from yts.cli import main, create_parser
        from yts.formatters import get_formatter
        print("✅ CLI imports successful")
        
        # Test formatter creation
        formatter = get_formatter("table")
        print("✅ Formatter creation successful")
        
        return True
    except Exception as e:
        print(f"❌ CLI import error: {e}")
        return False

def main():
    """Main test function."""
    print("YTS Library Test Suite")
    print("=" * 30)
    
    # Test CLI imports
    cli_ok = test_cli_imports()
    
    if not cli_ok:
        print("❌ CLI tests failed")
        sys.exit(1)
    
    # Test search functionality
    search_ok = test_search()
    
    if search_ok:
        print("\n🎉 All tests passed!")
        print("\nTry the CLI:")
        print("  python -m yts search 'python tutorial'")
        print("  python -m yts videos 'machine learning' --format json")
        print("  python -m yts channels 'tech reviewers'")
    else:
        print("\n❌ Search tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()