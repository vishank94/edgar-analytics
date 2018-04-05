# Table of Contents
1. [Introduction](README.md#introduction)
2. [Approach](README.md#approach)
3. [Dependencies](README.md#dependencies)
4. [Running the Code](README.md#running-the-code)
5. [Assumptions](README.md#assumptions)
6. [Directory Structure](README.md#directory-structure)


# Introduction

This repository contains solution to coding challenge edgar-analytics.


# Approach

1. For the purpose of data streaming, the input data is read line-by-line.
2. Each input data stream is appended with a DateTime column which is a combination of the date and time columns.
3. The solution is setup using:
(a) a queue which stores (user_ip,last_request_time) tuple.
(b) a hashmap which stores [first_request_time, number_of_requests] list against user_ip key.
4. Here, a double-ended queue is implemented as a queue for ease of access to deque attributes like peek(). 
5. Both the queue and the hashmap have unique entries for each active user session i.e. only one entry for each user_ip.
6. Each time a stream is read, it is directed to the manager function that decides where to redirect the stream- process_curr() or close_sessions().
7. The process_curr() checks for: 
(a) any existing user sessions that might have gotten expired at the current stream time and it removes it both from the queue and the hashmap.
(b) adds the current stream to the queue and the hashmap for a new user_ip; or updates user_ip’s last request time in the queue and increment the number of requests against that user_ip in the hashmap for an existing user_ip.
8. The close_sessions() is called only when the end-of-file is reached. It does the following:
(a) sorts the user sessions in chronological order of their first request times since the user session started first, ends first.
(b) empties the queue and the hashmap by closing all user sessions and prints to file.
9. Each time the duration of user session is calculated, the string Datetime value is converted to datetime format.
10. The user session is terminated either when end-of-file is reached or when current stream time - user’s last_request_time (stored in the queue) > inactivity_period.
11. To calculate time difference for session duration and when checking for session expiration:
(a) return the difference in the time values in seconds if both belong to the same day or are within 24 hours gap for different days.
(b) return the difference in the time values in seconds added with (86400 multiplied with the difference in their date values) if they both belong to different days.
12. Whenever user session ends- (the user_ip, first_time_request, last_time_request, duration of session, number of requests) in that session is printed to file.
13. The user session duration is calculated using (last_time_request-first_time_request+1).
14. Finally, all this the is orchestrated under analytics() that takes care of streaming as well.




# Dependencies
Python libraries: csv, datetime, collections- deque



# Running the Code
1. Python file sessionization.py needs to be run.
2. The input and output files' path is defined in main() and analytics() methods.
3. The repository directory structure given below must be maintained for the code to run successfully.


# Assumptions
1. IP addresses with dissimilar obfuscated fourth octet will refer to the different IP addresses. Example- 101.81.133.fja and 101.81.133.ffa are two different IPs.
2. IP addresses with same obfuscated fourth octet will refer to the same IP addresses. Example- 101.81.133.ffa and 101.81.133.ffa are the same IPs.
3. The date and time of the data streaming in would obey chronological ordering.


# Directory structure
The directory structure for my repo is as follows:

    ├── README.md 
    ├── run.sh
    ├── src
    │   └── sessionization.py
    ├── input
    │   └── inactivity_period.txt
    │   └── log.csv
    ├── output
    |   └── sessionization.txt
    ├── insight_testsuite
        └── run_tests.sh
        └── tests
            └── test_1
            |   ├── input
            |   │   └── inactivity_period.txt
            |   │   └── log.csv
            |   |__ output
            |   │   └── sessionization.txt
            ├── test_DiffDateSession
            |   ├── input
            |   │   └── inactivity_period.txt
            |   │   └── log.csv
            |   │── output
            |   │   └── sessionization.txt
		├── test_DuplicateRequests
            |   ├── input
            |   │   └── inactivity_period.txt
            |   │   └── log.csv
            |   │── output
            |   │   └── sessionization.txt
		├── test_HighInactivityPeriod
            |   ├── input
            |   │   └── inactivity_period.txt
		|   │   └── log.csv
            |   │── output
            |   │   └── sessionization.txt
		├── test_NextDayContinued
            |   ├── input
            |   │   └── inactivity_period.txt
		|   │   └── log.csv
            |   │── output
            |   │   └── sessionization.txt
		├── test_OneSecondSessions
            |   ├── input
            |   │   └── inactivity_period.txt
		|   │   └── log.csv
            |   │── output
            |   │   └── sessionization.txt
		├── test_UserSessionSplit
                ├── input
                │   └── inactivity_period.txt
		    │   └── log.csv
                │── output
                    └── sessionization.txt
