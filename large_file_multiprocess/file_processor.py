import os
import sys

from itertools import islice
from multiprocessing import current_process, Pool, cpu_count
from timeit import default_timer as timer
from pprint import pprint as pp

from bsd_parser import bsd_parser as bsd
from tasks import *


class FileProcessor:
    """
    Class for multiprocessing large file without splitting it

    Args:
        file_path: Path to the file.
        tasks: Lists of tasks which process 'message'

        file_mode: 'b' for reading file in binary mode, otherwise read in string mode
        num_of_process: Number of processes, default number of local machine
        chunk_size: Size of chunk (number of lines in file)
        parser: Parser for parsing each line, default bsd_parser

    Raises:
        TypeError: If element of task is not subclass of class Task

    """

    def __init__(self, file_path, tasks, *, file_mode='rb', num_of_process=None, chunk_size=None, parser=None):
        self._file_path = file_path

        for t in tasks:
            if issubclass(t, Task):
                raise TypeError("Element of task '{t}' must be subclass of Task class".format(t))
        self._tasks = tasks

        self._mode = 'rb' if file_mode == 'rb' else 'r'
        self._num_of_process = num_of_process or cpu_count()
        self._chunk_size = chunk_size or 100*1024
        # self._chunk_size = os.path.getsize(self._file_path) / self._num_of_process # some arithmetic can be done here
        self._bsd_parser = parser or bsd

        self.total_processing_time = None
        self.results = None

    def chunks_position_generator(self):
        """
        Generate start and end line position of chunk for file.

        Raises:
            IOError: If 'filename' does not exist or can't be read.

        Yields:
            tuple(int, int): Chunk start and end position.

        """
        with open(self._file_path, self._mode) as f:
            start = 0
            isl = islice(f, start, sys.maxsize, self._chunk_size)
            end = self._chunk_size
            while True:
                try:
                    next(isl)
                except StopIteration:   # end of file
                    return

                yield start, end
                start = end
                end += self._chunk_size

    def process(self, chunk):
        """
        Processing messages in chunk using task class:
            -

        Args:
            chunk: Tuple where first element is start position and second element is end position of chunk.

        Raises:
            IOError: If 'filename' does not exist or can't be read.

        """
        chunk_start, chunk_end = chunk

        # print('Processed by PID: ', current_process().pid)

        with open(self._file_path, self._mode) as f:
            ichunk = islice(f, chunk_start, chunk_end)

            # creating list of task instances independent for each process
            tasks_instances = [TC() for TC in self._tasks]

            for line in ichunk:
                if self._mode != 'rb':
                    line = bytes(line, 'utf-8')
                message = self._bsd_parser(line)
                for t in tasks_instances:
                    t(message)  # processing message for each task

            return {t.__class__: t for t in tasks_instances}

    def run(self):
        """
        Run processes from pool of processes and aggregate results.
        """
        pp(list(self.chunks_position_generator()).__len__())

        st = timer()
        with Pool(self._num_of_process) as p:
            per_process_results = p.map(self.process, list(self.chunks_position_generator()))

        # Transpose per_process_results from list of dictionaries with different tasks objects
        # [{'Task1': <tasks.Task1 object at ...>, 'Task2': <tasks.Task2 object at ...> },
        #  {'Task1': <tasks.Task1 object at ...>, 'Task2': <tasks.Task2 object at ...>}, ...]
        # To dictionary of lists of homogeneous tasks
        # {'Task1': [<tasks.Task1 object at ...>, <tasks.Task1 object at ...>, ...],
        #  'Task2': [<tasks.Task2 object at ...>, <tasks.Task2 object at ...>, ...], ...}
        per_task_results = {k: [dic[k] for dic in per_process_results] for k in per_process_results[0]}
        # pp(per_process_results)   #   Uncomment this two lines
        # pp(per_task_results)      #   to see structure before and after transposition

        et = timer()
        self.total_processing_time = et - st

        # Aggregate results of each individual chunk (each process) for each task
        # t1_results = Task1.aggregate(per_task_results[Task1])
        # t2_results = Task2.aggregate(per_task_results[Task2])
        # t3_results = Task3.aggregate(per_task_results[Task3])
        self.results = {task_class.__name__: task_class.aggregate(per_task_results[task_class])
                        for task_class in per_task_results.keys()}

if __name__ == '__main__':
    FILE_PATH = 'helpers/test_small_b.log'

    tasks = [Task1, Task2, Task3]
    fp = FileProcessor(FILE_PATH, tasks)
    fp.run()

    print('*********************************************************************')
    print('*********** Average length of the MSG part of the messages **********')
    print('*********************************************************************')
    print('Globally average is {0:.3f}'.format(fp.results['Task1'].total_average))
    pp('Per host average: ')
    for k, v in fp.results['Task1'].per_host.items():
        print('\t\t {0} = {1}'.format(k, v))
    print('*********************************************************************\n\n')

    print('*********************************************************************')
    print('**** Total number of Emergency and Alert severity level messages ****')
    print('*********************************************************************')
    print('Globally number of Emergency {0}'.format(fp.results['Task2'].total_emergency))
    print('Globally number of Alert {0}'.format(fp.results['Task2'].total_alert))
    print('Per host Emergency: ')
    for k, v in fp.results['Task2'].per_host['emergency'].items():
        print('\t\t {0} = {1}'.format(k, v))
    print('Per host Alert: ')
    for k, v in fp.results['Task2'].per_host['alert'].items():
        print('\t\t {0} = {1}'.format(k, v))
    print('*********************************************************************\n\n')

    print('*********************************************************************')
    print('************ Timestamp of the oldest and newest message *************')
    print('*********************************************************************')
    print('Globally oldest message is from: {0}'.format(fp.results['Task3'].oldest.strftime('%b %d %H:%M:%S')))
    print('Globally newest message is from: {0}'.format(fp.results['Task3'].newest.strftime('%b %d %H:%M:%S')))
    print('Per host oldest: ')
    for k, v in fp.results['Task3'].per_host['oldest'].items():
        print('\t\t {0} = {1}'.format(k, v.strftime('%b %d %H:%M:%S')))
    print('Per host oldest: ')
    for k, v in fp.results['Task3'].per_host['newest'].items():
        print('\t\t {0} = {1}'.format(k, v.strftime('%b %d %H:%M:%S')))
    print('*********************************************************************\n\n')

    print('*********************************************************************')
    print('EXECUTION TIME [s]: {0}'.format(fp.total_processing_time))
    print('*********************************************************************')
