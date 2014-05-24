#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A class for controlling and keeping track of pollers
"""
import sys
import os
import redis
from hashlib import sha1 
from datetime import datetime

from newslynx_core import settings
from newslynx_core.parsers.serialization import jsonify
from newslynx_core.s3.api import S3
from newslynx_core.parsers.parse_date import (
  current_timestamp
  )

import gevent 
import gevent.monkey
gevent.monkey.patch_all()

#instaniate a connection pool
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

class Controller:
  def __init__(self, **kwargs):
    self.org_id = kwargs.get('org_id')
    self.source_type = kwargs.get('source_type')
    self.key = self._build_key()
    self.rdb = redis.StrictRedis(connection_pool = pool)
    self.s3 = S3()
    self.date_slug = datetime.now().date().strftime('%Y/%m/%d')
    self.expires = settings.SET_EXPIRES
    
  def _build_key(self):
    return "%s:%s" % (self.org_id, self.source_type)

  def _date_slug(self):
    return 

  def _build_fp(self, task_id):
    task_hash = sha1(task_id).hexdigest()
    return os.path.join(self.org_id, self.source_type, self.date_slug, task_hash)

  def _now(self):
    return float(current_timestamp())

  def exists(self, task_id):
    return self.rdb.sismember(self.key, task_id)

  def add(self, task_id):
    self.rdb.sadd(self.key, task_id)
    # TODO: get sorted sets working
    # self.rdb.zadd(self.key, self._now(), task_id) 

  def pub(self, task_id, data):
    pass
    #fp = self._build_fp(task_id)
    #self.s3.put(fp, data),
    # self.rdb.publish( self.key, jsonify(data))

def lskeys():
  c = Controller(org_id = "", source_type = "")
  for k in c.rdb.keys():
    print k

def flushall():
  c = Controller(org_id = "", source_type = "")
  for k in c.rdb.keys():
    c.rdb.delete(k)

if __name__ == '__main__':
  if len(sys.argv) > 0:
    task = sys.argv[1]
    if task == "flushall":
      flushall()
    elif task == "lskeys":
      lskeys()
