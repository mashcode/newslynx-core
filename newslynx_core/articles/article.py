#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.utils.serialization import jsonify
from newslynx_core.articles.extraction.html import node_to_string
from newslynx_core.urls.parse_url import (
  prepare_url, get_domain, url_to_slug, url_to_hash, 
  reconcile_embed_url
  )

class ArticleInitializationError(Exception):
  pass

class Article:
  """
  An article object containing all possible 
  attributes we might want to extract. 

  Includes:
  # NewsLynx Attributes #
  - TK NewsLynx news source ID

  # URL Attributes #
  - url
    * canonical-ized
  - domain
    * generated from url / 
      potentially passed in as a NewsLynx attribute. 
  - slug
    * potentially used for naming/linking files in manta.
  - hash
    * potentially used for naming/linking files in manta.

  # Page Attributes #
  - raw html
  - metadata
    * meta_keywords 
    * meta_description 
    * meta_lang 
    * meta_favicon 

  # Article Attributes #
  - title
    * passed in from RSS feed or article extraction.
  - authors
    * passed in from a RSS feed or article extraction.
  - publish datetime
    * passed in from a RSS feed or set 
      when we first parse the story.
  - publish date
    * passed in from a RSS feed or set 
      when we first parse the story. 
  - TK local publish datetime / date 
    * here, we'll probaly want standardize publish
      dates to the time zone of the news source.
  - keywords 
    * Article keywords determined via nlp.
      Right now we're just using newspaper's 
      built-in functionality 
  - top image 
    * The image to display on article dashboard.
      Once again, we're piggy-backing off of 
      newspaper, which extracted this functionality
      from reddit's source code.
  - images 
    * A list of all article-related images 
      on the page.
  - movies 
    * A list of all movies on the page.
  - text 
    * The clean, pristine article text.
  - article_html.
    * The raw html of the article node 
      determined via extraction method.

  For now, most of these will be passed in from 
  newspaper's output.
  """
  
  def __init__(self, **kwargs):
    """
    An Article object will be initilized 
    with just the url for now. 

    Eventually, we'll probably want to pass in 
    some global NewsLynx attributes as well.
    """
    if 'url' not in kwargs:
      raise ArticleInitializationError(
        'An Article object must be initilized'
        'with an url!'
      )

    # TK newslynx-level attributes 
    self.source_id = kwargs.get('source_id', None)

    # url-based attributes 
    self.url = prepare_url(kwargs.get('url'))
    self.domain = get_domain(self.url)
    self.slug = url_to_slug(self.url)
    self.hash = url_to_hash(self.url)
    
    # page-level attributes 
    self.page_html = u''

    # metadata
    self.meta_keywords = []
    self.meta_description = u''
    self.meta_lang = u''
    self.meta_favicon = u''

    # article-level attributes 
    self.title = u''
    self.authors = []
    self.pub_datetime = None
    self.pub_date = None 
    self.local_pub_datetime = None 
    self.local_pub_date = None 
    self.keywords = []  # keywords extracted via nlp from the body text 
    self.top_img = u''
    self.imgs = [] # all image urls
    self.movies = [] # youtube, vimeo, etc
    self.text = u''
    self.article_html = u''

  def to_json(self):
    """
    turn an Article object into json.
    """
    return jsonify(self.to_dict())

  def to_dict(self):
    """
    turn an Article object into a dict.
    """
    return self.__dict__

  def from_newspaper(self, np_article):
    """
    Map the attributes of a newspaper Article object 
    to our Article object. 

    We'll overwrite the url attributes set 
    at initialization because newspaper's url 
    should be where the page actually is.
    """
    # url-based attributes 
    self.url = np_article.url
    self.domain = get_domain(self.url)
    self.slug = url_to_slug(self.url)
    self.hash = url_to_hash(self.url)
    
    # page-level attributes 
    self.page_html = np_article.html
    # metadata
    self.meta_keywords = np_article.meta_keywords
    self.meta_description = np_article.meta_description
    self.meta_lang = np_article.meta_lang
    self.meta_favicon = np_article.meta_favicon

    # article-level attributes 
    self.title = np_article.title
    self.authors = np_article.authors
    self.keywords = np_article.keywords
    self.imgs = np_article.imgs 
    self.text = np_article.text
    self.article_html = node_to_string(np_article.top_node)

    # Various hacks:
    # check for stupid 'None' output.
    if np_article.top_img == 'None' or not np_article.top_img:
      self.top_img = u''
    else:
      self.top_img = np_article.top_img
    
    # reconcile movies from embed codes
    if len(np_article.movies) > 0:
      for m in np_article.movies:
        self.movies.append(reconcile_embed_url(m))


