import argparse
import logging
import os
import re
import sys

from collectionmanager.track_info import TrackInfo


def first_letter_capital(name: str):
    if name:
        for part in re.compile(r'\s').split(name):
            if part and part[0].isalpha() and not part[0].isupper():
                return False

    return True


def check_file(file_path: str):
    logging.info("Checking file %s", file_path)
    track_info = TrackInfo(file_path)

    # Check if tags are present
    if track_info.artist is None:
        logging.warning("Artist name missing for %s", file_path)
    if track_info.album is None:
        logging.warning("Album name missing for %s", file_path)
    if track_info.name is None:
        logging.warning("Track name missing for %s", file_path)
    if track_info.track_number is None:
        logging.warning("Track number missing for %s", file_path)

    # Check if capitalization of track information is correct
    if not first_letter_capital(track_info.artist):
        logging.warning("Capitalization for artist of file %s is not correct", file_path)
    if not first_letter_capital(track_info.album):
        logging.warning("Capitalization for album of file %s is not correct", file_path)
    if not first_letter_capital(track_info.name):
        logging.warning("Capitalization for track name of file %s is not correct", file_path)


def main():
    """Main entry point of the script.
    """
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.WARN)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_dir", help="The directory to scan for files")
    args = parser.parse_args()

    for current_root_name, _, files in os.walk(args.scan_dir):
        for file_name in files:
            file_path = os.path.join(current_root_name, file_name)
            check_file(file_path)


if __name__ == '__main__':
    main()
