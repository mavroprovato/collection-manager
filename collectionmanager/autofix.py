import argparse
import logging
import os
import sys

import mutagen.id3

from collectionmanager import services

logger = logging.getLogger(__name__)


def main():
    """Main entry point of the script.
    """
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_dir", help="The directory to scan for files")
    args = parser.parse_args()

    for current_root_name, _, files in os.walk(args.scan_dir):
        for file_name in files:
            file_path = os.path.join(current_root_name, file_name)
            track_info = services.TrackInfo(str(file_path))
            save = False

            # Check track number
            if 'TRCK' not in track_info.file_info:
                logger.info("Track number missing from %s, setting.", file_path)
                file_track_info = file_name[:file_name.find('.')].strip()
                track_number = int(file_track_info[file_track_info.find('-') - 1:])
                logger.info("Track number will be set to %d.", track_number)
                track_info.file_info['TRCK'] = mutagen.id3.TRCK(
                    encoding=mutagen.id3.Encoding.LATIN1, text=str(track_number))
                save = True
            elif track_info.file_info['TRCK'][0].startswith('0'):
                logger.info("Track number for %s contains a leading zero, stripping.", file_path)
                track_number = int(track_info.file_info['TRCK'][0])
                track_info.file_info['TRCK'] = mutagen.id3.TRCK(
                    encoding=mutagen.id3.Encoding.LATIN1, text=str(track_number))
                save = True

            if save:
                track_info.file_info.save()


if __name__ == '__main__':
    main()
