import argparse
import logging
import os
import pathlib
import sys
import typing

import mutagen
import mutagen.id3
import requests

from collectionmanager.db.models import Track


class LastFmService:
    """Connector for the last.fm service
    """
    API_BASE = 'https://ws.audioscrobbler.com/2.0/'

    def __init__(self, api_key: str):
        """Create the last.fm album art fetcher.

        :param api_key: The API key for the service.
        """
        self.api_key = api_key
        self.cache = {}

    def fetch_album_art(self, artist: str, album: str) -> typing.Optional[dict]:
        """Fetch the album art for a release.

        :param artist: The artist name.
        :param album: The album name.
        :return If the album art was found, return a tuple with the content as the first element and the content type as
        the second.
        """
        # Check if the album art is in the cache
        album_art = self.cache.get((artist, album), {}).get('album_art', {})
        if not album_art:
            # Make the request for the album info
            response = requests.get(self.API_BASE, params={
                'method': 'album.getinfo', 'api_key': self.api_key, 'artist': artist, 'album': album, 'format': 'json'
            })
            response.raise_for_status()

            # Get the album art if it exists
            data = response.json()
            if 'album' in data:
                url = data['album']['image'][-1]['#text']
                response = requests.get(url)
                response.raise_for_status()

                album_art = {'content': response.content, 'type': response.headers['Content-Type']}

        # Save album art in cache
        if (artist, album) not in self.cache:
            self.cache[(artist, album)] = {}
        if album_art:
            self.cache[(artist, album)]['album_art'] = album_art

        return album_art


def main():
    """Main entry point of the script.
    """
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_dir", help="The directory to scan for files")
    parser.add_argument("--force", action='store_true', help="Search for album art even if it exists")
    parser.add_argument("--api-key", help="API key (if needed)")
    args = parser.parse_args()

    service = LastFmService(args.api_key)
    # Scan the input directory
    for current_root_name, _, files in os.walk(args.scan_dir):
        for file_name in files:
            file_path = os.path.join(current_root_name, file_name)
            track_info = Track.from_id3(pathlib.Path(file_path))

            if track_info['album_art'] is None or args.force:
                logging.info(f"Searching album art for file {file_path}")
                if track_info['album_artist'] is None or track_info['album'] is None:
                    logging.warning('Album artist or/and album name is missing, skipping file')
                    continue
                album_art = service.fetch_album_art(track_info['album_artist'], track_info['album'])
                if album_art:
                    file_info = mutagen.File(file_path)
                    file_info.tags.add(mutagen.id3.APIC(
                        encoding=3, data=album_art['content'], mime=album_art['type'], type=3))
                    file_info.save()
                    logging.info('Album art saved')
                else:
                    logging.info('No album art found, skipping')


if __name__ == '__main__':
    main()
