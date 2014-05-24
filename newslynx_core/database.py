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
facebook_posts = db['facebook_posts']
facebook_page_stats = db['facebook_page_stats']
facebook_insights = db['facebook_insights']
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
  articles.create_column('pub_datetime',     DateTime)
  articles.create_column('pub_date',         Date) 
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

  # TWITTER
  # Tweets
  twitter.create_column('twitter_id',        String)
  twitter.create_column('list_slug',         String)
  twitter.create_column('list_owner',        String)
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
  
  # FACEBOOK
  # Posts #
  facebook_posts.create_column('org_id', String)
  facebook_posts.create_column('page_id', String)
  facebook_posts.create_column('post_id', String)
  facebook_posts.create_column('urls', postgresql.ARRAY(String))
  facebook_posts.create_column('datetime', DateTime)
  facebook_posts.create_column('message', String)
  facebook_posts.create_column('description', String)
  facebook_posts.create_column('status_type', String)
  facebook_posts.create_column('type', String)

  # Page Stats
  facebook_page_stats.create_column('org_id', String)
  facebook_page_stats.create_column('page_stats_id', String)
  facebook_page_stats.create_column('page_id', String)
  facebook_page_stats.create_column('page_talking_about_count', Numeric)
  facebook_page_stats.create_column('page_likes', String)
  facebook_page_stats.create_column('datetime', DateTime)

  # Insights
  facebook_insights.create_column('insights_id', String)
  facebook_insights.create_column('org_id', String)
  facebook_insights.create_column('page_id', String)
  facebook_insights.create_column('post_id', String)
  facebook_insights.create_column('datetime', DateTime)


  # create_indices = [
  # ]
  # for c_idx in create_indices:
  #   try:
  #     db.query(c_idx)
  #   except ProgrammingError:
  #     continue

if __name__ == '__main__':
  generate_schema()

