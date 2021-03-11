"""Integration with last.fm
"""
import logging
import typing

import requests

from . import base

logger = logging.getLogger(__name__)


class LastFmService(base.BaseService):
    """Connector for the last.fm service
    """
    API_ROOT = 'https://ws.audioscrobbler.com/2.0/'
    USER_AGENT = 'collection-manager/0.0.1 (https://github.com/mavroprovato/collection-manager)'

    def __init__(self, api_key: str):
        """Create the last.fm service.

        :param api_key: The API key for the service.
        """
        super().__init__()
        self._api_key = api_key

    def fetch_album_art(self, artist: str, album: str) -> typing.Optional[bytes]:
        """Fetch album art.

        :param artist: The artist name.
        :param album: The album name.
        :return The album art if found.
        """
        # Make the request for the album info
        response = requests.get(self.API_ROOT, params={
            'method': 'album.getinfo', 'api_key': self._api_key, 'artist': artist, 'album': album, 'format': 'json'
        })
        response.raise_for_status()

        # Get the album art if it exists
        data = response.json()
        if 'album' in data:
            url = data['album']['image'][-1]['#text']

            if url:
                return self.fetch_image_from_url(url)
