import argparse
import logging
import os
import sys

import mutagen
import mutagen.id3


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
            file_info = mutagen.File(file_path)

            track_number = file_info['TRCK'][0] if 'TRCK' in file_info else None
            try:
                int(track_number)
            except ValueError:
                new_track_number = track_number[track_number.find('/') + 1:]
                file_info['TRCK'] = mutagen.id3.TRCK(text=new_track_number)
                logging.info('Changing track number from %s to %s for file %s', track_number, new_track_number,
                             file_path)
                file_info.save()

            disk_number = file_info['TPOS'][0] if 'TPOS' in file_info else None
            try:
                int(disk_number)
            except ValueError:
                new_disk_number = disk_number[disk_number.find('/')+1:]
                file_info['TPOS'] = mutagen.id3.TPOS(text=new_disk_number)
                logging.info('Changing disk number from %s to %s for file %s', disk_number, new_disk_number,
                             file_path)
                file_info.save()


if __name__ == '__main__':
    main()
