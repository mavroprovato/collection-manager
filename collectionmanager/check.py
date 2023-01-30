import argparse
import itertools
import logging
import pathlib
import re
import sys

from collectionmanager.services import trackinfo

# Logger for this module
logger = logging.getLogger(__name__)

# Unsafe characters for file naming
UNSAFE_CHARACTERS = re.compile(r'[<>:"/\\|?*]')
# The character to replace for unsafe charters
UNSAFE_CHARACTERS_REPLACE = '_'
# The file name pattern
FILE_NAME_PATTERN = re.compile(
    r'(?P<artist>[^/]+)/'
    r'\[(?P<year>[0-9]{4})] (?P<album>[^/]+)/'
    r'(?P<disk_number>[0-9]?)-?(?P<track_number>[0-9]{2})\. (?P<track_name>.+).(?P<type>mp3|flac)')


def check_capitalisation(name: str) -> bool:
    """Check if the first letter of every word is a capital letter.

    :param name: The name to check.
    :return: true if every first letter is a capital letter, false otherwise.
    """
    if name:
        for part in re.compile(r'\s').split(name):
            if part and part[0].isalpha() and not part[0].isupper():
                return False

    return True


def replace_unsafe_chars(string: str) -> str:
    """Replace unsafe characters in a string.

    :param string: The string.
    :return: The string after replacements.
    """
    return UNSAFE_CHARACTERS.sub(UNSAFE_CHARACTERS_REPLACE, string)


def check_file(scan_dir: pathlib.Path, file: pathlib.Path):
    """Check if the file contains usafe characters.

    :param scan_dir: The scan directory
    :param file: The file
    """
    logger.info("Checking file '%s", file)
    for part in file.relative_to(scan_dir).parts:
        if UNSAFE_CHARACTERS.findall(part):
            logger.warning(f"'%s' contains unsafe file name characters", file)
    # Parse track information
    track_info = trackinfo.TrackInfo.from_file(pathlib.Path(file))

    # Check track artist
    if not track_info.artist:
        logger.warning("Artist info is missing for file '%s", file)
    elif not check_capitalisation(track_info.artist):
        logger.warning("Artist info capitalization is wrong for file '%s': %s", file, track_info.artist)

    # Check track album
    if not track_info.album:
        logger.warning("Track album info is missing for file '%s", file)
    elif not check_capitalisation(track_info.album):
        logger.warning("Track album info capitalization is wrong for file '%s': %s", file, track_info.album)

    # Check track year
    if not track_info.year:
        logger.warning("Track year info is missing for file '%s", file)

    # Check track number
    if not track_info.number:
        logger.warning("Track number info is missing for file '%s", file)

    # Check track title
    if not track_info.title:
        logger.warning("Track title info is missing for file '%s", file)
    elif not check_capitalisation(track_info.title):
        logger.warning("Track title info capitalization is wrong for file '%s': %s", file, track_info.title)

    # Check album art
    # if not track_info.album_art:
    #     logger.warning("Album art is missing for file '%s", file)

    # Check naming conventions
    relative_file_name = str(file.relative_to(file.parent.parent.parent))
    match = FILE_NAME_PATTERN.match(relative_file_name)
    if match:
        # Check track year
        if track_info.year and int(match.group('year')) != track_info.year:
            logger.warning("File name year does not match file info for file '%s', should be '%s', is '%s'",
                           file, track_info.year, match.group('year'))
        # Check track album
        if track_info.album and match.group('album') != replace_unsafe_chars(track_info.album):
            logger.warning("File name album does not match file info for file '%s', should be '%s', is '%s'",
                           file, track_info.album, match.group('album'))
        # Check disk number
        if match.group('disk_number'):
            if not track_info.disk_number or int(match.group('disk_number')) != track_info.disk_number:
                logger.warning("File name disk number does not match file info for file '%s', should be '%s', is '%s'",
                               file, track_info.disk_number, match.group('disk_number'))

        # Check track number
        if track_info.number and int(match.group('track_number')) != track_info.number:
            logger.warning("File name track number does not match file info for file '%s', should be '%s', is '%s'",
                           file, track_info.number, match.group('track_number'))

        # TODO: replace this with a better way to check for compilations
        if track_info.album_artist != 'Various Artists' and match.group('artist') != 'Various Artists':
            if track_info.artist and match.group('artist') != replace_unsafe_chars(track_info.artist):
                logger.warning("File name artist does not match file info for file '%s', should be '%s', is '%s'",
                               file, track_info.artist, match.group('artist'))
    else:
        logger.warning("File name '%s' does not match naming conventions", file)


def main():
    """Main entry point of the script.
    """
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.WARN)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_dir", help="The directory to scan for files")
    args = parser.parse_args()

    scan_dir = pathlib.Path(args.scan_dir)
    for file in itertools.chain(scan_dir.rglob('*.flac'), scan_dir.rglob('*.mp3')):
        check_file(scan_dir, file)


if __name__ == '__main__':
    main()
