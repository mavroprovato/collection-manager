import abc
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


class BaseService(abc.ABC):
    """Abstract base class for services
    """
    MIN_SECS_BETWEEN_REQUESTS = 0

    def __init__(self):
        self._last_request_time = None
        self._release_cache = collections.defaultdict(dict)

    def album_art(self, artist: str, album: str):
        """Get the album art for a release.

        :param artist: The artist name.
        :param album: The album art.
        :return:
        """
        album_art = self._release_cache.get((artist, album), {}).get('album_art')
        if album_art:
            logger.debug("Album art found in cache")
            return album_art
        else:
            logger.info("Fetching album art for artist '%s' and album '%s' from service", artist, album)
            album_art = self.fetch_album_art(artist, album)
            if album_art:
                logger.info("Album art found")
                self._release_cache[(artist, album)]['album_art'] = album_art

                return album_art
            else:
                logger.warning("Album art not found")

    @abc.abstractmethod
    def fetch_album_art(self, artist: str, album: str) -> typing.Optional[bytes]:
        pass

    def perform_request(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """Performs a request to the musicbrainz API. Makes sure that requests do not happen more frequently than the
        parameter MIN_SECS_BETWEEN_REQUESTS dictates.

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
