from ..config import Config
from ..utils import get_csrf_token
from tinydb.database import Document
import click
import time


# TODO: use backoff
def check_execution(conf, id):
    while True:
        response = conf.session.get(f'{conf.base_url}/api/v2/executionrequest/{id}')
        response.raise_for_status()
        content = response.json()
        print(content)

        status = content['request']['status']
        if status == 'finished':
            break
        elif status == 'failed':
            raise Exception('Failed')
        
        time.sleep(5)

    return content


def push_layers(conf: Config):
    table = conf.db.table('layers')
    for d in table.all():
        if '__new_id__' in d and not conf.force:
            print('already uploaded')
            continue

        csrf, response = get_csrf_token(conf.session, f'{conf.base_url}/')
        conf.session.headers.update({'X-Csrftoken': csrf})

        files = {}
        for key, path in d['__files__'].items():
            files[key] = open(path, 'rb')

        response = conf.session.post(f'{conf.base_url}/api/v2/uploads/upload/', data={'store_spatial_files': "true", "time": "false", "overwrite_existing_layer": True}, files=files)

        for file in files.values():
            file.close()

        exec_id = None

        try:
            response.raise_for_status()
            content = response.json()
            print(content)
            exec_id = content['execution_id']
            click.echo(f'upload started{d["title"]}')
        except Exception as e:
            click.echo(f'error uploading {d["title"]} - {e}')
            print(response.text)

        last = None
        try:
            last = check_execution(conf, exec_id)
        except Exception as e:
            print(e)
            continue

        try:
            id = last['request']['output_params']['detail_url'][0].split('/')[-1]
        except Exception as e:
            print(e)
            continue

        response = conf.session.patch(
            f'{conf.base_url}/api/v2/datasets/{id}/', 
            json={
                'title': d['title'],
                'abstract': d['abstract']
            })
        print(response.text)

        table.upsert(Document({'__new_id__': id }, doc_id=d['id']))
        
        print('done')
