from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout


class StatsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("Statistics")
        title.setObjectName("section")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.labels = {}
        stats = [
            ("Status", "status_value"),
            ("Frames", "frames_value"),
            ("Duration", "duration_value"),
            ("FPS", "fps_value"),
        ]

        for i, (label_text, obj_name) in enumerate(stats):
            label = QLabel(label_text)
            label.setStyleSheet("color: #6e7681; font-size: 12px;")
            grid.addWidget(label, i, 0)

            value_label = QLabel("-")
            value_label.setObjectName("value")
            grid.addWidget(value_label, i, 1)
            self.labels[obj_name] = value_label

        layout.addLayout(grid)

    def update_stats(self, status="", frames=0, duration=0.0, fps=0.0):
        if status:
            self.labels["status_value"].setText(status)
        self.labels["frames_value"].setText(str(frames))
        self.labels["duration_value"].setText(f"{duration:.2f}s")
        self.labels["fps_value"].setText(f"{fps:.1f}")
