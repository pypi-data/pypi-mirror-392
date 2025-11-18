import logging

from .request import Requester
from .robots import RobotsParser
from .exception import GrabpyException
from .io import FileParts
from functools import lru_cache


class Grabber:
    def __init__(self, useragent: str, retries: int = 3) -> None:
        """Set retries to -1 to retry indefinitely"""

        self.robots_parser = RobotsParser(useragent)
        self.requester = Requester(retries)

    def __enter__(self) -> 'Grabber':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return

    @lru_cache(maxsize=8, typed=True)
    def get(self, url: str) -> bytes:
        parser = self.robots_parser.get_parser(url)

        if not self.robots_parser.can_scrape(parser, url):
            return b''

        delay: float = self.robots_parser.scrape_delay(parser)

        return self.requester.fetch(url, delay=delay)

    def download(self, url: str, fp: str) -> bool:
        parser = self.robots_parser.get_parser(url)

        if not self.robots_parser.can_scrape(parser, url):
            return False

        delay: float = self.robots_parser.scrape_delay(parser)

        try:
            content_length: int = self.requester.get_content_length(url, delay)

            with FileParts(fp, content_length) as file:
                for offset, chunk in self.requester.stream(url, content_length, delay):
                    file.write(offset, chunk)
        except GrabpyException as err:
            logging.error('%s', err)
            return False
        else:
            return True
