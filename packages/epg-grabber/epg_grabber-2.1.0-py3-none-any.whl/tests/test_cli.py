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
Comprehensive tests for the CLI module.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from io import StringIO

from epg_grabber.cli import main
from epg_grabber.exceptions import EPGError


class TestCLIArgumentParsing:
    """Test argument parsing functionality."""

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_default_arguments(self, mock_generator):
        """Test CLI with default arguments."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber']):
            main()

        mock_generator.assert_called_once_with('config.json', None, None)
        mock_instance.generate_epg.assert_called_once()

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_config_argument(self, mock_generator):
        """Test CLI with custom config file."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '--config', 'custom.json']):
            main()

        mock_generator.assert_called_once_with('custom.json', None, None)

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_output_argument(self, mock_generator):
        """Test CLI with custom output file."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('custom.xml', {
            'source': 'test',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '--output', 'custom.xml']):
            main()

        mock_generator.assert_called_once_with('config.json', 'custom.xml', None)

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_source_argument(self, mock_generator):
        """Test CLI with custom source."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'blesk',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '--source', 'blesk']):
            main()

        mock_generator.assert_called_once_with('config.json', None, 'blesk')

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_days_argument(self, mock_generator):
        """Test CLI with custom days ahead."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.config = {'epg': {}}
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '--days', '5']):
            main()

        assert mock_instance.config['epg']['days_ahead'] == 5

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_verbose_argument(self, mock_generator):
        """Test CLI with verbose logging."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.config = {'logging': {}}
        mock_instance._setup_logging = Mock()
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '--verbose']):
            main()

        assert mock_instance.config['logging']['level'] == 'DEBUG'
        mock_instance._setup_logging.assert_called_once()

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_silent_argument(self, mock_generator):
        """Test CLI with silent mode (no progress bar)."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.enable_progress_bar = Mock()
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '--silent']):
            main()

        # Progress bar should not be enabled in silent mode
        mock_instance.enable_progress_bar.assert_not_called()

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_progress_bar_enabled_by_default(self, mock_generator):
        """Test that progress bar is enabled by default."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.enable_progress_bar = Mock()
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test',
            'channels': 10,
            'programs': 100,
            'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber']):
            main()

        mock_instance.enable_progress_bar.assert_called_once()


