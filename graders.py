"""
The functionality of what's doing the actual grading is a black box to us, but
we know we can invoke them in different ways, such as HTTP or a commandline 
call. This module provides those abstractions for the edxagent.
"""
import abc
import logging
import random
import time
from collections import namedtuple

import requests
from requests.exceptions import ConnectionError, Timeout

log = logging.getLogger('edxagent.graders')

# TODO: Flesh these out
GraderRequest = namedtuple('GraderRequest', 'data')
GraderResponse = namedtuple('GraderResult', 'data success')


class Grader(object):
    """
    Interface to a type of Grader (HTTP, command-line, something more complex).
    Grader objects have the following responsibilities:

    1. Create a configured instance of themselves via from_config().
    2. Accept GraderRequest objects in grade(), invoke the underlying grading
       mechanism, and return a GraderResponse. Graders must handle all 
       serialization/deserialization necessary for this.
    3. We have to load the problem from somewhere. 
    4. Don't worry about multi-threading. In fact, we *should* block, or else
       edxagent will just pummel our server with as many requests as we can
       handle, and we want to explicitly shield from that.

    Your Grader should *NOT*:

    1. Do async operations (or rate limiting will be thrown off)
    2. Do anything computationally expensive.
    3. Do anything application specific.
    4. Do anything particularly complicated.

    Grader objects exist only to pass on requests to the smart things that
    actually understand how to do the real work of evaluating the problem and
    the student's solution. We want to keep it as small and simple as possible.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def grade(self, grader_request):
        """Given a GraderRequest object, return a GradeResult."""
        pass

    @classmethod
    def from_config(cls, **config):
        """Return a fully configured instance of this Grader based on the 
        config dictionary passed in."""
        raise NotImplementedError


class HTTPGrader(Grader):
    # TODO: Timeouts

    def __init__(self, url):
        self.url = url

    def grade(self, grade_request):
        # TODO: What do we do with a 500 error -- throw an exception?
        #       Make a GraderResponse that represents it?
        try:
            r = requests.post(self.url, data=grade_request.data)
            reply_data = r.json()
        except ConnectionError as conn_err:
            log.error(u"Connection error {0}".format(conn_err))
        except Timeout as timeout_err:
            log.error(u"Timeout error {0}".format(timeout_err))
        # whatever JSON exception is
        else:
            return GraderResponse(data=reply_data, success=True)

    @classmethod
    def from_config(cls, **config):
        pass


class SleepGrader(Grader):
    """Simple grader for debugging purposes."""

    def __init__(self, max_secs=0.01, min_secs=0):
        if min_secs >= max_secs:
            raise ValueError("min_secs ({0}) must be less than max_secs({1})"
                             .format(min_secs, max_secs))
        self.min_secs = min_secs
        self.max_secs = max_secs

    def grade(self, grader_request):
        time.sleep(random.uniform(self.min_secs, self.max_secs))
        return GraderResponse(data="Zzzzzzzz", success=True)

    def __unicode__(self):
        return u"SleepGrader: {} < t < {}".format(self.min_secs, self.max_secs)

    @classmethod
    def from_config(cls, **config):
        return cls()
