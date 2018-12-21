""" Image converter for CGM images.
"""

from typing import Dict
from typing import List

from queue import Empty as QueueEmpty
from multiprocessing import Queue
from multiprocessing import Process
from threading import Thread
import os
import sys
import time
import glob
import logging

import win32com.client
import pywintypes
import psutil

_log = logging.getLogger(__name__)

_FILES_PER_WORKER = 20


def _coolutils_worker(output_directory: str, output_extension: str,
                      images_priority: Queue, images: Queue):
    """ Initiate a CADConverter activex component and convert images in the
    supplied queues.

    This function will exit after _FILES_PER_WORKER conversions are done.

    :param output_directory: Where converted files will be saved.
    :param output_extension: Format of the output files (e.g. svg or png)
    :param images_priority: Images should be converted and are prioritized
    :param images: Images that should be converted
    """
    client = win32com.client.dynamic.Dispatch('CADConverter.CADConverterX')

    for _ in range(_FILES_PER_WORKER):
        try:
            input_file = images_priority.get_nowait()
        except QueueEmpty:
            input_file = images.get()

        if input_file is None:
            print('exiting')
            break

        filename, _ = os.path.splitext(os.path.basename(input_file))
        output_file = os.path.join(output_directory,
                                   '{}.{}'.format(filename, output_extension))

        _log.debug('Converting {} -> {}'.format(input_file, output_file))
        try:
            client.convert(input_file, output_file,
                           '-c {}'.format(output_extension.upper()))
            pass
        except pywintypes.com_error:
            _log.exception('Exception occurred during conversion')
            images.put(input_file)
            break
        time.sleep(0.25)  # Prevent process from consuming all CPU time
    sys.exit(0)


class CGMImageConverter(Thread):
    """ Uses CoolUtils CADConverterX activex component to convert CGM images to
    more popular image formats.
    """
    def __init__(self, input_directory: str, output_directory: str,
                 worker_count: int=3, skip_existing: bool=True,
                 output_extension: str='svg'):
        """ Create a new CGM image converter thread.

        Notes:
         * Files not ending with .cgm will be ignored
         * The input_directory is NOT processed recursively

        :param input_directory: Directory that contains CGM images that should
        be converted.
        :param output_directory: Where converted files will be saved.
        :param worker_count: How many processes that should be spawned
        simultaneously to speed up conversion.
        :param skip_existing: Skip conversion of files found in
        output_directory.
        :param output_extension: Format of the output files (e.g. svg or png).
        """
        super().__init__()
        self._running = True

        self._input_directory = input_directory
        self._output_directory = output_directory
        self._worker_count = worker_count
        self._output_extension = output_extension

        self._workers = []  # type: List[Process]
        self._image_queue_priority = Queue()
        self._image_queue = Queue()
        self._images = {}  # type: Dict[str, str]
        self._total_image_count = 0

        for file in glob.glob(os.path.join(input_directory, '*.cgm')):
            if skip_existing:
                name, _ = os.path.splitext(os.path.basename(file))
                o = os.path.join(output_directory,
                                 '{}.{}'.format(name, output_extension))

                if os.path.isfile(o):
                    _log.debug('Skipping {}'.format(file))
                    continue

            _log.debug('Adding {} to queue'.format(file))
            self._add_item(file)
            self._total_image_count += 1

    def prioritize(self, filename: str):
        """ Prioritize the conversion of an image.

        :param filename: Name of the image to prioritize.
        """
        # TODO Not deleting job from self._image_queue
        name, _ = os.path.splitext(os.path.basename(filename))
        file = self._images[name]
        self._image_queue_priority.put(file)

    def graceful_stop(self):
        """ Stop the thread and its sub-processes gracefully.
        """
        self._running = False

    def get_progress(self):
        return 1 - (self._image_queue.qsize() / self._total_image_count)

    def is_done(self):
        return self._image_queue.empty()

    def run(self):
        while self._running:
            self._workers = [w for w in self._workers if w.is_alive()]

            for _ in range(self._worker_count - len(self._workers)):
                self._dispatch_worker()
            time.sleep(1)

        _log.debug('Stopping thread')
        for _ in range(self._worker_count):
            self._image_queue_priority.put(None)
            print('put')

        _log.debug('Emptying queue')
        # The program will (apparently) not exit if the queue is not empty
        try:
            while True:
                self._image_queue.get_nowait()
        except QueueEmpty:
            pass

        _log.debug('Waiting for workers')
        for worker in self._workers:
            worker.join()

    def _add_item(self, filename: str):
        """ Add a new file that should be converted.

        :param filename: File that should be converted.
        """
        name, _ = os.path.splitext(os.path.basename(filename))

        self._image_queue.put(filename)
        self._images[name] = filename

    def _dispatch_worker(self):
        """ Create a new worker process and start it immediately.
        """
        _log.debug('Starting new worker process')
        worker = Process(target=_coolutils_worker,
                         args=(self._output_directory, self._output_extension,
                               self._image_queue_priority, self._image_queue))
        p = psutil.Process(worker.pid)
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

        self._workers.append(worker)
        worker.start()
