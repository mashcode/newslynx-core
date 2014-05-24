#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Most of the code here was extracted from newspaper's module for cleaning urls.
From: https://github.com/codelucas/newspaper/blob/master/newspaper/urls.py
"""

import re
import tldextract
from slugify import slugify 
from hashlib import sha1
import httplib
import requests
import httplib
from retrying import retry, RetryError
from urlparse import (
  urlparse, urljoin, urlsplit, urlunsplit, parse_qs
  )

from newslynx_core.parsers.parse_date import date_regex
from newslynx_core.parsers.parse_re import (
  match_regex
  )

from newslynx_core import settings

MAX_FILE_MEMO = 20000

ALLOWED_TYPES = [
  'html', 'htm', 'md', 'rst', 'aspx', 'jsp', 'rhtml', 'cgi',
  'xhtml', 'jhtml', 'asp'
  ]

GOOD_PATHS = [
  'story', 'article', 'feature', 'featured', 'slides',
  'slideshow', 'gallery', 'news', 'video', 'media',
  'v', 'radio', 'press'
  ]

BAD_CHUNKS = [
  'careers', 'contact', 'about', 'faq', 'terms', 'privacy',
  'advert', 'preferences', 'feedback', 'info', 'browse', 'howto',
  'account', 'subscribe', 'donate', 'shop', 'admin'
  ]

BAD_DOMAINS = [
  'amazon', 'doubleclick', 'twitter',
  'facebook'
  ]

# this regex was brought to you by django!
re_abs_url = re.compile(r"""
  ^(?:http|ftp)s?://                                                                 # http:// or https://
  (?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|  # domain...
  localhost|                                                                         # localhost...
  \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|                                                # ...or ipv4
  \[?[A-F0-9]*:[A-F0-9:]+\]?)                                                        # ...or ipv6
  (?::\d+)?                                                                          # optional port
  (?:/?|[/?]\S+)$
