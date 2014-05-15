import json
import yaml
import tarjan
import os
import importlib
from glob import glob
from tarjan import tc

import utils

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

    all = []
    schema = {}

    @classmethod
    def add(cls, subcls):
        cls.all.append(subcls)
        cls.schema.update(subcls.schema)

    def __init__(self, path):
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]
        self.spec = spec = yaml.load(open(path))
        self._dependencies = set(spec.get('dependencies', []))
        self.description = spec.get('description')
        self.schema = spec['schema']
        self.keys = utils.deflate(self.schema, '.').keys()
        self.requirements = set(spec.get('requires', []))
        self.fn = getattr(importlib.import_module('analyses.' + self.name), self.name)
        
        Step.add(self)

    @property
    def dependencies(self):
        _dependencies = set([step for step in Step.all if step.name in self._dependencies])

        for step in self.__class__.all:
            if step is self:
                continue

            needs = set(step.keys).intersection(self.requirements)
            if len(needs):
                _dependencies.add(step)

            return _dependencies

    def run(self, data={}):
        return self.fn(data)

    @classmethod
    def to_sql(cls):
        flattened_schema = utils.deflate(cls.schema)
        return utils.create_table_sql('articles', flattened_schema, 'url')

    @classmethod
    def alter_sql(cls, existing_columns):
        """
        You would get the existing columns like this: 

            SELECT * FROM information_schema.columns
            WHERE table_name = {name};

        """

        flattened_schema = utils.deflate(cls.schema)
        new_columns = flattened_schema.keys()
        new_fields = set(new_columns).difference(set(existing_columns))
        alterations = [utils.alter_table_sql('articles', column) for column in new_fields]
        return ";\n".join(alterations)

    def __eq__(self):
        return self.name

    def __repr__(self):
        return "<Step: {}>".format(self.name)


steps = [Step(f) for f in glob('analyses/*.yml')]
dependencies = {step: step.dependencies for step in steps}

# tarjan generates the required order of execution
recipe = map(utils.first, tarjan.tarjan(dependencies))

"""
Steps that run later can overwrite existing properties.

Steps however do not need to include existing fields in their return value
(and indeed cannot delete existing fields at all.)
"""

if __name__ == '__main__':

    data = {}
    for step in recipe:
        data.update(step.run(data))

    print recipe

    print data

    print json.dumps(Step.schema, indent=4)

    print Step.to_sql()

    print Step.alter_sql(['url', 'title'])