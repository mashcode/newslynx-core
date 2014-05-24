#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twython import Twython
from newslynx_core import settings

def connect(**kwargs):
  """
  Given 4 Environmental Variables, Connect to Twitter
  """
  
  # load credentials
  api_key = kwargs.get('api_key', settings.TWT_API_KEY)
  api_secret = kwargs.get('api_secret', settings.TWT_API_SECRET)
  oauth_token = kwargs.get('oauth_token', settings.TWT_ACCESS_TOKEN)
  oauth_secret = kwargs.get('oauth_secret', settings.TWT_ACCESS_SECRET)
  access_token = kwargs.get('access_token', None)

  api = Twython(
    app_key = api_key,
    app_secret = api_secret,
    oauth_token = oauth_token,
    oauth_token_secret = oauth_secret,
    access_token = access_token
    )

  # authenticate
  return api