"""
Constants needed for calculating the electric field.
"""

from typing import NamedTuple

import numpy as np

EPSILON_NOUGHT = 1 / (4 * np.pi * 10**-7 * 299792458**2)
"""
Vacuum permittivity (ε_0), in C^2 / N / m^2
"""

COULOMB_CONSTANT = 1 / (4 * np.pi * EPSILON_NOUGHT)
"""
Coulomb's constant (k), in N m^2 / C^2.
"""

Point2D = NamedTuple("Point2D", [("x", float), ("y", float)])
"""
A 2-dimensional point, with x and y float positions.
"""
