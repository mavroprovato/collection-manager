import logging
import os.path
import mutagen.id3
import pathlib
import sqlite3

# The file name of the database that holds the track information.
DB_FILENAME = os.path.expanduser('~/.collection-manager/db.sqlite')


class Database:
    """
    The song database
    """
    def __init__(self):
        """Constructor for the database object.
        """
        self.conn = Database.__create_connection()

    @staticmethod
    def __create_connection():
        """Create the connection to the database that holds the music library information.

        :return: The database connection.
        """
        db_file = pathlib.Path(DB_FILENAME)
        # Check if the file exists
        if not db_file.exists():
            # Make sure the parent directory exists
            if not db_file.parent.exists():
                db_file.parent.mkdir()

            # Create the database
            conn = sqlite3.connect(str(db_file))
            try:
                Database.create_schema(conn)
            except Exception:
                # Creation failed, delete the file
                os.remove(str(db_file))
                raise
        else:
            # File exists, create a connection
            conn = sqlite3.connect(str(db_file))

        return conn

    @staticmethod
    def create_schema(conn):
        """Create the database schema.

        :param conn: The database connection.
        """
        cursor = conn.cursor()
        try:
            with open(os.path.join(os.path.dirname(__file__), 'resources/db_schema.sql')) as f:
                current_sql = ''
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('--'):
                        continue
                    current_sql += line
                    if line[-1] == ';':
                        cursor.execute(current_sql)
                        current_sql = ''
        finally:
            cursor.close()

    def add_directory(self, directory):
        """Add a directory to the database.

        :param directory: Full path to the directory to be added.
        """
        cursor = self.conn.cursor()
        try:
            # Insert the directory
            cursor.execute("INSERT INTO directory(path) VALUES (?)", (directory, ))
            directory_id = cursor.lastrowid
            # Scan the directory for files
            logging.info('Scanning directory %s', directory)
            for root, relative_path, file_name in Database._scan_directory(directory):
                self.process_file(directory_id, directory, relative_path, file_name)
            logging.info('Scanning directory %s finished', directory)
        finally:
            cursor.close()

    def process_file(self, directory_id, directory, relative_path, file_name):
        """Process a file.

        :param directory_id: The identifier of the root directory.
        :param directory:
        :param relative_path: The path of the file relative to the root directory.
        :param file_name: The file name.
        """
        cursor = self.conn.cursor()
        try:
            logging.info('Processing file %s/%s', relative_path, file_name)
            id3 = mutagen.id3.ID3(os.path.join(directory, relative_path, file_name))
            # Get the artist
            if id3.getall('TPE1'):
                artist = str(id3.getall('TPE1')[0])
            else:
                artist = None
            cursor.execute("SELECT id FROM artist WHERE name = ?", (artist, ))
            artist_id = cursor.fetchone()
            if artist_id is None:
                cursor.execute("INSERT INTO artist(name) VALUES (?)", (artist, ))
                artist_id = cursor.lastrowid
            else:
                artist_id = artist_id[0]

            # Get the album name
            if id3.getall('TALB'):
                album_name = str(id3.getall('TALB')[0])
            else:
                album_name = None
            # Get the year
            if id3.getall('TDRC'):
                track_year = int(str(id3.getall('TDRC')[0]))
            else:
                track_year = None
            cursor.execute("SELECT id FROM album WHERE name = ? AND artist_id = ?", (album_name, artist_id))
            album_id = cursor.fetchone()
            if album_id is None:
                cursor.execute("""
                    INSERT INTO album(artist_id, name, year) VALUES (?, ?, ?)
                """, (artist_id, album_name, track_year))
                album_id = cursor.lastrowid
            else:
                album_id = album_id[0]

            # Get the track name
            if id3.getall('TIT2'):
                track_name = str(id3.getall('TIT2')[0])
            else:
                track_name = None

            # Get the track number
            if id3.getall('TRCK'):
                try:
                    track_number = int(str(id3.getall('TRCK')[0]))
                except ValueError:
                    track_number = None
            else:
                track_number = None

            # Insert the file information
            cursor.execute(
                """
                  INSERT INTO file(directory_id, album_id, relative_path, file_name, track_number, track_name)
                  VALUES (?, ?, ?, ?, ?, ?)
                """,
                (directory_id, album_id, relative_path, file_name, track_number, track_name)
            )
        finally:
            cursor.close()

    def save(self):
        """Save the changes to the database
        """
        self.conn.commit()

    @staticmethod
    def _scan_directory(directory):
        """Scan a directory for new or updated files.

        :param directory: The directory to scan.
        """
        for current_root_name, _, files in os.walk(directory):
            current_root = pathlib.Path(current_root_name)
            for file_name in files:
                yield directory, str(current_root.relative_to(directory)), file_name
