"""
Calculate the electric field of an infinite line charge.
"""

from typing import Tuple

import numpy as np
import sympy
from PyQt6 import QtCore, QtWidgets
from sympy.abc import x, y

# pylint: disable=import-error
from equations.base_charge import BaseCharge
from equations.constants import COULOMB_CONSTANT, COULOMB_CONSTANT_SYM, Point2D
from equations.sympy_helper import clean_inequality
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
            float: The net (signed) magnitude of the electric field at the given point.
        """

        radial_distance = self.radial_distance(point)

        # Make sure we don't divide by 0
        if radial_distance == 0.0:
            return 0.0

        # E = 2k λ/r
        return 2 * COULOMB_CONSTANT * self.charge_density / radial_distance

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
        # charge itself, so for x take the sin instead of cos.

        magnitude = self.electric_field_magnitude(point) * abs(np.sin(self._line_angle()))

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
        # charge itself, so for y take the cos instead of sin.

        magnitude = self.electric_field_magnitude(point) * abs(np.cos(self._line_angle()))

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
                val, success = QtWidgets.QInputDialog().getDouble(menu, "Set Charge Density",
                                                                  "Set Charge Density (C/m)")
                if success:
                    self.charge_density = val
                    self.charge_updated()
            elif action == set_eqn:
                new_eqn, success = MultiLineInputDialog(
                    ["X Coefficient", "Y Coefficient", "Offset"], menu,
                    "Set equation of the line in the form ax + by + c = 0").get_doubles()

                if success and False not in np.isfinite(new_eqn) and not (new_eqn[0] == 0.0
                                                                          and new_eqn[1] == 0.0):
                    self.x_coef, self.y_coef, self.offset = new_eqn
                    self.charge_updated()
            elif action == rmv_charge:
                return True
            elif action is None:
                return False

    def electric_field_mag_string(self) -> sympy.Basic:
        """
        Returns the position-independent electric field equation for this infinite line charge.
        """

        # E = 2k λ/r
        # radial distance
        r_sym = (abs(self.x_coef * x + self.y_coef * y + self.offset)
                 / sympy.sqrt(self.x_coef**2 + self.y_coef**2))

        return 2 * COULOMB_CONSTANT_SYM * self.charge_density / r_sym

    def _closest_point_string(self) -> Tuple[sympy.Basic, sympy.Basic]:
        """
        Return the formula for the closest point to a general x, y position.
        """

        x_pos = (self.y_coef * (self.y_coef * x - self.x_coef * y)
                 - self.x_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        y_pos = (self.x_coef * (self.x_coef * y - self.y_coef * x)
                 - self.y_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        return x_pos, y_pos

    def electric_field_x_string(self) -> sympy.Basic:
        """
        Returns the position-independent electric field x-component equation for this infinite line
        charge.
        """

        magnitude = self.electric_field_mag_string() * abs(np.sin(self._line_angle()))

        if magnitude == 0.0:
            return sympy.S.Zero

        closest_x_sym = self._closest_point_string()[0]
        neg_equality = clean_inequality(x <= closest_x_sym, x)
        pos_equality = clean_inequality(x >= closest_x_sym, x)

        return sympy.Piecewise((-magnitude, neg_equality), (magnitude, pos_equality))

    def electric_field_y_string(self) -> sympy.Basic:
        """
        Returns the position-independent electric field y-component equation for this infinite line
        charge.
        """

        magnitude = self.electric_field_mag_string() * abs(np.cos(self._line_angle()))

        if magnitude == 0.0:
            return sympy.S.Zero

        closest_y_sym = self._closest_point_string()[1]
        neg_equalities = clean_inequality(y <= closest_y_sym, y)
        pos_equalities = clean_inequality(y >= closest_y_sym, y)

        return sympy.Piecewise((-magnitude, neg_equalities), (magnitude, pos_equalities))

    def _line_angle(self) -> float:
        """
        Get the angle of the line as though it was through the origin, in radians.
        """

        if self.y_coef == 0.0:
            # Only have x component, so let the line point straight up (independent of x's sign).
            return np.pi / 2

        if self.x_coef == 0.0:
            # Only have y component, so let the line point straight in the +x direction (independent
            # of y's sign).
            return 0

        # The slope of the line, in ay + bx + c = 0 turns in to y = -b/a x - c/a
        return np.arctan(-self.y_coef / self.x_coef)
