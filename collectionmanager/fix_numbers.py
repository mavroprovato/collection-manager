import argparse
import logging
import os
import sys

import mutagen
import mutagen.id3

from collectionmanager.track_info import TrackInfo


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
            track_info = TrackInfo(file_path)

            # Fix the track number
            if track_info.track_number is not None:
                if track_info.track_number.find('/') != -1:
                    track_number = track_info.track_number[:track_info.track_number.find('/')]
                    logging.info('Changing track number from %s to %s for file %s', track_info.track_number,
                                 track_number, file_path)
                    track_info.file_info['TRCK'] = mutagen.id3.TRCK(text=track_number)
                    track_info.file_info.save()

            # Fix the disk number
            if track_info.disk_number is not None:
                if track_info.disk_number.find('/') != -1:
                    new_disk_number = track_info.disk_number[:track_info.disk_number.find('/')]
                    track_info.file_info['TPOS'] = mutagen.id3.TPOS(text=new_disk_number)
                    logging.info('Changing disk number from %s to %s for file %s', track_info.disk_number, new_disk_number,
                                 file_path)
                    track_info.file_info.save()


if __name__ == '__main__':
    main()
