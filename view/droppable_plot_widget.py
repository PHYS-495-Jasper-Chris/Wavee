"""
A PlotWidget that can be dropped into.
"""

import pyqtgraph

from PyQt6 import QtGui

from view.draggable_label import DraggableLabel  # pylint: disable=import-error


class DroppablePlotWidget(pyqtgraph.PlotWidget):
    """
    A PlotWidget that can be dropped into.
    """

    def __init__(self, parent=None, background='default', plotItem=None, **kargs):

        super().__init__(parent, background, plotItem, **kargs)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, ev: QtGui.QDragEnterEvent):
        """
        A drag has entered the widget
        """

        if ev.mimeData().hasFormat(DraggableLabel.MIME_FORMAT):
            ev.accept()

    def dragMoveEvent(self, ev: QtGui.QDragMoveEvent):
        """
        A drag is moving in the widget
        """

        if ev.mimeData().hasFormat(DraggableLabel.MIME_FORMAT):
            ev.accept()

    def dragLeaveEvent(self, ev: QtGui.QDragLeaveEvent):
        """
        A drag left the widget
        """

        ev.accept()

    def dropEvent(self, ev: QtGui.QDropEvent):
        """
        A drop event has occurred. Forward it to a listening slot in the MainWindow.
        """

        if not ev.mimeData().hasFormat(DraggableLabel.MIME_FORMAT):
            ev.ignore()

        plot_item = self.getPlotItem()
        if not isinstance(plot_item, pyqtgraph.PlotItem):
            raise RuntimeError("Unable to build plot!")
        view_box = plot_item.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox):
            raise RuntimeError("Unable to rebuild plot")

        mouse_point = view_box.mapSceneToView(ev.position())

        x_pos = mouse_point.x()
        y_pos = mouse_point.y()

        mime_data = ev.mimeData().data(DraggableLabel.MIME_FORMAT)
        label_type = DraggableLabel.LabelTypes(int.from_bytes(mime_data[0], "little"))

        print(x_pos, y_pos)
        print(label_type)

        ev.accept()
