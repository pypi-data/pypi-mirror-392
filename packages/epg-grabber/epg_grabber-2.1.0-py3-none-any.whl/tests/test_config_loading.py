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
Tests for configuration loading functionality.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch
from pathlib import Path
from epg_grabber.generator import CzechTVEPGGenerator
from epg_grabber.exceptions import ConfigError


class TestConfigurationLoading:
    """Test cases for configuration file loading."""

    def test_load_config_from_file(self):
        """Test loading configuration from a JSON file."""
        # Create a temporary config file
        config_data = {
            "source": {
                "type": "centrum_cz",
                "name": "Test Source",
                "base_url": "https://test.api.com"
            },
            "epg": {
                "days_ahead": 7,
                "timezone": "+0100"
            },
            "output": {
                "filename": "test.xml"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch('epg_grabber.generator.EPGSourceFactory.create_source'):
                generator = CzechTVEPGGenerator(config_file=config_file)

                # Check that config was loaded correctly
                assert generator.config['source']['name'] == 'Test Source'
                assert generator.config['epg']['days_ahead'] == 7
                assert generator.config['epg']['timezone'] == '+0100'
                assert generator.config['output']['filename'] == 'test.xml'
        finally:
            os.unlink(config_file)

    def test_load_config_nonexistent_file(self):
        """Test behavior when config file doesn't exist."""
        with patch('epg_grabber.generator.EPGSourceFactory.create_source'):
            # Should use defaults when file doesn't exist
            generator = CzechTVEPGGenerator(config_file="/nonexistent/config.json")

            # Should have default configuration
            assert generator.config is not None
            assert 'source' in generator.config
            assert 'epg' in generator.config

    def test_constructor_overrides_config_file(self):
        """Test that constructor parameters override config file values."""
        config_data = {
            "source": {
                "type": "centrum_cz",
                "name": "File Source",
                "base_url": "https://file.api.com"
            },
            "epg": {
                "days_ahead": 3,
                "timezone": "+0200"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch('epg_grabber.generator.EPGSourceFactory.create_source'):
                generator = CzechTVEPGGenerator(
                    config_file=config_file,
                    source_name="Constructor Source",
                    days_ahead=10,
                    timezone="+0100"
                )

                # Constructor parameters should override file values
                assert generator.config['source']['name'] == 'Constructor Source'
                assert generator.config['epg']['days_ahead'] == 10
                assert generator.config['epg']['timezone'] == '+0100'

                # Non-overridden values should come from file
                assert generator.config['source']['base_url'] == 'https://file.api.com'
        finally:
            os.unlink(config_file)

    def test_load_test_config_file(self):
        """Test loading the test configuration file."""
        test_config_path = Path(__file__).parent / "test_config.json"

        with patch('epg_grabber.generator.EPGSourceFactory.create_source'):
            generator = CzechTVEPGGenerator(config_file=str(test_config_path))

            # Check that test config was loaded
            assert generator.config['source']['name'] == 'Test Centrum Source'
            assert generator.config['epg']['days_ahead'] == 3
            assert generator.config['output']['filename'] == 'test_tvguide.xml'
            assert 'ct1' in generator.config['channels']

    def test_invalid_json_config_file(self):
        """Test behavior with invalid JSON config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            config_file = f.name

        try:
            with patch('epg_grabber.generator.EPGSourceFactory.create_source'):
                # Should raise ConfigError for invalid JSON
                with pytest.raises(ConfigError) as exc_info:
                    CzechTVEPGGenerator(config_file=config_file)

                assert "Invalid JSON in config file" in str(exc_info.value)
        finally:
            os.unlink(config_file)

    def test_config_file_with_missing_sections(self):
        """Test config file with missing sections."""
        config_data = {
            "source": {
                "type": "centrum_cz",
                "name": "Partial Source",
                "base_url": "https://test.api.com"
            }
            # Missing epg, output sections
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch('epg_grabber.generator.EPGSourceFactory.create_source'):
                generator = CzechTVEPGGenerator(config_file=config_file)

                # Config file is loaded as-is without merging defaults
                assert generator.config['source']['name'] == 'Partial Source'
                # Missing sections won't be automatically added
                assert generator.config == config_data
        finally:
            os.unlink(config_file)


class TestConfigurationValidation:
    """Test cases for configuration validation."""

    def test_source_type_validation(self):
        """Test validation of source type configuration."""
        with patch('epg_grabber.generator.EPGSourceFactory.create_source') as mock_factory:
            mock_factory.side_effect = ConfigError("Invalid source type")

            with pytest.raises(ConfigError) as exc_info:
                CzechTVEPGGenerator(source_type="invalid_source")

            assert "Failed to create EPG source" in str(exc_info.value)

    def test_source_config_validation(self):
        """Test validation of source configuration."""
        with patch('epg_grabber.generator.EPGSourceFactory.create_source') as mock_factory:
            mock_factory.side_effect = ConfigError("Invalid configuration")

            with pytest.raises(ConfigError):
                CzechTVEPGGenerator(
                    source_type="centrum_cz",
                    base_url=""  # Invalid empty base_url
                )

    def test_valid_configuration(self):
        """Test that valid configuration doesn't raise errors."""
        with patch('epg_grabber.generator.EPGSourceFactory.create_source'):
            # Should not raise any exceptions
            generator = CzechTVEPGGenerator(
                source_type="centrum_cz",
                source_name="Valid Source",
                base_url="https://valid.api.com",
                days_ahead=5,
                timezone="+0200"
            )

            assert generator.config is not None
            assert generator.source is not None
