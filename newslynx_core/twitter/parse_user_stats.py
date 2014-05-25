#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from newslynx_core.source import Source
from newslynx_core.twitter.api import connect
from newslynx_core.twitter.parse_tweet import TweetParser 

class TwitterUserStatsParser(Exception):
  pass

class TwitterUserStatsParser(Source):
  def __init__(self, **kwargs):
    if 'screen_name' not in kwargs:
      raise TwitterUserStatsParserInitError(
        'TwitterUserStatsParser requires a'
        'screen_name to run'
        )
    Source.__init__(
      self,
      org_id = kwargs.get('org_id', None),
      source_type = 'twitter_user_stats'
      )
    self.screen_name = kwargs.get('screen_name')
    self.api = connect(**kwargs)

  def task_id(self, tweet):
    return "%s-%s" % (self.screen_name, datetime.now().strftime('%s'))

  def poller(self):
    yield self.api.show_user(screen_name = self.screen_name)

  def parser(self, task_id, user):
    data = {}
    data['user_stats_id'] = task_id
    data['org_id'] = self.org_id
    data['datetime'] = datetime.now()
    data['screen_name'] = self.screen_name
    data['favorites'] = user.get('favourites_count', None)
    data['followers'] = user.get('followers_count', None)
    data['friends'] = user.get('friends_count', None)
    data['listed'] = user.get('listed_count', None)
    data['statuses'] = user.get('statuses_count', None)
    return data

if __name__ == '__main__':
  tusp = TwitterUserStatsParser(org_id = 'propublica', screen_name = 'propublica')
  tusp.run()

