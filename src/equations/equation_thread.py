"""
Implementation of a separate thread for equation rendering.
"""

from typing import Optional

from PyQt6 import QtCore

from equations.graph_window import Window


class EquationThread(QtCore.QThread):
    """
    A standalone thread for equation rendering, because this is highly computationally intensive and
    does not need to be blocking.
    """

    def __init__(self, graph_window: Window, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)

        self._graph_window = graph_window

        self.mag_html: str = ""
        self.x_html: str = ""
        self.y_html: str = ""

    def run(self) -> None:
        """
        Update the equation labels.
        """

        # Load all equations at once.
        self.mag_html = self._graph_window.electric_field_mag_html()
        self.x_html = self._graph_window.electric_field_x_html()
        self.y_html = self._graph_window.electric_field_y_html()

        self.finished.emit()
