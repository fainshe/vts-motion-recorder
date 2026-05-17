from ..core.timing import PrecisionTimer


class FrameBuffer:
    def __init__(self):
        self._frames: list[dict] = []
        self._timer = PrecisionTimer()

    def add_frame(self, timestamp: float, params: dict[str, float]):
        self._frames.append({
            "time": timestamp,
            "params": params.copy()
        })

    def clear(self):
        self._frames.clear()

    def get_frames(self) -> list[dict]:
        return self._frames.copy()

    def get_frame_count(self) -> int:
        return len(self._frames)

    def get_duration(self) -> float:
        if not self._frames:
            return 0.0
        return self._frames[-1]["time"] - self._frames[0]["time"]

    def start_timer(self):
        self._timer.start()

    def pause_timer(self):
        self._timer.pause()

    def resume_timer(self):
        self._timer.resume()

    def stop_timer(self):
        self._timer.stop()

    def get_elapsed(self) -> float:
        return self._timer.elapsed()
