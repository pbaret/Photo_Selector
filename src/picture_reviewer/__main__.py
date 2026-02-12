import logging
import sys
from PySide6.QtWidgets import QApplication
from .ui.main_window import MainWindow


def main() -> None:
    """Main entry point for the application."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Starting Picture Reviewer")

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
