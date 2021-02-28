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


def clear_album_art(input_dir: str, force: bool = False):
    """Clears album art for all files in a directory.

    :param input_dir: The file path.
    :param force: Set to true in order not to ask for user confirmation.
    """
    if not force:
        response = input("Are you sure you want to clear all album art (y/n)? ")
        if response == 'y':
            logging.info("Clearing album art for all files in %s", input_dir)
            for file_path in pathlib.Path(input_dir).glob('**/*.mp3'):
                track_info = services.TrackInfo(str(file_path))
                if 'APIC:' in track_info.file_info:
                    logger.info("Clearing album art from file %s", file_path)
                    track_info.file_info.pop('APIC:')
                    track_info.file_info.save()


def fetch_album_art(input_dir: str, service, force: bool = False):
    """Fetch album art for files in a directory.

    :param input_dir: The input directory.
    :param service: The service to use in order to fetch album art.
    :param force: Set to true in order to save the album art even if it exists.
    """
    logging.info("Fetching album art for all files in %s", input_dir)
    for file_path in pathlib.Path(input_dir).glob('**/*.mp3'):
        track_info = services.TrackInfo(str(file_path))
        if track_info.album_art is None or force:
            album_art = service.album_art(track_info.album_artist, track_info.album)
            track_info.file_info.tags.add(mutagen.id3.APIC(
                encoding=mutagen.id3.Encoding.LATIN1, data=album_art, mime="image/jpeg",
                type=mutagen.id3.PictureType.COVER_FRONT)
            )
            track_info.file_info.save()


def export_album_art(input_dir: str, service, output_dir: str):
    """Export album art to a directory.

    :param input_dir: The input directory.
    :param service: The service to use in order to fetch album art.
    :param output_dir:
    :return:
    """
    logging.info("Exporting album art for all files in %s to directory %s", input_dir, output_dir)
    for file_path in pathlib.Path(input_dir).glob('**/*.mp3'):
        track_info = services.TrackInfo(str(file_path))
        art_output_dir = pathlib.Path(output_dir) / track_info.album_artist / track_info.album
        art_output_dir.mkdir(parents=True, exist_ok=True)
        album_art = service.album_art(track_info.album_artist, track_info.album)
        if album_art:
            with open(art_output_dir / "AlbumArt.jpg", "wb") as f:
                f.write(album_art)


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
    parser.add_argument("--output", help="The output directory")
    args = parser.parse_args()

    service = services.LastFmService(args.api_key)

    if not os.path.isdir(args.directory):
        logging.error("%s is not a directory", args.directory)
        return

    if args.action == 'fetch':
        logging.info("Updating album art for files in directory %s", args.directory)
        fetch_album_art(args.directory, service, args.force)
    elif args.action == 'clear':
        clear_album_art(args.directory, args.force)
    elif args.action == 'export':
        if args.output:
            export_album_art(args.directory, service, args.output)
        else:
            print("You must specify an output directory")


if __name__ == '__main__':
    main()
