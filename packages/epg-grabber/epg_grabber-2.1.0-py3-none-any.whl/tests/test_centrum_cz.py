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
Comprehensive tests for the Centrum.cz EPG source.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from datetime import datetime

from epg_grabber.sources.centrum_cz import CentrumCzEPGSource
from epg_grabber.exceptions import APIError


class TestCentrumCzEPGSourceInitialization:
    """Test initialization and configuration."""

    def test_initialization_default_config(self):
        """Test initialization with default configuration."""
        config = {
            'name': 'Centrum.cz',
            'base_url': 'https://api.centrum.cz'
        }
        source = CentrumCzEPGSource(config)

        assert source.base_url == 'https://api.centrum.cz'
        assert source.name == 'Centrum.cz'
        assert source.channels_endpoint == '/channels'
        assert source.broadcasting_endpoint == '/broadcasting'
        assert source.logo_base_url == 'https://tvprogram.centrum.cz/static/images/channels/ch_'

    def test_initialization_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            'name': 'Custom Centrum',
            'base_url': 'https://custom.centrum.cz',
            'user_agent': 'CustomAgent/1.0',
            'channels_endpoint': '/custom/channels',
            'broadcasting_endpoint': '/custom/broadcasting',
            'logo_base_url': 'https://custom.centrum.cz/logos/ch_'
        }
        source = CentrumCzEPGSource(config)

        assert source.base_url == 'https://custom.centrum.cz'
        assert source.name == 'Custom Centrum'
        assert source.channels_endpoint == '/custom/channels'
        assert source.broadcasting_endpoint == '/custom/broadcasting'
        assert source.logo_base_url == 'https://custom.centrum.cz/logos/ch_'

    def test_session_headers(self):
        """Test that session headers are set correctly."""
        config = {
            'name': 'Centrum.cz',
            'base_url': 'https://api.centrum.cz',
            'user_agent': 'TestAgent/1.0'
        }
        source = CentrumCzEPGSource(config)

        assert source.session.headers['User-Agent'] == 'TestAgent/1.0'

    def test_session_headers_default(self):
        """Test default session headers."""
        config = {
            'name': 'Centrum.cz',
            'base_url': 'https://api.centrum.cz'
        }
        source = CentrumCzEPGSource(config)

        assert source.session.headers['User-Agent'] == 'CzechTVEPG/2.0.0'


