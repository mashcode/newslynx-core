from twython import TwythonStreamer
import twython

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

class MyStreamer(TwythonStreamer):
  def on_success(self, data):
    if 'text' in data:
        pprint(data)

  def on_error(self, status_code, data):
      print status_code

"""
{u'contributors': None,
 u'coordinates': None,
 u'created_at': u'Mon May 12 01:25:00 +0000 2014',
 u'entities': {u'hashtags': [],
               u'symbols': [],
               u'urls': [{u'display_url': u'propub.ca/1qn879w',
                          u'expanded_url': u'http://propub.ca/1qn879w',
                          u'indices': [11, 33],
                          u'url': u'http://t.co/2zjW4cLMeK'}],
               u'user_mentions': []},
 u'favorite_count': 0,
 u'favorited': False,
 u'filter_level': u'medium',
 u'geo': None,
 u'id': 465663903671009281,
 u'id_str': u'465663903671009281',
 u'in_reply_to_screen_name': None,
 u'in_reply_to_status_id': None,
 u'in_reply_to_status_id_str': None,
 u'in_reply_to_user_id': None,
 u'in_reply_to_user_id_str': None,
 u'lang': u'en',
 u'place': None,
 u'possibly_sensitive': False,
 u'retweet_count': 0,
 u'retweeted': False,
 u'source': u'<a href="https://about.twitter.com/products/tweetdeck" rel="nofollow">TweetDeck</a>',
 u'text': u'short link http://t.co/2zjW4cLMeK',
 u'truncated': False,
 u'user': {u'contributors_enabled': False,
           u'created_at': u'Sun Mar 30 22:04:45 +0000 2014',
           u'default_profile': False,
           u'default_profile_image': False,
           u'description': None,
           u'favourites_count': 0,
           u'follow_request_sent': None,
           u'followers_count': 37,
           u'following': None,
           u'friends_count': 9,
           u'geo_enabled': False,
           u'id': 2419585021,
           u'id_str': u'2419585021',
           u'is_translation_enabled': False,
           u'is_translator': False,
           u'lang': u'en',
           u'listed_count': 0,
           u'location': u'',
           u'name': u'NewsLynx',
           u'notifications': None,
           u'profile_background_color': u'FFFFFF',
           u'profile_background_image_url': u'http://abs.twimg.com/images/themes/theme1/bg.png',
           u'profile_background_image_url_https': u'https://abs.twimg.com/images/themes/theme1/bg.png',
           u'profile_background_tile': False,
           u'profile_image_url': u'http://pbs.twimg.com/profile_images/450660238094368770/aTwKIknx_normal.png',
           u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/450660238094368770/aTwKIknx_normal.png',
           u'profile_link_color': u'0838F7',
           u'profile_sidebar_border_color': u'FFFFFF',
           u'profile_sidebar_fill_color': u'DDEEF6',
           u'profile_text_color': u'333333',
           u'profile_use_background_image': False,
           u'protected': False,
           u'screen_name': u'newslynx',
           u'statuses_count': 4,
           u'time_zone': u'Atlantic Time (Canada)',
           u'url': u'http://newslynx.org',
           u'utc_offset': -10800,
           u'verified': False}}
"""

if __name__ == '__main__':
  
  stream = MyStreamer(
    settings.TWT_API_KEY, 
    settings.TWT_API_SECRET,
    settings.TWT_ACCESS_TOKEN,
    settings.TWT_ACCESS_SECRET)

  stream.statuses.filter(track=['propublica', 'propub ca', 'publicintegrity', 'ckbe at'], filter_level=None)
