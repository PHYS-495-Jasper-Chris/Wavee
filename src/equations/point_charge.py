"""
Calculate the electric field of a point charge.
"""

import numpy as np
import sympy
from PyQt6 import QtCore, QtWidgets
from sympy.abc import x, y

# pylint: disable=import-error
from equations.base_charge import BaseCharge
from equations.constants import COULOMB_CONSTANT, COULOMB_CONSTANT_SYM, Point2D
from view.multi_line_input_dialog import MultiLineInputDialog

# pylint: enable=import-error


class PointCharge(BaseCharge):
    """
    A single point charge, with a position and a charge.
    """

    def __init__(self, position: Point2D, charge: float) -> None:
        self.position = position
        self.charge = charge

    def electric_field_magnitude(self, point: Point2D) -> float:
        """
        Return the electric field magnitude generated by this point charge at a given point.

        Args:
            point (Point2D): x, y location of test point.

        Returns:
            float: magnitude of electric field.
        """

        radius = self._radius(point)

        # Make sure we don't divide by 0
        if radius == 0.0:
            return 0.0

        return COULOMB_CONSTANT * self.charge / radius**2

    def electric_field_x(self, point: Point2D) -> float:
        """
        Calculate the x component of the magnetic field generated by the point charge at a given
        point.

        Args:
            point (Point2D): test point to check.

        Returns:
            float: x component of electric field.
        """

        return self.electric_field_magnitude(point) * np.cos(self._theta(point))

    def electric_field_y(self, point: Point2D) -> float:
        """
        Calculate the y component of the magnetic field generated by the point charge at a given
        point.

        Args:
            point (Point2D): test point to check.

        Returns:
            float: y component of electric field.
        """

        return self.electric_field_magnitude(point) * np.sin(self._theta(point))

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
        set_center = menu.addAction("Set Position")
        set_charge = menu.addAction("Set Charge")
        rmv_charge = menu.addAction("Remove Charge")

        while True:
            action = menu.exec(pos.toPoint())

            if action == set_charge:
                val, success = QtWidgets.QInputDialog().getDouble(menu, "Set Charge",
                                                                  "Set Charge (C)")
                if success:
                    self.charge = val
                    self.charge_updated()
            elif action == set_center:
                new_center, success = MultiLineInputDialog(["X Position", "Y Position"],
                                                           menu).get_doubles()

                if success and False not in np.isfinite(new_center):
                    self.position = Point2D(*new_center)
                    self.charge_updated()
            elif action == rmv_charge:
                return True
            elif action is None:
                return False

    def electric_field_mag_eqn(self) -> sympy.Basic:
        """
        Returns the position-independent electric field equation of magnitude for this point charge.

        Returns:
            Basic: sympy representation of the signed magnitude of the electric field.
        """

        # The equation for a point charge is k q / r^2
        # r = sqrt(x_dist^2 + y_dist^2)
        # x_dist = abs(x - self.center.x)
        x_dist, y_dist = abs(x - self.position.x), abs(y - self.position.y)

        return COULOMB_CONSTANT_SYM * self.charge / (x_dist + y_dist)

    def electric_field_x_eqn(self) -> sympy.Basic:
        """
        Returns the position-independent electric field x-component equation for this point charge.

        Returns:
            Basic: sympy representation of the x-component of the electric field.
        """

        mag = self.electric_field_mag_eqn()
        theta = self._theta_eqn()
        return mag * sympy.cos(theta)  # type: ignore

    def electric_field_y_eqn(self) -> sympy.Basic:
        """
        Returns the position-independent electric field y-component equation for this point charge.

        Returns:
            Basic: sympy representation of the y-component of the electric field.
        """

        mag = self.electric_field_mag_eqn()
        theta = self._theta_eqn()
        return mag * sympy.sin(theta)  # type: ignore

    def _radius(self, point: Point2D) -> float:
        """
        Returns the radial distance from the given point.

        Args:
            point (Point2D): point to get radial distance from.

        Returns:
            float: radial distance from given point.
        """

        if len(point) != len(self.position):
            raise RuntimeError(
                "Point given does not match dimension of point charge position. point dim: "
                f"{len(point)} | charge dim: {len(self.position)}")

        sides_sum = 0.0
        for i, point_n in enumerate(point):
            sides_sum += abs(self.position[i] - point_n)**2

        return np.sqrt(sides_sum)

    def _theta(self, point: Point2D) -> float:
        """
        Calculate the angle from point charge location to test point.

        Args:
            point (Point2D): test point.

        Returns:
            float: angle in radians.
        """

        return np.arctan2(point.y - self.position.y, point.x - self.position.x)

    def _theta_eqn(self) -> sympy.Basic:
        """
        Returns the angle between any x, y point and the point charge location.
        """

        return sympy.atan2(y - self.position.y, x - self.position.x)  # type: ignore
