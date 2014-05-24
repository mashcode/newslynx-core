#!/usr/bin/env python
# -*- coding: utf-8 -*-

from newslynx_core.parsers.parse_url import (
  is_short_url, unshorten_url, prepare_url, 
  url_to_slug, get_domain, get_simple_domain,
  valid_url
  )
from newslynx_core import settings
from datetime import datetime

# mapping of tweet schema to newslynx schema
# via jsonpath

class TweetParser:
  def __init__(self, **kwargs):
    # options for identifyting links to content.
    self.domain = kwargs.get('domain', None)
    self.short_url = kwargs.get('short_url', None)

  def get_url_candidates(self, e):
    candidates = set()
    for url in e.get('urls', []):
      if url:
        candidates.add(url['expanded_url'])
    return list(candidates)

  def parse_url(self, url):
    """
    unshorten and/or normalize url.
    """
    if is_short_url(url, self.short_url):
       return prepare_url(unshorten_url(url))
    else:
      return prepare_url(url)

  def get_urls(self, e):
    urls = set()
    candidates = self.get_url_candidates(e)
    if len(candidates)==0:
      return []
    for url in candidates:
      urls.add(self.parse_url(url))
    return list(urls)

  def get_datetime(self, tweet):
    return datetime.strptime(tweet['created_at'], settings.TWT_DATE_FORMAT)

  def get_hashtags(self, e):
    hashtags = set()
    candidates = e.get('hashtags', [])
    if len(candidates) == 0:
      return []
    for c in candidates:
      hashtags.add(c.get('text'))
    return list(hashtags)

  def get_user_mentions(self, e):
    mentions = set()
    candidates = e.get('user_mentions', [])
    if len(candidates) == 0:
      return []
    for c in candidates:
      mentions.add(c['screen_name'])
    return list(mentions)

  def get_img_urls(self, e):
    img_urls = set()
    media = e.get('media', [])
    for m in media:
      if m:
        img_urls.add(m.get('expanded_url'))
    return list(img_urls)

  def get_user_data(self, tweet):
    user = tweet.get('user', {})
    return {
      'screen_name': user.get('screen_name', None),
      'followers': user.get('followers_count', None),
      'friends': user.get('friends_count', None),
      'profile_img': user.get('profile_image_url', None),
      'verified': 1 if user.get('verified', False) else 0 # convert bool
    }

  def parse(self, tweet):
    # set basic values
    output = {
      'twitter_id': tweet.get('id_str', None),
      'text': tweet.get('text', '').encode('utf-8'),
      'retweets': tweet.get('retweet_count', 0),
      'datetime': self.get_datetime(tweet),
      'favorites': tweet.get('favorites_count', 0),
      'in_reply_to_screen_name': tweet.get('in_reply_to_screen_name'),
      'in_reply_to_status_id': tweet.get('in_reply_to_status_id_str')
    }
    # lists
    e = tweet.get('entities', {})
    output['urls'] = self.get_urls(e)
    output['hashtags'] = self.get_hashtags(e)
    output['user_mentions'] = self.get_user_mentions(e)
    output['img_urls'] = self.get_img_urls(e)
    
    # user data
    user = self.get_user_data(tweet)

    return dict(user.items() + output.items())


