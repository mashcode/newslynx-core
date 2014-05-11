# -*- coding: utf-8 -*-

import json
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class JSONEncoder(json.JSONEncoder):
  """ This encoder will serialize all entities that have a to_dict
  method by calling that method and serializing the result. """

  def __init__(self, refs=False):
    self.refs = refs
    super(JSONEncoder, self).__init__()

  def default(self, obj):
    if isinstance(obj, datetime):
      return obj.isoformat()
    if isinstance(obj, date):
      return obj.isoformat()
    if isinstance(obj, UUID):
      return str(obj)
    if isinstance(obj, Decimal):
      return float(obj)
    if isinstance(obj, set):
      return list(obj)
    if self.refs and hasattr(obj, 'to_ref'):
      return obj.to_ref()
    if hasattr(obj, 'to_json'):
      return obj.to_json()
    if hasattr(obj, 'to_dict'):
      return obj.to_dict()
    
    return json.JSONEncoder.default(self, obj)

def jsonify(obj, refs=False, encoder=JSONEncoder):
  """ Custom JSONificaton to support obj.to_dict protocol. """
  if encoder is JSONEncoder:
    data = encoder(refs=refs).encode(obj)
  else:
    data = encoder().encode(obj)

  return data 