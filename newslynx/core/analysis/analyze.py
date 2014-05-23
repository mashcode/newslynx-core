import json
import sys
import os
import importlib
import textwrap
from glob import glob

import yaml
import manta
import askmanta
from tarjan import tarjan, tc

import utils
client = utils.client

def first(l):
    return l[0]

def deflate(obj, connector='-', parent_key=''):
    items = []

    for k, v in obj.items():
        if parent_key:
            new_key = parent_key + connector + k
        else:
            new_key = k

        if isinstance(v, dict):
            items.extend(deflate(v, connector, new_key).items())
        elif isinstance(v, list):
            value_type = v[0] + '[]'
            items.append((new_key, value_type))
        else:
            items.append((new_key, v))


    return dict(items)

def serialize_column(key, cast):
    return key + " " + cast

def alter_table_sql(name, column):
    return "ALTER TABLE {name} ADD COLUMN {column}".format(**locals())

def create_table_sql(name, columns, pk):
    definitions = ',\n    '.join([serialize_column(n, t) for n, t in columns.items()])

    return textwrap.dedent("""
        CREATE TABLE {name} (
            {definitions},
            PRIMARY KEY({pk})
        )
        """).format(**locals())


class Recipe(object):
    def __init__(self, location):
        self.name = location.split('/')[0]
        self.steps = []
        self.schema = {}

        print location, glob(location + '.yml')

        for f in glob(location + '.yml'):
            self.add(Step(f, self))

    @property
    def dependencies(self):
        return {step: step.dependencies for step in self.steps}

    @property
    def environment(self):
        _environment = {}

        for step in self.steps:
            for scope, env in step.environment.items():
                _environment.setdefault(scope, []).extend(env)

        return _environment

    @property
    def workflow(self):
        """ Generates a feasible order of execution based on 
        whatever dependencies have been stated. """
        return map(first, tarjan(self.dependencies))

    def add(self, step):
        self.steps.append(step)
        self.schema.update(step.schema)

    def to_sql(self):
        flattened_schema = deflate(self.schema)
        return create_table_sql('articles', flattened_schema, 'url')

    def alter_sql(self, existing_columns):
        """
        You would get the existing columns like this: 

            SELECT * FROM information_schema.columns
            WHERE table_name = {name};

        """

        flattened_schema = deflate(self.schema)
        new_columns = flattened_schema.keys()
        new_fields = set(new_columns).difference(set(existing_columns))
        alterations = [alter_table_sql('articles', column) for column in new_fields]
        return ";\n".join(alterations)

    def to_job(self):
        return map(lambda step: step.to_phase(), self.workflow)

    def run(self, data=None):
        """
        Steps that run later can overwrite existing properties.

        Steps however do not need to include existing fields in their return value
        (and indeed cannot delete existing fields at all.)
        """

        if not data:
            data = {}

        for step in self.steps:
            data.update(step.run(data))
        return data

class Step(object):
    """
    Schemas do not need to be strictly columnar. Deep structures
    will simply be flattened, so that `{field: {subfield: type}}`
    will be stored in Postgres as `field-subfield`.

    When specifying that a step requires certain fields to be present, 
    you can refer to such fields using dot notation: `field.subfield`.

    Arrays are supported as well, but they cannot contain complex data
    structures, only scalars. E.g. `myfield: [float]` is allowed.

    Any Postgres type can be used in specifying a schema, but 
    it is probably best to stick to these: 

        * text
        * integer
        * float
        * timestamp
        * date
        * datetime

    """

    def __init__(self, specpath, recipe):
        self.specpath = specpath
        self.path = specpath.replace('.yml', '.py')
        self.recipe = recipe
        self.name = os.path.splitext(os.path.basename(specpath))[0]
        self.spec = spec = yaml.load(open(specpath))
        self.environment = spec.get('environment', {})
        self._dependencies = set(spec.get('dependencies', []))
        self.description = spec.get('description')
        self.schema = spec.get('schema', {})
        self.keys = deflate(self.schema, '.').keys()
        self.requirements = set(spec.get('requirements', []))
        self.fn = getattr(importlib.import_module(self.name), self.name)

    @property
    def dependencies(self):
        _dependencies = set([step for step in self.recipe.steps if step.name in self._dependencies])

        for step in self.recipe.steps:
            if step is self:
                continue

            needs = set(step.keys).intersection(self.requirements)
            if len(needs):
                _dependencies.add(step)

            return _dependencies

    def to_phase(self):
        return {
            'script': self.path, 
            'dependencies': list(self.environment), 
        }

    def run(self, data={}):
        return self.fn(data)

    def __eq__(self):
        return self.name

    def __repr__(self):
        return "<Step: {}>".format(self.name)


if __name__ == '__main__':
    # CONSIDER: 
    # it might be smarter to use `mpipe` to control output naming, 
    # but then, this shouldn't be that slow either

    filename = sys.stdin.readline().strip()
    destination = os.path.normpath(os.path.join(filename, '../../analysis'))

    raw = client.get_object(filename)

    repository = sys.argv[1]
    sys.path.insert(0, repository)
    searchpath = os.path.join(sys.argv[1], '*')
    recipe = Recipe(searchpath)

    data = recipe.run({'raw': raw})
    del data['raw']
    current, snapshot = utils.versioned_save(destination, 'json', json.dumps(data))

    print current
    print snapshot

    if len(sys.argv) > 2 and sys.argv[2] == 'debug':
        print recipe.steps
        print recipe.run()
        print json.dumps(recipe.schema, indent=4)
        print recipe.to_sql()
        print recipe.alter_sql(['url', 'title'])
        print json.dumps(recipe.to_job(), indent=4)
        print recipe.environment