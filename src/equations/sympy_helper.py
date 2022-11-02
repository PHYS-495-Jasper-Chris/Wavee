from typing import List

import sympy


def _remove_infinities(inequality: sympy.core.relational.Relational) -> List:
    """
    Remove infinities from inequality, returning a simplified inequality.
    """

    if len(inequality.args) <= 0:
        return []

    ineqs = []

    if isinstance(inequality.args[0], sympy.core.relational.Relational):
        for ineq in inequality.args:
            if not ineq.has(sympy.core.numbers.Infinity) and not ineq.has(
                    sympy.core.numbers.NegativeInfinity):
                ineqs.append(ineq)

    else:
        ineqs = ([inequality] if not inequality.has(sympy.core.numbers.Infinity)
                 and not inequality.has(sympy.core.numbers.NegativeInfinity) else [])

    return ineqs


def clean_inequality(inequality: sympy.core.relational.Relational,
                     symbol: sympy.Symbol) -> sympy.And:
    """
    Builds a easy-to-understand inequality, solving for ``symbol`` and remove infinities.
    """

    ineqs = _remove_infinities(sympy.reduce_inequalities(inequality, [symbol]))

    return sympy.And(*ineqs)
