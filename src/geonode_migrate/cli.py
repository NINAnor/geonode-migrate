import click

from geonode_migrate.v3.commands import v3
from geonode_migrate.v4.commands import v4

@click.group()
def cli():
    pass

cli.add_command(v3)
cli.add_command(v4)
