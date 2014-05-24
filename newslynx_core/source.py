#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An abstract class for performing polling a feed of data.
Built in functionality for checking whether
we've done a task, adding this task to our log,
inserting the output into the respect table,
and publishing a message to the queue.
"""
from retrying import retry

from newslynx_core.controller import Controller
from newslynx_core.database import db
from newslynx_core import settings
from random import choice

import gevent
from gevent.queue import Queue
import gevent.monkey
gevent.monkey.patch_all()

def random_sleep():
  return choice([i/100. for i in range(50,100, 1)])

class SourceInitError(Exception):
  pass

class SourceTimeout(Exception):
  pass

class Source:
  """
  Each Source must be initialized with
  the following attributes
    - org_id
    - source_type
    - source_id
  """
  def __init__(self, **kwargs):

    if 'org_id' not in kwargs or \
       'source_type' not in kwargs:

      raise SourceInitError(
        'A Source requires an org_id and source_type'
        'in order to run.'
      )
      
    self.org_id = kwargs.get('org_id')
    self.source_type = kwargs.get('source_type')
    self.num_workers = kwargs.get('num_workers', settings.GEVENT_QUEUE_SIZE)
    self.timeout = kwargs.get('timeout', 20)

    # access datastores
    self._table = db[self.source_type]
    self._controller = Controller(
      org_id = kwargs.get('org_id'),
      source_type = kwargs.get('source_type')
      )

    # task queues
    self._tasks = Queue()

  """
  For each data source, overwrite these
  four functions:
  `task_id` => generates a key each item parsed 
  `poller` => takes an input and returns a generator
              of tasks 
  `parser` => performs a task.
  `messenger` => formats pubsub message from the output
                 of `parser`
  Then call `.run()`
  """

  def task_id(self, entity):
    """
    overwrite
    """
    pass

  def poller(self):
    """
    overwrite
    """
    pass
 
  def parser(self, task_id, item):
    """
    overwrite
    """
    pass

  def messenger(self, output):
    pass

  def _capitalist(self):
    """
    Owns the means of production
    """
    # generate entities
    for item in self.poller():

      # generate id
      task_id = self.task_id(item)

      # efficiency, don't repeat tasks
      if not self._controller.exists(task_id):

        # assign task to anonyous prole.
        self._tasks.put((task_id, item), block=True, timeout=self.timeout)

        # keep track of what we've done.
        self._controller.add(task_id)

  def _prole(self):
    """
    Works tirelessly.
    """
    while not self._tasks.empty():
      
      # clock in, get a task
      task_id, item = self._tasks.get()
      
      # do it
      output = self.parser(task_id, item)

      # if it worked, send off data
      if output:
        # push to redisquue / sql / s3
        self._table.insert(output)
        self._mailman(task_id, output)
        # sleep
        gevent.sleep(0.1)

  def _mailman(self, task_id, output):

    """
    Don't kill the messenger.
    """
    self._controller.pub(task_id, output)

  def _society(self):
    """
    It's the system man
    """
    # start the day
    gevent.spawn(self._capitalist).join()

    # do work.
    greenlets = gevent.joinall([
      gevent.spawn(self._prole) 
        for w in xrange(self.num_workers)
    ])

  def run(self):
    """
    Run
    """
    self._society()
    
  def debug(self):
    # generate entities
    for item in self.poller():
    
      # generate id
      task_id = self.task_id(item)
  
      # efficiency, don't repeat tasks
      if not self._controller.exists(task_id):
        output = self.parser(task_id, item)
        # if it worked, send off data
        if output:
          # push to redisquue / sql / s3
          self._table.insert(output)
          self._mailman(task_id, output)

