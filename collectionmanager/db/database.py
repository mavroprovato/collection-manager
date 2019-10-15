import logging
import pathlib

import mutagen
import sqlalchemy.orm

from collectionmanager.db import models


class Database:
    """Manager for the database.
    """
    db_file_name = 'db.sqlite'

    def __init__(self, base_dir: str):
        """Crate the database.

        :param base_dir:
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

    def scan_directory(self, directory_path: str):
        """Scan a directory.

        :param directory_path: The directory path.
        """
        # Check if the provided path is an existing directory
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

    @staticmethod
    def _process_file(session, directory_path: pathlib.Path, file_path: pathlib.Path):
        """Process a file.

        :param directory_path: The directory where the file belongs to.
        :param file_path: The file path.
        """
        logging.info(f"Scanning file {file_path}")
        # Get the file directory
        directory = session.query(models.Directory).filter(models.Directory.path == str(directory_path)).first()
        if directory is None:
            raise ValueError(f"Directory {directory_path} does not exits")

        # Get the track if it already exist
        file_name = file_path.relative_to(directory_path)
        track = session.query(models.Track).filter(
            models.Track.directory == directory, models.Track.file_name == str(file_name)).first()
        if track is None:
            track = models.Track()
            track.directory = directory
            track.file_name = str(file_name)

        # Populate track with ID3 information
        file_info = mutagen.File(file_path)

        # Add artist information
        artist_name = file_info['TPE1'][0] if 'TPE1' in file_info else None
        artist = None
        if artist_name:
            artist = session.query(models.Artist).filter(models.Artist.name == artist_name).first()
            if not artist:
                artist = models.Artist(name=artist_name)
                session.add(artist)
            track.artist = artist
        else:
            logging.warning("Album artist is missing")

        # Add the album information
        album_name = file_info['TALB'][0] if 'TALB' in file_info else None
        album_year = file_info['TDRC'][0].get_text() if 'TDRC' in file_info else None
        if album_name and album_year:
            album = session.query(models.Album).filter(
                models.Album.name == album_name, models.Album.year == album_year
            ).first()
            if not album:
                album = models.Album(name=album_name, year=album_year, artist=artist)
                session.add(album)
            track.album = album
        else:
            logging.warning("Album information is missing")

        # Add track information
        track.name = file_info['TIT2'][0] if 'TIT2' in file_info else None
        track.disk_number = file_info['TPOS'][0] if 'TPOS' in file_info else None
        track.number = file_info['TRCK'][0] if 'TRCK' in file_info else None

        session.add(track)

    def tracks(self):
        return []


def main():
    logging.basicConfig(level=logging.DEBUG)
    import os
    d = Database(os.path.expanduser('~/.local/share/collection-manager'))
    d.scan_directory(os.path.expanduser('~/Music'))


if __name__ == '__main__':
    main()
