#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Strategy:

* Open homepage in seleniumjs,
* make the window size 900x1200
* exctract all links and check if they're valid.
* for all valid links, extract:
* x,y coordinates
* whether the link has an image
* extract the headline
* divide the page up into 300x300 grids, and assign each link to a grid id,
* which moves from top left to bottom right.
* if there is more than on instance of a link in a grid, register it as a single
* link, and retain it's image, headline, and average position among all links.
* return a list of json.
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from datetime import datetime, timedelta
import socket

from newslynx_core.source import Source 
from newslynx_core.parsers.parse_url import (
  valid_url, prepare_url
  )
from newslynx_core import settings 

# set the socket timeout
socket.setdefaulttimeout(20)

class HomepageParserInitError(Exception):
  pass

class HomepageParser(Source):
  def __init__(self, **kwargs):
    if 'homepage' not in kwargs:
      raise HomepageParserInitError(
        'HomepageParser requires a '
        'hompage to run.'
        )
    Source.__init__(
      self,
      org_id = kwargs.get('org_id'),
      source_type = 'homepages'
      )
    self.homepage = kwargs.get('homepage')
    self.bucket_pixels = kwargs.get('bucket_pixels', settings.HOMEPAGE_BUCKET_PIXELS)
    self.browser = webdriver.PhantomJS()

  def readystate_complete(self):
    # AFAICT Selenium offers no better way to wait for the document to be loaded,
    # if one is in ignorance of its contents.
    return self.browser.execute_script("return document.readyState") == "complete"

  def get_homepage_safely(self):
    tries = 0
    try:
      self.browser.get(self.homepage)
      WebDriverWait(self.browser, 30).until(self.readystate_complete)
    
    except TimeoutException:
      self.browser.execute_script("window.stop();")

    except socket.timeout:
      while 1:

        try:
          self.browser.get(self.homepage)
          WebDriverWait(b, 5).until(readystate_complete)
    
        except TimeoutException:
          self.browser.execute_script("window.stop();")

        except:
          tries += 1
          if tries == 20:
            break
        else:
          break

    except Exception as e:
      pass

  def get_url(self, link):
    url = link.get_attribute("href")
    if url:
      return prepare_url(url)
    else:
      return ''

  def get_img_data(self, link):
    try:
      img = link.find_element_by_tag_name("img")
    except NoSuchElementException:
      img = None
    if img is not None:
      w = int(img.get_attribute("width"))
      h = int(img.get_attribute("height"))
      
      return dict(
        has_img = 1,
        img_width = w,
        img_height = h,
        img_area = w * h,
        img_src = img.get_attribute("src")
      )
    else:
      return dict(has_img = 0)

  def get_font_size(self, link):
    return int(link.value_of_css_property('font-size')[:-2])

  def bucket_coord(self, c):
    return int(c / self.bucket_pixels) + 1

  # TODO
  def get_bucket_data(self, x, y):
    if x == 0 and y == 0:
      return {}
    else:
      x_b = self.bucket_coord(x)
      y_b = self.bucket_coord(y)
      return {
        'x_bucket': x_b,
        'y_bucket': y_b,
        'bucket': (x_b + y_b) - 1
      }

  def valid_link(self, link):
    # only get visible links
    if not link.is_displayed():
      return False

    # only get valid links
    url = self.get_url(link)
    if valid_url(url):
      return True

    # default to invalid
    return False

  def task_id(self, link):
    url = self.get_url(link)
    return "%s-%s" % (url, datetime.now().strftime('%s'))

  def poller(self):
    # extract links 
    self.get_homepage_safely()
    links = self.browser.find_elements_by_tag_name('a')
    for link in links:
      if self.valid_link(link):
        yield link
  
  def parser(self, task_id, link):
    
    url = self.get_url(link)          

    # get coordinates
    x = int(link.location['x'])
    y = int(link.location['y'])

    bucket_dict = self.get_bucket_data(x, y)

    # get image
    img_dict = self.get_img_data(link)

    link_dict = {
      'homepage' : self.homepage,
      'homepage_id' : task_id,
      'org_id': self.org_id,
      'datetime': datetime.now(),
      'headline' :  link.text.strip(),
      'url': url,
      'font_size' : self.get_font_size(link),
      'x' : x,
      'y' : y
    }

    data = dict(
      link_dict.items() + 
      img_dict.items() + 
      bucket_dict.items()
      )          

    # return data
    return data

  # def messenger(self, output):
  #   return {
  #     'homepage_id' : output['homepage_id']
  #   }

if __name__ == '__main__':
  hp = HomepageParser(org_id = 'propublica', homepage = 'http://www.propublica.org/')
  hp.run()


