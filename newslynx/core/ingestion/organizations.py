# encoding: utf-8

"""
The idea is to get these from PostGres in the future, but 
for now we just grab 'em from a list of fixtures.
"""

import sys
import json
import yaml

if __name__ == '__main__':
    organizations = yaml.load(sys.stdin)
    for name, organization in organizations.items():
        print json.dumps(organization)