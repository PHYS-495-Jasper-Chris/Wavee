"""
The main window
"""

import os
import sys

import pyqtgraph

from PyQt6 import QtCore, QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window, holding subviews
    """

    # Type annotations for UI elements
    central_widget: QtWidgets.QWidget
    grid_layout: QtWidgets.QGridLayout
    graph_widget: pyqtgraph.PlotWidget
    point_charge_circle: QtWidgets.QWidget

    def __init__(self) -> None:
        super().__init__()

        uic.load_ui.loadUi(os.path.join(sys.path[0], "view/ui/main_window.ui"), self)

        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        self.show()
