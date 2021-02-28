"""Integration with last.fm
"""
import io
import logging

from PIL import Image, UnidentifiedImageError
import requests

from . import base

logger = logging.getLogger(__name__)


class LastFmService(base.BaseService):
    """Connector for the last.fm service
    """
    API_BASE = 'https://ws.audioscrobbler.com/2.0/'

    def __init__(self, api_key: str):
        """Create the last.fm service.

        :param api_key: The API key for the service.
        """
        super().__init__()
        self._api_key = api_key

    def fetch_album_art(self, artist: str, album: str) -> bytes:
        """Fetch album art.

        :param artist: The artist name.
        :param album: The album name.
        :return If the album art was found, return the URL of the album art.
        """
        # Make the request for the album info
        response = requests.get(self.API_BASE, params={
            'method': 'album.getinfo', 'api_key': self._api_key, 'artist': artist, 'album': album, 'format': 'json'
        })
        response.raise_for_status()

        # Get the album art if it exists
        data = response.json()
        if 'album' in data:
            url = data['album']['image'][-1]['#text']

            # Get the image content from the URL
            response = requests.get(url)
            response.raise_for_status()
            content = response.content
            content_type = response.headers['Content-Type']
            if content_type != 'image/jpeg':
                # Transform the image to JPEG.
                try:
                    logger.info("Transforming image to JPEG")
                    image = Image.open(io.BytesIO(content))
                    image = image.convert('RGB')
                    content = io.BytesIO()
                    image.save(content, format='JPEG')

                    return content.getvalue()
                except UnidentifiedImageError:
                    logger.error("Could not decode file fetched from %s", url)
