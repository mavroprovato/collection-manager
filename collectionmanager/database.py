import logging
import pathlib

import sqlalchemy

from collectionmanager import models


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

    def _get_engine(self) -> sqlalchemy.engine.base.Engine:
        """Get the SQLAlchemy engine.

        :return: The SQLAlchemy engine.
        """
        logging.info('Creating SQLAlchemy engine')
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


def main():
    import os
    d = Database(os.path.expanduser('~/.local/share/collection-manager'))


if __name__ == '__main__':
    main()

