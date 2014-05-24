#!/bin/sh

if [ -d newslynx_core.egg-info ]; then
  rm -rf newslynx_core.egg-info
fi
if [ -d build ]; then
  rm -rf build
fi
if [ -d dist ]; then
  rm -rf dist
fi
mkvirtualenv newslynx-core
workon newslynx-core
pip install -r requirements.txt
python setup.py install
python newslynx_core/controller.py flushall 
python newslynx_core/database.py init