class TestCentrumCzFetchChannels:
    """Test channel fetching functionality."""

    def test_fetch_channels_success(self):
        """Test successful channel fetching."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'ct1': {
                'id': 1,
                'name': 'ČT1',
                'category': 'Public',
                'slug': 'ct1'
            },
            'ct2': {
                'id': 2,
                'name': 'ČT2',
                'category': 'Public',
                'slug': 'ct2'
            },
            'nova': {
                'id': 3,
                'name': 'TV Nova',
                'category': 'Commercial',
                'slug': 'nova'
            }
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            channels = source.fetch_channels()

        assert len(channels) == 3
        assert 'ct1' in channels
        assert 'ct2' in channels
        assert 'nova' in channels

        # Test ČT1 channel
        ct1 = channels['ct1']
        assert ct1.id == '1'
        assert ct1.name == 'ČT1'
        assert ct1.category == 'Public'
        assert ct1.slug == 'ct1'
        assert ct1.logo_url == 'https://tvprogram.centrum.cz/static/images/channels/ch_ct1.png'

        # Test TV Nova channel
        nova = channels['nova']
        assert nova.id == '3'
        assert nova.name == 'TV Nova'
        assert nova.category == 'Commercial'
        assert nova.slug == 'nova'
        assert nova.logo_url == 'https://tvprogram.centrum.cz/static/images/channels/ch_nova.png'

    def test_fetch_channels_empty_response(self):
        """Test channel fetching with empty response."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch.object(source.session, 'get', return_value=mock_response):
            channels = source.fetch_channels()

        assert len(channels) == 0

    def test_fetch_channels_request_timeout(self):
        """Test channel fetching with request timeout."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        with patch.object(source.session, 'get', side_effect=requests.Timeout("Request timeout")):
            with pytest.raises(APIError) as exc_info:
                source.fetch_channels()

        assert "Failed to fetch channels from Centrum.cz" in str(exc_info.value)
        assert "Request timeout" in str(exc_info.value)

    def test_fetch_channels_http_error(self):
        """Test channel fetching with HTTP error."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        with patch.object(source.session, 'get', return_value=mock_response):
            with pytest.raises(APIError) as exc_info:
                source.fetch_channels()

        assert "Failed to fetch channels from Centrum.cz" in str(exc_info.value)

    def test_fetch_channels_connection_error(self):
        """Test channel fetching with connection error."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        with patch.object(source.session, 'get', side_effect=requests.ConnectionError("Connection failed")):
            with pytest.raises(APIError) as exc_info:
                source.fetch_channels()

        assert "Failed to fetch channels from Centrum.cz" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)

    def test_fetch_channels_json_decode_error(self):
        """Test channel fetching with JSON decode error."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch.object(source.session, 'get', return_value=mock_response):
            with pytest.raises(ValueError) as exc_info:
                source.fetch_channels()

        assert "Invalid JSON" in str(exc_info.value)

    def test_fetch_channels_url_construction(self):
        """Test that the correct URL is constructed for channel fetching."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.fetch_channels()

        expected_url = 'https://api.centrum.cz/channels'
        mock_get.assert_called_once_with(expected_url, timeout=30)

    def test_fetch_channels_custom_endpoint(self):
        """Test channel fetching with custom endpoint."""
        config = {
            'name': 'Centrum.cz',
            'base_url': 'https://api.centrum.cz',
            'channels_endpoint': '/custom/channels'
        }
        source = CentrumCzEPGSource(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.fetch_channels()

        expected_url = 'https://api.centrum.cz/custom/channels'
        mock_get.assert_called_once_with(expected_url, timeout=30)


class TestCentrumCzFetchProgrammes:
    """Test programme fetching functionality."""

    def test_fetch_programmes_success(self):
        """Test successful programme fetching."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1', 'ct2']

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'ct1': [
                {
                    'title': 'Evening News',
                    'start': '2025-01-15T19:00:00+01:00',
                    'stop': '2025-01-15T19:30:00+01:00',
                    'description': 'Daily news program',
                    'genre': 1
                },
                {
                    'title': 'Weather Forecast',
                    'start': '2025-01-15T19:30:00+01:00',
                    'stop': '2025-01-15T19:35:00+01:00',
                    'description': 'Weather information',
                    'genre': 2
                }
            ],
            'ct2': [
                {
                    'title': 'Documentary',
                    'start': '2025-01-15T20:00:00+01:00',
                    'stop': '2025-01-15T21:00:00+01:00',
                    'description': 'Nature documentary',
                    'genre': None  # Test with None genre
                }
            ]
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            programmes = source.fetch_programmes(date, channel_ids)

        assert len(programmes) == 2
        assert 'ct1' in programmes
        assert 'ct2' in programmes

        # Test CT1 programmes
        ct1_programmes = programmes['ct1']
        assert len(ct1_programmes) == 2

        news_prog = ct1_programmes[0]
        assert news_prog.title == 'Evening News'
        assert news_prog.start == '2025-01-15T19:00:00+01:00'
        assert news_prog.stop == '2025-01-15T19:30:00+01:00'
        assert news_prog.description == 'Daily news program'
        assert news_prog.genre == '1'

        weather_prog = ct1_programmes[1]
        assert weather_prog.title == 'Weather Forecast'
        assert weather_prog.genre == '2'

        # Test CT2 programmes
        ct2_programmes = programmes['ct2']
        assert len(ct2_programmes) == 1

        doc_prog = ct2_programmes[0]
        assert doc_prog.title == 'Documentary'
        assert doc_prog.description == 'Nature documentary'
        assert doc_prog.genre is None

    def test_fetch_programmes_empty_response(self):
        """Test programme fetching with empty response."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1']

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch.object(source.session, 'get', return_value=mock_response):
            programmes = source.fetch_programmes(date, channel_ids)

        assert len(programmes) == 0

    def test_fetch_programmes_partial_data(self):
        """Test programme fetching with partial data for some channels."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1', 'ct2', 'ct3']

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'ct1': [
                {
                    'title': 'News',
                    'start': '2025-01-15T19:00:00+01:00',
                    'stop': '2025-01-15T19:30:00+01:00',
                    'description': 'News program'
                }
            ],
            'ct3': [
                {
                    'title': 'Movie',
                    'start': '2025-01-15T20:00:00+01:00',
                    'stop': '2025-01-15T22:00:00+01:00',
                    'description': 'Action movie'
                }
            ]
            # ct2 is missing from response
        }

        with patch.object(source.session, 'get', return_value=mock_response):
            programmes = source.fetch_programmes(date, channel_ids)

        assert len(programmes) == 2
        assert 'ct1' in programmes
        assert 'ct3' in programmes
        assert 'ct2' not in programmes

    def test_fetch_programmes_request_timeout(self):
        """Test programme fetching with request timeout."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1']

        with patch.object(source.session, 'get', side_effect=requests.Timeout("Request timeout")):
            with pytest.raises(APIError) as exc_info:
                source.fetch_programmes(date, channel_ids)

        assert "Failed to fetch programmes from Centrum.cz for 2025-01-15" in str(exc_info.value)
        assert "Request timeout" in str(exc_info.value)

    def test_fetch_programmes_http_error(self):
        """Test programme fetching with HTTP error."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1']

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Internal Server Error")

        with patch.object(source.session, 'get', return_value=mock_response):
            with pytest.raises(APIError) as exc_info:
                source.fetch_programmes(date, channel_ids)

        assert "Failed to fetch programmes from Centrum.cz for 2025-01-15" in str(exc_info.value)

    def test_fetch_programmes_connection_error(self):
        """Test programme fetching with connection error."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1']

        with patch.object(source.session, 'get', side_effect=requests.ConnectionError("Connection failed")):
            with pytest.raises(APIError) as exc_info:
                source.fetch_programmes(date, channel_ids)

        assert "Failed to fetch programmes from Centrum.cz for 2025-01-15" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)

    def test_fetch_programmes_url_construction(self):
        """Test that the correct URL is constructed for programme fetching."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1', 'ct2', 'nova']

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.fetch_programmes(date, channel_ids)

        # Verify the URL construction
        call_args = mock_get.call_args
        url = call_args[0][0]

        assert url.startswith('https://api.centrum.cz/broadcasting/2025-01-15?')
        assert 'channels%5B%5D=ct1' in url
        assert 'channels%5B%5D=ct2' in url
        assert 'channels%5B%5D=nova' in url

    def test_fetch_programmes_custom_endpoint(self):
        """Test programme fetching with custom endpoint."""
        config = {
            'name': 'Centrum.cz',
            'base_url': 'https://api.centrum.cz',
            'broadcasting_endpoint': '/custom/broadcasting'
        }
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1']

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.fetch_programmes(date, channel_ids)

        call_args = mock_get.call_args
        url = call_args[0][0]
        assert url.startswith('https://api.centrum.cz/custom/broadcasting/2025-01-15?')

    def test_fetch_programmes_single_channel(self):
        """Test programme fetching for a single channel."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1']

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'ct1': [
                {
                    'title': 'Single Programme',
                    'start': '2025-01-15T19:00:00+01:00',
                    'stop': '2025-01-15T20:00:00+01:00',
                    'description': 'Test programme'
                }
            ]
        }

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            programmes = source.fetch_programmes(date, channel_ids)

        # Verify URL contains only one channel
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert url.count('channels%5B%5D=') == 1
        assert 'channels%5B%5D=ct1' in url

        assert len(programmes) == 1
        assert 'ct1' in programmes
        assert len(programmes['ct1']) == 1

    def test_fetch_programmes_multiple_channels(self):
        """Test programme fetching for multiple channels."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        date = datetime(2025, 1, 15)
        channel_ids = ['ct1', 'ct2', 'nova', 'prima']

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
            source.fetch_programmes(date, channel_ids)

        # Verify URL contains all channels
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert url.count('channels%5B%5D=') == 4
        for channel_id in channel_ids:
            assert f'channels%5B%5D={channel_id}' in url

    def test_fetch_programmes_date_formatting(self):
        """Test that dates are formatted correctly in the URL."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        # Test different date formats
        test_dates = [
            datetime(2025, 1, 1),    # New Year's Day
            datetime(2025, 12, 31),  # New Year's Eve
            datetime(2025, 6, 15),   # Mid-year
        ]

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        for test_date in test_dates:
            with patch.object(source.session, 'get', return_value=mock_response) as mock_get:
                source.fetch_programmes(test_date, ['ct1'])

            call_args = mock_get.call_args
            url = call_args[0][0]
            expected_date_str = test_date.strftime('%Y-%m-%d')
            assert f'/broadcasting/{expected_date_str}?' in url


class TestCentrumCzGetChannelLogoUrl:
    """Test channel logo URL functionality."""

    def test_get_channel_logo_url_default(self):
        """Test getting channel logo URL with default base URL."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        logo_url = source.get_channel_logo_url('ct1')
        assert logo_url == 'https://tvprogram.centrum.cz/static/images/channels/ch_ct1.png'

    def test_get_channel_logo_url_custom_base(self):
        """Test getting channel logo URL with custom base URL."""
        config = {
            'name': 'Centrum.cz',
            'base_url': 'https://api.centrum.cz',
            'logo_base_url': 'https://custom.centrum.cz/logos/ch_'
        }
        source = CentrumCzEPGSource(config)

        logo_url = source.get_channel_logo_url('nova')
        assert logo_url == 'https://custom.centrum.cz/logos/ch_nova.png'

    def test_get_channel_logo_url_various_channels(self):
        """Test getting logo URLs for various channel IDs."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        test_channels = ['ct1', 'ct2', 'nova', 'prima', 'joj', 'markiza']

        for channel_id in test_channels:
            logo_url = source.get_channel_logo_url(channel_id)
            expected_url = f'https://tvprogram.centrum.cz/static/images/channels/ch_{channel_id}.png'
            assert logo_url == expected_url

    def test_get_channel_logo_url_special_characters(self):
        """Test getting logo URLs for channel IDs with special characters."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        # Test with channel IDs that might contain special characters
        special_channels = ['ct1-hd', 'nova_sport', 'prima.cool']

        for channel_id in special_channels:
            logo_url = source.get_channel_logo_url(channel_id)
            expected_url = f'https://tvprogram.centrum.cz/static/images/channels/ch_{channel_id}.png'
            assert logo_url == expected_url

    def test_get_channel_logo_url_empty_channel_id(self):
        """Test getting logo URL for empty channel ID."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        logo_url = source.get_channel_logo_url('')
        assert logo_url == 'https://tvprogram.centrum.cz/static/images/channels/ch_.png'

    def test_get_channel_logo_url_none_channel_id(self):
        """Test getting logo URL for None channel ID."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        logo_url = source.get_channel_logo_url(None)
        assert logo_url == 'https://tvprogram.centrum.cz/static/images/channels/ch_None.png'


