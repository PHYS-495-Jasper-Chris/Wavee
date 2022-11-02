"""
A helper module providing convenience functions for sympy.
"""

from typing import List

import sympy
import sympy.core as sympyc


def _remove_infinities(inequality: sympyc.Basic) -> List[sympyc.relational.Relational]:
    """
    Remove infinities from inequality, returning a list of simplified inequalities.

    ``inequality`` is either a list of inequalities or a single inequality.
    """

    if len(inequality.args) <= 0:
        return []

    ineqs = []

    if isinstance(inequality.args[0], sympyc.relational.Relational):
        for ineq in inequality.args:
            if not ineq.has(sympyc.numbers.Infinity) and not ineq.has(
                    sympyc.numbers.NegativeInfinity):
                ineqs.append(ineq)
    else:
        ineqs = ([inequality] if not inequality.has(sympyc.numbers.Infinity)
                 and not inequality.has(sympyc.numbers.NegativeInfinity) else [])

    return ineqs


def clean_inequality(inequality: sympyc.relational.Relational, symbol: sympyc.Symbol) -> sympy.And:
    """
    Builds a easy-to-understand inequality, solving for ``symbol`` and remove infinities.
    """

    ineqs = _remove_infinities(sympy.reduce_inequalities(inequality, [symbol]))

    return sympy.And(*ineqs)
