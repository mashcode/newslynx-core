from newslynx_core.parsers.parse_url import (
  valid_url, get_simple_domain, prepare_url,
  is_abs_url
  )
import lxml.html 
from urlparse import urljoin

class URLExtractor:
  def __init__(self, **kwargs):
    self.domain = kwargs.get('domain')
    self.simple_domain = get_simple_domain(self.domain)

  def extract(self, html, text=None):
    
    intenal_links = set()
    external_links = set()

    tree = lxml.html.fromstring(html)

    for href in tree.xpath('//a/@href'):
      if not is_abs_url(href):
        href = urljoin(self.domain, href)
      if valid_url(href):
        if (self.domain in href or self.simple_domain in href) \
            and href != self.domain:
          intenal_links.add(prepare_url(href))
          
        else:
          external_links.add(prepare_url(href))

    return list(intenal_links), list(external_links)



