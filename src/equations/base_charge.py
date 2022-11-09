"""
An abstract charge, from which subclasses overload.
"""

import abc
from typing import Callable

from PyQt6 import QtCore
from sympy import Basic, preorder_traversal, Float

from equations.constants import Point2D  # pylint: disable=import-error


class BaseCharge(abc.ABC):
    """
    An abstract charge, from which subclasses overload.
    """
    charge_updated: Callable[[], None]
    """
    A signal to be emitted when an aspect of this charge changes.

    For example, if the position or charge changes, this signal is emitted.

    Note that this is not the same signal used when a charge is removed or added - that signal is
    emitted from ``Window``.
    """

    default_rounding = -1
    """
    number of decimal places to show when creating the equation string. If value is -1 no rounding
    will be done
    """

    @abc.abstractmethod
    def electric_field_magnitude(self, point: Point2D) -> float:
        """
        Return the electric field magnitude generated by this charge at a given point.

        Args:
            point (Point2D): x, y location of test point.

        Returns:
            float: magnitude of electric field.
        """

    @abc.abstractmethod
    def electric_field_x(self, point: Point2D) -> float:
        """
        Calculate the x component of the magnetic field generated by the charge at a given point.

        Args:
            point (Point2D): test point to check.

        Returns:
            float: x component of electric field.
        """

    @abc.abstractmethod
    def electric_field_y(self, point: Point2D) -> float:
        """
        Calculate the y component of the magnetic field generated by the charge at a given point.

        Args:
            point (Point2D): test point to check.

        Returns:
            float: y component of electric field.
        """

    @abc.abstractmethod
    def open_menu(self, pos: QtCore.QPointF) -> bool:
        """
        Open a context menu for this charge.

        Configures options associated with the charge.

        Args:
            pos (QPointF): The location to open the menu at.

        Returns:
            bool: True if this charge should be deleted, False otherwise.
        """

    @abc.abstractmethod
    def electric_field_mag_eqn(self, default_rounding = None) -> Basic:
        """
        Returns the position-independent electric field equation.

        Returns:
            Basic: sympy representation of the signed magnitude of the electric field.
        """

    @abc.abstractmethod
    def electric_field_x_eqn(self, default_rounding = None) -> Basic:
        """
        Returns the position-independent electric field x-component equation.

        Returns:
            Basic: sympy representation of the x-component of the electric field.
        """

    @abc.abstractmethod
    def electric_field_y_eqn(self, default_rounding = None) -> Basic:
        """
        Returns the position-independent electric field y-component equation.

        Returns:
            Basic: sympy representation of the y-component of the electric field.
        """

    def round_symbolic(self, expression, digits) -> Basic:
        """
        Rounds floats within sympy expression to given digits
        """
        tmp = expression
        for a in preorder_traversal(expression):
            if isinstance(a, Float):
                tmp = tmp.subs(a, round(a, digits))
        return tmp
