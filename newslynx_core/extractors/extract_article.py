#!/usr/bin/env python
# -*- coding: utf-8 -*-

from readability.readability import Document
import newspaper
import requests
import logging 
from retrying import retry 

from newslynx_core.parsers.parse_url import (
  prepare_url, get_domain
  )
from newslynx_core.parsers.parse_html import (
  get_html, node_to_string
  )
from newslynx_core.articles.article import Article
from newslynx_core import settings


class ArticleExtractorError(Exception):
  pass

class ArticleExtractor:
  """
  multi-method article extraction framework for NewsLynx.

  Our strategy will be as follows:
  1. Get JUST the article html using various methods
  2. TK: Come up with a method of scoring results and picking best option.
    * For now we'll just choose newspaper / goose because it seemed to do the 
      best of all open-source tools in this comparision:
      -  http://readwrite.com/2011/06/10/head-to-head-comparison-of-tex#awesm=~oDemRcIbyN4lYB
  3. TK: Apply image / url / movie / metadata extraction to raw page html.
    * For now we'll just go with newspaper / goose's built-in methods 
  4. Return an Article object.
  """
  def __init__(self, **kwargs):

    ## TK: more initialization settings 
    self.np_config = settings.NEWSPAPER_CONFIG

    # try to import goose.
    try:
      from goose import Goose 
    except ImportError:
      pass
    else:
      self.g = Goose({'browser_user_agent': settings.USER_AGENT})

  @retry(wait_random_min=100, wait_random_max=1000)
  def extract_newspaper(self, url, html=None):
    """
    Extract an article with newspaper.
    unfortunately the author did not include 
    a html option, so we'll hack it.
    """
    np_article = newspaper.Article(url = url, config=self.np_config)
    np_article.build()
    return np_article
    # return node_to_string(np_article.top_node)

  def extract_goose(self, html):
    """
    Extract an article with goose.

    NOTE: This is probably duplicitous since 
    newspaper extends python-goose's source code. 
    """
    g_article = self.g.extract(raw_html = html)
    return g_article
    #return node_to_string(g_article.top_node)

  def extract_boilerpipe(self, html):
    """ 
    Extract an article with Boilerpipe 
    
    NOTE: This is an optional method as 
    boilerpipe is dependency-heavy and
    will be potentially cumbersome 
    to run on manta.
    """
    try:
      from boilerpipe.extract import Extractor
    except ImportError:
      return 

    bp_extract = Extractor(html=html)
    return bp_extract.getHTML()

  def extract_readability(self, html):
    """
    Extract an article with Readability.
    """
    rdb_extract = Document(html)      
    return rdb.summary()

  def extract(self, **kwargs):
    """
    primary method for extraction, for now 
    we're basically just wrapping newspaper's 
    Article.build()
    """
    if 'url' not in kwargs or 'org_id' not in kwargs :
      raise ArticleExtractorError(
        'ArticleExtractor requires a url!'
      )
      
    # get the url 
    url = kwargs.get('url')
    org_id = kwargs.get('org_id')
    
    # Initialize an Article object
    article = Article(url = url, org_id = org_id)
    
    # for now we're just using newspaper 
    np_article = self.extract_newspaper(url = article.url)

    # populate our Article from newspaper Article 
    article = article.from_newspaper(np_article)

    # return an Article object
    return article

  def get_best_candidate(self, html):
    """
    TK: determine best node candidate 
    """
    pass 
