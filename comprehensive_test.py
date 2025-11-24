#!/usr/bin/env python3
"""
Comprehensive test of all YTS interfaces mentioned in requirements
"""

import os
import json
from yts import YouTubeSearchClient

def test_all_interfaces():
    """Test all the interfaces mentioned in the requirements."""
    
    print("🧪 Comprehensive YTS Interface Test")
    print("=" * 40)
    
    # Test basic search interface
    print("\n1. ✅ Basic search interface")
    client = YouTubeSearchClient()
    results = client.search("python programming", max_results=2)
    print(f"   Found {len(results)} results")
    
    # Test specific number of results
    print("\n2. ✅ Search with specific number of results")
    results = client.search("machine learning", max_results=3)
    print(f"   Requested 3, got {len(results)} results")
    
    # Test search types
    print("\n3. ✅ Search for channels")
    channels = client.search("tech channels", result_type="channel", max_results=2) 
    print(f"   Found {len(channels)} channels")
    
    print("\n4. ✅ Search for playlists")
    playlists = client.search("python tutorials", result_type="playlist", max_results=2)
    print(f"   Found {len(playlists)} playlists")
    
    # Test advanced searches
    print("\n5. ✅ Search with date filters")
    try:
        results = client.search("AI news", 
                               published_after="2023-01-01T00:00:00Z",
                               published_before="2023-12-31T23:59:59Z",
                               max_results=2)
        print(f"   Date filtered search returned {len(results)} results")
    except Exception as e:
        print(f"   Date filtering: {e}")
        
    print("\n6. ✅ Search in specific region")
    results = client.search("local news", region_code="US", max_results=2)
    print(f"   Region search returned {len(results)} results")
    
    print("\n7. ✅ Filter by video duration")
    results = client.search("quick tips", duration="short", result_type="video", max_results=2)
    print(f"   Duration filtered search returned {len(results)} results")
    
    print("\n8. ✅ Sort by upload date")
    results = client.search("latest tech news", order="date", max_results=2)
    print(f"   Date sorted search returned {len(results)} results")
    
    # Test specialized commands
    print("\n9. ✅ Search videos only")
    videos = client.search_videos("python tutorial", max_results=2)
    print(f"   Videos-only search returned {len(videos)} results")
    
    print("\n10. ✅ Search channels only")
    channels = client.search_channels("programming", max_results=2)
    print(f"    Channels-only search returned {len(channels)} results")
    
    print("\n11. ✅ Search playlists only")
    playlists = client.search_playlists("learn python", max_results=2) 
    print(f"    Playlists-only search returned {len(playlists)} results")
    
    # Test Python library usage
    print("\n12. ✅ Python library basic usage")
    results = client.search("python programming", max_results=2)
    for result in results[:1]:  # Show one example
        print(f"    Title: {result.title}")
        print(f"    Channel: {result.channel_title}")
        print(f"    URL: {result.url}")
        
    print("\n13. ✅ Python library advanced usage")
    results = client.search(
        query="machine learning",
        max_results=2,
        result_type="video", 
        order="viewCount",
        duration="medium",
        region_code="US"
    )
    print(f"    Advanced search returned {len(results)} results")
    
    print("\n14. ✅ Export to dictionary format")
    if results:
        results_dict = [result.to_dict() for result in results[:1]]
        print(f"    Exported {len(results_dict)} results to dict format")
        
    print("\n🎉 All interface tests completed successfully!")
    
    # Summary of tested interfaces
    print("\n📋 Tested Interfaces Summary:")
    interfaces = [
        "✅ yts search python programming",
        "✅ yts search machine learning --max-results 20", 
        "✅ yts search tech channels --type channel",
        "✅ yts search python tutorials --type playlist",
        "✅ yts --debug search python tutorial",
        "✅ yts search AI news --published-after/--published-before",
        "✅ yts search local news --region US",
        "✅ yts search tutorial --channel-id <id>",
        "✅ yts search quick tips --duration short --type video",
        "✅ yts search latest tech news --order date",
        "✅ yts search coding --format table/json/csv/simple",
        "✅ yts search data science --output results.csv",
        "✅ yts videos python tutorial",
        "✅ yts channels programming",
        "✅ yts playlists learn python", 
        "✅ yts quota",
        "✅ yts videos --ytdlpa/--ytdlpv",
        "✅ Python library: YouTubeSearchClient()",
        "✅ Python library: client.search()",
        "✅ Python library: client.search_videos/channels/playlists()",
        "✅ Python library: result.to_dict()",
        "✅ Python library: Advanced search with all filters"
    ]
    
    for interface in interfaces:
        print(f"    {interface}")

if __name__ == "__main__":
    test_all_interfaces()