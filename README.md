# General approach:

Top constraint: Input file may be very large (dozens of gigabytes) >> Conclusion: File cannot be read in memory (memory overflow will be occurred)


## IMPLEMENTED SOLUTION: Slice through large file chunk by chunk. 


### 'file_processor.py and FileProcessor class"
General algorithms: 
1. Split file into chunks
2. Process each chunk with separate process from pool.
		- Each chunk is processed line by line from start line to end line of chunk
		- Line is parsed using 'bsd_parser(line) function which return namedtuple 
		- Return statistics for chunk
3. Aggregate results returned from process
	
Note: I decide to create class 'FileProcessor' which receive 'file_path' and 'tasks' as list of tasks as mandatory parameters. I choose this way, so I can easily extend application with new statistics without changing anything in 'FileProcessor' class. Just create new task class and add it to list of tasks. Another win using this way is only one traversing through file and only one parsing (using 'bsd_parser') of log line for all tasks from list. 
	
'FileProcessor' can also receive parameters intended for configuration of processing. It is possible to configure mode of reading, number of processes spawned by pool, chunk size, override parser with some another...
	

### 'bsd_parser.py and bsd_parser function": 
When I design this function, I use documentation from https://tools.ietf.org/html/rfc3164 and use assumption from specification "every message adheres to the standard and all the messages come from the same year". I create straight forward parsing function. I choose to iterate through passed line and extract information in namedtuple "BSDLog(facility, severity, time, host, message)".
This function satisfies requirements from specification, but for real production it should be rewritten to satisfy all things from documentation (bad inputs, formats, max length, tags). It can be rewritten in class and separate on methods for each piece of work (PRI, HEADER, MSG) for example.
	
	
### 'task.py and tasks class": 
As I mentioned earlier, I encapsulate each task. To ensure some code robustness I introduce abstract class 'Task' '__call__' method for easier manipulation. 
Each task satisfies one requirement from specification.


### 'helpers/crate_data.py and test log files'
I decide to write this log generator based on lines of logs from specification. Additionally I include two log files for testing. If you run as main 'file_processor.py', results for file 'helpers/test_small_b.log' will be printed.



### Additional details without special order or importance:
- I leave comments in code on places where I think it is good for it.
- Another potential solution: Split large file into small files and run multiprocessing on them.
- namedtuple is used because of simpler retrieving and IDE recognized it, you do not need to remember names :) e.g. message.host

### Improvements for future:
- Unittests - I didn't write it, but if you need them I will gladly write them.
- BSD log parser - as mentioned earlier. Additionally: this is one of performance bottlenecks of application.
- App can be packed for command line execution (eg. >>python file_processor file.log --chunk_size=100000 --process=4) or for importing
- Results from chunks can be aggregated in parallel with processing (probably small improvements, depends on number of chunks)
- Results stored in 'self.results' from 'FileProcessor' class are pretty messy. 


EXAMPLE OF RESULTS:

*********************************************************************
*********** Average length of the MSG part of the messages **********
*********************************************************************
Globally average is 36.994
'Per host average: '
		 mymachine = 34.0
		 10.1.2.3 = 49.0
		 unicorn = 25.0
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 40.0
		 monty_pythonhost99 = 14.0
		 monty_python_host42 = 43.0
*********************************************************************


*********************************************************************
**** Total number of Emergency and Alert severity level messages ****
*********************************************************************
Globally number of Emergency 5
Globally number of Alert 100
Per host Emergency: 
		 mymachine = 1
		 10.1.2.3 = 1
		 unicorn = 1
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 1
		 monty_python_host42 = 1
Per host Alert: 
		 monty_pythonhost99 = 100
*********************************************************************


*********************************************************************
************ Timestamp of the oldest and newest message *************
*********************************************************************
Globally oldest message is from: Jan 01 01:01:01
Globally newest message is from: Oct 07 10:09:00
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 10.1.2.3 = Jan 01 01:01:01
		 unicorn = Oct 07 10:09:00
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 10.1.2.3 = Jan 25 05:06:34
		 unicorn = Oct 07 10:09:00
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
*********************************************************************


*********************************************************************
EXECUTION TIME [s]: 7.113764300000001
*********************************************************************
