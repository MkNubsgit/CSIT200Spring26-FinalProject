import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QSlider, QSpinBox, QScrollArea, QDial, QLineEdit,
    QSizePolicy, QLabel, QFileDialog, QColorDialog
)
from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QFont


## SLIDER CONTROL
class SliderControl(QWidget):
    def __init__(self, label, tooltip="", min_val=0, max_val=100):
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

        if tooltip:
            self.setToolTip(tooltip)


## ROTATION CONTROL
class RotationControl(QWidget):
    def __init__(self):
        super().__init__()

        col = QVBoxLayout(self)

        self.dial = QDial()
        self.dial.setRange(0, 360)
        self.dial.setWrapping(True)

        self.spin = QSpinBox()
        self.spin.setRange(0, 360)
        self.spin.setSuffix("°")

        self.dial.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.dial.setValue)

        col.addWidget(self.dial)
        col.addWidget(self.spin)


## CANVAS
class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 800)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._image = QImage(self.size(), QImage.Format.Format_RGB32)
        self._image.fill(QColor("#ffffff"))

        self._drawing = False
        self._last_point = QPoint()

        self.brush_size = 10
        self.brush_opacity = 100
        self.brush_color = QColor("#000000")
        self.tool = "brush"

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
        self.update()

    def save(self, path):
        return self._image.save(path)

    def load(self, path):
        img = QImage(path)
        if not img.isNull():
            self._image = img
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

    def resize_canvas(self, new_width, new_height):
        if new_width <= 0 or new_height <= 0:
            return
        new_image = QImage(new_width, new_height, QImage.Format.Format_RGB32)
        new_image.fill(QColor("#ffffff"))

        painter = QPainter(new_image)
        painter.drawImage(QPoint(0, 0), self._image)
        painter.end()

        self._image = new_image
        self.update()
        
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
        painter.drawImage(QPoint(0,0), self._image)


## MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Paint App")
        self.resize(1000, 700)

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        root.addWidget(self._build_toolbar())
        root.addLayout(self._build_content())

        self._connect()

    # ---------------------------
    # Toolbar
    # ---------------------------
    def _build_toolbar(self):
        bar = QWidget()
        row = QHBoxLayout(bar)

        # File buttons
        self.btn_new = QPushButton("New")
        self.btn_load = QPushButton("Load")
        self.btn_save = QPushButton("Save")

        row.addWidget(self.btn_new)
        row.addWidget(self.btn_load)
        row.addWidget(self.btn_save)

        # Sliders
        self.size_ctrl = SliderControl("Size")
        self.opacity_ctrl = SliderControl("Opacity")

        row.addWidget(self.size_ctrl)
        row.addWidget(self.opacity_ctrl)

        # Color
        self.color_btn = QPushButton("Color")
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#HEX")

        row.addWidget(self.color_btn)
        row.addWidget(self.hex_input)

        return bar

    # ---------------------------
    # Content
    # ---------------------------
    def _build_content(self):
        row = QHBoxLayout()

        self.canvas = Canvas()

        # Left panel
        left = QVBoxLayout()

        self.btn_eraser = QPushButton("Eraser")
        self.btn_fill = QPushButton("Brush")

        left.addWidget(self.btn_eraser)
        left.addWidget(self.btn_fill)

        row.addLayout(left)
        row.addWidget(self.canvas)

        return row

    # ---------------------------
    # Connections
    # ---------------------------
    def _connect(self):
        # brush
        self.size_ctrl.slider.valueChanged.connect(self.canvas.set_brush_size)
        self.opacity_ctrl.slider.valueChanged.connect(self.canvas.set_brush_opacity)

        # tools
        self.btn_eraser.clicked.connect(lambda: self.canvas.set_tool("eraser"))
        self.btn_fill.clicked.connect(lambda: self.canvas.set_tool("brush"))

        # file
        self.btn_new.clicked.connect(self.canvas.clear)
        self.btn_save.clicked.connect(self.save_file)
        self.btn_load.clicked.connect(self.load_file)

        # color
        self.color_btn.clicked.connect(self.pick_color)
        self.hex_input.returnPressed.connect(self.set_hex)

    # ---------------------------
    # Actions
    # ---------------------------
    def pick_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.canvas.set_brush_color(c)
            self.hex_input.setText(c.name())

    def set_hex(self):
        c = QColor(self.hex_input.text())
        if c.isValid():
            self.canvas.set_brush_color(c)

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save", "", "PNG (*.png)")
        if path:
            self.canvas.save(path)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open", "", "Images (*.png *.jpg)")
        if path:
            self.canvas.load(path)


## MAIN // RUN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())