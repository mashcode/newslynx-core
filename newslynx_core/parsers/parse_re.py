#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# hack to check for regex type
RE_TYPE = type(re.compile(r''))

def build_regex(regex):
  """
  a helper for building regexes 
  from multiple formats.
  """
  if not regex:
    return []
    
  # if the regex is not a list, make it one
  if not isinstance(regex, list):
    regex = [regex]
  
  # test all regex
  regexes = []
  for r in regex:

    # build strings
    if isinstance(r, str):
      r = re.compile(r)

    # append RE OBJ
    if isinstance(r, RE_TYPE):
      regexes.append(r)

  return regexes 

def get_matches(regexes, s):
  """
  create a list of matches
  """
  regexes = build_regex(regexes)
  return [m for m in (r.search(s) for r in regexes ) if m]


def match_regex(regexes, s, method="any"):
  """
  a helper for testing multiple regexes
  """
  if len(regexes) == 0:
    return True

  matches = get_matches(regexes, s)

  # apply tests
  if method == "all":
    return all(matches)

  elif method == "any":
    return any(matches)
  
  # optionally yield each match
  elif method == "matches":
    return matches