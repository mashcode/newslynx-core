#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import json
import urllib
import requests
import feedparser
import manta


client = manta.MantaClient(internal=True)


def save(filename, data, local=False):
    # askmanta should take care of the abstraction 
    # rather than us, but whatever
    if local:
        filename = os.path.join('data', filename)
        with open(filename, 'w') as f:
            f.write(data)
    else:         
        client.put_object(filename, data)
    
    print filename

def download(organization):
    url = organization['rss']
    data = feedparser.parse(url)

    for entry in data.entries:
        response = requests.get(entry.link)
        location = urllib.quote(entry.link, '')
        body = response.text
        save(location, body.encode('utf-8', local=True)


if __name__ == '__main__':
    organization = json.load(sys.stdin)
    download(organization)