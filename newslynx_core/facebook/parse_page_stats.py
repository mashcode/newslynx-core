#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime 

from newslynx_core.source import Source 
from newslynx_core.facebook.api import connect 

class FacebookPageStatsInitError(Exception):
  pass

class FacebookPageStats(Source):
  def __init__(self, **kwargs):

    if  'page_id' not in kwargs:
      raise FacebookPageStatsInitError(
        'FacebookPageStats requires a page_id in order to run'
      )
    Source.__init__(
      self, 
      org_id = kwargs.get('org_id'),
      source_type = 'facebook_page_stats'
    )
    self.api = connect()
    self.page_id = kwargs.get('page_id')

  def task_id(self, acct_data):
    # always update
    tid = "%s-%s" % (self.page_id, datetime.now().strftime('%s'))
    return tid

  def poller(self):
    yield self.api.get(self.page_id)

  def parser(self, task_id, item):
    data = {}
    data['org_id'] = self.org_id
    data['page_stats_id'] = task_id
    data['page_id'] = self.page_id
    data['page_talking_about_count'] = item['talking_about_count']
    data['page_likes'] = item['likes']
    data['datetime'] = datetime.now()

    return data 

if __name__ == '__main__':
  fbps = FacebookPageStats(org_id='propublica', page_id='propublica')
  fbps.run()

