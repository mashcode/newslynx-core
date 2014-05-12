#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dataset
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Integer, Numeric, String, DateTime, Date
from sqlalchemy.exc import ProgrammingError

from newslynx_core import settings

# connect to database and table
db = dataset.connect(settings.DATABASE_URL)

#tables
articles = db['articles']
galerts = db['galerts']
twitter = db['twitter']
facebook = db['facebook']
homepages = db['homepages']


def generate_schema():

  # ARTICLES #

  # Strings 
  articles.create_column('org_id',           String)
  articles.create_column('url',              String)
  articles.create_column('domain',           String)
  articles.create_column('simple_domain',    String)
  articles.create_column('slug',             String)
  articles.create_column('hash',             String)
  articles.create_column('meta_description', String)
  articles.create_column('meta_lang',        String)
  articles.create_column('meta_favicon',     String)
  articles.create_column('img',              String)
  articles.create_column('thumb',            String)
  articles.create_column('text',             String)
  articles.create_column('article_html',     String)
  articles.create_column('title',            String)
  
  # Dates
  articles.create_column('pub_datetime',     DateTime)
  articles.create_column('pub_date',         Date) 

  # Arrays
  articles.create_column('meta_keywords',    postgresql.ARRAY(String))
  articles.create_column('authors',          postgresql.ARRAY(String))
  articles.create_column('int_links',        postgresql.ARRAY(String))
  articles.create_column('ext_links',        postgresql.ARRAY(String))
  articles.create_column('tags',             postgresql.ARRAY(String))
  articles.create_column('keywords',         postgresql.ARRAY(String))
  articles.create_column('img_urls',         postgresql.ARRAY(String))
  articles.create_column('movies',           postgresql.ARRAY(String))


  # GALERTS

  galerts.create_column('galert_id',         String) 
  galerts.create_column('feed_url',          String)       
  galerts.create_column('url',               String)            
  galerts.create_column('title',             String)           
  galerts.create_column('summary',           String)         
  galerts.create_column('datetime',          DateTime)

  # TWEETS
  twitter.create_column('twitter_id',        String)
  twitter.create_column('text',              String)
  twitter.create_column('profile_img',       String)
  twitter.create_column('screen_name',       String)
  twitter.create_column('in_reply_to_status_id', String)
  twitter.create_column('in_reply_to_screen_name', String)

  twitter.create_column('datetime',          DateTime)

  twitter.create_column('favorites',         Numeric)
  twitter.create_column('followers',         Numeric)
  twitter.create_column('friends',           Numeric)
  twitter.create_column('retweets',          Numeric)
  twitter.create_column('verified',          Numeric)
  twitter.create_column('hashtags',          postgresql.ARRAY(String))
  twitter.create_column('urls',              postgresql.ARRAY(String))
  twitter.create_column('user_mentions',     postgresql.ARRAY(String))
  twitter.create_column('img_urls',          postgresql.ARRAY(String))
  

  # TODO #
  # # generate indices
  # create_indices = [
  # ]
  # for c_idx in create_indices:
  #   try:
  #     db.query(c_idx)
  #   except ProgrammingError:
  #     continue

if __name__ == '__main__':
  generate_schema()

