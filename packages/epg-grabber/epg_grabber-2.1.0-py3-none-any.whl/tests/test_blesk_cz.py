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
Comprehensive tests for the Blesk.cz EPG source.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from datetime import datetime

from epg_grabber.sources.blesk_cz import BleskCzEPGSource
from epg_grabber.base import Channel
from epg_grabber.exceptions import APIError


class TestBleskCzEPGSourceInitialization:
    """Test initialization and configuration."""

    def test_initialization_default_config(self):
        """Test initialization with default configuration."""
        config = {
            'name': 'Blesk.cz',
            'base_url': 'https://api.blesk.cz'
        }
        source = BleskCzEPGSource(config)

        assert source.base_url == 'https://api.blesk.cz'
        assert source.name == 'Blesk.cz'
        assert source.stations_endpoint == '/api/station'
        assert source.categories_endpoint == '/api/station/category'
        assert source.program_endpoint == '/api/program'
        assert source.program_tip_endpoint == '/api/program/tip'
        assert source.logo_base_url == 'https://tvprogram.blesk.cz/pvc/images/'
        assert source._categories is None
        assert source._stations_cache == {}

    def test_initialization_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            'name': 'Custom Blesk',
            'base_url': 'https://custom.blesk.cz',
            'user_agent': 'CustomAgent/1.0',
            'stations_endpoint': '/custom/stations',
            'categories_endpoint': '/custom/categories',
            'program_endpoint': '/custom/programs',
            'program_tip_endpoint': '/custom/tips',
            'logo_base_url': 'https://custom.blesk.cz/logos/'
        }
        source = BleskCzEPGSource(config)

        assert source.base_url == 'https://custom.blesk.cz'
        assert source.name == 'Custom Blesk'
        assert source.stations_endpoint == '/custom/stations'
        assert source.categories_endpoint == '/custom/categories'
        assert source.program_endpoint == '/custom/programs'
        assert source.program_tip_endpoint == '/custom/tips'
        assert source.logo_base_url == 'https://custom.blesk.cz/logos/'

    def test_session_headers(self):
        """Test that session headers are set correctly."""
        config = {
            'name': 'Blesk.cz',
            'base_url': 'https://api.blesk.cz',
            'user_agent': 'TestAgent/1.0'
        }
        source = BleskCzEPGSource(config)

        assert source.session.headers['User-Agent'] == 'TestAgent/1.0'
        assert source.session.headers['Accept'] == 'application/vnd.api+json'
        assert source.session.headers['Content-Type'] == 'application/vnd.api+json'


class TestBleskCzFetchCategories:
    """Test category fetching functionality."""

    def test_fetch_categories_success(self):
        """Test successful category fetching."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'attributes': {'name': 'Entertainment'}},
                {'id': '2', 'attributes': {'name': 'News'}},
                {'id': '3', 'attributes': {'name': 'Sports'}}
            ]
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            source.fetch_categories()

        assert source._categories == {
            '1': 'Entertainment',
            '2': 'News',
            '3': 'Sports'
        }

    def test_fetch_categories_empty_response(self):
        """Test category fetching with empty response."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'data': []}

        with patch.object(source.session, 'get', return_value=mock_response):
            source.fetch_categories()

        assert source._categories == {}

    def test_fetch_categories_api_error(self):
        """Test category fetching with API error."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        with patch.object(source.session, 'get', side_effect=requests.RequestException("API Error")):
            source.fetch_categories()

        assert source._categories == {}

    def test_fetch_categories_http_error(self):
        """Test category fetching with HTTP error."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        with patch.object(source.session, 'get', return_value=mock_response):
            source.fetch_categories()

        assert source._categories == {}


