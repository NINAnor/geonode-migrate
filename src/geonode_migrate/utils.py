from bs4 import BeautifulSoup
from requests import Session
import secrets
import string

alphabet = string.ascii_letters + string.digits

def generate_password(length=16):
	return ''.join(secrets.choice(alphabet) for i in range(length)) 


def get_csrf_token(session: Session, url: str):
	response = session.get(url)
	return BeautifulSoup(response.text, features="lxml").find('input', {"name": "csrfmiddlewaretoken"}).get("value"), response
