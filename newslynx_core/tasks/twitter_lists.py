#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.poll import Poll

# parser
from newslynx_core.twitter.parse_list import TwitterListParser

class twitter_lists(Poll):

  def get_tasks(self):
    for o in self.organizations:
      for l in o['twitter_lists']:
        yield {
          'list_owner': l['list_owner'],
          'list_name': l['list_name'],
          'org_id': o['org_id']
        }

  def exec_task(self, task):
    p = TwitterListParser(**task)
    p.run()

if __name__ == '__main__':
  t = twitter_lists()
  t.run()
