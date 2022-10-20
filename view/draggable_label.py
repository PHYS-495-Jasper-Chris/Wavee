"""
A draggable QLabel.
"""

import enum
from PyQt6 import QtWidgets, QtGui, QtCore


class DraggableLabel(QtWidgets.QLabel):
    """
    A QLabel that is draggable.

    Implements mouseMoveEvent & mousePressEvent
    """

    class LabelTypes(enum.Enum):
        PointCharge = enum.auto()
        InfiniteLineCharge = enum.auto()

        INVALID = enum.auto()

    def __init__(self):
        """
        Initialize class vars
        """

        self.drag_start_pos = QtCore.QPoint()

        self.label_type = DraggableLabel.LabelTypes.INVALID

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        When the mouse is moved, update its position.
        """

        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            return

        if ((event.pos() - self.drag_start_pos).manhattanLength() <
                QtWidgets.QApplication.startDragDistance()):
            # Haven't moved far enough yet to initiate a drag
            return

        data = QtCore.QByteArray()
        data.append(self.label_type.value)

        mime_data = QtCore.QMimeData()
        mime_data.setData("application/dragndrop-data", data)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(self.pixmap())
