from ..config import Config
from tinydb.database import Document
import click


def pull_users(conf: Config):
    response = conf.session.get(f'{conf.base_url}/api/owners/')
    data = response.json()

    table = conf.db.table('users')

    click.echo(f"Found users: {data['meta']['total_count']}")

    for doc in data['objects']:
        if not conf.force and table.contains(doc_id=doc['id']):
            click.echo(f'already downloaded {doc["id"]} - {doc["title"]}')
            continue

        table.upsert(Document(doc, doc_id=doc['id']))
        click.echo(f'downloaded {doc["id"]} - {doc["username"]}')
    
    response = conf.session.get(f'{conf.base_url}/api/groups/')
    data = response.json()

    table = conf.db.table('groups')

    click.echo(f"Found groups: {data['meta']['total_count']}")

    for doc in data['objects']:
        if not conf.force and table.contains(doc_id=doc['id']):
            click.echo(f'already downloaded {doc["id"]} - {doc["title"]}')
            continue

        table.upsert(Document(doc, doc_id=doc['id']))
        click.echo(f'downloaded {doc["id"]} - {doc["name"]}')

