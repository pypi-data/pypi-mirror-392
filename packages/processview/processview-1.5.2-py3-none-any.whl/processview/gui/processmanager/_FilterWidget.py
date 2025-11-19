from __future__ import annotations

from silx.gui import qt
from silx.gui import icons


class FilterWidget(qt.QWidget):
    """
    Widget to define some filtering pattern on dataset and / or processes
    """

    sigProcessPatternEditingFinished = qt.Signal()
    """signal emit when the process pattern editing finished"""

    sigDatasetPatternEditingFinished = qt.Signal()
    """signal emit when the dataset pattern editing finished"""

    def __init__(self, parent=None, name=" filter", font_size=12, icon_size=20):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        self.layout().setSpacing(2)
        self.layout().setContentsMargins(0, 0, 0, 0)

        font = self.font()
        font.setPixelSize(font_size)
        self.setFont(font)

        icon = icons.getQPixmap("processview:gui/icons/magnifying_glass")
        self._researchLabelIcon = qt.QLabel("", parent=self)
        self._researchLabelIcon.setPixmap(icon)
        self.layout().addWidget(qt.QLabel(name, self), 0, 1, 1, 1)
        self.layout().addWidget(self._researchLabelIcon, 0, 2, 1, 1)

        # filter by dataset id / name
        self._datasetLabel = qt.QLabel("dataset", self)
        self.layout().addWidget(self._datasetLabel, 1, 2, 1, 2)
        self._datasetPatternLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._datasetPatternLE, 1, 4, 1, 1)
        tooltip = (
            "Provide one or several dataset name or pattern to only "
            " display those datasets. Pattern should be separated by a "
            "semi colon. Handle linux wild card. Example: "
            "`pattern1; *suffix; prefix*`"
        )
        for widget in self._datasetLabel, self._datasetPatternLE:
            widget.setToolTip(tooltip)
        self._clearDatasetPatternPB = qt.QPushButton("clear", self)
        self._clearDatasetPatternPB.setAutoDefault(True)
        self.layout().addWidget(self._clearDatasetPatternPB, 1, 5, 1, 1)

        # filter by process name
        self._processLabel = qt.QLabel("process", self)
        self.layout().addWidget(self._processLabel, 2, 2, 1, 2)
        self._processPatternLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._processPatternLE, 2, 4, 1, 1)
        tooltip = (
            "Provide one or several process name or pattern to only "
            " display those datasets. Pattern should be separated by a "
            "semi colon. Handle linux wild card. Example: "
            "`pattern1; *suffix; prefix*`"
        )
        for widget in self._processLabel, self._processPatternLE:
            widget.setToolTip(tooltip)
        self._clearProcessPatternPB = qt.QPushButton("clear", self)
        self._clearProcessPatternPB.setAutoDefault(True)
        self.layout().addWidget(self._clearProcessPatternPB, 2, 5, 1, 1)

        # connect signal / slot
        self._clearProcessPatternPB.released.connect(self._processPatternLE.clear)
        self._clearProcessPatternPB.released.connect(
            self._processPatternEditingFinished
        )
        self._clearDatasetPatternPB.released.connect(self._datasetPatternLE.clear)
        self._clearDatasetPatternPB.released.connect(
            self._datasetPatternEditingFinished
        )
        self._datasetPatternLE.editingFinished.connect(
            self._datasetPatternEditingFinished
        )
        self._processPatternLE.editingFinished.connect(
            self._processPatternEditingFinished
        )

    def getProcessPatterns(self) -> tuple:
        patterns = self._processPatternLE.text().lstrip(" ").rstrip(" ")
        if patterns == "":
            return ("*",)
        res = patterns.replace(" ", "")
        return tuple(res.split(";"))

    def getDatasetPatterns(self) -> tuple:
        patterns = self._datasetPatternLE.text().lstrip(" ").rstrip(" ")
        if patterns == "":
            return ("*",)
        res = patterns.replace(" ", "")
        return tuple(res.split(";"))

    def _datasetPatternEditingFinished(self, *args, **kwargs):
        self.sigDatasetPatternEditingFinished.emit()

    def _processPatternEditingFinished(self, *args, **kwargs):
        self.sigProcessPatternEditingFinished.emit()
