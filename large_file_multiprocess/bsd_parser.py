from collections import namedtuple
from datetime import datetime
from itertools import islice


# probably a little slower alternative to namedtuple is to write class
BSDLog = namedtuple('BSDLog', 'facility severity time host message')


def bsd_parser(line):
    # From task specification:
    # You can assume that every message adheres to the standard and all the messages
    # come from the same year.
    # WRITE WHAT YOU DO NOT NEED TO WRITE

    iline = iter(line)

    next(iline)     # skipp first character '<'
    p = []
    while True:
        c = chr(next(iline))    # only for readability, should be compare with byte number
        if c == '>':
            break
        p.append(c)
    pri = int(''.join(p))
    facility, severity = divmod(pri, 8)

    # The TIMESTAMP will immediately follow the trailing ">" from the PRI
    time = [str(datetime.today().year), ' ']
    for _ in range(15):
        time.append(chr(next(iline)))
    # print(''.join(time))
    time = datetime.strptime(''.join(time), '%Y %b %d %H:%M:%S')

    # Single space characters MUST follow each of the TIMESTAMP
    next(iline)
    host = []
    while True:
        c = chr(next(iline))
        if c == ' ':    # Single space characters MUST follow each of the HOSTNAME
            break
        host.append(c)
    host = ''.join(host)

    message = []
    for c in iline:     # Exhaust iterator
        message.append(chr(c))
    message = ''.join(message)

    return BSDLog(facility, severity, time, host, message)


if __name__ == '__main__':
    b = b'<13>Sep 22 15:38:21 mymachine myproc% fatal error, terminating!'

    p = bsd_parser(b)

    print(p.facility)
    print(p.severity)
    print(p.time)
    print(p.host)
    print(p.message)

