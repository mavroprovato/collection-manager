import argparse
import logging
import os
import re
import sys

from collectionmanager.track_info import TrackInfo

WINDOWS_UNSAFE_PATTERN = re.compile(r'[<>:"/\\|?*]')


def first_letter_capital(name: str) -> bool:
    """Check if the first letter of every word is a capital letter.

    :param name: The name to check.
    :return: true if every first letter is a capital letter, false otherwise.
    """
    if name:
        for part in re.compile(r'\s').split(name):
            if part and part[0].isalpha() and not part[0].isupper():
                return False

    return True


def safe_windows_naming(file_path: str) -> bool:
    """Check if a file path is safe for Windows file system. The following characters should not appear:

        < (less than)
        >(greater than)
        : (colon)
        " (double quote)
        / (forward slash)
        \ (backslash)
        | (vertical bar or pipe)
        ? (question mark)
        * (asterisk)

    :param file_path:
    :return:
    """
    for file_component in file_path.split(os.sep):
        if WINDOWS_UNSAFE_PATTERN.findall(file_component):
            return False

    return True


def check_file(file_path: str) -> None:
    """Check a file, and print any errors that are found.

    :param file_path: The absolute file path.
    """
    logging.info("Checking file %s", file_path)
    track_info = TrackInfo(file_path)

    # Check if tags are present
    if track_info.artist is None:
        logging.warning("Artist name missing for %s", file_path)
    if track_info.album_artist is None:
        logging.warning("Album artist name missing for %s", file_path)
    if track_info.album is None:
        logging.warning("Album name missing for %s", file_path)
    if track_info.name is None:
        logging.warning("Track name missing for %s", file_path)
    if track_info.year is None:
        logging.warning("Track year missing for %s", file_path)
    if track_info.track_number is None:
        logging.warning("Track number missing for %s", file_path)
    if track_info.track_number is not None:
        try:
            int(track_info.track_number)
        except ValueError:
            logging.warning("Track number is not an integer for file %s", file_path)
    if track_info.disk_number is None:
        logging.warning("Disc number missing for %s", file_path)
    if track_info.disk_number is not None:
        try:
            int(track_info.disk_number)
        except ValueError:
            logging.warning("Disc number is not an integer for file %s", file_path)
    if track_info.album_art is None:
        logging.warning("Album art missing for %s", file_path)

    # Check if capitalization of track information is correct
    if not first_letter_capital(track_info.artist):
        logging.warning("Capitalization for artist of file %s is not correct", file_path)
    if not first_letter_capital(track_info.album):
        logging.warning("Capitalization for album of file %s is not correct", file_path)
    if not first_letter_capital(track_info.name):
        logging.warning("Capitalization for track name of file %s is not correct", file_path)

    # Check for safe windows characters
    if not safe_windows_naming(file_path):
        logging.warning("Name of file %s is not safe for Windows", file_path)

    # Check file naming
    file_name = os.path.basename(file_path)
    file_track_name = file_name[file_name.find('.')+2:file_name.rfind('.')]
    target_file_name = WINDOWS_UNSAFE_PATTERN.sub('_', track_info.name)
    if track_info.album_artist != track_info.artist:
        target_file_name = track_info.artist + ' - ' + target_file_name
    if file_track_name != target_file_name:
        logging.warning("File name is not correct for file %s, track name should be %s", file_path, target_file_name)


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
