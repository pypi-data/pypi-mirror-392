#!/usr/bin/env python3
"""
Date handler orchestrator for Tinybeans downloads
"""
import logging
import os
from datetime import datetime, timedelta
import click
from click_help_colors import HelpColorsCommand
from tinybeans_sync.downloader import TinybeansDownloader

logger = logging.getLogger(__name__)

def setup_logging(config, data_dir, daemon=False):
    """Configure console and optional file logging."""
    logging_config = (config or {}).get('logging', {})
    level_name = str(logging_config.get('level', 'INFO')).upper()
    level = getattr(logging, level_name, logging.INFO)

    console_format = "%(asctime)s %(levelname)s %(name)s: %(message)s" if daemon else "%(message)s"
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(console_format))

    logging.basicConfig(level=level, handlers=[console_handler], force=True)

    log_setting = logging_config.get('file')
    if log_setting is None:
        log_setting = os.path.join(data_dir, 'logs', 'tinybeans-sync.log')

    if log_setting:
        log_path = os.path.expanduser(log_setting)
        if not os.path.isabs(log_path):
            log_path = os.path.join(data_dir, log_path)
        log_dir = os.path.dirname(log_path)
        try:
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            logging.getLogger().addHandler(file_handler)
        except OSError as exc:
            logger.warning("Unable to write log file %s: %s", log_path, exc)

class DateHandler:
    def __init__(self, config_path, data_dir):
        self.downloader = TinybeansDownloader(config_path, data_dir)
        self.config = self.downloader.config
        # Use the same history instance as the downloader
        self.history = self.downloader.history

    def download_single_month(self, year, month):
        """Download all images for a single month"""
        logger.info("Processing %04d-%02d", year, month)
        return self.downloader.download_month(year, month)

    def download_date_range(self, start_date, end_date):
        """Download images for a date range (by months)"""
        logger.info("Processing date range: %s to %s", start_date, end_date)

        current = start_date.replace(day=1)  # Start at beginning of month
        total_downloaded = 0

        while current <= end_date:
            year = current.year
            month = current.month

            logger.info("=" * 50)
            downloaded = self.download_single_month(year, month)
            total_downloaded += downloaded

            # Move to next month
            if month == 12:
                current = current.replace(year=year + 1, month=1)
            else:
                current = current.replace(month=month + 1)

        logger.info("Total downloaded across all months: %d", total_downloaded)
        return total_downloaded

    def get_from_last_date_range(self):
        """Get date range starting from last download timestamp"""
        latest = self.history.get_latest_timestamp()
        if latest is None:
            logger.info("No download history found, starting from config dates")
            return None

        # Start from the day after the last download
        start_date = (latest + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

        logger.info("Resuming from last download: %s", latest.strftime('%Y-%m-%d %H:%M:%S'))
        logger.info("New range: %s to %s", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        return start_date, end_date

    def parse_date(self, date_str):
        """Parse date string in various formats"""
        formats = ['%Y-%m-%d', '%Y-%m', '%Y/%m/%d', '%m/%d/%Y']

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date: {date_str}")

@click.command(
    cls=HelpColorsCommand,
    help_headers_color="cyan",
    help_options_color="green",
    context_settings={"help_option_names": ["-h", "--help"]}
)
@click.option('--data', default=None, help='data directory (XDG_CONFIG_HOME/tinybeans-sync)')
@click.option('--config', '-c', default=None, help='config file path (<data>/config.yaml)')
@click.option('--force', is_flag=True, help='ignore history and re-download everything')
@click.option('--from-last-date', is_flag=True, help='resume from last download')
@click.option('--after', metavar='DATE', help='download on/after DATE (e.g., 2025-07-01)')
@click.option('--before', metavar='DATE', help='download on/before DATE (e.g., 2025-08-31)')
@click.option('--daemon', is_flag=True, help='emit timestamped logs')
def main(data, config, force, from_last_date, after, before, daemon):
    """Download original quality images from Tinybeans photo journals."""

    # Resolve data directory
    if data:
        data_dir = os.path.abspath(os.path.expanduser(data))
    else:
        data_dir = click.get_app_dir('tinybeans-sync')

    os.makedirs(data_dir, exist_ok=True)

    # Resolve config path
    if config:
        config_path = os.path.abspath(os.path.expanduser(config))
    else:
        config_path = os.path.join(data_dir, 'config.yaml')

    handler = DateHandler(config_path, data_dir)
    setup_logging(handler.config, data_dir, daemon=daemon)

    # Pass force flag to downloader
    if force:
        handler.downloader.force = True
        logger.info("Force mode: Ignoring download history")

    try:
        # Determine what dates to process
        if after:
            start_date = handler.parse_date(after)
            end_date = handler.parse_date(before) if before else datetime.now()
            handler.download_date_range(start_date, end_date)

        elif from_last_date:
            # Resume from last download
            date_range = handler.get_from_last_date_range()
            if date_range:
                start_date, end_date = date_range
                handler.download_date_range(start_date, end_date)
            else:
                logger.warning("No download history found. Use specific dates instead.")
                raise SystemExit(1)

        else:
            # Use config defaults
            dates_config = handler.config.get('dates', {})

            if dates_config.get('from_last_date', False):
                # From last date mode
                date_range = handler.get_from_last_date_range()
                if date_range:
                    start_date, end_date = date_range
                    handler.download_date_range(start_date, end_date)
                else:
                    logger.warning("No download history found. Configure specific dates in config.yaml")
                    raise SystemExit(1)

            elif dates_config.get('single_date'):
                # Single date
                date_str = dates_config['single_date']
                if isinstance(date_str, str):
                    date_obj = handler.parse_date(date_str)
                    handler.download_single_month(date_obj.year, date_obj.month)

            elif dates_config.get('after'):
                start_date = handler.parse_date(dates_config['after'])
                end_date_value = dates_config.get('before')
                end_date = handler.parse_date(end_date_value) if end_date_value else datetime.now()
                handler.download_date_range(start_date, end_date)

            else:
                logger.warning("No date configuration found. Use CLI arguments or configure dates in config.yaml")
                raise SystemExit(1)

    except Exception as e:
        logger.error("Error: %s", e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
