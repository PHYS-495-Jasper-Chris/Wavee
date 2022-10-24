"""
Equations used to calculate the electric field.
"""

from typing import List, Optional

import numpy as np

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import mayavi.mlab as mplt

EPSILON_NOUGHT = 1/(4 * np.pi * 10**-7 * 299792458**2)
COULOMB_CONSTANT = 1/(4 * np.pi * EPSILON_NOUGHT)
"""
Coulomb's constant, in N m^2 / C^2
"""

class InfiniteLineCharge:
    """
    A single infinite line of charge, with a slope and offset (m & b), and a charge density.
    """

    def __init__(self, x_coef: float, y_coef: float, offset: float, charge_density: float) -> None:
        """
        Initialize the infinite line charge with its equation and charge density

        The line equation is written in the form ``ax + by + c = 0``, where a is ``x_coef``, b is
        ``y_coef``, and c is ``offset``.

        Args:
            x_coef (float): The coefficient on x in the equation of the line (a)
            y_coef (float): The coefficient on y in the equation of the line (b)
            offset (float): The offset in the equation of the line (c)
            charge_density (float): The charge density, in C/m

        Raises:
            RuntimeError: Cannot have both the x and y coefficient equating to zero
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
        The shortest distance from a point to the infinite line of charge

        Args:
            point (List[float]): The point to measure the distance from

        Returns:
            float: minimal radial distance from point to line charge
        """

        return abs(self.x_coef * point[0] + self.y_coef * point[1]
                   + self.offset) / np.sqrt(self.x_coef**2 + self.y_coef**2)


    def closest_point(self, point: List[float]) -> List[float]:
        """
        The closest point on the line from a given point

        Args:
            point (List[float]): The point to find the closest point to in the form `[x, y]`

        Returns:
            List[float]: list representation of closest point `[x, y]`
        """

        x_pos = (self.y_coef * (self.y_coef * point[0] - self.x_coef * point[1])
                 - self.x_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        y_pos = (self.x_coef * (self.x_coef * point[1] - self.y_coef * point[0])
                 - self.y_coef * self.offset) / (self.x_coef**2 + self.y_coef**2)

        return [x_pos, y_pos]


    def electric_field_magnitude(self, point: List[float]) -> float:
        """
        The net magnitude of the electric field at point

        Args:
            point (List[float]): The point to measure the field at in the form `[x, y]`

        Returns:
            float: Magnitude of the electric field at the given point, value is zero if the magnitude is infinite
        """

        # E = 2k λ/r
        magnitude = 2 * COULOMB_CONSTANT * self.charge_density / self.radial_distance(point)

        return 0 if np.isinf(magnitude) else magnitude

    def electric_field_x(self, point: List[float]) -> float:
        """
        The x component of the electric field at a given point

        Args:
            point (List[float]): The point to measure the field at

        Returns:
            float: Magnitude of the electric field's x-component
        """

        # The direction of the electric field is completely orthogonal to the direction of the line
        # charge itself, so for x take the cos instead of sin.

        line_angle: float = np.arctan2(self.y_coef, self.x_coef)

        magnitude = self.electric_field_magnitude(point) * np.cos(line_angle)

        # If the x-component of the point is greater than that of the closest point on the line,
        # then the magnitude should be positive, otherwise it should be negative.
        if self.closest_point(point)[0] > point[0]:
            magnitude *= -1

        return magnitude

    def electric_field_y(self, point: List[float]) -> float:
        """
        The y component of the electric field at a given point

        Args:
            point (List[float]): The point to measure the field at

        Returns:
            float: Magnitude of the electric field's y-component
        """

        # The direction of the electric field is completely orthogonal to the direction of the line
        # charge itself, so for y take the sin instead of cos.

        line_angle: float = np.arctan2(self.y_coef, self.x_coef)

        magnitude = self.electric_field_magnitude(point) * np.sin(line_angle)

        # If the y-component of the point is greater than that of the closest point on the line,
        # then the magnitude should be positive, otherwise it should be negative.
        if self.closest_point(point)[1] > point[1]:
            magnitude *= -1

        return magnitude


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

        return np.sqrt(sides_sum)

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

    def __init__(self,
                 charges: Optional[List[PointCharge]] = None,
                 infinite_line_charges: Optional[List[InfiniteLineCharge]] = None) -> None:
        self.charges = charges if charges else []
        self.infinite_line_charges = infinite_line_charges or []

    def add_point_charge(self, point_charge: PointCharge) -> None:
        """
        Add point charge to the test window

        Args:
            point_charge (PointCharge): Point charge object
        """
        self.charges.append(point_charge)

    def add_line_charge(self, line_charge: InfiniteLineCharge) -> None:
        """
        Add an infinite line charge to the test window

        Args:
            line_charge (InfiniteLineCharge): Infinite line charge object
        """
        self.infinite_line_charges.append(line_charge)

    def electric_field_x(self, position: List[float]) -> float:
        """
        Calculate the x component of the electric field at a point

        Args:
            position (List[float]): The position to measure the electric field at

        Returns:
            float: x component of electric field
        """
        e_x = 0

        # Sum up electric field x component for each point charge
        for point_charge in self.charges:
            e_x += point_charge.electric_field_x(position)

        # Sum up electric field x component for each line charge
        for line_charge in self.infinite_line_charges:
            e_x += line_charge.electric_field_x(position)

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

        # Sum up electric field y component for each point charge
        for point_charge in self.charges:
            e_y += point_charge.electric_field_y(position)

        # Sum up electric field y component for each line charge
        for line_charge in self.infinite_line_charges:
            e_y += line_charge.electric_field_y(position)

        return e_y


def main():
    """
    Generate graphs for a set of point charges
    """

    a = PointCharge([10, 7], 10)
    b = PointCharge([-3, 5], 8)

    window = Window([a, b, PointCharge([0, 1], -5)],
                    [InfiniteLineCharge(0, 2, 0, 1),
                     InfiniteLineCharge(1, 0, 0, 1)])

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

            except ZeroDivisionError:
                mag_x[i][j] = 0
                mag_y[i][j] = 0

    p_z = np.zeros_like(p_x)
    fig = mplt.figure(fgcolor=(0, 0, 0), bgcolor=(1, 1, 1), size=(500, 500))
    fig.scene.z_plus_view()
    fig.scene.parallel_projection = True

    mplt.quiver3d(p_x, p_y, p_z, mag_x, mag_y, p_z)
    mplt.axes(y_axis_visibility=False)

    # Add original point charges
    pc_x, pc_y, pc_z, pc_s = [], [], [], []
    for point_charge in window.charges:
        pc_x.append(point_charge.position[0])
        pc_y.append(point_charge.position[1])
        pc_z.append(0.0)
        pc_s.append(abs(point_charge.charge))
    pc_s = [s / max(pc_s) for s in pc_s]
    nodes = mplt.quiver3d(pc_x,
                          pc_y,
                          pc_z,
                          pc_s,
                          pc_s,
                          pc_s,
                          mode="sphere",
                          scalars=[x / len(pc_s) for x in range(len(pc_s))],
                          scale_factor=0.5)
    nodes.glyph.glyph_source.glyph_source.center = [0, 0, 0]

    # Plot point charges themselves
    for point_charge in window.charges:
        plt.plot(*point_charge.position,
                 marker="o",
                 markersize=abs(point_charge.charge),
                 color="r" if point_charge.charge > 0.0 else "b")

    # Plot line charges
    x_range = np.linspace(top_left[0], bottom_right[0])
    for line_charge in window.infinite_line_charges:
        if line_charge.y_coef == 0:
            # ax + c = 0 -> x = -c/a
            plt.axvline(x=-line_charge.offset / line_charge.x_coef)
        elif line_charge.x_coef == 0:
            # by + c = 0 -> y = -c/b
            plt.axhline(y=-line_charge.offset / line_charge.y_coef)
        else:
            # ax + by + c = 0 -> by = -ax - c -> y = -a/b x - c/b
            plt.plot(
                x_range, -line_charge.x_coef / line_charge.y_coef * x_range
                - line_charge.offset / line_charge.y_coef)

    plt.quiver(p_x, p_y, mag_x, mag_y, color='b', units='xy', scale=10000000000)
    plt.title('Electric field')

    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
