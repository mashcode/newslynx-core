# -*- coding: utf-8 -*-
"""
this is a remix of newspaper which sampled reddit.
"""

import urllib
import StringIO
import cStringIO
import math
from PIL import Image, ImageFile
from urllib2 import Request, HTTPError, URLError, build_opener
from httplib import InvalidURL
import base64

from newslynx_core.parsers.parse_url import (
  url_to_filetype
  )
from newslynx_core import settings

# global image settings
IMG_CHUNK_SIZE = 1024
IMG_THUMB_SIZE = 90, 90
IMG_MIN_AREA = 5000
IMG_DIM_RATIO = 16/9.0
IMAGE_RETRIES = 1
SPRITE_PENALTY = 10

class ImageExtractor:
  """
  Class for Extracting Images 
  Taken From Reddit Source Code
  """
  def __init__(self, **kwargs):
    self.referer     = kwargs.get('referer', None)
    self.retries     = IMAGE_RETRIES,
    self.useragent   = settings.USER_AGENT
    self.top_img     = None

  def img_to_str(self, img):
    s = StringIO.StringIO()
    img.save(s, img.format)
    s.seek(0)
    return s.read()

  def str_to_img(self, s):
    s = StringIO.StringIO(s)
    s.seek(0)
    img = Image.open(s)
    return img

  def img_to_b64(self, img):
    s = cStringIO.StringIO()
    img.save(s, img.format)
    s.seek(0)
    return base64.b64encode(s.read())

  def b64_to_img(self, b64):
    s = cStringIO.StringIO(base64.b64decode(b64))
    s.seek()
    img = Image.open(s)
    return img

  def img_to_thumb(self, img):
    img = self.square_img(img)
    img.thumbnail(IMG_THUMB_SIZE, Image.ANTIALIAS) # inplace
    return img

  def img_entropy(self, mg):
    """
    Calculate the entropy of an image.
    """
    hist = img.histogram()
    hist_size = sum(hist)
    hist = [float(h) / hist_size for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])

  def square_img(self, img):
    """
    If the image is taller than it is wide, square it off. determine
    which pieces to cut off based on the entropy pieces.
    """
    x,y = img.size
    while y > x:
      # slice 10px at a time until square
      slice_height = min(y - x, 10)

      bottom = img.crop((0, y - slice_height, x, y))
      top = img.crop((0, 0, x, slice_height))

      # remove the slice with the least entropy
      if self.img_entropy(bottom) < img_entropy(top):
        img = img.crop((0, 0, x, y - slice_height))
      else:
        img = img.crop((0, slice_height, x, y))

      x,y = img.size

    return img

  def clean_url(self, url):
    """
    Url quotes unicode data out of urls.
    """
    url = url.encode('utf8')
    url = ''.join([urllib.quote(c) if ord(c) >= 127 else c for c in url])
    return url

  def img_from_url(self, img_url, dim):
    """ 
    Request an image and return a PIL 
    object.

    Optionally request only a chunk of the image 
    and calculate it's dims for testing.
    """
    cur_try = 0
    nothing = None if dim else (None, None)
    img_url = self.clean_url(img_url)

    if not img_url.startswith(('http://', 'https://')):
      return nothing

    while True:
      try:
        req = Request(img_url)
        req.add_header('User-Agent', self.useragent)
        if self.referer:
          req.add_header('Referer', self.referer)

        opener = build_opener()
        open_req = opener.open(req, timeout=5)

        # if we only need the dim of the image, we may not
        # need to download the entire thing
        if dim:
          content = open_req.read(IMG_CHUNK_SIZE)
        else:
          content = open_req.read()

        content_type = open_req.headers.get('content-type')

        if not content_type:
          return nothing

        if 'image' in content_type:
          p = ImageFile.Parser()
          new_data = content

          while not p.image and new_data:
            try:
              p.feed(new_data)

            except IOError, e:
              # pil failed to install, jpeg codec broken
              # **should work if you install via pillow
              print ('***jpeg misconfiguration! check pillow or pil'
                     'installation this machine: %s' % str(e))
              p = None
              break

            except ValueError, ve:
              print('cant read image format: %s' % img_url)
              p = None
              break

            except Exception, e:
              # For some favicon.ico images, the image is so small
              # that our PIL feed() method fails a length test.
              # We add a check below for this.
              is_favicon = (url_to_filetype(img_url) == 'ico')

              if is_favicon:
                print 'we caught a favicon!: %s' % img_url
                pass
              else:
                # import traceback
                # print traceback.format_exc()
                #print 'PIL feed() failure for image:', img_url, str(e)
                raise e

              p = None
              break

            new_data = open_req.read(IMG_CHUNK_SIZE)
            content += new_data

          if p is None:
            return nothing

          # return the size, or return the data
          if dim and p.image:
            return p.image.size

          elif dim:
            return nothing

        elif dim:
          # expected an image, but didn't get one
          return nothing

        return content_type, content

      except (URLError, HTTPError, InvalidURL), e:
        cur_try += 1
        if cur_try >= retries:
          print('error while fetching: %s refer: %s' % (img_url, self.referer))
          return nothing

      finally:
        if 'open_req' in locals():
          open_req.close()

  def fetch_img(self, img_url):
    """
    Fetch an img 
    """
    return self.img_from_url(img_url, False) 

  def fetch_img_dim(self, img_url):
    """
    Fetch just the dims 
    of an img
    """
    return self.img_from_url(img_url, True)

  def calc_img_area(self, dim, img_url):
    """
    Calculate the area of an image, 
    penalizing for logos and sprites
    """
    area = dim[0] * dim[1]
    
    # penalize images with "sprite" in their name
    lower_case_url = img_url.lower()
    if 'sprite' in lower_case_url or 'logo' in lower_case_url:
      print('penalizing sprite %s' % img_url)
      area /= SPRITE_PENALTY 

    return area

  def valid_img(self, dim, area):
    """
    various tests of an images validity
    """
    # PIL won't scale up, so we set a min width and
    # maintain the aspect ratio
    if dim[0] < IMG_THUMB_SIZE[0]:
      return False

    # ignore excessively long/wide images
    if max(dim) / min(dim) > IMG_DIM_RATIO:
      #print('ignore dims %s' % img_url)
      return False

    # calculate area and check against threshold
    return area > IMG_MIN_AREA


  def largest_img_url(self, img_urls):
    """
    Determine the largest img_url
    """
    max_area = 0
    max_url = None

    for img_url in img_urls:

      # get stats
      dim = self.fetch_img_dim(img_url)
      area = self.calc_img_area(dim, img_url)

      # check if the image is valid
      if self.valid_img(dim, area):

        # update values
        if area > max_area:
          max_area = area
          max_url = img_url

    return max_url

  def get_top_img(self, img_urls):
    """
    Identifies top image, trims out a thumbnail and also has a url.
    """
    # default to list
    if isinstance(img_urls, str):
      img_urls = [img_urls]

    # get largest img
    img_url = self.largest_img_url(img_urls)
    
    # if there's a valid img, get it.
    if img_url:
      content_type, img_str = self.fetch_img(img_url)

      # if we got an img parse it.
      if img_str:
        img = self.str_to_img(img_str)
        try:
          thumb = self.img_to_thumb(img)
        except IOError, e:
          if 'interlaced' in e.message:
            thumb = None
          else:
            thumb = None

      return img_url, self.img_to_b64(img), self.img_to_b64(thumb)

    return img_url, None, None
