import os
from PySide6.QtWidgets import QMainWindow, QWidget, QToolBar, QDockWidget, QListWidget, QListWidgetItem
from PySide6.QtWidgets import QDialog, QFileDialog, QProgressDialog, QMessageBox
from PySide6.QtGui import QAction, QKeyEvent
from PySide6.QtCore import Qt, QSize

from pathlib import Path
import logging
import shutil

import cv2

from picture_reviewer.ui.image_view import ImageView
from picture_reviewer.ui.motion_select_dialog import MotionPhotoFrameSelectorDialog
from picture_reviewer.core.indexer import ImageEntry, index_images
from picture_reviewer.core.image_loader import load_scaled_qpixmap
from picture_reviewer.core.tags import Tag, TAG_EMOJI, TAG_COLOR, TAG_BORDER_COLOR
from picture_reviewer.core.motion_photo import extract_motion_video, extract_frames_from_mp4

class MainWindow(QMainWindow):
    """
    MainWindow class for the Picture Reviewer application.
    This class provides a graphical user interface for reviewing and tagging images.
    It allows users to open a folder containing images, navigate through them, 
    tag them as selected or to be removed, and commit changes to organize the images 
    into designated folders. The application supports motion photos, enabling users 
    to extract the best frame from such images.
    Attributes:
        images_entries (list[ImageEntry]): List of image entries representing the images in the selected folder.
        images_tags (dict[Path, Tag]): Dictionary mapping image paths to their respective tags.
        current_index (int): Index of the currently displayed image.
        image_viewer (ImageView): Widget for displaying the currently selected image.
        file_list (QListWidget): List widget displaying the images in the selected folder.
        extract_motion_action (QAction): Action for extracting the best frame from motion photos.
        source_dir (Path): Path to the folder containing the images.
        selected_dir (Path): Path to the folder where selected images will be copied.
        to_remove_dir (Path): Path to the folder where images marked for removal will be moved.
    Methods:
        __init__(): Initializes the MainWindow and sets up the UI components.
        _build_toolbar(): Constructs the toolbar with actions for opening folders, extracting frames, and committing changes.
        _build_file_list(): Sets up the file list widget for displaying images.
        choose_folder(): Opens a dialog to select a folder and populates the image list.
        on_file_clicked(item): Displays the image corresponding to the clicked list item.
        display_index(i: int): Displays the image at the specified index.
        keyPressEvent(event: QKeyEvent): Handles key press events for navigation and tagging.
        update_list_item_visuals(item, tag: Tag, is_motion: bool): Updates the visuals of a list item based on its tag and motion status.
        action_next_image(): Displays the next image in the list.
        action_previous_image(): Displays the previous image in the list.
        commit_changes(): Processes tagged images and moves/copies them to the appropriate folders.
        compute_commit_plan(): Creates a plan for copying and moving images based on their tags.
        confirm_commit(plan): Displays a confirmation dialog for the commit action.
        extract_best_frame_from_current(): Extracts the best frame from the currently displayed motion photo.
    """

    def __init__(self):
        
        super().__init__()

        self.images_entries: list[ImageEntry] = []
        self.images_tags: dict[Path, Tag] = {}   # path → tag
        self.current_index: int = -1

        self.setWindowTitle("Picture Reviewer")

        self.image_viewer = ImageView()
        self.image_viewer.setFocusPolicy(Qt.StrongFocus)
        self.image_viewer.setFocus()
        self.setCentralWidget(self.image_viewer)

        self._build_toolbar()
        self._build_file_list()

        self.statusBar().showMessage("Ready")
        self.showMaximized()
        

    def _build_toolbar(self):
        tb = QToolBar("Main", movable=False, floatable=False)
        self.addToolBar(tb)

        open_action = QAction(parent = self, text = "📂 Open", toolTip="Open a Photo Folder")
        open_action.triggered.connect(self.choose_folder)
        tb.addAction(open_action)
        
        spacer = QWidget()
        spacer.setFixedWidth(16)
        tb.addWidget(spacer)

        self.extract_motion_action = QAction(parent=self, text="Extract best frame…")
        self.extract_motion_action.setEnabled(False)
        self.extract_motion_action.triggered.connect(self.extract_best_frame_from_current)
        tb.addAction(self.extract_motion_action)

        tb.addWidget(spacer)

        commit_action = QAction(parent = self, text = "🚀 Commit", toolTip="Process tagged images")
        commit_action.triggered.connect(self.commit_changes)
        tb.addAction(commit_action)


    def _build_file_list(self):
        self.file_list = QListWidget()
        self.file_list.setFixedWidth(250)
        self.file_list.setFocusPolicy(Qt.NoFocus)
        self.file_list.itemClicked.connect(self.on_file_clicked)

        dock = QDockWidget("Images", self)
        dock.setWidget(self.file_list)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select a folder")
        if not folder:
            return

        self.images_tags.clear()
        root = Path(folder)
        self.images_entries = index_images(root)

        if not self.images_entries:
            QMessageBox.warning(self, "No images", "No supported images found.")
            self.statusBar().showMessage("No images found")
        else:
            self.source_dir = root

            self.file_list.clear()

            for entry in self.images_entries:
                item = QListWidgetItem(entry.path.name)
                item.setData(Qt.UserRole, entry.path)  # store the full Path object
                self.file_list.addItem(item)
                self.images_tags[entry.path] = Tag.UNMARKED
                self.update_list_item_visuals(item, self.images_tags[entry.path], entry.is_motion)

            self.statusBar().showMessage(f"{len(self.images_entries)} images found")

            if self.images_entries:
                self.display_index(0)
            else:
                self.image_viewer.clear()   


    def on_file_clicked(self, item):
        row = self.file_list.row(item)
        self.display_index(row)


    def display_index(self, i: int):
        if not (0 <= i < len(self.images_entries)):
            logging.info(f"MainWindow.display_index: {i} is out of range")
            return

        self.current_index = i

        # Update list selection
        self.file_list.setCurrentRow(i)

        # Determine viewport size (the visible area of the viewer)
        ratio = self.image_viewer.devicePixelRatioF()
        physical_size = QSize(
            int(self.image_viewer.width() * ratio),
            int(self.image_viewer.height() * ratio)
        )

        path = self.images_entries[i].path
        tag = self.images_tags[path]
        pixmap = load_scaled_qpixmap(str(path), physical_size)
        self.image_viewer.set_pixmap(pixmap, border_color=TAG_BORDER_COLOR[tag])

        # Enable/disable Motion Photo action
        self.extract_motion_action.setEnabled(self.images_entries[i].is_motion)
        

    def keyPressEvent(self, event: QKeyEvent):
        if not self.images_entries:
            return
        
        key = event.key()
        path = self.images_entries[self.current_index].path
        current_tag = self.images_tags[path]
        new_tag = current_tag


        match key:
            # -------------------------
            # Navigation
            # -------------------------
            case Qt.Key_Right:
                self.action_next_image()

            case Qt.Key_Left:
                self.action_previous_image()

            case Qt.Key_Up:
                self.action_previous_image()

            case Qt.Key_Down:
                self.action_next_image()

            # -------------------------
            # Tagging
            # -------------------------
            case Qt.Key_U:
                new_tag = Tag.UNMARKED

            case Qt.Key_S:
                new_tag = (
                    Tag.UNMARKED
                    if current_tag == Tag.SELECTED
                    else Tag.SELECTED
                )

            case Qt.Key_R:
                new_tag = (
                    Tag.UNMARKED
                    if current_tag == Tag.TO_REMOVE
                    else Tag.TO_REMOVE
                )
        
            case _:
                super().keyPressEvent(event)

        if new_tag != current_tag:
            self.images_tags[path] = new_tag
            # Update list item
            item = self.file_list.item(self.current_index)
            self.update_list_item_visuals(item, new_tag, self.images_entries[self.current_index].is_motion)

            # Update viewer
            self.image_viewer.set_tag_visuals(TAG_BORDER_COLOR[new_tag])


    def update_list_item_visuals(self, item, tag: Tag, is_motion: bool):
        path = item.data(Qt.UserRole)
        emoji = TAG_EMOJI[tag]
        color = TAG_COLOR[tag]
        is_motion_str = "🎥" if is_motion else ""

        item.setText(f"{emoji} {is_motion_str}{path.name}")
        item.setForeground(color)


    def action_next_image(self):
        if self.current_index < len(self.images_entries) - 1:
            self.display_index(self.current_index + 1)


    def action_previous_image(self):
        if self.current_index > 0:
            self.display_index(self.current_index - 1)


    def commit_changes(self):
        plan = self.compute_commit_plan()

        if not plan["copy"] and not plan["move"]:
            QMessageBox.information(self, "Nothing to do", "No tagged images.")
            return

        # Step 4 — Confirmation dialog
        if not self.confirm_commit(plan):
            return

        # Ensure output folders exist
        self.selected_dir.mkdir(exist_ok=True)
        self.to_remove_dir.mkdir(exist_ok=True)

        # Step 5 — Progress dialog
        total = len(plan["copy"]) + len(plan["move"])
        progress = QProgressDialog("Processing...", None, 0, total, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()

        log_lines = []
        log_lines.append("Commit Log")
        log_lines.append("-------------------------")

        done = 0

        # Step 6 — Copy selected
        for src, dst in plan["copy"]:
            try:
                shutil.copy2(src, dst)
                log_lines.append(f"COPY: {src.name} -> selected/")
            except Exception as e:
                log_lines.append(f"ERROR copying {src.name}: {e}")

            done += 1
            progress.setValue(done)
            self.statusBar().showMessage(f"Copying… {done}/{total}")

        # Step 6 — Move removed
        for src, dst in plan["move"]:
            try:
                shutil.move(src, dst)
                log_lines.append(f"MOVE: {src.name} -> to_be_removed/")
            except Exception as e:
                log_lines.append(f"ERROR moving {src.name}: {e}")

            done += 1
            progress.setValue(done)
            self.statusBar().showMessage(f"Moving… {done}/{total}")

        # Step 7 — Write commit log
        log_path = self.source_dir / "commit_log.txt"
        log_path.write_text("\n".join(log_lines), encoding="utf-8")

        progress.close()

        # Step 8 — Final feedback
        QMessageBox.information(self, "Done", "Commit completed successfully.")
        self.statusBar().showMessage("Commit complete.")


    def compute_commit_plan(self):
        self.selected_dir = self.source_dir / "selected"
        self.to_remove_dir = self.source_dir / "to_be_removed"

        plan = {
            "copy": [],        # list of (src, dst)
            "move": [],        # list of (src, dst)
            "collisions": []   # list of dst paths that already exist
        }

        for path, tag in self.images_tags.items():
            if tag == Tag.SELECTED:
                dst = self.selected_dir / path.name
                if dst.exists():
                    plan["collisions"].append(dst)
                plan["copy"].append((path, dst))

            elif tag == Tag.TO_REMOVE:
                dst = self.to_remove_dir / path.name
                if dst.exists():
                    plan["collisions"].append(dst)
                plan["move"].append((path, dst))

        return plan
    

    def confirm_commit(self, plan) -> bool:
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Commit")

        lines = []
        lines.append(f"Copy {len(plan['copy'])} selected images.")
        lines.append(f"Move {len(plan['move'])} images to 'to_be_removed'.")

        if plan["collisions"]:
            lines.append("")
            lines.append("⚠️ Collisions detected:")
            for c in plan["collisions"]:
                lines.append(f" - {c.name}")

        msg.setText("\n".join(lines))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        return msg.exec() == QMessageBox.Ok
    

    def extract_best_frame_from_current(self):
        if not self.images_entries:
            return
        if not self.images_entries[self.current_index].is_motion:
            return
        
        jpeg_path = self.images_entries[self.current_index].path
        mp4_path = extract_motion_video(jpeg_path)
        if not mp4_path:
            QMessageBox.warning(self, "Error", "Could not extract motion video.")
            return

        frames = extract_frames_from_mp4(mp4_path, step=1)
        try:
            os.remove(mp4_path)
        except OSError:
            pass

        if not frames:
            QMessageBox.warning(self, "Error", "No frames found in motion video.")
            return
        
        motion_selection_dialog = MotionPhotoFrameSelectorDialog(frames=frames)
        if motion_selection_dialog.exec() == QDialog.Accepted:
            best_frame = motion_selection_dialog.get_selected_frame()
            best_frame_idx = motion_selection_dialog.current_index
            if best_frame is not None:
                if best_frame_idx == 0:
                    QMessageBox.information(self, "No change", "The first frame is already selected as the best frame.")
                    return
                else:
                    # write the corresponding jpeg file 
                    out_name = f"{jpeg_path.stem}_frame_{best_frame_idx:03d}.jpg"
                    out_path = self.source_dir / out_name
                    cv2.imwrite(str(out_path), best_frame)

                    entry = ImageEntry(out_path, False)
                    self.images_entries.append(entry)
                    self.images_tags[entry.path] = Tag.SELECTED
                    item = QListWidgetItem(entry.path.name)
                    item.setData(Qt.UserRole, entry.path)  # store the full Path object
                    self.file_list.addItem(item)
                    self.update_list_item_visuals(item, self.images_tags[entry.path], entry.is_motion)
                    QMessageBox.information(self, "Frame Extracted", f"{out_name} created and selected")
            else:
                logging.info("No frame was selected by the user.") #code should never get there, but just in case
        else: #QDialog.DialogCode.Accepted
            logging.info("User cancelled motion photo frame selection")

