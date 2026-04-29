import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QSpinBox,
    QLineEdit, QSizePolicy, QLabel, QFileDialog, QColorDialog, QDial
)
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QImage

## SLIDER CONTROL
"""We use this for opacity and size sliders."""
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


## ROTATION CONTROL
"""Would be used for rotation widget but it is not implemented currently."""
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
"""Canvas is set to minimum size as declared below. Sets brush size, opacity, color, tool to default 
and clears when making new. Implements save/load as well. Also handles undo/redo via history stack."""
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

    """History stack for undo/redo. We save a snapshot of the canvas after every stroke.
    Undo decrements the index and restores that snapshot.
    Redo increments the index and restores that snapshot.
    Any new stroke after an undo clears the redo history."""
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

    """The way we make our canvas update is by tracking when the left mouse button is held or not held. 
    When MouseLeft is clicked, we make the self._drawing method true, which then checks the position 
    of the mouse cursor and draws objects continuously until the left mouse button is released."""
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
        """On release we save a snapshot so undo can restore the state before this stroke."""
        self._drawing = False
        self._save_snapshot()

    """Canvas resize is implemented but not shown in UI, saving for if added later."""
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

    """Draw logic: If eraser is selected we cheat by making the eraser == background color which is 
    always white. Otherwise we use the brush color set by the QColorDialog module or hex input."""
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


## MAIN WINDOW
"""Main window that holds all other components. Builds the toolbar, left panel, and canvas.
Also handles color picking, hex input, recent colors swatches, and file operations."""
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
        """Builds the top toolbar with file buttons, undo/redo, sliders, 
        color picker, hex input, and recent color swatches."""
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
        """Recent colors: stores last 5 used colors as clickable swatches.
        Clicking a swatch restores that color as the active brush color."""
        self.swatches = []
        for i in range(5):
            swatch = QPushButton()
            swatch.setFixedSize(22, 22)
            self.swatches.append(swatch)
            row.addWidget(swatch)
        return bar

    def _build_content(self):
        """Builds the main content area with the left tool panel and canvas."""
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
        """Connects all buttons, sliders, and inputs to their respective canvas methods."""
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
        """Opens PyQt6 QColorDialog for color selection. Updates brush color,
        hex input field, and adds to recent colors."""
        c = QColorDialog.getColor()
        if c.isValid():
            self.canvas.set_brush_color(c)
            self.hex_input.setText(c.name())
            self.add_recent_color(c)

    def set_hex(self):
        """Parses hex input on Enter key press and updates brush color if valid."""
        c = QColor(self.hex_input.text())
        if c.isValid():
            self.canvas.set_brush_color(c)
            self.add_recent_color(c)

    def add_recent_color(self, color):
        """Adds a color to the recent colors list. Max 5 colors stored.
        Removes duplicates and updates swatch button backgrounds."""
        self.recent_colors = [c for c in self.recent_colors if c.name() != color.name()]
        self.recent_colors.insert(0, color)
        self.recent_colors = self.recent_colors[:5]
        for i, swatch in enumerate(self.swatches):
            if i < len(self.recent_colors):
                c = self.recent_colors[i].name()
                swatch.setStyleSheet(f"background-color: {c}; border: 1px solid #444;")
                swatch.clicked.connect(lambda _, col=self.recent_colors[i]: self._set_color_from_swatch(col))

    def _set_color_from_swatch(self, color):
        """Restores a color from a recent swatch and updates the hex input field."""
        self.canvas.set_brush_color(color)
        self.hex_input.setText(color.name())

    def save_file(self):
        """Opens a save dialog and writes the canvas image to a PNG file."""
        path, _ = QFileDialog.getSaveFileName(self, "Save", "", "PNG (*.png)")
        if path:
            self.canvas.save(path)

    def load_file(self):
        """Opens a load dialog and replaces the canvas with the selected PNG or JPG."""
        path, _ = QFileDialog.getOpenFileName(self, "Open", "", "Images (*.png *.jpg)")
        if path:
            self.canvas.load(path)


## MAIN // RUN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())