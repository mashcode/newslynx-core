#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import facepy
import yaml
from datetime import datetime, timedelta
from urlparse import parse_qs

from newslynx_core import settings

def connect(app_id=settings.FB_APP_ID, app_secret=settings.FB_APP_SECRET):
    access_token = generate_app_access_token(app_id, app_secret)
    return facepy.GraphAPI(access_token)

def generate_app_access_token(app_id, app_secret):
    """
    Get an extended OAuth access token.

    :param access_token: A string describing an OAuth access token.
    :param application_id: An icdsnteger describing the Facebook application's ID.
    :param application_secret_key: A string describing the Facebook application's secret key.

    Returns a tuple with a string describing the extended access token and a datetime instance
    describing when it expires.
    """
    # access tokens
    default_access_token = facepy.get_application_access_token(
        application_id = app_id,  
        application_secret_key = app_secret
    )
    graph = facepy.GraphAPI(default_access_token)

    response = graph.get(
        path='oauth/access_token',
        client_id = app_id,
        client_secret = app_secret,
        grant_type = 'client_credentials'
    )
    components = parse_qs(response)
    token = components['access_token'][0]
    return token

if __name__ == '__main__':

    from newslynx_core.facebook.parse_post import (
        FacebookPostParser
    )
    api = connect()
    parser = FacebookPostParser(org_id = 'propublica', page_id = 'propublica')
    posts = api.get('propublica/posts', page=False, retry=5, limit=5)
    print parser.parse(posts['data'][0])