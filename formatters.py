"""
Output formatters for different export formats.
"""

import json
import csv
from typing import List, Union, TextIO
from io import StringIO

try:
    from .models import VideoResult, ChannelResult, PlaylistResult
except ImportError:
    from models import VideoResult, ChannelResult, PlaylistResult


class OutputFormatter:
    """Base class for output formatters."""
    
    def format(self, results: List[Union[VideoResult, ChannelResult, PlaylistResult]], output_file: TextIO = None) -> str:
        """Format results and optionally write to file."""
        raise NotImplementedError


class TableFormatter(OutputFormatter):
    """Format results as a clean table."""
    
    def format(self, results: List[Union[VideoResult, ChannelResult, PlaylistResult]], output_file: TextIO = None) -> str:
        if not results:
            return "No results found."
            
        output = StringIO()
        
        for i, result in enumerate(results, 1):
            if isinstance(result, VideoResult):
                output.write(f"{i}. {result.title}\n")
                output.write(f"   Channel: {result.channel_title}\n")
                if result.duration:
                    output.write(f"   Duration: {result.duration}\n")
                if result.view_count:
                    output.write(f"   Views: {self._format_count(result.view_count)}\n")
                output.write(f"   URL: {result.url}\n")
                
            elif isinstance(result, ChannelResult):
                output.write(f"{i}. {result.name}\n")
                if result.description:
                    output.write(f"   Description: {result.description[:100]}{'...' if len(result.description) > 100 else ''}\n")
                if result.subscriber_count:
                    output.write(f"   Subscribers: {self._format_count(result.subscriber_count)}\n")
                output.write(f"   URL: {result.url}\n")
                
            elif isinstance(result, PlaylistResult):
                output.write(f"{i}. {result.title}\n")
                output.write(f"   Channel: {result.channel_title}\n")
                if result.video_count:
                    output.write(f"   Videos: {result.video_count}\n")
                output.write(f"   URL: {result.url}\n")
                
            if i < len(results):
                output.write("\n")
        
        formatted = output.getvalue()
        
        if output_file:
            output_file.write(formatted)
            
        return formatted
    
    def _format_count(self, count: int) -> str:
        """Format large numbers with K/M/B suffixes."""
        if count >= 1000000000:
            return f"{count/1000000000:.1f}B"
        elif count >= 1000000:
            return f"{count/1000000:.1f}M"
        elif count >= 1000:
            return f"{count/1000:.1f}K"
        return str(count)


class JSONFormatter(OutputFormatter):
    """Format results as JSON."""
    
    def format(self, results: List[Union[VideoResult, ChannelResult, PlaylistResult]], output_file: TextIO = None) -> str:
        data = [result.to_dict() for result in results]
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output_file:
            output_file.write(formatted)
            
        return formatted


class CSVFormatter(OutputFormatter):
    """Format results as CSV."""
    
    def format(self, results: List[Union[VideoResult, ChannelResult, PlaylistResult]], output_file: TextIO = None) -> str:
        if not results:
            return ""
            
        output = StringIO()
        
        # Group results by type for consistent CSV structure
        videos = [r for r in results if isinstance(r, VideoResult)]
        channels = [r for r in results if isinstance(r, ChannelResult)]
        playlists = [r for r in results if isinstance(r, PlaylistResult)]
        
        if videos:
            output.write("Videos:\n")
            writer = csv.writer(output)
            writer.writerow(["Title", "Channel", "Duration", "Views", "URL"])
            for video in videos:
                writer.writerow([
                    video.title,
                    video.channel_title,
                    video.duration or "",
                    video.view_count or "",
                    video.url
                ])
            output.write("\n")
            
        if channels:
            output.write("Channels:\n")
            writer = csv.writer(output)
            writer.writerow(["Name", "Description", "Subscribers", "URL"])
            for channel in channels:
                writer.writerow([
                    channel.name,
                    channel.description or "",
                    channel.subscriber_count or "",
                    channel.url
                ])
            output.write("\n")
            
        if playlists:
            output.write("Playlists:\n")
            writer = csv.writer(output)
            writer.writerow(["Title", "Channel", "Video Count", "URL"])
            for playlist in playlists:
                writer.writerow([
                    playlist.title,
                    playlist.channel_title,
                    playlist.video_count or "",
                    playlist.url
                ])
        
        formatted = output.getvalue()
        
        if output_file:
            output_file.write(formatted)
            
        return formatted


