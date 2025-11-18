from requests import Response
import requests
import os
import time
from typing import Callable, IO
from threading import Thread
from queue import Queue


class Requester:
    def __init__(self, retries: int, verbose: bool):
        self.retries = retries
        self.verbose = verbose

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
        timeout: float | tuple[int, int],
        headers: dict[str, str]
    ) -> Response | None:
        """All requests go through this function which respects the wishes of the robots file"""

        ok: int = 206 if stream else 200
        not_found: int = 404

        while retries:
            time.sleep(delay)

            response: Response = callback(url, stream=stream, timeout=timeout, headers=headers)

            if response.status_code == ok:
                return response

            if response.status_code == not_found:
                raise FileNotFoundError

            retries -= 1
            delay = (delay + 1) * 2

        return None

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
            except requests.exceptions.ChunkedEncodingError:
                chunk_size //= 2

    @staticmethod
    def _get_content_ranges(content_length: int, chunk_size: int):
        end: int = -1
        limit: int = content_length - 1

        while end < limit:
            start = end + 1
            end = min(start + chunk_size, limit)

            yield start, end

    def _get_content_length(self, delay: float, url: str) -> int | None:
        response: Response = self._request(requests.head, self.retries, delay, url, False, 10, {})

        if not response:
            return None

        return int(response.headers.get('Content-Length'))

    def fetch(self, url: str, delay: float) -> bytes:
        response: Response = self._request(requests.get, self.retries, delay, url, False, 10, {})
        return response.content if response else b''

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

    def _download_worker(self, output_queue: Queue, range_data: list, chunk_size: int, url: str, delay: float) -> None:
        for start, end in range_data:
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

    def stream(self, url: str, delay: float, file: IO) -> None:
        if not file.seekable():
            raise OSError(f'File "{file}" not seekable')

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