""", flags = re.VERBOSE)

# remove https / http / .html from url for slugging / hashing 
re_http = re.compile(r'^http(s)?')
re_html = re.compile(r'(index\.)?htm(l)?$')
re_index_html = re.compile(r'index\.htm(l)?$')
re_www = re.compile(r'^www\.')
re_slug = re.compile(r'[^\sA-Za-z]+')
re_slug_end = re.compile(r'(^[\-]+)|([\-]+)$')
re_urls = re.compile(r'https?://[^\s\'\"]+')
re_short_urls = re.compile(r'(https?://)?([a-z]+.[a-z]+/[^\s\'\"]+)')

def extract_urls(string):
    """
    get urls from input string
    """
    urls = re_urls.findall(string)
    short_urls = [
      i+j if i!='' else 'http://'+j 
        for i,j in re_short_urls.findall(string)
        ]
    return list(set(urls + short_urls))

def remove_args(url, keep_params=(), frags=False):
  """
  Remove all param arguments from a url.
  """
  parsed = urlsplit(url)
  filtered_query= '&'.join(
    qry_item for qry_item in parsed.query.split('&')
      if qry_item.startswith(keep_params)
  )
  if frags:
    frag = parsed[4:]
  else:
    frag = ('',)

  return urlunsplit(parsed[:3] + (filtered_query,) + frag)

def redirect_back(url, source_domain):
  """
  Some sites like Pinterest have api's that cause news
  args to direct to their site with the real news url as a
  GET param. This method catches that and returns our param.
  """
  parse_data = urlparse(url)
  domain = parse_data.netloc
  query = parse_data.query

  # If our url is even from a remotely similar domain or
  # sub domain, we don't need to redirect.
  if source_domain in domain or domain in source_domain:
    return url

  query_item = parse_qs(query)
  if query_item.get('url'):
    # log.debug('caught redirect %s into %s' % (url, query_item['url'][0]))
    return query_item['url'][0]

  return url

def prepare_url(url, source_url=None):
  """
  Operations that purify a url, removes arguments,
  redirects, and merges relatives with absolutes.
  """
  try:
    if source_url is not None:
      source_domain = urlparse(source_url).netloc
      proper_url = urljoin(source_url, url)
      proper_url = redirect_back(proper_url, source_domain)
      proper_url = remove_args(proper_url)
    else:
      proper_url = remove_args(url)
  except ValueError, e:
    print 'url %s failed on err %s' % (url, str(e))
    proper_url = u''

  # remove index.html
  proper_url = re_index_html.sub('', proper_url)

  # remove trailing slashes
  if proper_url.endswith('/'):
    proper_url = proper_url[:-1]

  return proper_url

def get_domain(abs_url, **kwargs):
  """
  returns a url's domain, this method exists to
  encapsulate all url code into this file
  """
  if abs_url is None:
    return None
  return urlparse(abs_url, **kwargs).netloc

def get_simple_domain(url):
  """
  returns a standardized domain
  i.e.:
  ``` 
  > get_simple_domain('http://publiceditor.blogs.nytimes.com/')
  > 'nytimes'
  ```
  """
  domain = get_domain(url)
  tld_dat = tldextract.extract(domain)
  return tld_dat.domain

def get_scheme(abs_url, **kwargs):
  """
  returns a url's scheme, this method exists to
  encapsulate all url code into this file
  """
  if abs_url is None:
    return None
  return urlparse(abs_url, **kwargs).scheme

def get_path(abs_url, **kwargs):
  """
  returns a url's path, this method exists to
  encapsulate all url code into this file
  """
  if abs_url is None:
    return None
  return urlparse(abs_url, **kwargs).path

def is_abs_url(url):
  """
  check if a url is absolute.
  """
  return (re_abs_url.search(url.lower()) != None)

def url_to_slug(url):
  """
  turn a url into a slug, removing (index).html 
  """
  
  url = get_path(url.decode('utf-8', 'ignore'))
  url = re_html.sub('', url).strip().lower()
  url = re_slug.sub(r'-', url)
  url = re_slug_end.sub('', url)

  if url.startswith('-'):
    url = url[1:]
  elif url.endswith('-'):
    url = url[-1]

  # remove starting slugs for
  # sections
  for path in GOOD_PATHS:
    slug = "%s-" % path
    if url.startswith(slug):
      url = url.replace(slug, '')

  return url.strip()

def url_to_hash(url):
  """
  turn a url into a unique sha1 hash
  """
  url = re_http.sub('', url)
  url = re_html.sub('', url)
  return sha1(url).hexdigest()

def reconcile_embed_url(url):
  """
  make an embedded movie url like this:
  //www.youtube.com/embed/vYNnPx8fZBs
  into a full url
  """
  if url.startswith('//'):
    url = "http%s" % url
  return url

def url_to_filetype(abs_url):
  """
  Input a URL and output the filetype of the file
  specified by the url. Returns None for no filetype.
  'http://blahblah/images/car.jpg' -> 'jpg'
  'http://yahoo.com'               -> None
  """
  path = urlparse(abs_url).path
  # Eliminate the trailing '/', we are extracting the file
  if path.endswith('/'):
    path = path[:-1]
  path_chunks = [x for x in path.split('/') if len(x) > 0]
  last_chunk = path_chunks[-1].split('.')  # last chunk == file usually
  file_type = last_chunk[-1] if len(last_chunk) >= 2 else None
  return file_type or None


def valid_url(
    url, 
    good_regex =  None, 
    bad_regex  =  None, 
    good_test  = 'any', 
    bad_test   = 'all', 
    test       =  False
  ):
  """
  Perform a regex check on an absolute url.
    
  BPA: NexsLynx also allows for checking against specifc regexes 
       and globally-known regexes.

  
  First, perform a few basic checks like making sure the format of the url
  is right, (scheme, domain, tld).

  Second, make sure that the url isn't some static resource, check the
  file type.

  Then, search of a YYYY/MM/DD pattern in the url. News sites
  love to use this pattern, this is a very safe bet.

  Separators can be [\.-/_]. Years can be 2 or 4 digits, must
  have proper digits 1900-2099. Months and days can be
  ambiguous 2 digit numbers, one is even optional, some sites are
  liberal with their formatting also matches snippets of GET
  queries with keywords inside them. ex: asdf.php?topic_id=blahlbah
  We permit alphanumeric, _ and -.

  Our next check makes sure that a keyword is within one of the
  separators in a url (subdomain or early path separator).
  cnn.com/story/blah-blah-blah would pass due to "story".

  We filter out articles in this stage by aggressively checking to
  see if any resemblance of the source& domain's name or tld is
  present within the article title. If it is, that's bad. It must
  be a company link, like 'cnn is hiring new interns'.

  We also filter out articles with a subdomain or first degree path
  on a registered bad keyword.
  """
  # If we are testing this method in the testing suite, we actually
  # need to preprocess the url like we do in the article's constructor!
  # if test:
  #   url = prepare_url(url)

  # # check global regex first
  # if settings.KNOWN_ARTICLE_REGEX.search(url):
  #   return True

  # if we pass in custom regexes, check those first
  if bad_regex:
    return not match_regex(bad_regex, url, bad_test)

  elif good_regex:
    return match_regex(good_regex, url, good_test)

  # 11 chars is shortest valid url length, eg: http://x.co
  if url is None or len(url) < 11:
    return False

  r1 = ('mailto:' in url) # TODO not sure if these rules are redundant
  r2 = ('http://' not in url) and ('https://' not in url)

  if r1 or r2:
    return False

  path = urlparse(url).path

  # input url is not in valid form (scheme, netloc, tld)
  if not path.startswith('/'):
    return False

  # the '/' which may exist at the end of the url provides us no information
  if path.endswith('/'):
    path = path[:-1]

  # '/story/cnn/blahblah/index.html' --> ['story', 'cnn', 'blahblah', 'index.html']
  path_chunks = [x for x in path.split('/') if len(x) > 0]

  # siphon out the file type. eg: .html, .htm, .md
  if len(path_chunks) > 0:
    file_type = url_to_filetype(url)

    # if the file type is a media type, reject instantly
    if file_type and file_type not in ALLOWED_TYPES:
      return False

    last_chunk = path_chunks[-1].split('.')
    # the file type is not of use to use anymore, remove from url
    if len(last_chunk) > 1:
      path_chunks[-1] = last_chunk[-2]

  # Index gives us no information
  if 'index' in path_chunks:
    path_chunks.remove('index')

  # extract the tld (top level domain)
  tld_dat = tldextract.extract(url)
  subd = tld_dat.subdomain
  tld = tld_dat.domain.lower()

  url_slug = path_chunks[-1] if path_chunks else u''

  if tld in BAD_DOMAINS:
    return False

  if len(path_chunks) == 0:
    dash_count, underscore_count = 0, 0
  else:
    dash_count = url_slug.count('-')
    underscore_count = url_slug.count('_')

  # If the url has a news slug title
  if url_slug and (dash_count > 4 or underscore_count > 4):

    if dash_count >= underscore_count:
      if tld not in [ x.lower() for x in url_slug.split('-') ]:
        return True

    if underscore_count > dash_count:
      if tld not in [ x.lower() for x in url_slug.split('_') ]:
        return True

  # There must be at least 2 subpaths
  if len(path_chunks) <= 1:
    return False

  # Check for subdomain & path red flags
  # Eg: http://cnn.com/careers.html or careers.cnn.com --> BAD
  for b in BAD_CHUNKS:
    if b in path_chunks or b == subd:
      return False

  match_date = date_regex.search(url)

  # if we caught the verified date above, it's an article
  if match_date:
    return True

  for GOOD in GOOD_PATHS:
    if GOOD.lower() in [p.lower() for p in path_chunks]:
      return True

  return False

# SHORT DOMAINS #

# a big ugly list of short_urls
re_short_domains = re.compile(r"""
  (^bit\.do$)|
  (^t\.co$)|
  (^go2\.do$)|
  (^adf\.ly$)|
  (^goo\.gl$)|
  (^bitly\.com$)|
  (^bit\.ly$)|
  (^tinyurl\.com$)|
  (^ow\.ly$)|
  (^bit\.ly$)|
  (^adcrun\.ch$)|
  (^zpag\.es$)|
  (^ity\.im$)|
  (^q\.gs$)|
  (^lnk\.co$)|
  (^viralurl\.com$)|
  (^is\.gd$)|
  (^vur\.me$)|
  (^bc\.vc$)|
  (^yu2\.it$)|
  (^twitthis\.com$)|
  (^u\.to$)|
  (^j\.mp$)|
  (^bee4\.biz$)|
  (^adflav\.com$)|
  (^buzurl\.com$)|
  (^xlinkz\.info$)|
  (^cutt\.us$)|
  (^u\.bb$)|
  (^yourls\.org$)|
  (^fun\.ly$)|
  (^hit\.my$)|
  (^nov\.io$)|
  (^crisco\.com$)|
  (^x\.co$)|
  (^shortquik\.com$)|
  (^prettylinkpro\.com$)|
  (^viralurl\.biz$)|
  (^longurl\.org$)|
  (^tota2\.com$)|
  (^adcraft\.co$)|
  (^virl\.ws$)|
  (^scrnch\.me$)|
  (^filoops\.info$)|
  (^linkto\.im$)|
  (^vurl\.bz$)|
  (^fzy\.co$)|
  (^vzturl\.com$)|
  (^picz\.us$)|
  (^lemde\.fr$)|
  (^golinks\.co$)|
  (^xtu\.me$)|
  (^qr\.net$)|
  (^1url\.com$)|
  (^tweez\.me$)|
  (^sk\.gy$)|
  (^gog\.li$)|
  (^cektkp\.com$)|
  (^v\.gd$)|
  (^p6l\.org$)|
  (^id\.tl$)|
  (^dft\.ba$)|
  (^aka\.gr$)|
  (^bbc.in$)|
  (^ift\.tt$)|
  (^amzn.to$)|
  (^p\.tl$)|
  (^trib\.al$)|
  (^1od\.biz$)|
  (^ht\.ly$)|
  (^fb\.me$)|
  (^4sq\.com$)|
  (^tmblr\.co$)|
  (^dlvr\.it$)|
  (^ow\.ly$)|
  (^mojo\.ly$)|
  (^propub\.ca$)|
  (^feeds\.propublica\.org$)|
  (^ckbe\.at$)|
  (^polti\.co$)|
  (^pocket\.co$)
  """, flags=re.VERBOSE)

def is_short_url(url, regex=None, test="any"):
  """
  test url for short links,
  allow str / list / retype's and passing in 
  custom urls
  """
  # pass in specific regexes
  domain  = get_domain(url)
  if regex:
    # only return if we match the custom domain, never fail
    # because of this
    custom_domain = match_regex(regex=regex, s=domain, test=test)
    if custom_domain:
      return True

  # test against known short links
  if re_short_domains.search(domain):
    return True
    
  else:
    return False

@retry(retry_on_result=is_short_url, stop_max_delay=settings.UNSHORTEN_TIMEOUT)
def unshorten_url(url):
  try:
    r = requests.get(url)
    return r.url
  except:
    return url

# # fast, recursive url shortener.
# @retry(stop_max_delay=5000)
# def unshorten_url(url):
#   parsed = urlparse(url)
#   h = httplib.HTTPConnection(parsed.netloc)
#   h.request('HEAD', parsed.path)
#   response = h.getresponse()
#   try:
#     if response.status/100 == 3 and response.getheader('Location'):
#       return unshorten_url(response.getheader('Location')) # changed to process chains of short urls
#     else:
#       return url
#   except RetryError:
#     return url

# def unshorten_url(url, regex=None, test="any"):
#   """
#   recursively unshorten a url
#   """
#   try:
#     # open url
#     r = requests.get(url)

#     # if we don't get anyhting just pass, we'll try
#     # again if it's a short link, otherwise
#     # we'll just return it.
#     if r.status_code != 200:
#       pass
#     # if we do get something, update url
#     else:
#       url = r.url

#     # if it's still short, recursively unshorten
#     if test:
#       tries = 0
#       while test:

#         # iterate tries
#         tries += 1
        
#         try:
#           r = requests.get(url)
        
#         except Exception as e:
#           print "error on `unshorten_link`, %s" % str(e)
#           break

#         else:
          
#           # TODO: don't fail silently
#           if r.status_code != 200:
#             break
          
#           # update url and give it one more shot!
#           else:
#             url = r.url
          
#             # if it's not short now, stop
#             if not is_short_url(url, regex, test):
#               break

#             # if we've tried X times, give up
#             if tries == settings.MAX_UNSHORTEN_ATTEMPTS:
#               break

#   except requests.exceptions.TooManyRedirects:
#     pass

#   # parse url at final state
#   return url

