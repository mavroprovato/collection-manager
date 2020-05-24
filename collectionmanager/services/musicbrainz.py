"""Module to fetch album art.
"""
import logging
import re
import time

import requests


class MusicbrainzService:
    HEADERS = {'User-Agent': 'collection-manager/0.0.1 (https://github.com/mavroprovato/collection-manager)'}
    API_BASE = 'https://musicbrainz.org/ws/2/release-group/'

    def __init__(self):
        """Create the Musicbrainz album art fetcher.
        """
        self.album_art_cache = {}

    def fetch(self, artist: str, album: str):
        """Fetch the album art for a release.

        :param artist: The artist name.
        :param album: The album name.
        """
        if (artist, album) not in self.album_art_cache:
            release_ids = self.get_release_ids(artist, album)
            album_art_list = []
            for release_id in release_ids:
                album_art = self.get_album_art(release_id)
                if album_art is not None:
                    album_art_list.append(album_art)
            self.album_art_cache[(artist, album)] = album_art_list

        return self.album_art_cache[(artist, album)]

    @staticmethod
    def get_release_ids(artist: str, album: str):
        """Search for the ids of a release.

        :param artist: The release artist.
        :param album: The release album.
        :return: A list with the release ids.
        """
        artist = re.sub(r'[:/()?\[\]!"]', '', artist)
        album = re.sub(r'[:/()?\[\]!"]', '', album)
        logging.info('Searching for release with artist "%s" and album "%s"', artist, album)

        retries = 2
        while True:
            response = requests.get(MusicbrainzService.API_BASE, params={
                'query': 'release:{} AND artist:{}'.format(album, artist), 'fmt': 'json'
            }, headers=MusicbrainzService.HEADERS)
            if response.status_code == requests.codes.unavailable and retries != 0:
                time.sleep(5)
                retries -= 1
            else:
                response.raise_for_status()
                break

        data = response.json()
        if data['release-groups']:
            logging.info('Found %d release(s).', len(data['release-groups']))
            return [x['id'] for x in data['release-groups']]
        else:
            logging.warning('Could not find release')
            return []

    @staticmethod
    def get_album_art(release_id: str):
        """Get the album art for a release.

        :param release_id: The release id.
        :return: A list with all available album art content.
        """
        logging.info('Searching cover for release with id: %s', release_id)
        url = "http://coverartarchive.org/release-group/" + release_id
        response = requests.get(url, headers=MusicbrainzService.HEADERS)
        if response.status_code == requests.codes.not_found:
            logging.warning('Could not find cover')
            return
        else:
            response.raise_for_status()

        data = response.json()
        logging.info('Found %d cover(s).', len(data['images']))

        url = data['images'][0]['thumbnails']['large']
        response = requests.get(url, headers=MusicbrainzService.HEADERS)
        response.raise_for_status()

        return response.content


