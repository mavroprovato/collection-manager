import collections
import datetime
import io
import time
import typing
import logging

from PIL import Image, UnidentifiedImageError
import requests
from requests import HTTPError

logger = logging.getLogger(__name__)


class BaseService:
    """Abstract base class for services
    """
    MIN_SECS_BETWEEN_REQUESTS = 0

    def __init__(self):
        self._last_request_time = None
        self._release_cache = collections.defaultdict(dict)

    def album_art(self, artist: str, album: str) -> typing.Optional[bytes]:
        """Get the album art for a release.

        :param artist: The artist name.
        :param album: The album art.
        :return: The album art.
        """
        return self._get_info(artist, album, 'album_art', 'Album art')

    def genre(self, artist: str, album: str) -> typing.Optional[str]:
        """Get the genre a release.

        :param artist: The artist name.
        :param album: The album art.
        :return: The genre.
        """
        return self._get_info(artist, album, 'genre', 'Genre')

    def _get_info(self, artist: str, album: str, key: str, description: str):
        """Gets the required album info. First checks in the local cache, and if the info is not found, it queries the
        service.

        :param artist: The artist name.
        :param album: The album name.
        :param key: The key of the information to get.
        :param description: The description of the key.
        :return:
        """
        if not artist:
            logger.warning("Artist not set, cannot fetch info")
            return None
        if not album:
            logger.warning("Album not set, cannot fetch info")
            return None

        info = self._release_cache.get((artist, album), {}).get(key)
        if info:
            logger.debug("% found in cache", description)

            return info
        else:
            logger.info("Fetching %s for artist %s and album %s from service", description, artist, album)
            info = getattr(self, f'fetch_{key}')(artist, album)
            if info:
                logger.info("%s found", description)
                self._release_cache[(artist, album)][key] = info

                return info
            else:
                logger.warning("%s not found", description)

    def perform_request(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """Performs a request to the service API. This method makes sure that requests do not happen more frequently
        than the parameter MIN_SECS_BETWEEN_REQUESTS dictates.

        :param url: The url for the request.
        :param params: The request parameters.
        :param headers: The request headers.
        :return: The response data as JSON.
        """
        if self._last_request_time is not None:
            secs_since_last_request = (datetime.datetime.now() - self._last_request_time).total_seconds()
            if secs_since_last_request < self.MIN_SECS_BETWEEN_REQUESTS:
                sleep_time = self.MIN_SECS_BETWEEN_REQUESTS - secs_since_last_request
                logger.info(f"Waiting for %.2f seconds before next request", sleep_time)
                time.sleep(sleep_time)
        self._last_request_time = datetime.datetime.now()

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

    @staticmethod
    def fetch_image_from_url(url: str) -> typing.Optional[bytes]:
        """Fetch an image from a URL. The image is transformed to JPEG if needed.

        :param url: The image URL.
        :return: The image.
        """
        # Get the image content from the URL
        response = requests.get(url)
        try:
            response.raise_for_status()
        except HTTPError:
            logger.warning("Could not fetch image %s", url)
            return None
        content = response.content
        content_type = response.headers['Content-Type']
        # Transform the image to JPEG if needed
        if content_type != 'image/jpeg':
            try:
                logger.info("Transforming image to JPEG")
                image = Image.open(io.BytesIO(content))
                image = image.convert('RGB')
                output = io.BytesIO()
                image.save(output, format='JPEG')

                content = output.getvalue()
            except UnidentifiedImageError:
                logger.error("Could not decode file fetched from %s", url)
                return None

        return content
