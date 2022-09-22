import requests
from bs4 import BeautifulSoup
from MyExceptions import InvalidUrlAddress


def create_soup(url):
    """Crée un objet soup à partir d'une adresse url.
    Arg:
        url (str): Adresse Url

    Returns:
        soup = objet soup de l'adresse Url
    """

    response = requests.get(url)
    if response.ok is False:
        raise InvalidUrlAddress
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup
