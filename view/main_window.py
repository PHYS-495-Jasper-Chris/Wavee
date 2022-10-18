"""
The main window
"""

import os
import sys

from typing import List, Optional, Tuple

import pyqtgraph

import numpy as np

from PyQt6 import QtCore, QtWidgets, QtGui, uic

from equations import PointCharge, Window
from view.droppable_plot_widget import DroppablePlotWidget

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
    graph_widget: DroppablePlotWidget
    point_charge_circle: QtWidgets.QLabel
    refresh_button: QtWidgets.QPushButton
    menu_bar: QtWidgets.QMenuBar

    def __init__(self) -> None:
        super().__init__()

        uic.load_ui.loadUi(os.path.join(sys.path[0], "view/ui/main_window.ui"), self)
        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)

        self.graph_window = Window(
            [PointCharge([1, 4], 10),
             PointCharge([-3, 5], 8),
             PointCharge([0, 1], -5)])
        self.refresh_button.clicked.connect(self._refresh_button_pressed)

        graph_menu = self.menu_bar.addMenu("Graph")
        refresh_graph_action = graph_menu.addAction("Refresh Graph")
        refresh_graph_action.setShortcuts(["Ctrl+R", "F5"])
        refresh_graph_action.triggered.connect(self._refresh_button_pressed)

        self._paint_shapes()
        self._build_plots()

        self.show()

    def _paint_shapes(self):
        """
        Create a circle for the point charge.

        Will also be used to draw other shapes.
        """

        canvas = QtGui.QPixmap(110, 110)

        painter = QtGui.QPainter(canvas)
        pen = QtGui.QPen()
        pen.setWidth(5)
        pen.setColor(QtGui.QColor('red'))
        painter.setPen(pen)
        painter.drawEllipse(5, 5, 100, 100)
        painter.end()

        self.point_charge_circle.setPixmap(canvas)

    def _refresh_button_pressed(self):
        """
        When the refresh button is pressed, reload the graphs
        """

        plot_item = self.graph_widget.getPlotItem()
        if not isinstance(plot_item, pyqtgraph.PlotItem):
            raise RuntimeError("Unable to build plot!")
        view_box = plot_item.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox):
            raise RuntimeError("Unable to rebuild plot")

        # Get the plot dimensions
        view_range: List[List[float]] = view_box.getState()["viewRange"]
        top_left = [view_range[0][0], view_range[1][1]]
        bottom_right = [view_range[0][1], view_range[1][0]]

        # Don't change the scale
        view_box.disableAutoRange()

        # Regenerate the plots with the new positions (and same charges)
        self._build_plots(dimensions=(top_left, bottom_right))

    def _build_plots(self,
                     dimensions: Optional[Tuple[List[float], List[float]]] = None,
                     new_point_charges: Optional[List[PointCharge]] = None,
                     max_mag_length: float = 20.0,
                     resolution: int = 20) -> None:
        """
        Build the plots of the electric field and the point charges.

        @param dimensions The dimensions to plot, (top_left, bottom_right). Defaults to
               ([-5, 6], [4, -3])
        @param new_point_charges Any additional point charges to add to the Window. Defaults to no
               new charges
        @param max_mag_length The length of the largest magnitude arrow. Defaults to 20.0
        @param resolution The number of x-axis arrows to plot. Defaults to 20
        """

        new_point_charges = new_point_charges or []
        dimensions = dimensions or ([-5.0, 6.0], [4.0, -3.0])

        plot_item = self.graph_widget.getPlotItem()
        if not isinstance(plot_item, pyqtgraph.PlotItem):
            raise RuntimeError("Unable to build plot!")
        axes = plot_item.axes
        view_box = plot_item.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox) or not isinstance(axes, dict):
            raise RuntimeError("Unable to build plot")

        plot_item.clear()

        for axis in axes:
            plot_item.getAxis(axis).setGrid(255)

        for new_point_charge in new_point_charges:
            self.graph_window.add_point_charge(new_point_charge)

        top_left = dimensions[0]
        bottom_right = dimensions[1]

        x_indices = resolution
        y_indices = int(self.graph_widget.height() / self.graph_widget.width() * resolution)

        x_distance = bottom_right[0] - top_left[0]
        y_distance = top_left[1] - bottom_right[1]

        p_x = [[0.0] * y_indices for _ in range(x_indices)]
        p_y = [[0.0] * y_indices for _ in range(x_indices)]

        mag_x = [[0.0] * y_indices for _ in range(x_indices)]
        mag_y = [[0.0] * y_indices for _ in range(x_indices)]
        net_mag = [[0.0] * y_indices for _ in range(x_indices)]

        for i in range(x_indices):
            for j in range(y_indices):
                x_pos = (i / (x_indices - 1)) * x_distance + top_left[0]
                y_pos = (j / (y_indices - 1)) * y_distance + bottom_right[1]
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
        for i in range(x_indices):
            for j in range(y_indices):
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

        self.proxy = pyqtgraph.SignalProxy(self.graph_widget.scene().sigMouseMoved,
                                           rateLimit=60,
                                           slot=self._mouse_moved)

        self.graph_widget.addItem(scatter_plot_item)

    def _mouse_moved(self, event):
        pos = event[0]
        if self.graph_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.graph_widget.getPlotItem().getViewBox().mapSceneToView(pos)
            x_pos = mouse_point.x()
            y_pos = mouse_point.y()
            ef_mag_x = self.graph_window.electric_field_x([x_pos, y_pos])
            ef_mag_y = self.graph_window.electric_field_y([x_pos, y_pos])
            ef_mag_net = np.sqrt(ef_mag_x**2 + ef_mag_y**2)

            self.graph_widget.setToolTip(
                f"({round(x_pos,2)},{round(y_pos,2)}) - value: {ef_mag_net:.6g}")

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
        number -= min_num
        max_num -= min_num

        # calculate how far to shift each color value
        percent = number / max_num
        r_diff = min_color[0] - max_color[0]
        g_diff = min_color[1] - max_color[1]
        b_diff = min_color[2] - max_color[2]
        r_shift = r_diff * percent
        g_shift = g_diff * percent
        b_shift = b_diff * percent

        r = min_color[0] - r_shift
        g = min_color[1] - g_shift
        b = min_color[2] - b_shift
        return (int(r), int(g), int(b))
