"""
Data models for YouTube search results.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class VideoResult:
    """Represents a video search result."""
    title: str
    url: str
    channel_title: str
    view_count: Optional[int] = None
    duration: Optional[str] = None  # Human readable format like "10:30"
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    upload_date: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return asdict(self)


@dataclass 
class ChannelResult:
    """Represents a channel search result."""
    name: str
    url: str
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return asdict(self)


@dataclass
class PlaylistResult:
    """Represents a playlist search result."""
    title: str
    url: str
    channel_title: str
    video_count: Optional[int] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return asdict(self)


@dataclass
class SearchResult:
    """Container for search results."""
    videos: list[VideoResult]
    channels: list[ChannelResult] 
    playlists: list[PlaylistResult]
    next_page_token: Optional[str] = None
    has_next_page: bool = False
    
    def __iter__(self):
        """Allow iteration over all results."""
        yield from self.videos
        yield from self.channels
        yield from self.playlists
    
    def total_count(self) -> int:
        """Get total number of results."""
        return len(self.videos) + len(self.channels) + len(self.playlists)


class SearchError(Exception):
    """Exception raised for search-related errors."""
    
    def __init__(self, message: str, response_code: Optional[int] = None):
        self.message = message
        self.response_code = response_code
        super().__init__(self.message)