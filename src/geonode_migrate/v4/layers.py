from ..config import Config
from ..utils import get_csrf_token
from tinydb.database import Document
import click


def push_layers(conf: Config):
    table = conf.db.table('layers')
    for d in table.all():
        print(d['file_position'])
        with open(d['file_position'], 'rb') as f:
            csrf, response = get_csrf_token(conf.session, f'{conf.base_url}/')
            conf.session.headers.update({'X-Csrftoken': csrf})

            print(d['storeType'])

            response = conf.session.post(f'{conf.base_url}/api/v2/uploads/upload/', data={'store_spatial_files': "true", "time": "false"}, files={
                'base_file': f,
                # 'zip_file': f,
            })

            try:
                response.raise_for_status()
                content = response.json()
                print(content)
                # id = content['url'].split('/')[-1]

                # conf.session.patch(f'{conf.base_url}/api/v2/documents/{id}/', json={
                #     'abstract': d['abstract']
                # })

                # table.upsert(Document({'__upload__': True }), doc_id=d['id'])
                click.echo(f'uploaded {d["title"]}')
            except Exception as e:
                click.echo(f'error uploading {d["title"]} - {e}')
                print(response.text)

        break