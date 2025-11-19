from __future__ import annotations

from silx.gui import qt
from processview.core.superviseprocess import SuperviseProcess

from .ProcessManager import ProcessManager
from ._OptionsWidget import OptionsWidget
from ..DropDownWidget import DropDownWidget
from .ObservationTable import ObservationTable
from ._DatasetProcessModel import DatasetProcessModel


class ProcessManagerWidget(qt.QWidget):
    """
    Main widget to display dataset vs process metadata
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self._manager = ProcessManager()

        self._optionsWidget = OptionsWidget(parent=self)
        self._dropDownOptionsWidget = DropDownWidget(parent=self)
        self._dropDownOptionsWidget.setWidget(self._optionsWidget)

        self._dropDownOptionsWidget.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)
        self.layout().addWidget(self._dropDownOptionsWidget)

        self.observationTable = ObservationTable(self)

        self.layout().addWidget(self.observationTable)
        self.observationTable.setModel(
            DatasetProcessModel(parent=self.observationTable, header=tuple())
        )
        self.observationTable.resizeColumnsToContents()
        self.observationTable.setSortingEnabled(True)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        # connect signal / slot
        self._manager.sigUpdated.connect(self._updateDatasetStates)
        self._manager.sigNewProcessRegistered.connect(self._updateProcesses)
        self._optionsWidget.filterWidget.sigDatasetPatternEditingFinished.connect(
            self._filterUpdated
        )
        self._optionsWidget.filterWidget.sigProcessPatternEditingFinished.connect(
            self._filterUpdated
        )
        self._manager.sigProcessUnregistered.connect(self._updateProcesses)
        self._optionsWidget._orderingWidget.sigSortTypeChanged.connect(
            self.observationTable.model()._setSorting
        )
        self._manager.sigProcessRenamed.connect(self._renameProcess)
        # update to fit existing processes / datasets
        self._updateProcesses()
        self._updateDatasetStates()

    def _updateDatasetStates(self):
        self.observationTable.model().setDatasets(self._manager.get_datasets())

    def _updateProcesses(self):
        self.observationTable.model().setProcesses(self._manager.get_processes())

    def _renameProcess(self, process: SuperviseProcess):
        self.observationTable.model().headerDataChanged.emit(
            qt.Qt.Horizontal, 0, len(self._manager.get_processes())
        )

    def _filterUpdated(self):
        self.observationTable.model().process_patterns = (
            self._dropDownOptionsWidget.getProcessPatterns()
        )
        self._updateProcesses()
        self.observationTable.model().dataset_patterns = (
            self._dropDownOptionsWidget.getDatasetPatterns()
        )
        self._updateDatasetStates()
