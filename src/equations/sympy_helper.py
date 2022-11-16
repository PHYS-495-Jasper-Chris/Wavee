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
