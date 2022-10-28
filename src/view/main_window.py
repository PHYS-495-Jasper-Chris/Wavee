"""
The main window.
"""

import os
import sys

from typing import Tuple

import pyqtgraph

import numpy as np

from PyQt6 import QtCore, QtWidgets, QtGui, uic

# pylint: disable=import-error
from equations.constants import Point2D
from view.droppable_plot_widget import DroppablePlotWidget
from view.draggable_label import DraggableLabel
# pylint: enable=import-error


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window, holding sub-views.
    """

    # Type annotations for UI elements
    central_widget: QtWidgets.QWidget
    grid_layout: QtWidgets.QGridLayout
    graph_widget: DroppablePlotWidget
    point_charge_circle: DraggableLabel
    line_charge_drawing: DraggableLabel
    circle_charge_drawing: DraggableLabel
    ring_charge_drawing: DraggableLabel
    refresh_button: QtWidgets.QPushButton
    menu_bar: QtWidgets.QMenuBar
    status_bar: QtWidgets.QStatusBar

    def __init__(self) -> None:
        super().__init__()

        uic.load_ui.loadUi(os.path.join(sys.path[0], "view/ui/main_window.ui"), self)
        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)

        self.refresh_button.clicked.connect(self.graph_widget.refresh_button_pressed)

        graph_menu = self.menu_bar.addMenu("Graph")
        refresh_graph_action = graph_menu.addAction("Refresh Graph")
        refresh_graph_action.setShortcuts(["Ctrl+R", "F5"])
        refresh_graph_action.triggered.connect(self.graph_widget.refresh_button_pressed)

        increase_graph_resolution = graph_menu.addAction("Increase resolution", "Ctrl+=")
        increase_graph_resolution.triggered.connect(self.graph_widget.increase_resolution)

        decrease_graph_resolution = graph_menu.addAction("Decrease resolution", "Ctrl+-")
        decrease_graph_resolution.triggered.connect(self.graph_widget.decrease_resolution)

        reset_graph_resolution = graph_menu.addAction("Reset resolution", "Ctrl+0")
        reset_graph_resolution.triggered.connect(self.graph_widget.reset_resolution)

        center_origin = graph_menu.addAction("Center at origin", "Ctrl+O")
        center_origin.triggered.connect(self.graph_widget.center_origin)

        default_range = graph_menu.addAction("Default range", "Ctrl+D")
        default_range.triggered.connect(self.graph_widget.default_range)

        charge_menu = self.menu_bar.addMenu("Charges")
        remove_charge = charge_menu.addAction("Remove last charge", "Ctrl+Backspace")
        remove_charge.triggered.connect(self.graph_widget.remove_charge)

        undo_remove_charge = charge_menu.addAction("Undo last removal", "Ctrl+Shift+Backspace")
        undo_remove_charge.triggered.connect(self.graph_widget.undo_remove_charge)

        self.proxy = pyqtgraph.SignalProxy(self.graph_widget.scene().sigMouseMoved,
                                           rateLimit=60,
                                           slot=self._mouse_moved)

        self._paint_shapes()
        self.graph_widget.build_plots()

        self.show()

    def _paint_shapes(self) -> None:
        """
        Create a circle for the point charge.

        Will also be used to draw other shapes.
        """

        # Paint circle
        canvas = QtGui.QPixmap(110, 110)
        canvas.fill(self.palette().color(self.backgroundRole()))

        painter = QtGui.QPainter(canvas)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.red, 5))
        painter.setBrush(QtCore.Qt.GlobalColor.red)
        painter.drawEllipse(5, 5, 100, 100)
        painter.end()

        self.point_charge_circle.setPixmap(canvas)
        self.point_charge_circle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.point_charge_circle.label_type = DraggableLabel.LabelTypes.POINT_CHARGE

        # Paint straight line
        canvas = QtGui.QPixmap(110, 110)
        canvas.fill(self.palette().color(self.backgroundRole()))

        painter = QtGui.QPainter(canvas)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.red, 5))
        painter.drawLine(55, 5, 55, 100)
        painter.end()

        self.line_charge_drawing.setPixmap(canvas)
        self.line_charge_drawing.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.line_charge_drawing.label_type = DraggableLabel.LabelTypes.INFINITE_LINE_CHARGE

        # Paint circle charge
        canvas = QtGui.QPixmap(110, 110)
        canvas.fill(self.palette().color(self.backgroundRole()))

        painter = QtGui.QPainter(canvas)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.red, 5))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, alpha=50)))
        painter.drawEllipse(5, 5, 100, 100)
        painter.end()

        self.circle_charge_drawing.setPixmap(canvas)
        self.circle_charge_drawing.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.circle_charge_drawing.label_type = DraggableLabel.LabelTypes.CIRCLE_CHARGE

        # Paint ring charge
        canvas = QtGui.QPixmap(110, 110)
        canvas.fill(self.palette().color(self.backgroundRole()))

        painter = QtGui.QPainter(canvas)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.red, 20))
        painter.drawEllipse(10, 10, 90, 90)
        painter.end()

        self.ring_charge_drawing.setPixmap(canvas)
        self.ring_charge_drawing.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ring_charge_drawing.label_type = DraggableLabel.LabelTypes.RING_CHARGE

    def _mouse_moved(self, event: Tuple) -> None:
        """
        Callback executed when the mouse moves in the graph widget.

        Args:
            event (Tuple): A tuple containing the position of the mouse.
        """

        pos = event[0]
        if self.graph_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.graph_widget.get_pi_vb()[1].mapSceneToView(pos)
            x_pos = mouse_point.x()
            y_pos = mouse_point.y()
            ef_mag_x = self.graph_widget.graph_window.electric_field_x(Point2D(x_pos, y_pos))
            ef_mag_y = self.graph_widget.graph_window.electric_field_y(Point2D(x_pos, y_pos))
            ef_mag_net = np.sqrt(ef_mag_x**2 + ef_mag_y**2)

            x_fs = "e" if abs(x_pos) > 1e5 else "f"
            y_fs = "e" if abs(y_pos) > 1e5 else "f"
            text = f"X: {x_pos:+.2{x_fs}} Y: {y_pos:+.2{y_fs}} Magnitude: {ef_mag_net:.6g}"

            self.graph_widget.setToolTip(text)
            self.status_bar.showMessage(text)
