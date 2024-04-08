from tinydb import TinyDB, where
import requests
import pathlib
import logging
import environ
import click
from jinja2 import Environment, PackageLoader, select_autoescape

from .utils import get_csrf_token

env = environ.Env()


class Config:
    def __init__(self, *args, db_path = "db.json", output = "data", force=False, **kwargs) -> None:
        self.db_path = db_path
        self.output_path = pathlib.Path(output)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(str(self.output_path / self.db_path))
        self.force = force

        self.__user_sessions = {}

        self.env = Environment(
            loader=PackageLoader("geonode_migrate"),
            autoescape=select_autoescape()
        )

    def login(self, version=3):
        self.base_url = env(f'GEONODE_V{version}_URL')
        self.session = requests.Session()
        self.geonode_user = env(f'GEONODE_V{version}_USER', default=None)
        self.geonode_password = env(f'GEONODE_V{version}_PASSWORD', default=None)

        if self.geonode_password and self.geonode_user:
            self._cookie_login(version=version)

        self._login_geoserver(version)

    def _login_geoserver(self, version=3):
        self.geoserver_session = requests.Session()
        self.geoserver_user = env(f'GEOSERVER_V{version}_USER', default=None)
        self.geoserver_password = env(f'GEOSERVER_V{version}_PASSWORD', default=None)

        if self.geoserver_password and self.geoserver_user:
            self.geoserver_session.auth = (self.geoserver_user, self.geoserver_password)

        click.echo(f'geoserver auth setup')

    def _login_token(self, version=3):
        self.token_session = requests.Session()
        self.clientid = env(f'CLIENTID_V{version}_USER', default=None)
        self.clientsecret = env(f'CLIENTSECRET_V{version}_PASSWORD', default=None)

        if self.clientid and self.clientsecret:
            basic = requests.auth.HTTPBasicAuth(self.clientid, self.clientsecret)
            response = self.token_session.post(f"{self.base_url}/o/token/", "grant_type=client_credentials", auth=basic, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            response.raise_for_status()
            content = response.json()
            self.token_session.headers.update({'Authentication': f'Bearer {content["access_token"]}'})

    def _cookie_login(self, version=3):
        csrf, response = get_csrf_token(session=self.session, url=f'{self.base_url}/account/login/')
        field = 'login' if version == 4 else 'username'
        response = self.session.post(f"{self.base_url}/account/login/", f"{field}={self.geonode_user}&password={self.geonode_password}&csrfmiddlewaretoken={csrf}", headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.session.headers.update({'X-Csrftoken': csrf})

        if version == 4:
            response = self.session.get(self.base_url + '/api/o/v4/userinfo')
            response.raise_for_status()
            self.access_token = response.json()['access_token']
            self.session.headers.update({'Authentication': f'Bearer {self.access_token}'})

        click.echo(f'successfully logged in geonode - {self.session.cookies}')

    def get_user_session(self, username, version=3):
        table = self.db.table('users')

        if username in self.__user_sessions:
            return self.__user_sessions['username']


        found = table.search(where('username') == username)
        if len(found) != 1:
            raise Exception(f'expected just one user with this username ({username}), found instead: {found}')
        
        u = found[0]

        user_session = requests.Session()

        csrf, response = get_csrf_token(session=user_session, url=f'{self.base_url}/account/login/')
        field = 'login' if version == 4 else 'username'
        response = user_session.post(f"{self.base_url}/account/login/", f"{field}={username}&password={u['password']}&csrfmiddlewaretoken={csrf}", headers={'Content-Type': 'application/x-www-form-urlencoded'})
        user_session.headers.update({'X-Csrftoken': csrf})

        if version == 4:
            response = user_session.get(self.base_url + '/api/o/v4/userinfo')
            response.raise_for_status()
            access_token = response.json()['access_token']
            user_session.headers.update({'Authentication': f'Bearer {access_token}'})

        click.echo(f'successfully logged in geonode - {user_session.cookies}')
