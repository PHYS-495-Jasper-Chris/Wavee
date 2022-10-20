"""
A PlotWidget that can be dropped into.
"""

import pyqtgraph

from PyQt6 import QtGui


class DroppablePlotWidget(pyqtgraph.PlotWidget):
    """
    A PlotWidget that can be dropped into.
    """

    def __init__(self, parent=None, background='default', plotItem=None, **kargs):

        super().__init__(parent, background, plotItem, **kargs)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        print("drag enter event:", event)

        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent):
        """
        A drop event has occurred. Forward it to a listening slot in the MainWindow.
        """

        print("drop event:", event)
