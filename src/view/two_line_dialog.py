"""
A QDialog with 2 input lines.
"""

from typing import Optional, Tuple

from PyQt6 import QtWidgets, QtCore


class TwoLineDialog(QtWidgets.QDialog):
    """
    A QDialog with 2 input lines.
    """

    def __init__(self,
                 top_line_label: str = "",
                 bottom_line_label: str = "",
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QFormLayout(self)
        self.top_line_le = QtWidgets.QLineEdit(self)
        layout.addRow(QtWidgets.QLabel(top_line_label), self.top_line_le)

        self.bottom_line_le = QtWidgets.QLineEdit(self)
        layout.addRow(QtWidgets.QLabel(bottom_line_label), self.bottom_line_le)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel, QtCore.Qt.Orientation.Horizontal,
            self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_doubles(self) -> Tuple[float, float, bool]:
        """
        Get both input lines as floats, as well as a bool demonstrating the status.

        If the dialog was accepted and both lines could both be successfully converted to floats,
        then success is set to True. Otherwise, the success is False.

        Any floats that could not be converted (or on a rejected dialog) are set to NaN.

        Returns:
            tuple(float, float, bool): The top line's value as a float, the bottom line's value as a
            float, and the success as a bool.
        """

        top, bottom, success = float("nan"), float("nan"), False

        if self.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            try:
                top = float(self.top_line_le.text())
                bottom = float(self.bottom_line_le.text())

                success = True
            except ValueError:
                pass

        return top, bottom, success
