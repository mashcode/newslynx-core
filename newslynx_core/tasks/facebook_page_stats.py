#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.poll import Poll

# parser
from newslynx_core.facebook.parse_page_stats import FacebookPageStatsParser

class facebook_page_stats(Poll):

  def get_tasks(self):
    for o in self.organizations:
      for page_id in o['facebook_pages']:
        if page_id:
          task = {
            'org_id': o['org_id'],
            'page_id': page_id
          }
          yield task 

  def exec_task(self, task):
    p = FacebookPageStatsParser(**task)
    p.run()

if __name__ == '__main__':
  t = facebook_page_stats()
  t.run()
