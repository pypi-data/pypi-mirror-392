#!/usr/bin/env python3
"""
Image downloader for Tinybeans entries
"""
import logging
import os
from datetime import datetime
from .api import TinybeansAPI
from .history import DownloadHistory

logger = logging.getLogger(__name__)

class TinybeansDownloader:
    def __init__(self, config_path, data_dir):
        self.data_dir = os.path.abspath(os.path.expanduser(data_dir))
        os.makedirs(self.data_dir, exist_ok=True)
        self.api = TinybeansAPI(config_path)
        self.config = self.api.auth.config
        # Initialize history with target downloads directory
        config_output_dir = self.config.get('download', {}).get('output_dir', 'downloads')
        target_root = os.path.expanduser(config_output_dir)
        os.makedirs(target_root, exist_ok=True)  # Ensure target root exists for downloads
        history_file = os.path.join(self.data_dir, 'tinybeans_history.json')

        self.history = DownloadHistory(history_file)
        self.force = False  # Can be set to ignore history

    def _generate_filename(self, timestamp, entry_id, sequence=0):
        """Generate filename based on config pattern"""
        download_config = self.config.get('download', {})
        pattern = download_config.get('filename_pattern', 'tinybeans-{date}_{time}.jpg')

        # Convert timestamp to datetime
        if timestamp:
            dt = datetime.fromtimestamp(timestamp / 1000)
            date_str = dt.strftime('%Y-%m-%d')
            time_str = dt.strftime('%H-%M-%S')
        else:
            date_str = 'unknown-date'
            time_str = 'unknown-time'

        # Replace pattern variables
        filename = pattern.replace('{date}', date_str).replace('{time}', time_str)

        # Handle duplicates by adding sequence
        if sequence > 0:
            name, ext = os.path.splitext(filename)
            filename = f"{name}-{sequence}{ext}"

        return filename, timestamp

    def _set_file_timestamp(self, filepath, timestamp):
        """Set file modification time to match photo timestamp"""
        download_config = self.config.get('download', {})
        if download_config.get('fix_timestamps', False) and timestamp:
            # Convert to seconds and set both access and modification time
            timestamp_sec = timestamp / 1000
            os.utime(filepath, (timestamp_sec, timestamp_sec))

    def download_month(self, year, month, output_dir=None):
        """Download all original quality images for a specific month"""
        if output_dir is None:
            config_output_dir = self.config.get('download', {}).get('output_dir', 'downloads')
            output_dir = os.path.expanduser(os.path.join(config_output_dir, f"{year}-{month:02d}"))

        logger.info("Downloading images for %04d-%02d", year, month)

        # Get entries from API
        entries = self.api.get_entries(year, month)
        photo_entries = [e for e in entries if e.get('type') == 'PHOTO']

        logger.info("Found %d total entries, %d photos", len(entries), len(photo_entries))

        # Skip if no photos found
        if len(photo_entries) == 0:
            logger.info("No photos to download")
            return 0

        # Create directory only if we have photos to download
        os.makedirs(output_dir, exist_ok=True)

        downloaded = 0

        for i, entry in enumerate(photo_entries, 1):
            entry_id = entry.get('id')
            timestamp = entry.get('timestamp')

            # Create readable timestamp
            if timestamp:
                date_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d_%H-%M-%S')
            else:
                date_str = f"unknown_{i:03d}"

            logger.info("Entry %d/%d: %s (%s)", i, len(photo_entries), entry_id, date_str)

            # Get original quality image URL
            blobs = entry.get('blobs', {})
            if isinstance(blobs, dict) and 'o' in blobs:
                original_url = blobs['o']

                # Check if we should ignore thumbnails
                ignore_thumbnails = self.config.get('download', {}).get('ignore_thumbnails', False)
                if ignore_thumbnails and 'thumbnail' in original_url.lower():
                    logger.info("Skipping video thumbnail for entry %s", entry_id)
                    continue

                # Generate clean filename
                sequence = 0
                while True:
                    filename, photo_timestamp = self._generate_filename(timestamp, entry_id, sequence)
                    filepath = os.path.join(output_dir, filename)

                    # Check if this filename already exists for a different entry
                    if os.path.exists(filepath):
                        # Check if it's the same file by looking in history
                        original_filename = original_url.split('/')[-1]
                        if self.history.is_attempted(original_filename):
                            # This is the same entry, use this filename
                            break
                        else:
                            # Different entry with same timestamp, increment sequence
                            sequence += 1
                            continue
                    else:
                        break

                # Use original filename for history tracking
                original_filename = original_url.split('/')[-1]

                # Check history first (unless force mode)
                if not self.force and self.history.is_attempted(original_filename):
                    logger.info("Entry %s already attempted (history)", entry_id)
                    continue

                # Download if not exists on disk (or force mode)
                if self.force or not os.path.exists(filepath):
                    try:
                        logger.info("Downloading %s", filename)
                        self._download_image(original_url, filepath)
                        self._set_file_timestamp(filepath, photo_timestamp)
                        self.history.mark_attempted(original_filename)
                        downloaded += 1
                        logger.info("Downloaded %s", filename)
                    except Exception as e:
                        logger.error("Error downloading %s: %s", filename, e)
                else:
                    # File exists and not in history - add to history
                    self.history.mark_attempted(original_filename)
                    logger.info("Already exists, added to history: %s", filename)
            else:
                logger.info("No original image found for entry %s", entry_id)

        logger.info("Downloaded %d new images to %s", downloaded, output_dir)
        return downloaded

    def _download_image(self, url, filepath):
        """Download a single image"""
        session = self.api.auth.get_session()
        response = session.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
