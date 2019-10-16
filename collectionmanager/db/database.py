import datetime
import logging
import pathlib
import typing

import mutagen
import sqlalchemy.orm
from sqlalchemy.orm import Session

from collectionmanager.db import models


class Database:
    """Manager for the database.
    """
    db_file_name = 'db.sqlite'

    def __init__(self, base_dir: str):
        """Create the database.

        :param base_dir: The base directory where the database file will be created.
        """
        self.base_dir = base_dir
        self.engine = self._get_engine()
        self.session_maker = sqlalchemy.orm.sessionmaker(bind=self.engine)

    def _get_engine(self) -> sqlalchemy.engine.base.Engine:
        """Get the SQLAlchemy engine.

        :return: The SQLAlchemy engine.
        """
        logging.info("Creating SQLAlchemy engine")
        # Make sure the base directory exists
        db_file_path = pathlib.Path(self.base_dir) / self.db_file_name
        db_file_path.parent.mkdir(parents=True, exist_ok=True)
        # Create engine
        engine = sqlalchemy.create_engine(f'sqlite:///{db_file_path}')
        if not db_file_path.exists():
            # Crate the database if it does not exist
            logging.info("Database file does not exist, creating")
            models.Base.metadata.create_all(engine)

        return engine

    def add_directory(self, directory_path: str):
        """Add a directory to the library.

        :param directory_path: The directory path.
        """
        # Check if the provided path exists
        directory_path = pathlib.Path(directory_path).resolve()
        if not directory_path.exists():
            raise ValueError(f"Path {directory_path} is does not exist")
        if not directory_path.is_dir():
            raise ValueError(f"Path {directory_path} is not a directory")

        # Check if the directory exists in the database
        session = self.session_maker()
        directory = session.query(models.Directory).filter(models.Directory.path == str(directory_path)).first()
        if directory is None:
            logging.debug("Directory does not exist, creating")
            directory = models.Directory(path=str(directory_path))
            session.add(directory)
            session.commit()

        # Scan the directory
        logging.info(f"Scanning directory {directory_path}")
        for file_path in directory_path.glob('**/*.mp3'):
            self._process_file(session, directory_path, file_path)
        session.commit()

    def tracks(self) -> typing.List[models.Track]:
        """Return the tracks in the database.

        :return: A list with the tracks.
        """
        session = self.session_maker()

        return session.query(models.Track).all()

    def _process_file(self, session: Session, directory_path: pathlib.Path, file_path: pathlib.Path):
        """Process a file.

        :param session: The database session to use.
        :param directory_path: The directory where the file belongs to.
        :param file_path: The file path.
        """
        logging.info(f"Scanning file {file_path}")
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

        # Populate track with ID3 information
        track_info = self._get_track_info(file_path)

        # Add artist information
        artist = None
        if track_info['artist_name']:
            artist = session.query(models.Artist).filter(models.Artist.name == track_info['artist_name']).first()
            if not artist:
                artist = models.Artist(name=track_info['artist_name'])
                session.add(artist)
            track.artist = artist
        else:
            logging.warning("Album artist is missing")

        # Add the album information
        if track_info['album_name'] and track_info['album_year']:
            album = session.query(models.Album).filter(
                models.Album.name == track_info['album_name'], models.Album.year == track_info['album_year']
            ).first()
            if not album:
                album = models.Album(name=track_info['album_name'], year=track_info['album_year'], artist=artist)
                session.add(album)
            track.album = album
        else:
            logging.warning("Album name and/or year is missing")

        # Add track information
        track.name = track_info['name']
        track.disk_number = track_info['disk_number']
        track.number = track_info['disk_number']
        track.last_scanned = datetime.datetime.now()

        session.add(track)

    @staticmethod
    def _get_track_info(file_path: pathlib.Path) -> dict:
        """Get the track information from the ID3 information of the file.

        :param file_path: The file path.
        :return: A dictionary with the track information.
        """
        file_info = mutagen.File(file_path)

        return {
            'artist_name': file_info['TPE1'][0] if 'TPE1' in file_info else None,
            'album_name': file_info['TALB'][0] if 'TALB' in file_info else None,
            'album_year': file_info['TDRC'][0].get_text() if 'TDRC' in file_info else None,
            'name': file_info['TIT2'][0] if 'TIT2' in file_info else None,
            'disk_number': file_info['TPOS'][0] if 'TPOS' in file_info else None,
            'number': file_info['TRCK'][0] if 'TRCK' in file_info else None
        }


def main():
    logging.basicConfig(level=logging.DEBUG)
    import os
    d = Database(os.path.expanduser('~/.local/share/collection-manager'))
    d.add_directory(os.path.expanduser('~/Music'))


if __name__ == '__main__':
    main()
