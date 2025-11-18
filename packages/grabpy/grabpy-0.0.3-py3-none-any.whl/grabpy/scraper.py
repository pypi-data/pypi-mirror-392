from .request import Requester
from .robots import RobotsParser
from functools import lru_cache
from uuid import uuid4
import shutil


class Grabber:
    def __init__(self, useragent: str, retries: int = 3, verbose: bool = False) -> None:
        """Set retries to -1 to retry indefinitely"""

        self.robots_parser = RobotsParser(useragent)
        self.requester = Requester(retries, verbose)

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
        temp: str = f'{uuid4()}.parts'

        with open(temp, 'wb') as f:
            self.requester.stream(url, delay, f)

        shutil.move(temp, fp)

        return True
