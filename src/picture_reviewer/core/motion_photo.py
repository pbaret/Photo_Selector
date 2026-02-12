from pathlib import Path
import re
import tempfile
import cv2


def is_motion_photo(jpeg_path: Path) -> bool:
    """
    Determine if a JPEG file is a motion photo by checking if XMP metadatathe 
    contains 'GCamera:MotionPhoto' tag.
    Args:
        jpeg_path (Path): Path object pointing to the JPEG file to check.
    Returns:
        bool: True if the JPEG file is a motion photo (contains GCamera:MotionPhoto
              in its XMP metadata), False otherwise.
    Raises:
        FileNotFoundError: If the file at jpeg_path does not exist.
        IOError: If the file cannot be read.
    """
    
    with open(jpeg_path, "rb") as f:
        data = f.read()

    # XMP is stored as an XML block inside the JPEG
    m = re.search(rb"<x:xmpmeta.*?</x:xmpmeta>", data, re.DOTALL)
    if not m:
        return False

    xmp = m.group(0)
    return b"GCamera:MotionPhoto" in xmp


def extract_motion_video(jpeg_path: Path) -> Path | None:
    """
    Extract the embedded MP4 from a Motion Photo JPEG using the
    Item:Length value from the XMP Container:Directory.
    Args:
        jpeg_path (Path): Path object pointing to the Motion Photo JPEG file.
    Returns:
        Path | None: A Path object pointing to the extracted MP4 file, or None if
              extraction fails.
    Raises:
        FileNotFoundError: If the file at jpeg_path does not exist.
        IOError: If the file cannot be read or written.
    """
    data = jpeg_path.read_bytes()

    # Extract XMP block
    m = re.search(rb"<x:xmpmeta.*?</x:xmpmeta>", data, re.DOTALL)
    if not m:
        return None

    xmp = m.group(0)

    # Find the MotionPhoto item with Item:Mime="video/mp4"
    m2 = re.search(
        rb'Item:Mime="video/mp4".*?Item:Length="(\d+)"',
        xmp,
        re.DOTALL
    )
    if not m2:
        return None

    mp4_length = int(m2.group(1))

    # Compute offset: MP4 is at the end of the file
    offset = len(data) - mp4_length
    if offset < 0:
        return None

    mp4_bytes = data[offset:]

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.write(mp4_bytes)
    tmp.close()

    return Path(tmp.name)


def extract_frames_from_mp4(mp4_path: Path, step: int = 3) -> list[cv2.MatLike]:
    """
    Extract frames from an MP4 video file at regular intervals.
    Args:
        mp4_path (Path): The file path to the MP4 video file to extract frames from.
        step (int, optional): The interval at which to extract frames. For example, a step of 3
                             means every 3rd frame will be extracted. Defaults to 3.
    Returns:
        list: A list of extracted frames as numpy arrays (BGR format from OpenCV).
              Returns an empty list if the video file cannot be opened or contains no frames.
    Example:
        >>> frames = extract_frames_from_mp4(Path("video.mp4"), step=5)
        >>> len(frames)
        42
    """

    cap = cv2.VideoCapture(str(mp4_path))
    if not cap.isOpened():
        return []

    frames = []
    index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if index % step == 0:
            frames.append(frame)

        index += 1

    cap.release()
    return frames

