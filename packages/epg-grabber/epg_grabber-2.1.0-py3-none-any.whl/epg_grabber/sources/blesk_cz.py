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
Blesk.cz EPG source implementation with enhanced programme details.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from ..base import EPGSource, Channel, Programme
from ..exceptions import APIError


class BleskCzEPGSource(EPGSource):
    """EPG source for Blesk.cz TV program data with enhanced programme details."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'CzechTVEPG/2.0.0'),
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json'
        })
        self.logger = logging.getLogger(__name__)
        self._categories = None  # Category cache

        # Endpoints
        self.stations_endpoint = config.get('stations_endpoint', '/api/station')
        self.categories_endpoint = config.get('categories_endpoint', '/api/station/category')
        self.program_endpoint = config.get('program_endpoint', '/api/program')
        self.program_tip_endpoint = config.get('program_tip_endpoint', '/api/program/tip')
        self.logo_base_url = config.get('logo_base_url', 'https://tvprogram.blesk.cz/pvc/images/')

        # Cache for stations data
        self._stations_cache = {}

    def fetch_categories(self):
        """Fetch and cache channel categories."""
        url = f"{self.base_url}{self.categories_endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            self._categories = {
                item['id']: item['attributes']['name']
                for item in response.json().get('data', [])
            }
            self.logger.info(f"Fetched {len(self._categories)} categories")
        except Exception as e:
            self.logger.error(f"Failed to fetch categories: {e}")
            self._categories = {}

    def fetch_channels(self) -> Dict[str, Channel]:
        """Fetch channels with correct logo URLs and category names."""
        if not self._categories:
            self.fetch_categories()

        url = f"{self.base_url}{self.stations_endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            self._stations_cache = {}

            for station in response.json().get('data', []):
                station_id = station['id']
                attrs = station['attributes']
                category_ids = attrs.get('categories', [])
                categories = [self._categories.get(str(cid), f"Unknown ({cid})")
                              for cid in category_ids]
                logo_url = attrs.get('logoUrl')  # Use the API-provided logoUrl

                channel_obj = Channel(
                    id=station_id,
                    name=attrs['name'],
                    category=", ".join(categories) if categories else "General",
                    slug=station_id,
                    logo_url=logo_url
                )
                self._stations_cache[station_id] = channel_obj

            return self._stations_cache

        except Exception as e:
            raise APIError(f"Channel fetch failed: {e}")

    def fetch_programmes(self, date: datetime, channel_ids: List[str]) -> Dict[str, List[Programme]]:
        """Fetch programmes with enhanced details including images."""
        url = f"{self.base_url}{self.program_endpoint}"
        payload = {
            "station_ids": channel_ids,
            "program_dates": [date.strftime('%Y-%m-%d')]
        }

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            programmes = {}

            # Also fetch programme tips to get image URLs
            programme_tips = self.fetch_programme_tips(date, "00:00:00", "23:59:59", channel_ids)
            tips_by_station_time = {}

            for tip in programme_tips:
                station_id = str(tip.get('station_id', ''))
                start_time = tip.get('start_time')
                if station_id and start_time:
                    key = f"{station_id}_{start_time}"
                    tips_by_station_time[key] = tip

            for program in response.json().get('data', []):
                attrs = program.get('attributes', {})
                station_id = str(attrs.get('station', ''))

                if station_id and station_id in channel_ids:
                    if station_id not in programmes:
                        programmes[station_id] = []

                    # Parse times
                    start_time = self._parse_time(attrs.get('startDateTime'))
                    duration = attrs.get('lengthMinutes', 30)
                    stop_time = self._parse_time(attrs.get('stopDateTime')) or \
                        self._calculate_stop_time(start_time, duration)

                    if start_time and stop_time:
                        # Try to find matching tip for image URL
                        tip_key = f"{station_id}_{start_time}"
                        matching_tip = tips_by_station_time.get(tip_key)
                        image_url = matching_tip.get('image_url') if matching_tip else None

                        programmes[station_id].append(Programme(
                            title=attrs.get('name', 'Unknown'),
                            start=start_time,
                            stop=stop_time,
                            description=attrs.get('description'),
                            genre=str(attrs.get('genre_id', '')) if attrs.get('genre_id') else None,
                            category=attrs.get('contentType', attrs.get('genre', attrs.get('category'))),
                            image_url=image_url,
                            content_type=attrs.get('contentType')
                        ))

            self.logger.info(f"Fetched {sum(len(p) for p in programmes.values())} programmes with enhanced details")
            return programmes

        except Exception as e:
            raise APIError(f"Programme fetch failed: {e}")

    def fetch_programme_tips(self, date: datetime, time_from: str = "00:00:00",
                             time_to: str = "23:59:59", stations: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch programme tips with enhanced details including images.

        Args:
            date: Date to fetch programmes for
            time_from: Start time (HH:MM:SS format)
            time_to: End time (HH:MM:SS format)
            stations: List of station IDs, or None for all stations

        Returns:
            List of programme dictionaries with enhanced details
        """
        url = f"{self.base_url}{self.program_tip_endpoint}"

        # Prepare parameters
        params = {
            'date_start': date.strftime('%Y-%m-%d'),
            'time_from': time_from,
            'time_to': time_to,
            'stations': ','.join(stations) if stations else 'undefined'
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            programmes = []
            for program in response.json().get('data', []):
                attrs = program.get('attributes', {})

                programme_data = {
                    'id': program.get('id'),
                    'title': attrs.get('name', 'Unknown'),
                    'content_type': attrs.get('contentType'),
                    'date': attrs.get('date'),
                    'station_id': str(attrs.get('station', '')),
                    'image_url': attrs.get('imageUrl'),
                    'start_datetime': attrs.get('startDateTime'),
                    'duration_minutes': attrs.get('lengthMinutes', 0),
                    'start_time': self._parse_time(attrs.get('startDateTime')),
                    'stop_time': self._calculate_stop_time(
                        self._parse_time(attrs.get('startDateTime')),
                        attrs.get('lengthMinutes', 0)
                    )
                }
                programmes.append(programme_data)

            self.logger.info(f"Fetched {len(programmes)} programme tips for {date.strftime('%Y-%m-%d')}")
            return programmes

        except Exception as e:
            raise APIError(f"Failed to fetch programme tips: {e}")

    def fetch_programme_details(self, programme_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific programme.

        Args:
            programme_id: The programme ID

        Returns:
            Dictionary with detailed programme information including description, cast, etc.
        """
        url = f"{self.base_url}{self.program_endpoint}/{programme_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json().get('data', {})
            attrs = data.get('attributes', {})

            programme_details = {
                'id': data.get('id'),
                'title': attrs.get('name'),
                'content_type': attrs.get('contentType'),
                'season_name': attrs.get('seasonName'),
                'date': attrs.get('date'),
                'station_id': str(attrs.get('station', '')),
                'description': attrs.get('description'),
                'image_url': attrs.get('imageUrl'),
                'start_datetime': attrs.get('startDateTime'),
                'duration_minutes': attrs.get('lengthMinutes', 0),
                'actors': attrs.get('actors', []),
                'gallery_images': attrs.get('galleryImages', []),
                'trailers': attrs.get('trailers', []),
                'next_episodes': attrs.get('nextEpisodes', [])
            }

            self.logger.info(f"Fetched details for programme {programme_id}")
            return programme_details

        except Exception as e:
            self.logger.error(f"Failed to fetch programme details for {programme_id}: {e}")
            return None

    def get_current_programmes_with_images(self, station_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Get current programmes with images for specified stations.

        Args:
            station_ids: List of station IDs, or None for all stations

        Returns:
            List of current programmes with image URLs
        """
        current_time = datetime.now()
        current_time_str = current_time.strftime('%H:%M:%S')

        return self.fetch_programme_tips(
            date=current_time,
            time_from=current_time_str,
            time_to="23:59:59",
            stations=station_ids
        )

    def _parse_time(self, time_str: Optional[str]) -> Optional[str]:
        """Convert Blesk time format to ISO8601."""
        if not time_str:
            return None
        try:
            # Handle timezone-aware datetime strings
            if '+' in time_str:
                dt = datetime.fromisoformat(time_str)
                return dt.isoformat()
            return datetime.fromisoformat(time_str.replace('Z', '+00:00')).isoformat()
        except Exception as e:
            self.logger.warning(f"Error parsing time {time_str}: {e}")
            return None

    def _calculate_stop_time(self, start: Optional[str], duration: int) -> Optional[str]:
        """Calculate stop time from duration."""
        if not start or not duration:
            return None
        try:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            return (start_dt + timedelta(minutes=duration)).isoformat()
        except Exception as e:
            self.logger.warning(f"Error calculating stop time: {e}")
            return None

    def get_channel_logo_url(self, channel_id: str) -> Optional[str]:
        """Return the logoUrl from the station cache if available."""
        return self._stations_cache.get(channel_id, Channel('', '', '', '', None)).logo_url
