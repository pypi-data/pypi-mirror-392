from __future__ import annotations

from silx.gui import qt

from ._OrderingWidget import _OrderingWidget
from ._FilterWidget import FilterWidget


class OptionsWidget(qt.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setLayout(qt.QGridLayout())

        # dataset ordering
        self._orderingWidget = _OrderingWidget(parent=self)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.layout().addWidget(self._orderingWidget, 2, 1, 3, 3)

        # filtering
        self._filterWidget = FilterWidget(parent=self)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.layout().addWidget(self._filterWidget, 4, 1, 3, 3)

    @property
    def filterWidget(self):
        return self._filterWidget

    # expose API
    def getProcessPatterns(self):
        return self._filterWidget.getProcessPatterns()

    def getDatasetPatterns(self):
        return self._filterWidget.getDatasetPatterns()
