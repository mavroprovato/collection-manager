"""Integration with musicbrainz.
"""
import datetime
import logging
import time
import typing

import requests

from .base import BaseService

logger = logging.getLogger(__name__)


class MusicbrainzService(BaseService):
    """Connector for the musicbrainz service
    """
    API_ROOT = 'https://musicbrainz.org/ws/2/release-group/'
    USER_AGENT = 'collection-manager/0.0.1 (https://github.com/mavroprovato/collection-manager)'
    MIN_SECS_BETWEEN_REQUESTS = 1

    def __init__(self):
        """Create the service
        """
        super().__init__()
        self._last_request_time = None

    def fetch_album_art(self, artist: str, album: str) -> typing.Optional[bytes]:
        """Fetch album art.

        :param artist: The artist name.
        :param album: The album name.
        :return The album art if found.
        """
        response = self.perform_request(url=self.API_ROOT, params={
            'query': 'release:{} AND artist:{}'.format(album, artist), 'fmt': 'json'
        }, headers={'User-Agent': self.USER_AGENT})
        for release in response['release-groups']:
            url = f"https://coverartarchive.org/release-group/{release['id']}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                for image in response.json()['images']:
                    if image['approved'] and image['front']:
                        return self.fetch_image_from_url(image['thumbnails']['large'])
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    continue
                else:
                    raise
