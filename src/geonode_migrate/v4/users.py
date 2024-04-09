from ..config import Config
from ..utils import get_csrf_token
from tinydb.database import Document
import click
from requests import Session


def push_users(conf: Config):
    table = conf.db.table('users')
    session = conf.session

    csrf, response = get_csrf_token(session, f'{conf.base_url}/')
    session.headers.update({'X-Csrftoken': csrf})
    auth = (conf.geonode_user, conf.geonode_password)

    for d in table.all():
        if '__new_id__' in d and not conf.force:
            click.echo(f'already uploaded {d["username"]}')
        else:
            
            data = {
                    'username': d['username'],
                    'password': d['password'],
                    'first_name': d['first_name'],
                    'last_name': d['last_name'],
                }
            
            if d['email']:
                data['email'] = d['email']

                print(data)

            response = session.post(f'{conf.base_url}/api/v2/users', json=data, auth=auth)

            try:
                response.raise_for_status()
                content = response.json()
                print(content)
                id = content['user']['pk']

                table.upsert(Document({'__new_id__': id }, doc_id=d['id']))
                click.echo(f'uploaded {d["username"]}')
            except Exception as e:
                print(response.text)
                click.echo(f'error uploading {d["username"]} - {e}')

        
        print('updating password')
        response = session.post(f'{conf.base_url}/api/v2/extra/admin-set-user-password/', json={'username': d['username'], 'password': d['password']}, auth=auth)
        print(response.text)

