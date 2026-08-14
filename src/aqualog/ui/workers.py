from __future__ import annotations
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

class WorkerSignals(QObject):
    result = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    finished = pyqtSignal()

class FunctionWorker(QRunnable):

    def __init__(self, fn, *args, progress=False, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.use_progress = progress

    @pyqtSlot()
    def run(self):
        try:
            if self.use_progress:
                self.kwargs['progress_callback'] = lambda current, total: self.signals.progress.emit(current, total)
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as exc:
            self.signals.error.emit(str(exc))
        finally:
            self.signals.finished.emit()
