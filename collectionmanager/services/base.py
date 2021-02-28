import abc
import collections
import logging

logger = logging.getLogger(__name__)


class BaseService(abc.ABC):
    """Abstract base class for services
    """
    def __init__(self):
        self._release_cache = collections.defaultdict(dict)

    def album_art(self, artist: str, album: str):
        """Get the album art for a release.

        :param artist: The artist name.
        :param album: The album art.
        :return:
        """
        album_art = self._release_cache.get((artist, album), {}).get('album_art')
        if album_art:
            logger.debug("Album art found in cache")
            return album_art
        else:
            logger.info("Fetching album art for artist '%s' and album '%s' from service", artist, album)
            album_art = self.fetch_album_art(artist, album)
            if album_art:
                logger.info("Album art found")
                self._release_cache[(artist, album)]['album_art'] = album_art

                return album_art
            else:
                logger.warning("Album art not found")

    @abc.abstractmethod
    def fetch_album_art(self, artist: str, album: str) -> bytes:
        pass
