from twython import TwythonStreamer
import twython

from newslynx_core.twitter.parse_tweet import (
  TweetParser
  )
from newslynx_core import settings

from pprint import pprint
"""
FROM 

Finally, to address a common use case where you may want to track 
all mentions of a particular domain name (i.e., regardless of 
subdomain or path), you should use "example com" as the track 
parameter for "example.com" (notice the lack of period between 
"example" and "com" in the track parameter). This will be over-inclusive, 
so make sure to do additional pattern-matching in your code. 
See the table below for more examples related to this issue.
"""

twp = TweetParser()

class StreamHandler(TwythonStreamer):
  def on_success(self, data):
    data = twp.parse(data)
    pprint(data)

  def on_error(self, status_code, data):
      print status_code

if __name__ == '__main__':
  
  stream = StreamHandler(
    settings.TWT_API_KEY, 
    settings.TWT_API_SECRET,
    settings.TWT_ACCESS_TOKEN,
    settings.TWT_ACCESS_SECRET)

  stream.statuses.filter(track=['hello', 'propub ca', 'publicintegrity', 'ckbe at'], filter_level=None)
