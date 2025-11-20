[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/robco)
# Czech TV EPG Grabber

Electronic Program Guide (EPG) data grabber in XMLTV format from (not only) Czech television sources. The library supports multiple EPG sources, including _Centrum.cz_ and _Blesk.cz_, is easily extensible by new EPG sources, and provides both programmatic and command-line interfaces with enhanced programme details including images, cast information, and detailed descriptions.

## Features

- 🎯 **Multi-source support** - Extensible architecture for multiple EPG sources (Centrum.cz, Blesk.cz)
- 📺 **XMLTV format** - Industry-standard EPG format compatible with Plex, Kodi, and other media centers
- 🖼️ **Enhanced programme data** - Programme images, cast information, detailed descriptions
- 🏷️ **Channel logos** - Exact logo URLs from EPG sources with category mapping
- 🇨🇿 **Czech language support** - Full UTF-8 encoding with proper Czech character handling
- ⚙️ **Flexible configuration** - Config file or constructor-based configuration
- 🔍 **Programme queries** - Query specific channel programming by time
- 📅 **Multi-day support** - Generate EPG data for multiple days ahead
- 🖥️ **CLI interface** - Command-line tool for easy automation
- 🐍 **Python API** - Clean programmatic interface for integration

## Installation

### From PyPI (when published)

```bash
pip install epg-grabber
```


### From Source

```bash
git clone https://github.com/robco/czech-tv-epg-grabber.git
cd czech-tv-epg-grabber
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Install from source
pip install -e .

# List full usage help
epg-grabber --help

# Generate EPG from default source (Centrum.cz)
epg-grabber

# Generate EPG from Blesk.cz with enhanced details
epg-grabber --source blesk_cz --output enhanced_epg.xml
```

### Python API Usage

```python
from czech_tv_epg import CzechTVEPGGenerator

# Basic usage
generator = CzechTVEPGGenerator()
output_file, stats = generator.generate_epg()

# Get current programme with details
current = generator.get_current_programme("1")
print(f"Now playing: {current['programme']['title']}")

```

## Available EPG sources

|   Source   |             Base URL             |                  Features                  |   API Type    |
| ---------- | -------------------------------- | ------------------------------------------ | ------------- |
| centrum_cz | https://tvprogram.centrum.cz     | Channel logos, basic programme info        | REST GET      |
| blesk_cz   | https://tvprogram.blesk.cz       | Enhanced details, images, cast, categories | REST POST/GET |

## Usage

### Command Line Interface

```bash
# List full usage help
epg-grabber --help

# List available EPG sources
epg-grabber --list-sources

# List channels with categories
epg-grabber --source blesk_cz --list-channels

# Get current programme with enhanced details
epg-grabber --source blesk_cz --current 62

# Get programme at specific time
epg-grabber --at-time 1 "2025-05-24 20:00"

# Generate EPG with programme images and cast info
epg-grabber --source blesk_cz --output enhanced_epg.xml --days 7

# Generate EPG but hide processing progress bar
epg-grabber --source blesk_cz --output enhanced_epg.xml --days 7 --silent
```

### Python API

```python
from epg_grabber import CzechTVEPGGenerator
from datetime import datetime

# Use Blesk.cz for enhanced programme details
generator = CzechTVEPGGenerator(
    source_type="blesk_cz",
    base_url="https://tvprogram.blesk.cz"
)

# Get programmes with images and cast info
tips = generator.get_programme_tips_with_images(
    date=datetime.now(),
    time_from="20:00:00",
    time_to="23:59:59"
)

for tip in tips:
    print(f"{tip['title']} - {tip['content_type']}")
    print(f"Image: {tip['image_url']}")
    
    # Get detailed cast and description
    details = generator.get_programme_details(tip['id'])
    if details:
        print(f"Cast: {[actor['name'] for actor in details['actors'][:3]]}")
```

## Configuration

### Using Configuration Files

### Centrum.cz config.json

