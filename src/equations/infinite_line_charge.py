"""
Calculate the electric field of an infinite line charge.
"""

from typing import List

import numpy as np

# pylint: disable=import-error
from equations.base_charge import BaseCharge
from equations.constants import COULOMB_CONSTANT
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

    def radial_distance(self, point: List[float]) -> float:
        """
        The shortest distance from a point to the infinite line of charge.

        Args:
            point (List[float]): The point to measure the distance from.

        Returns:
            float: minimal radial distance from ``point`` to line charge.
        """

        return abs(self.x_coef * point[0] + self.y_coef * point[1]
                   + self.offset) / np.sqrt(self.x_coef**2 + self.y_coef**2)

    def closest_point(self, point: List[float]) -> List[float]:
        """
        The closest point on the line from a given point.

        Args:
            point (List[float]): The point to find the closest point to in the form ``[x, y]``.

        Returns:
            List[float]: list representation of closest point ``[x, y]``.
        """

        x_pos = (self.y_coef * (self.y_coef * point[0] - self.x_coef * point[1])
                 - self.x_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        y_pos = (self.x_coef * (self.x_coef * point[1] - self.y_coef * point[0])
                 - self.y_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        return [x_pos, y_pos]

    def electric_field_magnitude(self, point: List[float]) -> float:
        """
        The net magnitude of the electric field at the given point.

        Args:
            point (List[float]): The point to measure the field at in the form ``[x, y]``.

        Returns:
            float: The net (signed) magnitude of the electric field at the given point, or zero if
            the magnitude is infinite.
        """

        # E = 2k λ/r
        magnitude = 2 * COULOMB_CONSTANT * self.charge_density / self.radial_distance(point)

        return 0.0 if np.isinf(magnitude) else magnitude

    def electric_field_x(self, point: List[float]) -> float:
        """
        The x component of the electric field at a given point.

        Args:
            point (List[float]): The point to measure the field at.

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
        if self.closest_point(point)[0] > point[0]:
            magnitude *= -1

        return magnitude

    def electric_field_y(self, point: List[float]) -> float:
        """
        The y component of the electric field at a given point.

        Args:
            point (List[float]): The point to measure the field at.

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
        if self.closest_point(point)[1] > point[1]:
            magnitude *= -1

        return magnitude
