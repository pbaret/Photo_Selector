from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap, QPen, QFont
from PySide6.QtCore import Qt, QRect


class ImageView(QWidget):
    """
    ImageView is a QWidget subclass that provides a custom widget for displaying images with optional borders.
    Attributes:
        _pixmap (QPixmap | None): The pixmap to be displayed in the widget.
        _border_color (QColor): The color of the border around the image.
    Methods:
        set_pixmap(pixmap: QPixmap, border_color=Qt.green):
            Sets the pixmap to be displayed and the border color, then updates the widget.
        set_tag_visuals(border_color):
            Updates the border color and refreshes the widget.
        clear():
            Clears the displayed pixmap and refreshes the widget.
        paintEvent(event):
            Handles the painting of the widget, including drawing the background, the image, and the border.
    """

    def __init__(self, parent=None):
        """
        Initializes the ImageView class.
        Parameters:
            parent (QWidget, optional): The parent widget for this ImageView instance. Defaults to None.
        Attributes:
            _pixmap (QPixmap | None): Holds the pixmap image to be displayed. Initialized to None.
            _border_color (QColor): The color of the border around the image. Initialized to green.
        Sets the background color of the widget to black.
        """
        super().__init__(parent)

        self._pixmap: QPixmap | None = None
        self._border_color = Qt.green

        self.setStyleSheet("background-color: black;")

    # -------------------------
    # Public API
    # -------------------------

    def set_pixmap(self, pixmap: QPixmap, border_color=Qt.green):
        """
        Sets the pixmap to be displayed and updates the border color.
        Args:
            pixmap (QPixmap): The QPixmap object to be set.
            border_color (Qt.GlobalColor, optional): The color of the border. 
                Defaults to Qt.green.
        This method updates the internal pixmap and border color, 
        and triggers a repaint of the widget.
        """
        self._pixmap = pixmap
        self._border_color = border_color
        self.update()


    def set_tag_visuals(self, border_color):
        """
        Sets the visual properties of the tag by updating the border color.
        Args:
            border_color (str): The color to be set for the border. 
                                It should be a valid color representation 
                                (e.g., hex code, color name).
        This method updates the instance's border color and triggers a refresh 
        of the visual representation by calling the update method.
        """

        self._border_color = border_color
        self.update()


    def clear(self):
        self._pixmap = None
        self.update()

    # -------------------------
    # Painting
    # -------------------------

    def paintEvent(self, event):
        """
        Handles the painting of the widget by drawing the image and its border.
        This method is called whenever the widget needs to be repainted. It fills the background
        with a black color, scales the pixmap to fit the widget while maintaining the aspect ratio,
        and draws the pixmap centered within the widget. Additionally, it draws a border around the
        widget using the specified border color.
        Parameters:
            event (QPaintEvent): The paint event that triggered this method.
        """
        painter = QPainter(self)

        # Fill background (stylesheet alone is not always enough)
        painter.fillRect(self.rect(), Qt.black)

        if not self._pixmap:
            return

        img_w = self._pixmap.width()
        img_h = self._pixmap.height()

        # Center the image
        x = 0
        y = 0

        # Draw image
        # Compute scaled size that fits the widget (logical pixels)
        target_size = self._pixmap.size().scaled(
            self.size(),
            Qt.KeepAspectRatio
        )

        painter.drawPixmap(
            QRect(x, y, target_size.width(), target_size.height()),
            self._pixmap
        )

        # Draw border
        pen = QPen(self._border_color, 20)
        painter.setPen(pen)
        painter.drawRect(x, y, self.width(), self.height())

        painter.end()