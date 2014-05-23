# this should accept a feed_url from stdin, I think and output a list of URLs
# (potentially after having checked if they're already present)
feed_url = '?'
fp = FeedParser(feed_url = feed_url, org_id = 'publicintegrity', domain = 'http://www.publicintegrity.org/')
fp.run()
