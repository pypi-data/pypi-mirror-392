from __future__ import annotations

from silx.gui import qt
from processview.gui.messagebox import MessageBox
from processview.core.manager import ProcessManager as _ProcessManager
from processview.core.superviseprocess import SuperviseProcess
from processview.core.dataset import DatasetIdentifier

from .ProcessManager import ProcessManager


class ObservationTable(qt.QTableView):
    """
    Redefinition of QTableView for datasets and processes
    """

    def __init__(self, parent):
        qt.QTableView.__init__(self, parent)
        self.verticalHeader().setSectionsClickable(True)

        # QMenu for the dataset name
        self.dataset_menu = qt.QMenu()
        self._copyAction = qt.QAction("copy")
        self.dataset_menu.addAction(self._copyAction)
        self._removeAction = qt.QAction("remove")
        self.dataset_menu.addAction(self._removeAction)

        # QMenu for cell from on dataset and one process
        self.menu_dataset_vs_process = qt.QMenu()
        self._reprocessAction = qt.QAction("reprocess")
        self.menu_dataset_vs_process.addAction(self._reprocessAction)
        self._cancelAction = qt.QAction("cancel")
        self.menu_dataset_vs_process.addAction(self._cancelAction)
        self._infoAction = qt.QAction("info")
        self.menu_dataset_vs_process.addAction(self._infoAction)
        self.menu_dataset_vs_process.addAction(self._removeAction)

        self._target = (None, None)
        # register target of the last menu (process, DatasetIdentifier)

        # connect signal / slot
        self._copyAction.triggered.connect(self._requestDatasetIdCopy)
        self._removeAction.triggered.connect(self._requestRemoveDataset)
        self._reprocessAction.triggered.connect(self._requestReprocessing)
        self._infoAction.triggered.connect(self._requestInfo)
        self._cancelAction.triggered.connect(self._requestCancelProcessing)

    def _processAt(self, x_pos):
        column = self.columnAt(x_pos)
        if column >= 1:
            processes = self.model()._processes
            process_idx = column - 1
            if process_idx < len(processes):
                return processes[list(processes.keys())[process_idx]]

    def _datasetAt(self, y_pos):
        row = self.rowAt(y_pos)
        if row >= 0:
            datasets = self.model()._sorted_datasets
            if row < len(datasets):
                return datasets[list(datasets.keys())[row]]

    def contextMenuEvent(self, event):
        row = self.columnAt(event.pos().x())
        dataset = self._datasetAt(event.pos().y())
        if row == 0:
            # handle column column
            self._target = (None, dataset)
            self.dataset_menu.exec_(event.globalPos())
        else:
            # handle processes column
            process = self._processAt(event.pos().x())
            if (
                process is not None
                and dataset is not None
                and _ProcessManager().met(process=process, dataset=dataset)
            ):
                self._target = (process, dataset)
                self.menu_dataset_vs_process.exec_(event.globalPos())
            else:
                self._target = (None, None)
        super().contextMenuEvent(event)

    def _requestReprocessing(self, *args, **kwargs):
        process, dataset = self._target

        if process is not None and dataset is not None:
            assert isinstance(process, SuperviseProcess)
            assert isinstance(dataset, DatasetIdentifier)
            process.reprocess(dataset.recreate_dataset())

    def _requestCancelProcessing(self, *args, **kwargs):
        process, dataset = self._target
        if process is not None and dataset is not None:
            assert isinstance(process, SuperviseProcess)
            assert isinstance(dataset, DatasetIdentifier)
            process.cancel(dataset.recreate_dataset())

    def _requestDatasetIdCopy(self, *args, **kwargs):
        _, dataset = self._target
        if dataset is not None:
            clipboard = qt.QGuiApplication.clipboard()
            clipboard.setText(dataset.to_str())

    def _requestRemoveDataset(self, *args, **kwargs):
        def get_dataset_at(row: int):
            datasets = self.model()._sorted_datasets
            return datasets.get(
                list(datasets.keys())[row],
                None,
            )

        datasets = [get_dataset_at(index.row()) for index in self.selectedIndexes()]
        [ProcessManager().remove_dataset(dataset) for dataset in datasets]
        self.model().remove_datasets(datasets)

    def _requestInfo(self, *args, **kwargs):
        process, dataset = self._target
        if process is not None and dataset is not None:
            infos = ProcessManager().get_dataset_details(
                dataset=dataset, process=process
            )
            if infos in (None, ""):
                infos = "No extra information provided"

            msg = MessageBox(self)
            msg.setInfos(infos=infos)
            extra_info = "{} processing {}".format(process.name, dataset)
            msg.setWindowTitle(extra_info)
            msg.setWindowModality(qt.Qt.NonModal)
            msg.show()

    def sizeHintForColumn(self, column):
        if column == 0:
            return 350
        else:
            return super().sizeHintForColumn(column)
