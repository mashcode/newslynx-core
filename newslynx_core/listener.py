#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An example of a pubsub listener, for testing. Will be folded into 
`newlsnyx-queue`
"""

import gevent
from gevent.queue import Queue
import gevent.monkey
gevent.monkey.patch_all()

import redis 
import threading

from newslynx_core.controller import pool
from newslynx_core import settings 

class Listener(threading.Thread):
   def __init__(self, channels):
     threading.Thread.__init__(self)
     self.redis = rdb
     self.pubsub = self.redis.pubsub()
     self.pubsub.subscribe(channels)

  def work(self, item):
     print item['channel'], ":", item['data']

  def run(self):
    for item in self.pubsub.listen():
      if item['data'] == "KILL":
        self.pubsub.unsubscribe()
        print self, "unsubscribed and finished"
        break
     else:
        self.work(item)

 if __name__ == '__main__':
   client = Listener(['proublica*'])
   client.start()
