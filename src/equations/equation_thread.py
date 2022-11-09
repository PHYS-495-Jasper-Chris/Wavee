"""
Implementation of a separate thread for equation rendering.
"""

from typing import Optional

from PyQt6 import QtCore

from equations.graph_window import GraphWindow


class EquationThread(QtCore.QThread):
    """
    A standalone thread for equation rendering, because this is highly computationally intensive and
    does not need to be blocking.
    """

    def __init__(self,
                 graph_window: GraphWindow,
                 parent: Optional[QtCore.QObject] = None,
                 default_rounding: int = 2) -> None:
        super().__init__(parent)

        self._graph_window = graph_window

        self.mag_html: str = ""
        self.x_html: str = ""
        self.y_html: str = ""
        self.default_rounding = default_rounding

    def increase_digits(self, amount: int) -> None:
        """
        Increase the max decimal places drawn by the amount given

        Args:
            amount (int): number of decimal places to add
        """

        self.default_rounding = max(self.default_rounding + amount, 0)

    def decrease_digits(self, amount: int) -> None:
        """
        Decrease the max decimal places drawn by the amount given. Will not reduce below zero.

        Args:
            amount (int): number of decimal places to subtract
        """

        self.default_rounding = max(self.default_rounding - amount, 0)

    def run(self) -> None:
        """
        Update the equation labels.
        """

        def_round = self.default_rounding

        # Load all equations at once.
        self.mag_html = self._graph_window.electric_field_mag_html(rounding=def_round)
        self.x_html = self._graph_window.electric_field_x_html(rounding=def_round)
        self.y_html = self._graph_window.electric_field_y_html(rounding=def_round)

        self.finished.emit()
