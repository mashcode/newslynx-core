#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.poll import Poll

# parser
from newslynx_core.alerts.parse_galert import GAlertParser

class galerts(Poll):

  def get_tasks(self):
    for o in self.organizations:
      for feed_url in o['galerts']:
        if feed_url:
          task = {
            'feed_url': feed_url,
            'org_id': o['org_id'],
            'domain': o['domain']
          }
          yield task 

  def exec_task(self, task):
    fp = GAlertParser(**task)
    fp.run()

if __name__ == '__main__':
  t = galerts()
  t.run()