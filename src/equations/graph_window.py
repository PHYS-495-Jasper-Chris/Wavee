"""
A graph window, holding the electric field of arbitrary charge distributions.
"""

from typing import Callable, List, Optional

import numpy as np
from sympy import latex

# pylint: disable=import-error
from equations.base_charge import BaseCharge
from equations.constants import Point2D

# pylint: enable=import-error


class Window:
    """
    A collection of charges, to be graphed
    """

    charges_updated: Callable[[], None]
    """
    A signal to be emitted when an aspect of any charge, or the list of charges, changes.

    For example, if the position of a charge changes, this signal is emitted. Also, if a charge is
    added or removed, this signal is emitted.
    """

    def __init__(self, charges: Optional[List[BaseCharge]] = None) -> None:
        """
        Initialize a collection of charges of any kind.

        Args:
            charges (Optional[List[PointCharge]]): The list of charges. Defaults to an empty list.
        """

        self.charges = charges or []

        self._removed_charges: List[BaseCharge] = []

    def add_charge(self, point_charge: BaseCharge) -> None:
        """
        Add point charge to the test window.

        Args:
            point_charge (PointCharge): Point charge to be added.
        """

        self.charges.append(point_charge)

        point_charge.charge_updated = self.charges_updated

        self.charges_updated()

    def remove_last_charge(self) -> None:
        """
        Remove the last charge that was added (ie, the charge at the end of the list of charges).
        """

        if len(self.charges) > 0:
            charge = self.charges.pop()
            self._removed_charges.append(charge)
            charge.charge_updated = lambda: None

            self.charges_updated()

    def undo_charge_removal(self) -> None:
        """
        Undo the latest removal if any exists.
        """

        if len(self._removed_charges) > 0:
            charge = self._removed_charges.pop()
            self.charges.append(charge)
            charge.charge_updated = self.charges_updated

            self.charges_updated()

    def remove_all_charges(self) -> None:
        """
        Remove all charges that are currently on the window, adding them to the list of removed
        charges.
        """

        if len(self.charges) > 0:
            for charge in self.charges:
                charge.charge_updated = lambda: None
                self._removed_charges.append(charge)

            self.charges = []
            self.charges_updated()

    def readd_all_charges(self) -> None:
        """
        Re-add all charges that have been removed to the window, removing them from the list of
        removed charges.
        """

        if len(self._removed_charges) > 0:
            for charge in self._removed_charges:
                charge.charge_updated = self.charges_updated
                self.charges.append(charge)

            self._removed_charges = []
            self.charges_updated()

    def net_electric_field(self, position: Point2D) -> float:
        """
        Calculate the net electric field magnitude at a point

        Args:
            position (Point2D): The position to measure the electric field at

        Returns:
            float: magnitude of electric field
        """

        return np.sqrt(self.electric_field_x(position)**2 + self.electric_field_y(position)**2)

    def electric_field_x(self, position: Point2D) -> float:
        """
        Calculate the x component of the electric field at a point.

        Args:
            position (Point2D): The position to measure the electric field at.

        Returns:
            float: x component of electric field.
        """

        e_x = 0.0

        # Sum up electric field x component for each charge
        for charge in self.charges:
            x_inc = charge.electric_field_x(position)
            e_x += x_inc if np.isfinite(x_inc) else 0.0

        return e_x

    def electric_field_y(self, position: Point2D) -> float:
        """
        Calculate the y component of the electric field at a point.

        Args:
            position (Point2D): The position to measure the electric field at.

        Returns:
            float: y component of electric field.
        """

        e_y = 0.0

        # Sum up electric field y component for each point charge
        for charge in self.charges:
            y_inc = charge.electric_field_y(position)
            e_y += y_inc if np.isfinite(y_inc) else 0.0

        return e_y

    def electric_field_mag_html(self) -> str:
        """
        Get the cumulative electric field magnitude by summing each charge's magnitude.
        """

        if len(self.charges) == 0:
            return ""

        full_eqn: str = ""

        for i, charge in enumerate(self.charges):
            full_eqn += f"E_{i}=" + latex(charge.electric_field_mag_string().simplify()) + ","

        full_eqn = full_eqn[:-1]

        source = f"""
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

        return source

    def electric_field_x_html(self) -> str:
        """
        Get the cumulative electric field magnitude by summing each charge's magnitude.
        """

        if len(self.charges) == 0:
            return ""

        full_eqn: str = ""

        for charge in self.charges:
            full_eqn += "\\left(" + latex(charge.electric_field_x_string().simplify()) + "\\right)+"

        full_eqn = "E_x(x,y)=" + full_eqn[:-1]

        source = f"""
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

        return source

    def electric_field_y_html(self) -> str:
        """
        Get the cumulative electric field magnitude by summing each charge's magnitude.
        """

        if len(self.charges) == 0:
            return ""

        full_eqn: str = ""

        for charge in self.charges:
            full_eqn += "\\left(" + latex(charge.electric_field_y_string().simplify()) + "\\right)+"

        full_eqn = "E_y(x,y)=" + full_eqn[:-1]

        source = f"""
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

        return source
