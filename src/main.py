"""
Instantiate the graphical user interface.
"""

import ctypes
import os
import sys

from PyQt6 import QtCore, QtWidgets, QtGui

from view.main_window import MainWindow


def main():
    """
    Start the graphical user interface.
    """

    app = QtWidgets.QApplication(sys.argv)

    # Disable all Qt messages
    QtCore.qInstallMessageHandler(lambda _, __, ___: None)

    # Set icon
    icon_path = os.path.join(sys.path[0], "../images/logo.png")
    icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(icon)

    # Fix icon on windows machines
    if sys.platform == "win32":
        win_app_id = "PHYS495.wavee"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(win_app_id)

    _ = MainWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
