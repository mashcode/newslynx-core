`newslynx-core` contains all NewsLynx functionality related to scraping, ingestion and analysis of articles, tweets, Facebook posts and so on.

## Storage

`newslynx-core` consists mainly of a bunch of standalone scripts that are glued together into map/reduce jobs. The output of these jobs is saved both to flat files and to Postgres. Some of these jobs to also signal external services of certain events. For example, when we've ingested new articles, our Pollster social media tracker will be asked to start tracking that content.

## Jobs

### Configuring a job

Jobs are described in [askmanta](https://github.com/stdbrouw/askmanta) YAML job files that tell Manta which scripts to run and what dependencies they need (files, linux packages, python modules).

A job configuration file might look like this: 

    - script: "organizations.py"
      inputs:
        - /var/tmp/files/organizations.yml
      dependencies:
        files:
          - ../../fixtures/organizations.yml
    - script: "feeds.py"
      dependencies:
        python:
          - requests
          - feedparser
          - manta

Note that while the askmanta job runner currently doesn't support running jobs locally, it is still really easy to test out your scripts, because Manta jobs translate fairly transparently into bash commands with piping. For example, the previous job configuration translates to: 

    cd newslynx/core;
    cat fixtures/organizations.yml \
        | python core/ingestion/organizations.py \
        | python core/ingestion feeds.py;

### Coding a job

Job steps can be both python scripts, specified using `script`, or commands, specified using `sh`. They have no special requirements: they take in `stdin` and they output to `stdout`, that's it.

Note that these scripts are not loaded as modules, but are executed using `python <script>.py`. Therefore, make sure to specify any dependencies on other Python files in the job description, because, for the sake of performance, you can't expect the entire source tree of `newslynx-core` to be present on the Manta compute system.

### Configuring an analysis step

The `analysis` job is the true heart of `newslynx-core`. It contains all of the content extraction and analyses that we perform on article content.

For this `analysis` job, in addition to an `analyze.yml` job file there are also configuration files for each step. They have the same filename as the analysis, but with a `.yml` extension. For example, the analysis that extracts the author(s) from an article is called `authors.py` and its config file is `authors.yml`

A step configuration file might look like this: 

    description: Extract keywords from the body copy as well as tags from the raw HTML.
    dependencies:
        - meta
    requirements:
        - body
    environment:
        python:
            - nltk
    schema:
        tags: text[]
        keywords: text[]

The step configuration may specifies three separate kinds of dependencies: 

* `environment` specifies dependencies on modules, packages and files -- this works identically to job config files
* `dependencies` specifies other analyses that should run first. In the example, the `meta` analysis step should run before the current step.
* `requirements` specifies that certain data should be present before this step can run. In the example, the `body` field needs to be present because this step will operate on that field.

Internally, `environment` gets added to the global job configuration. `requirements` will be analyzed to see which job provides that requirement and then merged with the information from `dependencies` this will be used to automatically determine the right order of execution. You don't need to worry about what order the analyses should run in, you only need to tell the system what each analysis needs, and the rest is taken care of.

Usually, you will want to use `requirements` in lieu of `dependencies` to specify the exact data you need, but sometimes it might be quicker or more useful to explicitly specify the other analyses you're depending on, and the `dependencies` configuration option will help with that.

You will find most of the logic just described in `core/analysis/analyze.py`.

### Coding an analysis step

For analysis steps, the expectation is that you will create an `<analysis>.py` file inside of the `core/analysis` directory, and inside of that file an `<analysis>` function, named identically to the file. This function will receive a dictionary and should return another dictionary. The return value need not include any of the data received (though it may). The return value only needs to contain newly added or modified fields.

For example: 

    def uppercase(data):
        return {
            'screaming-headline': data['title'].upper()
        }

## Schema

Storage in flat files is schemaless by nature. However, to determine the correct order of execution and also because we keep a copy of our data in a SQL database, it is necessary for analyses to specify their schema: the fields that they will `return`.

Schemas do not need to be strictly columnar. Deep structures will simply be flattened, so that `{field: {subfield: type}}` will be stored in Postgres as `field-subfield`.

Elsewhere in the configuration file, when specifying that a step requires certain fields to be present, you can refer to such fields in `requirements` using dot notation: `field.subfield`.

Arrays are supported as well. Simply append `[]` to the field type. Arrays cannot contain complex data structures, only scalars. E.g. `myfield: [float]` is allowed, as are strings, dates and such, but not objects.

Any Postgres type can be used in specifying a schema, but it is probably best to stick to these: 

    * text
    * integer
    * float
    * timestamp
    * date
    * datetime

Note that it does not make sense to use limited-length types like `char` or `varchar`, as these provide hardly any performance benefit in Postgres over `text` which is unlimited in length.

An example schema might be:

    schema:
        title: text
        authors: text[]
        social:
            facebook:
                shares: integer
                likes: integer

### Tools for working with the schema

The analysis runner can build up the entire schema for the `articles` table using of the information it has gathered from all of the individual analyses. The intent is to turn this into a commandline interface that can then create that table as well as inspect an existing table to see what fields should be added, modified or deleted -- but for safety's sake, leaving the actual execution of these steps to a human.

This same tool, currently functional but not exposed yet as a CLI, can also show the full JSON schema.

## Scheduling jobs

For now, the idea is to schedule jobs at regular intervals using `cron`. When the job pipeline and dependencies between jobs become an issue, we might take a look at tools like [Luigi](https://github.com/spotify/luigi).

## General thoughts about the architecture.

Currently, the architecture is based around the idea of map/reduce jobs. It should however be relatively straightforward (perhaps a day or two worth of work) to instead transfer information between different parts of a job using a message queue. You would still save everything to flat files and then to PostGres and all of the analysis and job specification code could stay similar or the same, but you'd "feed" it in a different way.

The advantage could be that you'd have finer control over parallellization. The disadvantage would be that you'd have to worry about running machines, deciding how many of them to run and making sure that they're not idling.

Because of the limited amount of work involved in switching to a MQ-based framework, we can think about this when the current approach becomes a nuisance, but don't really have to bother ourselves too much about it now.