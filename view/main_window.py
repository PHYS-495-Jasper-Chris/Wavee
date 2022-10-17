"""
The main window
"""

import os
import sys

from typing import List, Optional, Tuple

import pyqtgraph

import numpy as np

from PyQt6 import QtCore, QtWidgets, uic

from equations import PointCharge, Window


class CenterArrowItem(pyqtgraph.ArrowItem):
    """
    An ArrowItem that loads its position from the center, not from the head of the arrow.
    """

    def paint(self, p, *args):
        p.translate(-self.boundingRect().center())
        return super().paint(p, *args)


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window, holding sub-views
    """

    # Type annotations for UI elements
    central_widget: QtWidgets.QWidget
    grid_layout: QtWidgets.QGridLayout
    graph_widget: pyqtgraph.PlotWidget
    point_charge_circle: QtWidgets.QWidget

    def __init__(self) -> None:
        super().__init__()

        uic.load_ui.loadUi(os.path.join(sys.path[0], "view/ui/main_window.ui"), self)

        self.graph_window = Window(
            [PointCharge([1, 4], 10),
             PointCharge([-3, 5], 8),
             PointCharge([0, 1], -5)])

        self._build_plots()

        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        self.show()

    def _build_plots(self,
                     new_point_charges: Optional[List[PointCharge]] = None,
                     max_mag_length: float = 20.0,
                     resolution: int = 2) -> None:

        new_point_charges = new_point_charges or []

        plot_item = self.graph_widget.getPlotItem()
        if not isinstance(plot_item, pyqtgraph.PlotItem):
            raise RuntimeError("Unable to build plot!")
        axes = plot_item.axes
        view_box = plot_item.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox) or not isinstance(axes, dict):
            raise RuntimeError("Unable to build plot")

        for axis in axes:
            plot_item.getAxis(axis).setGrid(255)

        for new_point_charge in new_point_charges:
            self.graph_window.add_point_charge(new_point_charge)

        top_left = [-5, 6]
        bottom_right = [4, -3]

        # Doing all the calculations from zero and just shifting it back after is just so much
        # better

        x_shift = 0 - top_left[0] if top_left[0] < 0 else 0
        y_shift = 0 - bottom_right[1] if bottom_right[1] < 0 else 0

        shifted_top_left = [top_left[0] + x_shift, top_left[1] + y_shift]
        shifted_bottom_right = [bottom_right[0] + x_shift, bottom_right[1] + y_shift]

        x_len = (abs(shifted_top_left[0]) + abs(shifted_bottom_right[0])) * resolution
        y_len = (abs(shifted_top_left[1]) + abs(shifted_bottom_right[1])) * resolution

        p_x = [[0.0] * x_len for _ in range(y_len + 1)]
        p_y = [[0.0] * x_len for _ in range(y_len + 1)]

        mag_x = [[0.0] * x_len for _ in range(y_len + 1)]
        mag_y = [[0.0] * x_len for _ in range(y_len + 1)]
        net_mag = [[0.0] * x_len for _ in range(y_len + 1)]

        for i in range(len(p_x) - 1):
            for j in range(len(p_y) - 1):
                x_pos = i / resolution - x_shift
                y_pos = j / resolution - y_shift
                p_x[i][j] = x_pos
                p_y[i][j] = y_pos

                try:
                    ef_mag_x = self.graph_window.electric_field_x([x_pos, y_pos])
                    ef_mag_y = self.graph_window.electric_field_y([x_pos, y_pos])
                    ef_mag_net = np.sqrt(ef_mag_x**2 + ef_mag_y**2)
                    mag_x[i][j] = ef_mag_x
                    mag_y[i][j] = ef_mag_y
                    net_mag[i][j] = ef_mag_net

                except ZeroDivisionError:
                    pass

        max_mag: float = np.amax(net_mag)
        min_mag: float = np.amin(net_mag)
        min_mag_length = min_mag / max_mag * max_mag_length

        # Plot the vector arrows
        for i in range(len(p_x) - 1):
            for j in range(len(p_y) - 1):
                if net_mag[i][j] <= 0.0:
                    continue

                angle = 180 - np.rad2deg(np.arctan2(mag_y[i][j], mag_x[i][j]))
                normalized_mag = net_mag[i][j] / max_mag
                scaled_mag = normalized_mag * max_mag_length
                brush_color = self.get_color_from_mag(scaled_mag, min_mag_length, max_mag_length)
                arrow_item = CenterArrowItem(pos=(p_x[i][j], p_y[i][j]),
                                             tailLen=scaled_mag,
                                             brush=brush_color,
                                             angle=angle)
                self.graph_widget.addItem(arrow_item)

        # Plot point charges themselves
        scatter_plot_item = pyqtgraph.ScatterPlotItem()
        for point_charge in self.graph_window.charges:
            scatter_plot_item.addPoints(x=[point_charge.position[0]],
                                        y=[point_charge.position[1]],
                                        size=abs(point_charge.charge) * 4,
                                        symbol="o",
                                        brush="r" if point_charge.charge > 0.0 else "b")

        self.graph_widget.addItem(scatter_plot_item)

    def get_color_from_mag(self, mag: float, min_mag_length: float,
                           max_mag_length: float) -> Tuple[int, int, int]:
        """
        Return the color from the given mag. We use 4 different colors to draw brush our vectors
        with:
        blue -> green   | (low magnitude)
        green -> yellow | (med magnitude)
        yellow -> red   | (high magnitude)

        Args:
            mag (float): magnitude of the current vector
            max_mag_length (float): maximum possible magnitude value

        Returns:
            tuple: color to brush the arrow with
        """
        low_mag_color = (0, 255, 0)
        high_mag_color = (255, 255, 0)
        max_mag_color = (255, 0, 0)

        relative_strength = mag / max_mag_length

        # Green -> Yellow
        if relative_strength <= 0.50:
            return self.gradient_color_map(mag,
                                           min_mag_length,
                                           max_mag_length,
                                           min_color=low_mag_color,
                                           max_color=high_mag_color)

        # Yellow -> Red
        return self.gradient_color_map(mag,
                                       min_mag_length,
                                       max_mag_length,
                                       min_color=high_mag_color,
                                       max_color=max_mag_color)

    def gradient_color_map(
        self,
        number: float,
        min_num: float = 0,
        max_num: float = 100,
        min_color: tuple = (0, 0, 255),
        max_color: tuple = (255, 0, 0)
    ) -> Tuple[int, int, int]:
        """
        Takes in a range of numbers and maps it to the expected color given the start and end color
        of a gradient

        Args:
            number (float): given number to get color map of
            min_num (float): Smallest expected value
            max_num (float): Largest expected value
            min_color (tuple): Left most color of gradient
            max_color (tuple): Right most color of gradient

        Returns:
            tuple: R, G, B color as integers
        """

        if number < min_num:
            return min_color

        if number > max_num:
            return max_color

        # easier to have everything start from 0
        min_num = min_num - min_num if min_num > 0 else min_num + min_num
        max_num = max_num - min_num if min_num > 0 else max_num + min_num
        number = number - min_num if min_num > 0 else number + min_num

        # calculate how far to shift each color value
        percent = number / max_num
        r_diff = abs(min_color[0] - max_color[0])
        g_diff = abs(min_color[1] - max_color[1])
        b_diff = abs(min_color[2] - max_color[2])
        r_shift = r_diff * percent
        g_shift = g_diff * percent
        b_shift = b_diff * percent

        r = min_color[0] + r_shift if min_color[0] < max_color[0] else min_color[0] - r_shift
        g = min_color[1] + g_shift if min_color[1] < max_color[1] else min_color[1] - g_shift
        b = min_color[2] + b_shift if min_color[2] < max_color[2] else min_color[2] - b_shift
        return (int(r), int(g), int(b))
