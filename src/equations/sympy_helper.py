"""
A helper module providing convenience functions for sympy.
"""

from typing import Iterable, List, Union

import sympy
import sympy.core.numbers as nums


def _remove_infinities(inequality: sympy.Basic) -> List[sympy.Rel]:
    """
    Remove infinities from inequality, returning a list of simplified inequalities.

    ``inequality`` is either a list of inequalities or a single inequality.
    """

    if len(inequality.args) <= 0:
        return []

    ineqs = []

    if isinstance(inequality.args[0], sympy.Rel):
        for ineq in inequality.args:
            if not ineq.has(nums.Infinity) and not ineq.has(nums.NegativeInfinity):
                ineqs.append(ineq)
    else:
        ineqs = ([inequality] if not inequality.has(nums.Infinity)
                 and not inequality.has(nums.NegativeInfinity) else [])

    return ineqs  # type: ignore


def clean_inequality(inequality: Union[sympy.Rel, Iterable[sympy.Rel]],
                     symbol: sympy.Symbol) -> sympy.And:
    """
    Builds an easy-to-understand inequality, solving for ``symbol`` and removing infinities.
    """

    ineqs = _remove_infinities(sympy.reduce_inequalities(inequality, [symbol]))

    return sympy.And(*ineqs)


def round_symbolic(expression: sympy.Basic, digits: int) -> sympy.Basic:
    """
    Rounds floats within sympy expression to given digits.
    """

    if digits < 0:
        return expression

    return expression.xreplace(
        {n.evalf(): round(n, digits) for n in expression.atoms(sympy.Number)})


def make_source(full_eqn: str) -> str:
    """
    Makes a MathJax string representation of a LaTeX equation string.

    Args:
        full_eqn (str): The full LaTeX equation to render.

    Returns:
        str: The MathJax HTML to render, containing the relevant equation.
    """

    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>MathJax example</title>
  <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
  <script id="MathJax-script" async
          src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
  </script>
</head>
<body>
    <p>$${full_eqn}$$</p>
</body>
</html>
"""
