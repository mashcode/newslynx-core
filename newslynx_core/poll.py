#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.fixtures.organizations import ORGANIZATIONS
from newslynx_core.database import db 

import gevent
from gevent.queue import Queue
import gevent.monkey
gevent.monkey.patch_all(thread=False)


class PollTimeout(Exception):
  pass

class Poll:
  """
  An abstract class for running parsers.
  """
  def __init__(self, **kwargs):
    self.organizations = ORGANIZATIONS
    self.db = db # TODO: hook up to database
    self.num_workers = kwargs.get('num_workers', 5)
    self.timeout = kwargs.get('timeout', 300)
    self.tasks = Queue()

  def get_tasks(self, query=None):
    """
    extract metadata from organizations for parsing
    via sql query. (fixture for now.)
    """
    pass 

  def exec_task(self, task):
    pass

  def _get_tasks(self):
    for task in self.get_tasks():
      self.tasks.put_nowait(task)

  def _exec_tasks(self):
    while not self.tasks.empty():
      task = self.tasks.get()
      self.exec_task(task)
      gevent.sleep(0)

  def run(self):
    gevent.spawn(self._get_tasks).join()
    gevent.joinall([
        gevent.spawn(self._exec_tasks) 
          for w in xrange(self.num_workers)
    ])

  def debug(self):
    for task in self.poller():
      self.parser(task)


