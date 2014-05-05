#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.utils.serialization import jsonify
from newslynx_core.parsers.parse_url import (
  prepare_url, get_domain, url_to_slug, url_to_hash, 
  reconcile_embed_url, get_simple_domain
  )
from pprint import pprint 

class ArticleInitError(Exception):
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
  - simple_domain
    * generated from domain, ie nytimes.com > nytimes
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
      raise ArticleInitError(
        'An Article object must be initilized'
        'with an url!'
      )

    # TK newslynx-level attributes 
    self.source_id          = kwargs.get('source_id', None)

    # url-based attributes 
    self.url                = prepare_url(kwargs.get('url'))
    self.domain             = get_domain(self.url)
    self.simple_domain      = get_simple_domain(self.url)
    self.slug               = url_to_slug(self.url)
    self.hash               = url_to_hash(self.url)
    
    # page-level attributes 
    self.page_html          = None

    # metadata
    self.meta_keywords      = set()
    self.meta_description   = None
    self.meta_lang          = None
    self.meta_favicon       = None
    # self.tags = []

    # article-level attributes 
    self.title             = u''
    self.authors           = set()
    self.pub_datetime      = None
    self.pub_date          = None 
    # self.local_pub_datetime = None 
    # self.local_pub_date = None 
    self.keywords          = set()  # keywords extracted via nlp from the body text 
    self.img               = None
    self.image             = None
    self.img_urls          = set() # all image urls
    self.thumb             = None
    self.movies            = set() # youtube, vimeo, etc
    self.text              = None
    self.article_html      = None


  def from_newspaper(self, np_article, merge=False):
    """
    Map the attributes of a newspaper Article object 
    to our Article object. There's probably a more succint 
    way of doing this...
    class inheritance maybe ?
    """
    # url-based attributes #

    # We'll overwrite the url attributes set 
    # at initialization because newspaper's url 
    # should be where the page actually is.
    self.set_url(              np_article.url )
    self.domain = get_domain(  self.url )
    self.simple_domain =       get_simple_domain( self.url )
    self.slug = url_to_slug(   self.url )
    self.hash = url_to_hash(   self.url )
    
    # metadata
    self.set_meta_keywords(     np_article.meta_keywords )
    self.set_meta_description(  np_article.meta_description )
    self.set_meta_lang(         np_article.meta_lang )
    self.set_meta_favicon(      np_article.meta_favicon )
    self.set_keywords(          np_article.keywords )
    self.set_movies(            np_article.movies )

    # try to get images
    img = None
    try:
      img = np_article.top_img
    except AttributeError:
      pass
    try:
      img = np_article.image
    except AttributeError:
      pass
    try:
      img = np_article.img
    except AttributeError:
      pass
    finally:
      if img:
        self.set_img_urls( img)

    # merging logic
    if merge:

      # update if extracted text is longer
      if len(self.text) < np_article.text:

        self.set_text(          np_article.text )
        self.set_article_html(  np_article.article_html )

      # update img if there is none
      if (not self.img and  img):

        self.set_img(           img )

    else:
      self.set_text(            np_article.text )
      self.set_article_html(    np_article.article_html )
      self.set_img(             np_article.top_img )

    return self
    

  def set_url(self, title):
    self.title = title 

  def set_title(self, title):
    self.title = title 

  def set_page_html(self, page_html):
    self.page_html = page_html

  def set_article_html(self, article_html):
    self.article_html = article_html

  def set_text(self, text):
    self.text = text 

  def set_dates(self, dt):
    if dt:
      self.pub_date = dt.date()
      self.pub_datetime = dt 

  def set_updated(self, dt):
    if dt:
      self.updated_dateime = dt 
      self.updated_date = dt.date()

  def set_img_urls(self, img_urls):
    if img_urls:
      if isinstance(img_urls, list):
        for i in img_urls: self.img_urls.add(i)
      elif isinstance(img_urls, str):
        self.img_urls.add(img_urls)

  def set_thumb(self, thumb):
    self.thumb = thumb 

  def set_authors(self, authors):
    if authors:
      for a in authors: 
        self.authors.add(a)

  def set_img(self, img):
    if img and img not in ['None', '']:
      self.img = img

  def set_meta_keywords(self, meta_keywords):
    for m in meta_keywords: 
      self.meta_keywords.add(m)

  def set_meta_description(self, meta_description):
    self.meta_description = meta_description

  def set_meta_lang(self, meta_lang):
    self.meta_lang = meta_lang 

  def set_meta_favicon(self, meta_favicon):
    self.meta_favicon = meta_favicon

  def set_keywords(self, keywords):
    if keywords:
      for k in keywords: 
        self.keywords.add(k)

  def set_movies(self, movies):
    if movies:
      for m in movies: 
        self.movies.add(m)

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

