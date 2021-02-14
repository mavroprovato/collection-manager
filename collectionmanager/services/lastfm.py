"""Integration with last.fm
"""
import collections
import logging

import requests

logger = logging.getLogger(__name__)


class LastFmService:
    """Connector for the last.fm service
    """
    API_BASE = 'https://ws.audioscrobbler.com/2.0/'

    def __init__(self, api_key: str):
        """Create the last.fm service.

        :param api_key: The API key for the service.
        """
        self.api_key = api_key
        self.cache = collections.defaultdict(dict)

    def fetch_album_art(self, artist: str, album: str) -> str:
        """Fetch album art.

        :param artist: The artist name.
        :param album: The album name.
        :return If the album art was found, return the URL of the album art.
        """
        # Check if the album art is in the cache
        album_art = self.cache.get((artist, album), {}).get('album_art', {})
        if not album_art:
            # Make the request for the album info
            logger.info(f"Fetching album art for %s - %s", artist, album)
            response = requests.get(self.API_BASE, params={
                'method': 'album.getinfo', 'api_key': self.api_key, 'artist': artist, 'album': album, 'format': 'json'
            })
            response.raise_for_status()

            # Get the album art if it exists
            data = response.json()
            if 'album' in data:
                logger.info("Album art found")
                album_art = data['album']['image'][-1]['#text']
            else:
                logger.info("Could not find album art")

        # Save album art in cache
        if album_art:
            self.cache[(artist, album)]['album_art'] = album_art

        return album_art
