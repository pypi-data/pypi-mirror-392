import logging
import os
import time
from queue import Queue, Empty
from threading import Thread
from typing import Callable

import requests
from requests import Response
from requests.exceptions import ChunkedEncodingError, ConnectionError, StreamConsumedError, Timeout

from .exception import GrabpyException, HTTPError, HTTPNotFoundError, HTTPTimeoutError

logger = logging.getLogger(__name__)


class Requester:
    def __init__(self, retries: int):
        self.retries = retries

    @staticmethod
    def _int_to_unit(i: int) -> str:
        gb: int = 1_073_741_824
        mb: int = 1_048_576
        kb: int = 1024

        if i >= gb:
            return f'{(i / gb):.2f}Gb'
        elif i >= mb:
            return f'{(i / mb):.2f}Mb'
        elif i >= kb:
            return f'{(i / kb):.2f}Kb'
        else:
            return str(i)

    @staticmethod
    def _get_chunk_size(content_length: int | None) -> int:
        mb = 1024 * 1024

        if not content_length:
            return 1 * mb

        return max(1 * mb, min(content_length // 100, 16 * mb))

    @staticmethod
    def _request(
        callback: Callable,
        retries: int,
        delay: float,
        url: str,
        stream: bool,
        timeout: float | tuple[float, float],
        headers: dict[str, str]
    ) -> Response:
        """All requests go through this function which respects the wishes of the robots file"""

        ok: int = 206 if stream else 200
        not_found: int = 404

        while retries:
            time.sleep(delay)

            try:
                response: Response = callback(url, stream=stream, timeout=timeout, headers=headers)
            except Timeout:
                retries -= 1
                delay = (delay + 1) * 2

                logger.debug(
                    'Timed out. "%s" %ld %ld',
                    url,
                    retries,
                    delay
                )
            else:
                if response.status_code == ok:
                    return response

                if response.status_code == not_found:
                    raise HTTPNotFoundError(url)

        raise HTTPTimeoutError(url, timeout)

    @staticmethod
    def _iter_content(response: Response, chunk_size: int) -> bytes:
        try:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue

                yield chunk
        except (ChunkedEncodingError, ConnectionError) as err:
            logger.exception('%s', err)
            raise

    @staticmethod
    def _get_content_ranges(content_length: int | None, chunk_size: int) -> tuple[int, Queue]:
        queue = Queue()
        end: int = -1
        limit: int = content_length - 1
        count: int = 0

        while end < limit:
            start = end + 1
            end = min(start + chunk_size, limit)
            count += 1
            queue.put((start, end))

        return count, queue

    def _download_worker(self, output: Queue, ranges: Queue, chunk_size: int, url: str, delay: float) -> None:
        while True:
            try:
                start, end = ranges.get_nowait()
            except Empty:
                break

            logger.debug('Streaming "%s" [%ld:%ld]', url, start, end)

            headers = {'Range': f'bytes={start}-{end}', 'Connection': 'close'}
            response: Response = self._request(
                requests.get,
                self.retries,
                delay,
                url,
                True,
                (10, 60),
                headers
            )

            result = b''

            try:
                for chunk in self._iter_content(response, chunk_size // 4):
                    result += chunk

                output.put((start, result))
            except ChunkedEncodingError:
                chunk_size = max(512 * 4, chunk_size // 2)
                ranges.put((start, end))
            except ConnectionError:
                ranges.put((start, end))

    def get_content_length(self, url: str, delay: float) -> int:
        try:
            response: Response = self._request(
                requests.head,
                self.retries,
                delay,
                url,
                False,
                10,
                {}
            )
        except HTTPError:
            raise

        return int(response.headers.get('Content-Length'))

    def fetch(self, url: str, delay: float) -> bytes:
        logger.info('Fetching "%s".', url)

        try:
            response: Response = self._request(
                requests.get,
                self.retries,
                delay,
                url,
                False,
                10,
                {})
        except HTTPError as err:
            logger.error('Failed fetching "%s": %s', url, err)
            raise

        return response.content if response else b''

    def stream(self, url: str, content_length: int, delay: float) -> bytes:
        logger.info('Downloading "%s".', url)

        try:
            chunk_size = self._get_chunk_size(content_length)
            count, ranges = self._get_content_ranges(content_length, chunk_size)
            thread_count: int = (os.cpu_count() or 1) * 2
            results = Queue()
            threads = []

            for i in range(thread_count):
                t = Thread(target=self._download_worker, args=(results, ranges, chunk_size, url, delay))
                threads.append(t)
                t.start()

            for _ in range(count):
                yield results.get()

            for t in threads:
                t.join()
        except GrabpyException as err:
            logger.error('Failed downloading "%s": %s', url, err)
            raise

        logger.info(f'Downloaded "%s".', url)
