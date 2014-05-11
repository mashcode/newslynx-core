import gevent
from gevent.queue import Queue
import gevent.monkey
gevent.monkey.patch_all()

from newslynx_core.feeds.parse_feed import FeedParser
from newslynx_core import ORGANIZATIONS

from pprint import pprint


class FeedPoller:
  def __init__(self, **kwargs):
    self.organizations = ORGANIZATIONS # TODO: hook up to database
    self.num_workers = kwargs.get('num_workers', 10)
    self.tasks = Queue()

  def _feeder(self):
    for organization in self.organizations:
      # TODO: Make these objects
      org_id = organization['org_id']
      feed_urls = organization['rss_feeds']
      domain = organization['homepage']
      for feed_url in feed_urls:
        assignment = (feed_url, org_id, domain)
        self.tasks.put_nowait(assignment)

  def _parser(self):
    while not self.tasks.empty():
      assignment = self.tasks.get()
      feed_url, org_id, domain = assignment
      fp = FeedParser(feed_url=feed_url, org_id=org_id, domain=domain)
      fp.run()
      gevent.sleep(0)

  def poll(self):
    gevent.spawn(self._feeder).join()
    gevent.joinall([
        gevent.spawn(self._parser) 
          for w in xrange(self.num_workers)
    ])

  def debug(self):
    for organization in self.organizations:
      org_id = organization['org_id']
      feed_urls = organization['rss_feeds']
      domain = organization['homepage']
      for feed_url in feed_urls:
        fp = FeedParser(
          feed_url = feed_url, 
          org_id   = org_id, 
          domain   = domain
          )
        fp.run()

if __name__ == '__main__':
  fp = FeedPoller()
  fp.poll()

