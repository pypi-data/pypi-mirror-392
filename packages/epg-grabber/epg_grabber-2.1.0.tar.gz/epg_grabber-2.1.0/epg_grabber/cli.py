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
Command line interface for the Czech TV EPG generator.
"""

import argparse
import sys
import logging
from datetime import datetime

from .generator import CzechTVEPGGenerator
from .sources import EPGSourceFactory
from .exceptions import EPGError


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description='Generate Czech TV EPG in XMLTV format')
    parser.add_argument('--config', '-c', default='config.json', help='Configuration file path')
    parser.add_argument('--output', '-o', help='Output file path (overrides config)')
    parser.add_argument('--source', '-s', help='EPG source type (overrides config)')
    parser.add_argument('--days', '-d', type=int, help='Days ahead to fetch (overrides config)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--silent', action='store_true', help='Hide progress bar during data fetching')

    # Channel listing
    parser.add_argument('--list-channels', action='store_true', help='List all available channels')
    parser.add_argument('--list-sources', action='store_true', help='List all available EPG sources')
    parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table',
                        help='Output format for channel listing')

    # Programme queries
    parser.add_argument('--current', metavar='CHANNEL_ID', help='Get current programme for channel')
    parser.add_argument('--at-time', nargs=2, metavar=('CHANNEL_ID', 'DATETIME'),
                        help='Get programme at specific time (format: YYYY-MM-DD HH:MM)')
    parser.add_argument('--day-schedule', metavar='CHANNEL_ID', help='Get full day schedule for channel')
    parser.add_argument('--date', help='Date for queries (format: YYYY-MM-DD, default: today)')

    # Programme tips (Blesk.cz only)
    parser.add_argument('--programme-tips', action='store_true',
                        help='Get programme tips with images (Blesk.cz only)')
    parser.add_argument('--programme-details', metavar='PROGRAMME_ID',
                        help='Get detailed programme information (Blesk.cz only)')
    parser.add_argument('--time-from', default='00:00:00',
                        help='Start time for programme tips (HH:MM:SS)')
    parser.add_argument('--time-to', default='23:59:59',
                        help='End time for programme tips (HH:MM:SS)')

    args = parser.parse_args()

    try:
        if args.list_sources:
            sources = EPGSourceFactory.get_available_sources()
            print("Available EPG sources:")
            for source in sources:
                print(f"  - {source}")
            return

        generator = CzechTVEPGGenerator(args.config, args.output, args.source)

        # Set progress bar option
        if not args.silent:
            generator.enable_progress_bar()

        if args.days is not None:
            generator.config['epg']['days_ahead'] = args.days
        if args.verbose:
            generator.config['logging']['level'] = 'DEBUG'
            generator._setup_logging()

        if args.list_channels:
            generator.fetch_and_list_channels(args.format)
            return

        # Parse date if provided
        query_date = None
        if args.date:
            try:
                query_date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                print(f"Invalid date format: {args.date}. Use YYYY-MM-DD", file=sys.stderr)
                sys.exit(1)

        # Handle programme queries
        if args.current:
            result = generator.get_current_programme(args.current)
            if result:
                print(f"Current programme on {result['channel']['name']} (ID: {result['channel']['id']}):")
                print(f"  Title: {result['programme']['title']}")
                print(f"  Time: {result['programme']['start_datetime'].strftime('%H:%M')} - {result['programme']['stop_datetime'].strftime('%H:%M')}")
                print(f"  Duration: {result['programme']['duration_minutes']} minutes")
                print(f"  Time into programme: {result['time_into_programme_minutes']} minutes")
                if result['programme']['description']:
                    print(f"  Description: {result['programme']['description']}")
                if result['programme']['category']:
                    print(f"  Category: {result['programme']['category']}")
            else:
                print(f"No programme found for channel {args.current}")
            return

        if args.at_time:
            channel_id, time_str = args.at_time
            try:
                target_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                # Make it timezone-aware using CEST
                from datetime import timezone, timedelta
                cest = timezone(timedelta(hours=2))
                target_time = target_time.replace(tzinfo=cest)
            except ValueError:
                print(f"Invalid datetime format: {time_str}. Use YYYY-MM-DD HH:MM", file=sys.stderr)
                sys.exit(1)

            result = generator.get_programme_at_time(channel_id, target_time)
            if result:
                print(f"Programme on {result['channel']['name']} at {target_time.strftime('%Y-%m-%d %H:%M %Z')}:")
                print(f"  Title: {result['programme']['title']}")
                print(f"  Time: {result['programme']['start_datetime'].strftime('%H:%M')} - {result['programme']['stop_datetime'].strftime('%H:%M')}")
                print(f"  Duration: {result['programme']['duration_minutes']} minutes")
                if result['programme']['description']:
                    print(f"  Description: {result['programme']['description']}")
                if result['programme']['category']:
                    print(f"  Category: {result['programme']['category']}")
            else:
                print(f"No programme found for channel {channel_id} at {target_time}")
            return

        if args.day_schedule:
            date_to_use = query_date or datetime.now()
            programmes = generator.get_programmes_for_day(args.day_schedule, date_to_use)
            if programmes:
                channel_name = programmes[0]['channel']['name']
                print(f"Schedule for {channel_name} on {date_to_use.strftime('%Y-%m-%d')}:")
                print("-" * 60)
                for prog in programmes:
                    start_time = prog['programme']['start_datetime'].strftime('%H:%M')
                    stop_time = prog['programme']['stop_datetime'].strftime('%H:%M')
                    print(f"{start_time} - {stop_time}  {prog['programme']['title']}")
                    if prog['programme']['category']:
                        print(f"                    [{prog['programme']['category']}]")
            else:
                print(f"No programmes found for channel {args.day_schedule} on {date_to_use.strftime('%Y-%m-%d')}")
            return

        if args.programme_tips:
            query_date = query_date or datetime.now()
            tips = generator.get_programme_tips_with_images(
                query_date, args.time_from, args.time_to
            )
            for tip in tips:
                print(f"{tip['title']} ({tip['content_type']})")
                print(f"  Station: {tip['station_id']}")
                print(f"  Time: {tip['start_datetime']}")
                print(f"  Image: {tip['image_url']}")
            return

        if args.programme_details:
            details = generator.get_programme_details(args.programme_details)
            if details:
                print(f"Title: {details['title']}")
                print(f"Description: {details['description']}")
                print(f"Cast: {', '.join([actor['name'] for actor in details['actors']])}")
                print(f"Images: {len(details['gallery_images'])} gallery images")
            else:
                print(f"No details found for programme {args.programme_details}")
            return

        # Default: generate EPG
        output_file, stats = generator.generate_epg()

        print("EPG generated successfully!")
        print(f"Source: {stats['source']}")
        print(f"Output file: {output_file}")
        print(f"Channels: {stats['channels']}")
        print(f"Programs: {stats['programs']}")
        print(f"Date range: {stats['date_range']}")

    except EPGError as e:
        print(f"EPG Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
