"""
A graph window, holding the electric field of arbitrary charge distributions.
"""

from typing import List, Optional

import numpy as np

# pylint: disable=import-error
from equations.base_charge import BaseCharge
from equations.constants import Point2D
# pylint: enable=import-error


class Window:
    """
    A collection of charges, to be graphed
    """

    def __init__(self, charges: Optional[List[BaseCharge]] = None) -> None:
        """
        Initialize a collection of charges of any kind.

        Args:
            charges (Optional[List[PointCharge]]): The list of charges. Defaults to an empty list.
        """

        self.charges = charges or []

        self._removed_charges = []

    def add_charge(self, point_charge: BaseCharge) -> None:
        """
        Add point charge to the test window.

        Args:
            point_charge (PointCharge): Point charge to be added.
        """

        self.charges.append(point_charge)

    def remove_last_charge(self) -> None:
        """
        Remove the last charge that was added (ie, the charge at the end of the list of charges).
        """

        if len(self.charges) > 0:
            self._removed_charges.append(self.charges.pop())

    def undo_charge_removal(self) -> None:
        """
        Undo the latest removal if any exists.
        """

        if len(self._removed_charges) > 0:
            self.charges.append(self._removed_charges.pop())

    def net_electric_field(self, position: Point2D) -> float:
        """
        Calculate the net electric field magnitude at a point

        Args:
            position (Point2D): The position to measure the electric field at

        Returns:
            float: magnitude of electric field
        """

        e_x = 0.0
        e_y = 0.0

        for charge in self.charges:
            e_x += charge.electric_field_x(position)
            e_y += charge.electric_field_y(position)

        return np.sqrt(pow(e_x, 2) + pow(e_y, 2))

    def electric_field_x(self, position: Point2D) -> float:
        """
        Calculate the x component of the electric field at a point.

        Args:
            position (Point2D): The position to measure the electric field at.

        Returns:
            float: x component of electric field.
        """

        e_x = 0.0

        # Sum up electric field x component for each charge
        for charge in self.charges:
            e_x += charge.electric_field_x(position)

        return e_x

    def electric_field_y(self, position: Point2D) -> float:
        """
        Calculate the y component of the electric field at a point.

        Args:
            position (Point2D): The position to measure the electric field at.

        Returns:
            float: y component of electric field.
        """

        e_y = 0.0

        # Sum up electric field y component for each point charge
        for charge in self.charges:
            e_y += charge.electric_field_y(position)

        return e_y
