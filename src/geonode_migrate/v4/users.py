from ..config import Config
from ..utils import get_csrf_token
from tinydb.database import Document
import click


def push_users(conf: Config):
    table = conf.db.table('users')
    for d in table.all():
        if '__new_id__' in d:
            click.echo(f'already uploaded {d["username"]}')
            continue

        csrf, response = get_csrf_token(conf.session, f'{conf.base_url}/')
        conf.session.headers.update({'X-Csrftoken': csrf})

        response = conf.session.post(f'{conf.base_url}/api/v2/users/', json={
                'username': d['username'],
                'email': d['email'],
                'password': d['password'],
                'first_name': d['first_name'],
                'last_name': d['last_name'],
            })
                 
        try:
            response.raise_for_status()
            content = response.json()
            print(content)
            id = content['user']['pk']

            table.upsert(Document({'__new_id__': id }), doc_id=d['id'])
            click.echo(f'uploaded {d["username"]}')
        except Exception as e:
            click.echo(f'error uploading {d["username"]} - {e}')
