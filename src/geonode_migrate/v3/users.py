from ..config import Config
from ..utils import generate_password
from tinydb.database import Document
import click
import pathlib


def pull_users(conf: Config):
    response = conf.session.get(f'{conf.base_url}/api/owners/')
    data = response.json()

    table = conf.db.table('users')

    click.echo(f"Found users: {data['meta']['total_count']}")

    for doc in data['objects']:
        if not conf.force and table.contains(doc_id=doc['id']):
            click.echo(f'already downloaded {doc["id"]} - {doc["username"]}')
            continue

        doc['password'] = generate_password()

        table.upsert(Document(doc, doc_id=doc['id']))
        click.echo(f'downloaded {doc["id"]} - {doc["username"]}')
    

def pull_groups(conf: Config):
    table = conf.db.table('groups')
    response = conf.session.get(f'{conf.base_url}/api/groups/')
    data = response.json()
    docs_dir = conf.output_path / 'groups'
    docs_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Found groups: {data['meta']['total_count']}")

    for doc in data['objects']:
        if not conf.force and table.contains(doc_id=doc['id']):
            click.echo(f'already downloaded {doc["id"]} - {doc["title"]}')
            continue

        if doc['logo']:
            logo = pathlib.Path(doc['logo'])
            doc["file_position"] = str(docs_dir / logo.name )
            print(doc["file_position"])

            response = conf.session.get(f"{conf.base_url}{doc['logo']}")
            with open(doc["file_position"], 'wb') as f:
                f.write(response.content)
        else:
            doc["file_position"] = None

        table.upsert(Document(doc, doc_id=doc['id']))
        click.echo(f'downloaded {doc["id"]} - {doc["title"]}')