class TestBleskCzFetchChannels:
    """Test channel fetching functionality."""

    def test_fetch_channels_success(self):
        """Test successful channel fetching."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        # Mock categories
        source._categories = {'1': 'Entertainment', '2': 'News'}

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'ct1',
                    'attributes': {
                        'name': 'ČT1',
                        'categories': [1, 2],
                        'logoUrl': 'https://example.com/ct1.png'
                    }
                },
                {
                    'id': 'ct2',
                    'attributes': {
                        'name': 'ČT2',
                        'categories': [],
                        'logoUrl': 'https://example.com/ct2.png'
                    }
                }
            ]
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            channels = source.fetch_channels()

        assert len(channels) == 2
        assert 'ct1' in channels
        assert 'ct2' in channels

        ct1 = channels['ct1']
        assert ct1.id == 'ct1'
        assert ct1.name == 'ČT1'
        assert ct1.category == 'Entertainment, News'
        assert ct1.slug == 'ct1'
        assert ct1.logo_url == 'https://example.com/ct1.png'

        ct2 = channels['ct2']
        assert ct2.id == 'ct2'
        assert ct2.name == 'ČT2'
        assert ct2.category == 'General'
        assert ct2.logo_url == 'https://example.com/ct2.png'

    def test_fetch_channels_without_categories(self):
        """Test channel fetching without pre-fetched categories."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        # Mock category response
        mock_cat_response = Mock()
        mock_cat_response.raise_for_status.return_value = None
        mock_cat_response.json.return_value = {
            'data': [{'id': '1', 'attributes': {'name': 'Entertainment'}}]
        }

        # Mock stations response
        mock_stations_response = Mock()
        mock_stations_response.raise_for_status.return_value = None
        mock_stations_response.json.return_value = {
            'data': [{
                'id': 'ct1',
                'attributes': {
                    'name': 'ČT1',
                    'categories': [1],
                    'logoUrl': 'https://example.com/ct1.png'
                }
            }]
        }

        with patch.object(source.session, 'get') as mock_get:
            mock_get.side_effect = [mock_cat_response, mock_stations_response]
            channels = source.fetch_channels()

        assert len(channels) == 1
        assert channels['ct1'].category == 'Entertainment'

    def test_fetch_channels_api_error(self):
        """Test channel fetching with API error."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)
        source._categories = {}

        with patch.object(source.session, 'get', side_effect=requests.RequestException("API Error")):
            with pytest.raises(APIError) as exc_info:
                source.fetch_channels()

        assert "Channel fetch failed" in str(exc_info.value)

    def test_fetch_channels_unknown_categories(self):
        """Test channel fetching with unknown category IDs."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)
        source._categories = {'1': 'Entertainment'}

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': [{
                'id': 'ct1',
                'attributes': {
                    'name': 'ČT1',
                    'categories': [1, 999],  # 999 is unknown
                    'logoUrl': 'https://example.com/ct1.png'
                }
            }]
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            channels = source.fetch_channels()

        assert channels['ct1'].category == 'Entertainment, Unknown (999)'


