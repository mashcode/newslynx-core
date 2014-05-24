#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import boto
import boto.s3
from boto.s3.key import Key
import sys
import json
from urlparse import urlparse, urljoin
import StringIO
import gzip

from newslynx_core import settings
from newslynx_core.parsers.serialization import(
  jsongzify, un_gz
  )

def is_s3_uri(uri):
  """Return True if *uri* can be parsed into an S3 URI, False otherwise."""
  try:
    parse_s3_uri(uri)
    return True
  except ValueError:
    return False

def parse_s3_uri(uri):
  """Parse an S3 URI into (bucket, key)

  >>> parse_s3_uri('s3://walrus/tmp/')
  ('walrus', 'tmp/')

  If ``uri`` is not an S3 URI, raise a ValueError
  """
  if not uri.endswith('/'):
    uri += '/'
    
  components = urlparse(uri)
  if (components.scheme not in ('s3', 's3n')
          or '/' not in components.path):
    raise ValueError('Invalid S3 URI: %s' % uri)

  return components.netloc, components.path[1:]

class S3(object):
  """ A class for connecting to a s3 bucket and uploading/downloading files"""
  def __init__(self, **kwargs):
    self.s3_uri = kwargs.get('s3_uri', settings.AWS_S3_STOR)
    self.bucket_name, self.stor = parse_s3_uri(self.s3_uri)
    self.bucket = self._connect_to_bucket(self.bucket_name)

  def _connect_to_bucket(self, bucket_name):
    conn = boto.connect_s3(
      settings.AWS_ACCESS_KEY_ID, 
      settings.AWS_SECRET_ACCESS_KEY
      )
    for i in conn.get_all_buckets():
      if bucket_name == i.name:
          return i

  def make_fp(self, filepath):
    fp = os.path.join(self.stor, filepath + ".json.gz")
    return fp

  def put(self, filepath, data):
    k = Key(self.bucket)
    k.key = self.make_fp(filepath)
    data = jsongzify(data)
    k.set_contents_from_string(data)

  def get(self, filepath):
    k = Key(self.bucket)
    k.key = self.make_fp(filepath)
    if k.exists():
      s = k.get_contents_as_string()
      print s
      return json.loads(un_gz(s))
    else:
      return None

  def delete(self, filepath):
    k = Key(self.bucket)
    k.key = self.make_fp(filepath)
    self.bucket.delete_key(k)

if __name__ == '__main__':
  s3 = S3()
  print s3.bucket_name
  print s3.stor 
  s3.put('test', {'data': 'test'})
  print s3.get('test')
  s3.delete('test')
  print s3.get('test')

