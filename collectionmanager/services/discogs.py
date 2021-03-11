"""Integration with discogs
"""
import logging
import typing

from . import base

logger = logging.getLogger(__name__)


class DiscogsService(base.BaseService):
    """Connector for the discogs service
    """
    API_ROOT = 'https://api.discogs.com'
    USER_AGENT = 'collection-manager/0.0.1 +https://github.com/mavroprovato/collection-manager'
    MIN_SECS_BETWEEN_REQUESTS = 2

    def __init__(self, token: str):
        """Create the discogs service.

        :param token: The token for the service.
        """
        super().__init__()
        self._token = token

    def fetch_album_art(self, artist: str, album: str) -> typing.Optional[bytes]:
        """Fetch album art.

        :param artist: The artist name.
        :param album: The album name.
        :return The album art if found.
        """
        response = self.perform_request(f"{self.API_ROOT}/database/search", params={
            'artist': artist.replace(',', ' '), 'release_title': album.replace(',', ' '), 'token': self._token
        }, headers={'User-Agent': self.USER_AGENT})

        for result in response['results']:
            url = result.get('cover_image')
            if url:
                image = self.fetch_image_from_url(url)
                if image:
                    return image

    def fetch_genre(self, artist: str, album: str) -> typing.Optional[bytes]:
        """Fetch album genre.

        :param artist: The artist name.
        :param album: The album name.
        :return The album art if found.
        """
        response = self.perform_request(f"{self.API_ROOT}/database/search", params={
            'artist': artist.replace(',', ' '), 'release_title': album.replace(',', ' '), 'token': self._token
        }, headers={'User-Agent': self.USER_AGENT})

        for result in response['results']:
            if 'style' in result and result['style']:
                return result['style'][0]
