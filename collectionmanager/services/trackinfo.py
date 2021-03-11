"""Track information
"""
import mutagen


class TrackInfo:
    """Holds information about a music track
    """
    def __init__(self, file_path: str):
        """Load ID3 track information from an MP3 file.

        :param file_path: The file path.
        :return: A dictionary with the track information.
        """
        self.file_info = mutagen.File(file_path)

        self.name = self.file_info['TIT2'][0] if 'TIT2' in self.file_info else None
        self.artist = self.file_info['TPE1'][0] if 'TPE1' in self.file_info else None
        self.album_artist = self.file_info['TPE2'][0] if 'TPE2' in self.file_info else None
        self.album = self.file_info['TALB'][0] if 'TALB' in self.file_info else None
        self.year = self.file_info['TDRC'][0].get_text() if 'TDRC' in self.file_info else None
        self.genre = self.file_info['TCON'][0] if 'TCON' in self.file_info else None
        self.album_art = self.file_info['APIC:'] if 'APIC:' in self.file_info else None
        self.number = self.file_info['TRCK'][0] if 'TRCK' in self.file_info else None
        self.disk_number = self.file_info['TPOS'][0] if 'TPOS' in self.file_info else None
