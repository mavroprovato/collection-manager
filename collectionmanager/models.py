"""Module that contains the models
"""
import sqlalchemy.ext.declarative
import sqlalchemy.orm

Base = sqlalchemy.ext.declarative.declarative_base()


class Directory(Base):
    """A directory that is scanned for music files
    """
    __tablename__ = 'directories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    path = sqlalchemy.Column(sqlalchemy.String)


class Artist(Base):
    """Information about an artist.
    """
    __tablename__ = 'artists'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)


class Album(Base):
    """Information about an album.
    """
    __tablename__ = 'albums'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.Integer)
    artist_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))


class Track(Base):
    """Information about a track.
    """
    __tablename__ = 'tracks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    disk_number = sqlalchemy.Column(sqlalchemy.Integer)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    file_name = sqlalchemy.Column(sqlalchemy.String)
    directory_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('directories.id'))
    artist_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))
    album_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('albums.id'))

