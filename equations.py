import sympy as sp
import matplotlib.pyplot as plt
import numpy as np

COULOMB_CONSTANT, MU_NAUGHT, EPSILON_NAUGHT, R = sp.symbols("k, \\mu_{0}, \\epsilon_{0}, r")


def coulombs_law_eqn(charge: float):
    """
    Determines the electric field at a point ``radius`` away from a single point
    charge ``charge``.

    @param charge The charge of the point charge

    E = k|q|/r^2
    """

    equation = "1/(4 * sp.pi * EPSILON_NAUGHT) * (abs(charge)) / R ** 2"

    return eval(equation)


sp.init_printing()

res = coulombs_law_eqn(7)
print(res)

x = np.linspace(1, 10, 100)
y = [res.subs({R: r_val, EPSILON_NAUGHT: 1, sp.pi: np.pi}) for r_val in x]

plt.plot(x, y)
plt.show()

sp.preview(sp.latex(res), output="png")
