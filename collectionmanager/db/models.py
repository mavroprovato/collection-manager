"""Module that contains the models
"""
import pathlib

import mutagen
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
    length = sqlalchemy.Column(sqlalchemy.Float)
    file_name = sqlalchemy.Column(sqlalchemy.String)
    encoder_info = sqlalchemy.Column(sqlalchemy.JSON)
    last_scanned = sqlalchemy.Column(sqlalchemy.DateTime)

    directory_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('directories.id'))
    track_artist_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))
    album_artist_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))
    album_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('albums.id'))

    directory = sqlalchemy.orm.relationship('Directory')
    track_artist = sqlalchemy.orm.relationship('Artist', foreign_keys=[track_artist_id])
    album_artist = sqlalchemy.orm.relationship('Artist', foreign_keys=[album_artist_id])
    album = sqlalchemy.orm.relationship('Album')

    @staticmethod
    def from_id3(file_path: pathlib.Path) -> dict:
        """Get the track information from the ID3 information of the file.

        :param file_path: The file path.
        :return: A dictionary with the track information.
        """
        file_info = mutagen.File(file_path)

        return {
            'track_artist': file_info['TPE1'][0] if 'TPE1' in file_info else None,
            'album_artist': file_info['TPE2'][0] if 'TPE2' in file_info else None,
            'album': file_info['TALB'][0] if 'TALB' in file_info else None,
            'year': file_info['TDRC'][0].get_text() if 'TDRC' in file_info else None,
            'album_art': file_info['APIC:'] if 'APIC:' in file_info else None,
            'name': file_info['TIT2'][0] if 'TIT2' in file_info else None,
            'disk_number': file_info['TPOS'][0] if 'TPOS' in file_info else None,
            'number': file_info['TRCK'][0] if 'TRCK' in file_info else None,
            'length': file_info.info.length,
            'encoder_info': {
                'bitrate': file_info.info.bitrate,
                'bitrate_mode': str(file_info.info.bitrate_mode),
                'sample_rate': file_info.info. sample_rate,
                'encoder_info': file_info.info.encoder_info,
            }
        }
