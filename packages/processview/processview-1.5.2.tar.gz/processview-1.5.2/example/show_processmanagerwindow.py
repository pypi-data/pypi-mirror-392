from __future__ import annotations

import time
import numpy
import threading
from silx.gui import qt
from processview.gui.processmanager import ProcessManagerWindow
from processview.core.superviseprocess import SuperviseProcess
from processview.core.dataset import Dataset
from processview.core.dataset import DatasetIdentifier
from processview.core.manager import DatasetState
from processview.gui.processmanager import ProcessManager
import datetime


class _DummyDataset(Dataset):
    def __init__(self, name):
        super().__init__()
        self.__name = name

    def __str__(self) -> str:
        return self.__name

    def get_identifier(self) -> DatasetIdentifier:
        return _DummyIdentifier(
            self,
            metadata={
                "name": self.__name,
                "creation_time": datetime.datetime.now(),
                "modification_time": datetime.datetime.now(),
            },
        )


class _DummyIdentifier(DatasetIdentifier):
    def to_str(self):
        return str(self)

    def __str__(self):
        return self.name()

    def __eq__(self, other):
        return self.name() == other.name()

    def __hash__(self):
        return hash(self.name())


app = qt.QApplication([])

window = ProcessManagerWindow(parent=None)
window.show()

p1 = SuperviseProcess(name="process1")
p2 = SuperviseProcess(name="process2")
p3 = SuperviseProcess(name="process3")


manager = ProcessManager()


class RecursiveThread(threading.Thread):
    def __init__(self, execute_each: int):
        self.running = True
        self.execute_each = execute_each
        super().__init__()

    def run(self):
        """Method implementing thread loop that updates the plot"""
        while self.running:
            time.sleep(self.execute_each)
            self.process()

    def process(self):
        raise NotImplementedError()

    def stop(self):
        """Stop the update thread"""
        self.running = False
        self.join(2)


class CreateNewDataset(RecursiveThread):
    """Thread creating a new dataset each n seconds"""

    def process(self):
        dataset = _DummyDataset(f"scan {numpy.random.randint(0, 999999)}")
        manager.notify_dataset_state(
            dataset=dataset, state=DatasetState.PENDING, process=p1
        )


class UpdateDataset(RecursiveThread):
    """Thread that will update randomly one of the existing dataset"""

    def process(self):
        datasets = manager.get_datasets()
        if len(datasets) == 0:
            return
        dataset_to_update = numpy.random.choice(datasets)
        state = numpy.random.choice(DatasetState)
        process = numpy.random.choice(manager.get_processes())
        manager.notify_dataset_state(
            dataset=dataset_to_update,
            state=state,
            process=process,
        )


create_new_dataset_thread = CreateNewDataset(execute_each=3)
create_new_dataset_thread.start()
update_dataset_thread = UpdateDataset(execute_each=1)
update_dataset_thread.start()

app.exec_()

create_new_dataset_thread.stop()
update_dataset_thread.stop()
