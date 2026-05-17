from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal


class ControlsWidget(QWidget):
    record_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    play_clicked = pyqtSignal()
    seek_clicked = pyqtSignal(float)
    fps_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._recording = False
        self._playing = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 4, 0, 4)

        self.record_btn = QPushButton("Record")
        self.record_btn.setObjectName("recordBtn")
        self.record_btn.setFixedHeight(44)
        self.record_btn.setMinimumWidth(100)
        self.record_btn.clicked.connect(self._on_record)
        layout.addWidget(self.record_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setFixedHeight(44)
        self.pause_btn.setMinimumWidth(80)
        self.pause_btn.clicked.connect(self._on_pause)
        self.pause_btn.setEnabled(False)
        layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFixedHeight(44)
        self.stop_btn.setMinimumWidth(80)
        self.stop_btn.clicked.connect(self._on_stop)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        layout.addSpacing(16)

        self.play_btn = QPushButton("Play")
        self.play_btn.setObjectName("playBtn")
        self.play_btn.setFixedHeight(44)
        self.play_btn.setMinimumWidth(80)
        self.play_btn.clicked.connect(self._on_play)
        self.play_btn.setEnabled(False)
        layout.addWidget(self.play_btn)

        self.playback_pause_btn = QPushButton("Pause")
        self.playback_pause_btn.setFixedHeight(44)
        self.playback_pause_btn.setFixedWidth(80)
        self.playback_pause_btn.clicked.connect(self._on_playback_pause)
        self.playback_pause_btn.setEnabled(False)
        layout.addWidget(self.playback_pause_btn)

        layout.addStretch()

        fps_label = QLabel("FPS:")
        fps_label.setStyleSheet("color: #a0a0b0; font-weight: 500;")
        layout.addWidget(fps_label)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60"])
        self.fps_combo.setFixedWidth(80)
        self.fps_combo.currentTextChanged.connect(self._on_fps_changed)
        layout.addWidget(self.fps_combo)

    def _on_record(self):
        if not self._recording:
            self._recording = True
            self.record_btn.setText("Recording...")
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.play_btn.setEnabled(False)
            self.playback_pause_btn.setEnabled(False)
            self.fps_combo.setEnabled(False)
            self.record_clicked.emit()
        else:
            self._on_stop()

    def _on_stop(self):
        if self._recording:
            self._recording = False
            self.record_btn.setText("Record")
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.fps_combo.setEnabled(True)
            self.stop_clicked.emit()

    def _on_pause(self):
        self.pause_clicked.emit()
        if self.pause_btn.text() == "Pause":
            self.pause_btn.setText("Resume")
        else:
            self.pause_btn.setText("Pause")

    def _on_play(self):
        self.play_clicked.emit()
        self.playback_pause_btn.setEnabled(True)

    def _on_playback_pause(self):
        self.seek_clicked.emit(-1)

    def _on_fps_changed(self, text):
        self.fps_changed.emit(int(text))

    def set_recording_state(self, recording):
        self._recording = recording
        if not recording:
            self.record_btn.setText("Record")
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.fps_combo.setEnabled(True)

    def set_playback_state(self, playing, paused=False):
        self._playing = playing
        self.play_btn.setEnabled(not playing)
        self.playback_pause_btn.setEnabled(playing)
        if playing:
            self.playback_pause_btn.setText("Pause" if not paused else "Resume")
