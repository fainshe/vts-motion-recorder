import json
import time
import threading
from pathlib import Path
import asyncio
import websockets
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton, QFileDialog, QMessageBox, QLabel, QFrame
)
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from ..core.config import config
from ..core.bridge import bridge
from ..vtubestudio.client import VTSClient
from ..recorder.engine import RecorderEngine, RecordingState
from ..playback.engine import PlaybackEngine
from ..exporter.project_manager import ProjectManager

from .styles.dark_theme import DARK_THEME
from .widgets.controls import ControlsWidget
from .widgets.timeline import TimelineWidget
from .widgets.param_viewer import ParamViewerWidget
from .widgets.stats_panel import StatsPanel


class VTSPlayer(QObject):
    finished = pyqtSignal()
    frame_applied = pyqtSignal(float, float)

    def __init__(self, motion_data):
        super().__init__()
        self.motion_data = motion_data
        self._running = False
        self._thread = None
        self._ws = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._play, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _play(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._play_async())
        except asyncio.CancelledError:
            pass
        finally:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()

    async def _play_async(self):
        frames = self.motion_data.get("frames", [])
        if not frames:
            self.finished.emit()
            return

        uri = f"ws://{config.vts_host}:{config.vts_port}"
        try:
            self._ws = await asyncio.wait_for(websockets.connect(uri), timeout=5.0)
        except Exception as e:
            print(f"Failed to connect to VTS for playback: {e}")
            self.finished.emit()
            return

        try:
            await self._authenticate()
            await self._send_motion(frames)
        finally:
            await self._ws.close()
            self.finished.emit()

    async def _authenticate(self):
        auth_file = Path(config.config_file)
        token = None
        if auth_file.exists():
            try:
                token = json.loads(auth_file.read_text()).get("token")
            except Exception:
                pass

        if token:
            request = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "auth",
                "messageType": "AuthenticationRequest",
                "data": {
                    "pluginName": config.plugin_name,
                    "pluginDeveloper": config.plugin_developer,
                    "authenticationToken": token
                }
            }
            await self._ws.send(json.dumps(request))
            await asyncio.wait_for(self._ws.recv(), timeout=5.0)

    async def _send_motion(self, frames):
        duration = self.motion_data["meta"]["duration"]
        fps = self.motion_data["meta"].get("fps", 60)
        frame_interval = 1.0 / fps

        from ..playback.interpolator import Interpolator

        start_time = time.perf_counter()

        while self._running:
            elapsed = time.perf_counter() - start_time
            if elapsed >= duration:
                break

            params = Interpolator.interpolate(frames, elapsed)

            param_list = [
                {"id": name, "value": value, "weight": 1.0}
                for name, value in params.items()
            ]

            if param_list:
                request = {
                    "apiName": "VTubeStudioPublicAPI",
                    "apiVersion": "1.0",
                    "requestID": "inject",
                    "messageType": "InjectParameterDataRequest",
                    "data": {
                        "faceFound": False,
                        "mode": "set",
                        "parameterValues": param_list
                    }
                }
                try:
                    await self._ws.send(json.dumps(request))
                    self.frame_applied.emit(elapsed, duration)
                except Exception:
                    break

            await asyncio.sleep(frame_interval)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vts_client = VTSClient()
        self.recorder = RecorderEngine()
        self.playback = PlaybackEngine()
        self.project_mgr = ProjectManager()
        self._current_motion_data = None
        self._vts_player = None

        self._setup_ui()
        self._connect_signals()
        self._apply_theme()

    def _setup_ui(self):
        self.setWindowTitle("Live2D Motion Recorder")
        self.setMinimumSize(1000, 750)
        self.resize(1100, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Live2D Motion Recorder")
        self.title_label.setObjectName("title")
        header_layout.addWidget(self.title_label)

        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("status")
        self.status_label.setStyleSheet(
            "background-color: #e94560; color: white; padding: 6px 14px; border-radius: 6px;"
        )
        header_layout.addWidget(self.status_label)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedHeight(40)
        self.connect_btn.setMinimumWidth(120)
        self.connect_btn.clicked.connect(self._on_connect)
        header_layout.addWidget(self.connect_btn)

        main_layout.addLayout(header_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)

        self.controls = ControlsWidget()
        main_layout.addWidget(self.controls)

        self.timeline = TimelineWidget()
        self.timeline.seeked.connect(self._on_timeline_seek)
        main_layout.addWidget(self.timeline)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        left_group = QGroupBox("Parameters")
        left_layout = QVBoxLayout(left_group)
        self.param_viewer = ParamViewerWidget()
        left_layout.addWidget(self.param_viewer)
        content_layout.addWidget(left_group, stretch=2)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)

        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)

        export_group = QGroupBox("Actions")
        export_layout = QVBoxLayout(export_group)

        self.export_json_btn = QPushButton("Save as JSON")
        self.export_json_btn.clicked.connect(self._on_export_json)
        self.export_json_btn.setEnabled(False)
        export_layout.addWidget(self.export_json_btn)

        self.export_compressed_btn = QPushButton("Save as Compressed")
        self.export_compressed_btn.clicked.connect(self._on_export_compressed)
        self.export_compressed_btn.setEnabled(False)
        export_layout.addWidget(self.export_compressed_btn)

        self.load_motion_btn = QPushButton("Load Motion File")
        self.load_motion_btn.clicked.connect(self._on_load_motion)
        export_layout.addWidget(self.load_motion_btn)

        self.send_vts_btn = QPushButton("Send to VTS")
        self.send_vts_btn.setObjectName("playBtn")
        self.send_vts_btn.clicked.connect(self._on_send_to_vts)
        self.send_vts_btn.setEnabled(False)
        export_layout.addWidget(self.send_vts_btn)

        right_layout.addWidget(export_group)
        content_layout.addLayout(right_layout, stretch=1)

        main_layout.addLayout(content_layout)

        footer_layout = QHBoxLayout()
        self.version_label = QLabel("v1.0.0 - Fainshe")
        self.version_label.setStyleSheet("color: #6e7681; font-size: 11px;")
        footer_layout.addWidget(self.version_label)
        footer_layout.addStretch()
        self.fps_monitor = QLabel("FPS: --")
        self.fps_monitor.setStyleSheet("color: #6e7681; font-size: 11px; font-family: monospace;")
        footer_layout.addWidget(self.fps_monitor)
        main_layout.addLayout(footer_layout)

    def _connect_signals(self):
        bridge.connection_status.connect(self._on_connection_status)
        bridge.parameters_discovered.connect(self._on_parameters_discovered)
        bridge.parameter_update.connect(self._on_parameter_update)
        bridge.recording_state_changed.connect(self._on_recording_state_changed)
        bridge.frame_recorded.connect(self._on_frame_recorded)
        self.playback.frame_updated.connect(self._on_playback_frame)
        self.playback.state_changed.connect(self._on_playback_state_changed)
        self.controls.record_clicked.connect(self._on_start_recording)
        self.controls.stop_clicked.connect(self._on_stop_recording)
        self.controls.pause_clicked.connect(self._on_pause_recording)
        self.controls.play_clicked.connect(self._on_play_motion)
        self.controls.fps_changed.connect(self._on_fps_changed)

    def _apply_theme(self):
        self.setStyleSheet(DARK_THEME)

    def _on_connect(self):
        if self.vts_client.is_connected:
            self.vts_client.disconnect()
            self.connect_btn.setText("Connect")
        else:
            self.vts_client.set_parameter_callback(self._on_parameter_update)
            self.vts_client.connect()
            self.connect_btn.setText("Connecting...")
            self.connect_btn.setEnabled(False)

    def _on_connection_status(self, status, kwargs):
        status_colors = {
            "connected": "#00b894",
            "authenticated": "#00b894",
            "disconnected": "#e94560",
            "error": "#e94560",
            "auth_error": "#fdcb6e",
            "reconnecting": "#fdcb6e",
        }
        color = status_colors.get(status, "#6e7681")
        self.status_label.setStyleSheet(
            f"background-color: {color}; color: white; padding: 6px 14px; border-radius: 6px;"
        )
        self.status_label.setText(status.replace("_", " ").title())

        if status in ("connected", "authenticated"):
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setEnabled(True)
        elif status == "auth_error":
            self.connect_btn.setText("Connect")
            self.connect_btn.setEnabled(True)
            msg = kwargs.get("message", "Unknown error")
            QMessageBox.warning(self, "Auth Error",
                f"Authentication failed:\n{msg}\n\n"
                "Make sure:\n"
                "1. VTube Studio is running\n"
                "2. WebSocket API is enabled in Settings\n"
                "3. You clicked 'Allow' in the VTube Studio prompt")

    def _on_parameters_discovered(self, count, kwargs):
        self.stats_panel.update_stats(status="Connected", fps=self.recorder.fps)

    def _on_parameter_update(self, params):
        self.param_viewer.update_parameters(params)
        if self.recorder.state == RecordingState.RECORDING:
            self.recorder.record_frame(params)

    def _on_start_recording(self):
        fps = self.controls.fps_combo.currentText()
        self.recorder.start_recording(int(fps))
        self.controls.pause_btn.setEnabled(True)
        self.controls.stop_btn.setEnabled(True)
        self.controls.play_btn.setEnabled(False)
        self.controls.playback_pause_btn.setEnabled(False)
        self.controls.fps_combo.setEnabled(False)

    def _on_stop_recording(self):
        self.recorder.stop_recording()
        frames = self.recorder.get_raw_frames()
        self.controls.set_recording_state(False)

        if frames:
            self._current_motion_data = self.recorder.build_motion_data(frames)
            self.playback.load_motion(self._current_motion_data)
            self.timeline.set_duration(self._current_motion_data["meta"]["duration"])
            self.export_json_btn.setEnabled(True)
            self.export_compressed_btn.setEnabled(True)
            self.send_vts_btn.setEnabled(True)

            stats = self.recorder.get_stats()
            self.stats_panel.update_stats(
                status="Idle",
                frames=stats["frame_count"],
                duration=stats["duration"],
                fps=stats["fps"]
            )

    def _on_pause_recording(self):
        if self.recorder.state == RecordingState.RECORDING:
            self.recorder.pause_recording()
        elif self.recorder.state == RecordingState.PAUSED:
            self.recorder.resume_recording()

    def _on_recording_state_changed(self, state, kwargs):
        pass

    def _on_frame_recorded(self, frame_count, elapsed, kwargs):
        self.stats_panel.update_stats(
            status="Recording",
            frames=frame_count,
            duration=elapsed,
            fps=self.recorder.fps
        )

    def _on_play_motion(self):
        if self.playback.frames:
            self.playback.play()

    def _on_playback_frame(self, params, time_pos):
        self.param_viewer.update_parameters(params)
        self.timeline.set_current_time(time_pos)

    def _on_playback_state_changed(self, state):
        playing = state == "playing"
        paused = state == "paused"
        self.controls.set_playback_state(playing, paused)

    def _on_timeline_seek(self, time_pos):
        self.playback.seek(time_pos)

    def _on_fps_changed(self, fps):
        self.recorder.fps = fps
        self.vts_client.set_poll_interval(1.0 / fps)

    def _on_export_json(self):
        motion_data = self._get_current_motion()
        if not motion_data:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Motion JSON", str(config.motions_dir),
            "JSON Files (*.json)"
        )
        if filepath:
            self.project_mgr.save_motion(motion_data, Path(filepath).stem)
            QMessageBox.information(self, "Success", f"Saved to {filepath}")

    def _on_export_compressed(self):
        motion_data = self._get_current_motion()
        if not motion_data:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Compressed Motion", str(config.motions_dir),
            "Compressed Motion (*.motion.gz)"
        )
        if filepath:
            self.project_mgr.save_motion(motion_data, Path(filepath).stem, compressed=True)
            QMessageBox.information(self, "Success", f"Saved to {filepath}")

    def _on_load_motion(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Motion File", str(config.motions_dir),
            "Motion Files (*.json *.motion.gz)"
        )
        if filepath:
            try:
                motion_data = self.project_mgr.load_motion(filepath)
                self._current_motion_data = motion_data
                self.playback.load_motion(motion_data)
                self.timeline.set_duration(motion_data["meta"]["duration"])
                self.export_json_btn.setEnabled(True)
                self.export_compressed_btn.setEnabled(True)
                self.send_vts_btn.setEnabled(True)

                stats = motion_data["meta"]
                self.stats_panel.update_stats(
                    status="Loaded",
                    frames=stats.get("frame_count", 0),
                    duration=stats.get("duration", 0),
                    fps=stats.get("fps", 60)
                )
                QMessageBox.information(self, "Success", "Motion file loaded")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load motion: {e}")

    def _on_send_to_vts(self):
        motion_data = self._get_current_motion()
        if not motion_data:
            return

        self._vts_player = VTSPlayer(motion_data)
        self._vts_player.finished.connect(self._on_vts_playback_finished)
        self._vts_player.frame_applied.connect(self._on_vts_frame_applied)
        self.send_vts_btn.setText("Stop Sending")
        self.send_vts_btn.clicked.disconnect(self._on_send_to_vts)
        self.send_vts_btn.clicked.connect(self._on_stop_vts_playback)
        self._vts_player.start()

    def _on_stop_vts_playback(self):
        if self._vts_player:
            self._vts_player.stop()

    def _on_vts_playback_finished(self):
        self.send_vts_btn.setText("Send to VTS")
        self.send_vts_btn.clicked.disconnect(self._on_stop_vts_playback)
        self.send_vts_btn.clicked.connect(self._on_send_to_vts)
        self.stats_panel.update_stats(status="Idle")

    def _on_vts_frame_applied(self, time_pos, duration):
        self.timeline.set_current_time(time_pos)
        self.stats_panel.update_stats(
            status="Sending to VTS",
            duration=time_pos
        )

    def _get_current_motion(self):
        if self._current_motion_data:
            return self._current_motion_data
        frames = self.recorder.get_raw_frames()
        if frames:
            return self.recorder.build_motion_data(frames)
        return None

    def closeEvent(self, event):
        self.vts_client.disconnect()
        super().closeEvent(event)
