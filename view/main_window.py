"""
The main window
"""

import os
import sys

from collections import namedtuple
from typing import List, Optional, Tuple

import pyqtgraph

import numpy as np

from PyQt6 import QtCore, QtWidgets, QtGui, uic

# pylint: disable=import-error
from equations import InfiniteLineCharge, PointCharge, Window
from view.droppable_plot_widget import DroppablePlotWidget
from view.draggable_label import DraggableLabel
# pylint: enable=import-error

RGBTuple = namedtuple("RGBTuple", ["r", "g", "b"])
GraphBounds = namedtuple("GraphBounds", ["top_left", "bottom_right"])


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
    point_charge_circle: DraggableLabel
    line_charge_drawing: DraggableLabel
    refresh_button: QtWidgets.QPushButton
    menu_bar: QtWidgets.QMenuBar
    status_bar = QtWidgets.QStatusBar

    DEFAULT_GRAPH_RESOLUTION = 20
    """
    The default number of x-axis points to render.
    """

    def __init__(self) -> None:
        super().__init__()

        self.graph_resolution = MainWindow.DEFAULT_GRAPH_RESOLUTION

        uic.load_ui.loadUi(os.path.join(sys.path[0], "view/ui/main_window.ui"), self)
        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)

        self.graph_window = Window(
            charges=[PointCharge([1, 4], 10),
                     PointCharge([-3, 5], 8),
                     PointCharge([0, 1], -5)],
            infinite_line_charges=[
                InfiniteLineCharge(3, 2, 1, 0.5),
                InfiniteLineCharge(0, 1, 1, 1),
                InfiniteLineCharge(1, 0, 2, -1)
            ])
        self.refresh_button.clicked.connect(self._refresh_button_pressed)

        graph_menu = self.menu_bar.addMenu("Graph")
        refresh_graph_action = graph_menu.addAction("Refresh Graph")
        refresh_graph_action.setShortcuts(["Ctrl+R", "F5"])
        refresh_graph_action.triggered.connect(self._refresh_button_pressed)

        increase_graph_resolution = graph_menu.addAction("Increase resolution", "Ctrl+=")
        increase_graph_resolution.triggered.connect(self._increase_resolution)

        decrease_graph_resolution = graph_menu.addAction("Decrease resolution", "Ctrl+-")
        decrease_graph_resolution.triggered.connect(self._decrease_resolution)

        reset_graph_resolution = graph_menu.addAction("Reset resolution", "Ctrl+0")
        reset_graph_resolution.triggered.connect(self._reset_resolution)

        self.proxy = pyqtgraph.SignalProxy(self.graph_widget.scene().sigMouseMoved,
                                           rateLimit=60,
                                           slot=self._mouse_moved)

        self._paint_shapes()
        self._build_plots()

        self.show()

    def _paint_shapes(self):
        """
        Create a circle for the point charge.

        Will also be used to draw other shapes.
        """

        # Paint circle
        canvas = QtGui.QPixmap(110, 110)
        canvas.fill(self.palette().color(self.backgroundRole()))

        painter = QtGui.QPainter(canvas)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        pen = QtGui.QPen()
        pen.setWidth(5)
        pen.setColor(QtGui.QColor("red"))
        painter.setPen(pen)
        painter.drawEllipse(5, 5, 100, 100)
        painter.end()

        self.point_charge_circle.setPixmap(canvas)
        self.point_charge_circle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.point_charge_circle.label_type = DraggableLabel.LabelTypes.PointCharge

        # Paint straight line
        canvas = QtGui.QPixmap(110, 110)
        canvas.fill(self.palette().color(self.backgroundRole()))

        painter = QtGui.QPainter(canvas)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        pen = QtGui.QPen()
        pen.setWidth(5)
        pen.setColor(QtGui.QColor("red"))
        painter.setPen(pen)
        painter.drawLine(55, 5, 55, 100)
        painter.end()

        self.line_charge_drawing.setPixmap(canvas)
        self.line_charge_drawing.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.line_charge_drawing.label_type = DraggableLabel.LabelTypes.InfiniteLineCharge

    def _reset_resolution(self):
        self.graph_resolution = MainWindow.DEFAULT_GRAPH_RESOLUTION
        self._build_plots(dimensions=self._get_graph_bounds(), resolution=self.graph_resolution)

    def _increase_resolution(self):
        self.graph_resolution += 1
        self._build_plots(dimensions=self._get_graph_bounds(), resolution=self.graph_resolution)

    def _decrease_resolution(self):
        self.graph_resolution -= 1
        self.graph_resolution = max(self.graph_resolution, 0)
        self._build_plots(dimensions=self._get_graph_bounds(), resolution=self.graph_resolution)

    def _get_graph_bounds(self) -> GraphBounds:
        """
        Get the top left and bottom right corners of the graph.
        """

        plot_item = self.graph_widget.getPlotItem()
        if not isinstance(plot_item, pyqtgraph.PlotItem):
            raise RuntimeError("Unable to build plot!")
        view_box = plot_item.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox):
            raise RuntimeError("Unable to rebuild plot")

        # Get the plot dimensions
        view_range: List[List[float]] = view_box.viewRange()
        top_left = [view_range[0][0], view_range[1][1]]
        bottom_right = [view_range[0][1], view_range[1][0]]

        return GraphBounds(top_left, bottom_right)

    def _refresh_button_pressed(self):
        """
        When the refresh button is pressed, reload the graphs, keeping the
        resolution the same and updating the dimensions.
        """

        # Regenerate the plots with the new positions (and same charges)
        self._build_plots(dimensions=self._get_graph_bounds(), resolution=self.graph_resolution)

    def _build_plots(self,
                     dimensions: Optional[GraphBounds] = None,
                     new_point_charges: Optional[List[PointCharge]] = None,
                     max_mag_length: float = 20.0,
                     resolution: int = DEFAULT_GRAPH_RESOLUTION) -> None:
        """
        Build the plots of the electric field and the point charges.

        @param dimensions The dimensions to plot, (top_left, bottom_right). Defaults to
               ([-5, 6], [4, -3])
        @param new_point_charges Any additional point charges to add to the Window. Defaults to no
               new charges
        @param max_mag_length The length of the largest magnitude arrow. Defaults to 20.0
        @param resolution The number of x-axis arrows to plot. Defaults to DEFAULT_GRAPH_RESOLUTION
        """

        should_autoscale = dimensions is None

        new_point_charges = new_point_charges or []
        dimensions = dimensions or GraphBounds([-5.0, 6.0], [4.0, -3.0])

        plot_item = self.graph_widget.getPlotItem()
        if not isinstance(plot_item, pyqtgraph.PlotItem):
            raise RuntimeError("Unable to build plot!")
        axes = plot_item.axes
        view_box = plot_item.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox) or not isinstance(axes, dict):
            raise RuntimeError("Unable to build plot")

        # Disable autoscaling if we are manually setting our dimensions
        if should_autoscale:
            view_box.enableAutoRange()
        else:
            view_box.disableAutoRange()

        # Remove old graphs
        plot_item.clear()

        for axis in axes:
            plot_item.getAxis(axis).setGrid(255)

        for new_point_charge in new_point_charges:
            self.graph_window.add_point_charge(new_point_charge)

        # Plot point charges themselves
        scatter_plot_item = pyqtgraph.ScatterPlotItem()
        for point_charge in self.graph_window.charges:
            scatter_plot_item.addPoints(x=[point_charge.position[0]],
                                        y=[point_charge.position[1]],
                                        size=abs(point_charge.charge) * 4,
                                        symbol="o",
                                        brush="r" if point_charge.charge > 0.0 else "b")

        self.graph_widget.addItem(scatter_plot_item)

        for line_charge in self.graph_window.infinite_line_charges:
            if line_charge.y_coef == 0:
                # ax + c = 0 -> x = -c/a
                pos = (-line_charge.offset / line_charge.x_coef, 0)
            else:
                # ax + by + c = 0 -> y = -a/b*c - c/b
                pos = (0, -line_charge.offset / line_charge.y_coef)

            angle = np.rad2deg(np.arctan2(-line_charge.x_coef, line_charge.y_coef))
            line_plot_item = pyqtgraph.InfiniteLine(
                pos=pos,
                angle=angle,
                pen={
                    "color": "r" if line_charge.charge_density > 0 else "b",
                    "width": 4
                })

            self.graph_widget.addItem(line_plot_item)

        top_left: List[float] = dimensions.top_left
        bottom_right: List[float] = dimensions.bottom_right

        x_indices = resolution
        y_indices = max(int(self.graph_widget.height() / self.graph_widget.width() * resolution), 1)

        x_distance = bottom_right[0] - top_left[0]
        y_distance = top_left[1] - bottom_right[1]

        p_x = [[0.0] * y_indices for _ in range(x_indices)]
        p_y = [[0.0] * y_indices for _ in range(x_indices)]

        mag_x = [[0.0] * y_indices for _ in range(x_indices)]
        mag_y = [[0.0] * y_indices for _ in range(x_indices)]
        net_mag = [[0.0] * y_indices for _ in range(x_indices)]

        for i in range(x_indices):
            try:
                x_percentage = i / (x_indices - 1)
            except ZeroDivisionError:
                x_percentage = 0.5

            x_pos = x_percentage * x_distance + top_left[0]

            for j in range(y_indices):
                try:
                    y_percentage = j / (y_indices - 1)
                except ZeroDivisionError:
                    y_percentage = 0.5

                y_pos = y_percentage * y_distance + bottom_right[1]

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

        # Build sorted array holding indexes of magnitude
        MagIndexes = namedtuple("MagIndexes", ["magnitude", "x", "y"])
        flat_arr: List[MagIndexes] = []
        for i in range(x_indices):
            for j in range(y_indices):
                flat_arr.append(MagIndexes(net_mag[i][j], i, j))

        flat_arr.sort(key=lambda mag_idx: mag_idx.magnitude)

        net_mag_idx = [[(0.0, int(0))] * y_indices for _ in range(x_indices)]

        for idx, mag_idx in enumerate(flat_arr):
            # Now build mapping from unsorted net_mag array to sorted array
            net_mag_idx[mag_idx.x][mag_idx.y] = (mag_idx.magnitude, idx)

        if len(flat_arr) > 0:
            max_mag: float = np.amax(net_mag)
        else:
            max_mag = 1.0

        # Plot the vector arrows
        for i in range(x_indices):
            for j in range(y_indices):
                if net_mag[i][j] <= 0.0:
                    continue

                sorted_idx = net_mag_idx[i][j][1]

                angle = 180 - np.rad2deg(np.arctan2(mag_y[i][j], mag_x[i][j]))
                normalized_mag = net_mag[i][j] / max_mag
                scaled_mag = normalized_mag * max_mag_length
                brush_color = self.get_color_from_mag(sorted_idx, len(flat_arr))
                arrow_item = CenterArrowItem(pos=(p_x[i][j], p_y[i][j]),
                                             tailLen=scaled_mag,
                                             brush=brush_color,
                                             angle=angle)
                self.graph_widget.addItem(arrow_item)

    def _mouse_moved(self, event):
        pos = event[0]
        if self.graph_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.graph_widget.getPlotItem().getViewBox().mapSceneToView(pos)
            x_pos = mouse_point.x()
            y_pos = mouse_point.y()
            ef_mag_x = self.graph_window.electric_field_x([x_pos, y_pos])
            ef_mag_y = self.graph_window.electric_field_y([x_pos, y_pos])
            ef_mag_net = np.sqrt(ef_mag_x**2 + ef_mag_y**2)

            x_fs = "e" if abs(x_pos) > 1e5 else "f"
            y_fs = "e" if abs(y_pos) > 1e5 else "f"
            text = f"X: {x_pos:+.2{x_fs}} Y: {y_pos:+.2{y_fs}} Magnitude: {ef_mag_net:.6g}"

            self.graph_widget.setToolTip(text)
            self.status_bar.showMessage(text)

    def get_color_from_mag(self, index: int, max_index: int) -> Tuple[int, int, int]:
        """
        Return the color from the given index. We use 3 different colors to draw brush our vectors
        with:
        green -> yellow | (low magnitude)
        yellow -> red   | (high magnitude)

        Args:
            index (int): The index into the sorted array
            max_index (int): The length of the sorted array

        Returns:
            tuple: color to brush the arrow with
        """

        low_mag_color = RGBTuple(0, 255, 0)
        med_mag_color = RGBTuple(255, 255, 0)
        high_mag_color = RGBTuple(255, 0, 0)

        percentile = (index + 1) / max_index

        # Green -> Yellow
        if percentile <= 0.50:
            return self.gradient_color_map(percentile * 2, low_mag_color, med_mag_color)

        # Yellow -> Red
        return self.gradient_color_map((percentile - 0.50) * 2, med_mag_color, high_mag_color)

    def gradient_color_map(self, percentile: float, min_color: RGBTuple,
                           max_color: RGBTuple) -> RGBTuple:
        """
        Takes in a percentile of an array and maps it to the expected color given the start and end
        color of a gradient

        Args:
            percentile (float): The percentile of this index
            min_color (tuple): Left most color of gradient
            max_color (tuple): Right most color of gradient

        Returns:
            tuple: R, G, B color as integers
        """

        if percentile <= 0.0:
            return min_color

        if percentile >= 1.0:
            return max_color

        # calculate how far to shift each color value
        r_diff = min_color.r - max_color.r
        g_diff = min_color.g - max_color.g
        b_diff = min_color.b - max_color.b
        r_shift = r_diff * percentile
        g_shift = g_diff * percentile
        b_shift = b_diff * percentile

        r = min_color[0] - r_shift
        g = min_color[1] - g_shift
        b = min_color[2] - b_shift
        return RGBTuple(int(r), int(g), int(b))
