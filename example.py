#!/usr/bin/env python3
"""
Example usage of YTS library
"""

from yts import YouTubeSearchClient, SearchError

def main():
    print("YTS Library Example")
    print("=" * 20)
    
    # Create client
    client = YouTubeSearchClient()
    
    try:
        # Search for videos
        print("\n🔍 Searching for 'python tutorial' videos...")
        videos = client.search_videos("python tutorial", max_results=3)
        
        for i, video in enumerate(videos, 1):
            print(f"\n{i}. {video.title}")
            print(f"   Channel: {video.channel_title}")
            print(f"   Duration: {video.duration}")
            print(f"   Views: {video.view_count:,}" if video.view_count else "   Views: Unknown")
            print(f"   URL: {video.url}")
            
        # Search for channels
        print("\n\n🔍 Searching for 'programming' channels...")
        channels = client.search_channels("programming", max_results=2)
        
        for i, channel in enumerate(channels, 1):
            print(f"\n{i}. {channel.name}")
            print(f"   Description: {channel.description[:100] + '...' if channel.description else 'No description'}")
            print(f"   URL: {channel.url}")
            
        # Search with filters
        print("\n\n🔍 Searching for short 'python' videos...")
        short_videos = client.search("python", 
                                    result_type="video",
                                    duration="short", 
                                    order="date",
                                    max_results=2)
                                    
        for i, video in enumerate(short_videos, 1):
            print(f"\n{i}. {video.title}")
            print(f"   Duration: {video.duration}")
            print(f"   Channel: {video.channel_title}")
            
        print("\n✅ Example completed successfully!")
        
    except SearchError as e:
        print(f"❌ Search error: {e.message}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()