```json
{
  "source": {
    "type": "centrum_cz",
    "base_url": "https://tvprogram.centrum.cz/api"
  },
  "epg": {
    "days_ahead": 5,
    "timezone": "+0200"
  },
  "output": {
    "path": "./epg_output",
    "filename": "tvguide.xml"
  }
}
```

### Blesk.cz config.json

```json
{
  "source": {
    "type": "blesk_cz",
    "base_url": "https://tvprogram.blesk.cz"
  },
  "epg": {
    "days_ahead": 7,
    "timezone": "+0200"
  },
  "output": {
    "filename": "enhanced_epg.xml"
  }
}
```

### Constructor based configuration

```python
generator = CzechTVEPGGenerator(
    source_type="blesk_cz",
    base_url="https://tvprogram.blesk.cz",
    days_ahead=7,
    channels=["62", "63", "64"],
    output_filename="my_epg.xml"
)
```

### Using Constructor Parameters

```python
from epg_grabber import CzechTVEPGGenerator

generator = CzechTVEPGGenerator(
              source_type="centrum_cz",
              base_url="https://tvprogram.centrum.cz/api",
              output_path="./epg_files",
              output_filename="my_epg.xml",
              days_ahead=7,
              channels=,
              log_level="DEBUG"
)
```

## Enhanced XMLTV Output

The generated XMLTV includes:
* Programme images as <icon> tags
* Cast information in <credits> sections
* Content types as sub-titles (Film, Seriál, etc.)
* Enhanced descriptions from detailed API calls
* Episode information when available

```xml
<programme start="20250526200000 +0200" stop="20250526213000 +0200" channel="ch_62">
  <title lang="cs">Hrabě Monte Christo (3/4)</title>
  <sub-title lang="cs">Seriál</sub-title>
  <desc lang="cs">Jeden z nejkrásnějších příběhů všech dob...</desc>
  <icon src="https://ms2.ostium.cz/instance/tv-program/jm9Vdzuj/h230w170t.jpg"/>
  <credits>
    <actor>Jacques Weber</actor>
    <actor>Carla Romanelli</actor>
  </credits>
</programme>
```
## Usage examples

### Grab EPG and store as XMLTV file

```bash
# Generate enhanced EPG for Plex
epg-grabber --source blesk_cz --output /path/to/plex/tvguide.xml --days 7
```

### Grab EPG and show progress

```bash
epg-grabber --days 6

Fetching 6 days of programmes: 100%|███████| 864/864 [00:28<00:00, 30.45items/s]
Creating XMLTV programmes:   1%|       | 163/25008 [00:29<1:15:13,  5.50items/s]
```

### Automated updates

```bash
# Daily EPG updates via cron
0 6 * * * /usr/local/bin/epg-grabber --source blesk_cz --output /var/epg/tvguide.xml --days 7
```

## Development

### Adding new EPG sources

```python
from epg_grabber.base import EPGSource, Channel, Programme
from epg_grabber.sources import EPGSourceFactory

class MyEPGSource(EPGSource):
    def fetch_channels(self):
        # Implement channel fetching
        pass
    
    def fetch_programmes(self, date, channel_ids):
        # Implement programme fetching
        pass
    
    def get_channel_logo_url(self, channel_id):
        # Implement logo URL generation
        pass

# Register the new source
EPGSourceFactory.register_source('mysource', MyEPGSource)
```

### Error handling

```python
from epg_grabber import CzechTVEPGGenerator
from epg_grabber.exceptions import EPGError, ConfigError, APIError

try:
    generator = CzechTVEPGGenerator(source_type="blesk_cz")
    result = generator.get_current_programme("62")
except ConfigError as e:
    print(f"Configuration error: {e}")
except APIError as e:
    print(f"API error: {e}")
except EPGError as e:
    print(f"EPG error: {e}")
```

## Testing

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=epg_grabber --cov-report=term-missing

# Run specific test file
pytest tests/test_base.py -v

# Run tests with coverage report
pytest --cov=epg_grabber --cov-report=html
```
