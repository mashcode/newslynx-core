import click
import os
from newslynx_core import tasks


# groups
@click.group()
def poll(ctx):
    pass

@click.group()
def parse(ctx):
    pass 

@click.group()
def query(ctx):
    pass 

def listen(ctx):
    pass

@click.group()
def manage(ctx):
    pass 

# poll commands:
@poll.command()
def articles():
  tasks.articles().run()


@poll.command()
def articles():
  tasks.articles().run()

@poll.command()
def facebook_page_stats():
  facebook_page_stats

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

cli = click.CommandCollection(sources=[poll])

if __name__ == '__main__':
    cli()