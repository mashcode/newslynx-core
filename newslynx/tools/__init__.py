import json
import argparse


# TODO: figure out where to get the recipes
def schema(arguments):
    if arguments.alter:
        print recipe.alter_sql(existing_fields)
    elif arguments.sql:
        print recipe.to_sql()
    else:
        print json.dumps(recipe.schema, indent=4)
    

arguments = argparse.ArgumentParser()
subparsers = arguments.add_subparsers()

build = subparsers.add_parser('schema',
    help="describe the output schema of a map/reduce job")
build.set_defaults(func=schema)
build.add_argument('--sql',
    default=False, action='store_true',
    help="output the schema as a SQL table description")
build.add_argument('--alter',
    default=False, action='store_true',
    help="output the schema as a series of SQL alter statements")

if __name__ == '__main__':
    args = arguments.parse_args()
    args.func(args)