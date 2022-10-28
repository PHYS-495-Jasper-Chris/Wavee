"""
A QDialog with 2 input lines.
"""

from typing import List, Optional, Tuple

from PyQt6 import QtWidgets, QtCore


class MultiLineInputDialog(QtWidgets.QDialog):
    """
    A QDialog with 2 input lines.
    """

    def __init__(self, labels: List[str], parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QFormLayout(self)

        self.line_edits: List[QtWidgets.QLineEdit] = []
        for label in labels:
            self.line_edits.append(QtWidgets.QLineEdit(self))
            layout.addRow(QtWidgets.QLabel(label), self.line_edits[-1])

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel, QtCore.Qt.Orientation.Horizontal,
            self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_doubles(self) -> Tuple[List[float], bool]:
        """
        Get all input lines as floats, as well as a bool demonstrating the status.

        If the dialog was accepted and all lines could be successfully converted to floats,
        then success is set to True. Otherwise, the success is False.

        Any floats that could not be converted (or on a rejected dialog) are set to NaN.

        Returns:
            tuple(List[float], bool): The every line's value as a float and the success as a bool.
        """

        doubles, success = [float("nan") for _ in self.line_edits], False

        if self.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            success = True
            for i, line_edit in enumerate(self.line_edits):
                try:
                    doubles[i] = float(line_edit.text())
                except ValueError:
                    success = False

        return doubles, success
