import tracemalloc


class PyMemoryTracker:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        self.start_mem: int | None = None

    def start(self) -> None:
        if self.enabled:
            tracemalloc.start()
            self.start_mem, _ = tracemalloc.get_traced_memory()

    def stop(self) -> int | None:
        if not self.enabled:
            return None

        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak
