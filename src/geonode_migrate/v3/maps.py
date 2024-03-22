from ..config import Config
from tinydb.database import Document
import click


def pull_maps(conf: Config):
    response = conf.session.get(f'{conf.base_url}/api/maps/')
    data = response.json()

    table = conf.db.table('maps')

    click.echo(f"Found users: {data['meta']['total_count']}")

    for doc in data['objects']:
        if not conf.force and table.contains(doc_id=doc['id']):
            click.echo(f'already downloaded {doc["id"]} - {doc["title"]}')
            continue

        response = conf.session.get(f'{conf.base_url}/api/maps/{doc["id"]}')
        data = response.json()
        table.upsert(Document(data, doc_id=data['id']))

        click.echo(f'downloaded {doc["id"]} - {doc["title"]}')
