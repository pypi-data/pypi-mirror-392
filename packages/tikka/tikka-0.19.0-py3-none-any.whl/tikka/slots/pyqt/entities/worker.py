# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
from typing import Callable, List, Optional

from PyQt5.QtCore import QMutex, QObject, QRunnable, QThread, QThreadPool, pyqtSignal


class QWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, call: Callable, mutex: QMutex) -> None:
        """
        Init QWorker instance with function to call and mutex (thread lock handling)

        :param call: Function to call
        :param mutex: QMutex instance to handle thread locks
        """
        super().__init__()

        self.call = call
        self.mutex = mutex

    def run(self) -> None:
        """
        Run call function

        :return:
        """
        self.mutex.lock()
        self.call()
        self.mutex.unlock()

        self.finished.emit()


class AsyncQWorker(QThread):
    def __init__(
        self, call: Callable, mutex: QMutex, parent: Optional[QObject] = None
    ) -> None:
        """
        Init QWorker instance with function to call

        :param call: Function to call
        :param mutex: QMutex instance to handle thread locks
        :param parent: Parent QObject instance
        """
        super().__init__(parent)
        self.worker = QWorker(call, mutex)
        self.worker.moveToThread(self)
        # run worker when thread is started
        self.started.connect(self.worker.run)
        # quit thread when worker is finished
        self.worker.finished.connect(self.quit)


class TaskWorker(QRunnable):
    """
    TaskWorker class
    """

    finished = pyqtSignal()

    def __init__(self, call: Callable, task_id: int = 0) -> None:
        """
        Init TaskWorker instance

        :param call: Callable function
        :param task_id: ID number for task
        """
        super().__init__()
        self.call = call
        self.task_id = task_id
        self.setAutoDelete(True)

    def run(self):
        """
        Run call

        :return:
        """
        try:
            logging.debug(
                "Worker %s running in thread: %s", self.task_id, QThread.currentThread()
            )
            self.call()
        except Exception as e:
            logging.exception("Task %s  failed: %s", self.task_id, str(e))


class SimpleThreadPoolManager:
    """
    Simple Thread Pool Manager
    """

    def __init__(self, workers: List[TaskWorker]):
        """
        Init SimpleThreadPoolManager instance

        :param workers: List of Callable functions
        """
        self.workers = workers
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(len(self.workers))

    def start(self):
        """
        Start calls in parallel then wait for all call to end

        :return:
        """
        self.start_async()
        self.thread_pool.waitForDone()

    def start_async(self):
        """
        Start calls in parallel, but do not wait for the end

        :return:
        """
        for worker in self.workers:
            self.thread_pool.start(worker)
