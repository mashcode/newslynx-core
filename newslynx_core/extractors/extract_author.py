#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re 

from newslynx_core.parsers.parse_html import (
  strip_tags, string_to_doc
  )

class AuthorExtractor:
  def __init__(self, **kwargs):
    # Chunk the line by non alphanumeric tokens (few name exceptions)
    # >>> re.split("[^\w\'\-]", "Lucas Ou-Yang, Dean O'Brian and Ronald")
    # ['Lucas Ou-Yang', '', 'Dean O'Brian', 'and', 'Ronald'
    self.re_name_token = re.compile(r"[^\w\'\-\.]")

    # by / from
    self.re_by = re.compile(r'[bB][yY][\:\s]|[fF]rom[\:\s]')

    # initials
    self.re_initial = re.compile(r'^([A-Z](\.)?){1,2}$', re.IGNORECASE)
    self.initial_count = 0

    # prefix / suffix
    self.re_prefix_suffix = re.compile(r"""
      (^[Dd][Rr](\.)?$)|                   # Dr.
      (^[Mm](\.)?([Dd])(\.)?$)|            # MD
      (^[SsJj][Rr](\.)?$)|                 # SR / JR
      (^[Mm](iss)?([RrSs])?([Ss])?(\.)?$)| # Mr / Ms. / Mrs / Miss
      (^P(\.)?[Hh][Dd](\.)?)|              # PHD
      (^I(\.)?I(\.)?I(\.)?$)|              # III 
      (^I(\.)?V(\.)?$)|                    # IV
      (^V(\.)$)                            # V
    """, re.VERBOSE)

    # digits
    self.re_digits = re.compile('\d')

    # how long can a name  be?
    self.MIN_NAME_TOKENS = 2
    self.MAX_NAME_TOKENS = 4

    # what can a name be separated by?
    # delimeters
    self.DELIM = ['and', '']

    self.ATTRS = ['name', 'rel', 'itemprop', 'class', 'id']
    self.VALS = ['author', 'byline']

  def format_authors(self, _authors):
    authors = []
    uniq = list(set([s.lower().replace('.', '') for s in _authors]))

    for name in uniq:
      tokens = [
        w.upper() if self.re_initial.search(w) else w.title() 
          for w in name.split(' ') 
      ]
      authors.append(' '.join(tokens))

    return authors or []

  def match_initial(self, token):
    return self.re_initial.match(token) or self.re_prefix_suffix.match(token)

  def valid_initial(self, curname):
    """
    Only include an inital if we haven't passed
    the max name token range.
    """
    return (len(curname) < self.MAX_NAME_TOKENS + 1)

  def is_initial(self, curname, token):
    return  self.valid_initial(curname) or self.match_initial(token) 

  def end_name(self, curname):
    est_count = self.MIN_NAME_TOKENS + self.initial_count
    return (len(curname) == est_count)

  def from_string(self, search_str):
    """
    Takes a candidate line of html or text and
    extracts out the name(s) in list form
    >>> search_str('<div>By: <strong>Lucas Ou-Yang</strong>, \
                    <strong>Alex Smith</strong></div>')
    ['Lucas Ou-Yang', 'Alex Smith']
    """
    # clean string
    search_str = strip_tags(search_str)
    search_str = self.re_by.sub('', search_str)
    search_str = search_str.strip()

    # tokenize
    name_tokens = [ s.strip() for s in self.re_name_token.split(search_str) ]

    _authors, authors = [], []
    curname = [] # List of first, last name tokens

    for token in name_tokens:

      # check if the length of the name 
      # and the token suggest an initial
      if self.is_initial(curname, token):
        
        # upper case initial & increment
        token = token.upper()
        self.initial_count +=1

      # if we're at a delimiter, check if the name is complete
      if token.lower() in self.DELIM:

        # check valid name based on initial count
        if self.end_name(curname):
          _authors.append(' '.join(curname))
          
          # reset
          self.initial_count = 0
          curname = []

      # otherwise, append token
      elif not self.re_digits.search(token):
        curname.append(token)

    # One last check at end
    valid_name = (len(curname) >= 2)
    if valid_name:
      _authors.append(' '.join(curname))

    return self.format_authors(_authors)


  def from_html(self, html):
    """
    Fetch the authors of the article, return as a list
    Only works for english articles.
    """

    # Try 1: Search popular author tags for authors

    matches = []
    _authors = []
    doc = string_to_doc(html)

    for attr in self.ATTRS:
      for val in self.VALS:
        found = doc.xpath('//*[@%s="%s"]' % (attr, val))
        matches.extend(found)

    for match in matches:
      content = u''

      if match.tag == 'meta':
        mm = match.xpath('@content')
        if len(mm) > 0:
          content = mm[0]

        else: # match.tag == <any other tag>
          content = match.text or u'' # text_content()

        if len(content) > 0:
          _authors.extend(self.from_string(content))

    return format_authors(_authors)