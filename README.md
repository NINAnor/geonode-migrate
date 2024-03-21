# Geonode migrate

## Setup
```
pdm install
cp .env.example .env
```

Add your credentials to `.env`


## Run
### Download
```
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-users
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-documents
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-layers
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-maps
```
### Upload
```
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-users
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-documents
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-layers
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-maps
```
