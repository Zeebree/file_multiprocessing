
# General approach:  
  
Top constraint: Input file may be very large (dozens of gigabytes) >> Conclusion: File cannot be read in memory (memory overflow would occur)  
  
  
## IMPLEMENTED SOLUTION: Slice through large file chunk by chunk.   
  
  
### 'file_processor.py and FileProcessor class"  
General algorithms:   
1. Split file into chunks  
2. Process each chunk with separate process from pool.  
      - Each chunk is processed line by line from start to end  
      - Line is parsed using 'bsd_parser(line) function which returns namedtuple   
      - Return statistics for chunk  
3. Aggregate results returned from process  
     
Class 'FileProcessor' receives 'file_path' and 'tasks' as mandatory parameters. I choose this way, so application can be easily extend with new statistics without changing 'FileProcessor' class: just create new task class and add it to list of tasks. Another win using this way is only one traversing through file and only one parsing (using 'bsd_parser') of log line for all tasks from list.   
     
'FileProcessor' can also receive parameters intended for configuration of processing. It is possible to configure mode of reading, number of processes spawned by pool, chunk size, override parser with some another...  
     
  
### 'bsd_parser.py and bsd_parser function":   
When I designed this function, I used documentation from https://tools.ietf.org/html/rfc3164 and assumption from specification "every message adheres to the standard and all the messages come from the same year". I created straight forward parsing function. I choose to iterate through passed line and extract information in namedtuple "BSDLog(facility, severity, time, host, message)".  
This function satisfies requirements from specification, but for real production it should be refactored to handle bad inputs, max length, tags... It can be written as a class and where parsing can be separated on methods for each piece of work (PRI, HEADER, MSG) for example.  
     
     
### 'task.py and tasks class":   
As I mentioned earlier, I encapsulated each task. To ensure some code robustness I introduced abstract class 'Task' '__call__' method for easier manipulation.   
Each task satisfies one requirement from specification.  
  
  
### 'helpers/crate_data.py and test log files'  
I decided to write this log generator based on lines of logs from specification. I included two log files for testing. If you run 'file_processor.py' as main program, results for file 'helpers/test_small_b.log' will be printed.  
  
  
  
### Additional details:  
- I left comments in code to additionally explain some sections.  


### Improvements for future:  
- Unit tests
- BSD log parser should be refactored to handle bad inputs, max length, tags... . Additionally, this is one of performance bottlenecks of application, so it is worth to explore possibilities for  its optimization.  
- Application can be packed for command line execution (eg. >>python file_processor file.log --chunk_size=100000 --process=4).
- Results from chunks can be aggregated in parallel with processing (probably small improvements, depends on number of chunks)  
- Getting results stored in 'self.results' from 'FileProcessor' class can be simplified for use, by introducing some properties.   
  
### Performance results summary:  
I run app on logs of different size:  
 - Processing 28.2MB (400 thousands of lines) file takes about 6.5 seconds , 4 process
 - Processing 282MB (4 million of lines) file takes about 65 seconds, 4 process  
 - Processing 282MB (4 million of lines) file takes about 209 seconds, 1 process  
 - Processing 2.82GB (40 millions of lines) file takes about 708 seconds, 4 process 
 - Processing 11GB  (160 millions of lines) file takes about 3179 seconds, 4 process    
 
 Environment:
 - Python 3.6.5 (v3.6.5:f59c0932b4, Mar 28 2018, 16:07:46) [MSC v.1900 32 bit (Intel)] on win32
 - CPU i5-3570 from 2011
 - RAM 8GB
 - Win10
  
### Additional approaches
- Another potential solution: split large file into small files and run multiprocessing on them. 
- Specialize some process for handling IO bound operations handling and some others for handling CPU bound operations. 
  
  
## EXAMPLE OF RESULTS:  
  
### Processing 28.2MB (400105 lines) file takes about 6.5 seconds, 4 process  
 ```
*********************************************************************
*********** Average length of the MSG part of the messages **********
*********************************************************************
Globally average is 36.994
'Per host average: '
		 monty_pythonhost99 = 14.0
		 monty_python_host42 = 43.0
		 10.1.2.3 = 49.0
		 unicorn = 25.0
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 40.0
		 mymachine = 34.0
*********************************************************************


*********************************************************************
**** Total number of Emergency and Alert severity level messages ****
*********************************************************************
Globally number of Emergency 5
Globally number of Alert 100
Per host Emergency: 
		 unicorn = 1
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 1
		 monty_python_host42 = 1
		 mymachine = 1
		 10.1.2.3 = 1
Per host Alert: 
		 monty_pythonhost99 = 100
*********************************************************************


*********************************************************************
************ Timestamp of the oldest and newest message *************
*********************************************************************
Globally oldest message is from: Jan 01 01:01:01
Globally newest message is from: Dec 31 23:23:23
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 01 01:01:01
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 25 05:06:34
*********************************************************************


*********************************************************************
EXECUTION TIME [s]: 6.5471564
*********************************************************************
```

