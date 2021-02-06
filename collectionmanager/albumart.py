import argparse
import io
import logging
import os
import mutagen.id3
import pathlib
import requests
import sys
import typing

from PIL import Image, UnidentifiedImageError

from collectionmanager import db, services


class AlbumArtFetcher:
    def __init__(self) -> None:
        """Create the album art fetcher.
        """
        self.cache = {}

    def fetch_album_art(self, url: str, force_jpeg=True) -> typing.Tuple[str, str]:
        """Fetch the album art from the provided url.

        :param url: The url.
        :param force_jpeg: If true, the downloaded picture will be transformed to JPEG.
        :return: A tuple, with the binary content as the first element, and the content type as the second.
        """
        if url not in self.cache:
            # Get the image content from the URL
            response = requests.get(url)
            response.raise_for_status()
            content = response.content
            content_type = response.headers['Content-Type']
            if content_type != 'image/jpeg' and force_jpeg:
                # Try to transform the image to JPEG if requested.
                try:
                    logging.info("Transforming image to JPEG")
                    image = Image.open(io.BytesIO(content))
                    image = image.convert('RGB')
                    content = io.BytesIO()
                    image.save(content, format='JPEG')
                    content = content.getvalue()
                    content_type = 'image/jpeg'
                except UnidentifiedImageError:
                    logging.error("Could not decode file from %s", url)

            self.cache[url] = (content, content_type)

        return self.cache[url]


def save_album_art(service, fetcher, file_path: str, force: bool = False) -> typing.NoReturn:
    """Save the album art for a file.

    :param service: The service to fetch the data for.
    :param fetcher: The album art fetcher.
    :param file_path: The file path.
    :param force: Set to true in order to save the album art even if it exists.
    """
    track_info = db.Track.from_id3(pathlib.Path(file_path))

    if track_info['album_art'] is None or force:
        logging.info(f"Searching album art for file {file_path}")
        if track_info['album_artist'] is None:
            logging.warning('Album artist is missing, skipping file')
            return
        if track_info['album'] is None:
            logging.warning('Album name is missing, skipping file')
            return
        album_art = service.fetch_album_art(track_info['album_artist'], track_info['album'])
        if album_art:
            content, content_type = fetcher.fetch_album_art(album_art)
            if content and content_type:
                file_info = mutagen.File(file_path)
                file_info.tags.add(mutagen.id3.APIC(
                    encoding=mutagen.id3.Encoding.LATIN1, data=content, mime=content_type,
                    type=mutagen.id3.PictureType.COVER_FRONT))
                file_info.save()
                logging.info('Album art saved')
            else:
                logging.warning('Could not download album art')
        else:
            logging.warning('No album art found, skipping')


def main():
    """Main entry point of the script.
    """
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_dir", help="The directory to scan for files")
    parser.add_argument("--force", action='store_true', help="Search for album art even if it exists")
    parser.add_argument("--api-key", help="The API key for the service")
    args = parser.parse_args()

    service = services.LastFmService(args.api_key)
    fetcher = AlbumArtFetcher()

    # Scan the input directory
    if not os.path.isdir(args.scan_dir):
        logging.error("%s is not a directory", args.scan_dir)
    logging.info("Scanning directory %s", args.scan_dir)
    for current_root_name, _, files in os.walk(args.scan_dir):
        for file_name in files:
            file_path = os.path.join(current_root_name, file_name)
            save_album_art(service, fetcher, file_path, args.force)


if __name__ == '__main__':
    main()
