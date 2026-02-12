
# Photo Selector

## Overview

Photo Selector is a lightweight utility application designed to help users browse, filter, and organize photo collections efficiently. Whether you're managing personal photos or curating images for a project, Photo Selector provides an intuitive interface for selection and organization tasks.

## Features

- **Browse & Preview**: Quick thumbnail and full-size preview of images
- **Tagging System**: Organize photos with custom tags (selection, to be removed) - though for later bulk operations
- **Export Options**: Save selected photos to custom directories
- **Lightweight**: Minimal dependencies for fast performance

## Installation

### Prerequisites

- Python 3.14+
- developed with uv for dependency management (main dependencies include pyside6, pillow, opencv-python)

### Setup

```bash
git clone https://github.com/yourusername/photo_selector.git
cd photo_selector
uv sync
```

Then to launch the application:

```bash
uv run python -m picture_reviewer

OR

python run_app.py
```

## Usage

1. Launch the application
2. Navigate to your photo directory
3. Use Keyboard Arrows or the scroll list on the left to browse the images
4. Use `S` to mark SELECT, `R` to mark "TO REMOVE" or `U` to UNMARK the current image
   (Optional) Motion photos are marked with a "🎥" Emoji. You can browse the motion frames 
   to select an alternative frame by clicking the "Extract best frame" button of the toolbar
5. Click "Commit" when you're done tagging you photos. This will :
    - COPY the "SELECTED" photos in a SELECTED folder under the initially selected photo directory
    - MOVE the "TO REMOVE" photos in a TOBEREMOVED folder under the initially selected photo directory

The philosophy behind this application was the struggle while sorting and selecting among the 4000+ smartphone photo I take every year to make yearly photo books.
The SELECTED folder serve as the basis for the photo book software (hence the copy photo).  

## Development

### Project Structure

```
photo_selector/
├── src/picture_reviewer
│   ├── ui/          # UI components
│   ├── core/        # Core logic
|   └── __main__.py  # Main entry point
└── pyproject.toml   # Dependencies

```

### Final word

Feel free to use, and give feedbacks