import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QSlider, QSpinBox, QScrollArea, QDial, QLineEdit, QSizePolicy, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


# SliderControl  —  labelled sliders + spinboxes
class SliderControl(QWidget):
    def __init__(self, label, tooltip="", min_val=0, max_val=100):
        super().__init__()
        self.setObjectName("SliderOuter")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        inner = QWidget()
        inner.setObjectName("SliderGroup")

        row = QHBoxLayout(inner)
        row.setContentsMargins(6, 3, 6, 3)
        row.setSpacing(6)

        lbl = QLabel(label)
        lbl.setFixedWidth(45)
        lbl.setFont(QFont("Arial", 10))

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setFixedWidth(110)

        self.spin = QSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setFixedWidth(60)
        self.spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        # sync slider and spinbox to update same value
        self.slider.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.slider.setValue)

        row.addWidget(lbl)
        row.addWidget(self.slider)
        row.addWidget(self.spin)

        outer_row = QHBoxLayout(self)
        outer_row.setContentsMargins(0, 0, 0, 0)
        outer_row.addWidget(inner)

        if tooltip:
            self.setToolTip(tooltip)


# RotationControl  —  dial + degree spinbox
class RotationControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setToolTip("Brush rotation (0–360°)")

        col = QVBoxLayout(self)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)

        self.dial = QDial()
        self.dial.setRange(0, 360)
        self.dial.setWrapping(True)
        self.dial.setFixedSize(50, 50)

        self.spin = QSpinBox()
        self.spin.setRange(0, 360)
        self.spin.setSuffix("°")
        self.spin.setFixedWidth(60)
        self.spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.dial.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.dial.setValue)

        col.addWidget(self.dial, alignment=Qt.AlignmentFlag.AlignCenter)
        col.addWidget(self.spin, alignment=Qt.AlignmentFlag.AlignCenter)


# Canvas  —  drawing surface PLACEHOLDER
class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Canvas")
        self.setMinimumSize(400, 400)
        self.setToolTip("Drawing area")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


# MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSIT200 PAINT PROJECT")
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._build_toolbar())
        root.addWidget(self._make_separator())
        root.addLayout(self._build_content())

        self._apply_styles()

    # TOOLBAR
    def _build_toolbar(self):
        bar = QWidget()
        bar.setObjectName("Toolbar")

        row = QHBoxLayout(bar)
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(8)

        # File actions
        file_tips = {
            "New":  "Create a new canvas",
            "Load": "Open an existing file",
            "Save": "Save the current canvas",
        }
        for name, tip in file_tips.items():
            btn = QPushButton(name)
            btn.setToolTip(tip)
            row.addWidget(btn)

        row.addSpacing(10)

        # History actions
        history_tips = {
            "Undo": "Undo the last action",
            "Redo": "Redo the last undone action",
        }
        for name, tip in history_tips.items():
            btn = QPushButton(name)
            btn.setToolTip(tip)
            row.addWidget(btn)

        row.addSpacing(15)

        row.addWidget(SliderControl("Size",    tooltip="Brush size (0–100)"))
        row.addWidget(SliderControl("Opacity", tooltip="Brush opacity (0–100)"))

        row.addSpacing(15)
        row.addWidget(RotationControl())
        row.addSpacing(15)

        color_btn = QPushButton("Color")
        color_btn.setToolTip("Open the color picker")
        row.addWidget(color_btn)

        hex_input = QLineEdit()
        hex_input.setPlaceholderText("#HEX")
        hex_input.setFixedWidth(80)
        hex_input.setToolTip("Enter a hex color value")
        row.addWidget(hex_input)

        # Recent colors
        for i in range(5):
            swatch = QPushButton()
            swatch.setFixedSize(22, 22)
            swatch.setToolTip(f"Recent color {i + 1}")
            row.addWidget(swatch)

        row.addStretch()
        return bar

    # Left panel - primarily brush picker
    def _build_left_panel(self):
        panel = QWidget()
        panel.setObjectName("LeftPanel")
        panel.setFixedWidth(130)

        col = QVBoxLayout(panel)
        col.setContentsMargins(5, 5, 5, 5)
        col.setSpacing(6)

        # Scrollable brush grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        brush_grid_widget = QWidget()
        grid = QGridLayout(brush_grid_widget)
        grid.setSpacing(4)

        for i in range(12):
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setToolTip(f"Brush {i + 1}")
            grid.addWidget(btn, i // 2, i % 2)

        scroll.setWidget(brush_grid_widget)
        col.addWidget(scroll)

        col.addWidget(self._make_separator(horizontal=True))

        tool_tips = {
            "Eraser": "Erase strokes",
            "Fill":   "Flood fill a region",
        }
        for name, tip in tool_tips.items():
            btn = QPushButton(name)
            btn.setFixedHeight(36)
            btn.setToolTip(tip)
            col.addWidget(btn)

        col.addStretch()
        return panel

    # Panel and canvas content 
    def _build_content(self):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        canvas_col = QVBoxLayout()
        canvas_col.setContentsMargins(10, 10, 10, 10)
        canvas_col.addWidget(Canvas())

        row.addWidget(self._build_left_panel(), 0)
        row.addWidget(self._make_separator(vertical=True), 0)
        row.addLayout(canvas_col, 1)

        return row

    # separators for visual separation
    def _make_separator(self, vertical=False, horizontal=False):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine if vertical else QFrame.Shape.HLine)
        return line







    # STYLESHEET FOR COLORING DO NOT REMOVE
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #d0d0d0;
                color: #111;
                font-size: 12px;
            }

            QWidget#Toolbar {
                background-color: #bcbcbc;
                border-bottom: 2px solid #888;
            }

            QWidget#LeftPanel {
                background-color: #c6c6c6;
                border-right: 1px solid #888;
            }

            QWidget#Canvas {
                background-color: #ffffff;
                border: 2px solid #222;
            }

            QWidget#SliderOuter {
                background-color: #b0b0b0;
            }

            QWidget#SliderGroup {
                background-color: #b0b0b0;
                border: 1px solid #888;
                border-radius: 4px;
            }

            QWidget#SliderGroup QLabel {
                color: #111;
            }

            QPushButton {
                background-color: #a8a8a8;
                border: 1px solid #666;
                padding: 4px;
            }

            QPushButton:hover {
                background-color: #969696;
            }

            QPushButton:pressed {
                background-color: #7f7f7f;
            }

            QLineEdit, QSpinBox {
                background-color: #ffffff;
                border: 1px solid #666;
                padding: 2px;
                color: #000;
            }

            QSlider::groove:horizontal {
                background: #999;
                height: 6px;
            }

            QSlider::handle:horizontal {
                background: #333;
                width: 10px;
                margin: -4px 0;
            }

            QFrame {
                background-color: #777;
            }

            QToolTip {
                background-color: #333;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 3px;
                font-size: 11px;
            }
        """)


#Main function 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())