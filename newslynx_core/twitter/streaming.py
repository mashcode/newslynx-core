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
    print data
    data = twp.parse(data)
    pprint(data)

  def on_error(self, status_code, data):
      print status_code

class TwitterStream:
  def __init__(self, **kwargs):
    self.stream = StreamHandler(
      settings.TWT_API_KEY, 
      settings.TWT_API_SECRET,
      settings.TWT_ACCESS_TOKEN,
      settings.TWT_ACCESS_SECRET
    ) 
    self.terms = kwargs.get('terms')
    self.filter_level = kwargs.get('filter_level', None)

  def run(self):
    self.stream.statuses.filter(
      track=self.terms, 
      filter_level=self.filter_level
      )

if __name__ == '__main__':
  ts = TwitterStream(terms=[
    'propublica org', 'propub ca', 'ny chalkbeat org', 'tn chalkbeat org',
    'motherjones com', 'mojo ly', 'co chalkbeat org', 'invw org', 
    'ckbe at', 'in chalkbeat org', 'publicintegrity org', 'yo'
    ])
  ts.run()
  


  
