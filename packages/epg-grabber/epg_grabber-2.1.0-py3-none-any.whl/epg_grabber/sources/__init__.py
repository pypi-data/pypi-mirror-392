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
EPG source factory and registry.
"""

from typing import Dict, Type, List
from ..base import EPGSource
from ..exceptions import ConfigError
from .centrum_cz import CentrumCzEPGSource
from .blesk_cz import BleskCzEPGSource


class EPGSourceFactory:
    """Factory for creating EPG source instances."""

    _sources: Dict[str, Type[EPGSource]] = {
        'centrum': CentrumCzEPGSource,
        'centrum.cz': CentrumCzEPGSource,
        'centrum_cz': CentrumCzEPGSource,
        'blesk': BleskCzEPGSource,
        'blesk.cz': BleskCzEPGSource,
        'blesk_cz': BleskCzEPGSource,
    }

    @classmethod
    def register_source(cls, name: str, source_class: Type[EPGSource]):
        """Register a new EPG source."""
        cls._sources[name] = source_class

    @classmethod
    def create_source(cls, source_type: str, config: Dict) -> EPGSource:
        """Create an EPG source instance."""
        if source_type not in cls._sources:
            available = ', '.join(cls._sources.keys())
            raise ConfigError(f"Unknown EPG source '{source_type}'. Available sources: {available}")

        source_class = cls._sources[source_type]
        source = source_class(config)

        if not source.validate_config():
            raise ConfigError(f"Invalid configuration for source '{source_type}'")

        return source

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """Get list of available source types."""
        return list(cls._sources.keys())


def get_source(source_type: str, config: Dict) -> EPGSource:
    """Convenience function to create EPG source."""
    return EPGSourceFactory.create_source(source_type, config)
