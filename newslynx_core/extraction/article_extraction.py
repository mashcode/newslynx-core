#!/usr/bin/env python
# -*- coding: utf-8 -*-

from boilerpipe.extract import Extractor
from readability.readability import Document
import requests

def extract_article(url):
  
  r = requests.get(url)
  
  # the the url exists, continue
  if r.status_code == 200:
    
    # extract and parse response url
    url = parse_url(r.url)

    # extract html
    html = r.content.decode('utf-8', errors='ignore')

    # run boilerpipe
    BP = Extractor(html=html)

    # run readability
    Rdb = Document(html)

    # return article data
    return {
      'extracted_title': Rdb.short_title().strip(),
      'extracted_content': strip_tags(BP.getText()),
      'extracted_html': Rdb.summary()
    }

  # otherwise return an empty dict
  else:
    return {
      'extracted_title': None,
      'extracted_content': None,
      'extracted_html': None
    }

if __name__ == '__main__':
  url = 'http://www.nytimes.com/2014/05/04/fashion/Jason-Patric-Does-Sperm-Donor-Mean-Dad-parental-rights.html'
  extract_article(url)
