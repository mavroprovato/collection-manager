import mutagen


class TrackInfo:
    """Holds information about tracks
    """
    def __init__(self, file_name):
        """Track constructor

        :param file_name: The absolute file name
        """
        self.name = None
        self.album = None
        self.artist = None
        self.album_artist = None
        self.disc_number = None
        self.track_number = None
        self.year = None
        self.album_art = None

        file_info = mutagen.File(file_name)
        self._parse(file_info)
        self.info = file_info.info

    def _parse(self, file_info):
        self.name = file_info['TIT2'][0] if 'TIT2' in file_info else None
        self.album = file_info['TALB'][0] if 'TALB' in file_info else None
        self.artist = file_info['TPE1'][0] if 'TPE1' in file_info else None
        self.album_artist = file_info['TPE2'][0] if 'TPE2' in file_info else None
        self.disc_number = file_info['TPOS'][0] if 'TPOS' in file_info else None
        self.track_number = file_info['TRCK'][0] if 'TRCK' in file_info else None
        self.year = str(file_info['TDRC'][0]) if 'TDRC' in file_info else None
        self.album_art = file_info['APIC:'] if 'APIC:' in file_info else None
