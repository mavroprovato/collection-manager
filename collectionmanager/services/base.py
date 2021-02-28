import abc
import collections
import io
import typing
import logging

from PIL import Image, UnidentifiedImageError
import requests


logger = logging.getLogger(__name__)


class BaseService(abc.ABC):
    """Abstract base class for services
    """
    def __init__(self):
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
    def fetch_album_art(self, artist: str, album: str) -> bytes:
        pass

    @staticmethod
    def fetch_image_from_url(url: str) -> typing.Optional[bytes]:
        """Fetch an image from a URL. The image is transformed to JPEG if needed.

        :param url: The image URL.
        :return: The image.
        """
        # Get the image content from the URL
        response = requests.get(url)
        response.raise_for_status()
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
