from ..config import Config
from tinydb.database import Document
from pathlib import Path
import click

def pull_layers(conf: Config):
    # TODO: handle pagination
    response = conf.session.get(f'{conf.base_url}/api/layers/')
    data = response.json()

    table = conf.db.table('layers')
    dir = conf.output_path / 'layers'
    dir.mkdir(parents=True, exist_ok=True)

    click.echo(data['meta']['total_count'])

    for doc in data['objects']:
        response = conf.session.get(f'{conf.base_url}/api/layers/{doc["id"]}')
        data = response.json()

        layer_dir = dir / str(doc["id"])
        layer_dir.mkdir(exist_ok=True, parents=True)

        if data["storeType"] == "coverageStore":
            extension = 'tiff'
            response = conf.geoserver_session.get(f"{conf.base_url}/geoserver/wcs?format=image%2Ftiff&request=GetCoverage&version=2.0.1&service=WCS&coverageid={data['typename']}")
        else:
            extension = 'zip'
            response = conf.geoserver_session.get(f"{conf.base_url}/geoserver/geonode/ows?service=WFS&version=1.0.0&request=GetFeature&typeName={data['typename']}&outputFormat=SHAPE-ZIP")


        data["file_position"] = str(layer_dir / f'{data["name"]}.{extension}')

        with open(data["file_position"], 'wb') as f:
            f.write(response.content)

        
        data["style_position"] = str(layer_dir / f'{data["name"]}.sld')
        response = conf.geoserver_session.get(f'{conf.base_url}/geoserver/rest/styles/{data["name"]}.sld')
        with open(data["style_position"], 'wb') as f:
            f.write(response.content)
        
        table.upsert(Document(data, doc_id=data['id']))

        click.echo(f'downloaded {doc["title"]}')
