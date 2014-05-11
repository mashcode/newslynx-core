#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from newslynx_core.source import Source
from newslynx_core.extractors.extract_author import AuthorExtractor
from newslynx_core.feeds.libs import feedparser
from newslynx_core.parsers.parse_url import (
  valid_url, prepare_url
  )
from newslynx_core.parsers.parse_html import (
  strip_tags
  )
from newslynx_core.parsers.parse_date import (
  time_to_datetime, current_local_datetime
  )

class GAlertParserInitError(Exception):
  pass

class GAlertParser(Source):
  def __init__(self, **kwargs):

    if 'feed_url' not in kwargs or \
        'org_id' not in kwargs or \
        'domain' not in kwargs:
      raise GAlertParserInitError(
        'FeedParser requires a feed_url, org_id, and domain'
        'in order to run.'
      )

    Source.__init__(
      self, 
      org_id = kwargs.get('org_id'),
      source_type = 'galerts'
    )
    self.feed_url = kwargs.get('feed_url')
    self.domain = kwargs.get('domain')
    self.re_ga_link = re.compile(r'http(s)?://www\.google\.com/url\?q=')
    self.extract_author = AuthorExtractor()


  # HELPERS # 
  def parse_link(self, entry):
    print entry
    internal = False
    raw_link = self.re_ga_link.sub('', entry.link)
    link = prepare_url(raw_link)
    return link

  def parse_title(self, entry):
    return strip_tags(entry.title)

  def parse_summary(self, entry):
    return strip_tags(entry.summary)

  def parse_date(self, entry):
    return time_to_datetime(entry.published_parsed)

  def parse_authors(self, entry):
    return self.extract_author.extract(entry.author)

  # CORE #
  def task_id(self, item):
    return item.id

  def poller(self):
    f = feedparser.parse(self.feed_url)
    for item in reversed(f.entries):
      yield item

  def parser(self, task_id, item):
    data = {}
    link = self.parse_link(item)
    print link
    if link:
      data['galert_id'] = task_id
      data['feed_url'] = self.feed_url
      data['url'] = link
      data['title'] = self.parse_title(item)
      data['summary'] = self.parse_summary(item)
      data['datetime'] = self.parse_date(item)

      return data

  def messenger(self, output):
    """
    overwrite, output list of tuples of 
    channel, data 
    """
    return {
      'url': output['url']
    }

if __name__ == '__main__':
  feed_url = 'http://www.google.com/alerts/feeds/14752688329844321840/4874425503898649357'
  ga = GAlertParser(feed_url = feed_url, org_id = 'propublica', domain='http://www.propublica.org')
  ga.run()

