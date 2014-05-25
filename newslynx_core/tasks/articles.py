#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.poll import Poll

# parser
from newslynx_core.feeds.parse_feed import FeedParser

class articles(Poll):

  def get_tasks(self):
    for o in self.organizations:
      for feed_url in o['rss_feeds']:
        if feed_url:
          task = {
            'feed_url': feed_url,
            'org_id': o['org_id'],
            'domain': o['domain']
          }
          yield task 

  def exec_task(self, task):
    fp = FeedParser(**task)
    fp.run()

if __name__ == '__main__':
  p = articles()
  p.run()

