from PySide6.QtGui import QImageReader, QPixmap
from PySide6.QtCore import Qt, QSize


def load_scaled_qpixmap(path: str, viewport_size: QSize) -> QPixmap:
    """
    Load an image from disk and scale it to fit within a viewport while preserving aspect ratio.
    EXIF orientation metadata is automatically applied to the image.
    
    Args:
        path (str): File path to the image to load.
        viewport_size (QSize): Target viewport size that the image should fit within.
            The image will be scaled to fit this size while maintaining its aspect ratio.
    Returns:
        QPixmap: The scaled image as a QPixmap object. Returns an empty QPixmap if the
            image fails to load or read.
    Note:
        - EXIF orientation is automatically applied during loading
        - The image is decoded at the scaled size for optimal performance and memory usage
        - Aspect ratio is preserved during scaling
    """
    reader = QImageReader(path)

    # Apply EXIF orientation automatically
    reader.setAutoTransform(True)

    # Decode at target size (fast + low memory)
    original_size = reader.size()
    if viewport_size.width() > 0 and viewport_size.height() > 0:
        # Compute aspect-ratio–preserving scaled size
        scaled = original_size.scaled(viewport_size, Qt.KeepAspectRatio)
        reader.setScaledSize(scaled)        

    img = reader.read()
    if img.isNull():
        return QPixmap()  # return empty pixmap on failure

    return QPixmap.fromImage(img)
