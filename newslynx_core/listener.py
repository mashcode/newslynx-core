#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An example of a pubsub listener, for testing. Will be folded into 
`newlsnyx-queue`
"""
import threading
from newslynx_core import settings 
from newslynx_core.controller import rdb
from newslynx_core.parsers.serialization import jsonify
 
class Listener(threading.Thread):
  def __init__(self, channels):
    threading.Thread.__init__(self)
    self.rdb = rdb
    self.pubsub = self.rdb.pubsub()
    self.pubsub.subscribe(channels)
  
  def work(self, item):
    print jsonify(item['data'])
  
  def run(self):
    for item in self.pubsub.listen():
      if item['data'] == "KILL":
        self.pubsub.unsubscribe()
        print self, "unsubscribed and finished"
        break
      else:
        self.work(item)

if __name__ == '__main__':

  l = Listener(['propublica:articles'])
  l.run()
