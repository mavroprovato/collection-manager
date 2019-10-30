import argparse
import logging
import os
import pathlib
import re
import sys

from collectionmanager.db.models import Track

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
        \\ (backslash)
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
    logging.info(f"Checking file {file_path}")
    track_info = Track.from_id3(pathlib.Path(file_path))

    # Check for safe windows characters
    if not safe_windows_naming(file_path):
        logging.warning("Name of file %s is not safe for Windows", file_path)

    # Check artist
    if track_info['track_artist'] is None:
        logging.warning(f"Track artist name missing for {file_path}")
    else:
        # Check if capitalization of artist is correct
        if not first_letter_capital(track_info['track_artist']):
            logging.warning(f"Capitalization for track artist of file {file_path} is not correct")

    # Check album artist
    if track_info['album_artist'] is None:
        logging.warning(f"Album artist name missing for {file_path}")
    else:
        # Check if capitalization of album artist is correct
        if not first_letter_capital(track_info['album_artist']):
            logging.warning("Capitalization for album artist of file %s is not correct", file_path)

    # Check album
    if track_info['album'] is None:
        logging.warning(f"Album name missing for {file_path}")
    else:
        if not first_letter_capital(track_info['album']):
            logging.warning("Capitalization for album of file %s is not correct", file_path)

    # Check track name
    if track_info['name'] is None:
        logging.warning(f"Track name missing for {file_path}")
    else:
        if not first_letter_capital(track_info['name']):
            logging.warning(f"Capitalization for track name of file {file_path} is not correct")

    # Check track year
    if track_info['year'] is None:
        logging.warning(f"Track year missing for {file_path}")
    else:
        try:
            int(track_info['year'])
        except ValueError:
            logging.warning(f"Track year is not a number for {file_path}")

    # Check track number
    if track_info['number'] is None:
        logging.warning(f"Track number missing for {file_path}")
    else:
        try:
            int(track_info['number'])
        except ValueError:
            logging.warning(f"Track number is not a number for {file_path}")

    # Check track disk number
    if track_info['disk_number'] is None:
        logging.warning(f"Disc number missing for {file_path}")
    else:
        try:
            int(track_info['disk_number'])
        except ValueError:
            logging.warning(f"Disk number is not a number for {file_path}")

    # Check album art
    if track_info['album_art'] is None:
        logging.warning(f"Album art missing for {file_path}")

    # Check file naming
    file_name = os.path.basename(file_path)
    file_track_name = file_name[file_name.find('.')+2:file_name.rfind('.')]
    if track_info['album'] is not None and track_info['year'] is not None:
        album_dir_name = f"[{track_info['year']}] {WINDOWS_UNSAFE_PATTERN.sub('_', track_info['album'])}"
        parent_dir_name = os.path.basename(os.path.dirname(file_path))
        if album_dir_name != parent_dir_name:
            logging.warning(f"Parent directory for file {file_path} is not correct, should be {album_dir_name}")
    target_track_name = WINDOWS_UNSAFE_PATTERN.sub('_', track_info['name'])
    if track_info['album_artist'] != track_info['track_artist']:
        target_track_name = WINDOWS_UNSAFE_PATTERN.sub('_', track_info['track_artist'] + ' - ' + target_track_name)
    if file_track_name != target_track_name:
        logging.warning(f"File name is not correct for file {file_path}, track name should be {target_track_name}")
    if track_info['number'] is not None:
        try:
            int(track_info['number'])
            target_file_name = '{:02d}. {}.mp3'.format(int(track_info['number']), target_track_name)
            if not file_name.endswith(target_file_name):
                logging.warning(f"File name {file_name} is not correct, should be {target_file_name} ")
        except ValueError:
            pass


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
