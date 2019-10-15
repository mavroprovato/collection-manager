import matplotlib.pyplot as plt
import os

import collectionmanager.db.database as database


def main():
    db = database.Database(os.path.expanduser("~/.local/share/collection-manager"))
    count_albums_by_decade(db)


def count_albums_by_year(db):
    count_by_year = db.count_albums_by_year()
    plt.bar(list(x[0] for x in count_by_year), list(x[1] for x in count_by_year))
    plt.show()


def count_albums_by_decade(db):
    count_by_decade = db.count_by_decade()
    plt.bar(list(x[0] for x in count_by_decade), list(x[1] for x in count_by_decade))
    plt.show()


if __name__ == '__main__':
    main()
