#!/usr/bin/env python
# -*- coding: utf-8 -*-

from readability.readability import Document
import newspaper
import requests
from pprint import pprint
from lxml import etree 

from newslynx_core.urls.parse_url import (
  prepare_url, get_domain
  )
from newslynx_core.articles.extraction.html import (
  get_html, strip_tags 
  )
from newslynx_core.articles.article import Article
from newslynx_core import settings

class ArticleExtractorInitializationError(Exception):
  pass

class ArticleExtractor:
  """
  multi-method article extraction framework for NewsLynx.

  Our strategy is as follows:
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
    self.np_config = newspaper.Config()
    try:
      from goose import Goose 
    except ImportError:
      pass
    else:
      self.g = Goose({'browser_user_agent': settings.USER_AGENT})

  def _set_np_config(self):
    self.np_config = newspaper.Config()
    self.np_config.browser_user_agent = settings.USER_AGENT
    self.np_config.request_timeout = settings.REQUEST_TIMEOUT

  def extract_newspaper(self, url, html=None):
    """
    Extract an article with newspaper.
    unfortunately the author did not include 
    a raw_html option, so we'll just pass in 
    the url.

    NOTE: This is probably duplicitous since 
    newspaper is just built off of python-goose's 
    source code. 

    TODO: If we do use newspaper, we should abstract 
    out its parser rather than applying it's image / 
    metadata / video / title / author extraction methods 
    as well.
    """
    np_article = newspaper.Article(url = url, config=self.np_config)
    np_article.build()
    return np_article
    # return np_article.article_html

  def extract_goose(self, html):
    """
    Extract an article with goose.
    """
    g_article = self.g.extract(raw_html = html)
    return g_article
    #return etree.tostring(g_article.top_node)

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
    we're just wrapping newspaper's Article.build()
    """
    if 'url' not in kwargs:
      raise ArticleExtractorInitializationError(
        'extract requires a url!'
      )
    # get the url 
    url = kwargs.get('url')
    # # TK extract html 
    # html = get_html(url)

    # for now we're just using newspaper 
    np_article = self.extract_newspaper(url=url)

    # initialize an Article object
    article = Article(url = url)

    # populate Article from newspaper Article 
    article.from_newspaper(np_article)

    # return an Article object
    return article

if __name__ == '__main__':
  url = 'http://www.nytimes.com/2014/05/04/fashion/Jason-Patric-Does-Sperm-Donor-Mean-Dad-parental-rights.html'
  a = ArticleExtractor()
  article = a.extract(url=url)
  pprint(article.to_json())


