import sympy as sp

from sympy.printing.preview import system_default_viewer

import numpy as np

COULOMB_CONSTANT, MU_NAUGHT, EPSILON_NAUGHT, r = sp.symbols("k, \\mu_{0}, \\epsilon_{0}, r")


def coulombs_law_eqn(charge: float):
    """
    Determines the electric field at a point ``radius`` away from a single point
    charge ``charge``.

    @param charge The charge of the point charge
    """
    return eval("1/(4 * sp.pi * EPSILON_NAUGHT) * (abs(charge)) / r**2")


sp.init_printing()
sp.preview(sp.latex(coulombs_law_eqn(7)), output="png", viewer=system_default_viewer)
