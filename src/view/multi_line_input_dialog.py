"""
A QDialog with multiple input lines.
"""

from typing import List, Optional, Tuple, Type, TypeVar

from PyQt6 import QtWidgets, QtCore


class MultiLineInputDialog(QtWidgets.QDialog):
    """
    A QDialog with multiple input lines.
    """

    LineType = TypeVar("LineType", bound=QtWidgets.QWidget)
    """
    A generic line edit type.
    """

    def __init__(self,
                 labels: List[str],
                 parent: Optional[QtWidgets.QWidget] = None,
                 description: Optional[str] = None) -> None:
        super().__init__(parent)

        self.labels = labels
        self.description = description

        self.lines: List[MultiLineInputDialog.LineType] = []

    def get_doubles(self) -> Tuple[List[float], bool]:
        """
        Get all input lines as floats, as well as a bool demonstrating the status.

        If the dialog was accepted and all lines could be successfully converted to floats,
        then success is set to True. Otherwise, the success is False.

        Any floats that could not be converted (or on a rejected dialog) are set to NaN.

        Returns:
            tuple(List[float], bool): Every line's value as a float and the success as a bool.
        """

        self._make_layout(QtWidgets.QDoubleSpinBox)

        doubles, success = [float("nan") for _ in self.lines], False

        if self.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            success = True
            for i, line_edit in enumerate(self.lines):
                try:
                    doubles[i] = float(line_edit.text())
                except ValueError:
                    success = False

        return doubles, success

    def get_texts(self) -> Tuple[List[str], bool]:
        """
        Get all input lines as strings, as well as a bool demonstrating the status.

        If the dialog was accepted, then success is set to True. Otherwise, the success is False.

        Returns:
            tuple(List[str], bool): Every line's text as a str and the success as a bool.
        """

        self._make_layout(QtWidgets.QLineEdit)

        texts, success = ["" for _ in self.lines], False

        if self.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            success = True

            for i, line_edit in enumerate(self.lines):
                texts[i] = line_edit.text()

        return texts, success

    def _make_layout(self, line_type: Type[LineType]) -> None:
        """
        Make the layout with a specific line type.
        """

        layout = QtWidgets.QFormLayout(self)

        if self.description is not None:
            layout.addRow(QtWidgets.QLabel(self.description, self))

        for label in self.labels:
            self.lines.append(line_type(self))
            layout.addRow(QtWidgets.QLabel(label), self.lines[-1])

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel, QtCore.Qt.Orientation.Horizontal,
            self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)
