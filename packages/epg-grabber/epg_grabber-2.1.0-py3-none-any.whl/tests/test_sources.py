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
Tests for the sources module.
"""

import pytest
from unittest.mock import Mock, patch
from epg_grabber.sources import EPGSourceFactory, get_source
from epg_grabber.exceptions import ConfigError
from epg_grabber.base import EPGSource


class MockEPGSource(EPGSource):
    """Mock EPG source for testing."""

    def fetch_channels(self):
        return {}

    def fetch_programmes(self, date, channel_ids):
        return {}

    def get_channel_logo_url(self, channel_id):
        return None


class TestEPGSourceFactory:
    """Test cases for EPGSourceFactory class."""

    def test_get_available_sources(self):
        """Test get_available_sources returns expected sources."""
        sources = EPGSourceFactory.get_available_sources()

        assert isinstance(sources, list)
        assert len(sources) > 0

        # Check for expected source aliases
        expected_sources = ['centrum', 'centrum.cz', 'centrum_cz', 'blesk', 'blesk.cz', 'blesk_cz']
        for source in expected_sources:
            assert source in sources

    def test_register_source(self):
        """Test register_source adds new source to registry."""
        # Save original sources to restore later
        original_sources = EPGSourceFactory._sources.copy()

        try:
            EPGSourceFactory.register_source('test_source', MockEPGSource)

            sources = EPGSourceFactory.get_available_sources()
            assert 'test_source' in sources

            # Test that we can create the registered source
            config = {'name': 'Test', 'base_url': 'https://test.com'}
            source = EPGSourceFactory.create_source('test_source', config)
            assert isinstance(source, MockEPGSource)

        finally:
            # Restore original sources
            EPGSourceFactory._sources = original_sources

    def test_create_source_unknown_type(self):
        """Test create_source with unknown source type."""
        config = {'name': 'Test', 'base_url': 'https://test.com'}

        with pytest.raises(ConfigError) as exc_info:
            EPGSourceFactory.create_source('unknown_source', config)

        assert "Unknown EPG source 'unknown_source'" in str(exc_info.value)
        assert "Available sources:" in str(exc_info.value)

    def test_create_source_valid_config(self):
        """Test create_source with valid configuration."""
        config = {'name': 'Centrum', 'base_url': 'https://api.centrum.cz'}

        result = EPGSourceFactory.create_source('centrum_cz', config)

        # Should return an instance of the source
        assert result is not None
        assert hasattr(result, 'validate_config')
        assert hasattr(result, 'fetch_channels')
        assert hasattr(result, 'fetch_programmes')

    def test_create_source_invalid_config(self):
        """Test create_source with invalid configuration."""
        config = {'name': 'Centrum'}  # Missing base_url

        with pytest.raises(ConfigError) as exc_info:
            EPGSourceFactory.create_source('centrum_cz', config)

        assert "Invalid configuration for source 'centrum_cz'" in str(exc_info.value)

    def test_create_source_blesk_aliases(self):
        """Test create_source with different Blesk source aliases."""
        config = {'name': 'Blesk', 'base_url': 'https://api.blesk.cz'}

        # Test all Blesk aliases
        aliases = ['blesk', 'blesk.cz', 'blesk_cz']
        for alias in aliases:
            result = EPGSourceFactory.create_source(alias, config)
            assert result is not None
            assert hasattr(result, 'validate_config')
            assert hasattr(result, 'fetch_channels')
            assert hasattr(result, 'fetch_programmes')

    def test_create_source_centrum_aliases(self):
        """Test create_source with different Centrum source aliases."""
        config = {'name': 'Centrum', 'base_url': 'https://api.centrum.cz'}

        # Test all Centrum aliases
        aliases = ['centrum', 'centrum.cz', 'centrum_cz']
        for alias in aliases:
            result = EPGSourceFactory.create_source(alias, config)
            assert result is not None
            assert hasattr(result, 'validate_config')
            assert hasattr(result, 'fetch_channels')
            assert hasattr(result, 'fetch_programmes')


class TestGetSourceFunction:
    """Test cases for get_source convenience function."""

    @patch('epg_grabber.sources.EPGSourceFactory.create_source')
    def test_get_source_calls_factory(self, mock_create_source):
        """Test get_source calls EPGSourceFactory.create_source."""
        mock_source = Mock()
        mock_create_source.return_value = mock_source

        config = {'name': 'Test', 'base_url': 'https://test.com'}
        result = get_source('centrum_cz', config)

        mock_create_source.assert_called_once_with('centrum_cz', config)
        assert result == mock_source

    @patch('epg_grabber.sources.EPGSourceFactory.create_source')
    def test_get_source_propagates_exceptions(self, mock_create_source):
        """Test get_source propagates exceptions from factory."""
        mock_create_source.side_effect = ConfigError("Test error")

        config = {'name': 'Test', 'base_url': 'https://test.com'}

        with pytest.raises(ConfigError) as exc_info:
            get_source('invalid_source', config)

        assert "Test error" in str(exc_info.value)


class TestSourceRegistry:
    """Test cases for source registry functionality."""

    def test_source_registry_immutability(self):
        """Test that external modifications don't affect internal registry."""
        # Get sources list
        sources = EPGSourceFactory.get_available_sources()
        original_count = len(sources)

        # Modify the returned list
        sources.append('malicious_source')

        # Get sources again - should be unchanged
        new_sources = EPGSourceFactory.get_available_sources()
        assert len(new_sources) == original_count
        assert 'malicious_source' not in new_sources

    def test_source_registry_contains_expected_types(self):
        """Test that source registry contains expected source types."""
        sources = EPGSourceFactory.get_available_sources()

        # Should contain both Centrum and Blesk sources
        centrum_sources = [s for s in sources if 'centrum' in s]
        blesk_sources = [s for s in sources if 'blesk' in s]

        assert len(centrum_sources) >= 3  # centrum, centrum.cz, centrum_cz
        assert len(blesk_sources) >= 3    # blesk, blesk.cz, blesk_cz

    def test_source_registry_case_sensitivity(self):
        """Test that source registry is case sensitive."""
        config = {'name': 'Test', 'base_url': 'https://test.com'}

        # These should work
        valid_sources = ['centrum_cz', 'blesk_cz']
        for source in valid_sources:
            try:
                EPGSourceFactory.create_source(source, config)
            except ConfigError as e:
                # Config error is OK (invalid config), but not unknown source
                assert "Unknown EPG source" not in str(e)

        # These should fail (wrong case)
        invalid_sources = ['CENTRUM_CZ', 'Blesk_Cz', 'centrum_CZ']
        for source in invalid_sources:
            with pytest.raises(ConfigError) as exc_info:
                EPGSourceFactory.create_source(source, config)
            assert "Unknown EPG source" in str(exc_info.value)
