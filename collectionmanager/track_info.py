import mutagen


class TrackInfo:
    """Holds information about tracks
    """
    def __init__(self, file_name):
        """Track constructor

        :param file_name: The absolute file name
        """
        self.artist = None
        self.album = None
        self.name = None
        self.track_number = None

        self._parse(mutagen.File(file_name))

    def _parse(self, file_info):
        self.artist = file_info['TALB'][0] if 'TALB' in file_info else None
        self.album = file_info['TPE1'][0] if 'TPE1' in file_info else None
        self.name = file_info['TIT2'][0] if 'TIT2' in file_info else None
        self.number = int(file_info['TRCK'][0]) if 'TALB' in file_info else None
        self.year = int(str(file_info['TDRC'][0])) if 'TDRC' in file_info else None
