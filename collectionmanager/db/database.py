import argparse
import datetime
import logging
import os
import pathlib
import sys
import typing

from PyQt5 import QtCore
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, Session

from collectionmanager.db import models


class Database:
    """Manager for the database.
    """
    db_file_name = 'db.sqlite'

    def __init__(self):
        """Create the database.
        """
        self.engine = self._get_engine()

    def _get_engine(self) -> Engine:
        """Get the SQLAlchemy engine.

        :return: The SQLAlchemy engine.
        """
        logging.info("Creating SQLAlchemy engine")
        # Make sure the base directory exists
        base_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
        db_file_path = pathlib.Path(base_dir) / self.db_file_name
        db_file_path.parent.mkdir(parents=True, exist_ok=True)
        # Create engine
        engine = create_engine(f'sqlite:///{db_file_path}?check_same_thread=false')
        if not db_file_path.exists():
            # Crate the database if it does not exist
            logging.info("Database file does not exist, creating")
            models.Base.metadata.create_all(engine)

        return engine

    def rescan(self, force: bool = False):
        """Rescan the library.

        :param force: Force update file info
        """
        logging.info("Rescanning the database")

        for directory in self.directories():
            directory_path = pathlib.Path(directory.path)
            if datetime.datetime.fromtimestamp(os.path.getmtime(str(directory_path))) > directory.last_scanned or force:
                self.add_directory(directory.path, force)

    def add_directory(self, directory_path: str, force: bool = False):
        """Add a directory to the library.

        :param directory_path: The directory path.
        :param force: Force update file info
        """
        logging.info(f"Adding directory {directory_path} with force = {force}")

        # Check if the provided path exists in the file system
        directory_path = pathlib.Path(directory_path).resolve()
        if not directory_path.exists():
            raise ValueError(f"Path {directory_path} is does not exist")
        if not directory_path.is_dir():
            raise ValueError(f"Path {directory_path} is not a directory")

        # Check if the directory exists in the database
        session = sessionmaker(bind=self.engine)()
        directory = session.query(models.Directory).filter(models.Directory.path == str(directory_path)).first()
        if directory is None:
            logging.debug("Directory does not exist, creating")
            directory = models.Directory(path=str(directory_path))
            session.add(directory)
            session.commit()

        # Scan the directory
        logging.info(f"Scanning directory {directory_path}")
        for file_path in directory_path.glob('**/*.mp3'):
            self._process_file(session, directory_path, file_path, force)

        # Save the changes
        directory.last_scanned = datetime.datetime.now()
        session.commit()

    def remove_missing(self):
        """Remove all missing tracks from the library
        """
        logging.info(f"Removing missing files from the database")

        # Scan all tracks
        session = sessionmaker(bind=self.engine)()
        for track in self.tracks():
            track_path = pathlib.Path(track.directory.path, track.file_name)
            if not track_path.exists():
                logging.info(f"File {track_path} does not exist")
                logging.info(f"Deleting track")
                session.delete(track)

        session.commit()

    def directories(self) -> typing.List[models.Directory]:
        """Return the directories in the database.

        :return: A list with the directories.
        """
        session = sessionmaker(bind=self.engine)()

        return session.query(models.Directory).all()

    def artists(self, order_by: str = 'name') -> typing.List[models.Artist]:
        """Return the tracks in the database.

        :return: A list with the tracks.
        """
        session = sessionmaker(bind=self.engine)()

        return session.query(models.Artist).order_by(order_by)

    def tracks(self, artist: models.Artist = None, directory: models.Directory = None) -> typing.List[models.Track]:
        """Return the tracks in the database.

        :param artist: The artist to filter by.
        :param directory: The directory to filter by.
        :return: A list with the tracks.
        """
        session = sessionmaker(bind=self.engine)()
        query = session.query(models.Track)
        if directory is not None:
            query = query.filter(models.Track.directory == directory)
        if artist is not None:
            query = query.filter(models.Track.artist == artist)

        return query.all()

    @staticmethod
    def _process_file(session: Session, directory_path: pathlib.Path, file_path: pathlib.Path, force: bool = False):
        """Process a file.

        :param session: The database session to use.
        :param directory_path: The directory where the file belongs to.
        :param file_path: The file path.
        """
        # Get the file directory
        directory = session.query(models.Directory).filter(models.Directory.path == str(directory_path)).first()
        if directory is None:
            raise ValueError(f"Directory {directory_path} does not exits")

        # Get the track from the database if it already exists
        file_name = file_path.relative_to(directory_path)
        track = session.query(models.Track).filter(
            models.Track.directory == directory, models.Track.file_name == str(file_name)).first()
        if track is None:
            track = models.Track()
            track.directory = directory
            track.file_name = str(file_name)
        else:
            if track.last_scanned > datetime.datetime.fromtimestamp(os.path.getmtime(str(file_path))) and not force:
                logging.debug(f"File {file_path} already scanned")
                return

        # Populate track with ID3 information
        logging.info(f"Reading file information for {file_path}")
        track_info = models.Track.from_id3(file_path)

        # Add album artist information
        album_artist = None
        if track_info['album_artist']:
            album_artist = session.query(models.Artist).filter(models.Artist.name == track_info['album_artist']).first()
            if not album_artist:
                album_artist = models.Artist(name=track_info['album_artist'])
                session.add(album_artist)
            track.album_artist = album_artist
        else:
            logging.warning("Album artist is missing")

        # Add track artist information
        track_artist = None
        if track_info['track_artist']:
            track_artist = session.query(models.Artist).filter(models.Artist.name == track_info['track_artist']).first()
            if not track_artist:
                track_artist = models.Artist(name=track_info['track_artist'])
                session.add(track_artist)
            track.track_artist = track_artist
        else:
            logging.warning("Track artist is missing")

        # Add the album information
        if track_info['album'] and track_info['year']:
            album = session.query(models.Album).filter(
                models.Album.name == track_info['album'], models.Album.year == track_info['year']
            ).first()
            if not album:
                album = models.Album(name=track_info['album'], year=track_info['year'], artist=album_artist)
                session.add(album)
            track.album = album
        else:
            logging.warning("Album name and/or year is missing")

        # Add track information
        track.name = track_info['name']
        track.track_artist = track_artist
        track.album_artist = album_artist
        track.disk_number = track_info['disk_number']
        track.number = track_info['disk_number']
        track.length = track_info['length']
        track.encoder_info = track_info['encoder_info']
        track.last_scanned = datetime.datetime.now()

        session.add(track)


def main():
    """The main entry point of the module.
    """
    parser = argparse.ArgumentParser(description='Perform database operations')
    parser.add_argument('--log-level', default='INFO', help='The logging level')
    parser.add_argument('--force', type=bool, default=False, help='If true, the action is forced without checking '
                                                                  'modified times')
    parser.add_argument('action', help='The action to perform.')
    parser.add_argument('files', nargs='*', help='The files for which to perform the action')
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=args.log_level.upper())
    d = Database()
    if args.action == 'rescan':
        d.rescan(args.force)
    elif args.action == 'remove_missing':
        d.remove_missing()
    elif args.action == 'add_directories':
        for directory in args.files:
            d.add_directory(directory, args.force)
    else:
        raise ValueError(f"Unknown action {args.action}")


if __name__ == '__main__':
    main()
