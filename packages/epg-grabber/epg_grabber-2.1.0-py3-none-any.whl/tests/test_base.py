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
Tests for the base module.
"""

import pytest
from datetime import datetime
from epg_grabber.base import Channel, Programme, EPGSource


class TestChannel:
    """Test cases for Channel data class."""

    def test_channel_creation(self):
        """Test Channel can be created with required fields."""
        channel = Channel(
            id="ct1",
            name="ČT1",
            category="public",
            slug="ct1"
        )
        assert channel.id == "ct1"
        assert channel.name == "ČT1"
        assert channel.category == "public"
        assert channel.slug == "ct1"
        assert channel.logo_url is None

    def test_channel_creation_with_logo(self):
        """Test Channel can be created with logo URL."""
        channel = Channel(
            id="ct1",
            name="ČT1",
            category="public",
            slug="ct1",
            logo_url="https://example.com/logo.png"
        )
        assert channel.logo_url == "https://example.com/logo.png"

    def test_channel_to_dict(self):
        """Test Channel to_dict method."""
        channel = Channel(
            id="ct1",
            name="ČT1",
            category="public",
            slug="ct1",
            logo_url="https://example.com/logo.png"
        )
        expected_dict = {
            'id': 'ct1',
            'name': 'ČT1',
            'category': 'public',
            'slug': 'ct1',
            'logo_url': 'https://example.com/logo.png'
        }
        assert channel.to_dict() == expected_dict

    def test_channel_to_dict_without_logo(self):
        """Test Channel to_dict method without logo URL."""
        channel = Channel(
            id="ct2",
            name="ČT2",
            category="public",
            slug="ct2"
        )
        expected_dict = {
            'id': 'ct2',
            'name': 'ČT2',
            'category': 'public',
            'slug': 'ct2',
            'logo_url': None
        }
        assert channel.to_dict() == expected_dict


class TestProgramme:
    """Test cases for Programme data class."""

    def test_programme_creation_minimal(self):
        """Test Programme can be created with minimal required fields."""
        programme = Programme(
            title="Test Programme",
            start="20250617120000 +0200",
            stop="20250617130000 +0200"
        )
        assert programme.title == "Test Programme"
        assert programme.start == "20250617120000 +0200"
        assert programme.stop == "20250617130000 +0200"
        assert programme.description is None
        assert programme.genre is None
        assert programme.category is None
        assert programme.image_url is None
        assert programme.content_type is None
        assert programme.actors is None
        assert programme.season_info is None

    def test_programme_creation_full(self):
        """Test Programme can be created with all fields."""
        programme = Programme(
            title="Test Movie",
            start="20250617120000 +0200",
            stop="20250617140000 +0200",
            description="A great test movie",
            genre="Drama",
            category="Movie",
            image_url="https://example.com/image.jpg",
            content_type="movie",
            actors=["Actor 1", "Actor 2"],
            season_info="Season 1, Episode 5"
        )
        assert programme.title == "Test Movie"
        assert programme.start == "20250617120000 +0200"
        assert programme.stop == "20250617140000 +0200"
        assert programme.description == "A great test movie"
        assert programme.genre == "Drama"
        assert programme.category == "Movie"
        assert programme.image_url == "https://example.com/image.jpg"
        assert programme.content_type == "movie"
        assert programme.actors == ["Actor 1", "Actor 2"]
        assert programme.season_info == "Season 1, Episode 5"

    def test_programme_to_dict_minimal(self):
        """Test Programme to_dict method with minimal fields."""
        programme = Programme(
            title="Test Programme",
            start="20250617120000 +0200",
            stop="20250617130000 +0200"
        )
        expected_dict = {
            'title': 'Test Programme',
            'start': '20250617120000 +0200',
            'stop': '20250617130000 +0200',
            'description': None,
            'genre': None,
            'category': None,
            'image_url': None,
            'content_type': None,
            'actors': None,
            'season_info': None
        }
        assert programme.to_dict() == expected_dict

    def test_programme_to_dict_full(self):
        """Test Programme to_dict method with all fields."""
        programme = Programme(
            title="Test Movie",
            start="20250617120000 +0200",
            stop="20250617140000 +0200",
            description="A great test movie",
            genre="Drama",
            category="Movie",
            image_url="https://example.com/image.jpg",
            content_type="movie",
            actors=["Actor 1", "Actor 2"],
            season_info="Season 1, Episode 5"
        )
        expected_dict = {
            'title': 'Test Movie',
            'start': '20250617120000 +0200',
            'stop': '20250617140000 +0200',
            'description': 'A great test movie',
            'genre': 'Drama',
            'category': 'Movie',
            'image_url': 'https://example.com/image.jpg',
            'content_type': 'movie',
            'actors': ['Actor 1', 'Actor 2'],
            'season_info': 'Season 1, Episode 5'
        }
        assert programme.to_dict() == expected_dict


class MockEPGSource(EPGSource):
    """Mock implementation of EPGSource for testing."""

    def fetch_channels(self):
        """Mock implementation of fetch_channels."""
        return {
            'ct1': Channel(id='ct1', name='ČT1', category='public', slug='ct1')
        }

    def fetch_programmes(self, date, channel_ids):
        """Mock implementation of fetch_programmes."""
        return {
            'ct1': [
                Programme(
                    title='Test Programme',
                    start='20250617120000 +0200',
                    stop='20250617130000 +0200'
                )
            ]
        }

    def get_channel_logo_url(self, channel_id):
        """Mock implementation of get_channel_logo_url."""
        return f"https://example.com/{channel_id}_logo.png"


class TestEPGSource:
    """Test cases for EPGSource abstract base class."""

    def test_epg_source_initialization(self):
        """Test EPGSource can be initialized with config."""
        config = {
            'name': 'Test Source',
            'base_url': 'https://api.example.com'
        }
        source = MockEPGSource(config)
        assert source.config == config
        assert source.name == 'Test Source'
        assert source.base_url == 'https://api.example.com'

    def test_epg_source_initialization_defaults(self):
        """Test EPGSource initialization with missing config values."""
        config = {}
        source = MockEPGSource(config)
        assert source.config == config
        assert source.name == 'Unknown'
        assert source.base_url == ''

    def test_validate_config_valid(self):
        """Test validate_config with valid configuration."""
        config = {
            'name': 'Test Source',
            'base_url': 'https://api.example.com'
        }
        source = MockEPGSource(config)
        assert source.validate_config() is True

    def test_validate_config_missing_name(self):
        """Test validate_config with missing name."""
        config = {
            'base_url': 'https://api.example.com'
        }
        source = MockEPGSource(config)
        assert source.validate_config() is False

    def test_validate_config_missing_base_url(self):
        """Test validate_config with missing base_url."""
        config = {
            'name': 'Test Source'
        }
        source = MockEPGSource(config)
        assert source.validate_config() is False

    def test_validate_config_empty(self):
        """Test validate_config with empty configuration."""
        config = {}
        source = MockEPGSource(config)
        assert source.validate_config() is False

    def test_get_source_info(self):
        """Test get_source_info method."""
        config = {
            'name': 'Test Source',
            'base_url': 'https://api.example.com'
        }
        source = MockEPGSource(config)
        info = source.get_source_info()
        expected_info = {
            'name': 'Test Source',
            'url': 'https://api.example.com'
        }
        assert info == expected_info

    def test_abstract_methods_implemented(self):
        """Test that abstract methods are implemented in mock."""
        config = {
            'name': 'Test Source',
            'base_url': 'https://api.example.com'
        }
        source = MockEPGSource(config)

        # Test fetch_channels
        channels = source.fetch_channels()
        assert isinstance(channels, dict)
        assert 'ct1' in channels
        assert isinstance(channels['ct1'], Channel)

        # Test fetch_programmes
        programmes = source.fetch_programmes(datetime.now(), ['ct1'])
        assert isinstance(programmes, dict)
        assert 'ct1' in programmes
        assert isinstance(programmes['ct1'], list)
        assert len(programmes['ct1']) > 0
        assert isinstance(programmes['ct1'][0], Programme)

        # Test get_channel_logo_url
        logo_url = source.get_channel_logo_url('ct1')
        assert isinstance(logo_url, str)
        assert 'ct1' in logo_url

    def test_cannot_instantiate_abstract_class(self):
        """Test that EPGSource cannot be instantiated directly."""
        config = {'name': 'Test', 'base_url': 'https://example.com'}
        with pytest.raises(TypeError):
            EPGSource(config)
