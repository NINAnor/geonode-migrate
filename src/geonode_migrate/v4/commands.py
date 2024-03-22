import click
from ..config import Config
from .documents import push_documents
from .layers import push_layers
from .users import push_users

@click.group()
@click.option('-o', '--output', default='data')
@click.pass_context
def v4(ctx, output):
    ctx.ensure_object(dict)
    conf = Config(
        output=output,
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
def upload_users(ctx):
    conf = ctx.obj['config']
    push_users(conf)


@v4.command()
@click.pass_context
def upload(ctx):
    conf = ctx.obj['config']
    push_users(conf)
    push_documents(conf)
    push_layers(conf)
