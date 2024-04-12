# Geonode migrate

## Setup
```
pdm install
cp .env.example .env
```

Add your credentials to `.env`


## Geonode 4 setup
In the geonode 4 project you need to add the following folder and code: 
- `upmigrate` folder, needs to be added in the project directory at the same level as `static`, `templates`, `settings.py`, etc..
- in `urls.py` add the following code:

```py
urlpatterns = [
    path('', include('{{ GEONODE_PROJECT_NAME }}.upmigrate.urls')),
] + urlpatterns
```

This adds new REST API endpoints that helps the migration process, without this `ownership` cannot be set

## Run
### Download
```
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-users
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-groups
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-documents
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-layers
pdm run gn-migrate v3 -u http://my.geonode-v3.com download-maps
```
### Upload
```
# First the users
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-users
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-documents
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-layers
pdm run gn-migrate v4 -u http://my.geonode-v4.com sync-layers
pdm run gn-migrate v4 -u http://my.geonode-v4.com upload-maps
```

# NOTEs
**IMPORTANT**: be sure to read this section.

The migration process cannot be run as a single command as it requires to check intermediate results before going on.

First set up the environment variables in the `.env` file

Run one by one the commands to download (there is also a donwnload command that runs them in order)

Data will be saved locally in a json file, files will be saved in different directories.

## Download (Geonode V3)
Download is fault tolerant, it will try to continue from the last successful point, avoiding to save again the same object if is already present in the json.
This is checked by `id`. You can force the overwrite with `--force`

Exported resources:
- users
- groups
- keywords
- documents
- layers
- maps


### Users
Downloaded users will be saved in json, a new password will be generated for them
What is exported:
- data exposed in the REST APIs
- a new password

NOT exported:
- profile image

### Documents
Documents are fully exported, the original file is retrieved and saved.

### Maps
Maps are retrieved as exposed by the REST API and saved in the json

### Layers
Layers are exported from Geoserver, rasters as `tif` images, vectors as `shapefiles` (**THIS ARE NOT ORIGINAL DATA - REQUIRES MANUAL CHECK**).
Also the style `sld` is exported.
Metadata of the layers are exported as json provided by the REST API.


## Upload (Geonode V4)
Upload is lazy, it will ignore already uploaded resources and continue from the where it stopped.
This is done checking the presence of a field named `__new_id__` that contains the ID in the new geonode instance.

Uploadable resources:
- users
- documents
- layers
- maps*


### Users
Users can be syncronized, make sure to start from them to avoid errors on assigning ownership.
The new password will be set up for them.
Users in Geonode 3 could have only a username without an email, make sure to set the following variables in geonode project:
```
ACCOUNT_OPEN_SIGNUP: "True"
ACCOUNT_EMAIL_REQUIRED: "False"
```

### Documents
Documents are uploaded back without issues (note that files that have `.` in the name beside the extension can cause issues in the upload process).

### Maps
Maps are not really syncronized back, Geonode v4 keeps in the database a "blob" json with the mapstore configuration for the map, then django is completely unaware of how to manage it.
There is as of today no logic to migrate a map created in the v3 to v4 (see [this discussion](https://github.com/NINAnor/geonode-migrate/issues/4)).

Then maps are created as empty, populating ownership, some metadata and centering the map where it was originally.

### Layers
Layers can be uploaded back with some caveats:
- upload process sometimes fails and there is no way to make it work, so when it happens the layer will be marked as FAILED and will be skipped, you should manually check it and try to solve the error
- all the uploaded resources will be saved on the disk in a folder that geoserver will use to serve them, the folder itself will have a random name, multiple folder could have the same content, but only those that have a successful upload will be used by geoserver. **It's very risky to clean up** as you could delete used files. For this reason when the upload fails in the json it will be saved a new field called `__delete_path__`.
- Vector datasets when uploaded provide in the REST API the ID to the resource (`__new_id__`), this does not happen with rasters. For this reason you should **always** run `sync-layers` after `upload-layers`. Sync layers will search the dataset by name and will try to associate them (so it will generate a new `__new_id__` for the datasets that have an `identifier` equal to the name). If you don't do this, it will end up with the disk full of copies (geoserver itself would probably avoid processing them as the identifier already exists)
- `sync-layers` will also syncronize the metadata of the layer and the `ownership`
- some things needs to be done manually
- upload is performed with `overwrite_existing_layer` to avoid duplicates, while the UI by default creates multiple copies if you upload the same file


## Management commands
Management commands allow to interact easily with the json "database"

check the available options with `--help`

- clean-user (delete users and groups)
- get-password (obtain the password of a user)
- list-{layers,users,maps,documentes} (provides the resource stored locally and if they have been uploaded)
- clean-table (removes the `__new_id__` property from a table)
- show-table-id (shows the new id of a resource)
- set-table-id (set the new id of a resource)

