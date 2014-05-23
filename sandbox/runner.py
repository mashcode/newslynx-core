import json
import yaml
import tarjan
import os
import importlib
from glob import glob
from tarjan import tc

import utils


class Recipe(object):
    def __init__(self, location):
        self.name = location.split('/')[0]
        self.steps = []
        self.schema = {}

        for f in glob(location + '.yml'):
            self.add(Step(f, self))

    @property
    def dependencies(self):
        return {step: step.dependencies for step in self.steps}

    @property
    def workflow(self):
        """ Generates a feasible order of execution based on 
        whatever dependencies have been stated. """
        return map(utils.first, tarjan.tarjan(self.dependencies))

    def add(self, step):
        self.steps.append(step)
        self.schema.update(step.schema)

    def to_sequelize(self):
        flattened_schema = utils.deflate(self.schema)
        return {k: v.upper() for k, v in flattened_schema.items()}

    def to_sql(self):
        flattened_schema = utils.deflate(self.schema)
        return utils.create_table_sql('articles', flattened_schema, 'url')

    def alter_sql(self, existing_columns):
        """
        You would get the existing columns like this: 

            SELECT * FROM information_schema.columns
            WHERE table_name = {name};

        """

        flattened_schema = utils.deflate(self.schema)
        new_columns = flattened_schema.keys()
        new_fields = set(new_columns).difference(set(existing_columns))
        alterations = [utils.alter_table_sql('articles', column) for column in new_fields]
        return ";\n".join(alterations)

    def to_job(self, concat=True):
        # concatenation means that we execute all steps together in one
        # big map operation, which is actually what we want to do most
        # of the time
        if concat:
            raise NotImplementedError()
        else:
            return map(lambda step: step.to_phase(), self.workflow)

    def run(self):
        """
        Steps that run later can overwrite existing properties.

        Steps however do not need to include existing fields in their return value
        (and indeed cannot delete existing fields at all.)
        """
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
        self.environment = spec.get('environment')
        self._dependencies = set(spec.get('dependencies', []))
        self.description = spec.get('description')
        self.schema = spec['schema']
        self.keys = utils.deflate(self.schema, '.').keys()
        self.requirements = set(spec.get('requirements', []))
        self.fn = getattr(importlib.import_module('analyses.' + self.name), self.name)

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
            'dependencies': self.environment, 
        }

    def run(self, data={}):
        return self.fn(data)

    def __eq__(self):
        return self.name

    def __repr__(self):
        return "<Step: {}>".format(self.name)



if __name__ == '__main__':
    recipe = Recipe('analyses/*')
    print recipe.steps
    print recipe.run()
    print json.dumps(recipe.schema, indent=4)
    print recipe.to_sql()
    print recipe.to_sequelize()
    print recipe.alter_sql(['url', 'title'])
    print json.dumps(recipe.to_job(), indent=4)