class TestBleskCzFetchProgrammes:
    """Test programme fetching functionality."""

    def test_fetch_programmes_success(self):
        """Test successful programme fetching."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)
        channel_ids = ['ct1', 'ct2']

        # Mock programme response
        mock_prog_response = Mock()
        mock_prog_response.raise_for_status.return_value = None
        mock_prog_response.json.return_value = {
            'data': [
                {
                    'attributes': {
                        'station': 'ct1',
                        'name': 'News',
                        'startDateTime': '2025-01-01T20:00:00+01:00',
                        'stopDateTime': '2025-01-01T20:30:00+01:00',
                        'lengthMinutes': 30,
                        'description': 'Evening news',
                        'genre_id': 1,
                        'contentType': 'News'
                    }
                }
            ]
        }

        # Mock programme tips response
        mock_tips_response = Mock()
        mock_tips_response.raise_for_status.return_value = None
        mock_tips_response.json.return_value = {
            'data': [
                {
                    'attributes': {
                        'station': 'ct1',
                        'startDateTime': '2025-01-01T20:00:00+01:00',
                        'imageUrl': 'https://example.com/news.jpg'
                    }
                }
            ]
        }

        with patch.object(source.session, 'post', return_value=mock_prog_response):
            with patch.object(source.session, 'get', return_value=mock_tips_response):
                programmes = source.fetch_programmes(date, channel_ids)

        assert 'ct1' in programmes
        assert len(programmes['ct1']) == 1

        prog = programmes['ct1'][0]
        assert prog.title == 'News'
        assert prog.start == '2025-01-01T20:00:00+01:00'
        assert prog.stop == '2025-01-01T20:30:00+01:00'
        assert prog.description == 'Evening news'
        assert prog.genre == '1'
        assert prog.category == 'News'
        assert prog.content_type == 'News'
        assert prog.image_url == 'https://example.com/news.jpg'

    def test_fetch_programmes_without_stop_time(self):
        """Test programme fetching when stop time needs to be calculated."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)
        channel_ids = ['ct1']

        mock_prog_response = Mock()
        mock_prog_response.raise_for_status.return_value = None
        mock_prog_response.json.return_value = {
            'data': [
                {
                    'attributes': {
                        'station': 'ct1',
                        'name': 'Movie',
                        'startDateTime': '2025-01-01T20:00:00+01:00',
                        'stopDateTime': None,  # Missing stop time
                        'lengthMinutes': 120,
                        'description': 'A great movie'
                    }
                }
            ]
        }

        mock_tips_response = Mock()
        mock_tips_response.raise_for_status.return_value = None
        mock_tips_response.json.return_value = {'data': []}

        with patch.object(source.session, 'post', return_value=mock_prog_response):
            with patch.object(source.session, 'get', return_value=mock_tips_response):
                programmes = source.fetch_programmes(date, channel_ids)

        prog = programmes['ct1'][0]
        assert prog.title == 'Movie'
        assert prog.start == '2025-01-01T20:00:00+01:00'
        # Stop time should be calculated: 20:00 + 120 minutes = 22:00
        assert prog.stop == '2025-01-01T22:00:00+01:00'

    def test_fetch_programmes_api_error(self):
        """Test programme fetching with API error."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)
        channel_ids = ['ct1']

        with patch.object(source.session, 'post', side_effect=requests.RequestException("API Error")):
            with pytest.raises(APIError) as exc_info:
                source.fetch_programmes(date, channel_ids)

        assert "Programme fetch failed" in str(exc_info.value)

    def test_fetch_programmes_invalid_times(self):
        """Test programme fetching with invalid time formats."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)
        channel_ids = ['ct1']

        mock_prog_response = Mock()
        mock_prog_response.raise_for_status.return_value = None
        mock_prog_response.json.return_value = {
            'data': [
                {
                    'attributes': {
                        'station': 'ct1',
                        'name': 'Invalid Programme',
                        'startDateTime': 'invalid-time',
                        'stopDateTime': 'invalid-time',
                        'lengthMinutes': 30
                    }
                }
            ]
        }

        mock_tips_response = Mock()
        mock_tips_response.raise_for_status.return_value = None
        mock_tips_response.json.return_value = {'data': []}

        with patch.object(source.session, 'post', return_value=mock_prog_response):
            with patch.object(source.session, 'get', return_value=mock_tips_response):
                programmes = source.fetch_programmes(date, channel_ids)

        # Programme with invalid times should be skipped
        assert programmes.get('ct1', []) == []


class TestBleskCzFetchProgrammeTips:
    """Test programme tips fetching functionality."""

    def test_fetch_programme_tips_success(self):
        """Test successful programme tips fetching."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'tip1',
                    'attributes': {
                        'name': 'Great Movie',
                        'contentType': 'Movie',
                        'date': '2025-01-01',
                        'station': 'ct1',
                        'imageUrl': 'https://example.com/movie.jpg',
                        'startDateTime': '2025-01-01T20:00:00+01:00',
                        'lengthMinutes': 120
                    }
                }
            ]
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            tips = source.fetch_programme_tips(date)

        assert len(tips) == 1
        tip = tips[0]
        assert tip['id'] == 'tip1'
        assert tip['title'] == 'Great Movie'
        assert tip['content_type'] == 'Movie'
        assert tip['station_id'] == 'ct1'
        assert tip['image_url'] == 'https://example.com/movie.jpg'
        assert tip['duration_minutes'] == 120

    def test_fetch_programme_tips_with_time_range(self):
        """Test programme tips fetching with custom time range."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'data': []}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.fetch_programme_tips(date, "18:00:00", "22:00:00", ['ct1', 'ct2'])

        # Verify the correct parameters were sent
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['date_start'] == '2025-01-01'
        assert params['time_from'] == '18:00:00'
        assert params['time_to'] == '22:00:00'
        assert params['stations'] == 'ct1,ct2'

    def test_fetch_programme_tips_no_stations(self):
        """Test programme tips fetching without specific stations."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'data': []}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.fetch_programme_tips(date)

        # Verify stations parameter is set to 'undefined'
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['stations'] == 'undefined'

    def test_fetch_programme_tips_api_error(self):
        """Test programme tips fetching with API error."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        date = datetime(2025, 1, 1)

        with patch.object(source.session, 'get', side_effect=requests.RequestException("API Error")):
            with pytest.raises(APIError) as exc_info:
                source.fetch_programme_tips(date)

        assert "Failed to fetch programme tips" in str(exc_info.value)


