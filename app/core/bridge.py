from PyQt6.QtCore import QObject, pyqtSignal


class SignalBridge(QObject):
    connection_status = pyqtSignal(str, dict)
    parameters_discovered = pyqtSignal(int, dict)
    recording_state_changed = pyqtSignal(str, dict)
    frame_recorded = pyqtSignal(int, float, dict)
    parameter_update = pyqtSignal(dict)

    def emit_connection_status(self, status: str, **kwargs):
        self.connection_status.emit(status, kwargs)

    def emit_parameters_discovered(self, count: int, **kwargs):
        self.parameters_discovered.emit(count, kwargs)

    def emit_recording_state_changed(self, state: str, **kwargs):
        self.recording_state_changed.emit(state, kwargs)

    def emit_frame_recorded(self, frame_count: int, elapsed: float, **kwargs):
        self.frame_recorded.emit(frame_count, elapsed, kwargs)

    def emit_parameter_update(self, params: dict):
        self.parameter_update.emit(params)


bridge = SignalBridge()
