#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gevent
from gevent.queue import Queue
import gevent.monkey
gevent.monkey.patch_all()

from newslynx_core.articles.article import Article
from newslynx_core.extractors.extract_article import ArticleExtractor
from newslynx_core.extractors.extract_image import ImageExtractor
from newslynx_core.extractors.extract_author import AuthorExtractor
from newslynx_core.extractors.extract_url import URLExtractor
from newslynx_core.feeds.libs import feedparser
from newslynx_core.parsers.parse_jsonpath import get_jsonpath
from newslynx_core.parsers.parse_html import strip_tags
from newslynx_core.parsers.parse_date import (
  time_to_datetime, current_local_datetime
  )
from newslynx_core.parsers.parse_url import (
  prepare_url, unshorten_url, valid_url
  )
from newslynx_core import settings

from pprint import pprint 

URL_CANDIDATE_JSONPATH = [
  'id', 'feedburner_origlink', 'link', 'links[*].href'
]

# applies to feed AND individual entries.
DATE_CANDIDATE_JSONPATH = [
  'updated_parsed', 'published_parse'
]

AUTHOR_CANDIDATE_JSONPATH = [
  'author', 'author_detail.name', 'authors[*].name'
]

IMG_CANDIDATE_JSONPATH = [
  'media_content[*].url'
]

CONTENT_CANDIDATE_JSONPATH = [
  'content[*].value', 'summary'
]

TAG_CANDIDATE_JSONPATH = [
  'tags[*].label', 'tags[*].term'
]

f = open('feeds.json', 'wb')

class CandidateParserError(Exception):
  pass

class FeedParserInitError(Exception):
  pass

class FeedParserError(Exception):
  pass