### Processing 282MB (4000105 lines) file takes about 65 seconds, 4 process  
```
*********************************************************************
*********** Average length of the MSG part of the messages **********
*********************************************************************
Globally average is 36.999
'Per host average: '
		 unicorn = 25.0
		 monty_python_host42 = 43.0
		 10.1.2.3 = 49.0
		 mymachine = 34.0
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 40.0
		 monty_pythonhost99 = 14.0
*********************************************************************


*********************************************************************
**** Total number of Emergency and Alert severity level messages ****
*********************************************************************
Globally number of Emergency 5
Globally number of Alert 100
Per host Emergency: 
		 unicorn = 1
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 1
		 monty_python_host42 = 1
		 10.1.2.3 = 1
		 mymachine = 1
Per host Alert: 
		 monty_pythonhost99 = 100
*********************************************************************


*********************************************************************
************ Timestamp of the oldest and newest message *************
*********************************************************************
Globally oldest message is from: Jan 01 01:01:01
Globally newest message is from: Dec 31 23:23:23
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 01 01:01:01
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 25 05:06:34
*********************************************************************


*********************************************************************
EXECUTION TIME [s]: 64.0536369
*********************************************************************
```

### Processing 282MB (4000105 lines) file takes about 209 seconds, 1 process 
```
*********************************************************************
*********** Average length of the MSG part of the messages **********
*********************************************************************
Globally average is 36.999
'Per host average: '
		 monty_pythonhost99 = 14.0
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 40.0
		 monty_python_host42 = 43.0
		 mymachine = 34.0
		 unicorn = 25.0
		 10.1.2.3 = 49.0
*********************************************************************


*********************************************************************
**** Total number of Emergency and Alert severity level messages ****
*********************************************************************
Globally number of Emergency 5
Globally number of Alert 100
Per host Emergency: 
		 unicorn = 1
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 1
		 monty_python_host42 = 1
		 10.1.2.3 = 1
		 mymachine = 1
Per host Alert: 
		 monty_pythonhost99 = 100
*********************************************************************


*********************************************************************
************ Timestamp of the oldest and newest message *************
*********************************************************************
Globally oldest message is from: Jan 01 01:01:01
Globally newest message is from: Dec 31 23:23:23
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 01 01:01:01
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 25 05:06:34
*********************************************************************


*********************************************************************
EXECUTION TIME [s]: 209.75309439999998
*********************************************************************
```
 
### Processing 2.82GB (40001005 lines) file takes about 594 seconds, 4 process 
```
*********************************************************************
*********** Average length of the MSG part of the messages **********
*********************************************************************
Globally average is 36.999
'Per host average: '
		 monty_pythonhost99 = 14.0
		 mymachine = 34.0
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 40.0
		 unicorn = 25.0
		 10.1.2.3 = 49.0
		 monty_python_host42 = 43.0
*********************************************************************


*********************************************************************
**** Total number of Emergency and Alert severity level messages ****
*********************************************************************
Globally number of Emergency 5
Globally number of Alert 1000
Per host Emergency: 
		 unicorn = 1
		 10.1.2.3 = 1
		 monty_python_host42 = 1
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 1
		 mymachine = 1
Per host Alert: 
		 monty_pythonhost99 = 1000
*********************************************************************


*********************************************************************
************ Timestamp of the oldest and newest message *************
*********************************************************************
Globally oldest message is from: Jan 01 01:01:01
Globally newest message is from: Dec 31 23:23:23
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 01 01:01:01
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 25 05:06:34
*********************************************************************


*********************************************************************
EXECUTION TIME [s]: 594.6569814
*********************************************************************
```

### Processing 11GB  (160 millions of lines) file takes about 3179 seconds, 4 process  
```
*********************************************************************
*********** Average length of the MSG part of the messages **********
*********************************************************************
Globally average is 36.999
'Per host average: '
		 mymachine = 34.0
		 monty_python_host42 = 43.0
		 monty_pythonhost99 = 14.0
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 40.0
		 unicorn = 25.0
		 10.1.2.3 = 49.0
*********************************************************************


*********************************************************************
**** Total number of Emergency and Alert severity level messages ****
*********************************************************************
Globally number of Emergency 5
Globally number of Alert 4000
Per host Emergency: 
		 10.1.2.3 = 1
		 mymachine = 1
		 monty_python_host42 = 1
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = 1
		 unicorn = 1
Per host Alert: 
		 monty_pythonhost99 = 4000
*********************************************************************


*********************************************************************
************ Timestamp of the oldest and newest message *************
*********************************************************************
Globally oldest message is from: Jan 01 01:01:01
Globally newest message is from: Dec 31 23:23:23
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 01 01:01:01
Per host oldest: 
		 mymachine = Sep 22 15:38:21
		 FEDC:BA98:7654:3210:FEDC:BA98:7654:3210 = Aug 03 22:14:15
		 monty_python_host42 = Dec 31 23:23:23
		 monty_pythonhost99 = Sep 21 22:22:22
		 unicorn = Oct 07 10:09:00
		 10.1.2.3 = Jan 25 05:06:34
*********************************************************************


*********************************************************************
EXECUTION TIME [s]: 3179.4857226
*********************************************************************
```