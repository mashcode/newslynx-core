#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parser
from newslynx_core.twitter.parse_stream import (
  TwitterStreamParser
  )
from newslynx_core.fixtures.organizations import ORGANIZATIONS
class twitter_stream:
  organizations = ORGANIZATIONS
  def run(self):
    terms = set()
    for o in self.organizations:
      for query in o['twitter_searches']:
        terms.add(query)
    p = TwitterStreamParser(terms=list(terms))
    p.run()

if __name__ == '__main__':
  ts = twitter_stream()
  ts.run()
