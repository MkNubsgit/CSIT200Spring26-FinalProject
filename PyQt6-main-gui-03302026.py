import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QSpinBox,
    QLineEdit, QSizePolicy, QLabel, QFileDialog, QColorDialog, QDial
)
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QImage

class SliderControl(QWidget):
    def __init__(self, label, min_val=0, max_val=100):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(6, 3, 6, 3)
        lbl = QLabel(label)
        lbl.setFixedWidth(45)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.spin = QSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.slider.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.slider.setValue)
        row.addWidget(lbl)
        row.addWidget(self.slider)
        row.addWidget(self.spin)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._image = QImage(self.size(), QImage.Format.Format_RGB32)
        self._image.fill(QColor("#ffffff"))
        self._drawing = False
        self._last_point = QPoint()
        self.brush_size = 10
        self.brush_opacity = 100
        self.brush_color = QColor("#000000")
        self.tool = "brush"
        self.history = []
        self.history_index = -1
        self._save_snapshot()

    def set_brush_size(self, v):
        self.brush_size = max(1, v)

    def set_brush_opacity(self, v):
        self.brush_opacity = v

    def set_brush_color(self, c):
        self.brush_color = c

    def set_tool(self, tool):
        self.tool = tool

    def clear(self):
        self._image.fill(QColor("#ffffff"))
        self._save_snapshot()
        self.update()

    def save(self, path):
        return self._image.save(path)

    def load(self, path):
        img = QImage(path)
        if not img.isNull():
            self._image = img
            self._save_snapshot()
            self.update()

    def _save_snapshot(self):
        self.history = self.history[:self.history_index + 1]
        self.history.append(self._image.copy())
        self.history_index += 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._image = self.history[self.history_index].copy()
            self.update()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._image = self.history[self.history_index].copy()
            self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drawing = True
            self._last_point = e.position().toPoint()
            self._draw(self._last_point, self._last_point)

    def mouseMoveEvent(self, e):
        if self._drawing:
            p = e.position().toPoint()
            self._draw(self._last_point, p)
            self._last_point = p

    def mouseReleaseEvent(self, e):
        self._drawing = False
        self._save_snapshot()

    def _draw(self, p1, p2):
        painter = QPainter(self._image)
        if self.tool == "eraser":
            color = QColor("#ffffff")
            opacity = 1.0
        else:
            color = self.brush_color
            opacity = self.brush_opacity / 100
        painter.setOpacity(opacity)
        painter.setPen(QPen(color, self.brush_size,
                            Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap))
        painter.drawLine(p1, p2)
        painter.end()
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), self._image)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recent_colors = []
        self.setWindowTitle("Paint App")
        self.resize(1000, 700)
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.addWidget(self._build_toolbar())
        root.addLayout(self._build_content())
        self._connect()

    def _build_toolbar(self):
        bar = QWidget()
        row = QHBoxLayout(bar)
        self.btn_new = QPushButton("New")
        self.btn_load = QPushButton("Load")
        self.btn_save = QPushButton("Save")
        self.btn_undo = QPushButton("Undo")
        self.btn_redo = QPushButton("Redo")
        row.addWidget(self.btn_new)
        row.addWidget(self.btn_load)
        row.addWidget(self.btn_save)
        row.addWidget(self.btn_undo)
        row.addWidget(self.btn_redo)
        self.size_ctrl = SliderControl("Size")
        self.size_ctrl.slider.setValue(10)
        self.opacity_ctrl = SliderControl("Opacity")
        self.opacity_ctrl.slider.setValue(100)
        row.addWidget(self.size_ctrl)
        row.addWidget(self.opacity_ctrl)
        self.color_btn = QPushButton("Color")
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#HEX")
        row.addWidget(self.color_btn)
        row.addWidget(self.hex_input)
        self.swatches = []
        for i in range(5):
            swatch = QPushButton()
            swatch.setFixedSize(22, 22)
            self.swatches.append(swatch)
            row.addWidget(swatch)
        return bar

    def _build_content(self):
        row = QHBoxLayout()
        self.canvas = Canvas()
        left = QVBoxLayout()
        self.btn_eraser = QPushButton("Eraser")
        self.btn_brush = QPushButton("Brush")
        left.addWidget(self.btn_eraser)
        left.addWidget(self.btn_brush)
        left.addStretch()
        row.addLayout(left)
        row.addWidget(self.canvas)
        return row

    def _connect(self):
        self.size_ctrl.slider.valueChanged.connect(self.canvas.set_brush_size)
        self.opacity_ctrl.slider.valueChanged.connect(self.canvas.set_brush_opacity)
        self.btn_eraser.clicked.connect(lambda: self.canvas.set_tool("eraser"))
        self.btn_brush.clicked.connect(lambda: self.canvas.set_tool("brush"))
        self.btn_new.clicked.connect(self.canvas.clear)
        self.btn_save.clicked.connect(self.save_file)
        self.btn_load.clicked.connect(self.load_file)
        self.btn_undo.clicked.connect(self.canvas.undo)
        self.btn_redo.clicked.connect(self.canvas.redo)
        self.color_btn.clicked.connect(self.pick_color)
        self.hex_input.returnPressed.connect(self.set_hex)

    def pick_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.canvas.set_brush_color(c)
            self.hex_input.setText(c.name())
            self.add_recent_color(c)

    def set_hex(self):
        c = QColor(self.hex_input.text())
        if c.isValid():
            self.canvas.set_brush_color(c)
            self.add_recent_color(c)

    def add_recent_color(self, color):
        self.recent_colors = [c for c in self.recent_colors if c.name() != color.name()]
        self.recent_colors.insert(0, color)
        self.recent_colors = self.recent_colors[:5]
        for i, swatch in enumerate(self.swatches):
            if i < len(self.recent_colors):
                c = self.recent_colors[i].name()
                swatch.setStyleSheet(f"background-color: {c}; border: 1px solid #444;")
                swatch.clicked.connect(lambda _, col=self.recent_colors[i]: self._set_color_from_swatch(col))

    def _set_color_from_swatch(self, color):
        self.canvas.set_brush_color(color)
        self.hex_input.setText(color.name())

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save", "", "PNG (*.png)")
        if path:
            self.canvas.save(path)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open", "", "Images (*.png *.jpg)")
        if path:
            self.canvas.load(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())