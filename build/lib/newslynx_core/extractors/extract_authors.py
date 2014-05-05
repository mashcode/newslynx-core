#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re 

from newslynx_core.parsers.parse_html import (
  strip_tags, string_to_doc
  )

re_by = re.compile(r'[bB][yY][\:\s]|[fF]rom[\:\s]')
# Chunk the line by non alphanumeric tokens (few name exceptions)

# >>> re.split("[^\w\'\-]", "Lucas Ou-Yang, Dean O'Brian and Ronald")
# ['Lucas Ou-Yang', '', 'Dean O'Brian', 'and', 'Ronald'
re_name_token = re.compile(r"[^\w\'\-\.]")
re_initial = re.compile(r'^([A-Z](\.)?){1,2}$', re.IGNORECASE)
re_prefix_suffix = re.compile(r"""
  (^[Dd][Rr](\.)?$)|                   # Dr.
  (^[Mm](\.)?([Dd])(\.)?$)|            # MD
  (^[SsJj][Rr](\.)?$)|                 # SR / JR
  (^[Mm](iss)?([RrSs])?([Ss])?(\.)?$)| # Mr / Ms. / Mrs / Miss
  (^P(\.)?[Hh][Dd](\.)?)|              # PHD
  (^I(\.)?I(\.)?I(\.)?$)|              # III 
  (^I(\.)?V(\.)?$)|                    # IV
  (^V(\.)$)                            # V
""", re.VERBOSE)

re_digits = re.compile('\d')

# delimeters
DELIM = ['and', '']

MIN_NAME_TOKENS = 2
MAX_NAME_TOKENS = 4

def contains_digits(d):
  return bool(re_digits.search(d))

def format_authors(_authors):
  authors = []
  uniq = list(set([s.lower().replace('.', '') for s in _authors]))

  for name in uniq:
    tokens = [
      w.upper() if re_initial.search(w) else w.title() 
        for w in name.split(' ') 
    ]
    authors.append(' '.join(tokens))

  return authors or []

def parse_byline(search_str):
  """
  Takes a candidate line of html or text and
  extracts out the name(s) in list form
  >>> search_str('<div>By: <strong>Lucas Ou-Yang</strong>, \
                  <strong>Alex Smith</strong></div>')
  ['Lucas Ou-Yang', 'Alex Smith']
  """
  # clean string
  search_str = strip_tags(search_str)
  search_str = re_by.sub('', search_str)
  search_str = search_str.strip()

  # tokenize
  name_tokens = [s.strip() for s in re_name_token.split(search_str)]

  _authors, authors = [], []
  curname = [] # List of first, last name tokens
  init_count = 0

  for token in name_tokens:
    # check for initial
    init = (re_initial.match(token) or re_prefix_suffix.match(token))
    if ( init and len(curname) < MAX_NAME_TOKENS + 1 ):
      # upper case initial
      token = token.upper()
      init_count +=1

    # if we're at a delimiter, check if the name is complete
    if token.lower() in DELIM:
      
      # check valid name based on initial count
      est_count = MIN_NAME_TOKENS + init_count
      if (len(curname) == est_count):
        _authors.append(' '.join(curname))
        
        # reset
        init_count = 0
        curname = []

    # otherwise, append token
    elif not contains_digits(token):
      curname.append(token)

  # One last check at end
  valid_name = (len(curname) >= 2)
  if valid_name:
    _authors.append(' '.join(curname))

  return format_authors(_authors)


def extract_authors(html):
    """
    Fetch the authors of the article, return as a list
    Only works for english articles.
    """

    # Try 1: Search popular author tags for authors

    ATTRS = ['name', 'rel', 'itemprop', 'class', 'id']
    VALS = ['author', 'byline']
    matches = []
    _authors = []
    doc = string_to_doc(html)

    for attr in ATTRS:
      for val in VALS:
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
          _authors.extend(parse_byline(content))

    return format_authors(_authors)