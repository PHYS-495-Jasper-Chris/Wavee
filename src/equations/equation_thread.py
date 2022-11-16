"""
Implementation of a separate thread for equation rendering.
"""

from typing import List, Optional

from PyQt6 import QtCore
from sympy import Basic

from equations.graph_window import GraphWindow
from equations.sympy_helper import round_symbolic


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

        self.rounding = default_rounding

        self._unrounded_mag_eqns: List[Basic] = []
        self._unrounded_x_eqns: List[Basic] = []
        self._unrounded_y_eqns: List[Basic] = []

        self.mag_eqns: List[Basic] = []
        self.x_eqns: List[Basic] = []
        self.y_eqns: List[Basic] = []

    def run(self) -> None:
        """
        Update the equation labels when the charges are changed.
        """

        # Load all equations at once.
        temp_mag_eqns = self._graph_window.electric_field_mag_eqns()
        temp_x_eqns = self._graph_window.electric_field_x_eqns()
        temp_y_eqns = self._graph_window.electric_field_y_eqns()

        self._unrounded_mag_eqns = temp_mag_eqns
        self._unrounded_x_eqns = temp_x_eqns
        self._unrounded_y_eqns = temp_y_eqns

        self.update_rounding()

        self.finished.emit()

    def change_rounding(self, increment: int) -> None:
        """
        Increase (or decrease) the rounding by ``increment``, resulting in more (or fewer) digits
        after the decimal place.

        Does not automatically rebuild the equations.

        Args:
            increment (int): The change to the current value of ``rounding``.
        """

        self.rounding += increment

        # Make sure rounding never goes below zero.
        self.rounding = max(self.rounding, 0)

    def update_rounding(self) -> None:
        """
        Update the rounding on the current equations.
        """

        temp_mag_eqns = [round_symbolic(eqn, self.rounding) for eqn in self._unrounded_mag_eqns]
        temp_x_eqns = [round_symbolic(eqn, self.rounding) for eqn in self._unrounded_x_eqns]
        temp_y_eqns = [round_symbolic(eqn, self.rounding) for eqn in self._unrounded_y_eqns]

        self.mag_eqns = temp_mag_eqns
        self.x_eqns = temp_x_eqns
        self.y_eqns = temp_y_eqns
