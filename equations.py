import sympy as sp
import matplotlib.pyplot as plt
import numpy as np

COULOMB_CONSTANT, MU_NAUGHT, EPSILON_NAUGHT, R = sp.symbols("k, \\mu_{0}, \\epsilon_{0}, r")


def coulombs_law_eqn(charge: float):
    """
    Determines the electric field at a point ``radius`` away from a single point
    charge ``charge``.

    E = k|q|/r^2

    @param charge The charge of the point charge.
    """

    equation = "1/(4 * sp.pi * EPSILON_NAUGHT) * (abs(charge)) / R ** 2"

    return eval(equation)


def main():
    sp.init_printing()

    res = coulombs_law_eqn(100)
    print(res)

    x = np.linspace(1, 10, 100)
    y = [res.subs({R: r_val, EPSILON_NAUGHT: 1, sp.pi: np.pi}) for r_val in x]

    plt.plot(x, y)
    plt.show()

    latex_str = "$" + sp.latex(res) + "$"
    sp.preview(latex_str, output="png", dvioptions=["-D", "1200"])


if __name__ == "__main__":
    main()
