from ..config import Config
from ..utils import get_csrf_token
from tinydb.database import Document
import click
import json


def push_maps(conf: Config):
    table = conf.db.table('maps')
    for d in table.all():
        if '__new_id__' in d and not conf.force:
            print('already uploaded')
            continue

        csrf, response = get_csrf_token(conf.session, f'{conf.base_url}/')
        conf.session.headers.update({'X-Csrftoken': csrf})

        tpl = conf.env.get_template('map_body.json')
        body = json.loads(tpl.render({
            'title': d['title'],
            'base_url': conf.base_url,
            'center_x': d['center_x'],
            'center_y': d['center_y'],
            'crs': d['projection'],
            'zoom': d['zoom'],
        }))

        response = conf.session.post(
            f'{conf.base_url}/api/v2/maps/?include[]=data',
            json=body
        )
        response.raise_for_status()
        content = response.json()

        table.upsert(Document({'__new_id__': content['map']['pk'] }, doc_id=d['id']))
        
        print('done')
