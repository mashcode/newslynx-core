#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from datetime import datetime, timedelta
import pytz

from newslynx_core import settings

# jobs will always 
# be running on us-east ?
local_tz = pytz.timezone(settings.LOCAL_TZ)
UTC = pytz.timezone('UTC')

date_regex = re.compile(r"""
  ([\./\-_]{0,1}(19|20)\d{2}) # year
  [\./\-_]{0,1} # separator
  (([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_])) # month/date/section
  ([0-3]{0,1}[0-9][\./\-]{0,1})? # ?
""", flags = re.VERBOSE)

def time_to_datetime(ts):
  """
  convert time to datetime obj
  """
  return datetime.fromtimestamp(time.mktime(ts))

def get_tz(tz=None):
  """
  build pytz object, 
  default to EST
  """
  if tz:
    return pytz.timezone(tz)
  else:
    return local_tz 

def current_local_datetime(tz):
  # utc_now
  dt = datetime.now()
  return dt.replace(tzinfo=local_tz)
  # # localize
  # return localize_datetime(dt)

def current_timestamp():
  return int(datetime.now().strftime('%s'))

def localize_datetime(dt):
  """
  localize a tz-aware datetime object 
  from one timezone to another timezone.
  """  
  # normalize
  to_tz = get_tz(local_tz)
  return to_tz.normalize(dt.astimezone(to_tz))
