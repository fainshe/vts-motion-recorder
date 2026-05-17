DARK_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    font-size: 13px;
}

QPushButton {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #0f3460;
    border-color: #533483;
}

QPushButton:pressed {
    background-color: #0a1128;
}

QPushButton:disabled {
    background-color: #0d1117;
    color: #484f58;
    border-color: #161b22;
}

QPushButton#recordBtn {
    background-color: #e94560;
    border-color: #ff6b6b;
    color: white;
    font-weight: 600;
    padding: 10px 24px;
}

QPushButton#recordBtn:hover {
    background-color: #ff6b6b;
}

QPushButton#recordBtn:disabled {
    background-color: #6b1d2d;
    border-color: #4a1520;
    color: #666666;
}

QPushButton#playBtn {
    background-color: #00b894;
    border-color: #00cec9;
    color: white;
    font-weight: 600;
}

QPushButton#playBtn:hover {
    background-color: #00cec9;
}

QPushButton#playBtn:disabled {
    background-color: #006b54;
    border-color: #004d3d;
    color: #666666;
}

QLabel {
    color: #e0e0e0;
}

QLabel#title {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.5px;
}

QLabel#section {
    font-size: 14px;
    font-weight: 600;
    color: #a0a0b0;
    margin-bottom: 8px;
}

QLabel#value {
    color: #74b9ff;
    font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

QLabel#status {
    padding: 6px 14px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 12px;
}

QGroupBox {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 20px;
    font-weight: 600;
    font-size: 13px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: #a0a0b0;
}

QScrollArea {
    border: 1px solid #0f3460;
    border-radius: 8px;
    background-color: #0d1117;
}

QScrollBar:vertical {
    background-color: #16213e;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #533483;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QComboBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
}

QComboBox:hover {
    border-color: #533483;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #e0e0e0;
    selection-background-color: #0f3460;
    border: 1px solid #0f3460;
}

QSlider::groove:horizontal {
    background-color: #0f3460;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #74b9ff;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background-color: #a0d2ff;
}

QProgressBar {
    background-color: #0f3460;
    border: 1px solid #16213e;
    border-radius: 6px;
    text-align: center;
    height: 24px;
}

QProgressBar::chunk {
    background-color: #74b9ff;
    border-radius: 5px;
}

QLineEdit {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 8px 14px;
}

QLineEdit:focus {
    border-color: #74b9ff;
}

QStatusBar {
    background-color: #0d1117;
    color: #6e7681;
    border-top: 1px solid #161b22;
    font-size: 12px;
}

QToolTip {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 8px;
}

QMenuBar {
    background-color: #1a1a2e;
    color: #e0e0e0;
    border-bottom: 1px solid #0f3460;
}

QMenuBar::item {
    padding: 8px 14px;
}

QMenuBar::item:selected {
    background-color: #16213e;
}

QMenu {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 28px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #0f3460;
}

QFrame[frameShape="4"] {
    background-color: #0f3460;
    max-height: 1px;
}
"""
