from enum import Enum, auto
from PySide6.QtGui import QColor


class Tag(Enum):
    """
    Enumeration of possible tag states for an image.

    Members:
    - UNMARKED: Default state; the image has not been reviewed or marked.
    - SELECTED: Image has been marked as selected/kept.
    - TO_REMOVE: Image has been marked for removal or exclusion.
    """
    UNMARKED = auto()
    SELECTED = auto()
    TO_REMOVE = auto()


TAG_EMOJI = {
    Tag.UNMARKED: "",
    Tag.SELECTED: "✅",
    Tag.TO_REMOVE: "🗑️",
}
"""Mapping[Tag, str]: Emoji used as icons to represent each `Tag` in the UI.

Empty string is used for `Tag.UNMARKED`.
"""


TAG_COLOR = {
    Tag.UNMARKED: QColor("black"),
    Tag.SELECTED: QColor("green"),
    Tag.TO_REMOVE: QColor("red"),
}
"""Mapping[Tag, QColor]: Primary color for tag visuals (text/icon).

Colors are `QColor` instances.
"""


TAG_BORDER_COLOR = {
    Tag.UNMARKED: QColor("black"),
    Tag.SELECTED: QColor("green"),
    Tag.TO_REMOVE: QColor("red"),
}
"""Mapping[Tag, QColor]: Border color to use for image frames based on `Tag`.

UI components that draw a highlighted border around images should consult this
mapping to determine the appropriate color for the currently applied tag.
Colors are `QColor` instances.
"""
