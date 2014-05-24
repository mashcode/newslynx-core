#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.poll import Poll

# parser
from newslynx_core.twitter.parse_user import TwitterUserParser
"""
twitter user timeline
"""
class twitter_users(Poll):

  def get_tasks(self):
    for o in self.organizations:
      for screen_name in o['twitter_accounts']:
        yield {
          'org_id': o['org_id'],
          'screen_name': screen_name
        }

  def exec_task(self, task):
    p = TwitterUserParser(**task)
    p.run()

if __name__ == '__main__':
  t = twitter_users()
  t.run()
