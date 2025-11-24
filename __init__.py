"""
YTS - YouTube Search Library
A Python library for searching YouTube without using the YouTube API.
Based on PipePipe's search implementation.
"""

from .client import YouTubeSearchClient
from .models import (
    VideoResult, ChannelResult, PlaylistResult, 
    SearchResult, SearchError
)

__version__ = "0.1.0"
__all__ = [
    "YouTubeSearchClient",
    "VideoResult", 
    "ChannelResult", 
    "PlaylistResult",
    "SearchResult",
    "SearchError"
]