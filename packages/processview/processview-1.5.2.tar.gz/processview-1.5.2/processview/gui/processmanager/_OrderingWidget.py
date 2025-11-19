from __future__ import annotations

from silx.gui import qt
from processview.core.sorting import SortType, tooltips


class _OrderingWidget(qt.QWidget):
    """Widget to let the user define the ordering of datasets"""

    sigSortTypeChanged = qt.Signal(str)
    """emit when sort type changed. Paramater is the name of the new sorting type"""

    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setLayout(qt.QFormLayout())
        self._sortingTypeCB = qt.QComboBox(self)
        for sort_type in SortType:
            self._sortingTypeCB.addItem(sort_type.value)
            self._sortingTypeCB.setItemData(
                self._sortingTypeCB.findText(sort_type.value),
                tooltips[sort_type],
                qt.Qt.ToolTipRole,
            )
        self.layout().addRow("sorting", self._sortingTypeCB)

        # set up
        self._sortingTypeCB.setCurrentIndex(
            self._sortingTypeCB.findText(SortType.FIRST_APPEARANCE.value)
        )

        # connect signal / slot
        self._sortingTypeCB.currentIndexChanged.connect(self._changed)

    def _changed(self, *args, **kwargs):
        self.sigSortTypeChanged.emit(self.getCurrentSort().value)

    def getCurrentSort(self) -> SortType:
        return SortType(self._sortingTypeCB.currentText())
