"""
A draggable QLabel.
"""

import enum
import sys

from typing import Optional

from PyQt6 import QtWidgets, QtGui, QtCore


class DraggableLabel(QtWidgets.QLabel):
    """
    A QLabel that is draggable.

    Implements mouseMoveEvent & mousePressEvent.
    """

    MIME_FORMAT = "application/drag-n-drop-data"
    """
    The MIME format to use for Drag and Drop data.
    """

    class LabelTypes(enum.IntEnum):
        """
        Enum of possible labels.
        """

        POINT_CHARGE = enum.auto()
        INFINITE_LINE_CHARGE = enum.auto()

        INVALID = enum.auto()

    def __init__(self, parent: Optional[QtWidgets.QWidget]):
        """
        Initialize class variables.

        Args:
            parent (Optional[QWidget]): The parent widget that this widget is a child widget of.
        """

        super().__init__(parent)

        self.drag_start_pos = QtCore.QPoint()

        self.label_type = DraggableLabel.LabelTypes(DraggableLabel.LabelTypes.INVALID)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:  # pylint: disable=invalid-name
        """
        When the left mouse button is pressed, mark the beginning of the drag.

        Args:
            ev (QMouseEvent): The QMouseEvent indicating a mouse press.
        """

        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            self.drag_start_pos = ev.pos()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:  # pylint: disable=invalid-name
        """
        When the mouse is moved, update its position.

        Args:
            ev (QMouseEvent): The QMouseEvent indicating a mouse movement.
        """

        if not ev.buttons() & QtCore.Qt.MouseButton.LeftButton:
            return

        if ((ev.pos() - self.drag_start_pos).manhattanLength() <
                QtWidgets.QApplication.startDragDistance()):
            # Haven't moved far enough yet to initiate a drag
            return

        data = QtCore.QByteArray()
        val = self.label_type.value
        data.append(val.to_bytes((val.bit_length() + 7) // 8, sys.byteorder))

        mime_data = QtCore.QMimeData()
        mime_data.setData(DraggableLabel.MIME_FORMAT, data)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(self.pixmap())

        drag.exec()
