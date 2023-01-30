"""Track information
"""
import dataclasses
import enum
import pathlib

import mutagen
import mutagen.mp3
import mutagen.flac


class FileType(enum.Enum):
    """Enumeration for supported file types
    """
    MP3 = 'mp3'
    FLAC = 'flac'


@dataclasses.dataclass
class AlbumArt:
    """Class holding album art information
    """
    mime: str
    data: bytes


@dataclasses.dataclass
class TrackInfo:
    """Class holding the track information
    """
    type = FileType = None
    artist: str = None
    album_artist: str = None
    album: str = None
    year: int = None
    disk_number: int = None
    title: str = None
    number: int = None
    file_info: dict = None
    album_art: AlbumArt = None

    @staticmethod
    def from_file(file: str | pathlib.Path) -> 'TrackInfo':
        """Read the track information from a file.

        :param file: The file.
        :return: The track information
        """
        track_info = TrackInfo()
        track_info.file_info = mutagen.File(file)

        if isinstance(track_info.file_info, mutagen.mp3.MP3):
            track_info.type = FileType.MP3
            track_info.artist = track_info.file_info['TPE1'][0] if 'TPE1' in track_info.file_info else None
            track_info.album_artist = track_info.file_info['TPE2'][0] if 'TPE2' in track_info.file_info else None
            track_info.album = track_info.file_info['TALB'][0] if 'TALB' in track_info.file_info else None
            if 'TDRC' in track_info.file_info:
                try:
                    track_info.year = int(str(track_info.file_info['TDRC'][0]))
                except ValueError:
                    pass
            if 'TPOS' in track_info.file_info:
                try:
                    track_info.disk_number = int(str(track_info.file_info['TPOS'][0]))
                except ValueError:
                    pass
            if 'TRCK' in track_info.file_info:
                try:
                    track_info.number = int(str(track_info.file_info['TRCK'][0]))
                except ValueError:
                    pass
            track_info.title = track_info.file_info['TIT2'][0] if 'TIT2' in track_info.file_info else None
            if 'APIC:' in track_info.file_info:
                track_info.album_art = AlbumArt(track_info.file_info['APIC:'].mime, track_info.file_info['APIC:'].data)
        elif isinstance(track_info.file_info, mutagen.flac.FLAC):
            track_info.type = FileType.FLAC
            track_info.artist = track_info.file_info['artist'][0] if 'artist' in track_info.file_info else None
            track_info.album_artist = track_info.file_info['albumartist'][0] if 'albumartist' in track_info.file_info \
                else None
            track_info.album = track_info.file_info['album'][0] if 'album' in track_info.file_info else None
            if 'date' in track_info.file_info:
                try:
                    track_info.year = int(str(track_info.file_info['date'][0]))
                except ValueError:
                    pass
            if 'discnumber' in track_info.file_info:
                try:
                    track_info.disk_number = int(str(track_info.file_info['discnumber'][0]))
                except ValueError:
                    pass
            if 'tracknumber' in track_info.file_info:
                try:
                    track_info.number = int(str(track_info.file_info['tracknumber'][0]))
                except ValueError:
                    pass
            track_info.title = track_info.file_info['title'][0] if 'title' in track_info.file_info else None
            if track_info.file_info.pictures:
                track_info.album_art = AlbumArt(
                    track_info.file_info.pictures[0].mime, track_info.file_info.pictures[0].data)

        return track_info
