#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import json
from lxml import html
from readability.readability import Document

# ultimately, these analyses will be split out and ordered through a 
# dependency graph, but let's get started without...

def extract(content):
    document = Document(content)
    body = document.summary()
    doc = html.fromstring(body)
    paragraphs = [paragraph.text_content() for paragraph in doc.cssselect('p')]

    data = {
        'summary': document.summary(html_partial=True), 
        'title': document.short_title(), 
        'body': '\n\n'.join(paragraphs),
    }

    return data


if __name__ == '__main__':
    for line in sys.stdin.readlines():
        filename = line.rstrip('\n')
        path = os.path.join('data', filename)
        content = open(path).read()
        data = extract(content)
        out = os.path.join('data', filename + '.json')
        json.dump(data, open(out, 'w'))