class TestBleskCzFetchProgrammeDetails:
    """Test programme details fetching functionality."""

    def test_fetch_programme_details_success(self):
        """Test successful programme details fetching."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        programme_id = 'prog123'

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': {
                'id': 'prog123',
                'attributes': {
                    'name': 'Amazing Movie',
                    'contentType': 'Movie',
                    'seasonName': 'Season 1',
                    'date': '2025-01-01',
                    'station': 'ct1',
                    'description': 'An amazing movie with great actors',
                    'imageUrl': 'https://example.com/movie.jpg',
                    'startDateTime': '2025-01-01T20:00:00+01:00',
                    'lengthMinutes': 120,
                    'actors': [
                        {'name': 'Actor One'},
                        {'name': 'Actor Two'}
                    ],
                    'galleryImages': ['img1.jpg', 'img2.jpg'],
                    'trailers': ['trailer1.mp4'],
                    'nextEpisodes': ['ep2', 'ep3']
                }
            }
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            details = source.fetch_programme_details(programme_id)

        assert details['id'] == 'prog123'
        assert details['title'] == 'Amazing Movie'
        assert details['content_type'] == 'Movie'
        assert details['season_name'] == 'Season 1'
        assert details['description'] == 'An amazing movie with great actors'
        assert details['station_id'] == 'ct1'
        assert details['duration_minutes'] == 120
        assert len(details['actors']) == 2
        assert details['actors'][0]['name'] == 'Actor One'
        assert len(details['gallery_images']) == 2
        assert len(details['trailers']) == 1
        assert len(details['next_episodes']) == 2

    def test_fetch_programme_details_not_found(self):
        """Test programme details fetching when programme not found."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        programme_id = 'nonexistent'

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        with patch.object(source.session, 'get', return_value=mock_response):
            details = source.fetch_programme_details(programme_id)

        assert details is None

    def test_fetch_programme_details_api_error(self):
        """Test programme details fetching with API error."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        programme_id = 'prog123'

        with patch.object(source.session, 'get', side_effect=requests.RequestException("API Error")):
            details = source.fetch_programme_details(programme_id)

        assert details is None


class TestBleskCzCurrentProgrammes:
    """Test current programmes functionality."""

    @patch('epg_grabber.sources.blesk_cz.datetime')
    def test_get_current_programmes_with_images(self, mock_datetime):
        """Test getting current programmes with images."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        # Mock current time
        mock_now = datetime(2025, 1, 1, 20, 30, 0)
        mock_datetime.now.return_value = mock_now

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'data': []}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.get_current_programmes_with_images(['ct1', 'ct2'])

        # Verify the correct parameters were sent
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['date_start'] == '2025-01-01'
        assert params['time_from'] == '20:30:00'
        assert params['time_to'] == '23:59:59'
        assert params['stations'] == 'ct1,ct2'

    @patch('epg_grabber.sources.blesk_cz.datetime')
    def test_get_current_programmes_all_stations(self, mock_datetime):
        """Test getting current programmes for all stations."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        mock_now = datetime(2025, 1, 1, 20, 30, 0)
        mock_datetime.now.return_value = mock_now

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'data': []}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.get_current_programmes_with_images()

        # Verify stations parameter is set to 'undefined'
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['stations'] == 'undefined'


class TestBleskCzUtilityMethods:
    """Test utility methods."""

    def test_parse_time_iso_format(self):
        """Test parsing ISO format time strings."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        # Test with timezone
        result = source._parse_time('2025-01-01T20:00:00+01:00')
        assert result == '2025-01-01T20:00:00+01:00'

        # Test with Z timezone
        result = source._parse_time('2025-01-01T20:00:00Z')
        assert result == '2025-01-01T20:00:00+00:00'

    def test_parse_time_invalid_format(self):
        """Test parsing invalid time strings."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        result = source._parse_time('invalid-time')
        assert result is None

        result = source._parse_time(None)
        assert result is None

    def test_calculate_stop_time_success(self):
        """Test calculating stop time from start time and duration."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        start_time = '2025-01-01T20:00:00+01:00'
        duration = 90  # 90 minutes

        result = source._calculate_stop_time(start_time, duration)
        assert result == '2025-01-01T21:30:00+01:00'

    def test_calculate_stop_time_invalid_input(self):
        """Test calculating stop time with invalid input."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        # Invalid start time
        result = source._calculate_stop_time('invalid-time', 90)
        assert result is None

        # No start time
        result = source._calculate_stop_time(None, 90)
        assert result is None

        # No duration
        result = source._calculate_stop_time('2025-01-01T20:00:00+01:00', None)
        assert result is None

    def test_get_channel_logo_url_found(self):
        """Test getting channel logo URL when channel exists."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        # Add a channel to the cache
        source._stations_cache['ct1'] = Channel(
            id='ct1',
            name='ČT1',
            category='General',
            slug='ct1',
            logo_url='https://example.com/ct1.png'
        )

        result = source.get_channel_logo_url('ct1')
        assert result == 'https://example.com/ct1.png'

    def test_get_channel_logo_url_not_found(self):
        """Test getting channel logo URL when channel doesn't exist."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        result = source.get_channel_logo_url('nonexistent')
        assert result is None


class TestBleskCzIntegration:
    """Integration tests for Blesk.cz source."""

    def test_full_workflow_simulation(self):
        """Test a complete workflow simulation."""
        config = {'name': 'Blesk.cz', 'base_url': 'https://api.blesk.cz'}
        source = BleskCzEPGSource(config)

        # Mock all API responses
        mock_cat_response = Mock()
        mock_cat_response.raise_for_status.return_value = None
        mock_cat_response.json.return_value = {
            'data': [{'id': '1', 'attributes': {'name': 'Entertainment'}}]
        }

        mock_stations_response = Mock()
        mock_stations_response.raise_for_status.return_value = None
        mock_stations_response.json.return_value = {
            'data': [{
                'id': 'ct1',
                'attributes': {
                    'name': 'ČT1',
                    'categories': [1],
                    'logoUrl': 'https://example.com/ct1.png'
                }
            }]
        }

        mock_prog_response = Mock()
        mock_prog_response.raise_for_status.return_value = None
        mock_prog_response.json.return_value = {
            'data': [{
                'attributes': {
                    'station': 'ct1',
                    'name': 'News',
                    'startDateTime': '2025-01-01T20:00:00+01:00',
                    'stopDateTime': '2025-01-01T20:30:00+01:00',
                    'lengthMinutes': 30,
                    'description': 'Evening news'
                }
            }]
        }

        mock_tips_response = Mock()
        mock_tips_response.raise_for_status.return_value = None
        mock_tips_response.json.return_value = {'data': []}

        with patch.object(source.session, 'get') as mock_get:
            with patch.object(source.session, 'post', return_value=mock_prog_response):
                mock_get.side_effect = [mock_cat_response, mock_stations_response, mock_tips_response]

                # Fetch channels
                channels = source.fetch_channels()
                assert len(channels) == 1
                assert 'ct1' in channels

                # Fetch programmes
                date = datetime(2025, 1, 1)
                programmes = source.fetch_programmes(date, ['ct1'])
                assert 'ct1' in programmes
                assert len(programmes['ct1']) == 1
                assert programmes['ct1'][0].title == 'News'
