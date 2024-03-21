from ..config import Config
from tinydb.database import Document
from pathlib import Path
import click
import zipfile
import io


def pull_users(conf: Config):
    response = conf.session.get(f'{conf.base_url}/api/owners/')
    data = response.json()

    table = conf.db.table('users')

    click.echo(f"Found users: {data['meta']['total_count']}")

    for doc in data['objects']:
        table.upsert(Document(doc, doc_id=doc['id']))

        click.echo(f'downloaded {doc["id"]} - {doc["username"]}')
