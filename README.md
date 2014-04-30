This is a proposal for one way we could handle the data collection and analysis: as a bunch of map-reduce jobs. A basic map-reduce job is implemented here:

* grab the feeds
* extract article urls
* download the HTML
* extract the content

Look at `download.py` and `analyze.py` to get an idea of how the code would work.

Look at `ingestion.yml` to get an idea of how the job is specified.