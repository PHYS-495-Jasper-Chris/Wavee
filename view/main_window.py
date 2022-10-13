"""
The main window
"""

import os
import sys

from typing import List

import pyqtgraph

import numpy as np

from PyQt6 import QtCore, QtWidgets, uic

from equations import PointCharge, Window


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

        a = PointCharge([10, 7], 10)
        b = PointCharge([-3, 5], 8)

        self.graph_window = Window([a, b, PointCharge([0, 1], -5)])

        self._build_plots()

        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        self.show()

    def _build_plots(self, new_point_charges: List[PointCharge] = []) -> None:
        for new_point_charge in new_point_charges:
            self.graph_window.add_point_charge(new_point_charge)

        top_left = [-10, 10]
        bottom_right = [10, -10]
        x_len = abs(top_left[0]) + abs(bottom_right[0])
        y_len = abs(top_left[1]) + abs(bottom_right[1])

        p_x = [[0.0] * x_len for _ in range(y_len + 1)]
        p_y = [[0.0] * x_len for _ in range(y_len + 1)]

        mag_x = [[0.0] * x_len for _ in range(y_len + 1)]
        mag_y = [[0.0] * x_len for _ in range(y_len + 1)]

        for i in range(top_left[0], bottom_right[0] + 1):
            for j in range(bottom_right[1], top_left[1] + 1):
                p_x[i][j] = i
                p_y[i][j] = j
                try:
                    mag_x[i][j] = self.graph_window.electric_field_x([i, j])
                    mag_y[i][j] = self.graph_window.electric_field_y([i, j])

                except ZeroDivisionError:
                    mag_x[i][j] = 0
                    mag_y[i][j] = 0

        for i in range(y_len + 1):
            for j in range(x_len):
                x_m, y_m = mag_x[i][j], mag_y[i][j]
                angle = np.rad2deg(np.arctan2(y_m, x_m))
                magnitude = np.sqrt(x_m**2 + y_m**2) / 1000000000

                ai = pyqtgraph.ArrowItem(pos=(p_x[i][j], p_y[i][j]), tailLen=magnitude, angle=angle)
                self.graph_widget.addItem(ai)

        # Plot point charges themselves
        scatter_plot_item = pyqtgraph.ScatterPlotItem()
        for point_charge in self.graph_window.charges:
            scatter_plot_item.addPoints(x=[point_charge.position[0]],
                                        y=[point_charge.position[1]],
                                        size=abs(point_charge.charge) * 4,
                                        symbol="o",
                                        brush="r" if point_charge.charge > 0.0 else "b")

        self.graph_widget.addItem(scatter_plot_item)
