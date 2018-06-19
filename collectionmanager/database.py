import logging
import os.path
import pathlib
import sqlite3

import collectionmanager.track_info as track_info


class Database:
    """The track database
    """
    def __init__(self, config_dir):
        """Constructor for the database object.
        """
        self.conn = Database._create_connection(config_dir)

    @staticmethod
    def _create_connection(config_dir):
        """Create the connection to the database that holds the music library information.

        :return: The database connection.
        """
        db_file = pathlib.Path(config_dir, 'db.sqlite')
        # Check if the file exists
        if not db_file.exists():
            # Make sure the parent directory exists
            if not db_file.parent.exists():
                db_file.parent.mkdir()

            # Create the database
            conn = sqlite3.connect(str(db_file), check_same_thread=False)
            try:
                Database._create_schema(conn)
            except Exception:
                # Creation failed, delete the file
                os.remove(str(db_file))
                raise
        else:
            # File exists, create a connection
            conn = sqlite3.connect(str(db_file), check_same_thread=False)

        return conn

    @staticmethod
    def _create_schema(conn):
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
            logging.info('Scanning directory %s', directory)
            cursor.execute("INSERT INTO directory(path) VALUES (?)", (directory, ))
            directory_id = cursor.lastrowid
            # Scan the directory for files
            for root, relative_path, file_name in Database._scan_directory(directory):
                self._process_file(directory_id, directory, relative_path, file_name)
            logging.info('Scanning directory %s finished', directory)
        finally:
            cursor.close()

    def save(self):
        """Save the changes to the database
        """
        self.conn.commit()

    def track_data(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT d.path AS directory_path, t.file_name, ar.name AS artist_name, al.name AS album_name,
                       t.number, t.name AS track_name
                FROM track t
                JOIN directory d ON t.directory_id = d.id
                JOIN album al ON al.id = t.album_id
                JOIN artist ar ON ar.id = al.artist_id
                ORDER BY d.path, t.file_name
            """)

            return list(cursor)
        finally:
            cursor.close()

    def _process_file(self, directory_id, directory, relative_path, file_name):
        """Process a file.

        :param directory_id: The identifier of the root directory.
        :param directory: The directory to add.
        :param relative_path: The path of the file relative to the root directory.
        :param file_name: The file name.
        """
        cursor = self.conn.cursor()
        try:
            logging.debug('Processing file %s', os.path.join(relative_path, file_name))
            file_path = os.path.join(directory, relative_path, file_name)
            track = track_info.TrackInfo(file_path)

            # Save the artist
            cursor.execute("SELECT id FROM artist WHERE name = ?", (track.artist, ))
            artist_id = cursor.fetchone()
            if artist_id is None:
                cursor.execute("INSERT INTO artist(name) VALUES (?)", (track.artist, ))
                artist_id = cursor.lastrowid
            else:
                artist_id = artist_id[0]

            # Save the album
            cursor.execute("SELECT id FROM album WHERE name = ? AND artist_id = ?", (track.album, artist_id))
            album_id = cursor.fetchone()
            if album_id is None:
                cursor.execute("""
                    INSERT INTO album(artist_id, name, year) VALUES (?, ?, ?)
                """, (artist_id, track.album, track.year))
                album_id = cursor.lastrowid
            else:
                album_id = album_id[0]

            # Insert the file information
            cursor.execute(
                """
                  INSERT INTO track(directory_id, album_id, name, number, file_name)
                  VALUES (?, ?, ?, ?, ?)
                """,
                (directory_id, album_id, track.name, track.track_number, os.path.join(relative_path, file_name))
            )
            logging.debug('Processing file %s finished', os.path.join(relative_path, file_name))
        finally:
            cursor.close()

    def count_albums_by_year(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT year, COUNT(*)
                FROM album
                GROUP BY year
                ORDER BY year
            """)

            return cursor.fetchall()
        finally:
            cursor.close()

    def count_by_decade(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT substr(year, 3, 1) || '0', COUNT(*)
                FROM album
                GROUP BY substr(year, 3, 1) || '0'
                ORDER BY year
            """)

            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def _scan_directory(directory):
        """Scan a directory for new or updated files.

        :param directory: The directory to scan.
        """
        for current_root_name, _, files in os.walk(directory):
            current_root = pathlib.Path(current_root_name)
            for file_name in files:
                yield directory, str(current_root.relative_to(directory)), file_name
