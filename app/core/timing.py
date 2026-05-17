import time


class PrecisionTimer:
    def __init__(self):
        self._start_time = 0.0
        self._paused_time = 0.0
        self._pause_start = 0.0
        self._running = False
        self._paused = False

    def start(self):
        self._start_time = time.perf_counter()
        self._running = True
        self._paused = False
        self._paused_time = 0.0

    def stop(self):
        self._running = False
        self._paused = False

    def pause(self):
        if self._running and not self._paused:
            self._pause_start = time.perf_counter()
            self._paused = True

    def resume(self):
        if self._running and self._paused:
            self._paused_time += time.perf_counter() - self._pause_start
            self._paused = False

    def elapsed(self) -> float:
        if not self._running:
            return 0.0
        if self._paused:
            return self._pause_start - self._start_time - self._paused_time
        return time.perf_counter() - self._start_time - self._paused_time

    def is_running(self) -> bool:
        return self._running

    def is_paused(self) -> bool:
        return self._paused