class FeedParser:
  """
  Strategy: 
  Use feedparser to extract / standardize feeds.
  For each entry:
  1. find all possible urls and get best 
     candidate(s) by checking which are valid 
     via `valid_url()`. if still not, open links 
     and check if these links are shortened, 
     and unshorten them. Default to id if 
     it exists.
  2. parse mutliple date candidates and 
     select the earliest.
  3. parse all uniq authors
  4. get all images, select top_img
  5. TK extract article links from html
  """
  
  def __init__(self, **kwargs):

    if 'feed_url' not in kwargs:
      raise FeedParserInitError(
        'FeedParser requires a feed_url.'
      )
    
    # kwargs
    self.org_id          = kwargs.get('org_id', None)
    self.feed_url        = kwargs.get('feed_url')
    self.domain          = kwargs.get('domain')
    self.source          = kwargs.get('source', None)
    self.entry_urls      = kwargs.get('entry_urls', None)
    self.good_regex      = kwargs.get('good_regex', None)
    self.bad_regex       = kwargs.get('bad_regex', None)
    self.short_regex     = kwargs.get('short_regex', None)
    self.max_entries     = kwargs.get('max_entries', settings.MAX_FEED_ENTRIES)
    self.is_complete     = kwargs.get('is_complete', False)
    self.is_full_text    = kwargs.get('is_full_text', False)
    self.timezone        = kwargs.get('timezone', settings.LOCAL_TZ)

    # extractors
    self.image_extract   = ImageExtractor(referer = self.feed_url)
    self.article_extract = ArticleExtractor()
    self.author_extract  = AuthorExtractor()
    self.url_extract     = URLExtractor(domain = self.domain)
        
    # article urls we've already seen
    self.article_urls    = set()

    # gevent
    self.tasks = Queue()
    self.num_workers = kwargs.get('num_workers', settings.GEVENT_QUEUE_SIZE)

  # check / update url
  def _add_article(self, url):
    self.article_urls.add(url)

  def _dup_article(self, url):
    return (url in self.article_urls)

  def _check_new_url(self, url):
    if not self._dup_article(url):
      self._add_article(url)
      return False
    else:
      return True

  def get_candidates(self, obj, jsonpath):
    """
    evaluate an object with jsonpath, 
    and get all unique vals / lists
    of values
    """
    candidates = set()
    for path in jsonpath:
      path_candidates = get_jsonpath(obj, path)

      if isinstance(path_candidates, list):
        for candidate in path_candidates:
          if candidate:
            candidates.add(candidate)

      elif isinstance(path_candidates, dict):
        for k in path_candidates.keys():
          candidates.add(candidate)

      elif isinstance(path_candidates, str):
        candidates.add(candidate)

    return list(candidates)


  def get_entry_url(self, entry):
    """
    Two strategies:
    1: check candidates for valid urls
    2: Open / Unshorten candidates
    3: If still none, default to first candidate
    """
    # defaults to orig_link -> id -> link
    # only if valid
    if 'feedburner_origlink' in entry: 
      if valid_url(entry.feedburner_origlink):
        return prepare_url(entry.feedburner_origlink)
  
    if 'link' in entry:
      if valid_url(entry.link):
        return prepare_url(entry.link)

    if 'id' in entry:
      if valid_url(entry.id):                  
        return prepare_url(entry.id)

    # get potential candidates
    candidates = self.get_candidates(entry, URL_CANDIDATE_JSONPATH)

    # if no candidates, return an empty string
    if len(candidates) == 0:
      #print "< no url found! >"
      return None

    # test for valid urls:
    valid_urls = list(set([
      u for u in candidates if not self._dup_article(u) and valid_url(u)
      ]))
    
    # if we have one or more, update entry_urls and return the first
    if len(valid_urls) >= 1:
      return valid_urls[0]

    # else, expand all candidates and filter out ones we've seen
    expanded_urls = list(set([ 
      u for u  in (unshorten_url(url=c, regex=self.short_regex) for c in candidates)
        if not self._dup_article(u) and valid_url(u)
      ]))

    # if we've found one or more return the first
    if len(expanded_urls) >= 1:
      return expanded_urls[0]

    # if we STILL haven't found anything, just
    # return the first candidate:
    return candidates[0]


  def get_date(self, obj):
    """
    return earliest time of candidates or current time.
    """
    candidates = self.get_candidates(obj, DATE_CANDIDATE_JSONPATH)
    if len(candidates) > 0:
      return time_to_datetime(sorted(candidates)[0])

    else:
      return current_local_datetime(self.timezone)

  
  def get_authors(self, entry):
    """
    return all candidates, and parse unique
    """
    
    authors = set()
    
    _authors = self.get_candidates(entry, AUTHOR_CANDIDATE_JSONPATH)
    for _a in _authors:
      for author in self.author_extract.from_string(_a):
        authors.add(author)

    return list(authors)

  def get_imgs(self, entry):
    img_urls = self.get_candidates(entry, IMG_CANDIDATE_JSONPATH)
    img_url, img, thumb = self.image_extract.get_top_img(img_urls)
    return img_urls, img_url, img, thumb
  
  def get_article_html(self, entry):
    """
    Get all article text candidates and check which one is the longest.
    """
    candidates = self.get_candidates(entry, CONTENT_CANDIDATE_JSONPATH)
    candidates.sort(key = len)
    return candidates[-1]
  
  def get_tags(self, entry):
    tags = set()
    _tags = self.get_candidates(entry, TAG_CANDIDATE_JSONPATH)
    for _t in _tags:
      tags.add(_t)

    return list(tags)

  def get_text(self, article_html):
    return strip_tags(article_html)
  
  def get_title(self, entry):
    return entry['title']

  def get_urls(self, article_html):
    return self.url_extract.extract(html = article_html)


  def parse_entry(self, e):

    entry, updated_at = e
    """
    Parse an entry in an Article and 
    merge data with Article Extraction
    """
    url  = self.get_entry_url(entry)
    dup  = self._check_new_url(url)

    if url and not dup:

      # initialize an article object
      article = Article(url = url, source=self.source)
      
      # get image
      img_urls, img_url, img, thumb = self.get_imgs( entry )

      # get html
      article_html = self.get_article_html( entry )

      int_links, ext_links = self.get_urls(article_html)

      # get title
      title = self.get_title( entry )
      
      # set values 
      article.set_article_html(   article_html )
      article.set_text(           self.get_text( article_html ) )
      article.set_title(          title)
      article.set_int_links(      int_links)
      article.set_ext_links(      ext_links)
      article.set_tags(           self.get_tags( entry ) )
      article.set_authors(        self.get_authors( entry ) )
      article.set_dates(          self.get_date( entry ) )
      article.set_updated(        updated_at )
      article.set_img_urls(       img_urls )
      article.set_img(            img )
      article.set_thumb(          thumb )
      
      # get article extraction and merge
      np_article = self.article_extract.extract( url = url )

      if np_article:
        article = article.from_newspaper( np_article, merge=True)
        f.write(article.to_json() + "\n")
      else:
        f.write(article.to_json() + "\n")
        
  
  def get_entries(self):
    """
    parse feed and stream unique records
    """
    f = feedparser.parse(self.feed_url)

    updated_at = self.get_date(f)
    for entry in f.entries:
      self.tasks.put_nowait((entry, updated_at))

  def parse(self):
    while not self.tasks.empty():
      item = self.tasks.get()
      self.parse_entry(item)
      gevent.sleep(0)

  def run(self):
    gevent.spawn(self.get_entries).join()
    gevent.joinall([
        gevent.spawn(self.parse) 
          for w in xrange(self.num_workers)
    ])


if __name__ == '__main__':
  feed_url = 'http://rss.nytimes.com/services/xml/rss/nyt/Science.xml'
  fp = FeedParser(feed_url = feed_url, source = 'http://www.nytimes.com/')
  fp.run()
