#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A class for controlling and keeping track of pollers
"""

import redis

from newslynx_core import settings
from newslynx_core.utils.serialization import jsonify
from newslynx_core.parsers.parse_date import (
  current_timestamp
  )
#instaniate a connection pool
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

class Controller:
  def __init__(self, **kwargs):
    self.org_id = kwargs.get('org_id')
    self.source_type = kwargs.get('source_type')
    self.key = self._build_key()
    self.rdb = redis.StrictRedis(connection_pool = pool)
    self.expires = settings.SET_EXPIRES
    

  def _build_key(self):
    return "%s:%s" % (self.org_id, self.source_type)

  def _now(self):
    return float(current_timestamp())

  def exists(self, task_id):
    return self.rdb.sismember(self.key, task_id)

  def add(self, task_id):
    self.rdb.sadd(self.key, task_id)
    # self.rdb.zadd(self.key, self._now(), task_id)

  def pub(self, data):
    self.rdb.publish(self.key, jsonify(data))