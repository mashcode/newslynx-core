#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.poll import Poll

# parser
from newslynx_core.homepages.parse_homepage import HomepageParser


class homepages(Poll):

  def get_tasks(self):
    for o in self.organizations:
      yield {
        'org_id': o['org_id'],
        'homepage': o['homepage']
      }

  def exec_task(self, task):
    p = HomepageParser(**task)
    p.run()

if __name__ == '__main__':
  t = homepages()
  t.run()
