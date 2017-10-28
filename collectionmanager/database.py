import os.path
import pathlib
import sqlite3

# The file name of the database that holds the track information.
DB_FILENAME = os.path.expanduser('~/.collection-manager/db.sqlite')

# The create scripts for the database.
CREATE_DDL = (
    """
    CREATE TABLE directory (
        id INTEGER PRIMARY KEY,
        path TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE path (
        id INTEGER PRIMARY KEY,
        directory_id INTEGER,
        relative_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        FOREIGN KEY(directory_id) REFERENCES directory(id) ON DELETE CASCADE
    )
    """,
)


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
            Database.create_schema(conn)
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
            for ddl in CREATE_DDL:
                cursor.execute(ddl)
        finally:
            cursor.close()

    def add_directory(self, directory):
        """Add a directory to the database.

        :param directory: Full path to the directory to be added.
        """
        cursor = self.conn.cursor()
        try:
            # Insert the directory
            cursor.execute("""
              INSERT INTO directory(path) VALUES (?)
            """, (directory, ))
            directory_id = cursor.lastrowid
            # Scan the directory for files
            for root, relative_path, file_name in Database._scan_directory(directory):
                self.process_file(directory_id, file_name, relative_path)
        finally:
            cursor.close()

    def process_file(self, directory_id, file_name, relative_path):
        """Process a file.

        :param directory_id: The identifier of the root directory.
        :param relative_path: The path of the file relative to the root directory.
        :param file_name: The file name.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO path(directory_id, relative_path, file_name) VALUES (?, ?, ?)
            """, (directory_id, relative_path, file_name))
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
