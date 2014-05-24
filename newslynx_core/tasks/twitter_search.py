#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.poll import Poll

# parser
from newslynx_core.twitter.parse_search import TwitterSearchParser

"""
twitter user timeline
"""
class twitter_search(Poll):

  def get_tasks(self):
    for o in self.organizations:
      for query in o['twitter_searches']:
        yield {
          'org_id': o['org_id'],
          'query': query
        }

  def exec_task(self, task):
    p = TwitterSearchParser(**task)
    p.run()

if __name__ == '__main__':
  t = twitter_search()
  t.run()
