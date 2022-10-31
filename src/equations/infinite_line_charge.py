"""
Calculate the electric field of an infinite line charge.
"""

import numpy as np

from PyQt6 import QtWidgets, QtCore

# pylint: disable=import-error
from equations.base_charge import BaseCharge
from equations.constants import COULOMB_CONSTANT, Point2D
from view.multi_line_input_dialog import MultiLineInputDialog
# pylint: enable=import-error


class InfiniteLineCharge(BaseCharge):
    """
    A single infinite line of charge, with a slope and offset (m & b), and a charge density.
    """

    def __init__(self, x_coef: float, y_coef: float, offset: float, charge_density: float) -> None:
        """
        Initialize the infinite line charge with its equation and charge density.

        The line equation is written in the form ``ax + by + c = 0``, where a is ``x_coef``, b is
        ``y_coef``, and c is ``offset``.

        Args:
            x_coef (float): The coefficient on x in the equation of the line (a).
            y_coef (float): The coefficient on y in the equation of the line (b).
            offset (float): The offset in the equation of the line (c).
            charge_density (float): The charge density, in C/m.

        Raises:
            RuntimeError: Cannot have both the x and y coefficient equating to zero.
        """

        if x_coef == 0 and y_coef == 0:
            raise RuntimeError(
                "Invalid infinite line charge equation: x_coef and y_coef cannot simultaneously be "
                "0")

        self.x_coef = x_coef
        self.y_coef = y_coef
        self.offset = offset
        self.charge_density = charge_density

    def radial_distance(self, point: Point2D) -> float:
        """
        The shortest distance from a point to the infinite line of charge.

        Args:
            point (Point2D): The point to measure the distance from.

        Returns:
            float: minimal radial distance from ``point`` to line charge.
        """

        return (abs(self.x_coef * point.x + self.y_coef * point.y + self.offset)
                / np.sqrt(self.x_coef**2 + self.y_coef**2))

    def closest_point(self, point: Point2D) -> Point2D:
        """
        The closest point on the line from a given point.

        Args:
            point (Point2D): The point to find the closest point to.

        Returns:
            Point2D: The closest point.
        """

        x_pos = (self.y_coef * (self.y_coef * point.x - self.x_coef * point.y)
                 - self.x_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        y_pos = (self.x_coef * (self.x_coef * point.y - self.y_coef * point.x)
                 - self.y_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        return Point2D(x_pos, y_pos)

    def electric_field_magnitude(self, point: Point2D) -> float:
        """
        The net magnitude of the electric field at the given point.

        Args:
            point (Point2D): The point to measure the field at.

        Returns:
            float: The net (signed) magnitude of the electric field at the given point, or zero if
            the magnitude is infinite.
        """

        radial_distance = self.radial_distance(point)

        # Make sure we don't divide by 0
        if radial_distance == 0.0:
            return 0.0

        # E = 2k λ/r
        magnitude = 2 * COULOMB_CONSTANT * self.charge_density / radial_distance

        return 0.0 if np.isinf(magnitude) else magnitude

    def electric_field_x(self, point: Point2D) -> float:
        """
        The x component of the electric field at a given point.

        Args:
            point (Point2D): The point to measure the field at.

        Returns:
            float: Magnitude of the electric field's x-component due to the infinite line charge at
            this point.
        """

        # The direction of the electric field is completely orthogonal to the direction of the line
        # charge itself, so for x take the cos instead of sin.

        line_angle: float = np.arctan2(self.y_coef, self.x_coef)

        magnitude = self.electric_field_magnitude(point) * np.cos(line_angle)

        # If the x-component of the point is greater than that of the closest point on the line,
        # then the magnitude should be kept the same, otherwise it should be negated.
        if self.closest_point(point).x > point.x:
            magnitude *= -1

        return magnitude

    def electric_field_y(self, point: Point2D) -> float:
        """
        The y component of the electric field at a given point.

        Args:
            point (Point2D): The point to measure the field at.

        Returns:
            float: Magnitude of the electric field's y-component due to the infinite line charge at
            this point.
        """

        # The direction of the electric field is completely orthogonal to the direction of the line
        # charge itself, so for y take the sin instead of cos.

        line_angle: float = np.arctan2(self.y_coef, self.x_coef)

        magnitude = self.electric_field_magnitude(point) * np.sin(line_angle)

        # If the y-component of the point is greater than that of the closest point on the line,
        # then the magnitude should be kept the same, otherwise it should be negated.
        if self.closest_point(point).y > point.y:
            magnitude *= -1

        return magnitude

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
        set_eqn = menu.addAction("Set Equation of Line")
        rmv_charge = menu.addAction("Remove Charge")

        while True:
            action = menu.exec(pos.toPoint())

            if action == set_charge:
                print("Need to set charge")
            elif action == set_eqn:
                new_eqn, success = MultiLineInputDialog(
                    ["X Coefficient", "Y Coefficient", "Offset"], menu,
                    "Set equation of the line in the form ax + by + c = 0").get_doubles()

                if success and False not in np.isfinite(new_eqn):
                    self.x_coef, self.y_coef, self.offset = new_eqn
            elif action == rmv_charge:
                return True
            elif action is None:
                return False
