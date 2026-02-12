from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QSlider
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

import cv2


class MotionPhotoFrameSelectorDialog(QDialog):
    """
    MotionPhotoFrameSelectorDialog is a dialog for selecting the best frame from a series of motion photos' frames.
    Attributes:
        frames (list): A list of frames (images) to be displayed for selection.
        current_index (int): The index of the currently selected frame.
    Methods:
        __init__(frames, parent=None): Initializes the dialog with the given frames and sets up the UI components.
        on_slider_changed(value: int): Updates the current frame index based on the slider's value and refreshes the preview.
        on_prev(): Decreases the current frame index and updates the slider if not at the first frame.
        on_next(): Increases the current frame index and updates the slider if not at the last frame.
        resizeEvent(event): Overrides the default resize event to update the preview when the dialog is resized.
        update_preview(): Updates the displayed image in the label based on the current frame index.
        get_selected_frame(): Returns the currently selected frame.
    """

    def __init__(self, frames, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select best frame")
        self.frames = frames
        self.current_index = 0

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.frames) - 1)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.on_slider_changed)

        btn_prev = QPushButton("Previous")
        btn_next = QPushButton("Next")
        btn_ok = QPushButton("Use this frame")
        btn_cancel = QPushButton("Cancel")

        btn_prev.clicked.connect(self.on_prev)
        btn_next.clicked.connect(self.on_next)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        h_buttons = QHBoxLayout()
        h_buttons.addWidget(btn_prev)
        h_buttons.addWidget(btn_next)
        h_buttons.addStretch()
        h_buttons.addWidget(btn_cancel)
        h_buttons.addWidget(btn_ok)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.slider)
        layout.addLayout(h_buttons)
        self.setLayout(layout)

        self.update_preview()

    def on_slider_changed(self, value: int):
        self.current_index = value
        self.update_preview()

    def on_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.slider.setValue(self.current_index)

    def on_next(self):
        if self.current_index < len(self.frames) - 1:
            self.current_index += 1
            self.slider.setValue(self.current_index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()

    def update_preview(self):
        frame = self.frames[self.current_index]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(
            pix.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def get_selected_frame(self):
        return self.frames[self.current_index]
