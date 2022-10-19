import pyqtgraph


class DroppablePlotWidget(pyqtgraph.PlotWidget):
    """
    A PlotWidget that can be dropped into.
    """

    def __init__(self, parent=None, background='default', plotItem=None, **kargs):

        super().__init__(parent, background, plotItem, **kargs)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, ev):
        print("drag enter event:", ev)

        ev.accept()

    def dropEvent(self, ev):
        """
        A drop event has occurred. Forward it to a listening slot in the MainWindow.
        """

        print("drop event:", ev)
