"""
Calculate the electric field of a point charge.
"""

import numpy as np

# pylint: disable=import-error
from equations.base_charge import BaseCharge
from equations.constants import COULOMB_CONSTANT, Point2D
# pylint: enable=import-error


class PointCharge(BaseCharge):
    """
    A single point charge, with a position and a charge.
    """

    def __init__(self, position: Point2D, charge: float) -> None:
        self.position = position
        self.charge = charge

    def radius(self, point: Point2D) -> float:
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

    def electric_field_magnitude(self, point: Point2D) -> float:
        """
        Return the electric field magnitude generated by this point charge at a given point.

        Args:
            point (Point2D): x, y location of test point.

        Returns:
            float: magnitude of electric field.
        """

        return COULOMB_CONSTANT * self.charge / self.radius(point)**2

    def theta(self, point: Point2D) -> float:
        """
        Calculate the angle from point charge location to test point.

        Args:
            point (Point2D): test point.

        Returns:
            float: angle.
        """

        return np.arccos(abs((point.x - self.position.x)) / self.radius(point))

    def electric_field_x(self, point: Point2D) -> float:
        """
        Calculate the x component of the magnetic field generated by the point charge at a given
        point.

        Args:
            point (Point2D): test point to check.

        Returns:
            float: x component of electric field.
        """

        magnitude = self.electric_field_magnitude(point) * np.cos(self.theta(point))
        magnitude = magnitude * -1 if point.x < self.position.x else magnitude
        return magnitude

    def electric_field_y(self, point: Point2D) -> float:
        """
        Calculate the y component of the magnetic field generated by the point charge at a given
        point.

        Args:
            point (Point2D): test point to check.

        Returns:
            float: y component of electric field.
        """

        magnitude = self.electric_field_magnitude(point) * np.sin(self.theta(point))
        magnitude = magnitude * -1 if point.y < self.position.y else magnitude
        return magnitude
