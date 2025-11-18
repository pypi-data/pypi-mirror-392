from .exception import GrabpyException, HTTPError, FileNotSeekableError, HTTPTimeoutError, HTTPNotFoundError
from requests import Response
from requests.exceptions import ChunkedEncodingError, ConnectionError, Timeout
from typing import Callable, IO
from threading import Thread
from queue import Queue
import requests
import os
import time
import logging

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
    def _iter_content(response: Response, content_size: int, chunk_size: int) -> bytes:
        acquired: int = 0

        while acquired < content_size:
            try:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        continue

                    acquired += len(chunk)

                    yield chunk
            except (ChunkedEncodingError, ConnectionError):
                chunk_size //= 2

    @staticmethod
    def _get_content_ranges(content_length: int | None, chunk_size: int):
        end: int = -1
        limit: int = content_length - 1

        while end < limit:
            start = end + 1
            end = min(start + chunk_size, limit)

            yield start, end

    def _get_content_length(self, delay: float, url: str) -> int:
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

    @staticmethod
    def chunk_list(lst, n):
        size = len(lst) // n
        remainder = len(lst) % n

        chunks = []
        start = 0

        for i in range(n):
            extra = 1 if i < remainder else 0
            end = start + size + extra
            chunks.append(lst[start:end])
            start = end

        return chunks

    @staticmethod
    def _ensure_file_is_seekable(file: IO) -> None:
        if not file.seekable():
            raise FileNotSeekableError(file)

    def _download_worker(self, output_queue: Queue, range_data: list, chunk_size: int, url: str, delay: float) -> None:
        for start, end in range_data:
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

            for chunk in self._iter_content(response, end - start, chunk_size // 4):
                result += chunk

            output_queue.put((start, result))

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

    def stream(self, url: str, delay: float, file: IO) -> None:
        logger.info('Downloading "%s".', url)

        try:
            self._ensure_file_is_seekable(file)

            content_length = self._get_content_length(delay, url)
            chunk_size = self._get_chunk_size(content_length)
            ranges = list(self._get_content_ranges(content_length, chunk_size))
            thread_count: int = (os.cpu_count() or 1) * 2
            range_chunks = self.chunk_list(ranges, thread_count)
            results = Queue()
            threads = []

            for i in range(thread_count):
                chunk_list = range_chunks[i]
                t = Thread(target=self._download_worker, args=(results, chunk_list, chunk_size, url, delay))
                threads.append(t)
                t.start()

            file.truncate(content_length)

            for _ in range(len(ranges)):
                offset, chunk = results.get()
                file.seek(offset)
                file.write(chunk)

            for t in threads:
                t.join()
        except GrabpyException as err:
            logger.error('Failed downloading "%s": %s', url, err)
            raise

        logger.info(f'Downloaded "%s".', url)
