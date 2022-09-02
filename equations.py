import sympy as sp

import numpy as np

COULOMB_CONSTANT = (sp.symbols("k"), 1234)
MU_NAUGHT, EPSILON_NAUGHT, r = sp.symbols("\\mu_{0}, \\epsilon_{0}, r")


def coulombs_law_eqn(charge: float):
    """
    Determines the electric field at a point ``radius`` away from a single point
    charge ``charge``.

    @param charge The charge of the point charge

    E = k|q|/r^2
    """

    equation = "1/(4 * sp.pi * EPSILON_NAUGHT) * (abs(charge)) / r ** 2"

    return eval(equation)


sp.init_printing()

res = coulombs_law_eqn(7)
print(res)

for r_val in range(1, 10, 1):
    f = res.subs({r: r_val, EPSILON_NAUGHT: 1, sp.pi: np.pi})
    print(f)

sp.preview(sp.latex(res), output="png")
