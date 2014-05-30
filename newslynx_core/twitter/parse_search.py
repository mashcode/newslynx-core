#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.source import Source
from newslynx_core.twitter.api import connect
from newslynx_core.twitter.parse_tweet import TweetParser 

from pprint import pprint

class TwitterSearchParserInitError(Exception):
  pass

class TwitterSearchParser(Source):
  def __init__(self, **kwargs):
    if 'query' not in kwargs:
      raise TwitterSearchParserInitError(
        'TwitterListParser requires a '
        'search to run'
        )
    Source.__init__(
      self,
      org_id = kwargs.get('org_id', 'public'),
      source_type = 'twitter',
      hask_key = 'public'
      )
    self.api = connect(**kwargs)
    self.query = kwargs.get('query')
    self.limit = kwargs.get('limit', 100)
    self.twp  = TweetParser(
      domain = kwargs.get('domain', None),
      short_url = kwargs.get('short_url', None)
      )

  def task_id(self, tweet):
    return tweet['id_str']

  def poller(self):
    tweets = self.api.search(q = self.query, count = self.limit)
    for tweet in reversed(tweets['statuses']):
      yield tweet

  def parser(self, task_id, tweet):
    data = self.twp.parse(tweet)
    data['org_id'] = self.org_id
    data['query']= self.query
    return data


if __name__ == '__main__':
  tsp = TwitterSearchParser(query='propublica')
  tsp.run()

