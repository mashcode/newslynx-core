#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Portions of this module were taken from newspaper
github.com/codelucas/newspaper
"""

import re
from HTMLParser import HTMLParser
import requests
from cookielib import CookieJar as cj
from lxml import etree

from newslynx_core import settings 

def get_request_kwargs(timeout, useragent):
  """
  This Wrapper method exists b/c some values in req_kwargs dict
  are methods which need to be called every time we make a request.
  """
  return {
      'headers' : {'User-Agent': useragent},
      'cookies' : cj(),
      'timeout' : timeout,
      'allow_redirects' : True
  }

def get_html(url, response=None):
  """
  Retrieves the html for either a url or a response object. All html
  extractions MUST come from this method due to some intricies in the
  requests module. To get the encoding, requests only uses the HTTP header
  encoding declaration requests.utils.get_encoding_from_headers() and reverts
  to ISO-8859-1 if it doesn't find one. This results in incorrect character
  encoding in a lot of cases.
  """
  FAIL_ENCODING = 'ISO-8859-1'
  useragent = settings.USER_AGENT
  timeout = settings.REQUEST_TIMEOUT

  if response is not None:
    if response.encoding != FAIL_ENCODING:
      return response.text
    return response.content # not unicode, fix later

  try:
    html = None
    response = requests.get(url=url, **get_request_kwargs(timeout, useragent))
    if response.encoding != FAIL_ENCODING:
      html = response.text
    else:
      html = response.content # not unicode, fix later
    if html is None:
      html = u''
    return html

  except Exception, e:
    log.debug('%s on %s' % (e, url))
    return u''

def node_to_string(node):
  """
  get the inner html of an lxml node.
  """
  return etree.tostring(node)

# html stripping
class MLStripper(HTMLParser):
  def __init__(self):
    self.reset()
    self.fed = []

  def handle_data(self, d):
    self.fed.append(d)

  def get_data(self):
    return ''.join(self.fed)

def strip_tags(html):
  """
  string tags and clean text from html.
  """
  s = MLStripper()
  s.feed(html)
  raw_text = s.get_data()
  raw_text = re.sub(r'\n|\t|\r', ' ', raw_text)
  return re.sub('\s+', ' ', raw_text).strip()

