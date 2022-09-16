from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np

COULOMB_CONSTANT = 8.99 * 10**9
"""
Coulomb's constant, in N m^2 / C^2
"""


class PointCharge:
    """
    A single point charge, with a position and a charge
    """

    def __init__(self, position: List[float], charge: float) -> None:
        self.position = position
        self.charge = charge

    def radius(self, point: List[float]) -> float:
        """
        Returns the radial distance from the given point

        Args:
            point (List[float]): point to get radial distance from

        Returns:
            float: radial distance from given point
        """
        if len(point) != len(self.position):
            raise RuntimeError(
                "Point given does not match dimension of point charge position. point dim: "
                f"{len(point)} | charge dim: {len(self.position)}")

        sides_sum = 0
        for i, point_n in enumerate(point):
            sides_sum += abs(self.position[i] - point_n)**2

        return sides_sum**(1 / 2)

    def electric_field_magnitude(self, point: List[float]) -> float:
        """
        Return the electric field magnitude generated by this point charge at a given point

        Args:
            point (List[float]): x,y location of test point

        Returns:
            float: magnitude of electric field
        """
        return COULOMB_CONSTANT * self.charge / self.radius(point)**2

    def theta(self, point: List[float]) -> float:
        """
        Calculate the angle from point charge location to test point

        Args:
            point (List[float]): test point

        Returns:
            float: angle
        """
        return np.arccos(abs((point[0] - self.position[0])) / self.radius(point))

    def electric_field_x(self, point: List[float]) -> float:
        """
        Calculate the x component of the magnetic field generated by the point charge at a given
        point

        Args:
            point (List[float]): test point to check

        Returns:
            float: x component of electric field
        """
        magnitude = self.electric_field_magnitude(point) * np.cos(self.theta(point))
        magnitude = magnitude * -1 if point[0] < self.position[0] else magnitude
        return magnitude

    def electric_field_y(self, point: List[float]) -> float:
        """
        Calculate the y component of the magnetic field generated by the point charge at a given
        point

        Args:
            point (List[float]): test point to check

        Returns:
            float: y component of electric field
        """
        magnitude = self.electric_field_magnitude(point) * np.sin(self.theta(point))
        magnitude = magnitude * -1 if point[1] < self.position[1] else magnitude
        return magnitude


class Window:
    """
    A collection of charges, to be graphed
    """

    def __init__(self, charges: Optional[List[PointCharge]] = None) -> None:
        self.charges = charges if charges else []

    def add_point_charge(self, point_charge: PointCharge) -> None:
        """
        Add point charge to the test window

        Args:
            point_charge (PointCharge): Point charge object
        """
        self.charges.append(point_charge)

    def net_electric_field(self, position: List[float]) -> float:
        """
        Calculate the net electric field magnitude at a point

        Args:
            position (List[float]): The position to measure the electric field at

        Returns:
            float: magnitude of electric field
        """
        dims = len(self.charges[0].position) if len(self.charges) > 0 else 0

        if dims <= 1:
            return self.electric_field_x(position)

        e_x = 0.0
        e_y = 0.0
        for point_charge in self.charges:
            e_x += point_charge.electric_field_x(position)
            e_y += point_charge.electric_field_y(position)

        return np.sqrt(pow(e_x, 2) + pow(e_y, 2))

    def electric_field_x(self, position: List[float]) -> float:
        """
        Calculate the x component of the electric field at a point

        Args:
            position (List[float]): The position to measure the electric field at

        Returns:
            float: x component of electric field
        """
        e_x = 0
        for point_charge in self.charges:
            e_x += point_charge.electric_field_x(position)
        return e_x

    def electric_field_y(self, position: List[float]) -> float:
        """
        Calculate the y component of the electric field at a point

        Args:
            position (List[float]): The position to measure the electric field at

        Returns:
            float: y component of electric field
        """
        e_y = 0
        for point_charge in self.charges:
            e_y += point_charge.electric_field_y(position)
        return e_y


def main():
    """
    Generate graphs for a set of point charges
    """

    a = PointCharge([10, 7], 10)
    b = PointCharge([-3, 5], 8)

    window = Window([a, b, PointCharge([0, 1], -5)])

    top_left = [-10, 10]
    bottom_right = [10, -10]
    x_len = abs(top_left[0]) + abs(bottom_right[0])
    y_len = abs(top_left[1]) + abs(bottom_right[1])

    p_x = [[0.0] * x_len for _ in range(y_len + 1)]
    p_y = [[0.0] * x_len for _ in range(y_len + 1)]

    mag_x = [[0.0] * x_len for _ in range(y_len + 1)]
    mag_y = [[0.0] * x_len for _ in range(y_len + 1)]

    for i in range(top_left[0], bottom_right[0] + 1):
        for j in range(bottom_right[1], top_left[1] + 1):
            p_x[i][j] = i
            p_y[i][j] = j
            try:
                mag_x[i][j] = window.electric_field_x([i, j])
                mag_y[i][j] = window.electric_field_y([i, j])

                mag_x[i][j] = 0 if abs(mag_x[i][j]) > 10000000000 else mag_x[i][j]
                mag_y[i][j] = 0 if abs(mag_y[i][j]) > 10000000000 else mag_y[i][j]
            except ZeroDivisionError:
                mag_x[i][j] = 0
                mag_y[i][j] = 0

    # Plot point charges themselves
    for point_charge in window.charges:
        plt.plot(*point_charge.position,
                 marker="o",
                 markersize=abs(point_charge.charge),
                 color="r" if point_charge.charge > 0.0 else "b")

    plt.quiver(p_x, p_y, mag_x, mag_y, color='b', units='xy', scale=10000000000)
    plt.title('Electric field')

    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
