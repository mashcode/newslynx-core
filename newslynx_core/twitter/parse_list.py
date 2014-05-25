#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.source import Source
from newslynx_core.twitter.api import connect
from newslynx_core.twitter.parse_tweet import TweetParser 

class TwitterListParserInitError(Exception):
  pass


class TwitterListParser(Source):
  def __init__(self, **kwargs):
    if 'list_owner' not in kwargs and 'list_name' not in kwargs:
      raise TwitterListParserInitError(
        'TwitterListParser requires a list_owner'
        'and list_slug to run'
        )
    Source.__init__(
      self,
      org_id = kwargs.get('org_id', 'public'),
      source_type = 'twitter',
      hask_key = 'public'
      )
    self.list_owner = kwargs.get('list_owner')
    self.list_name = kwargs.get('list_name')
    self.api = connect()
    self.limit = kwargs.get('limit', 200)
    self.twp  = TweetParser(
      domain = kwargs.get('domain', None),
      short_url = kwargs.get('short_url', None)
      )

  def task_id(self, tweet):
    return tweet['id_str']

  def poller(self):
    tweets = self.api.get_list_statuses(
      owner_screen_name = self.list_owner,
      slug =  self.list_name,
      count = self.limit
    )
    for tweet in tweets:
      yield tweet

  def parser(self, task_id, tweet):
    data = self.twp.parse(tweet)
    data['list_name'] = self.list_name,
    data['list_owner'] = self.list_owner,
    data['org_id'] = self.org_id
    return data

if __name__ == '__main__':
  tlp = TwitterListParser(list_owner = 'cspan', list_name = 'members-of-congress')
  tlp.run()
