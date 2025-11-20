# MIT License
#
# Copyright (c) 2025 Róbert Malovec
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Base classes for EPG sources and data structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class Channel:
    """Channel data structure."""
    id: str
    name: str
    category: str
    slug: str
    logo_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'slug': self.slug,
            'logo_url': self.logo_url
        }


@dataclass
class Programme:
    """Programme data structure with enhanced fields."""
    title: str
    start: str
    stop: str
    description: Optional[str] = None
    genre: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    content_type: Optional[str] = None
    actors: Optional[List[str]] = None
    season_info: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'start': self.start,
            'stop': self.stop,
            'description': self.description,
            'genre': self.genre,
            'category': self.category,
            'image_url': self.image_url,
            'content_type': self.content_type,
            'actors': self.actors,
            'season_info': self.season_info
        }


class EPGSource(ABC):
    """Abstract base class for EPG sources."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize EPG source with configuration."""
        self.config = config
        self.name = config.get('name', 'Unknown')
        self.base_url = config.get('base_url', '')

    @abstractmethod
    def fetch_channels(self) -> Dict[str, Channel]:
        """Fetch available channels from the source."""
        pass

    @abstractmethod
    def fetch_programmes(self, date: datetime, channel_ids: List[str]) -> Dict[str, List[Programme]]:
        """Fetch programmes for given date and channels."""
        pass

    @abstractmethod
    def get_channel_logo_url(self, channel_id: str) -> Optional[str]:
        """Get logo URL for a channel."""
        pass

    def validate_config(self) -> bool:
        """Validate source configuration."""
        required_fields = ['name', 'base_url']
        return all(field in self.config for field in required_fields)

    def get_source_info(self) -> Dict[str, str]:
        """Get source information for XMLTV metadata."""
        return {
            'name': self.name,
            'url': self.base_url
        }
