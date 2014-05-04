"""
This is an extraction of newspapers module for cleaning urls.
From: https://github.com/codelucas/newspaper/blob/master/newspaper/urls.py
"""

import re
import logging 
from urlparse import (
    urlparse, urljoin, urlsplit, urlunsplit, parse_qs)
from slugify import slugify 
from hashlib import sha1

# this regex was brought to you by django!
abs_url_regex = re.compile(
    r'^(?:http|ftp)s?://'                                                                 # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'                                                                         # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'                                                # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'                                                        # ...or ipv6
    r'(?::\d+)?'                                                                          # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

re_abs_url = re.compile(abs_url_regex)

# remove https / http from url
re_http = re.compile(r'http(s)?')
re_html = re.compile(r'(index\.)?htm(l)?$')

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

    return proper_url

def get_domain(abs_url, **kwargs):
    """
    returns a url's domain, this method exists to
    encapsulate all url code into this file
    """
    if abs_url is None:
        return None
    return urlparse(abs_url, **kwargs).netloc

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
    return (re_abs_url_regex.search(url) != None)

def url_to_slug(url):
    """
    turn a url into a slug, removing http/https and .html 
    """
    url = re_http.sub('', url)
    url = re_html.sub('', url)
    return slugify(url)

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