class SimpleFormatter(OutputFormatter):
    """Format results as simple text list."""
    
    def format(self, results: List[Union[VideoResult, ChannelResult, PlaylistResult]], output_file: TextIO = None) -> str:
        if not results:
            return "No results found."
            
        lines = []
        for result in results:
            if isinstance(result, VideoResult):
                lines.append(f"{result.title} - {result.channel_title}")
            elif isinstance(result, ChannelResult):
                lines.append(f"{result.name}")
            elif isinstance(result, PlaylistResult):
                lines.append(f"{result.title} - {result.channel_title}")
                
        formatted = "\n".join(lines)
        
        if output_file:
            output_file.write(formatted)
            
        return formatted


class YtdlpFormatter(OutputFormatter):
    """Format results as yt-dlp commands."""
    
    def __init__(self, audio_format: bool = False):
        self.audio_format = audio_format
    
    def format(self, results: List[Union[VideoResult, ChannelResult, PlaylistResult]], output_file: TextIO = None) -> str:
        if not results:
            return "No results found."
            
        lines = []
        for result in results:
            if isinstance(result, VideoResult):
                if self.audio_format:
                    lines.append(f"yt-dlp -x --audio-format mp3 '{result.url}'")
                else:
                    lines.append(f"yt-dlp '{result.url}'")
            elif isinstance(result, PlaylistResult):
                if self.audio_format:
                    lines.append(f"yt-dlp -x --audio-format mp3 '{result.url}'")
                else:
                    lines.append(f"yt-dlp '{result.url}'")
                    
        formatted = "\n".join(lines)
        
        if output_file:
            output_file.write(formatted)
            
        return formatted


class YtdlpTableFormatter(OutputFormatter):
    """Format results as a table with 'yt-dlp' instead of URL column."""
    
    def __init__(self, audio_format: bool = False):
        self.audio_format = audio_format
    
    def format(self, results: List[Union[VideoResult, ChannelResult, PlaylistResult]], output_file: TextIO = None) -> str:
        if not results:
            return "No results found."
            
        output = StringIO()
        
        for i, result in enumerate(results, 1):
            if isinstance(result, VideoResult):
                output.write(f"{i}. {result.title}\n")
                output.write(f"   Channel: {result.channel_title}\n")
                if result.duration:
                    output.write(f"   Duration: {result.duration}\n")
                if result.view_count:
                    output.write(f"   Views: {self._format_count(result.view_count)}\n")
                if self.audio_format:
                    output.write(f"   yt-dlp -x --audio-format mp3 '{result.url}'\n")
                else:
                    output.write(f"   yt-dlp '{result.url}'\n")
                
            elif isinstance(result, ChannelResult):
                output.write(f"{i}. {result.name}\n")
                if result.description:
                    output.write(f"   Description: {result.description[:100]}{'...' if len(result.description) > 100 else ''}\n")
                if result.subscriber_count:
                    output.write(f"   Subscribers: {self._format_count(result.subscriber_count)}\n")
                output.write(f"   {result.url}\n")
                
            elif isinstance(result, PlaylistResult):
                output.write(f"{i}. {result.title}\n")
                output.write(f"   Channel: {result.channel_title}\n")
                if result.video_count:
                    output.write(f"   Videos: {result.video_count}\n")
                if self.audio_format:
                    output.write(f"   yt-dlp -x --audio-format mp3 '{result.url}'\n")
                else:
                    output.write(f"   yt-dlp '{result.url}'\n")
                
            if i < len(results):
                output.write("\n")
        
        formatted = output.getvalue()
        
        if output_file:
            output_file.write(formatted)
            
        return formatted
    
    def _format_count(self, count: int) -> str:
        """Format large numbers with K/M/B suffixes."""
        if count >= 1000000000:
            return f"{count/1000000000:.1f}B"
        elif count >= 1000000:
            return f"{count/1000000:.1f}M"
        elif count >= 1000:
            return f"{count/1000:.1f}K"
        return str(count)


def get_formatter(format_name: str, **kwargs) -> OutputFormatter:
    """Get formatter by name."""
    formatters = {
        "table": TableFormatter,
        "json": JSONFormatter,
        "csv": CSVFormatter,
        "simple": SimpleFormatter,
        "ytdlp": YtdlpFormatter,
        "ytdlpa": lambda: YtdlpTableFormatter(audio_format=True),
        "ytdlpv": lambda: YtdlpTableFormatter(audio_format=False)
    }
    
    if format_name not in formatters:
        raise ValueError(f"Unknown format: {format_name}")
        
    formatter_class = formatters[format_name]
    if callable(formatter_class) and not isinstance(formatter_class, type):
        return formatter_class()
    return formatter_class(**kwargs)