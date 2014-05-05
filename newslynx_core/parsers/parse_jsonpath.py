#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jsonpath_rw as jsonpath 

def get_jsonpath(obj, path, null=[]):
  """
  from https://pypi.python.org/pypi/jsonpath-rw/1.3.0
  parse a dict with jsonpath:
  usage:
  d = {'a' : [{'a':'b'}]}
  get_jsonpath(d, 'a[0].a')
  ['b']
  """
  jp = jsonpath.parse(path)
  res = [m.value for m in jp.find(obj)]
  if len(res) == 0:
    return null
  else:
    return res