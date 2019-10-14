import typing


class DiscogsService:
    def fetch_album_art(self, artist: str, album: str) -> typing.Optional[typing.Tuple[bytes, str]]:
        raise NotImplementedError
