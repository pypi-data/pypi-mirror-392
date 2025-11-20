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
Centrum.cz EPG source implementation.
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

from ..base import EPGSource, Channel, Programme
from ..exceptions import APIError


class CentrumCzEPGSource(EPGSource):
    """EPG source for Centrum.cz TV program data."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'CzechTVEPG/2.0.0')
        })
        self.logger = logging.getLogger(__name__)

        # Centrum-specific endpoints
        self.channels_endpoint = config.get('channels_endpoint', '/channels')
        self.broadcasting_endpoint = config.get('broadcasting_endpoint', '/broadcasting')
        self.logo_base_url = config.get('logo_base_url', 'https://tvprogram.centrum.cz/static/images/channels/ch_')

    def fetch_channels(self) -> Dict[str, Channel]:
        """Fetch channels from Centrum.cz API."""
        url = f"{self.base_url}{self.channels_endpoint}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            channels = {}
            for channel_id, info in data.items():
                logo_url = self.get_channel_logo_url(channel_id)
                channels[channel_id] = Channel(
                    id=str(info['id']),
                    name=info['name'],
                    category=info['category'],
                    slug=info['slug'],
                    logo_url=logo_url
                )

            self.logger.info(f"Fetched {len(channels)} channels from Centrum.cz")
            return channels

        except requests.RequestException as e:
            raise APIError(f"Failed to fetch channels from Centrum.cz: {e}")

    def fetch_programmes(self, date: datetime, channel_ids: List[str]) -> Dict[str, List[Programme]]:
        """Fetch programmes from Centrum.cz API."""
        date_str = date.strftime('%Y-%m-%d')
        channels_param = "&".join([f"channels%5B%5D={ch_id}" for ch_id in channel_ids])
        url = f"{self.base_url}{self.broadcasting_endpoint}/{date_str}?{channels_param}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            programmes = {}
            for channel_id, program_list in data.items():
                programmes[channel_id] = []
                for program in program_list:
                    programmes[channel_id].append(Programme(
                        title=program['title'],
                        start=program['start'],
                        stop=program['stop'],
                        description=program.get('description'),
                        genre=str(program.get('genre', '')) if program.get('genre') else None
                    ))

            program_count = sum(len(progs) for progs in programmes.values())
            self.logger.info(f"Fetched {program_count} programmes from Centrum.cz for {date_str}")
            return programmes

        except requests.RequestException as e:
            raise APIError(f"Failed to fetch programmes from Centrum.cz for {date_str}: {e}")

    def get_channel_logo_url(self, channel_id: str) -> Optional[str]:
        """Get logo URL for Centrum.cz channel."""
        return f"{self.logo_base_url}{channel_id}.png"
