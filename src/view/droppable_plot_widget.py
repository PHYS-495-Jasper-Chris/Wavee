"""
A PlotWidget that can be dropped into.
"""

import sys

from collections import namedtuple
from typing import List, NamedTuple, Optional, Tuple

import pyqtgraph

import numpy as np

from PyQt6 import QtGui, QtWidgets, QtCore

# pylint: disable=import-error
from equations.circle_charge import CircleCharge
from equations.constants import Point2D
from equations.graph_window import Window
from equations.infinite_line_charge import InfiniteLineCharge
from equations.point_charge import PointCharge
from equations.ring_charge import RingCharge
from view.draggable_label import DraggableLabel
# pylint: enable=import-error

RGBTuple = NamedTuple("RGBTuple", [("r", int), ("g", int), ("b", int)])
GraphBounds = NamedTuple("GraphBounds", [("top_left", Point2D), ("bottom_right", Point2D)])


class CenterArrowItem(pyqtgraph.ArrowItem):
    """
    An ArrowItem that loads its position from the center, not from the head of the arrow.
    """

    def paint(self, p: QtGui.QPainter, *args) -> None:
        p.translate(-self.boundingRect().center())
        return super().paint(p, *args)


class DroppablePlotWidget(pyqtgraph.PlotWidget):
    """
    A PlotWidget that can be dropped into.
    """

    DEFAULT_GRAPH_RESOLUTION = 20
    """
    The default number of x-axis points to render.
    """

    def __init__(self,
                 parent: Optional[QtWidgets.QWidget] = None,
                 background: str = 'default',
                 plotItem: Optional[pyqtgraph.PlotItem] = None,
                 **kargs) -> None:
        super().__init__(parent, background, plotItem, **kargs)

        self.setAcceptDrops(True)

        self.aspect_ratio_fixed = True
        """
        Whether the aspect ratio is fixed at 1:1. Calling ``toggle_even_aspect_ratio`` toggles this
        value.
        """

        self.graph_resolution = DroppablePlotWidget.DEFAULT_GRAPH_RESOLUTION
        """
        The number of x-axis points to render.
        """

        self.graph_window = Window([
            PointCharge(Point2D(1, 4), 10),
            PointCharge(Point2D(-3, 5), 8),
            PointCharge(Point2D(0, 1), -5),
            InfiniteLineCharge(3, 2, 1, 0.5),
            InfiniteLineCharge(0, 1, 1, 1),
            InfiniteLineCharge(1, 0, 2, -1),
            CircleCharge(Point2D(1, 2), 2.5, 2.0),
            RingCharge(Point2D(0, 0), 2, 3, -4),
            RingCharge(Point2D(0, 0), 5, 6, -4),
            RingCharge(Point2D(0, 0), 0, 1, 20)
        ])

    def get_pi_vb(self) -> Tuple[pyqtgraph.PlotItem, pyqtgraph.ViewBox]:
        """
        Get the PlotItem & ViewBox.

        Returns:
            Tuple[pyqtgraph.PlotItem, pyqtgraph.ViewBox]: Tuple of the current ``PlotItem`` and the
            current ``ViewBox`` if they exist.

        Raises:
            RuntimeError: An error occurred getting the current PlotItem or ViewBox.
        """

        plot_item = self.getPlotItem()
        if not isinstance(plot_item, pyqtgraph.PlotItem):
            raise RuntimeError("Unable to build plot!")
        view_box = plot_item.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox):
            raise RuntimeError("Unable to rebuild plot")

        return plot_item, view_box

    def dragEnterEvent(self, ev: QtGui.QDragEnterEvent) -> None:  # pylint: disable=invalid-name
        """
        A drag has entered the widget.

        Args:
            ev (QtGui.QDragEnterEvent): The QDragEnterEvent event to handle.
        """

        if ev.mimeData().hasFormat(DraggableLabel.MIME_FORMAT):
            ev.accept()

    def dragMoveEvent(self, ev: QtGui.QDragMoveEvent) -> None:  # pylint: disable=invalid-name
        """
        A drag is moving in the widget.

        Args:
            ev (QtGui.QDragMoveEvent): The QDragMoveEvent event to handle.
        """

        if ev.mimeData().hasFormat(DraggableLabel.MIME_FORMAT):
            ev.accept()

    def dragLeaveEvent(self, ev: QtGui.QDragLeaveEvent) -> None:  # pylint: disable=invalid-name
        """
        A drag left the widget.

        Args:
            ev (QtGui.QDragLeaveEvent): The QDragLeaveEvent event to handle.
        """

        ev.accept()

    def dropEvent(self, ev: QtGui.QDropEvent) -> None:  # pylint: disable=invalid-name
        """
        A drop event has occurred. Forward it to a listening slot in the MainWindow.

        Args:
            ev (QtGui.QDropEvent): The QDropEvent event to handle.
        """

        if not ev.mimeData().hasFormat(DraggableLabel.MIME_FORMAT):
            ev.ignore()

        view_box = self.get_pi_vb()[1]

        mouse_point = view_box.mapSceneToView(ev.position())

        x_pos = mouse_point.x()
        y_pos = mouse_point.y()

        mime_data = ev.mimeData().data(DraggableLabel.MIME_FORMAT)
        label_type = DraggableLabel.LabelTypes(int.from_bytes(mime_data[0], sys.byteorder))

        # Add in the correct charge shape
        if label_type == DraggableLabel.LabelTypes.POINT_CHARGE:
            self.graph_window.add_charge(PointCharge(Point2D(x_pos, y_pos), 1))
        elif label_type == DraggableLabel.LabelTypes.INFINITE_LINE_CHARGE:
            self.graph_window.add_charge(InfiniteLineCharge(1, 0, -x_pos, 1))
        elif label_type == DraggableLabel.LabelTypes.CIRCLE_CHARGE:
            self.graph_window.add_charge(CircleCharge(Point2D(x_pos, y_pos), 1, 1))
        elif label_type == DraggableLabel.LabelTypes.RING_CHARGE:
            self.graph_window.add_charge(RingCharge(Point2D(x_pos, y_pos), 0.5, 1, 1))
        else:
            raise RuntimeWarning(
                f"Unexpected label type {label_type} encountered in DroppablePlotWidget.dropEvent")

        ev.accept()

        # Rebuild the plot after new charge is added.
        self.build_plots(dimensions=self._get_graph_bounds())

        # Open the relevant menu.
        rmv_charge = self.graph_window.charges[-1].open_menu(self.mapToGlobal(ev.position()))
        if rmv_charge:
            self.remove_charge()

        # Rebuild the plots after the menu selections have been made.
        self.build_plots(dimensions=self._get_graph_bounds())

    def build_plots(self,
                    dimensions: Optional[GraphBounds] = None,
                    max_mag_length: float = 20.0) -> None:
        """
        Build the plots of the electric field and the point charges.

        If this is the first time building the plots, add all the points and then autoscale.
        Otherwise, use the provided dimensions (likely from the graph bounds).

        Args:
            dimensions (Optional[GraphBounds]): The dimensions to plot, (top_left, bottom_right).
                Defaults to the range set by the point charges.
            max_mag_length (float): The length of the largest magnitude arrow. Defaults to 20.0.

        Raises:
            RuntimeError: The plot or axes are invalid.
        """

        should_autoscale = dimensions is None

        plot_item, view_box = self.get_pi_vb()
        axes = plot_item.axes
        if not isinstance(axes, dict):
            raise RuntimeError("Unable to build plot!")

        # Disable autoscaling before adding items to graph for improved performance
        view_box.disableAutoRange()

        # Remove old graphs
        plot_item.clear()

        for axis in axes:
            plot_item.getAxis(axis).setGrid(255)

        default_dimensions = self._plot_charges()

        # Build the dimensions based solely on the charges, or the provided dimensions.
        dimensions = dimensions or default_dimensions

        # Draw arrows at uniform test points based current view and resolution
        top_left = dimensions.top_left
        bottom_right = dimensions.bottom_right

        x_indices = self.graph_resolution
        y_indices = max(int(self.height() / self.width() * x_indices), 1)

        x_distance = bottom_right.x - top_left.x
        y_distance = top_left.y - bottom_right.y

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

            x_pos = x_percentage * x_distance + top_left.x

            for j in range(y_indices):
                try:
                    y_percentage = j / (y_indices - 1)
                except ZeroDivisionError:
                    y_percentage = 0.5

                y_pos = y_percentage * y_distance + bottom_right.y

                p_x[i][j] = x_pos
                p_y[i][j] = y_pos

                try:
                    ef_mag_x = self.graph_window.electric_field_x(Point2D(x_pos, y_pos))
                    ef_mag_y = self.graph_window.electric_field_y(Point2D(x_pos, y_pos))
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

        net_mag_idx = [[0] * y_indices for _ in range(x_indices)]
        for idx, mag_idx in enumerate(flat_arr):
            # Now build mapping from unsorted net_mag array to sorted array
            net_mag_idx[mag_idx.x][mag_idx.y] = idx

        # Plot the vector arrows
        for i in range(x_indices):
            for j in range(y_indices):
                if net_mag[i][j] <= 0.0:
                    continue

                angle = 180 - np.rad2deg(np.arctan2(mag_y[i][j], mag_x[i][j]))
                normalized_mag = net_mag[i][j] / flat_arr[-1].magnitude
                scaled_mag = normalized_mag * max_mag_length
                brush_color = self._get_color_from_mag(net_mag_idx[i][j], len(flat_arr))
                arrow_item = CenterArrowItem(pos=(p_x[i][j], p_y[i][j]),
                                             tailLen=scaled_mag,
                                             brush=brush_color,
                                             angle=angle)
                self.addItem(arrow_item)

        if should_autoscale:
            # Enable autoscaling if no dimension set.
            view_box.enableAutoRange()

    def reset_resolution(self) -> None:
        """
        Reset the graph resolution and rebuild the plots based on currently viewable dimensions.
        """

        self.graph_resolution = DroppablePlotWidget.DEFAULT_GRAPH_RESOLUTION
        self.build_plots(dimensions=self._get_graph_bounds())

    def increase_resolution(self) -> None:
        """
        Increase the graph resolution by 1 and rebuild the plots based on currently viewable
        dimensions.
        """

        self.graph_resolution += 1
        self.build_plots(dimensions=self._get_graph_bounds())

    def decrease_resolution(self) -> None:
        """
        Decrease the graph resolution by 1 (keeping above 0) and rebuild the plots based on
        currently viewable dimensions.
        """

        self.graph_resolution -= 1
        self.graph_resolution = max(self.graph_resolution, 0)
        self.build_plots(dimensions=self._get_graph_bounds())

    def refresh_button_pressed(self) -> None:
        """
        When the refresh button is pressed, reload the graphs, keeping the resolution the same and
        updating the dimensions.
        """

        # Regenerate the plots with the new positions (and same charges)
        self.build_plots(dimensions=self._get_graph_bounds())

    def center_origin(self) -> None:
        """
        Center the ViewBox around the origin without changing the scale factors.
        """

        view_box = self.get_pi_vb()[1]

        # Ideally, our bounds would be centered around [0, 0], so that
        # (bottom_right_x + top_left_x == 0) and (top_left_y + bottom_right_y == 0).
        # This means we need to shift left by half the x component and down by half the y component.

        current_bounds = self._get_graph_bounds()
        x_component = current_bounds.bottom_right.x + current_bounds.top_left.x
        y_component = current_bounds.top_left.y + current_bounds.bottom_right.y

        view_box.translateBy((-x_component / 2, -y_component / 2))

    def default_range(self) -> None:
        """
        Rebuild the graphs at the default position (ie, with autogenerated dimensions).
        """

        self.build_plots()

    def toggle_even_aspect_ratio(self) -> None:
        """
        Toggle requiring the aspect ratio to be 1:1 so that circles are properly shaped.
        """

        view_box = self.get_pi_vb()[1]
        view_box.setAspectLocked(self.aspect_ratio_fixed, 1)

        self.aspect_ratio_fixed = not self.aspect_ratio_fixed

    def remove_charge(self) -> None:
        """
        Remove the last charge added, and rebuild the graphs.
        """

        self.graph_window.remove_last_charge()

        self.build_plots(dimensions=self._get_graph_bounds())

    def undo_remove_charge(self) -> None:
        """
        Undo the latest removal, and rebuild the graphs.
        """

        self.graph_window.undo_charge_removal()

        self.build_plots(dimensions=self._get_graph_bounds())

    def _plot_charges(self) -> GraphBounds:
        """
        Plot the charges themselves.
        """

        leftmost, rightmost, topmost, bottommost = np.inf, -np.inf, -np.inf, np.inf

        # Plot all charges
        for charge in self.graph_window.charges:

            # Point charges
            if isinstance(charge, PointCharge):
                radius = abs(charge.charge) / 5

                leftmost = min(leftmost, charge.position.x - radius)
                rightmost = max(rightmost, charge.position.x + radius)
                topmost = max(topmost, charge.position.y + radius)
                bottommost = min(bottommost, charge.position.y - radius)

                ellipse_item = QtWidgets.QGraphicsEllipseItem(charge.position.x - radius,
                                                              charge.position.y - radius,
                                                              radius * 2, radius * 2)
                ellipse_item.setBrush(
                    QtCore.Qt.GlobalColor.red if charge.charge > 0 else QtCore.Qt.GlobalColor.blue)
                ellipse_item.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
                ellipse_item.pen().setWidth(0)
                self.addItem(ellipse_item)

            # Infinite Line charges
            elif isinstance(charge, InfiniteLineCharge):
                if charge.y_coef == 0:
                    # ax + c = 0 -> x = -c/a
                    pos = Point2D(-charge.offset / charge.x_coef, 0)

                    leftmost = min(leftmost, pos.x)
                    rightmost = max(rightmost, pos.x)
                else:
                    # ax + by + c = 0 -> y = -a/b*x - c/b
                    pos = Point2D(0, -charge.offset / charge.y_coef)

                    if charge.x_coef == 0:
                        topmost = max(topmost, pos.y)
                        bottommost = min(bottommost, pos.y)

                angle = np.rad2deg(np.arctan2(-charge.x_coef, charge.y_coef))
                line_plot_item = pyqtgraph.InfiniteLine(
                    pos=pos,
                    angle=angle,
                    pen={
                        "color": "r" if charge.charge_density > 0 else "b",
                        "width": 4
                    })

                self.addItem(line_plot_item)

            # Circle charges
            elif isinstance(charge, CircleCharge):
                leftmost = min(leftmost, charge.center.x - charge.outer_radius)
                rightmost = max(rightmost, charge.center.x + charge.outer_radius)
                topmost = max(topmost, charge.center.y + charge.outer_radius)
                bottommost = min(bottommost, charge.center.y - charge.outer_radius)

                ellipse_item = QtWidgets.QGraphicsEllipseItem(charge.center.x - charge.outer_radius,
                                                              charge.center.y - charge.outer_radius,
                                                              charge.outer_radius * 2,
                                                              charge.outer_radius * 2)
                ellipse_item.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
                ellipse_item.pen().setWidth(0)
                brush = (QtGui.QColor(255, 0, 0, alpha=128)
                         if charge.charge_density > 0 else QtGui.QColor(0, 0, 255, alpha=128))
                ellipse_item.setBrush(brush)
                self.addItem(ellipse_item)

            # Ring charges
            elif isinstance(charge, RingCharge):
                leftmost = min(leftmost, charge.center.x - charge.outer_radius)
                rightmost = max(rightmost, charge.center.x + charge.outer_radius)
                topmost = max(topmost, charge.center.y + charge.outer_radius)
                bottommost = min(bottommost, charge.center.y - charge.outer_radius)

                middle_radii = (charge.outer_radius + charge.inner_radius) / 2
                ellipse_item = QtWidgets.QGraphicsEllipseItem(charge.center.x - middle_radii,
                                                              charge.center.y - middle_radii,
                                                              middle_radii * 2, middle_radii * 2)
                pen_color = (QtGui.QColor(255, 0, 0, alpha=128)
                             if charge.charge_density > 0 else QtGui.QColor(0, 0, 255, alpha=128))
                ellipse_item.setPen(QtGui.QPen(pen_color,
                                               charge.outer_radius - charge.inner_radius))
                ellipse_item.setBrush(QtGui.QColor(0, 0, 0, alpha=0))  # transparent
                self.addItem(ellipse_item)
            else:
                raise RuntimeWarning(f"Unexpected charge type {type(charge)}")

        dimensions = None

        if False in np.isfinite([leftmost, rightmost, topmost, bottommost]):
            dimensions = GraphBounds(Point2D(-1, 1), Point2D(1, -1))

        rightmost = max(rightmost, leftmost + 1.0)
        topmost = max(topmost, bottommost + 1)

        return dimensions or GraphBounds(Point2D(leftmost, topmost), Point2D(rightmost, bottommost))

    def _get_graph_bounds(self) -> GraphBounds:
        """
        Get the top left and bottom right corners of the graph.

        Returns:
            GraphBounds: A GraphBounds tuple of the top left point and the bottom right point of the
            currently viewable section of the graph.
        """

        view_box = self.get_pi_vb()[1]

        # Get the plot dimensions
        view_range: List[List[float]] = view_box.viewRange()
        top_left = Point2D(view_range[0][0], view_range[1][1])
        bottom_right = Point2D(view_range[0][1], view_range[1][0])

        return GraphBounds(top_left, bottom_right)

    def _get_color_from_mag(self, index: int, length: int) -> RGBTuple:
        """
        Return the color from the given index. We use 3 different colors to draw brush our vectors
        with:
        green -> yellow | (low magnitude)
        yellow -> red   | (high magnitude)

        Args:
            index (int): The index into the sorted array.
            length (int): The length of the sorted array.

        Returns:
            RGBTuple: An RGBTuple of R, G, B colors to brush the arrow with.
        """

        low_mag_color = RGBTuple(0, 255, 0)
        med_mag_color = RGBTuple(255, 255, 0)
        high_mag_color = RGBTuple(255, 0, 0)

        percentile = (index + 1) / length

        # Green -> Yellow
        if percentile <= 0.50:
            return self._gradient_color_map(percentile * 2, low_mag_color, med_mag_color)

        # Yellow -> Red
        return self._gradient_color_map((percentile - 0.50) * 2, med_mag_color, high_mag_color)

    def _gradient_color_map(self, percentile: float, min_color: RGBTuple,
                            max_color: RGBTuple) -> RGBTuple:
        """
        Takes in a percentile of an array and maps it to the expected color given the start and end
        color of a gradient.

        Args:
            percentile (float): The percentile of this index.
            min_color (RGBTuple): Left most color of gradient.
            max_color (RGBTuple): Right most color of gradient.

        Returns:
            RGBTuple: An RGBTuple of R, G, B colors as integers.
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

        r = min_color.r - r_shift
        g = min_color.g - g_shift
        b = min_color.b - b_shift
        return RGBTuple(int(r), int(g), int(b))
