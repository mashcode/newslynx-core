# encoding: utf-8

import os
from utils import client, silence

"""
- get a list of all org directories
- in today's date, get all article dirs
- check for those that don't yet have an `analysis` directory

=> these are the articles on which we will operate
"""

# note: some of this is definitely parallelizable, though 
# at the current workload speed is really not an issue
if __name__ == '__main__':
    def is_organization(meta):
        return meta['type'] == 'directory' and '.' in meta['name']

    domains = [name for name, meta in client.ls(root).items() if is_organization(meta)]
    
    articles = []    

    for domain in domains:
        ls = silence(client.ls, {})

        def today(*segments):
            return os.path.join(root, domain, date.today().isoformat(), 'articles', *segments)

        article_names = sum([ls(today()).keys() for domain in domains], [])
        articles.extend([today(name, 'analysis') for name in article_names])

    exists = lambda d: silence(client.ls, False)(d)
    
    for article in articles:
        if exists(article) is False:
            print os.path.join(os.path.dirname(article), 'raw', 'latest.html')
