#!/usr/bin/env python3
"""Setup script for yts - YouTube Search CLI and Library."""

from setuptools import setup, find_packages

# Create a simple long description for now
long_description = """
# YTS - YouTube Search Library

A Python library for searching YouTube without using the YouTube API.
Based on PipePipe's search implementation using web scraping.

## Features
- Search videos, channels, and playlists
- No API key required
- Multiple output formats (table, JSON, CSV, simple)
- yt-dlp integration
- Command line interface

## Installation
```bash
pip install yts
```

## Usage
```python
from yts import YouTubeSearchClient

client = YouTubeSearchClient()
results = client.search("python programming")
for result in results:
    print(f"{result.title} - {result.url}")
```
"""

setup(
    name="yts",
    version="0.1.0",
    author="t0mk",
    description="YouTube Search CLI and Python Library without API (based on PipePipe)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/t0mk/yts",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ]
    },
    entry_points={
        "console_scripts": [
            "yts=yts.cli:main",
        ],
    },
    keywords="youtube search cli library video channel playlist no-api web-scraping",
    project_urls={
        "Bug Reports": "https://github.com/t0mk/yts/issues",
        "Source": "https://github.com/t0mk/yts",
        "Documentation": "https://github.com/t0mk/yts#readme",
    },
)