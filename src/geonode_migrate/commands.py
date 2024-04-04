import click
from .config import Config
from tinydb import where
from tinydb.operations import set, delete
from tinydb.database import Document


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


@manage.command()
@click.pass_context
def list_layers(ctx):
    conf = ctx.obj['config']
    for l in conf.db.table('layers').all():
        print(f"{l['id']} - {l['title']} --- {l['__new_id__'] if '__new_id__' in l else 'NOT UPLOADED'}")


@manage.command()
@click.pass_context
def list_users(ctx):
    conf = ctx.obj['config']
    for l in conf.db.table('users').all():
        print(f"{l['id']} - {l['username']} --- {l['__new_id__'] if '__new_id__' in l else 'NOT UPLOADED'}")



@manage.command()
@click.pass_context
def list_documents(ctx):
    conf = ctx.obj['config']
    for l in conf.db.table('documents').all():
        print(f"{l['id']} - {l['title']} --- {l['__new_id__'] if '__new_id__' in l else 'NOT UPLOADED'}")


@manage.command()
@click.pass_context
def list_maps(ctx):
    conf = ctx.obj['config']
    for l in conf.db.table('maps').all():
        print(f"{l['id']} - {l['title']} --- {l['__new_id__'] if '__new_id__' in l else 'NOT UPLOADED'}")


@manage.command()
@click.argument('table')
@click.pass_context
def clean_table(ctx, table):
    conf = ctx.obj['config']
    conf.db.table(table).update(set('__new_id__', None))
    conf.db.table(table).update(delete('__new_id__'))
    if table == 'layers':
        conf.db.table(table).update(set('__delete_path__', None))
        conf.db.table(table).update(delete('__delete_path__'))


@manage.command()
@click.argument('table')
@click.argument('id')
@click.option('-k', 'key')
@click.pass_context
def show_table_id(ctx, table, id, key=None):
    conf = ctx.obj['config']
    row = conf.db.table(table).get(doc_id=int(id))
    if key:
        print(row[key] if key in row else f'Row has no key {key}')
    else:
        print(row)


@manage.command()
@click.argument('table')
@click.argument('id', type=int)
@click.argument('key')
@click.argument('value')
@click.pass_context
def set_table_id(ctx, table, id, key, value):
    conf = ctx.obj['config']
    row = conf.db.table(table).get(doc_id=id)
    if row:
        conf.db.table(table).upsert(Document({key: value}, doc_id=id))
        print(conf.db.table(table).get(doc_id=id))
        print('done')

    else:
        print('row not found')
