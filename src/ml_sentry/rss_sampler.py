import threading
import time

import psutil


class RssPeakSampler:
    def __init__(self, process: psutil.Process, interval: float) -> None:
        self._process = process
        self._interval = interval
        self._stop_event = threading.Event()
        self._peak = 0
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        peak = 0
        while not self._stop_event.is_set():
            rss = self._process.memory_info().rss
            if rss > peak:
                peak = rss
            time.sleep(self._interval)
        self._peak = peak

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> int:
        self._stop_event.set()
        self._thread.join()
        return self._peak
