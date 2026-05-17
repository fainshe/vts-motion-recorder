from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QMouseEvent


class TimelineWidget(QWidget):
    seeked = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(48)
        self.setMinimumWidth(300)
        self._duration = 0.0
        self._current_time = 0.0
        self._is_dragging = False

    def set_duration(self, duration):
        self._duration = duration
        self.update()

    def set_current_time(self, time):
        self._current_time = time
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._seek_from_event(event)

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self._seek_from_event(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._seek_from_event(event)

    def _seek_from_event(self, event):
        if self._duration <= 0:
            return
        x = event.position().x()
        ratio = max(0.0, min(1.0, x / self.width()))
        time_pos = ratio * self._duration
        self._current_time = time_pos
        self.seeked.emit(time_pos)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        painter.fillRect(0, 0, width, height, QColor(15, 52, 96))

        if self._duration <= 0:
            return

        ratio = self._current_time / self._duration if self._duration > 0 else 0
        progress_width = int(width * ratio)

        painter.fillRect(0, 0, progress_width, height, QColor(116, 185, 255))

        painter.setPen(QColor(100, 120, 160))
        marker_interval = self._get_marker_interval()
        t = 0.0
        while t <= self._duration:
            x = int((t / self._duration) * width)
            painter.drawLine(x, 0, x, 10)
            painter.drawText(x + 6, height - 12, f"{t:.1f}s")
            t += marker_interval

        if progress_width > 0:
            painter.setPen(QColor(255, 255, 255, 200))
            painter.drawLine(progress_width, 0, progress_width, height)

    def _get_marker_interval(self):
        if self._duration <= 5:
            return 1.0
        elif self._duration <= 30:
            return 5.0
        elif self._duration <= 120:
            return 10.0
        else:
            return 30.0
