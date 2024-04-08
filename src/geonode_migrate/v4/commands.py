import click
from ..config import Config
from .documents import push_documents
from .layers import push_layers, sync_layers as sync_layers_fn
from .users import push_users
from .maps import push_maps

@click.group()
@click.option('-o', '--output', default='data')
@click.option('-f', '--force', is_flag=True)
@click.pass_context
def v4(ctx, output, force):
    ctx.ensure_object(dict)
    conf = Config(
        output=output,
        force=force,
    )
    conf.login(version=4)

    ctx.obj['config'] = conf



@v4.command()
@click.pass_context
def upload_documents(ctx):
    conf = ctx.obj['config']
    push_documents(conf)


@v4.command()
@click.pass_context
def upload_layers(ctx):
    conf = ctx.obj['config']
    push_layers(conf)


@v4.command()
@click.pass_context
def sync_layers(ctx):
    conf = ctx.obj['config']
    sync_layers_fn(conf)

@v4.command()
@click.pass_context
def upload_users(ctx):
    conf = ctx.obj['config']
    push_users(conf)


@v4.command()
@click.pass_context
def upload_maps(ctx):
    conf = ctx.obj['config']
    push_maps(conf)


@v4.command()
@click.pass_context
def upload(ctx):
    conf = ctx.obj['config']
    push_users(conf)
    push_maps(conf)
    push_documents(conf)
    push_layers(conf)
