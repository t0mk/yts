"""
Command Line Interface for YTS (YouTube Search)
"""

import argparse
import sys
import asyncio
from typing import Optional

from .client import YouTubeSearchClient
from .models import SearchError
from .formatters import get_formatter


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="YTS - YouTube Search without API",
        prog="yts"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode to see API calls"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for content")
    search_parser.add_argument("query", nargs="+", help="Search query")
    search_parser.add_argument("--max-results", type=int, default=20, help="Maximum number of results")
    search_parser.add_argument("--type", choices=["video", "channel", "playlist"], default="video", help="Type of content to search for")
    search_parser.add_argument("--order", choices=["relevance", "date", "viewCount", "rating"], default="relevance", help="Sort order")
    search_parser.add_argument("--published-after", help="Published after date (ISO format)")
    search_parser.add_argument("--published-before", help="Published before date (ISO format)")
    search_parser.add_argument("--duration", choices=["short", "medium", "long"], help="Video duration filter")
    search_parser.add_argument("--region", help="Region code (e.g., US)")
    search_parser.add_argument("--channel-id", help="Search within specific channel")
    search_parser.add_argument("--format", choices=["table", "json", "csv", "simple"], default="table", help="Output format")
    search_parser.add_argument("--output", help="Output file")
    search_parser.add_argument("--ytdlpa", action="store_true", help="Generate yt-dlp audio download commands")
    search_parser.add_argument("--ytdlpv", action="store_true", help="Generate yt-dlp video download commands")
    
    # Specialized search commands
    videos_parser = subparsers.add_parser("videos", help="Search videos only")
    videos_parser.add_argument("query", nargs="+", help="Search query")
    videos_parser.add_argument("--max-results", type=int, default=20, help="Maximum number of results")
    videos_parser.add_argument("--order", choices=["relevance", "date", "viewCount", "rating"], default="relevance", help="Sort order")
    videos_parser.add_argument("--published-after", help="Published after date (ISO format)")
    videos_parser.add_argument("--published-before", help="Published before date (ISO format)")
    videos_parser.add_argument("--duration", choices=["short", "medium", "long"], help="Video duration filter")
    videos_parser.add_argument("--region", help="Region code (e.g., US)")
    videos_parser.add_argument("--channel-id", help="Search within specific channel")
    videos_parser.add_argument("--format", choices=["table", "json", "csv", "simple"], default="table", help="Output format")
    videos_parser.add_argument("--output", help="Output file")
    videos_parser.add_argument("--ytdlpa", action="store_true", help="Generate yt-dlp audio download commands")
    videos_parser.add_argument("--ytdlpv", action="store_true", help="Generate yt-dlp video download commands")
    
    channels_parser = subparsers.add_parser("channels", help="Search channels only")
    channels_parser.add_argument("query", nargs="+", help="Search query")
    channels_parser.add_argument("--max-results", type=int, default=20, help="Maximum number of results")
    channels_parser.add_argument("--format", choices=["table", "json", "csv", "simple"], default="table", help="Output format")
    channels_parser.add_argument("--output", help="Output file")
    
    playlists_parser = subparsers.add_parser("playlists", help="Search playlists only")
    playlists_parser.add_argument("query", nargs="+", help="Search query")
    playlists_parser.add_argument("--max-results", type=int, default=20, help="Maximum number of results")
    playlists_parser.add_argument("--format", choices=["table", "json", "csv", "simple"], default="table", help="Output format")
    playlists_parser.add_argument("--output", help="Output file")
    playlists_parser.add_argument("--ytdlpa", action="store_true", help="Generate yt-dlp audio download commands")
    playlists_parser.add_argument("--ytdlpv", action="store_true", help="Generate yt-dlp video download commands")
    
    # Quota command (placeholder for API compatibility)
    quota_parser = subparsers.add_parser("quota", help="Check quota information")
    
    return parser


def handle_search(args, client: YouTubeSearchClient):
    """Handle search command."""
    query = " ".join(args.query)
    
    if args.debug:
        print(f"Searching for: {query}")
        print(f"Type: {args.type}")
        print(f"Max results: {args.max_results}")
    
    try:
        results = client.search(
            query=query,
            max_results=args.max_results,
            result_type=args.type,
            order=args.order,
            published_after=args.published_after,
            published_before=args.published_before,
            duration=args.duration,
            region_code=args.region,
            channel_id=args.channel_id
        )
        
        # Determine output format
        format_name = args.format
        if args.ytdlpa:
            format_name = "ytdlpa"
        elif args.ytdlpv:
            format_name = "ytdlpv"
            
        formatter = get_formatter(format_name)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                formatter.format(results, f)
            print(f"Results saved to {args.output}")
        else:
            output = formatter.format(results)
            print(output)
            
    except SearchError as e:
        print(f"Search error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_videos(args, client: YouTubeSearchClient):
    """Handle videos command."""
    query = " ".join(args.query)
    
    try:
        results = client.search_videos(
            query=query,
            max_results=args.max_results,
            order=args.order,
            published_after=args.published_after,
            published_before=args.published_before,
            duration=args.duration,
            region_code=args.region,
            channel_id=args.channel_id
        )
        
        # Determine output format
        format_name = args.format
        if args.ytdlpa:
            format_name = "ytdlpa"
        elif args.ytdlpv:
            format_name = "ytdlpv"
            
        formatter = get_formatter(format_name)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                formatter.format(results, f)
            print(f"Results saved to {args.output}")
        else:
            output = formatter.format(results)
            print(output)
            
    except SearchError as e:
        print(f"Search error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_channels(args, client: YouTubeSearchClient):
    """Handle channels command."""
    query = " ".join(args.query)
    
    try:
        results = client.search_channels(
            query=query,
            max_results=args.max_results
        )
        
        formatter = get_formatter(args.format)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                formatter.format(results, f)
            print(f"Results saved to {args.output}")
        else:
            output = formatter.format(results)
            print(output)
            
    except SearchError as e:
        print(f"Search error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_playlists(args, client: YouTubeSearchClient):
    """Handle playlists command."""
    query = " ".join(args.query)
    
    try:
        results = client.search_playlists(
            query=query,
            max_results=args.max_results
        )
        
        # Determine output format
        format_name = args.format
        if args.ytdlpa:
            format_name = "ytdlpa"
        elif args.ytdlpv:
            format_name = "ytdlpv"
            
        formatter = get_formatter(format_name)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                formatter.format(results, f)
            print(f"Results saved to {args.output}")
        else:
            output = formatter.format(results)
            print(output)
            
    except SearchError as e:
        print(f"Search error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_quota(args):
    """Handle quota command (placeholder)."""
    print("YTS does not use YouTube API, so there are no quota limits.")
    print("You can make unlimited searches without API keys.")


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create client
    client = YouTubeSearchClient()
    
    # Handle commands
    if args.command == "search":
        handle_search(args, client)
    elif args.command == "videos":
        handle_videos(args, client)
    elif args.command == "channels":
        handle_channels(args, client)
    elif args.command == "playlists":
        handle_playlists(args, client)
    elif args.command == "quota":
        handle_quota(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()