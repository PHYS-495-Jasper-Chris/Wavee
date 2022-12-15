"""
The main window.
"""
import os
import sys
from typing import Tuple

import pyqtgraph
from PyQt6 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets, uic
from sympy import latex

# pylint: disable=import-error
from equations.constants import Point2D
from equations.equation_thread import EquationThread
from equations.sympy_helper import make_source
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
        self.equations_thread.started.connect(self._clear_equations)
        self.equations_thread.finished.connect(self._update_equations)

        self.graph_widget.graph_window.charges_updated = self._charges_updated

        self.refresh_button.clicked.connect(self.graph_widget.refresh_button_pressed)

        self.proxy = pyqtgraph.SignalProxy(self.graph_widget.scene().sigMouseMoved,
                                           rateLimit=60,
                                           slot=self._mouse_moved)

        self._add_menus()
        self._paint_shapes()
        self.graph_widget.build_plots()
        self.equations_thread.start()

        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)

    def _add_menus(self) -> None:
        """
        Add menus and actions to window.
        """

        # ---- GRAPH MENU OPTIONS ----
        graph_menu = self.menu_bar.addMenu("Graph")
        refresh_graph_action = graph_menu.addAction("Refresh Graph",
                                                    self.graph_widget.refresh_button_pressed)
        refresh_graph_action.setShortcuts(["Ctrl+R", "F5"])
        graph_menu.addAction("Increase resolution", "Ctrl+=", self.graph_widget.increase_resolution)
        graph_menu.addAction("Decrease resolution", "Ctrl+-", self.graph_widget.decrease_resolution)
        graph_menu.addAction("Reset resolution", "Ctrl+0", self.graph_widget.reset_resolution)
        graph_menu.addAction("Center at origin", "Ctrl+O", self.graph_widget.center_origin)
        graph_menu.addAction("Default range", "Ctrl+D", self.graph_widget.default_range)
        graph_menu.addAction("Toggle fixed aspect ratio", "Ctrl+A",
                             self.graph_widget.toggle_even_aspect_ratio)

        # ---- CHARGES MENU OPTIONS ----
        charge_menu = self.menu_bar.addMenu("Charges")
        charge_menu.addAction("Remove last charge", "Ctrl+Backspace",
                              self.graph_widget.remove_charge)
        charge_menu.addAction("Undo last removal", "Ctrl+Shift+Backspace",
                              self.graph_widget.undo_remove_charge)
        charge_menu.addAction("Remove all charges", "Ctrl+Alt+Backspace",
                              self.graph_widget.graph_window.remove_all_charges)
        charge_menu.addAction("Re-add all charges", "Ctrl+Shift+Alt+Backspace",
                              self.graph_widget.graph_window.readd_all_charges)

        # ---- EQUATION MENU OPTIONS ----
        equation_menu = self.menu_bar.addMenu("Equations")
        equation_menu.addAction("Increase digits shown", "Ctrl+]", self._increment_equations_digits)
        equation_menu.addAction("Decrease digits shown", "Ctrl+[", self._decrement_equations_digits)

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

        mag_eqns = self.equations_thread.mag_eqns
        x_eqns = self.equations_thread.x_eqns
        y_eqns = self.equations_thread.y_eqns

        mag_html = ""
        for i, mag_eqn in enumerate(mag_eqns):
            mag_html += f"E_{i}={latex(mag_eqn)},"

        x_html = "E_x(x,y)="
        for i, x_eqn in enumerate(x_eqns):
            if len(x_eqns) > 1:
                x_html += f"\\left({latex(x_eqn)}\\right)+"
            else:
                x_html += f"{latex(x_eqn)}+"

        y_html = "E_y(x,y)="
        for i, y_eqn in enumerate(y_eqns):
            if len(y_eqns) > 1:
                y_html += f"\\left({latex(y_eqn)}\\right)+"
            else:
                y_html += f"{latex(y_eqn)}+"

        self.net_mag_equation_label.setHtml(make_source(mag_html[:-1]) if mag_eqns else "")
        self.x_equation_label.setHtml(make_source(x_html[:-1]) if x_eqns else "")
        self.y_equation_label.setHtml(make_source(y_html[:-1]) if y_eqns else "")

    def _clear_equations(self) -> None:
        """
        When the equations thread is running, clear the current equations.
        """

        loading_html = "<center>Loading...</center>"

        self.net_mag_equation_label.setHtml(loading_html)
        self.x_equation_label.setHtml(loading_html)
        self.y_equation_label.setHtml(loading_html)

    def _increment_equations_digits(self):
        """
        Increase the number of digits shown in the equations window by 1.
        """

        self.equations_thread.change_rounding(1)
        self.equations_thread.update_rounding()
        self._update_equations()

    def _decrement_equations_digits(self):
        """
        Decrease the number of digits shown in the equations window by 1.
        """

        self.equations_thread.change_rounding(-1)
        self.equations_thread.update_rounding()
        self._update_equations()
