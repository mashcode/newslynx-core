from datetime import datetime 
from newslynx_core.facebook.api import connect
from newslynx_core.source import Source 

class FacebookInsightsParserInitError(Exception):
  pass

class FacebookInsightsParser(Source):
  def __init__(self, **kwargs):
    if 'page_id' not in kwargs:
      raise FacebookInsightsParserInitError(
        'FacebooInsightsParser requires a page_id'
        )
    Source.__init__(self,
      org_id = kwargs.get('org_id'),
      source_type = 'facebook_insights'
      )
    self.page_id = kwargs.get('page_id')
    self.limit = kwargs.get('limit', 200)
    self.api = connect()

  def task_id(self, post_id):
    return "%s-%s" % (post_id, datetime.now().strftime('%s'))

  def poller(self):
    page = self.api.get(self.page_id + "/posts", page=False, retry=5, limit = self.limit)
    for post in reversed(page['data']):
      yield post['id']

  def parser(self, task_id, post_id):
    """
    Get insights data if indicated so by the config file
    """
    # default data
    insights = {}
    insights['insights_id'] = task_id
    insights['org_id'] = self.org_id 
    insights['page_id'] = self.page_id
    insights['post_id'] = post_id
    insights['datetime'] = datetime.now()

    graph_results = self.api.get(post_id + "/insights", page=False, retry=5)
    data = graph_results['data']

    for d in data:
      val = d['values'][0]['value']
      if isinstance(val, dict):
        for k, v in val.iteritems():
          insights[k] = v

      else:
        insights[d['name']] = val

    return insights

  def messenger(self, output):
    return {
      'insights_id': output['insights_id']
    }

if __name__ == '__main__':
  fbis = FacebookInsightsParser(org_id = 'newslynx', page_id = 'me')
  fbis.run()
