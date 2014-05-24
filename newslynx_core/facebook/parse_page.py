#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.source import Source
from newslynx_core.facebook.api import connect
from newslynx_core.facebook.parse_post import (
  FacebookPostParser
  )

class FacebookPageParserInitError(Exception):
  pass

class FacebookPageParser(Source):
  def __init__(self, **kwargs):
    if 'page_id' not in kwargs:
      raise FacebookPageParserInitError(
        'FacebookPageParser must have a page_id'
        )
    Source.__init__(self,
      org_id = kwargs.get('org_id'),
      source_type = 'facebook_posts'
      )
    self.api = connect()
    self.page_id = kwargs.get('page_id')
    self.limit = kwargs.get('limit', 200)
    self.post_parser = FacebookPostParser(
      org_id = kwargs.get('org_id'),
      page_id = self.page_id,
      regex = kwargs.get('short_url', None)
      )

  def task_id(self, post):
    return post['id']

  def poller(self):
    page = self.api.get(self.page_id + '/posts', page=False, retry=5, limit=5)
    for post in reversed(page['data']):
      yield post

  def parser(self, task_id, post):
    return self.post_parser.parse(post)

  # def messnger(self, output):
  #   return {
  #     'post_id': output['post_id']
  #   }

if __name__ == '__main__':
  fbpp = FacebookPageParser(org_id='propublica', page_id='propublica')
  fbpp.run()
