import textwrap

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