"""
Just runs all parsing methods for now,
TK unit tests 
"""

print "TESTING FEED PARSING / ARTICLE EXTRACTION ..."
from newslynx_core.feeds.parse_feed import FeedParser
feed_url = 'http://feeds.propublica.org/propublica/main?format=xml'
fp = FeedParser(feed_url = feed_url, org_id = 'propublica', domain = 'http://www.propublica.org/')
fp.run()

print "TESTING GALERTS PARSING ..."
from newslynx_core.alerts.parse_galert import GAlertParser
feed_url = 'http://www.google.com/alerts/feeds/14752688329844321840/4874425503898649357'
ga = GAlertParser(feed_url = feed_url, org_id = 'propublica', domain='http://www.propublica.org')
ga.run()

print "TESTING FACEBBOOK PAGE PARSING ..."
from newslynx_core.facebook.parse_page import FacebookPageParser
fbpp = FacebookPageParser(org_id='propublica', page_id='propublica')
fbpp.run()

print "TESTING FACEBBOOK PAGE STATS PARSING ..."
from newslynx_core.facebook.parse_page_stats import FacebookPageStats
fbpp = FacebookPageStats(org_id='propublica', page_id='propublica')
fbpp.run()

print "TESTING HOMEPAGE PARSING ..."
from newslynx_core.homepages.parse_homepage import HomepageParser
hp = HomepageParser(org_id = 'propublica', homepage = 'http://www.propublica.org/')
hp.run()

print "TESTING TWITTER LIST PARSING ... "
from newslynx_core.twitter.parse_list import TwitterListParser
tlp = TwitterListParser(list_owner = 'propublica', list_name = 'propublica-staff')
tlp.run()

print "TESTING TWITTER USER STATS PARSING ... "
from newslynx_core.twitter.parse_user_stats import TwitterUserStatsParser
tusp = TwitterUserStatsParser(org_id = 'propublica', screen_name = 'propublica')
tusp.run()

print "TESTING TWITTER USER TIMELINE PARSING ... "
from newslynx_core.twitter.parse_user import TwitterUserParser
tup = TwitterUserParser(org_id = 'propublica', screen_name = 'propublica')
tup.run()

print "TESTING TWITTER STREAM PARSING ... "
from newslynx_core.twitter.parse_stream import TwitterStreamParser 
ts = TwitterStreamParser(terms=[
  'propublica org', 'propub ca', 'ny chalkbeat org', 'tn chalkbeat org',
  'motherjones com', 'mojo ly', 'co chalkbeat org', 'invw org', 
  'ckbe at', 'in chalkbeat org', 'publicintegrity org', 'hello'
  ])
print ts.run()