class TestCLIListSources:
    """Test list sources functionality."""

    @patch('epg_grabber.cli.EPGSourceFactory')
    def test_list_sources(self, mock_factory):
        """Test listing available sources."""
        mock_factory.get_available_sources.return_value = ['centrum', 'blesk', 'test']

        with patch('sys.argv', ['epg-grabber', '--list-sources']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Available EPG sources:" in output
        assert "centrum" in output
        assert "blesk" in output
        assert "test" in output


class TestCLIListChannels:
    """Test list channels functionality."""

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_list_channels_table_format(self, mock_generator):
        """Test listing channels in table format."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.fetch_and_list_channels = Mock()

        with patch('sys.argv', ['epg-grabber', '--list-channels']):
            main()

        mock_instance.fetch_and_list_channels.assert_called_once_with('table')

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_list_channels_json_format(self, mock_generator):
        """Test listing channels in JSON format."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.fetch_and_list_channels = Mock()

        with patch('sys.argv', ['epg-grabber', '--list-channels', '--format', 'json']):
            main()

        mock_instance.fetch_and_list_channels.assert_called_once_with('json')

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_list_channels_csv_format(self, mock_generator):
        """Test listing channels in CSV format."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.fetch_and_list_channels = Mock()

        with patch('sys.argv', ['epg-grabber', '--list-channels', '--format', 'csv']):
            main()

        mock_instance.fetch_and_list_channels.assert_called_once_with('csv')


class TestCLIProgrammeQueries:
    """Test programme query functionality."""

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_current_programme_found(self, mock_generator):
        """Test getting current programme when found."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_current_programme.return_value = {
            'channel': {'name': 'Test Channel', 'id': 'test'},
            'programme': {
                'title': 'Test Programme',
                'start_datetime': datetime(2025, 1, 1, 20, 0),
                'stop_datetime': datetime(2025, 1, 1, 21, 0),
                'duration_minutes': 60,
                'description': 'Test description',
                'category': 'Entertainment'
            },
            'time_into_programme_minutes': 15
        }

        with patch('sys.argv', ['epg-grabber', '--current', 'test']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Current programme on Test Channel" in output
        assert "Test Programme" in output
        assert "20:00 - 21:00" in output
        assert "60 minutes" in output
        assert "15 minutes" in output
        assert "Test description" in output
        assert "Entertainment" in output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_current_programme_not_found(self, mock_generator):
        """Test getting current programme when not found."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_current_programme.return_value = None

        with patch('sys.argv', ['epg-grabber', '--current', 'test']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "No programme found for channel test" in output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_programme_at_time_found(self, mock_generator):
        """Test getting programme at specific time when found."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programme_at_time.return_value = {
            'channel': {'name': 'Test Channel', 'id': 'test'},
            'programme': {
                'title': 'Test Programme',
                'start_datetime': datetime(2025, 1, 1, 20, 0),
                'stop_datetime': datetime(2025, 1, 1, 21, 0),
                'duration_minutes': 60,
                'description': 'Test description',
                'category': 'Entertainment'
            }
        }

        with patch('sys.argv', ['epg-grabber', '--at-time', 'test', '2025-01-01 20:30']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Programme on Test Channel at 2025-01-01 20:30" in output
        assert "Test Programme" in output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_programme_at_time_not_found(self, mock_generator):
        """Test getting programme at specific time when not found."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programme_at_time.return_value = None

        with patch('sys.argv', ['epg-grabber', '--at-time', 'test', '2025-01-01 20:30']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "No programme found for channel test at" in output

    def test_programme_at_time_invalid_format(self):
        """Test getting programme at time with invalid datetime format."""
        with patch('sys.argv', ['epg-grabber', '--at-time', 'test', 'invalid-date']):
            with patch('sys.stderr', new=StringIO()) as fake_err:
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 1
        error_output = fake_err.getvalue()
        assert "Invalid datetime format" in error_output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_day_schedule_found(self, mock_generator):
        """Test getting day schedule when programmes found."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programmes_for_day.return_value = [
            {
                'channel': {'name': 'Test Channel'},
                'programme': {
                    'title': 'Programme 1',
                    'start_datetime': datetime(2025, 1, 1, 20, 0),
                    'stop_datetime': datetime(2025, 1, 1, 21, 0),
                    'category': 'News'
                }
            },
            {
                'channel': {'name': 'Test Channel'},
                'programme': {
                    'title': 'Programme 2',
                    'start_datetime': datetime(2025, 1, 1, 21, 0),
                    'stop_datetime': datetime(2025, 1, 1, 22, 0),
                    'category': None
                }
            }
        ]

        with patch('sys.argv', ['epg-grabber', '--day-schedule', 'test']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Schedule for Test Channel" in output
        assert "Programme 1" in output
        assert "Programme 2" in output
        assert "20:00 - 21:00" in output
        assert "21:00 - 22:00" in output
        assert "[News]" in output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_day_schedule_not_found(self, mock_generator):
        """Test getting day schedule when no programmes found."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programmes_for_day.return_value = []

        with patch('sys.argv', ['epg-grabber', '--day-schedule', 'test']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "No programmes found for channel test" in output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_day_schedule_with_custom_date(self, mock_generator):
        """Test getting day schedule with custom date."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programmes_for_day.return_value = []

        with patch('sys.argv', ['epg-grabber', '--day-schedule', 'test', '--date', '2025-01-15']):
            main()

        # Verify the date was parsed and passed correctly
        call_args = mock_instance.get_programmes_for_day.call_args
        assert call_args[0][0] == 'test'  # channel_id
        assert call_args[0][1].date() == datetime(2025, 1, 15).date()

    def test_invalid_date_format(self):
        """Test CLI with invalid date format."""
        with patch('sys.argv', ['epg-grabber', '--day-schedule', 'test', '--date', 'invalid-date']):
            with patch('sys.stderr', new=StringIO()) as fake_err:
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 1
        error_output = fake_err.getvalue()
        assert "Invalid date format" in error_output


class TestCLIProgrammeTips:
    """Test programme tips functionality (Blesk-specific)."""

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_programme_tips(self, mock_generator):
        """Test getting programme tips."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programme_tips_with_images.return_value = [
            {
                'title': 'Test Programme',
                'content_type': 'Movie',
                'station_id': 'test_station',
                'start_datetime': '2025-01-01T20:00:00',
                'image_url': 'http://example.com/image.jpg'
            }
        ]

        with patch('sys.argv', ['epg-grabber', '--programme-tips']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Test Programme (Movie)" in output
        assert "Station: test_station" in output
        assert "Time: 2025-01-01T20:00:00" in output
        assert "Image: http://example.com/image.jpg" in output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_programme_tips_with_time_range(self, mock_generator):
        """Test getting programme tips with custom time range."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programme_tips_with_images.return_value = []

        with patch('sys.argv', ['epg-grabber', '--programme-tips', '--time-from', '18:00:00', '--time-to', '22:00:00']):
            main()

        # Verify the time range was passed correctly
        call_args = mock_instance.get_programme_tips_with_images.call_args
        assert call_args[0][1] == '18:00:00'  # time_from
        assert call_args[0][2] == '22:00:00'  # time_to

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_programme_details(self, mock_generator):
        """Test getting programme details."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programme_details.return_value = {
            'title': 'Test Programme',
            'description': 'Test description',
            'actors': [{'name': 'Actor 1'}, {'name': 'Actor 2'}],
            'gallery_images': ['img1.jpg', 'img2.jpg']
        }

        with patch('sys.argv', ['epg-grabber', '--programme-details', 'test_id']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Title: Test Programme" in output
        assert "Description: Test description" in output
        assert "Cast: Actor 1, Actor 2" in output
        assert "Images: 2 gallery images" in output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_programme_details_not_found(self, mock_generator):
        """Test getting programme details when not found."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.get_programme_details.return_value = None

        with patch('sys.argv', ['epg-grabber', '--programme-details', 'test_id']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "No details found for programme test_id" in output


class TestCLIErrorHandling:
    """Test error handling in CLI."""

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_epg_error_handling(self, mock_generator):
        """Test handling of EPGError exceptions."""
        mock_generator.side_effect = EPGError("Test EPG error")

        with patch('sys.argv', ['epg-grabber']):
            with patch('sys.stderr', new=StringIO()) as fake_err:
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 1
        error_output = fake_err.getvalue()
        assert "EPG Error: Test EPG error" in error_output

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    @patch('epg_grabber.cli.logging')
    def test_unexpected_error_handling(self, mock_logging, mock_generator):
        """Test handling of unexpected exceptions."""
        mock_generator.side_effect = ValueError("Unexpected error")

        with patch('sys.argv', ['epg-grabber']):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
        mock_logging.error.assert_called_once()

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_epg_generation_error(self, mock_generator):
        """Test error during EPG generation."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.side_effect = EPGError("Generation failed")

        with patch('sys.argv', ['epg-grabber']):
            with patch('sys.stderr', new=StringIO()) as fake_err:
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 1
        error_output = fake_err.getvalue()
        assert "EPG Error: Generation failed" in error_output


class TestCLISuccessOutput:
    """Test successful EPG generation output."""

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_successful_epg_generation_output(self, mock_generator):
        """Test output for successful EPG generation."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'centrum',
            'channels': 25,
            'programs': 1500,
            'date_range': '2025-01-01 to 2025-01-03'
        })

        with patch('sys.argv', ['epg-grabber']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "EPG generated successfully!" in output
        assert "Source: centrum" in output
        assert "Output file: output.xml" in output
        assert "Channels: 25" in output
        assert "Programs: 1500" in output
        assert "Date range: 2025-01-01 to 2025-01-03" in output


class TestCLIShortOptions:
    """Test CLI short option aliases."""

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_short_config_option(self, mock_generator):
        """Test -c short option for config."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test', 'channels': 10, 'programs': 100, 'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '-c', 'custom.json']):
            main()

        mock_generator.assert_called_once_with('custom.json', None, None)

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_short_output_option(self, mock_generator):
        """Test -o short option for output."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('custom.xml', {
            'source': 'test', 'channels': 10, 'programs': 100, 'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '-o', 'custom.xml']):
            main()

        mock_generator.assert_called_once_with('config.json', 'custom.xml', None)

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_short_source_option(self, mock_generator):
        """Test -s short option for source."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'blesk', 'channels': 10, 'programs': 100, 'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '-s', 'blesk']):
            main()

        mock_generator.assert_called_once_with('config.json', None, 'blesk')

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_short_days_option(self, mock_generator):
        """Test -d short option for days."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.config = {'epg': {}}
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test', 'channels': 10, 'programs': 100, 'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '-d', '7']):
            main()

        assert mock_instance.config['epg']['days_ahead'] == 7

    @patch('epg_grabber.cli.CzechTVEPGGenerator')
    def test_short_verbose_option(self, mock_generator):
        """Test -v short option for verbose."""
        mock_instance = Mock()
        mock_generator.return_value = mock_instance
        mock_instance.config = {'logging': {}}
        mock_instance._setup_logging = Mock()
        mock_instance.generate_epg.return_value = ('output.xml', {
            'source': 'test', 'channels': 10, 'programs': 100, 'date_range': '2025-01-01 to 2025-01-02'
        })

        with patch('sys.argv', ['epg-grabber', '-v']):
            main()

        assert mock_instance.config['logging']['level'] == 'DEBUG'
        mock_instance._setup_logging.assert_called_once()
