#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twython import TwythonStreamer
import twython

from newslynx_core.twitter.parse_tweet import (
  TweetParser
  )
from newslynx_core.controller import Controller
from newslynx_core.database import db 
from newslynx_core import settings

"""
FROM 

Finally, to address a common use case where you may want to track 
all mentions of a particular domain name (i.e., regardless of 
subdomain or path), you should use "example com" as the track 
parameter for "example.com" (notice the lack of period between 
"example" and "com" in the track parameter). This will be over-inclusive, 
so make sure to do additional pattern-matching in your code. 
See the table below for more examples related to this issue.
"""

# generic tweet parser as default
_twp = TweetParser()

class StreamHandler(TwythonStreamer):
  def __init__(self, **kwargs):
    
    TwythonStreamer.__init__(
      self,
      kwargs.get('api_key'),
      kwargs.get('api_secret'),
      kwargs.get('access_token'),
      kwargs.get('access_secret')
      )
    self.controller = Controller(
      org_id = 'public',
      source_type = 'twitter'
      )
    self._table = db['twitter']
    self.func = kwargs.get('func', _twp.parse)

  def on_success(self, data):
    task_id = data['id_str']
    if not self.controller.exists(task_id):
      output = self.func(data)
      self.controller.add(task_id)
      self._table.insert(output)
      self.controller.pub(task_id)

  def on_error(self, status_code, data):
    print status_code

class TwitterStreamParser:
  def __init__(self, **kwargs):
    self.stream = StreamHandler(
      api_key = kwargs.get('api_key', settings.TWT_API_KEY), 
      api_secret = kwargs.get('api_secret', settings.TWT_API_SECRET),
      access_token = kwargs.get('access_token', settings.TWT_ACCESS_TOKEN),
      access_secret = kwargs.get('access_secret', settings.TWT_ACCESS_SECRET),
      func = kwargs.get('func', _twp.parse)
    ) 
    self.terms = kwargs.get('terms')
    self.filter_level = kwargs.get('filter_level', None)

  def run(self):
    self.stream.statuses.filter(
      track=self.terms, 
      filter_level=self.filter_level
      )

if __name__ == '__main__':
  ts = TwitterStreamParser(terms=[
    'propublica org', 'propub ca', 'ny chalkbeat org', 'tn chalkbeat org',
    'motherjones com', 'mojo ly', 'co chalkbeat org', 'invw org', 
    'ckbe at', 'in chalkbeat org', 'publicintegrity org', 'yo'
    ])
  print ts.run()
  


  
