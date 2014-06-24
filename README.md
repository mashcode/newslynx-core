newslynx-core
=============
The core framework for populating newslynx's data store.

## Install

Install `newslynx-core` and it's core dependencies via:
```
mkvirtualenv newslynx-core
git clone https://github.com/newslynx/newslynx-core.git
cd newslynx-core
pip install -r requirements.txt
python setup.py install
```

And then install optional libs. Read [this](http://stackoverflow.com/questions/8525193/how-to-install-jpype-on-os-x-lion-to-use-with-neo4j) before installing `boilerpipe`.

```
pip install git+https://github.com/grangier/python-goose.git
pip install boilerpipe
```

## TODO
 - [x] Utilities for parsing various things.
 - [x] Utilities for extracting Articles
 - [x] Utilities for extracting URLs
 - [x] Utilites for extracing Images
 - [x] Utilites for extracing Authors
 - [x] Article Extraction
 - [x] `newslynx_core.database.db`. 
  * The `dataset` object and explicit **postgresql** schema definitions for each source table. 
 - [x] `newslynx_core.controller.Controller`
  * A **redis** controller for Sources.
  * contains methods for de-duplication, messaging, and flushing
 - [x] `newslnyx_core.source.Source`
  * An abstract class for grabbing data from any source.
  * For each source, inherit this class and overwrite `.task_id()`, `poller`, `parser`, and `messenger`.
  * this process will run on **gevent** queues, checking for duplicates via `Controller`,
    and inserting new records into `db`
 - [x] `newlynx_core.poll.Poll`
  * An abstract class for Polling multiple sources
  * Uses `Contoller` to determine what to poll when.
 - [x] `newslynx_core.feeds.parse_feed.FeedParser`
 - [x] `newslynx_core.alerts.parse_galert.GAlertParser`
 - [x] `newslynx_core.social_media.facebook`
   * connecting to api
   * parsing facebook pages.
   * parse facebook page stats
   * parsing facebook posts.
   * parsing facebook insights.
   * TODO authentication with other users credentials.
 - [x] `newslynx_core.social_media.twitter`
   * parse twitter searches
   * parse lists
   * parse users timelines
   * parse user stats
   * reading from streaming API
   * TODO authentication with other users credentials.
- [x] `newslynx_core.homepage`
  * detect what aritcle links are on each organization's homepage, when.
- [ ] Figure out this stupid debug message:
```
Exception KeyError: KeyError(4322285680,) in <module 'threading' from '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/threading.pyc'> ignored
```
## Framework:

Data will be polled from various sources using this basic strategy:

1. Store unique identifiers of every thing we poll for each
   organization, including these source types:
  * rss feeds
  * articles 
  * homepages
  * twitter posts
  * twitter lists   
  * facebook pages
  * google alerts
  * TK

  In sorted sets in **redis** where the name of the set is `<org_id>:<source_type>`
  the key is `<source_id>` (urls, twitter ids, etc.), and the value is 
  the time it first entered the system. In the case of dynamic feeds (google alerts, twitter lists, facebook pages, homepages, etc.), the value will be the time we last updated that source. Each day we will check these hashes and flush values which are older than some set interval of time ( a month or something...). We'll also store
  a hash of url -> organization 

2. Each time a poller is run, we'll preference those dynamic feeds which have been updated the longest ago. However, there will be an upper limit to this preference, and every poller will have a minimum frequency with which it runs.  For those feeds we do poll, we'll only execute computationally intensive tasks (like parsing and extraction) for entities that are not yet in their respective sets.

3. If we do find a new entity, we'll insert it into it's respective table in **postgres**, with added information to associate it with a particular organization.

4. Finally, we'll issue a simple message to `newslynx-queue` in the following format: 
  * channel = "<org_id>:<source_type>"
  * message = "<source_id>" # maybe other json as well.

The messages from this queue will then be served via a subscribable API.
This queue will help power **pollster**, the approval river, and imapact recipes
** NOTE ** 
Some feeds will not specifically associated with specific organizations, like `twitter-lists`.

## Schema:
```
  # ARTICLES
  articles.org_id – String
  articles.url – String
  articles.domain – String
  articles.simple_domain – String
  articles.slug –  String
  articles.hash – String
  articles.meta_description – String
  articles.meta_lang – String
  articles.meta_favicon –     String
  articles.img – String
  articles.thumb – String
  articles.text – String
  articles.article_html –  String
  articles.title – String
  articles.pub_datetime – DateTime
  articles.pub_date – Date 
  articles.meta_keywords –  ARRAY(String)
  articles.authors – ARRAY(String)
  articles.int_links – ARRAY(String)
  articles.ext_links – ARRAY(String)
  articles.tags – ARRAY(String)
  articles.keywords – ARRAY(String)
  articles.img_urls – ARRAY(String)
  articles.movies – ARRAY(String)


  # GALERTS
  galerts.galert_id – String 
  galerts.feed_url – String 
  galerts.url – String 
  galerts.title – String 
  galerts.summary – String 
  galerts.datetime – DateTime

  # TWITTER
  # Tweets
  twitter.twitter_id –  String
  twitter.org_id – String
  twitter.query – String
  twitter.list_name – String
  twitter.list_owner – String
  twitter.text – String
  twitter.profile_img – String
  twitter.screen_name – String
  twitter.in_reply_to_status_id – String
  twitter.in_reply_to_screen_name – String
  twitter.datetime – DateTime
  twitter.favorites – Numeric
  twitter.followers – Numeric
  twitter.friends – Numeric
  twitter.retweets – Numeric
  twitter.verified – Numeric
  twitter.hashtags – ARRAY(String)
  twitter.urls – ARRAY(String)
  twitter.user_mentions –     ARRAY(String)
  twitter.img_urls – ARRAY(String)

  #User Stats
  twitter_user_stats.user_stats_id – String
  twitter_user_stats.org_id – String
  twitter_user_stats.datetime – DateTime
  twitter_user_stats.screen_name – String
  twitter_user_stats.favorites – Numeric
  twitter_user_stats.followers – Numeric 
  twitter_user_stats.friends – Numeric 
  twitter_user_stats.listed – Numeric
  twitter_user_stats.statuses – Numeric 
  
  # FACEBOOK
  # Posts #
  facebook_posts.org_id – String
  facebook_posts.page_id – String
  facebook_posts.post_id – String
  facebook_posts.urls – ARRAY(String)
  facebook_posts.datetime – DateTime
  facebook_posts.message – String
  facebook_posts.description – String
  facebook_posts.status_type – String
  facebook_posts.type – String

  # Page Stats
  facebook_page_stats.org_id –String
  facebook_page_stats.page_stats_id –String
  facebook_page_stats.page_id –String
  facebook_page_stats.page_talking_about_count –Numeric
  facebook_page_stats.page_likes –String
  facebook_page_stats.datetime –DateTime
  # TODO Explicit definitions for stats
  
  # Insights
  facebook_insights.insights_id – String
  facebook_insights.org_id – String
  facebook_insights.page_id – String
  facebook_insights.post_id – String
  facebook_insights.datetime – DateTime

  # HOMEPAGES
  homepages.homepage – String 
  homepages.homepage_id – String 
  homepages.org_id – String 
  homepages.datetime – DateTime 
  homepages.headline – String 
  homepages.url – String
  homepages.font_size – Numeric
  homepages.x – Numeric
  homepages.y – Numeric
  homepages.x_bucket – Numeric 
  homepages.y_bucket – Numeric
  homepages.bucket – Numeric
  homepages.has_img – Numeric
  homepages.img_width – Numeric
  homepages.img_height – Numeric
  homepages.img_area – Numeric
  homepages.img_src – String
```

