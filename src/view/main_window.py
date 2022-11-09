"""
The main window.
"""

import os
import sys
from typing import Tuple

import pyqtgraph
from PyQt6 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets, uic

# pylint: disable=import-error
from equations.constants import Point2D
from equations.equation_thread import EquationThread
from view.draggable_label import DraggableLabel
from view.droppable_plot_widget import DroppablePlotWidget

# pylint: enable=import-error


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window, holding sub-views.
    """

    # Type annotations for UI elements
    central_widget: QtWidgets.QWidget
    grid_layout: QtWidgets.QGridLayout
    graph_widget: DroppablePlotWidget
    net_mag_equation_label: QtWebEngineWidgets.QWebEngineView
    x_equation_label: QtWebEngineWidgets.QWebEngineView
    y_equation_label: QtWebEngineWidgets.QWebEngineView
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

        self.equations_thread = EquationThread(self.graph_widget.graph_window, self)
        self.equations_thread.finished.connect(self._update_equations)

        self.graph_widget.graph_window.charges_updated = self._charges_updated

        self.refresh_button.clicked.connect(self.graph_widget.refresh_button_pressed)

        # ---- GRAPH MENU OPTIONS ----
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

        aspect_ratio_toggle = graph_menu.addAction("Toggle fixed aspect ratio", "Ctrl+A")
        aspect_ratio_toggle.triggered.connect(self.graph_widget.toggle_even_aspect_ratio)

        # ---- CHARGES MENU OPTIONS ----
        charge_menu = self.menu_bar.addMenu("Charges")
        remove_charge = charge_menu.addAction("Remove last charge", "Ctrl+Backspace")
        remove_charge.triggered.connect(self.graph_widget.remove_charge)

        undo_remove_charge = charge_menu.addAction("Undo last removal", "Ctrl+Shift+Backspace")
        undo_remove_charge.triggered.connect(self.graph_widget.undo_remove_charge)

        remove_all_charges = charge_menu.addAction("Remove all charges", "Ctrl+Alt+Backspace")
        remove_all_charges.triggered.connect(self.graph_widget.graph_window.remove_all_charges)

        readd_all_charges = charge_menu.addAction("Re-add all charges", "Ctrl+Shift+Alt+Backspace")
        readd_all_charges.triggered.connect(self.graph_widget.graph_window.readd_all_charges)

        # ---- EQUATION MENU OPTIONS ----
        equation_menu = self.menu_bar.addMenu("Equations")

        increase_digits = equation_menu.addAction("Increase digits shown", "Ctrl+]")
        increase_digits.triggered.connect(self.increment_equations_digits)

        decrease_digits = equation_menu.addAction("Decrease digits shown", "Ctrl+[")
        decrease_digits.triggered.connect(self.decrement_equations_digits)

        self.proxy = pyqtgraph.SignalProxy(self.graph_widget.scene().sigMouseMoved,
                                           rateLimit=60,
                                           slot=self._mouse_moved)

        self._paint_shapes()
        self.graph_widget.build_plots()
        self.equations_thread.start()

        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.show()

    def _paint_shapes(self) -> None:
        """
        Create an icon for each charge type in the right hand drag and drop menu.
        """
        self._paint_point_charge_icon()
        self._paint_infinite_line_charge_icon()
        self._paint_circle_charge_icon()
        self._paint_ring_charge_icon()

    def _paint_point_charge_icon(self) -> None:
        """
        Paint the drag and drop circle for point charge on the right hand column.

        This is a solid red circle.
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

    def _paint_infinite_line_charge_icon(self) -> None:
        """
        Paint the drag and drop line for line charge elements on the right hand column.

        This is a solid vertical line.
        """
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

    def _paint_circle_charge_icon(self) -> None:
        """
        Paint the drag and drop circle for circle charge elements on the right hand column.

        This is a transparent red circle with a solid red border.
        """
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

    def _paint_ring_charge_icon(self) -> None:
        """
        Paint the drag and drop ring for ring charge elements on the right hand column.

        This is a completely transparent circle with a thick red border.
        """
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

    def _mouse_moved(self, event: Tuple[QtCore.QPointF]) -> None:
        """
        Callback executed when the mouse moves in the graph widget.

        Args:
            event (Tuple[QPointF]): A tuple containing the position of the mouse.
        """

        pos = event[0]
        if self.graph_widget.sceneBoundingRect().contains(pos):
            mouse_point: QtCore.QPointF = self.graph_widget.get_pi_vb()[1].mapSceneToView(pos)
            x_pos, y_pos = mouse_point.x(), mouse_point.y()
            ef_mag_net = self.graph_widget.graph_window.net_electric_field(Point2D(x_pos, y_pos))

            x_fs = "e" if abs(x_pos) > 1e5 or (x_pos != 0.0 and abs(x_pos) < 1e-2) else "f"
            y_fs = "e" if abs(y_pos) > 1e5 or (y_pos != 0.0 and abs(y_pos) < 1e-2) else "f"
            text = f"X: {x_pos:+.2{x_fs}} Y: {y_pos:+.2{y_fs}} Magnitude: {ef_mag_net:.6g}"

            self.graph_widget.setToolTip(text)
            self.status_bar.showMessage(text)

    def _charges_updated(self) -> None:
        """
        When charges change, do several things:

        1.) Reload the graphs.
        2.) Reload the equations (this is __really__ slow).
        """

        self.graph_widget.charges_updated()
        self.equations_thread.start()

    def _update_equations(self) -> None:
        """
        Read the values from the equations thread and update the labels.
        """

        self.net_mag_equation_label.setHtml(self.equations_thread.mag_html)
        self.x_equation_label.setHtml(self.equations_thread.x_html)
        self.y_equation_label.setHtml(self.equations_thread.y_html)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:  # pylint: disable=invalid-name
        """
        When the window is resized, automatically resize the equation web views.

        TODO: figure out if this works.
        """

        super().resizeEvent(a0)

        def set_height(height: str, label: QtWebEngineWidgets.QWebEngineView) -> None:
            label.resize(label.width(), int(height) + 20)

        # TODO: figure out how to do this properly (this doesn't work)
        self.net_mag_equation_label.page().runJavaScript(
            "document.documentElement.scrollHeight;",
            lambda height: set_height(height, self.net_mag_equation_label))
        self.x_equation_label.page().runJavaScript(
            "document.documentElement.scrollHeight;",
            lambda height: set_height(height, self.x_equation_label))
        self.y_equation_label.page().runJavaScript(
            "document.documentElement.scrollHeight;",
            lambda height: set_height(height, self.y_equation_label))

    def increment_equations_digits(self):
        """
        Increase the number of digits shown in the equations window by 1
        """
        self.equations_thread.increase_digits(1)
        self.equations_thread.start()

    def decrement_equations_digits(self):
        """
        Decrease the number of digits shown in the equations window by 1
        """
        self.equations_thread.decrease_digits(1)
        self.equations_thread.start()
