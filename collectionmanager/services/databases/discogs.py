"""Integration with discogs
"""
import collections
import functools
import logging

import requests

from collectionmanager.services.databases import base

logger = logging.getLogger(__name__)


class DiscogsService(base.BaseService):
    """Connector for the discogs service
    """
    API_ROOT = 'https://api.discogs.com'
    USER_AGENT = 'collection-manager/0.0.1 +https://github.com/mavroprovato/collection-manager'

    def __init__(self, token: str):
        """Create the discogs service.

        :param token: The token for the service.
        """
        super().__init__()
        self.token = token

    def album_art(self, artist: str, album: str) -> bytes | None:
        """Fetch the album art.

        :param artist: The artist name.
        :param album: The album name.
        :return: The album art if found.
        """
        info = self._album_info(artist, album)
        for image in info['images']:
            if image['type'] == 'primary':
                return self.fetch_image_from_url(image['resource_url'], headers={'User-Agent': self.USER_AGENT})

        return None

    def genres(self, artist: str, album: str) -> list[str]:
        """Fetch the album genres.

        :param artist: The artist name.
        :param album: The album name.
        :return: The album art if found.
        """
        info = self._album_info(artist, album)

        return info['styles']

    @functools.cache
    def _album_info(self, artist: str, album: str) -> dict:
        """Fetch the album info from the Discogs API.

        :param artist: The artist name.
        :param album: The album name.
        :return: The album info if found.
        """
        # Get the release info
        # TODO: fetch all releases with pagination. Probably does not effect the results that much
        logger.info('Fetching album info from discogs API')
        data = self._make_request(
            "/database/search", params={"artist": artist.replace(',', ' '), "album": album.replace(',', ' ')}
        )

        # Get the master release
        master_ids = collections.Counter([result['master_id'] for result in data['results']])
        if not master_ids:
            return {}
        master_id = master_ids.most_common()[0][0]

        # Get the master release information
        return self._make_request(f"/masters/{master_id}")

    def _make_request(self, path: str, params: dict | None = None) -> dict:
        """Make a request to the Discogs API.

        :param params: The request parameters.
        :return: The response from the Discogs API.
        """
        if params is None:
            params = {}
        params['token'] = self.token

        response = requests.get(f"{self.API_ROOT}/{path}", params=params, headers={'User-Agent': self.USER_AGENT})
        response.raise_for_status()

        return response.json()
