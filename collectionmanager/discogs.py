import json
import logging
import os
import sys
import time

import requests
from PyQt5 import QtCore, QtWidgets


class DiscogsManager:
    base_url = 'https://api.discogs.com'
    headers = {
        'User-Agent': 'collection-manager/0.0.1 +mavroprovato.net/1.0',
    }

    def __init__(self, config_dir, token):
        self.config_dir = config_dir
        self.token = token
        self.collection = self.get_collection()
        self.artists = self.get_artists()
        self.releases = self.get_releases()

    def get_collection(self):
        file_name = os.path.join(self.config_dir, 'collection.json')
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                return json.load(f)
        else:
            collection = self.fetch_collection()
            with open(file_name, 'w') as f:
                json.dump(collection, f)
            return collection

    def fetch_collection(self):
        collection = []

        # Get the user name of the logged in user
        logging.info('Getting user name')
        identity_response = self.make_request('{}/oauth/identity'.format(self.base_url))
        username = identity_response['username']

        # Get user folders
        logging.info('Getting collection folders')
        folders_response = self.make_request('{}/users/{}/collection/folders'.format(self.base_url, username))

        # Get all releases for the "All" folder
        for folder in folders_response['folders']:
            if folder['name'] != 'All':
                continue
            url = folder['resource_url']
            page = 0
            while True:
                logging.info('Processing page %d', page)
                try:
                    folder_response = self.make_request('{}/releases'.format(url), {'page': page, 'per_page': 100})
                    collection += [release for release in folder_response['releases']]
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        # No more pages
                        break
                    else:
                        raise e

                page += 1

        return collection

    def get_artists(self):
        artists = {}
        os.makedirs(os.path.join(self.config_dir, 'artists'), exist_ok=True)
        for release in self.collection:
            for artist in release['basic_information']['artists']:
                file_name = os.path.join(self.config_dir, 'artists', str(artist['id']) + '.json')
                if os.path.exists(file_name):
                    with open(file_name, 'r') as f:
                        artists[artist['id']] = json.load(f)
                else:
                    if artist['name'] == 'Various':
                        continue
                    logging.info('Fetching artist %s', artist['name'])
                    artist_info = self.make_request(artist['resource_url'])
                    with open(file_name, 'w') as f:
                        json.dump(artist_info, f)
                    artists[artist['id']] = artist_info

        return artists

    def get_releases(self):
        releases = {}
        os.makedirs(os.path.join(self.config_dir, 'releases'), exist_ok=True)

        for release in self.collection:
            release_id = release['basic_information']['id']
            file_name = os.path.join(self.config_dir, 'releases', str(release_id) + '.json')
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    releases[release_id] = json.load(f)
            else:
                logging.info('Fetching release %s', release_id)
                release_info = self.make_request(release['basic_information']['resource_url'])
                with open(file_name, 'w') as f:
                    json.dump(release_info, f)
                releases[release_id] = release_info

        return releases

    def make_request(self, url, request_params=None, retry_count=3):
        while True:
            try:
                params = {'token': self.token}
                if request_params is not None:
                    params.update(request_params)

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                retry_count -= 1
                if retry_count == 0:
                    raise e
                time.sleep(1)

        return response.json()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('collection-manager')

    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    config_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
    manager = DiscogsManager(config_dir, sys.argv[1])


if __name__ == '__main__':
    main()
