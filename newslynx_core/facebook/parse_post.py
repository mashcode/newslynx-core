#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime 

from newslynx_core.parsers.parse_date import (
  current_local_datetime
  )
from newslynx_core.parsers.parse_url import (
  prepare_url, is_short_url, unshorten_url, extract_urls
  )
from newslynx_core.parsers.parse_re import (
  build_regex
  )
from newslynx_core import settings

class FacebookPostParser:
  def __init__(self, **kwargs):
    self.page_id = kwargs.get('page_id', None)
    self.org_id = kwargs.get('org_id', None)
    self.regex = kwargs.get('short_url', None)
    if self.regex:
      self.regex = build_regex(self.regex)

  def get_url_candidates(self, post):
    urls = set()
    if post.has_key('link'):
      urls.add(post['link'])
    if post.has_key('source'):
      urls.add(post['source'])
    if post.has_key('message'):
      msg_urls = self.parse_message_urls(post['message'])
      for u in msg_urls: urls.add(u)
    return list(urls)

  def parse_message_urls(self, message):
    urls = extract_urls(message)
    return urls

  # TODO: improve this
  def get_img(self, post):
    return post.get('picture', None)

  def get_urls(self, post):
    candidates = self.get_url_candidates(post)
    urls = set()
    for u in candidates:
      if 'facebook' not in u:
        if is_short_url(u):
          u = unshorten_url(u)
        urls.add(prepare_url(u))
    return list(urls)

  def get_datetime(self, post):
    if post.has_key('updated_time'):
      return datetime.strptime(post['updated_time'], settings.FB_DATE_FORMAT)
    else:
      return datetime.now()

  def parse(self, post):
    data = {}
    data['org_id'] = self.org_id
    data['page_id'] = self.page_id
    data['post_id'] = post.get('id', None)
    data['urls'] = self.get_urls(post)
    data['img_url'] = self.get_img(post)
    data['datetime'] = self.get_datetime(post)
    data['message'] = post.get('message', None)
    data['description'] = post.get('description', None)
    data['status_type'] = post.get('status_type', None)
    data['type'] = post.get('type', None)
    return data



