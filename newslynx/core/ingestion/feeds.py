# encoding: utf-8

import sys
import os
import json
from datetime import date, datetime
import base64
import requests
import feedparser
import manta
from manta.errors import MantaAPIError

import logging

#logging.basicConfig(level='DEBUG')

url = os.environ['MANTA_URL']
account = os.environ['MANTA_USER']
key_id = os.environ.get('MANTA_KEY_ID')
signer = None

if key_id:
    signer = manta.SSHAgentSigner(key_id)

client = manta.MantaClient(url, account, signer)


# Manta expects directory names to end with a trailing slash
def dirname(filename):
    return os.path.dirname(filename) + '/'


def save(filename, data, local=False):
    # askmanta should take care of the abstraction 
    # rather than us, but whatever
    if local:
        filename = os.path.join('data', filename)
        with open(filename, 'w') as f:
            f.write(data)
    else:
        print filename
        client.mkdirp(dirname(filename))
        client.put_object(filename, data)


def versioned_save(directory, extension, data):
    if len(extension) and not extension.startswith('.'):
        extension = '.' + extension

    now = datetime.today().isoformat()[:16]
    latest = os.path.join(directory, 'latest' + extension)
    snaplink = os.path.join(directory, now + extension)
    # Manta is supposed to be strongly consistent, but 
    # it doesn't really look that way...
    save(latest, data)
    client.ln(latest, snaplink)


def download(organization):
    url = organization['feeds'][0]
    raw = requests.get(url).text
    feed = feedparser.parse(raw)
    today = date.today().isoformat()
    basedir = '/stdbrouw/stor/{domain}/{today}'.format(
        domain=organization['domain'], 
        today=today, 
    )
    versioned_save(basedir + '/feeds', '', raw.encode('utf-8'))

    for entry in feed.entries:
        destination = '{basedir}/articles/{url}/raw/'.format(
            basedir=basedir, 
            #url=urllib.quote(entry.link, ''),
            url=base64.urlsafe_b64encode(entry.link),
        )

        # only fetch an article if we haven't before
        # 
        # head_directory can fail gracefully (error status code)
        # and not-so-gracefully (throwing an exception) so we 
        # have to catch both
        try:
            response = client.head_directory(destination)
            assert response['status'] == '200'
        except (MantaAPIError, ValueError):
            article = requests.get(entry.link)
            body = article.text
            versioned_save(destination, 'html', body.encode('utf-8'))


if __name__ == '__main__': 
    for data in sys.stdin:
       organization = json.loads(data)
       download(organization)

