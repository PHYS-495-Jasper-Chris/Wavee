"""
Instantiate the graphical user interface.
"""

import sys

from PyQt6 import QtWidgets, QtCore

from view.main_window import MainWindow


def main():
    """
    Start the graphical user interface.
    """

    app = QtWidgets.QApplication(sys.argv)

    # Disable all Qt messages
    QtCore.qInstallMessageHandler(lambda _, __, ___: None)

    _ = MainWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
