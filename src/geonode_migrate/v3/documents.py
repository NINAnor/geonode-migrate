from ..config import Config
from tinydb.database import Document
from pathlib import Path
import click

def pull_documents(conf: Config):
    # TODO: handle pagination
    response = conf.session.get(f'{conf.base_url}/api/documents/')
    data = response.json()

    docs_table =conf.db.table('documents')
    docs_dir = conf.output_path / 'documents'
    docs_dir.mkdir(parents=True, exist_ok=True)

    for doc in data['objects']:
        response = conf.session.get(f'{conf.base_url}/api/documents/{doc["id"]}')
        doc_data = response.json()

        del doc_data['csw_anytext']
        del doc_data['metadata_xml']

        if not Path(doc_data['title']).suffixes:
            title = f"{doc_data['title']}.{doc_data['extension']}"
        else:
            title = doc_data['title']

        doc_data["file_position"] = str(docs_dir / title)

        response = conf.session.get(f"{conf.base_url}/documents/{doc_data['id']}/download")
        with open(doc_data["file_position"], 'wb') as f:
            f.write(response.content)

        docs_table.upsert(Document(doc_data, doc_id=doc_data['id']))
        click.echo(f'downloaded {doc["id"]} - {doc["title"]}')
