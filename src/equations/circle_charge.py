"""
Calculate the electric field of solid circle of charge.
"""

import numpy as np
from PyQt6 import QtCore, QtWidgets

# pylint: disable=import-error
from equations.constants import Point2D
from equations.ring_charge import RingCharge
from view.multi_line_input_dialog import MultiLineInputDialog

# pylint: enable=import-error


class CircleCharge(RingCharge):
    """
    A single circle of charge, with a position, radius, and a charge density.
    """

    def __init__(self, center: Point2D, radius: float, charge_density: float) -> None:
        """
        Initialize the circle of charge with a center, a radius, and a charge density.

        Args:
            center (Point2D): The center of the circle of charge.
            radius (float): The radius of the circle of charge. Outside this, there is no charge.
            charge_density (float): The charge density, in C/m^2, inside the ``radius``.
        """

        super().__init__(center, 0.0, radius, charge_density)

    def open_menu(self, pos: QtCore.QPointF) -> bool:
        """
        Open a context menu for this charge.

        Configures options associated with the charge.

        Args:
            pos (QPointF): The location to open the menu at.

        Returns:
            bool: True if this charge should be deleted, False otherwise.
        """

        menu = QtWidgets.QMenu()
        set_charge = menu.addAction("Set Charge Density")
        set_radius = menu.addAction("Set Radius")
        set_center = menu.addAction("Set Center")
        rmv_charge = menu.addAction("Remove Charge")

        while True:
            action = menu.exec(pos.toPoint())

            if action == set_charge:
                val, success = QtWidgets.QInputDialog().getDouble(menu, "Set Charge Density",
                                                                  "Set Charge Density (C/m^2)")
                if success:
                    self.charge_density = val
                    self.charge_updated()
            elif action == set_radius:
                val, success = QtWidgets.QInputDialog().getDouble(menu, "Set Radius",
                                                                  "Set Radius (m)")
                if success:
                    self.outer_radius = val
                    self.charge_updated()
            elif action == set_center:
                new_center, success = MultiLineInputDialog(["X Position", "Y Position"],
                                                           menu).get_doubles()

                if success and False not in np.isfinite(new_center):
                    self.center = Point2D(*new_center)
                    self.charge_updated()
            elif action == rmv_charge:
                return True
            elif action is None:
                return False
