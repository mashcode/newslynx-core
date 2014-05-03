"""
This is newspapers module for cleaning urls
From: https://github.com/codelucas/newspaper/blob/master/newspaper/urls.py
"""

import re

from urlparse import (
    urlparse, urljoin, urlsplit, urlunsplit, parse_qs)

from .packages.tldextract import tldextract

log = logging.getLogger(__name__)

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
        log.critical('url %s failed on err %s' % (url, str(e)))
        # print 'url %s failed on err %s' % (url, str(e))
        proper_url = u''

    return proper_url