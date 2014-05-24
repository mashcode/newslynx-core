#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.source import Source
from newslynx_core.twitter.api import connect
from newslynx_core.twitter.parse_tweet import TweetParser 

class TwitterListParserInitError(Exception):
  pass

class TwitterUserParser(Source):
  def __init__(self, **kwargs):
    if 'screen_name' not in kwargs:
      raise TwitterUserParserInitError(
        'TwitterListParser requires a '
        'screen_name to run'
        )
    Source.__init__(
      self,
      org_id = kwargs.get('org_id', 'public'),
      source_type = 'twitter'
      )
    self.screen_name = kwargs.get('screen_name')
    self.limit = kwargs.get('limit', 200)
    self.api = connect()
    self.twp  = TweetParser(
      domain = kwargs.get('domain', None),
      short_url = kwargs.get('short_url', None)
      )

  def task_id(self, tweet):
    return tweet['id_str']

  def poller(self):
    tweets = self.api.get_user_timeline(
      screen_name=self.screen_name,
      count = self.limit
      )
    for tweet in tweets:
      yield tweet

  def parser(self, task_id, tweet):
    return self.twp.parse(tweet)

  def messenger(self, output):
    return {
      'twitter_id': output['twitter_id']
    }

if __name__ == '__main__':
  tlp = TwitterUserParser(screen_name = 'cspan')
  tlp.run()
