from __future__ import annotations

from silx.gui import qt
from .ProcessManagerWidget import ProcessManagerWidget


class ProcessManagerWindow(qt.QMainWindow):
    """
    Main window of the process manager
    """

    def __init__(self, parent):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)

        self._centralWidget = ProcessManagerWidget(parent=self)
        self.setCentralWidget(self._centralWidget)
