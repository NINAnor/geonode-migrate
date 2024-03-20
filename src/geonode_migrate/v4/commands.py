import click
from ..config import Config
from .documents import push_documents
from .layers import push_layers

@click.group()
@click.option('-u', '--url', required=True, help="URL of the Geonode 4 instance")
@click.option('-o', '--output', default='data')
@click.pass_context
def v4(ctx, url, output):
    ctx.ensure_object(dict)
    conf = Config(
        base_url=url,
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
