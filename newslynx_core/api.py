#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
import os
from os.path import abspath, dirname
from newslynx_core.database import db
from newslynx_core.parsers.serialization import jsonify
from gevent.wsgi import WSGIServer

# intitialize app
app = Flask(__name__)
app.root_path = abspath(dirname(__file__))

def format_list(l):
  return "('%s')" % "', '".join(l)

def query_response(q):
  return jsonify(list(db.query(q)))

@app.route('/article-urls')
def article_urls():
  org_ids = request.args.get('org_ids', None)
  limit = str(request.args.get('limit', 200))
  sort = request.args.get('sort', 'desc')

  if org_ids:
    args = org_ids.split(',')
    print args
    filtr = "WHERE org_id in %s" % format_list(args)
  else:
    filtr = None 
  q = """SELECT url, org_id, pub_datetime 
         FROM articles %s 
         ORDER BY pub_datetime %s
         LIMIT %s""" % (filtr, sort, limit)

  return query_response(q)

@app.route('/query/<q>')
def query(q):
  return query_response(q)

if __name__ == '__main__':
  port = int(80)
  http_server = WSGIServer(('0.0.0.0', port), app)
  http_server.serve_forever()


