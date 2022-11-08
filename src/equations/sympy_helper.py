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

    return ineqs


def clean_inequality(inequality: Union[sympy.Rel, Iterable[sympy.Rel]],
                     symbol: sympy.Symbol) -> sympy.And:
    """
    Builds a easy-to-understand inequality, solving for ``symbol`` and remove infinities.
    """

    ineqs = _remove_infinities(sympy.reduce_inequalities(inequality, [symbol]))

    return sympy.And(*ineqs)
