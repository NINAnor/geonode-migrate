import click
from .config import Config
from geonode_migrate.v3.commands import v3
from geonode_migrate.v4.commands import v4
from .commands import manage

@click.group()
def cli():
    pass

cli.add_command(v3)
cli.add_command(v4)
cli.add_command(manage)
