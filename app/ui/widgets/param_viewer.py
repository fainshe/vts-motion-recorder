from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt


class ParamViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._param_labels = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        title = QLabel("Parameters")
        title.setObjectName("section")
        layout.addWidget(title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(250)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(2)
        self.content_layout.setContentsMargins(4, 4, 4, 4)

        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)

        self.empty_label = QLabel("Connect to VTube Studio to see parameters")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #6e7681; padding: 40px 20px;")
        layout.addWidget(self.empty_label)

    def update_parameters(self, params):
        if self.empty_label:
            self.empty_label.hide()

        for name, value in params.items():
            if name not in self._param_labels:
                self._add_param_label(name)
            self._param_labels[name].setText(f"{value:+.3f}")

    def _add_param_label(self, name):
        row = QFrame()
        row.setStyleSheet("background-color: #0d1117; border-radius: 4px;")
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.setSpacing(2)

        name_label = QLabel(name)
        name_label.setStyleSheet("color: #a0a0b0; font-weight: 500; font-size: 12px;")

        value_label = QLabel("0.000")
        value_label.setObjectName("value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        row_layout.addWidget(name_label)
        row_layout.addWidget(value_label)

        self.content_layout.addWidget(row)
        self._param_labels[name] = value_label

    def clear(self):
        for label in self._param_labels.values():
            label.deleteLater()
        self._param_labels.clear()
        if self.empty_label:
            self.empty_label.show()
