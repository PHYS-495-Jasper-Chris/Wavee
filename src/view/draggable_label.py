"""
A draggable QLabel.
"""

import enum

from typing import Optional

from PyQt6 import QtWidgets, QtGui, QtCore


class DraggableLabel(QtWidgets.QLabel):
    """
    A QLabel that is draggable.

    Implements mouseMoveEvent & mousePressEvent
    """

    MIME_FORMAT = "application/drag-n-drop-data"
    """
    The MIME format to use for Drag and Drop data
    """

    class LabelTypes(enum.Enum):
        PointCharge = enum.auto()
        InfiniteLineCharge = enum.auto()

        INVALID = enum.auto()

    def __init__(self, parent: Optional[QtWidgets.QWidget]):
        """
        Initialize class vars
        """

        super().__init__(parent)

        self.drag_start_pos = QtCore.QPoint()

        self.label_type = DraggableLabel.LabelTypes.INVALID

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        When the mouse is moved, update its position.
        """

        if not event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            return

        if ((event.pos() - self.drag_start_pos).manhattanLength() <
                QtWidgets.QApplication.startDragDistance()):
            # Haven't moved far enough yet to initiate a drag
            return

        data = QtCore.QByteArray()
        val: int = int(self.label_type.value)
        data.append(val.to_bytes((val.bit_length() + 7) // 8, "little"))

        mime_data = QtCore.QMimeData()
        mime_data.setData(DraggableLabel.MIME_FORMAT, data)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(self.pixmap())

        drag.exec()
