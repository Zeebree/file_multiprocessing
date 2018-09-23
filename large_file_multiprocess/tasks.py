import abc
from collections import defaultdict, Counter, namedtuple
from functools import reduce
from pprint import pprint as pp

Task1Results = namedtuple('Task1Results', 'total_average per_host')
Task2Results = namedtuple('Task2Results', 'total_emergency total_alert per_host')
Task3Results = namedtuple('Task3Results', 'oldest newest per_host')


class Task(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def process(self, message):
        pass

    @abc.abstractmethod
    def get_state(self):
        pass

    @abc.abstractclassmethod
    def aggregate(self, task_objects):
        pass

    @abc.abstractmethod
    def __call__(self, message):
        pass


class Task1:
    """
    Task for global and per host processing the average length of the MSG part of the messages
    """

    def __init__(self):
        self.lines_per_host = defaultdict(int)
        self.length_per_host = defaultdict(int)
        # self.data = dict()      # {'host': {'lines': int, 'total_length: int}}  messy way :)

    def process(self, message):
        """
        Per host message processing for counting lines and summing lengths of MSG part of BSD.

        Args:
            message: Message in BSD format

        """
        self.lines_per_host[message.host] += 1
        self.length_per_host[message.host] += len(message.message)

    def get_state(self):
        return dict(self.lines_per_host), dict(self.length_per_host)

    @classmethod
    def aggregate(cls, task_objects):
        """
        Aggregate lists of tasks objects. Use it for summing processing results of different processes.

        Raises:
            TypeError: If task object is not type of Task

        Returns:
            Task1Results(float, dict): Return namedtuple with total average and per host average
        """

        for t in task_objects:
            if isinstance(t, Task):
                raise TypeError('Object must be subtype of Task')

        per_hosts_lines = dict(reduce(lambda x, y: x + y,
                                      map(Counter, [task.get_state()[0] for task in task_objects])))
        per_hosts_lengths = dict(reduce(lambda x, y: x + y,
                                        map(Counter, [task.get_state()[1] for task in task_objects])))

        print(sum(per_hosts_lines.values()))
        total_average = sum(per_hosts_lengths.values()) / sum(per_hosts_lines.values())
        per_host_averages = {k: per_hosts_lengths[k]/per_hosts_lines[k]
                             for k in per_hosts_lines.keys()}

        return Task1Results(total_average, per_host_averages)

    def __call__(self, message):
        self.process(message)


class Task2:
    """
    Task for global and per host processing the total number of Emergency and Alert severity level messages

    Numerical         Severity
          Code
           0       Emergency: system is unusable
           1       Alert: action must be taken immediately
           2       Critical: critical conditions
           3       Error: error conditions
           4       Warning: warning conditions
           5       Notice: normal but significant condition
           6       Informational: informational messages
           7       Debug: debug-level messages
    """
    def __init__(self):
        self.emergency = defaultdict(int)
        self.alert = defaultdict(int)

    def process(self, message):
        """
        Per host message processing for counting Emergency and Alert messages.

        Args:
            message: Message in BSD format

        """
        if message.severity == 0:
            self.emergency[message.host] += 1
        if message.severity == 1:
            self.alert[message.host] += 1

    def get_state(self):
        return self.emergency, self.alert

    @classmethod
    def aggregate(cls, task_objects):
        """
        Aggregate lists of tasks objects. Use it for summing processing results of different processes.

        Raises:
            TypeError: If task object is not type of Task

        Returns:
            Task2Results(int, int, dict): Return namedtuple with total counts and per host counts of emergency and alert
        """

        for t in task_objects:
            if isinstance(t, Task):
                raise TypeError('Object must be subtype of Task')

        per_host_emergency = dict(reduce(lambda x, y: x + y,
                                         map(Counter, [task.get_state()[0] for task in task_objects])))
        per_host_alert = dict(reduce(lambda x, y: x + y,
                                     map(Counter, [task.get_state()[1] for task in task_objects])))

        return Task2Results(sum(per_host_emergency.values()), sum(per_host_alert.values()),
                            {'emergency': per_host_emergency,
                             'alert': per_host_alert})

    def __call__(self, message):
        self.process(message)


class Task3:
    """
    Task for global and per host processing for timestamp of the oldest and newest message
    """
    def __init__(self):
        self.oldest = dict()
        self.newest = dict()

    def process(self, message):
        """
        Per host message processing for oldest and newest message.

        Args:
            message: Message in BSD format

        """
        if message.host in self.oldest:
            if message.time > self.newest[message.host]:
                self.newest[message.host] = message.time
            if message.time < self.oldest[message.host]:
                self.oldest[message.host] = message.time

        else:   # If not in dicts already, add it. Time is the same for both oldest and newest
            self.oldest[message.host] = message.time
            self.newest[message.host] = message.time

    def get_state(self):
        return self.oldest, self.newest

    @classmethod
    def aggregate(cls, task_objects):
        """
        Aggregate lists of tasks objects. Use it for summing processing results of different processes.

        Raises:
            TypeError: If task object is not type of Task

        Returns:
            Task3Results(int, int, dict): Return namedtuple with oldest, newest and per_host
        """

        for t in task_objects:
            if isinstance(t, Task):
                raise TypeError('Object must be subtype of Task')
        oldest = [task.get_state()[0] for task in task_objects]
        newest = [task.get_state()[1] for task in task_objects]

        # Transpose list of dict [{'host1': h1t1, 'host2': h2t1, ...}, ...]
        # to dict of hosts {'host1': [h1t1, h1t2,...], ...}
        transposed_oldest = {k: [dic[k] for dic in oldest] for k in oldest[0]}
        transposed_newest = {k: [dic[k] for dic in newest] for k in newest[0]}

        per_host_oldest = {k: min(v) for k, v in transposed_oldest.items()}
        per_host_newest = {k: max(v) for k, v in transposed_newest.items()}

        # pp(per_host_oldest)
        # pp(per_host_newest)

        return Task3Results(min(per_host_oldest.values()), max(per_host_newest.values()),
                            {'oldest': per_host_oldest,
                             'newest': per_host_newest})

    def __call__(self, message):
        self.process(message)
