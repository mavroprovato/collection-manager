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

    albums = sqlalchemy.orm.relationship('Album', back_populates='artist')


class Album(Base):
    """Information about an album.
    """
    __tablename__ = 'albums'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.Integer)
    artist_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))

    artist = sqlalchemy.orm.relationship('Artist', back_populates='albums')
    tracks = sqlalchemy.orm.relationship('Track', back_populates='album')


class Track(Base):
    """Information about a track.
    """
    __tablename__ = 'tracks'
    __table_args__ = (sqlalchemy.Index('idx_directory_file_name', 'directory_id', 'file_name'), )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    disk_number = sqlalchemy.Column(sqlalchemy.Integer)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    file_name = sqlalchemy.Column(sqlalchemy.String)
    last_scanned = sqlalchemy.Column(sqlalchemy.DateTime)

    directory_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('directories.id'))
    artist_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))
    album_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('albums.id'))

    directory = sqlalchemy.orm.relationship('Directory')
    artist = sqlalchemy.orm.relationship('Artist')
    album = sqlalchemy.orm.relationship('Album')

