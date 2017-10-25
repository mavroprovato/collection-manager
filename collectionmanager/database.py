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
        if not db_file.exists():
            # Make sure the parent directory exists
            if not db_file.parent.exists():
                db_file.parent.mkdir()
            # Create the database
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            try:
                for ddl in CREATE_DDL:
                    cursor.execute(ddl)
            finally:
                cursor.close()
        else:
            # File exists, create a connection
            conn = sqlite3.connect(str(db_file))

        return conn

    def add_directory(self, directory):
        """Add a directory to the database.

        :param directory: Full path to the directory to be added.
        """
        cursor = self.conn.cursor()
        # Insert the directory
        try:
            cursor.execute('INSERT INTO directory(path) VALUES (?)', (directory, ))
        finally:
            cursor.close()

    def save(self):
        """Save the changes to the database
        """
        self.conn.commit()
