import typing

import requests


class LastFmConnector:
    """Connector for the last.fm service
    """
    API_BASE = 'https://ws.audioscrobbler.com/2.0/'

    def __init__(self, api_key: str):
        """Create the last.fm album art fetcher.

        :param api_key: The API key for the service.
        """
        self.api_key = api_key

    def fetch_album_art(self, artist: str, album: str) -> typing.Optional[typing.Tuple[bytes, str]]:
        """Fetch the album art for a release.

        :param artist: The artist name.
        :param album: The album name.
        :return If the album art was found, return a tuple with the content as the first element and the content type as
        the second.
        """
        # Make the request for the album info
        response = requests.get(self.API_BASE, params={
            'method': 'album.getinfo', 'api_key': self.api_key, 'artist': artist, 'album': album, 'format': 'json'
        })
        response.raise_for_status()

        # Get the album art if it exists
        data = response.json()
        if 'album' in data:
            url = data['album']['image'][-1]['#text']
            response = requests.get(url)
            response.raise_for_status()

            return response.content, response.headers['Content-Type']
