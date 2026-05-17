import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, Qt

from ..core.events import bus
from .interpolator import Interpolator


class PlaybackEngine(QObject):
    frame_updated = pyqtSignal(dict, float)
    state_changed = pyqtSignal(str)
    playback_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._frames: list[dict] = []
        self._duration: float = 0.0
        self._current_time: float = 0.0
        self._playing = False
        self._paused = False
        self._timer = QTimer()
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._on_tick)
        self._start_time = 0.0
        self._paused_elapsed = 0.0
        self._fps = 60

    def load_motion(self, motion_data: dict):
        self.stop()
        self._frames = motion_data.get("frames", [])
        self._duration = motion_data.get("meta", {}).get("duration", 0.0)
        self._current_time = 0.0
        if self._frames:
            self._fps = motion_data.get("meta", {}).get("fps", 60)
            interval = int(1000.0 / self._fps)
            self._timer.setInterval(max(interval, 16))

    def play(self):
        if not self._frames:
            return

        if self._paused:
            self._paused = False
            self._start_time = time.perf_counter() - self._paused_elapsed
        else:
            self._current_time = 0.0
            self._start_time = time.perf_counter()

        self._playing = True
        self._timer.start()
        self.state_changed.emit("playing")
        bus.emit("playback_state_changed", state="playing")

    def pause(self):
        if self._playing and not self._paused:
            self._timer.stop()
            self._paused = True
            self._paused_elapsed = self._current_time
            self.state_changed.emit("paused")
            bus.emit("playback_state_changed", state="paused")

    def stop(self):
        self._timer.stop()
        self._playing = False
        self._paused = False
        self._current_time = 0.0
        self._paused_elapsed = 0.0
        self.state_changed.emit("stopped")
        bus.emit("playback_state_changed", state="stopped")

        if self._frames:
            self.frame_updated.emit(self._frames[0]["params"], 0.0)

    def seek(self, time_pos: float):
        self._current_time = max(0.0, min(time_pos, self._duration))
        self._paused_elapsed = self._current_time

        if self._playing:
            self._start_time = time.perf_counter() - self._current_time

        params = Interpolator.interpolate(self._frames, self._current_time)
        self.frame_updated.emit(params, self._current_time)
        bus.emit("playback_seeked", time=self._current_time)

    def _on_tick(self):
        if not self._playing:
            return

        self._current_time = time.perf_counter() - self._start_time

        if self._current_time >= self._duration:
            self._current_time = self._duration
            self.stop()
            self.playback_finished.emit()
            return

        params = Interpolator.interpolate(self._frames, self._current_time)
        self.frame_updated.emit(params, self._current_time)

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def current_time(self) -> float:
        return self._current_time

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def frames(self) -> list[dict]:
        return self._frames.copy()
