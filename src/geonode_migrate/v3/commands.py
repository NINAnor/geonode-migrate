import click
from ..config import Config
from .documents import pull_documents
from .layers import pull_layers
from .users import pull_users, pull_groups
from .keywords import pull_keywords
from .maps import pull_maps

@click.group()
@click.option('-o', '--output', default='data')
@click.option('-f', '--force', is_flag=True)
@click.pass_context
def v3(ctx, output, force):
    ctx.ensure_object(dict)
    conf = Config(
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
def download_keywords(ctx):
    conf = ctx.obj['config']
    pull_keywords(conf)


@v3.command()
@click.pass_context
def download_users(ctx):
    conf = ctx.obj['config']
    pull_users(conf)


@v3.command()
@click.pass_context
def download_groups(ctx):
    conf = ctx.obj['config']
    pull_groups(conf)


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
    pull_groups(conf)
    pull_keywords(conf)
    pull_layers(conf)
    pull_documents(conf)
    pull_maps(conf)
