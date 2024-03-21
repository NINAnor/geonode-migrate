from ..config import Config
from tinydb.database import Document
from pathlib import Path
import click
import zipfile
import io


SHP_ALLOWED_EXT = {
    '.shp': 'base_file', 
    '.prj': 'prj_file', 
    '.dbf': 'dbf_file',
    '.shx': 'shx_file',
}

def pull_layers(conf: Config):
    # TODO: handle pagination
    response = conf.session.get(f'{conf.base_url}/api/layers/')
    data = response.json()

    table = conf.db.table('layers')
    dir = conf.output_path / 'layers'
    dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Found layers: {data['meta']['total_count']}")

    for doc in data['objects']:
        if not conf.force and table.contains(doc_id=doc['id']):
            click.echo(f'already downloaded {doc["id"]} - {doc["title"]}')
            continue
        
        try:
            response = conf.session.get(f'{conf.base_url}/api/layers/{doc["id"]}')
            data = response.json()

            layer_dir = dir / str(doc["id"])
            layer_dir.mkdir(exist_ok=True, parents=True)

            data['__files__'] = {}

            if data["storeType"] == "coverageStore":
                extension = 'tiff'
                response = conf.geoserver_session.get(f"{conf.base_url}/geoserver/wcs?format=image%2Ftiff&request=GetCoverage&version=2.0.1&service=WCS&coverageid={data['typename']}")
                data["__files__"]["base_file"] = str(layer_dir / f'{data["name"]}.{extension}')

                with open(data["__files__"]["base_file"], 'wb') as f:
                    f.write(response.content)
            else:
                response = conf.geoserver_session.get(f"{conf.base_url}/geoserver/geonode/ows?service=WFS&version=1.0.0&request=GetFeature&typeName={data['typename']}&outputFormat=SHAPE-ZIP")

                with zipfile.ZipFile(io.BytesIO(response.content)) as zip:
                    files = [n for n in zip.namelist() if any([n.endswith(ext) for ext in SHP_ALLOWED_EXT.keys()])]
                    for f in files:
                        ext = Path(f).suffix
                        zip.extract(f, path=str(layer_dir))
                        data["__files__"][SHP_ALLOWED_EXT[ext]] = str(layer_dir / f)
            
            data["__files__"]['sld_file'] = str(layer_dir / f'{data["name"]}.sld')
            response = conf.geoserver_session.get(f'{conf.base_url}/geoserver/rest/styles/{data["name"]}.sld')
            with open(data["__files__"]['sld_file'], 'wb') as f:
                f.write(response.content)
            
            table.upsert(Document(data, doc_id=data['id']))

            click.echo(f'downloaded {doc["id"]} - {doc["title"]}')
        except Exception as e:
            click.echo(f'error {doc["id"]} - {doc["title"]}: {e}', err=True)
