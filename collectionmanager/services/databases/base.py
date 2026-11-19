import io
import logging

from PIL import Image, UnidentifiedImageError
import requests
from requests import HTTPError

logger = logging.getLogger(__name__)


class BaseService:
    """Abstract base class for services
    """
    def album_art(self, artist: str, album: str) -> bytes | None:
        """Get the album art for a release.

        :param artist: The artist name.
        :param album: The album art.
        :return: The album art.
        """

    def genres(self, artist: str, album: str) -> list[str]:
        """Get the genre a release.

        :param artist: The artist name.
        :param album: The album art.
        :return: The genre.
        """

    @staticmethod
    def fetch_image_from_url(url: str, headers: dict | None = None) -> bytes | None:
        """Fetch an image from a URL. The image is transformed to JPEG if needed.

        :param url: The image URL.
        :param headers: The headers for the request.
        :return: The image.
        """
        # Get the image content from the URL
        if headers is None:
            headers = {}
        response = requests.get(url, headers=headers)
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
