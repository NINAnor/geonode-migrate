import click
from ..config import Config
from .documents import pull_documents
from .layers import pull_layers
from .users import pull_users
from .maps import pull_maps

@click.group()
@click.option('-u', '--url', required=True, help="URL of the Geonode 3 instance")
@click.option('-o', '--output', default='data')
@click.option('-f', '--force', default=False)
@click.pass_context
def v3(ctx, url, output, force):
    ctx.ensure_object(dict)
    conf = Config(
        base_url=url,
        output=output,
        force=force,
    )
    conf.login(version=3)

    ctx.obj['config'] = conf



@v3.command()
@click.pass_context
def download_documents(ctx):
    conf = ctx.obj['config']
    pull_documents(conf)


@v3.command()
@click.pass_context
def download_layers(ctx):
    conf = ctx.obj['config']
    pull_layers(conf)



@v3.command()
@click.pass_context
def download_users(ctx):
    conf = ctx.obj['config']
    pull_users(conf)


@v3.command()
@click.pass_context
def download_maps(ctx):
    conf = ctx.obj['config']
    pull_maps(conf)


@v3.command()
@click.pass_context
def download(ctx):
    conf = ctx.obj['config']
    pull_users(conf)
    pull_layers(conf)
    pull_documents(conf)
    pull_maps(conf)
