import click
from .config import Config
from tinydb import where

@click.group()
@click.option('-o', '--output', default='data')
@click.pass_context
def manage(ctx, output):
    ctx.ensure_object(dict)
    conf = Config(
        output=output,
    )

    ctx.obj['config'] = conf


@manage.command()
@click.pass_context
def clean_users(ctx):
    conf = ctx.obj['config']
    conf.db.drop_table('users')
    conf.db.drop_table('groups')


@manage.command()
@click.argument('username')
@click.pass_context
def get_password(ctx, username):
    conf = ctx.obj['config']
    table = conf.db.table('users')

    users = table.search(where('username') == username)
    for u in users:
        click.echo(u['password'])
    
    if not users:
        click.echo('no user found')
