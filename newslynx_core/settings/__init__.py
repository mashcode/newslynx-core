#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Global Settings for newslynx-core should go in here.
"""
import re
import os
import newspaper
import logging
from datetime import timedelta

# suppress requests logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.ERROR)

# POSTGRESQL
DATABASE_URL = os.getenv('NEWSLYNX_DB_URL')

# Facebook API
FB_APP_ID = os.getenv('NEWSLYNX_FB_APP_ID')
FB_APP_SECRET = os.getenv('NEWSLYNX_FB_APP_SECRET')
FB_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+0000"

# Twitter API
TWT_API_KEY = os.getenv('NEWSLYNX_TWT_API_KEY')
TWT_API_SECRET = os.getenv('NEWSLYNX_TWT_API_SECRET')
TWT_ACCESS_TOKEN = os.getenv('NEWSLYNX_TWT_ACCESS_TOKEN')
TWT_ACCESS_SECRET = os.getenv('NEWSLYNX_TWT_ACCESS_SECRET')
TWT_DATE_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'

# AWS API
AWS_ACCESS_KEY_ID = os.getenv('NEWSLYNX_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('NEWSLYNX_AWS_SECRET_ACCESS_KEY')
AWS_S3_STOR = os.getenv('NEWSLYNX_S3_STOR')

HOMEPAGE_BUCKET_PIXELS = 50

# SET EXPIRATION
SET_EXPIRES = timedelta(days=30)

# GEVENT TASK QUEUE SIZE
GEVENT_QUEUE_SIZE = 8

# requests settings 
USER_AGENT = "NewsLynx | (Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_1) AppleWebKit/534.48.3 (KHTML, like Gecko) Version/5.1 Safari/534.48.3)"
REQUEST_TIMEOUT = 15

# date settings 
LOCAL_TZ = 'EST'

# article regexes we already know
KNOWN_ARTICLE_REGEX = re.compile(r"""
  (.*propublica.org/[a-z]+/[a-z0-9/-]+)|
""", re.VERBOSE)

# parsing settings
NEWSPAPER_CONFIG = newspaper.Config()
NEWSPAPER_CONFIG.browser_user_agent = USER_AGENT
NEWSPAPER_CONFIG.request_timeout = REQUEST_TIMEOUT
NEWSPAPER_CONFIG.keep_article_html = True
NEWSPAPER_CONFIG.fetch_images = True
NEWSPAPER_CONFIG.MIN_WORD_COUNT = 200

# url settings
MAX_UNSHORTEN_ATTEMPTS = 5


