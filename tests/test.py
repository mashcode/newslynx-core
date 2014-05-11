from newslynx_core.extractors.extract_article import ArticleExtractor
from newslynx_core.extractors.extract_author import AuthorExtractor
from newslynx_core.extractors.extract_image import ImageExtractor
from newslynx_core.feeds.parse_feed import FeedParser
from newslynx_core.feeds.build_feed import FeedBuilder
# from newslynx_core import organizations

from pprint import pprint

def test_article_extraction():
  from pprint import pprint
  url = 'http://www.nytimes.com/2014/05/04/fashion/Jason-Patric-Does-Sperm-Donor-Mean-Dad-parental-rights.html'
  ax = ArticleExtractor()
  article = ax.extract(url=url)

def pro_plutionium():
  feed_url = 'http://feeds.feedburner.com/motherjones/BlogsAndArticles?format=xml'
  fp = FeedParser(feed_url = feed_url)
  fp.run()

if __name__ == '__main__':
  pro_plutionium()
 