class TestCentrumCzIntegration:
    """Integration tests for Centrum.cz source."""

    def test_full_workflow_simulation(self):
        """Test a complete workflow simulation."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        # Mock channels response
        mock_channels_response = Mock()
        mock_channels_response.raise_for_status.return_value = None
        mock_channels_response.json.return_value = {
            'ct1': {
                'id': 1,
                'name': 'ČT1',
                'category': 'Public',
                'slug': 'ct1'
            },
            'nova': {
                'id': 2,
                'name': 'TV Nova',
                'category': 'Commercial',
                'slug': 'nova'
            }
        }

        # Mock programmes response
        mock_programmes_response = Mock()
        mock_programmes_response.raise_for_status.return_value = None
        mock_programmes_response.json.return_value = {
            'ct1': [
                {
                    'title': 'Morning News',
                    'start': '2025-01-15T07:00:00+01:00',
                    'stop': '2025-01-15T08:00:00+01:00',
                    'description': 'Morning news program',
                    'genre': 1
                },
                {
                    'title': 'Documentary',
                    'start': '2025-01-15T20:00:00+01:00',
                    'stop': '2025-01-15T21:00:00+01:00',
                    'description': 'Nature documentary',
                    'genre': 3
                }
            ],
            'nova': [
                {
                    'title': 'Entertainment Show',
                    'start': '2025-01-15T19:00:00+01:00',
                    'stop': '2025-01-15T20:00:00+01:00',
                    'description': 'Popular entertainment show',
                    'genre': 2
                }
            ]
        }

        with patch.object(source.session, 'get') as mock_get:
            mock_get.side_effect = [mock_channels_response, mock_programmes_response]

            # Fetch channels
            channels = source.fetch_channels()
            assert len(channels) == 2
            assert 'ct1' in channels
            assert 'nova' in channels

            # Verify channel properties
            assert channels['ct1'].name == 'ČT1'
            assert channels['ct1'].category == 'Public'
            assert channels['nova'].name == 'TV Nova'
            assert channels['nova'].category == 'Commercial'

            # Fetch programmes
            date = datetime(2025, 1, 15)
            programmes = source.fetch_programmes(date, ['ct1', 'nova'])

            # Verify programmes
            assert 'ct1' in programmes
            assert 'nova' in programmes
            assert len(programmes['ct1']) == 2
            assert len(programmes['nova']) == 1

            # Verify programme details
            ct1_morning = programmes['ct1'][0]
            assert ct1_morning.title == 'Morning News'
            assert ct1_morning.description == 'Morning news program'
            assert ct1_morning.genre == '1'

            nova_show = programmes['nova'][0]
            assert nova_show.title == 'Entertainment Show'
            assert nova_show.description == 'Popular entertainment show'
            assert nova_show.genre == '2'

    def test_error_recovery_workflow(self):
        """Test workflow with error recovery scenarios."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        # Test channels fetch success, programmes fetch failure
        mock_channels_response = Mock()
        mock_channels_response.raise_for_status.return_value = None
        mock_channels_response.json.return_value = {
            'ct1': {
                'id': 1,
                'name': 'ČT1',
                'category': 'Public',
                'slug': 'ct1'
            }
        }

        with patch.object(source.session, 'get') as mock_get:
            # First call (channels) succeeds
            mock_get.return_value = mock_channels_response
            channels = source.fetch_channels()
            assert len(channels) == 1

            # Second call (programmes) fails
            mock_get.side_effect = requests.RequestException("Network error")
            date = datetime(2025, 1, 15)

            with pytest.raises(APIError):
                source.fetch_programmes(date, ['ct1'])

    def test_performance_with_many_channels(self):
        """Test performance characteristics with many channels."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        # Create a large number of channels
        many_channels = {}
        channel_ids = []
        for i in range(50):
            channel_id = f'channel_{i:02d}'
            channel_ids.append(channel_id)
            many_channels[channel_id] = {
                'id': i,
                'name': f'Channel {i}',
                'category': 'Test',
                'slug': channel_id
            }

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = many_channels

        with patch.object(source.session, 'get', return_value=mock_response):
            channels = source.fetch_channels()

        assert len(channels) == 50

        # Test that all channels have correct logo URLs
        for channel_id in channel_ids:
            assert channel_id in channels
            expected_logo = f'https://tvprogram.centrum.cz/static/images/channels/ch_{channel_id}.png'
            assert channels[channel_id].logo_url == expected_logo

    def test_edge_case_data_handling(self):
        """Test handling of edge case data scenarios."""
        config = {'name': 'Centrum.cz', 'base_url': 'https://api.centrum.cz'}
        source = CentrumCzEPGSource(config)

        # Test with unusual but valid data
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'ct1': [
                {
                    'title': '',  # Empty title
                    'start': '2025-01-15T00:00:00+01:00',
                    'stop': '2025-01-15T00:01:00+01:00',
                    'description': None,  # None description
                    'genre': 0  # Zero genre
                },
                {
                    'title': 'Very Long Title That Might Cause Issues With Some Systems Because It Contains Many Words And Characters',
                    'start': '2025-01-15T23:59:00+01:00',
                    'stop': '2025-01-16T00:00:00+01:00',  # Crosses midnight
                    'description': 'Normal description',
                    'genre': 999  # High genre number
                }
            ]
        }

        date = datetime(2025, 1, 15)

        with patch.object(source.session, 'get', return_value=mock_response):
            programmes = source.fetch_programmes(date, ['ct1'])

        assert 'ct1' in programmes
        assert len(programmes['ct1']) == 2

        # Test empty title handling
        empty_title_prog = programmes['ct1'][0]
        assert empty_title_prog.title == ''
        assert empty_title_prog.description is None
        assert empty_title_prog.genre is None  # Genre 0 is converted to None due to falsy check

        # Test long title handling
        long_title_prog = programmes['ct1'][1]
        assert len(long_title_prog.title) > 50
        assert long_title_prog.genre == '999'
