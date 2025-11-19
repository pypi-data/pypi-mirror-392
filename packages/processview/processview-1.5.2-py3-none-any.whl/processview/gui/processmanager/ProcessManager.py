from __future__ import annotations

from silx.gui import qt
from processview.core.manager import ProcessManager as _ProcessManager
from processview.core.superviseprocess import SuperviseProcess
from processview.utils import docstring
from processview.core.manager import DatasetState


class ProcessManager(qt.QObject):
    sigUpdated = qt.Signal()
    """Signal emitted when the state of some process / dataset is updated
    """

    sigNewProcessRegistered = qt.Signal()
    """Signal emitted when a new process is registered"""

    sigProcessUnregistered = qt.Signal()
    """Signal emitted when a process is unregistered"""

    sigProcessRenamed = qt.Signal(SuperviseProcess)
    """Emit when the process is renamed"""

    def __init__(self):
        qt.QObject.__init__(self)
        self.manager = _ProcessManager()

        # monkey patch manager updated function
        # TODO: add / remove callback would be simpler
        self.manager.add_update_callback(self.updated)
        self.manager.add_new_process_callback(self.processAdded)
        self.manager.add_process_removed_callback(self.processRemoved)
        self.manager.add_process_name_changed_callback(self.processRenamed)

    def updated(self):
        self.sigUpdated.emit()

    def processAdded(self):
        self.sigNewProcessRegistered.emit()

    def processRemoved(self):
        self.sigProcessUnregistered.emit()

    def processRenamed(self, process):
        self.sigProcessRenamed.emit(process)

    def destroyed(self, object_):
        self.manager.remove_update_callback(self.updated)
        qt.QObject.destroyed(object_)

    # expose some of the original ProcessManager API
    @docstring(_ProcessManager)
    def notify_dataset_state(self, dataset, process, state, details=None) -> None:
        self.manager.notify_dataset_state(
            dataset=dataset, process=process, state=state, details=details
        )

    @docstring(_ProcessManager)
    def get_dataset_state(self, dataset, process) -> None | DatasetState:
        return self.manager.get_dataset_state(dataset_id=dataset, process=process)

    @docstring(_ProcessManager)
    def get_dataset_details(self, dataset, process) -> None | DatasetState:
        return self.manager.get_dataset_details(dataset_id=dataset, process=process)

    @docstring(_ProcessManager)
    def get_dataset_stream(self, dataset, time_stamp=False) -> tuple:
        return self.manager.get_dataset_stream(dataset=dataset, time_stamp=time_stamp)

    @docstring(_ProcessManager)
    def get_process_history(self, process, time_stamp=False) -> tuple:
        return self.manager.get_process_history(process=process, time_stamp=time_stamp)

    @docstring(_ProcessManager)
    def get_processes(self):
        return self.manager.get_processes()

    @docstring(_ProcessManager)
    def get_datasets(self):
        return self.manager.get_datasets()

    def remove_dataset(self, *args, **kwargs):
        return self.manager.remove_dataset(*args, **kwargs)
