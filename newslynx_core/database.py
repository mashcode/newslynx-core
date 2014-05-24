#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dataset
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Integer, Numeric, String, DateTime, Date
from sqlalchemy.exc import ProgrammingError

from newslynx_core import settings

# connect to database and table
db_url = settings.DATABASE_URL
db = dataset.connect(db_url)

#tables
articles = db['articles']
galerts = db['galerts']
twitter = db['twitter']
twitter_user_stats = db['twitter_user_stats']
facebook_posts = db['facebook_posts']
facebook_page_stats = db['facebook_page_stats']
facebook_insights = db['facebook_insights']
homepages = db['homepages']

def create_index(table, column):
  idx = "idx_%s_%s" % (table, column)
  q = """CREATE INDEX %s ON %s (%s);""" % (idx, table, column)
  db.query(q)

def ensure_schema():

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
  twitter.create_column('org_id',            String)
  twitter.create_column('query',             String)
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

  #User Stats
  twitter_user_stats.create_column('user_stats_id',   String)
  twitter_user_stats.create_column('org_id',          String)
  twitter_user_stats.create_column('datetime',        DateTime)
  twitter_user_stats.create_column('screen_name',     String)
  twitter_user_stats.create_column('favorites',       Numeric)
  twitter_user_stats.create_column('followers',       Numeric) 
  twitter_user_stats.create_column('friends',         Numeric) 
  twitter_user_stats.create_column('listed',          Numeric)
  twitter_user_stats.create_column('statuses',        Numeric) 
  
  # FACEBOOK
  # Posts #
  facebook_posts.create_column('org_id',              String)
  facebook_posts.create_column('page_id',             String)
  facebook_posts.create_column('post_id',             String)
  facebook_posts.create_column('urls',                postgresql.ARRAY(String))
  facebook_posts.create_column('datetime',            DateTime)
  facebook_posts.create_column('message',             String)
  facebook_posts.create_column('description',         String)
  facebook_posts.create_column('status_type',         String)
  facebook_posts.create_column('type',                String)

  # Page Stats
  facebook_page_stats.create_column('org_id',String)
  facebook_page_stats.create_column('page_stats_id',String)
  facebook_page_stats.create_column('page_id',String)
  facebook_page_stats.create_column('page_talking_about_count',Numeric)
  facebook_page_stats.create_column('page_likes',String)
  facebook_page_stats.create_column('datetime',DateTime)

  # Insights
  facebook_insights.create_column('insights_id', String)
  facebook_insights.create_column('org_id', String)
  facebook_insights.create_column('page_id', String)
  facebook_insights.create_column('post_id', String)
  facebook_insights.create_column('datetime', DateTime)


  # TODO Explicit definitions for stats


  # indices = {
  #}
  # for k,v in indices:
  #   try:
  #     create_index(k, v)
  #   except ProgrammingError:
  #     continue


  # create histogram function
  psql_histogram  = """
  CREATE OR REPLACE FUNCTION hist_sfunc (state INTEGER[], val REAL, min REAL, max REAL, nbuckets INTEGER) RETURNS INTEGER[] AS $$
  DECLARE
    bucket INTEGER;
    i INTEGER;
  BEGIN
    bucket := width_bucket(val, min, max, nbuckets - 1) - 1;
   
    IF state[0] IS NULL THEN
      FOR i IN SELECT * FROM generate_series(0, nbuckets - 1) LOOP
        state[i] := 0;
      END LOOP;
    END IF;
   
    state[bucket] = state[bucket] + 1;
   
    RETURN state;
  END;
  $$ LANGUAGE plpgsql IMMUTABLE;
   
  DROP AGGREGATE IF EXISTS histogram (REAL, REAL, REAL, INTEGER);
  CREATE AGGREGATE histogram (REAL, REAL, REAL, INTEGER) (
         SFUNC = hist_sfunc,
         STYPE = INTEGER[]
  );
  """
  db.query(psql_histogram)

  psql_median = """
  CREATE OR REPLACE FUNCTION _final_median(numeric[])
     RETURNS numeric AS
  $$
     SELECT AVG(val)
     FROM (
       SELECT val
       FROM unnest($1) val
       ORDER BY 1
       LIMIT  2 - MOD(array_upper($1, 1), 2)
       OFFSET CEIL(array_upper($1, 1) / 2.0) - 1
     ) sub;
  $$
  LANGUAGE 'sql' IMMUTABLE;
   
  DROP AGGREGATE IF EXISTS median(numeric);
  CREATE AGGREGATE median(numeric) (
    SFUNC=array_append,
    STYPE=numeric[],
    FINALFUNC=_final_median,
    INITCOND='{}'
  );
  """
  try:
    db.query(psql_median)
  except ProgrammingError:
    pass

  psql_rm_null = """
  CREATE OR REPLACE FUNCTION array_rm_null(anyarray)
  RETURNS anyarray AS $$
    SELECT ARRAY( SELECT DISTINCT t2.v2 FROM (SELECT t1.v1 as v2 FROM (SELECT unnest($1) as v1) t1 WHERE t1.v1 IS NOT NULL) t2)
  $$ LANGUAGE sql;
  """

  try:
    db.query(psql_rm_null)
  except ProgrammingError:
    pass

  psql_array_reverse = """
  CREATE OR REPLACE FUNCTION array_reverse(anyarray) RETURNS anyarray AS $$
  SELECT ARRAY(
      SELECT $1[i]
      FROM generate_series(
          array_lower($1,1),
          array_upper($1,1)
      ) AS s(i)
      ORDER BY i ASC
  );
  $$ LANGUAGE 'sql' STRICT IMMUTABLE;
  """

  try:
    db.query(psql_array_reverse)
  except ProgrammingError:
    pass

def gen_db():
  db_name = db_url.split('/')[-1]
  try:
    db.query('drop database %s;' % db_name)
  except ProgrammingError:
    db.query('create database %s;' % db_name)
  else:
    db.query('create database %s;' % db_name)

if __name__ == '__main__':
  import sys
  if len(sys.argv) != 0:
    if sys.argv[0] == 'init':
      gen_db()

  ensure_schema()

