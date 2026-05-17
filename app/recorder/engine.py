import time
from datetime import datetime, timezone

from ..core.config import config
from ..core.events import bus
from ..core.timing import PrecisionTimer
from .buffer import FrameBuffer
from .optimizer import MotionOptimizer


class RecordingState:
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"


class RecorderEngine:
    def __init__(self):
        self.state = RecordingState.IDLE
        self.buffer = FrameBuffer()
        self.optimizer = MotionOptimizer(
            smoothing_window=config.smoothing_window,
            threshold=config.duplicate_threshold
        )
        self.fps = config.default_fps
        self._frame_interval = 1.0 / self.fps
        self._last_frame_time = 0.0
        self._recording_start = 0.0

    def start_recording(self, fps: int | None = None):
        if fps:
            self.fps = fps
            self._frame_interval = 1.0 / self.fps

        self.buffer.clear()
        self.state = RecordingState.RECORDING
        self._recording_start = time.perf_counter()
        self._last_frame_time = 0.0
        self.buffer.start_timer()
        bus.emit("recording_state_changed", state=self.state)

    def stop_recording(self) -> list[dict]:
        frames = self.buffer.get_frames()
        self.buffer.stop_timer()
        self.state = RecordingState.IDLE
        bus.emit("recording_state_changed", state=self.state)
        return frames

    def pause_recording(self):
        if self.state == RecordingState.RECORDING:
            self.state = RecordingState.PAUSED
            self.buffer.pause_timer()
            bus.emit("recording_state_changed", state=self.state)

    def resume_recording(self):
        if self.state == RecordingState.PAUSED:
            self.state = RecordingState.RECORDING
            self.buffer.resume_timer()
            bus.emit("recording_state_changed", state=self.state)

    def record_frame(self, params: dict[str, float]):
        if self.state != RecordingState.RECORDING:
            return

        current_time = time.perf_counter()
        if current_time - self._last_frame_time < self._frame_interval * 0.8:
            return

        elapsed = self.buffer.get_elapsed()
        self.buffer.add_frame(elapsed, params)
        self._last_frame_time = current_time
        bus.emit("frame_recorded", frame_count=self.buffer.get_frame_count(), elapsed=elapsed)

    def get_raw_frames(self) -> list[dict]:
        return self.buffer.get_frames()

    def get_optimized_frames(self, smooth: bool = True, remove_dupes: bool = True, reduce_kf: bool = False) -> list[dict]:
        raw = self.buffer.get_frames()
        return self.optimizer.optimize(raw, smooth, remove_dupes, reduce_kf)

    def get_stats(self) -> dict:
        return {
            "state": self.state,
            "frame_count": self.buffer.get_frame_count(),
            "duration": self.buffer.get_duration(),
            "fps": self.fps,
        }

    def build_motion_data(self, frames: list[dict] | None = None) -> dict:
        if frames is None:
            frames = self.buffer.get_frames()

        duration = self.buffer.get_duration()
        actual_fps = len(frames) / duration if duration > 0 else self.fps

        return {
            "meta": {
                "fps": round(actual_fps, 2),
                "duration": round(duration, 3),
                "frame_count": len(frames),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "parameters": list(frames[0]["params"].keys()) if frames else [],
            },
            "frames": frames,
        }
