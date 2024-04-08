from ..config import Config
from tinydb.database import Document
import click


def pull_keywords(conf: Config):
    response = conf.session.get(f'{conf.base_url}/api/keywords/')
    data = response.json()

    table = conf.db.table('keywords')

    click.echo(f"Found keywords: {data['meta']['total_count']}")

    for doc in data['objects']:
        if not conf.force and table.contains(doc_id=doc['id']):
            click.echo(f'already downloaded {doc["id"]} - {doc["name"]}')
            continue

        response = conf.session.get(f'{conf.base_url}/api/keywords/{doc["id"]}')
        data = response.json()
        table.upsert(Document(data, doc_id=data['id']))

        click.echo(f'downloaded {doc["id"]} - {doc["name"]}')
