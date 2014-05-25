import click
import os
from newslynx_core import tasks
from newslynx_core.listener import Listener

# groups
@click.group()
def poll(ctx):
    pass

@click.group()
def listen(ctx):
    pass

@listen.command()
@click.option('--channels', default='public:twitter', help='A list of channels to subscribe to')
def listen(channels):
  l = Listener(channels.split(','))
  l.run()

# poll commands:
@poll.command()
def articles():
  tasks.articles().run()

@poll.command()
def facebook_page_stats():
  tasks.facebook_page_stats().run()

@poll.command()
def facebook_pages():
  tasks.facebook_pages().run()

@poll.command()
def galerts():
  tasks.galerts().run()

@poll.command()
def homepages():
  tasks.homepages().run()

@poll.command()
def twitter_lists():
  tasks.twitter_lists().run()

@poll.command()
def twitter_search():
  tasks.twitter_search().run()

@poll.command()
def twitter_stream():
  tasks.twitter_stream().run()

@poll.command()
def twitter_user_stats():
  tasks.twitter_user_stats().run()

@poll.command()
def twitter_users():
  tasks.twitter_users().run()

cli = click.CommandCollection(sources=[poll, listen])

if __name__ == '__main__':
    cli()
