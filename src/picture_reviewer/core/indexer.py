from pathlib import Path
from dataclasses import dataclass
from picture_reviewer.core.motion_photo import is_motion_photo

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}

@dataclass
class ImageEntry:
    """
    Represents a single image entry in the photo collection.

    Attributes:
        path (Path): The file system path to the image file.
        is_motion (bool): Indicates whether the image contains motion (motion photo from smartphones).
    """
    path: Path
    is_motion: bool


def index_images(root: Path) -> list[ImageEntry]:
    """
    Index all supported image files in a directory and its subdirectories.
    Recursively searches the given root directory for image files with supported
    extensions and creates ImageEntry objects for each file. For JPEG files,
    detects whether they are motion photos.
    Args:
        root (Path): The root directory path to search for images.
    Returns:
        list[ImageEntry]: A list of ImageEntry objects sorted by parent directory
            path (case-insensitive) and then by filename (case-insensitive).
            Returns an empty list if root does not exist or is not a directory.
    Raises:
        None: Returns empty list on invalid root path instead of raising.
    """
    if not root.exists() or not root.is_dir():
        return []

    files = [
        ImageEntry(path=path, is_motion=False) for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXT
    ]

    for entry in files:
        if entry.path.suffix.lower() in {".jpg", ".jpeg"}:
            entry.is_motion = is_motion_photo(entry.path)

    # Sort by parent path, then filename lowercase
    files.sort(key=lambda entry: (str(entry.path.parent).lower(), entry.path.name.lower()))
    return files

