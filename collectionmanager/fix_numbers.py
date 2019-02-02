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
    logging.basicConfig(stream=sys.stdout, level=logging.WARN)

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
                disk_number = track_number[track_number.find('/') + 1:]
                file_info['TRCK'] = mutagen.id3.TRCK(text=disk_number)
                file_info.save()

            disk_number = file_info['TPOS'][0] if 'TPOS' in file_info else None
            try:
                int(disk_number)
            except ValueError:
                disk_number = disk_number[disk_number.find('/')+1:]
                file_info['TPOS'] = mutagen.id3.TPOS(text=disk_number)
                file_info.save()


if __name__ == '__main__':
    main()
