This is not maintained -- It was a personal experiment, so please do not use in production!
=========
The basic idea is that you install this program on a machine that has a grader
(like 6.00x's xserver). Each edX Agent will be responsible for one grader type,
and will listen to as many queues as necessary. If you have multiple kinds of
things you want graded, you'd simply run two instances of this agent with
different config.

An agent has a fixed number of threads that will be configurable, so you always
have a fixed number of maximum concurrent requests. I used threads because it
was simple, and we're I/O bound, so CPU concurrency wasn't really an issue. I
did various tests using the SleepGrader and HTTPGrader and it gave the kind of
parallelism you'd expect.

The flow is simple. EdX Agent listens on a set of queues with worker threads.
When it gets a GraderRequest from the LMS, in instantiates a Grader that has
been specified in configuration. This Grader knows how to invoke whatever
underlying mechanism is necessary to evaluate the request (HTTP call to a local
server, subprocess call to a binary, etc.). The Grader gets the reply, makes a
GraderResponse out of it, and passes it back. The agent then takes that response
and sends it to a queue that some LMS worker will read from to update students'
scores.

To play with this:

1. Run a local web server
2. Start this agent: python edxagent.py
3. Run the simple request maker: python mockrequester.py

TODO List
---------
For internal use:

* Read from config files, and switch handlers based on them.
* Add handler methods for connection failure and re-init in ConsumerMixin
* Figure out what GraderRequest and GraderResult should have in them
* Heartbeats
* Finish the other leg of this and push the response back to another queue
* Create something that reads from that other queue and updates LMS db
* Actually implement the commandline interface
* Move logger setup
* Create the on_decode_error for our GradeRequestConsumer
* Implement command line Grader
* Use optional credentials for RabbitMQ
* Better debug tools
* Datadog integration
* QoS with multiple queues.
* Daemon threads can cause problems:
    http://joeshaw.org/2009/02/24/605/
  So we should switch to a more manual accounting:
    http://www.regexprn.com/2010/05/killing-multithreaded-python-programs.html
    http://notemagnet.blogspot.com/2009/10/writing-monitoring-threads-in-python.html

For external use:

* LMS query step where it has an API key and asks us what the RabbitMQ config
should be. Not necessary if everything's in house.
* Use daemon lib
