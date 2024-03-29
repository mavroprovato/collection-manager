"""Module to manage album art.
"""
import argparse
import logging
import os
import pathlib
import mutagen.id3
import sys

from collectionmanager import services

logger = logging.getLogger(__name__)


def clear_album_genre(input_dir: str, force: bool = False):
    """Clears album genre for all files in a directory.

    :param input_dir: The file path.
    :param force: Set to true in order not to ask for user confirmation.
    """
    if not force:
        response = input("Are you sure you want to clear all album genre (y/n)? ")
        if response == 'y':
            logging.info("Clearing album genre for all files in %s", input_dir)
            for file_path in pathlib.Path(input_dir).glob('**/*.mp3'):
                track_info = services.TrackInfo(str(file_path))
                if 'TCON' in track_info.file_info:
                    logger.info("Clearing album genre from file %s", file_path)
                    track_info.file_info.pop('TCON')
                    track_info.file_info.save()


def fetch_album_genre(input_dir: str, service, force: bool = False):
    """Fetch album genre for files in a directory.

    :param input_dir: The input directory.
    :param service: The service to use in order to fetch album art.
    :param force: Set to true in order to save the album art even if it exists.
    """
    logging.info("Fetching album genre for all files in %s", input_dir)
    for file_path in pathlib.Path(input_dir).glob('**/*.mp3'):
        track_info = services.TrackInfo(str(file_path))
        if track_info.genre is None or force:
            genre = service.genre(track_info.album_artist, track_info.album)
            if genre:
                track_info.file_info.tags.add(mutagen.id3.TCON(encoding=mutagen.id3.Encoding.UTF8, text=genre))
                track_info.file_info.save()


def export_album_genre(input_dir: str, service, force: bool = False):
    """Export album art to a directory.

    :param input_dir: The input directory.
    :param service: The service to use in order to fetch album art.
    :param force: Set to true in order to save the album art even if it exists.
    :return:
    """
    logging.info("Fetching genre for all files in %s", input_dir)
    for file_path in pathlib.Path(input_dir).glob('**/*.mp3'):
        track_info = services.TrackInfo(str(file_path))
        if track_info.genre is None or force:
            genre = service.genre(track_info.album_artist, track_info.album)
            if genre:
                logger.info("Genre for artist %s and album %s is %s", track_info.album_artist, track_info.album, genre)


def main():
    """Main entry point of the script.
    """
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["fetch", "export", "clear"], help="The action to perform")
    parser.add_argument("directory", help="The directory to scan for files")
    parser.add_argument("--force", action='store_true', help="Force the action")
    parser.add_argument("--api-key", help="The API key for the service")
    args = parser.parse_args()

    service = services.DiscogsService(args.api_key)

    if not os.path.isdir(args.directory):
        logging.error("%s is not a directory", args.directory)
        return

    if args.action == 'fetch':
        fetch_album_genre(args.directory, service, args.force)
    elif args.action == 'clear':
        clear_album_genre(args.directory, args.force)
    elif args.action == 'export':
        export_album_genre(args.directory, service, args.force)


if __name__ == '__main__':
    main()
