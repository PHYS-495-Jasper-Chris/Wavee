"""
A ScatterPlotItem with elements whose radii scale depending on the zoom.
"""

from typing import List

import pyqtgraph


class ScalingScatterPlotItem(pyqtgraph.ScatterPlotItem):
    """
    A ScatterPlotItem with elements whose radii scale depending on the zoom.
    """

    def viewRangeChanged(self):
        """
        When the ViewBox range changes, update every point charge's size accordingly.
        """

        view_box = self.getViewBox()
        if not isinstance(view_box, pyqtgraph.ViewBox):
            # The ViewBox does not exist yet. That's fine.
            return

        view_range: List[List[float]] = view_box.viewRange()
        x_range = view_range[0][1] - view_range[0][0]
        y_range = view_range[1][1] - view_range[1][0]

        # Assume that the size is set for a 1x1 range.
        # If this is the case, then the radius should decrease as the square of each side.
        # However, we're not guaranteed that the x and y ranges are equal (or even close to equal).
        # Let's assume that the smaller range is more representative, and use that as our scaling
        # factor.

        # TODO: decide if this is the best way to approach this, and figure out what I'm doing
        # that's stupid here.

        divisor = min(x_range, y_range)**2

        item: pyqtgraph.SpotItem
        for item in self.points():
            try:
                initial_size = item.data()["initial_size"]
                brush = item.data()["brush"]
            except (KeyError, TypeError):
                continue

            new_size = max(initial_size / divisor, 25)
            item.setSize(new_size)
            item.setBrush(brush)

        return super().viewRangeChanged()
