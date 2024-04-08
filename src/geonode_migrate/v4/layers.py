from ..config import Config
from ..utils import get_csrf_token
from tinydb.database import Document
import click
import time
import pathlib


class FailedUpload(Exception):
    def __init__(self, *args: object, response = None) -> None:
        super().__init__(*args)
        self.__response = response

    
    def get_response(self):
        return self.__response


def get_filename(name):
    fname = pathlib.Path(name)
    return fname.name[:-len(''.join(fname.suffixes))]


# TODO: use backoff
def check_execution(conf, id):
    while True:
        status = 'continue'
        response = conf.session.get(f'{conf.base_url}/api/v2/executionrequest/{id}')
        try:
            response.raise_for_status()
            content = response.json()
            print(content)
            status = content['request']['status']
        except:
            time.sleep(5)
            continue

        if status == 'finished':
            break
        elif status == 'failed':
            raise FailedUpload('Failed', response=content)
        
        time.sleep(5)

    return content


def get_layer_id_by_name(conf, filename):
    name = get_filename(filename)
    print(name)
    response = conf.session.get(f'{conf.base_url}/api/v2/datasets/?filter{{name}}={name}')
    response.raise_for_status()
    content = response.json()
    print(content)
    if content['total'] != 1:
        raise Exception(f'found {content["total"]} datasets with that name')
    return content['datasets'][0]['pk']


def push_layers(conf: Config):
    table = conf.db.table('layers')
    for d in table.all():
        print(f"uploading {d['id']} - {d['title']} ## {d['__files__']['base_file'].split('/')[-1]}")
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
        id = None
        try:
            last = check_execution(conf, exec_id)
        except FailedUpload as e:
            id = 'FAILED'
            p = e.get_response()['request']['input_params']['files']['base_file']
            table.upsert(Document({'__delete_path__': p, '__new_id__': 'FAILED' }, doc_id=d['id']))
            continue
        else:
            output = last['request']['output_params']
            if 'detail_url' in output:
                try:
                    id = ['detail_url'][0].split('/')[-1]
                except Exception as e:
                    print(e)
                    continue
            else:
                print('terminated, but not found an id, trying to match by name')
                try:
                    id = get_layer_id_by_name(conf, last['request']['name'])
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


def sync_layers(conf: Config):
    table = conf.db.table('layers')
    for d in table.all():
        print(f"syncing {d['id']} - {d['title']} ## {d['__files__']['base_file'].split('/')[-1]} --- {d['__new_id__'] if '__new_id__' in d else 'NOT UPLOADED'}")
        if '__new_id__' not in d:
            try:
                id = get_layer_id_by_name(conf, d['__files__']['base_file'])
                print('found a layer with the same name')
                d['__new_id__'] = id
                table.upsert(Document({'__new_id__': id }, doc_id=d['id']))
            except Exception as e:
                print(e)
                continue
        elif d["__new_id__"] in ['FAILED', 'SKIP']:
            continue
        else:
            id = d["__new_id__"]

        data = {
                'title': d['title'],
                'title_en': d['title_en'],
                'abstract': d['abstract'],
                'abstract_en': d['abstract_en'],
                'language': d['language'],
            }
        
        if 'category' in d and d['category']:
            data['category'] = { 'identifier': d['category']['identifier'] }

        csrf, response = get_csrf_token(conf.session, f'{conf.base_url}/')
        conf.session.headers.update({'X-Csrftoken': csrf})

        response = conf.session.patch(
            f'{conf.base_url}/api/v2/datasets/{id}/', 
            json=data)
        try:
            response.raise_for_status()
        except:
            print(response.text)
        
        print('done')
