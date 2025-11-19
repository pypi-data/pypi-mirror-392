from __future__ import annotations

import fnmatch
import datetime

from silx.gui import qt
from processview.core.sorting import SortType
from processview.core.manager import DatasetState
from processview.core.dataset import DatasetIdentifier
from processview.gui.utils.qitem_model_resetter import qitem_model_resetter

from .ProcessManager import ProcessManager

from collections import OrderedDict


_DATASET_STATE_BACKGROUND = {
    DatasetState.ON_GOING: qt.QColor("#839684"),  # light blue
    DatasetState.SUCCEED: qt.QColor("#068c0c"),  # green
    DatasetState.FAILED: qt.QColor("#f52718"),  # red
    DatasetState.PENDING: qt.QColor("#609ab3"),  # blue gray
    DatasetState.SKIPPED: qt.QColor("#f08e0e"),  # light orange
    DatasetState.WAIT_USER_VALIDATION: qt.QColor("#cb34c1"),  # pink
    DatasetState.CANCELLED: qt.QColor("#a4a8a2"),  # light black
}


class DatasetProcessModel(qt.QAbstractTableModel):
    def __init__(self, parent, header, *args):
        qt.QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self._processes = OrderedDict()
        # processes with order as key and Process as value
        self._sorted_datasets = OrderedDict()
        self._unsorted_datasets = OrderedDict()
        self._processPatterns = tuple()
        # is there some process name pattern to follow ?
        self._datasetPatterns = tuple()
        # is there some dataset id pattern to follow ?
        self._sort_type = SortType.FIRST_APPEARANCE

    def _match_dataset_patterns(self, dataset):
        if len(self._datasetPatterns) == 0:
            return True
        for pattern in self._datasetPatterns:
            if fnmatch.fnmatch(str(dataset), pattern):
                return True
        return False

    def _match_process_patterns(self, process):
        if len(self.process_patterns) == 0:
            return True
        for pattern in self._processPatterns:
            if process.name is None or pattern is None:
                continue
            elif fnmatch.fnmatch(process.name, pattern):
                return True
        return False

    @property
    def process_patterns(self):
        return self._processPatterns

    @process_patterns.setter
    def process_patterns(self, patterns):
        self._processPatterns = patterns

    @property
    def dataset_patterns(self):
        return self._datasetPatterns

    @dataset_patterns.setter
    def dataset_patterns(self, patterns):
        self._datasetPatterns = patterns

    def remove_datasets(self, datasets):
        remaining_datasets = list(self._unsorted_datasets)
        for dataset in datasets:
            if not isinstance(dataset, DatasetIdentifier):
                raise ValueError(
                    f"dataset is expected to be a dataset identifier. Get {type(dataset)} instead"
                )
            try:
                remaining_datasets.remove(dataset)
            except Exception:
                pass

        with qitem_model_resetter(self):
            self.setDatasets(remaining_datasets)

    def clear(self):
        with qitem_model_resetter(self):
            self._processes = OrderedDict()

    def rowCount(self, parent=None):
        return len(self._unsorted_datasets)

    def columnCount(self, parent=None):
        return len(self._processes) + 1

    def setProcesses(self, processes):
        assert isinstance(processes, (tuple, list))
        with qitem_model_resetter(self):
            self._processes = {}
            processes = list(filter(self._match_process_patterns, processes))
            for i_process, process in enumerate(processes):
                self._processes[i_process] = process

    @staticmethod
    def sort_datasets(datasets: list, sort_type):
        if sort_type is SortType.FIRST_APPEARANCE:
            pass
        elif sort_type is SortType.LAST_APPEARANCE:
            datasets.reverse()
        elif sort_type in (SortType.ALPHABETICAL, SortType.REVERSE_ALPHABETICAL):
            datasets = sorted(
                datasets,
                key=lambda x: x.name() or "",
                reverse=sort_type is SortType.REVERSE_ALPHABETICAL,
            )
        elif sort_type in (SortType.CREATION_TIME, SortType.REVERSE_CREATION_TIME):
            datasets = sorted(
                datasets,
                key=lambda x: x.creation_time() or datetime.datetime.fromtimestamp(0),
                reverse=sort_type is SortType.REVERSE_CREATION_TIME,
            )
        elif sort_type in (
            SortType.MODIFICATION_TIME,
            SortType.REVERSE_MODIFICATION_TIME,
        ):
            datasets = sorted(
                datasets,
                key=lambda x: x.modification_time()
                or datetime.datetime.fromtimestamp(0),
                reverse=sort_type is SortType.REVERSE_MODIFICATION_TIME,
            )
        else:
            raise ValueError("sort type not handled")
        return datasets

    def setDatasets(self, datasets):
        assert isinstance(datasets, (tuple, list))
        with qitem_model_resetter(self):
            self._unsorted_datasets = datasets
            # filter datasets
            datasets = list(filter(self._match_dataset_patterns, datasets))
            # sort datasets
            datasets = self.sort_datasets(datasets=datasets, sort_type=self._sort_type)

            self._sorted_datasets.clear()
            for i_dataset, dataset in enumerate(datasets):
                self._sorted_datasets[i_dataset] = dataset

    def headerData(self, col, orientation, role):
        if orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
            if col == 0:
                return
            else:
                process_idx = col - 1
            if process_idx < len(self._processes):
                return self._processes[process_idx].name
        return None

    def data(self, index, role):
        if index.isValid() is False:
            return None

        if role not in (qt.Qt.DisplayRole, qt.Qt.ToolTipRole, qt.Qt.BackgroundRole):
            return None

        if index.column() == 0:
            # if dataset name
            if role == qt.Qt.DisplayRole:
                return self._sorted_datasets[index.row()].short_description() or str(
                    self._sorted_datasets[index.row()]
                )
            elif role == qt.Qt.ToolTipRole:
                return self._sorted_datasets[index.row()].long_description()
            elif role == qt.Qt.BackgroundRole:
                return qt.QColor("#dedede")
            else:
                return

        dataset_short_name = self._sorted_datasets[index.row()]
        process_name = self._processes[index.column() - 1]
        dataset_process_state = ProcessManager().get_dataset_state(
            dataset=dataset_short_name, process=process_name
        )
        dataset_process_details = ProcessManager().get_dataset_details(
            dataset=dataset_short_name, process=process_name
        )
        if role == qt.Qt.BackgroundRole:
            if dataset_process_state is None:
                # if "unmet"
                return qt.QColor("#ffffff")
            else:
                return _DATASET_STATE_BACKGROUND[dataset_process_state]
        elif role == qt.Qt.DisplayRole:
            if dataset_process_state is None:
                return ""
            else:
                return dataset_process_state.value
        if role == qt.Qt.ToolTipRole:
            if dataset_process_details is None:
                return ""
            else:
                return dataset_process_details

    def _setSorting(self, sort_type: SortType):
        sort_type = SortType(sort_type)
        changed = self._sort_type is not sort_type
        if changed:
            self._sort_type = sort_type
            self.setDatasets(datasets=self._unsorted_datasets)
            self.layoutChanged.emit()
