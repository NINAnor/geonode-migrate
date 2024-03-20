from ..config import Config
from ..utils import get_csrf_token
from tinydb.database import Document
import click


def push_documents(conf: Config):
    table = conf.db.table('documents')
    for d in table.all():
        with open(d['file_position'], 'rb') as f:
            csrf, response = get_csrf_token(conf.session, f'{conf.base_url}/')
            conf.session.headers.update({'X-Csrftoken': csrf})

            response = conf.session.post(f'{conf.base_url}/documents/upload?no__redirect=true', data={'title': d['title']}, files={
                'doc_file': f
            })

            try:
                response.raise_for_status()
                content = response.json()
                id = content['url'].split('/')[-1]

                conf.session.patch(f'{conf.base_url}/api/v2/documents/{id}/', json={
                    'abstract': d['abstract']
                })

                table.upsert(Document({'__upload__': True }), doc_id=d['id'])
                click.echo(f'uploaded {d["title"]}')
            except Exception:
                click.echo(f'error uploading {d["title"]}')
