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
 - [ ] `newslynx_core.database.db`. 
  * The `dataset` object and explicit **postgresql** schema definitions for each source table. 
 - [x] `newslynx_core.controller.Controller`
  * A **redis** controller for Sources.
  * contains methods for de-duplication, messaging, and flushing
 - [x] `newslnyx_core.source.Source`
  * An abstract class for grabbing data from any source.
  * For each source, inherit this class and overwrite `.task_id()`, `poller`, `parser`, and `messenger`.
  * this process will run on **gevent** queues, checking for duplicates via `Controller`,
    and inserting new records into `db`
 - [ ] `newlynx_core.poll.Poll`
  * An abstract class for Polling multiple sources
  * Uses `Contoller` to determine what to poll when.
 - [x] `FeedParser`
 - [ ] `GAlert`
 - [ ] `Facebook`
   * parsing facebook posts
 - [ ] `Twitter`
   * search twitter
   * build lists
   * parse lists
   * parse users
   * reading from streaming API (one set method, polls all org domains and shortlinks and checks for valid urls)
- [ ] `Homepage`, detect what aritcle links are on each organization's homepage, when.

## Framework:

Data will be polled from various sources using this basic straegy:

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

## Data Sources

### Articles

### RSS Feeds

### Homeapges

### Twitter Lists

### Twitter Streaming

### Google Alerts

### Facebook Pages
   
