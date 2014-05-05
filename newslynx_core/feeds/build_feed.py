#!/usr/bin/env python
# -*- coding: utf-8 -*-

import newspaper

from newslynx_core.feeds.libs import feedfinder
from newslynx_core.feeds.parse_feed import FeedParser
from newslynx_core.extractors.extract_article import ArticleExtractor

class FeedBuilderInitError(Exception):
  pass

class FeedBuilderRunError(Exception):
  pass

class FeedBuilder:
  """
  One strategy for ensuring article completeness will 
  involve constructing alternative feeds, joining
  them, and removing duplicates on the fly

  These are our steps
  1. build a source using newspaper 
  2. using extracted category urls from newspaper 
     and the base domain, find alternative 
     rss feeds with feedfinder and parse them
     and yield Article objects
  3. iterate through article urls, check if 
     they match the domain, regexes, and whether 
     they have been parsed before. yield new lynx!
  4. Could also crawl a site and check for valid 
     urls.
  """

  def __init__(self, **kwargs):
    # must have source url
    if 'source_url' not in kwargs:
      raise FeedBuilderInitError(
        'Must include a source_url and domain'
      )
    # kwargs
    self.source_url    =  kwargs.get('source_url')
    self.simple_domain =  get_simple_domain(self.source_url)
    self.feed_urls     =  kwargs.get('feed_urls', [])
    self.source        =  kwargs.get('source', 'feedfinder')
    self.is_complete   =  kwargs.get('is_complete', False)
    self.is_full_text  =  kwargs.get('is_full_text', False)
    self.good_regex    =  kwargs.get('good_regex', None)
    self.bad_regex     =  kwargs.get('bad_regex', None)
    self.timezone      =  kwargs.get('timezone', None)
    self.np_config     =  kwargs.get('np_config', settings.NEWSPAPER_CONFIG)

    # build our news source
    self.np_source = newspaper.build(self.source_url, self.np_config)

    # init article extractor
    self.article_extractor = ArticleExtractor()

    # feeds we've already seen 
    self.feed_urls = set( self.np_source.feed_urls() + self.feed_urls )

    # article urls we've already seen
    self.article_urls = set()

  # utility for initlizing a feed.
  def _init_feed_parser(self, feed_url):
    return FeedParser(
      feed_url       =  feed_url,
      source         =  self.source,
      is_complete    =  self.is_complete,
      is_full_text   =  self.is_full_text,
      good_regex     =  self.good_regex,
      bad_regex      =  self.bad_regex,
      timezone       =  self.timezone
    )

  # check / update feed
  def _add_feed_url(self, feed_url):
    self.feed_urls.add(url)

  def _dup_feed_url(self, feed_url):
    return (feed_urls in self.feed_urls)

  def _update_feed_urls(self, feed_url):
    if self._dup_feed_url(feed_url):
      return False
    else:
      self._add_feed_url(feed_url)
      return True

  # check / update url
  def _add_article_url(self, url):
    self.article_urls.add(url)

  def _dup_article_url(self, url):
    return (url in self.article_urls)

  def _update_article_urls(self, url):
    if self._dup_article_url(url):
      return False
    else:
      self._add_article_url(url)
      return True
  
  def _get_initial_feeds(self):
    for feed_url in list(self.feed_urls):
      yield feed_url

  # get feeds from 
  def _get_category_feeds(self):
    # loop through each category
    for category_url in self.np_source.category_urls():
      # do a simple domain check
      if simple_domain in category_url:
        # find feeds
        feed_urls = feedfinder.feeds(category_url)
        # loop through urls
        for feed_url in feed_urls:
          # check for dups
          if self._update_feed_urls(feed_url):
            # yield
            yield feed_url

  def _parse_feed(self, feed_url):
    """
    iterate a feed and check for duplicates
    """
    fp = _init_feed_parser(feed_url)
    for article in fp.parse():
      if self._update_article_urls(article_url):
        yield article

  def _pool_feeds(self):
    """
    TO DO: gevent integration
    There must be a more elegant 
    way of doing all this generating / 
    updating.
    """
    tasks = [
      self._get_initial_feeds(),
      self._get_category_feeds()
    ]
    for task in tasks:
      for feed in task:
        articles = self._parse_feed(feed_url)
        for article in articles:
          yield article

  def from_feedfinder(self):
    pool = self._pool_feeds()
    for article in pool:
      yield article

  def _pool_urls(self):
    for article in np_source.article_urls:
      url = article.url
      if simple_domain in url:
        if self._update_article_urls(url):
          yield url

  def from_homepage(self):
    for url in self._pool_urls():
      article =  self.article_extractor(url=url)
      yield article

  def _iter_methods(self, methods):
    
    for m in methods:

      # fun via feed finder
      if m == 'feedfinder':
        for article in self.from_feedfinder():
          yield article

      # run via newspaper
      elif m == 'newspaper':
        for article in self.from_newspaper():
          yield article

  def build(self, methods = ['feedfinder', 'homepage']):
    """
    build the feed and stream results 
    """
    for article in self._iter_methods():
      yield article


