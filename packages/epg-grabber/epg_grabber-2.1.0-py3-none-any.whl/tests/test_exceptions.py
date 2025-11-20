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
Tests for the exceptions module.
"""

import pytest
from epg_grabber.exceptions import EPGError, ConfigError, APIError


class TestEPGError:
    """Test cases for EPGError exception."""

    def test_epg_error_creation(self):
        """Test EPGError can be created with a message."""
        error = EPGError("Test error message")
        assert str(error) == "Test error message"

    def test_epg_error_inheritance(self):
        """Test EPGError inherits from Exception."""
        error = EPGError("Test error")
        assert isinstance(error, Exception)

    def test_epg_error_raise(self):
        """Test EPGError can be raised and caught."""
        with pytest.raises(EPGError) as exc_info:
            raise EPGError("Test error")
        assert str(exc_info.value) == "Test error"


class TestConfigError:
    """Test cases for ConfigError exception."""

    def test_config_error_creation(self):
        """Test ConfigError can be created with a message."""
        error = ConfigError("Configuration error")
        assert str(error) == "Configuration error"

    def test_config_error_inheritance(self):
        """Test ConfigError inherits from EPGError."""
        error = ConfigError("Config error")
        assert isinstance(error, EPGError)
        assert isinstance(error, Exception)

    def test_config_error_raise(self):
        """Test ConfigError can be raised and caught."""
        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Invalid configuration")
        assert str(exc_info.value) == "Invalid configuration"

    def test_config_error_caught_as_epg_error(self):
        """Test ConfigError can be caught as EPGError."""
        with pytest.raises(EPGError):
            raise ConfigError("Config error")


class TestAPIError:
    """Test cases for APIError exception."""

    def test_api_error_creation(self):
        """Test APIError can be created with a message."""
        error = APIError("API request failed")
        assert str(error) == "API request failed"

    def test_api_error_inheritance(self):
        """Test APIError inherits from EPGError."""
        error = APIError("API error")
        assert isinstance(error, EPGError)
        assert isinstance(error, Exception)

    def test_api_error_raise(self):
        """Test APIError can be raised and caught."""
        with pytest.raises(APIError) as exc_info:
            raise APIError("HTTP 500 error")
        assert str(exc_info.value) == "HTTP 500 error"

    def test_api_error_caught_as_epg_error(self):
        """Test APIError can be caught as EPGError."""
        with pytest.raises(EPGError):
            raise APIError("API error")


class TestExceptionHierarchy:
    """Test cases for exception hierarchy."""

    def test_all_exceptions_caught_as_epg_error(self):
        """Test all custom exceptions can be caught as EPGError."""
        exceptions = [
            EPGError("Base error"),
            ConfigError("Config error"),
            APIError("API error")
        ]

        for exception in exceptions:
            with pytest.raises(EPGError):
                raise exception

    def test_exception_messages_preserved(self):
        """Test exception messages are preserved through inheritance."""
        messages = [
            "Base EPG error",
            "Configuration is invalid",
            "API endpoint not found"
        ]

        exceptions = [
            EPGError(messages[0]),
            ConfigError(messages[1]),
            APIError(messages[2])
        ]

        for i, exception in enumerate(exceptions):
            assert str(exception) == messages[i]
