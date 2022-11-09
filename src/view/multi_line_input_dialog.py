"""
A QDialog with multiple input lines.
"""

from typing import List, Optional, Tuple, Type, TypeVar

from PyQt6 import QtCore, QtWidgets


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

    def get_doubles(
        self,
        value: float = 0.0,
        minimum: float = float("-inf"),
        maximum: float = float("inf")
    ) -> Tuple[List[float], bool]:
        """
        Get all input lines as floats, as well as a bool demonstrating the status.

        If the dialog was accepted and all lines could be successfully converted to floats,
        then success is set to True. Otherwise, the success is False.

        Any floats that could not be converted (or on a rejected dialog) are set to NaN.

        Args:
            value (float): The default value to set the spinners to. Defaults to 0.
            minimum (float): The minimum possible value. Defaults to -INF.
            maximum (float): The maximum possible value. Defaults to INF.

        Returns:
            Tuple[List[float], bool]: Every line's value as a float and the success as a bool.
        """

        spin_boxes = self._make_layout(QtWidgets.QDoubleSpinBox)

        for spin_box in spin_boxes:
            spin_box.setValue(value)
            spin_box.setMinimum(minimum)
            spin_box.setMaximum(maximum)
            spin_box.setMinimumWidth(100)
            spin_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        doubles, success = [float("nan") for _ in spin_boxes], False

        if self.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            success = True
            for i, spin_box in enumerate(spin_boxes):
                try:
                    doubles[i] = float(spin_box.text())
                except ValueError:
                    success = False

        return doubles, success

    def get_texts(self) -> Tuple[List[str], bool]:
        """
        Get all input lines as strings, as well as a bool demonstrating the status.

        If the dialog was accepted, then success is set to True. Otherwise, the success is False.

        Returns:
            tuple[List[str], bool]: Every line's text as a str and the success as a bool.
        """

        line_edits = self._make_layout(QtWidgets.QLineEdit)

        texts, success = ["" for _ in line_edits], False

        if self.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            success = True

            line_edit: QtWidgets.QLineEdit
            for i, line_edit in enumerate(line_edits):
                texts[i] = line_edit.text()

        return texts, success

    def _make_layout(self, line_type: Type[LineType]) -> List[LineType]:
        """
        Make the layout with a specific line type.

        Args:
            line_type (Type[LineType]): The type of user-editable line to add to the layout.

        Returns:
            List[LineType]: The list of user-editable lines based on the ``line_type``.
        """

        layout = QtWidgets.QFormLayout(self)

        if self.description is not None:
            layout.addRow(QtWidgets.QLabel(self.description, self))

        lines = []
        for label in self.labels:
            lines.append(line_type(self))
            layout.addRow(QtWidgets.QLabel(label), lines[-1])

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel, QtCore.Qt.Orientation.Horizontal,
            self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        return lines
