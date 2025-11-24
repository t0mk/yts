# YTS - YouTube Search Library

A Python library for searching YouTube without using the YouTube API. Based on PipePipe's search implementation using web scraping.

## Features

- Search videos, channels, and playlists without API keys
- Multiple output formats (table, JSON, CSV, simple)
- yt-dlp integration for easy downloading
- Fast and reliable web scraping
- Command line interface
- Python library for programmatic use

## Installation

```bash
pip install yts
```

Or install from source:

```bash
git clone https://github.com/t0mk/yts
cd yts
pip install -e .
```

## Command Line Usage

### Basic Search

```bash
# Search for videos (default) - no quotes needed for multi-word queries
yts search python programming

# Search with specific number of results
yts search machine learning --max-results 20

# Search for channels
yts search tech channels --type channel

# Search for playlists
yts search python tutorials --type playlist

# Enable debug mode to see API calls
yts --debug search python tutorial
```

### Advanced Searches

```bash
# Search with date filters
yts search AI news --published-after "2023-01-01T00:00:00Z" --published-before "2023-12-31T23:59:59Z"

# Search in specific region
yts search local news --region US

# Search within a specific channel
yts search tutorial --channel-id "UC_x5XG1OV2P6uZZ5FSM9Ttw"

# Filter by video duration
yts search quick tips --duration short --type video

# Sort by upload date
yts search latest tech news --order date
```

### Output Formats

```bash
# Table format (default) - clean layout
yts search coding --format table

# JSON output
yts search programming --format json

# CSV output
yts search tutorials --format csv

# Simple text list
yts search reviews --format simple

# Save to file
yts search data science --format csv --output results.csv
```

### Specialized Commands

```bash
# Search videos only
yts videos python tutorial

# Search channels only
yts channels programming

# Search playlists only
yts playlists learn python

# Check quota information (always shows unlimited)
yts quota
```

### yt-dlp Integration

```bash
# Generate yt-dlp commands for audio download (MP3)
yts videos --ytdlpa python tutorial
yts playlists --ytdlpa coding course

# Generate yt-dlp commands for video download
yts videos --ytdlpv machine learning
yts playlists --ytdlpv full stack development

# Example output with --ytdlpa:
# yt-dlp -x --audio-format mp3 'https://youtube.com/watch?v=...'
```

## Python Library Usage

### Basic Usage

```python
from yts import YouTubeSearchClient

# Create client
client = YouTubeSearchClient()

# Search for videos
results = client.search("python programming", max_results=10)

# Print results
for result in results:
    print(f"Title: {result.title}")
    print(f"Channel: {result.channel_title}")
    print(f"URL: {result.url}")
    print("---")
```

### Advanced Usage

```python
from yts import YouTubeSearchClient
from datetime import datetime

client = YouTubeSearchClient()

# Advanced search with filters
results = client.search(
    query="machine learning",
    max_results=25,
    result_type="video",
    order="viewCount",
    published_after="2023-01-01T00:00:00Z",
    duration="medium",
    region_code="US"
)

# Search specific content types
videos = client.search_videos("python tutorial", max_results=15)
channels = client.search_channels("tech reviewers", max_results=10)
playlists = client.search_playlists("coding bootcamp", max_results=5)

# Export to different formats
import json
results_dict = [result.to_dict() for result in results]
with open("search_results.json", "w") as f:
    json.dump(results_dict, f, indent=2)
```

### Error Handling

```python
from yts import YouTubeSearchClient, SearchError

client = YouTubeSearchClient()

try:
    results = client.search("python programming")
    for result in results:
        print(f"{result.title} - {result.url}")
except SearchError as e:
    print(f"Search failed: {e.message}")
    if e.response_code:
        print(f"HTTP Status: {e.response_code}")
```

## Search Parameters

### Common Parameters

- `query`: Search terms (string)
- `max_results`: Maximum number of results (int, default: 20)
- `result_type`: Type of content ("video", "channel", "playlist")
- `order`: Sort order ("relevance", "date", "viewCount", "rating")

### Video-Specific Parameters

- `duration`: Video length ("short", "medium", "long")
- `published_after`: ISO format date string
- `published_before`: ISO format date string
- `region_code`: Country code (e.g., "US", "GB", "JP")
- `channel_id`: Search within specific channel

## Output Formats

### VideoResult

```python
@dataclass
class VideoResult:
    title: str
    url: str
    channel_title: str
    view_count: Optional[int] = None
    duration: Optional[str] = None  # Human readable like "10:30"
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    upload_date: Optional[str] = None
    description: Optional[str] = None
```

### ChannelResult

```python
@dataclass 
class ChannelResult:
    name: str
    url: str
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
```

### PlaylistResult

```python
@dataclass
class PlaylistResult:
    title: str
    url: str
    channel_title: str
    video_count: Optional[int] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
```

## Requirements

- Python 3.8+
- aiohttp>=3.8.0
- beautifulsoup4>=4.10.0

## How It Works

YTS uses web scraping to extract search results from YouTube's web interface, similar to how PipePipe works. It:

1. Builds search URLs with appropriate filters
2. Fetches HTML content from YouTube
3. Extracts JSON data from the page (ytInitialData)
4. Falls back to HTML parsing if JSON extraction fails
5. Parses and structures the results

This approach doesn't require API keys and isn't subject to quota limits, but may break if YouTube significantly changes their website structure.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Limitations

- Results may be less comprehensive than official YouTube API
- May break if YouTube changes their website structure
- No support for live streams or premieres metadata
- Rate limiting should be implemented by users if making many requests

## Related Projects

- [PipePipe](https://github.com/InfinityLoop1309/PipePipe) - The Android app this library is based on
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Download videos from YouTube and other sites
- [youtube-dl](https://github.com/ytdl-org/youtube-dl) - The original video downloader