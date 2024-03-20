from bs4 import BeautifulSoup
from requests import Session

def get_csrf_token(session: Session, url: str):
	response = session.get(url)
	return BeautifulSoup(response.text, features="lxml").find('input', {"name": "csrfmiddlewaretoken"}).get("value"), response
