#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent
from gevent.queue import Queue
import gevent.monkey
gevent.monkey.patch_all()

from newslynx_core.fixtures.organizations import ORGANIZATIONS

class Poll:
  """
  An abstract class for running parsers.
  """
  def __init__(self, **kwargs):
    self.organizations = ORGANIZATIONS # TODO: hook up to database
    self.num_workers = kwargs.get('num_workers', 10)
    self.tasks = Queue()

  def poller(self):
    """
    extract metadata from organizations for parsing
    """
    pass 

  def parser(self, kw):
    pass

  def _assign_tasks(self):
    for task in self.poller():
      self.tasks.put_no_wait(task)

  def _run_tasks(self):
    while not self.tasks.empty():
      task = self.tasks.get()
      self.parser(task)
      gevent.sleep(0)

  def run(self):
    gevent.spawn(self._assign_tasks).join()
    gevent.joinall([
        gevent.spawn(self._run_tasks) 
          for w in xrange(self.num_workers)
    ])

  def debug(self):
    for task in self.poller():
      self.parser(task)


