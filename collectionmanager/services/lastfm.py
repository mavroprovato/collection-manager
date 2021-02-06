"""Integration with last.fm
"""
import collections

import requests


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
            response = requests.get(self.API_BASE, params={
                'method': 'album.getinfo', 'api_key': self.api_key, 'artist': artist, 'album': album, 'format': 'json'
            })
            response.raise_for_status()

            # Get the album art if it exists
            data = response.json()
            if 'album' in data:
                for image in data['album']['image']:
                    if image['size'] == 'large':
                        album_art = image['#text']

        # Save album art in cache
        if album_art:
            self.cache[(artist, album)]['album_art'] = album_art

        return album_art
