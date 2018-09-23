"""
Create example of BSD log file. Increasing/decreasing values of ranges can produce bigger/smaller file.
"""
RANGE_1 = 100
RANGE_2 = 500

FILE_PATH = 'test_small_b.log'

# log has no Alert or Emergency messages
log = b"""<47>Sep 22 15:38:21 mymachine myproc% fatal error, terminating!
<34>Jan 25 05:06:34 10.1.2.3 su: 'su root' failed for sprinkles on /dev/pts/8
<13>Oct  7 10:09:00 unicorn sched# invalid operation
<165>Aug  3 22:14:15 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 awesomeapp starting up version 3.0.1...
"""

# log2 has logs with Emergency severity and oldest message
log2 = b"""<0>Sep 22 15:38:21 mymachine myproc% fatal error, terminating!
<8>Jan  1 01:01:01 10.1.2.3 su: 'su root' failed for sprinkles on /dev/pts/8
<64>Oct  7 10:09:00 unicorn sched# invalid operation
<128>Aug  3 22:14:15 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 awesomeapp starting up version 3.0.1...
"""

with open(FILE_PATH, 'wb') as f:
    for i in range(RANGE_1):
        for j in range(RANGE_2):
            f.write(log)

    f.write(log2)   # Write some extreme time values and all logs with Emergency severity

    for i in range(RANGE_1):
        for j in range(RANGE_2):
            f.write(log)
        f.write(b"<33>Sep 21 22:22:22 monty_pythonhost99 Life of Brian\n")     # Alert severity

    # Newest message and Emergency severity
    f.write(b"<24>Dec 31 23:23:23 monty_python_host42 always look on the bride side of your life\n")

print('done')

