"""
YouTube Search Client
Main client class for searching YouTube using web scraping (no API required).
Based on PipePipe's search implementation.
"""

import asyncio
import json
import re
from typing import List, Optional, Union, Dict, Any
from urllib.parse import quote_plus, urljoin, urlparse
from datetime import datetime

try:
    import aiohttp
except ImportError:
    raise ImportError("aiohttp is required. Install with: pip install aiohttp")

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("beautifulsoup4 is required. Install with: pip install beautifulsoup4")

from .models import VideoResult, ChannelResult, PlaylistResult, SearchResult, SearchError


class YouTubeSearchClient:
    """
    YouTube search client that doesn't require API keys.
    Uses web scraping similar to how PipePipe works.
    """
    
    def __init__(self, max_results: int = 20):
        self.max_results = max_results
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    def search(self, query: str, max_results: int = None, result_type: str = "video", 
               order: str = "relevance", published_after: str = None, 
               published_before: str = None, duration: str = None, 
               region_code: str = None, channel_id: str = None) -> List[Union[VideoResult, ChannelResult, PlaylistResult]]:
        """
        Search YouTube synchronously.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: class default)
            result_type: Type of content to search for ("video", "channel", "playlist")
            order: Sort order ("relevance", "date", "viewCount", "rating")
            published_after: ISO format date string
            published_before: ISO format date string
            duration: Video duration ("short", "medium", "long") 
            region_code: Country code (e.g. "US")
            channel_id: Search within specific channel
            
        Returns:
            List of search results
        """
        return asyncio.run(self._async_search(
            query=query,
            max_results=max_results,
            result_type=result_type, 
            order=order,
            published_after=published_after,
            published_before=published_before,
            duration=duration,
            region_code=region_code,
            channel_id=channel_id
        ))
        
    def search_videos(self, query: str, max_results: int = None, **kwargs) -> List[VideoResult]:
        """Search for videos only."""
        results = self.search(query, max_results, result_type="video", **kwargs)
        return [r for r in results if isinstance(r, VideoResult)]
        
    def search_channels(self, query: str, max_results: int = None, **kwargs) -> List[ChannelResult]:
        """Search for channels only.""" 
        results = self.search(query, max_results, result_type="channel", **kwargs)
        return [r for r in results if isinstance(r, ChannelResult)]
        
    def search_playlists(self, query: str, max_results: int = None, **kwargs) -> List[PlaylistResult]:
        """Search for playlists only."""
        results = self.search(query, max_results, result_type="playlist", **kwargs)
        return [r for r in results if isinstance(r, PlaylistResult)]
    
    async def _async_search(self, query: str, max_results: int = None,
                           result_type: str = "video", order: str = "relevance",
                           published_after: str = None, published_before: str = None,
                           duration: str = None, region_code: str = None,
                           channel_id: str = None) -> List[Union[VideoResult, ChannelResult, PlaylistResult]]:
        """Internal async search method."""
        
        if not query.strip():
            raise SearchError("Query cannot be empty")
            
        max_results = max_results or self.max_results
        
        async with self:
            try:
                url = self._build_search_url(
                    query, result_type, order, published_after, published_before,
                    duration, region_code, channel_id
                )
                
                html_content = await self._fetch_page(url)
                results = self._parse_search_results(html_content, result_type)
                
                return results[:max_results]
                
            except Exception as e:
                if isinstance(e, SearchError):
                    raise
                raise SearchError(f"Search failed: {str(e)}")
    
    def _build_search_url(self, query: str, result_type: str, order: str,
                         published_after: str, published_before: str,  
                         duration: str, region_code: str, channel_id: str) -> str:
        """Build YouTube search URL with filters."""
        
        base_url = "https://www.youtube.com/results?search_query="
        url = f"{base_url}{quote_plus(query)}"
        
        # Build search parameters (sp parameter)
        filters = []
        
        # Result type
        if result_type == "video":
            filters.append("EgIQAQ%253D%253D")  # Video filter
        elif result_type == "channel":
            filters.append("EgIQAg%253D%253D")  # Channel filter  
        elif result_type == "playlist":
            filters.append("EgIQAw%253D%253D")  # Playlist filter
            
        # Sort order
        if order == "date":
            filters.append("CAI%253D")  # Upload date
        elif order == "viewCount":
            filters.append("CAM%253D")  # View count
        elif order == "rating":
            filters.append("CAE%253D")  # Rating
            
        # Duration
        if duration == "short":
            filters.append("EgIYAQ%253D%253D")  # Under 4 minutes
        elif duration == "medium":
            filters.append("EgIYAw%253D%253D")  # 4-20 minutes
        elif duration == "long":
            filters.append("EgIYAg%253D%253D")  # Over 20 minutes
            
        # Upload date
        if published_after or published_before:
            # This would need more complex implementation for exact dates
            pass
            
        if filters:
            # Combine filters (this is simplified - real implementation would be more complex)
            sp_param = filters[0]  # Use first filter for now
            url += f"&sp={sp_param}"
            
        # Channel search
        if channel_id:
            url += f"&channel={channel_id}"
            
        # Region
        if region_code:
            url += f"&region={region_code}"
            
        return url
    
    async def _fetch_page(self, url: str) -> str:
        """Fetch a web page."""
        if not self.session:
            raise SearchError("Session not initialized")
            
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise SearchError(f"HTTP {response.status}: Failed to fetch search results", response.status)
                return await response.text()
        except aiohttp.ClientError as e:
            raise SearchError(f"Network error: {str(e)}")
            
    def _parse_search_results(self, html_content: str, result_type: str) -> List[Union[VideoResult, ChannelResult, PlaylistResult]]:
        """Parse search results from YouTube HTML."""
        results = []
        
        # Try to extract JSON data first (more reliable)
        json_results = self._extract_json_results(html_content, result_type)
        if json_results:
            results.extend(json_results)
            
        # Fallback to HTML parsing if JSON extraction fails
        if not results:
            html_results = self._parse_html_results(html_content, result_type) 
            results.extend(html_results)
            
        return results
    
    def _extract_json_results(self, html_content: str, result_type: str) -> List[Union[VideoResult, ChannelResult, PlaylistResult]]:
        """Extract results from ytInitialData JSON in the page."""
        results = []
        
        # Find ytInitialData JSON
        json_match = re.search(r'var ytInitialData = ({.+?});', html_content, re.DOTALL)
        if not json_match:
            return results
            
        try:
            data = json.loads(json_match.group(1))
            
            # Navigate to search results
            contents = data.get("contents", {})
            search_results = contents.get("twoColumnSearchResultsRenderer", {})
            primary_contents = search_results.get("primaryContents", {})
            section_list = primary_contents.get("sectionListRenderer", {})
            
            for section in section_list.get("contents", []):
                if "itemSectionRenderer" in section:
                    items = section["itemSectionRenderer"].get("contents", [])
                    for item in items:
                        result = self._parse_json_item(item, result_type)
                        if result:
                            results.append(result)
                            
        except (json.JSONDecodeError, KeyError) as e:
            # JSON parsing failed, will fall back to HTML parsing
            pass
            
        return results
    
    def _parse_json_item(self, item: Dict[str, Any], result_type: str) -> Optional[Union[VideoResult, ChannelResult, PlaylistResult]]:
        """Parse a single item from YouTube JSON data."""
        
        # Video result
        if "videoRenderer" in item and result_type in ["video", "all"]:
            video = item["videoRenderer"]
            
            video_id = video.get("videoId", "")
            title = self._extract_text(video.get("title", {}))
            channel_title = self._extract_text(video.get("ownerText", {}))
            
            duration_text = self._extract_text(video.get("lengthText", {}))
            view_count = self._parse_view_count(self._extract_text(video.get("viewCountText", {})))
            
            thumbnail_url = None
            thumbnail_data = video.get("thumbnail", {})
            if "thumbnails" in thumbnail_data:
                thumbnails = thumbnail_data["thumbnails"]
                if thumbnails:
                    thumbnail_url = thumbnails[-1].get("url")  # Get highest resolution
                    
            return VideoResult(
                title=title,
                url=f"https://www.youtube.com/watch?v={video_id}",
                channel_title=channel_title,
                duration=duration_text,
                duration_seconds=self._parse_duration_to_seconds(duration_text),
                view_count=view_count,
                thumbnail_url=thumbnail_url
            )
            
        # Channel result
        elif "channelRenderer" in item and result_type in ["channel", "all"]:
            channel = item["channelRenderer"]
            
            channel_id = channel.get("channelId", "")
            name = self._extract_text(channel.get("title", {}))
            description = self._extract_text(channel.get("descriptionSnippet", {}))
            subscriber_count = self._parse_view_count(self._extract_text(channel.get("subscriberCountText", {})))
            
            avatar_url = None
            thumbnail_data = channel.get("thumbnail", {})
            if "thumbnails" in thumbnail_data:
                thumbnails = thumbnail_data["thumbnails"]
                if thumbnails:
                    avatar_url = thumbnails[-1].get("url")
                    
            return ChannelResult(
                name=name,
                url=f"https://www.youtube.com/channel/{channel_id}",
                description=description,
                subscriber_count=subscriber_count,
                avatar_url=avatar_url
            )
            
        # Playlist result
        elif "playlistRenderer" in item and result_type in ["playlist", "all"]:
            playlist = item["playlistRenderer"]
            
            playlist_id = playlist.get("playlistId", "")
            title = self._extract_text(playlist.get("title", {}))
            channel_title = self._extract_text(playlist.get("ownerText", {}))
            video_count = self._parse_video_count(self._extract_text(playlist.get("videoCountText", {})))
            
            thumbnail_url = None
            thumbnails = playlist.get("thumbnails", [])
            if thumbnails and "thumbnails" in thumbnails[0]:
                thumb_data = thumbnails[0]["thumbnails"]
                if thumb_data:
                    thumbnail_url = thumb_data[-1].get("url")
                    
            return PlaylistResult(
                title=title,
                url=f"https://www.youtube.com/playlist?list={playlist_id}",
                channel_title=channel_title,
                video_count=video_count,
                thumbnail_url=thumbnail_url
            )
            
        return None
    
    def _parse_html_results(self, html_content: str, result_type: str) -> List[Union[VideoResult, ChannelResult, PlaylistResult]]:
        """Fallback HTML parsing using BeautifulSoup."""
        results = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        if result_type in ["video", "all"]:
            # Look for video containers
            video_containers = soup.select('div[data-context-item-id], .ytd-video-renderer')
            for container in video_containers:
                result = self._parse_video_container(container)
                if result:
                    results.append(result)
                    
        if result_type in ["channel", "all"]:
            # Look for channel containers
            channel_containers = soup.select('.ytd-channel-renderer')
            for container in channel_containers:
                result = self._parse_channel_container(container)
                if result:
                    results.append(result)
                    
        if result_type in ["playlist", "all"]:
            # Look for playlist containers
            playlist_containers = soup.select('.ytd-playlist-renderer')
            for container in playlist_containers:
                result = self._parse_playlist_container(container)
                if result:
                    results.append(result)
                    
        return results
    
    def _parse_video_container(self, container) -> Optional[VideoResult]:
        """Parse a video container from HTML."""
        try:
            # Extract video ID
            video_id = container.get('data-context-item-id')
            if not video_id:
                link = container.select_one('a[href*="watch?v="]')
                if link:
                    href = link.get('href', '')
                    match = re.search(r'watch\?v=([^&]+)', href)
                    if match:
                        video_id = match.group(1)
                        
            if not video_id:
                return None
                
            # Extract title
            title_elem = container.select_one('h3 a, .video-title, #video-title')
            title = title_elem.get('title', '') or title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract channel
            channel_elem = container.select_one('.ytd-channel-name a, .channel-name')
            channel_title = channel_elem.get_text(strip=True) if channel_elem else ""
            
            # Extract duration
            duration_elem = container.select_one('.ytd-thumbnail-overlay-time-status-renderer, .duration')
            duration = duration_elem.get_text(strip=True) if duration_elem else ""
            
            # Extract thumbnail
            img_elem = container.select_one('img')
            thumbnail_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            if thumbnail_url and thumbnail_url.startswith('//'):
                thumbnail_url = 'https:' + thumbnail_url
                
            if title:
                return VideoResult(
                    title=title,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    channel_title=channel_title,
                    duration=duration,
                    duration_seconds=self._parse_duration_to_seconds(duration),
                    thumbnail_url=thumbnail_url
                )
                
        except Exception:
            pass
            
        return None
    
    def _parse_channel_container(self, container) -> Optional[ChannelResult]:
        """Parse a channel container from HTML."""
        try:
            # Extract channel ID
            link = container.select_one('a[href*="/channel/"], a[href*="/c/"], a[href*="/@"]')
            if not link:
                return None
                
            href = link.get('href', '')
            channel_url = urljoin('https://www.youtube.com', href)
            
            # Extract name
            name_elem = container.select_one('.ytd-channel-name, .channel-title, h3 a')
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            # Extract description
            desc_elem = container.select_one('.channel-description, .description-snippet')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract avatar
            img_elem = container.select_one('img')
            avatar_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            if avatar_url and avatar_url.startswith('//'):
                avatar_url = 'https:' + avatar_url
                
            if name:
                return ChannelResult(
                    name=name,
                    url=channel_url,
                    description=description,
                    avatar_url=avatar_url
                )
                
        except Exception:
            pass
            
        return None
    
    def _parse_playlist_container(self, container) -> Optional[PlaylistResult]:
        """Parse a playlist container from HTML.""" 
        try:
            # Extract playlist ID
            link = container.select_one('a[href*="list="]')
            if not link:
                return None
                
            href = link.get('href', '')
            match = re.search(r'list=([^&]+)', href)
            if not match:
                return None
                
            playlist_id = match.group(1)
            
            # Extract title
            title_elem = container.select_one('.playlist-title, h3 a, #video-title')
            title = title_elem.get('title', '') or title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract channel
            channel_elem = container.select_one('.ytd-channel-name a, .playlist-owner')
            channel_title = channel_elem.get_text(strip=True) if channel_elem else ""
            
            # Extract thumbnail
            img_elem = container.select_one('img')
            thumbnail_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            if thumbnail_url and thumbnail_url.startswith('//'):
                thumbnail_url = 'https:' + thumbnail_url
                
            if title:
                return PlaylistResult(
                    title=title,
                    url=f"https://www.youtube.com/playlist?list={playlist_id}",
                    channel_title=channel_title,
                    thumbnail_url=thumbnail_url
                )
                
        except Exception:
            pass
            
        return None
    
    def _extract_text(self, text_obj: Dict[str, Any]) -> str:
        """Extract text from YouTube's JSON text objects."""
        if isinstance(text_obj, str):
            return text_obj
        if isinstance(text_obj, dict):
            if "simpleText" in text_obj:
                return text_obj["simpleText"]
            elif "runs" in text_obj:
                return "".join(run.get("text", "") for run in text_obj["runs"])
        return ""
    
    def _parse_view_count(self, text: str) -> Optional[int]:
        """Parse view count from text like '1.2M views'."""
        if not text:
            return None
            
        # Remove commas and normalize
        text = text.replace(',', '').replace(' views', '').replace(' subscribers', '')
        
        # Handle K, M, B suffixes
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if text.upper().endswith(suffix):
                try:
                    number = float(text[:-1])
                    return int(number * multiplier)
                except ValueError:
                    pass
                    
        # Try to parse as regular number
        try:
            return int(text)
        except ValueError:
            return None
    
    def _parse_video_count(self, text: str) -> Optional[int]:
        """Parse video count from text."""
        if not text:
            return None
            
        # Extract number from text like "123 videos"
        match = re.search(r'(\d+)', text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
                
        return None
    
    def _parse_duration_to_seconds(self, duration_text: str) -> Optional[int]:
        """Convert duration like '10:30' to seconds."""
        if not duration_text:
            return None
            
        try:
            parts = duration_text.split(':')
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except (ValueError, IndexError):
            pass
            
        return None