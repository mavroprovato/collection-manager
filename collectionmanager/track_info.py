import mutagen


class TrackInfo:
    """Holds information about tracks
    """
    def __init__(self, file_name):
        """Track constructor

        :param file_name: The absolute file name
        """
        self.file_info = mutagen.File(file_name)

    @property
    def name(self):
        return self.file_info['TIT2'][0] if 'TIT2' in self.file_info else None

    @property
    def album(self):
        return self.file_info['TALB'][0] if 'TALB' in self.file_info else None

    @property
    def artist(self):
        return self.file_info['TPE1'][0] if 'TPE1' in self.file_info else None

    @property
    def album_artist(self):
        return self.file_info['TPE2'][0] if 'TPE2' in self.file_info else None

    @property
    def disk_number(self):
        return self.file_info['TPOS'][0] if 'TPOS' in self.file_info else None

    @property
    def track_number(self):
        return self.file_info['TRCK'][0] if 'TRCK' in self.file_info else None

    @property
    def year(self):
        return self.file_info['TDRC'][0].get_text() if 'TDRC' in self.file_info else None

    @property
    def album_art(self):
        return self.file_info['APIC:'] if 'APIC:' in self.file_info else None

    @property
    def length(self):
        return self.file_info.info.length

    @property
    def bitrate(self):
        return self.file_info.info.bitrate

    @property
    def bitrate_mode(self):
        return self.file_info.info.bitrate_mode

    @property
    def sample_rate(self):
        return self.file_info.info.sample_rate

    @property
    def encoder_info(self):
        return self.file_info.info.encoder_info
