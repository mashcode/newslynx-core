"""
Global Settings for newslynx-core should go in here.
"""
import re
import newspaper
import logging
from datetime import timedelta

# suppress requests logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.ERROR)

# requests settings 
USER_AGENT = "NewsLynx | (Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_1) AppleWebKit/534.48.3 (KHTML, like Gecko) Version/5.1 Safari/534.48.3)"
REQUEST_TIMEOUT = 15

# POSTGRESQL
DATABASE_URL = 'postgresql://brian:brian@localhost:5432/newslynx_core'

# SET EXPIRATION
SET_EXPIRES = timedelta(days=30)

# GEVENT TASK QUEUE SIZE
GEVENT_QUEUE_SIZE = 10

# parsing settings
NEWSPAPER_CONFIG = newspaper.Config()
NEWSPAPER_CONFIG.browser_user_agent = USER_AGENT
NEWSPAPER_CONFIG.request_timeout = REQUEST_TIMEOUT
NEWSPAPER_CONFIG.keep_article_html = True
NEWSPAPER_CONFIG.fetch_images = True
NEWSPAPER_CONFIG.MIN_WORD_COUNT = 200


# url settings
MAX_UNSHORTEN_ATTEMPTS = 5

# date settings 
LOCAL_TZ = 'EST'

# article regexes we already know
KNOWN_ARTICLE_REGEX = re.compile(r"""
  (.*\.nytimes\.com/(.*/)?[0-9]+/[0-9]+/[0-9]+/.*)|
  (.*propublica.org/[a-z]+/[a-z0-9/-]+)|
""", re.VERBOSE)