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
Core EPG generator class with multi-source support and constructor configuration.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Union

from .base import EPGSource, Channel, Programme
from .sources import EPGSourceFactory
from .exceptions import EPGError, ConfigError


class CzechTVEPGGenerator:
    """Main class for generating Czech TV EPG data in XMLTV format."""

    def __init__(self,
                 config_file: Optional[str] = None,
                 output_path: Optional[Union[str, Path]] = None,
                 source_type: Optional[str] = None,
                 # Source configuration
                 source_name: Optional[str] = None,
                 base_url: Optional[str] = None,
                 channels_endpoint: Optional[str] = None,
                 broadcasting_endpoint: Optional[str] = None,
                 logo_base_url: Optional[str] = None,
                 user_agent: Optional[str] = None,
                 # EPG configuration
                 days_ahead: Optional[int] = None,
                 timezone: Optional[str] = None,
                 language: Optional[str] = None,
                 generator_name: Optional[str] = None,
                 # Output configuration
                 output_filename: Optional[str] = None,
                 encoding: Optional[str] = None,
                 pretty_print: Optional[bool] = None,
                 # Channel and genre configuration
                 channels: Optional[List[Union[str, int]]] = None,
                 genre_mapping: Optional[Dict[str, str]] = None,
                 # Logging configuration
                 log_level: Optional[str] = None,
                 log_format: Optional[str] = None,
                 show_progress: Optional[bool] = False):
        """
        Initialize the EPG generator with configuration.

        Args:
            config_file: Path to configuration file (optional)
            output_path: Override output path for XMLTV file
            source_type: EPG source type

            # Source configuration
            source_name: Name of the EPG source
            base_url: Base URL for the EPG API
            channels_endpoint: Endpoint for channels API
            broadcasting_endpoint: Endpoint for broadcasting API
            logo_base_url: Base URL for channel logos
            user_agent: User agent for HTTP requests

            # EPG configuration
            days_ahead: Number of days ahead to fetch
            timezone: Timezone for XMLTV timestamps
            language: Language code for EPG data
            generator_name: Name of the generator

            # Output configuration
            output_filename: Output filename
            encoding: File encoding
            pretty_print: Whether to pretty print XML

            # Channel and genre configuration
            channels: List of channel IDs to fetch
            genre_mapping: Mapping of genre IDs to category names

            # Logging configuration
            log_level: Logging level
            log_format: Logging format
        """
        self.config_file = config_file

        # Load base configuration from file if available, otherwise use defaults
        if config_file and Path(config_file).exists():
            self.config = self._load_config(config_file)
        else:
            if config_file:
                logging.debug(f"Config file {config_file} not found. Using constructor parameters and defaults.")
            self.config = self._get_default_config()

        self.show_progress = show_progress
        self._progress_bar = None

        # Override with constructor parameters
        self._apply_constructor_overrides(
            output_path, source_type, source_name, base_url, channels_endpoint,
            broadcasting_endpoint, logo_base_url, user_agent, days_ahead, timezone,
            language, generator_name, output_filename, encoding, pretty_print,
            channels, genre_mapping, log_level, log_format
        )

        self._setup_logging()
        self.source = self._create_source()

    def _apply_constructor_overrides(self, output_path, source_type, source_name, base_url,
                                     channels_endpoint, broadcasting_endpoint, logo_base_url,
                                     user_agent, days_ahead, timezone, language, generator_name,
                                     output_filename, encoding, pretty_print, channels,
                                     genre_mapping, log_level, log_format):
        """Apply constructor parameter overrides to configuration."""

        # Handle source type change - apply source-specific defaults
        if source_type:
            self.config['source']['type'] = source_type
            source_configs = self.config.get('source_configs', {})
            if source_type in source_configs:
                # Apply source-specific configuration
                source_config = source_configs[source_type].copy()
                source_config['type'] = source_type
                source_config['user_agent'] = self.config['source'].get('user_agent', 'CzechTVEPG/2.0.0')
                self.config['source'].update(source_config)

        # Output configuration
        if output_path:
            self.config['output']['path'] = str(Path(output_path).resolve())
        if output_filename:
            self.config['output']['filename'] = output_filename
        if encoding:
            self.config['output']['encoding'] = encoding
        if pretty_print is not None:
            self.config['output']['pretty_print'] = pretty_print

        # Source configuration overrides (these take precedence over source_configs)
        if source_name:
            self.config['source']['name'] = source_name
        if base_url:
            self.config['source']['base_url'] = base_url
        if channels_endpoint:
            self.config['source']['channels_endpoint'] = channels_endpoint
        if broadcasting_endpoint:
            self.config['source']['broadcasting_endpoint'] = broadcasting_endpoint
        if logo_base_url:
            self.config['source']['logo_base_url'] = logo_base_url
        if user_agent:
            self.config['source']['user_agent'] = user_agent

        # EPG configuration
        if days_ahead is not None:
            self.config['epg']['days_ahead'] = days_ahead
        if timezone:
            self.config['epg']['timezone'] = timezone
        if language:
            self.config['epg']['language'] = language
        if generator_name:
            self.config['epg']['generator_name'] = generator_name

        # Channel and genre configuration
        if channels is not None:
            self.config['channels'] = [str(ch) for ch in channels]
        if genre_mapping:
            self.config['genre_mapping'] = genre_mapping

        # Logging configuration
        if log_level:
            self.config['logging']['level'] = log_level
        if log_format:
            self.config['logging']['format'] = log_format

    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        logging.info(f"Loading config file {config_file}.")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Ensure output directory exists
                output_path = Path(config.get('output', {}).get('path', '.'))
                output_path.mkdir(parents=True, exist_ok=True)
                return config
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}")

    def _get_default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "source": {
                "type": "centrum_cz",
                "name": "Centrum TV Program",
                "base_url": "https://tvprogram.centrum.cz/api",
                "channels_endpoint": "/channels",
                "broadcasting_endpoint": "/broadcasting",
                "logo_base_url": "https://tvprogram.centrum.cz/static/images/channels/ch_",
                "user_agent": "CzechTVEPG/2.0.0"
            },
            "epg": {
                "days_ahead": 5,
                "timezone": "+0200",
                "language": "cs",
                "generator_name": "Czech TV EPG Generator"
            },
            "output": {
                "path": ".",
                "filename": "tvguide.xml",
                "encoding": "utf-8",
                "pretty_print": True
            },
            "channels": [],
            "genre_mapping": {
                "1": "Entertainment",
                "3": "Movie / Drama",
                "4": "Series / Drama",
                "5": "Documentary",
                "7": "Music / Ballet / Dance",
                "8": "Science / Nature / Documentary",
                "9": "News / Current affairs"
            },
            "logging": {
                "level": "WARN",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            # Add source-specific configurations
            "source_configs": {
                "centrum_cz": {
                    "name": "Centrum TV Program",
                    "base_url": "https://tvprogram.centrum.cz/api",
                    "channels_endpoint": "/channels",
                    "broadcasting_endpoint": "/broadcasting",
                    "logo_base_url": "https://tvprogram.centrum.cz/static/images/channels/ch_"
                },
                "blesk_cz": {
                    "name": "Blesk TV Program",
                    "base_url": "https://tvprogram.blesk.cz",
                    "stations_endpoint": "/api/station",
                    "program_endpoint": "/api/program",
                    "logo_base_url": "https://tvprogram.blesk.cz/images/stations/"
                }
            }
        }

    def enable_progress_bar(self):
        """Enable progress bar display."""
        self.show_progress = True

    def _create_progress_bar(self, total: int, description: str = "Processing"):
        """Create a progress bar if enabled."""
        if self.show_progress:
            try:
                from tqdm import tqdm
                return tqdm(total=total, desc=description, unit="items")
            except ImportError:
                self.logger.warning("tqdm not installed. Install with: pip install tqdm")
                return None
        return None

    def _update_progress_bar(self, progress_bar, increment: int = 1):
        """Update progress bar if it exists."""
        if progress_bar:
            progress_bar.update(increment)

    def _close_progress_bar(self, progress_bar):
        """Close progress bar if it exists."""
        if progress_bar:
            progress_bar.close()

    def _setup_logging(self, log_level="WARN"):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', log_level)),
            format=log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger = logging.getLogger(__name__)

    def _create_source(self, epg_source="centrum_cz") -> EPGSource:
        """Create EPG source instance based on configuration."""
        source_config = self.config.get('source', {})
        source_type = source_config.get('type', epg_source)

        try:
            return EPGSourceFactory.create_source(source_type, source_config)
        except Exception as e:
            raise ConfigError(f"Failed to create EPG source '{source_type}': {e}")

    def _format_xmltv_time(self, iso_time: str) -> str:
        """Convert ISO time to XMLTV format."""
        try:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            timezone = self.config['epg']['timezone']
            return dt.strftime(f'%Y%m%d%H%M%S {timezone}')
        except Exception as e:
            self.logger.warning(f"Failed to parse time {iso_time}: {e}")
            return iso_time

    def _parse_iso_time(self, iso_time: str) -> datetime:
        """Parse ISO time string to datetime object."""
        return datetime.fromisoformat(iso_time.replace('Z', '+00:00'))

    def get_programme_at_time(self, channel_id: Union[str, int], target_time: datetime) -> Optional[Dict]:
        """
        Get the programme airing on a specific channel at a specific time.

        Args:
            channel_id: Channel ID to query
            target_time: The datetime to query for

        Returns:
            Dictionary with programme information and channel details, or None if not found
        """
        try:
            channel_id = str(channel_id)

            # Ensure target_time is timezone-aware
            if target_time.tzinfo is None:
                # Assume local timezone if not specified
                from datetime import timezone, timedelta
                # Use the configured timezone
                tz_offset = self.config['epg']['timezone']
                if tz_offset == "+0200":
                    tz = timezone(timedelta(hours=2))
                elif tz_offset == "+0100":
                    tz = timezone(timedelta(hours=1))
                else:
                    # Default to UTC if unknown timezone
                    tz = timezone.utc
                target_time = target_time.replace(tzinfo=tz)

            # Fetch channels to get channel info
            channels = self.source.fetch_channels()
            if channel_id not in channels:
                raise EPGError(f"Channel {channel_id} not found")

            channel = channels[channel_id]

            # Fetch programmes for the target date
            programmes = self.source.fetch_programmes(target_time.date(), [channel_id])

            if channel_id not in programmes:
                return None

            # Find the programme that contains the target time
            for programme in programmes[channel_id]:
                start_time = self._parse_iso_time(programme.start)
                stop_time = self._parse_iso_time(programme.stop)

                if start_time <= target_time < stop_time:
                    genre_mapping = self.config.get('genre_mapping', {})
                    category = None
                    if programme.genre and programme.genre in genre_mapping:
                        category = genre_mapping[programme.genre]

                    return {
                        'channel': {
                            'id': channel.id,
                            'name': channel.name,
                            'category': channel.category,
                            'logo_url': channel.logo_url
                        },
                        'programme': {
                            'title': programme.title,
                            'start': programme.start,
                            'stop': programme.stop,
                            'start_datetime': start_time,
                            'stop_datetime': stop_time,
                            'description': programme.description,
                            'genre': programme.genre,
                            'category': category,
                            'duration_minutes': int((stop_time - start_time).total_seconds() / 60)
                        },
                        'query_time': target_time,
                        'time_into_programme_minutes': int((target_time - start_time).total_seconds() / 60)
                    }

            return None

        except Exception as e:
            self.logger.error(f"Error querying programme for channel {channel_id} at {target_time}: {e}")
            raise EPGError(f"Failed to get programme information: {e}")

    def get_current_programme(self, channel_id: Union[str, int]) -> Optional[Dict]:
        """
        Get the programme currently airing on a specific channel.

        Args:
            channel_id: Channel ID to query

        Returns:
            Dictionary with current programme information, or None if not found
        """
        return self.get_programme_at_time(channel_id, datetime.now())

    def get_programmes_for_day(self, channel_id: Union[str, int], date: Optional[datetime] = None) -> List[Dict]:
        """
        Get all programmes for a specific channel on a specific day.

        Args:
            channel_id: Channel ID to query
            date: Date to query (default: today)

        Returns:
            List of programme dictionaries
        """
        if date is None:
            date = datetime.now()

        try:
            channel_id = str(channel_id)

            # Fetch channels to get channel info
            channels = self.source.fetch_channels()
            if channel_id not in channels:
                raise EPGError(f"Channel {channel_id} not found")

            channel = channels[channel_id]

            # Fetch programmes for the date
            programmes = self.source.fetch_programmes(date.date(), [channel_id])

            if channel_id not in programmes:
                return []

            result = []
            genre_mapping = self.config.get('genre_mapping', {})

            for programme in programmes[channel_id]:
                start_time = self._parse_iso_time(programme.start)
                stop_time = self._parse_iso_time(programme.stop)

                category = None
                if programme.genre and programme.genre in genre_mapping:
                    category = genre_mapping[programme.genre]

                result.append({
                    'channel': {
                        'id': channel.id,
                        'name': channel.name,
                        'category': channel.category,
                        'logo_url': channel.logo_url
                    },
                    'programme': {
                        'title': programme.title,
                        'start': programme.start,
                        'stop': programme.stop,
                        'start_datetime': start_time,
                        'stop_datetime': stop_time,
                        'description': programme.description,
                        'genre': programme.genre,
                        'category': category,
                        'duration_minutes': int((stop_time - start_time).total_seconds() / 60)
                    }
                })

            return result

        except Exception as e:
            self.logger.error(f"Error getting programmes for channel {channel_id} on {date.date()}: {e}")
            raise EPGError(f"Failed to get programmes: {e}")

    def fetch_and_list_channels(self, output_format: str = "table") -> Optional[List[Dict]]:
        """
        Fetch and display all available channels.

        Args:
            output_format: Format for output ('table', 'json', 'csv', 'return')

        Returns:
            List of channel data if output_format is 'return', None otherwise
        """
        try:
            channels = self.source.fetch_channels()

            if output_format == "return":
                return [channel.to_dict() for channel in channels.values()]

            elif output_format == "table":
                print(f"Source: {self.source.name}")
                print(f"{'ID':<4} | {'Name':<25} | {'Category':<20} | {'Slug':<15}")
                print("-" * 70)
                for channel in channels.values():
                    print(f"{channel.id:<4} | {channel.name:<25} | {channel.category:<20} | {channel.slug:<15}")

            elif output_format == "json":
                formatted_channels = {ch_id: ch.to_dict() for ch_id, ch in channels.items()}
                print(json.dumps(formatted_channels, indent=2, ensure_ascii=False))

            elif output_format == "csv":
                print("ID,Name,Category,Slug")
                for channel in channels.values():
                    print(f"{channel.id},{channel.name},{channel.category},{channel.slug}")

            else:
                raise ValueError(f"Unsupported output format: {output_format}")

        except Exception as e:
            self.logger.error(f"Error fetching channels: {e}")
            raise EPGError(f"Failed to list channels: {e}")

    def get_available_sources(self) -> List[str]:
        """Get list of available EPG sources."""
        return EPGSourceFactory.get_available_sources()

    def get_output_filepath(self, filename: Optional[str] = None) -> Path:
        """Get the full output file path."""
        output_config = self.config['output']
        path = Path(output_config['path'])
        filename = filename or output_config['filename']
        return path / filename

    def get_channel_ids(self, channels_data: Dict[str, Channel]) -> List[str]:
        """Get list of channel IDs to fetch."""
        config_channels = self.config.get('channels', [])

        if config_channels:
            return [str(ch_id) for ch_id in config_channels if str(ch_id) in channels_data]
        else:
            return list(channels_data.keys())

    def create_xmltv_channels(self, tv_element: ET.Element, channels_data: Dict[str, Channel], channel_ids: List[str]):
        """Create channel elements in XMLTV."""
        for channel_id in channel_ids:
            if channel_id in channels_data:
                channel = channels_data[channel_id]
                channel_elem = ET.SubElement(tv_element, "channel")
                channel_elem.set("id", f"ch_{channel_id}")

                display_name = ET.SubElement(channel_elem, "display-name")
                display_name.text = channel.name

                if channel.logo_url:
                    icon = ET.SubElement(channel_elem, "icon")
                    icon.set("src", channel.logo_url)

    def create_xmltv_programmes(self, tv_element: ET.Element, all_data: Dict[str, List[Programme]],
                                channels_data: Dict[str, Channel]):
        """Create programme elements in XMLTV with enhanced details including images."""
        genre_mapping = self.config.get('genre_mapping', {})
        language = self.config['epg']['language']

        # Calculate total programmes for progress bar
        total_programs = sum(len(programmes) for programmes in all_data.values())

        # Create progress bar
        progress_bar = self._create_progress_bar(
            total_programs,
            "Creating XMLTV programmes"
        )

        processed_programs = 0

        try:
            for channel_id, programmes in all_data.items():
                if channel_id in channels_data:
                    for programme in programmes:
                        programme_elem = ET.SubElement(tv_element, "programme")
                        programme_elem.set("channel", f"ch_{channel_id}")
                        programme_elem.set("start", self._format_xmltv_time(programme.start))
                        programme_elem.set("stop", self._format_xmltv_time(programme.stop))

                        # Title
                        title = ET.SubElement(programme_elem, "title")
                        title.set("lang", language)
                        title.text = programme.title

                        # Description
                        if programme.description:
                            desc = ET.SubElement(programme_elem, "desc")
                            desc.set("lang", language)
                            desc.text = programme.description

                        # Category
                        category_text = programme.category
                        if not category_text and programme.genre and programme.genre in genre_mapping:
                            category_text = genre_mapping[programme.genre]

                        if category_text:
                            category = ET.SubElement(programme_elem, "category")
                            category.set("lang", "en")
                            category.text = category_text

                        # Add programme image if available (for Blesk.cz source)
                        if hasattr(self.source, 'fetch_programme_details'):
                            self._add_programme_enhancements(programme_elem, programme, channel_id)

                        processed_programs += 1

                        # Update progress bar for each programme processed
                        self._update_progress_bar(progress_bar, 1)

        finally:
            # Always close the progress bar, even if an exception occurs
            self._close_progress_bar(progress_bar)

        self.logger.info(f"Created {processed_programs} programme entries")

    def _add_programme_enhancements(self, programme_elem: ET.Element, programme: Programme, channel_id: str):
        """Add enhanced programme details for sources that support it (like Blesk.cz)."""
        try:
            # Try to get programme image from tips API first
            programme_tips = self._get_programme_tips_for_time(programme.start, [channel_id])
            programme_image_url = None
            programme_id = None

            for tip in programme_tips:
                if tip.get('title') == programme.title and str(tip.get('station_id')) == channel_id:
                    programme_image_url = tip.get('image_url')
                    programme_id = tip.get('id')
                    break

            # Add programme icon/image
            if programme_image_url:
                icon = ET.SubElement(programme_elem, "icon")
                icon.set("src", programme_image_url)

            # Get detailed programme information if we have the ID
            if programme_id:
                details = self.source.fetch_programme_details(programme_id)
                if details:
                    # Add enhanced description if available
                    if details.get('description') and not programme.description:
                        desc = ET.SubElement(programme_elem, "desc")
                        desc.set("lang", self.config['epg']['language'])
                        desc.text = details['description']

                    # Add cast/credits
                    actors = details.get('actors', [])
                    if actors:
                        credits = ET.SubElement(programme_elem, "credits")
                        for actor in actors[:10]:  # Limit to first 10 actors
                            if actor.get('name'):
                                actor_elem = ET.SubElement(credits, "actor")
                                actor_elem.text = actor['name']

                    # Add content type as sub-title if available
                    if details.get('content_type'):
                        sub_title = ET.SubElement(programme_elem, "sub-title")
                        sub_title.set("lang", "cs")
                        sub_title.text = details['content_type']

                    # Add season information if available
                    if details.get('season_name'):
                        episode_num = ET.SubElement(programme_elem, "episode-num")
                        episode_num.set("system", "onscreen")
                        episode_num.text = details['season_name']

        except Exception as e:
            self.logger.warning(f"Failed to add programme enhancements: {e}")

    def _get_programme_tips_for_time(self, start_time: str, channel_ids: List[str]) -> List[Dict]:
        """Get programme tips for a specific time range."""
        try:
            # Parse the start time to get date and time
            start_dt = self._parse_iso_time(start_time)
            date = start_dt.date()
            time_from = start_dt.strftime('%H:%M:%S')

            # Get tips for a 1-hour window around the programme
            end_time = start_dt + timedelta(hours=1)
            time_to = end_time.strftime('%H:%M:%S')

            if hasattr(self.source, 'fetch_programme_tips'):
                return self.source.fetch_programme_tips(
                    datetime.combine(date, datetime.min.time()),
                    time_from,
                    time_to,
                    channel_ids
                )
        except Exception as e:
            self.logger.warning(f"Failed to get programme tips: {e}")

        return []

    def get_programme_tips_with_images(self, date: Optional[datetime] = None,
                                       time_from: str = "00:00:00",
                                       time_to: str = "23:59:59",
                                       station_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Get programme tips with images for specified time range.
        Only works with Blesk.cz source.
        """
        if not hasattr(self.source, 'fetch_programme_tips'):
            raise EPGError("Programme tips with images only supported by Blesk.cz source")

        if date is None:
            date = datetime.now()

        return self.source.fetch_programme_tips(date, time_from, time_to, station_ids)

    def get_programme_details(self, programme_id: str) -> Optional[Dict]:
        """
        Get detailed programme information including cast, description, images.
        Only works with Blesk.cz source.
        """
        if not hasattr(self.source, 'fetch_programme_details'):
            raise EPGError("Detailed programme information only supported by Blesk.cz source")

        return self.source.fetch_programme_details(programme_id)

    def get_current_programmes_with_images(self, station_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Get current programmes with poster images.
        Only works with Blesk.cz source.
        """
        if not hasattr(self.source, 'get_current_programmes_with_images'):
            raise EPGError("Current programmes with images only supported by Blesk.cz source")

        return self.source.get_current_programmes_with_images(station_ids)

    def generate_epg(self, start_date: Optional[datetime] = None, output_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """Generate complete EPG data with optional progress bar."""
        if start_date is None:
            start_date = datetime.now()

        days_ahead = self.config['epg']['days_ahead']
        self.logger.info(f"Generating EPG for {days_ahead + 1} days starting from {start_date.strftime('%Y-%m-%d')} using {self.source.name}")

        # Fetch channels first
        channels_data = self.source.fetch_channels()
        channel_ids = self.get_channel_ids(channels_data)

        if not channel_ids:
            raise EPGError("No channels configured or available")

        # Create XMLTV root element
        tv = ET.Element("tv")
        source_info = self.source.get_source_info()
        tv.set("source-info-name", source_info['name'])
        tv.set("source-data-url", source_info['url'])
        tv.set("generator-info-name", self.config['epg']['generator_name'])
        tv.set("date-generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        self.create_xmltv_channels(tv, channels_data, channel_ids)

        # Calculate total operations for progress bar
        total_operations = (days_ahead + 1) * len(channel_ids)
        progress_bar = self._create_progress_bar(
            total_operations,
            f"Fetching {days_ahead + 1} days of programmes"
        )

        # Fetch and aggregate programme data
        all_programme_data = {}
        try:
            for day_offset in range(days_ahead + 1):
                fetch_date = start_date + timedelta(days=day_offset)

                if self.show_progress and not progress_bar:
                    print(f"Fetching programmes for {fetch_date.strftime('%Y-%m-%d')}...")

                daily_data = self.source.fetch_programmes(fetch_date, channel_ids)

                # Update progress bar for each channel processed
                self._update_progress_bar(progress_bar, len(channel_ids))

                for channel_id, programmes in daily_data.items():
                    if channel_id not in all_programme_data:
                        all_programme_data[channel_id] = []
                    all_programme_data[channel_id].extend(programmes)

        finally:
            self._close_progress_bar(progress_bar)

        self.create_xmltv_programmes(tv, all_programme_data, channels_data)

        output_file = self.get_output_filepath(output_filename)
        self._write_xml_file(tv, output_file)

        stats = {
            'source': self.source.name,
            'channels': len(channel_ids),
            'programs': sum(len(programmes) for programmes in all_programme_data.values()),
            'date_range': f"{start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=days_ahead)).strftime('%Y-%m-%d')}",
            'generated_at': datetime.now().isoformat(),
            'output_file': str(output_file)
        }

        self.logger.info(f"EPG generation completed: {stats}")
        return str(output_file), stats

    def _write_xml_file(self, tv_element: ET.Element, filepath: Path):
        """Write XML element to file with proper encoding."""
        encoding = self.config['output']['encoding']

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding=encoding) as f:
            f.write(f'<?xml version="1.0" encoding="{encoding.upper()}"?>\n')

            if self.config['output'].get('pretty_print', False):
                ET.indent(tv_element, space="  ", level=0)

            rough_string = ET.tostring(tv_element, encoding='unicode')
            f.write(rough_string)

        self.logger.info(f"XMLTV file written to {filepath}")
