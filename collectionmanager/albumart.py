"""Module to fetch album art.
"""
import argparse
import logging
import os
import re
import sys
import time

import mutagen
import mutagen.id3
import requests

_cache = {}


class MusicbrainzFetcher:
    HEADERS = {'User-Agent': 'collection-manager/0.0.1 (https://github.com/mavroprovato/collection-manager)'}

    def fetch(self, artist: str, album: str):
        """Fetch the album art for a release.

        :param artist: The artist name.
        :param album: The album name.
        """
        if (artist, album) not in _cache:
            release_ids = self.get_release_ids(artist, album)
            album_art_list = []
            for release_id in release_ids:
                album_art = self.get_album_art(release_id)
                if album_art is not None:
                    album_art_list.append(album_art)
            _cache[(artist, album)] = album_art_list

        return _cache[(artist, album)]

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
            response = requests.get('http://musicbrainz.org/ws/2/release-group/', params={
                'query': 'release:{} AND artist:{}'.format(album, artist), 'fmt': 'json'
            }, headers=MusicbrainzFetcher.HEADERS)
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
        response = requests.get(url, headers=MusicbrainzFetcher.HEADERS)
        if response.status_code == requests.codes.not_found:
            logging.warning('Could not find cover')
            return
        else:
            response.raise_for_status()

        data = response.json()
        logging.info('Found %d cover(s).', len(data['images']))

        url = data['images'][0]['thumbnails']['large']
        response = requests.get(url, headers=MusicbrainzFetcher.HEADERS)
        response.raise_for_status()

        return response.content


class LastFmFetcher:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch(self, artist: str, album: str):
        """Fetch the album art for a release.

        :param artist: The artist name.
        :param album: The album name.
        """
        if (artist, album) not in _cache:
            response = requests.get('http://ws.audioscrobbler.com/2.0/', params={
                'method': 'album.getinfo', 'api_key': self.api_key, 'artist': artist, 'album': album, 'format': 'json'
            })
            response.raise_for_status()
            data = response.json()
            url = data['album']['image'][3]['#text'] if 'album' in data else None
            if url:
                response = requests.get(url)
                album_art_list = [response.content]
                _cache[(artist, album)] = album_art_list
            else:
                return []

        return _cache[(artist, album)]


def main():
    """Main entry point of the script.
    """
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_dir", help="The directory to scan for files")
    parser.add_argument("--force", action='store_true', help="Search for album art even if it exists")
    parser.add_argument("--api-key", help="API key (if needed)")
    args = parser.parse_args()

    fetcher = LastFmFetcher(args.api_key)
    # Scan the input directory
    for current_root_name, _, files in os.walk(args.scan_dir):
        for file_name in files:
            file_path = os.path.join(current_root_name, file_name)
            file_info = mutagen.File(file_path)

            if 'APIC:' not in file_info or args.force:
                logging.info('Searching album art for file %s', file_path)
                if 'TPE1' not in file_info or 'TALB' not in file_info:
                    logging.warning('Required file info missing, skipping')
                    continue
                artist, album = file_info['TPE1'][0], file_info['TALB'][0]
                album_art_list = fetcher.fetch(artist, album)
                if len(album_art_list) == 0:
                    logging.info('No album art found, skipping')
                    continue
                album_art = album_art_list[0]
                file_info.tags.add(mutagen.id3.APIC(encoding=3, mime='image/jpeg', type=3, data=album_art))
                file_info.save()
                logging.info('Album art set')
            else:
                logging.info('Skipping file %s', file_path)


if __name__ == '__main__':
    main()