import requests
from bs4 import BeautifulSoup
import csv
from pathlib2 import Path
from MyExceptions import *
from Models import Book, Category
from Utile import create_soup


def find_all_url_category(url):
    """Trouve tous les noms et adresses url des catégories d'ouvrages.

    Arg:
        url (str): Adresse Url du site 'Books to scrape'

    Returns:
        all_url_category (dict) = Les clés sont les noms des catégories d'ouvrages, les valeurs sont les adresses url
            des index des ouvrages respectifs.
    """

    soup = ""
    try:
        soup = create_soup(url)
    except InvalidUrlAddress:
        pass
    nav_list_ul = soup.find("ul", class_="nav nav-list")
    a_in_ul_nav = nav_list_ul.find_all("a")
    all_url_category = {}
    for a in a_in_ul_nav:
        name_of_category = a.text.strip()
        link = "http://books.toscrape.com/catalogue/category/" + a['href'].replace('../', '')
        all_url_category[name_of_category] = link
    del all_url_category['Books']
    return all_url_category


def iterate_in_books(books, category_name):
    """Pour chaque url d'ouvrages, cette fonction :
        - crée une instance de la classe 'Book'
        - ajoute les informations de l'instance de Book dans une liste.

        Arg:
            books = liste obtenue par l'instance d'une catégorie

        Returns:
            list_for_csv = Une liste contenant les en-têtes ainsi que les informations propres à chaque ouvrage
            à écrire dans un fichier csv.
    """

    list_for_csv = [[
        'Product_page_url',
        'universal_product_code',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'product_description',
        'category',
        'review_rating',
        'image_url',
    ]]

    for url in books:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        book = Book(soup)
        list_for_csv.append([
            url,
            book.get_universal_product_code(),
            book.get_title(),
            book.get_price_including_tax(),
            book.get_price_excluding_tax(),
            book.get_number_available(),
            book.get_description(),
            category_name,
            book.get_review_rating(),
            book.get_image_url(),
        ])
        download_image(book, category_name)

    return list_for_csv


def download_image(book, category_name):
    """Télécharge l'image de chaque ouvrage

    Arg:
        book : instance de Book
        category_name (str) : nom de la catégorie de l'ouvrage
    """

    response = requests.get(book.get_image_url())
    if response.ok is False:
        raise InvalidUrlAddress
    soup = response.content

    path = Path('data/' + category_name)
    if not path.exists():
        path.mkdir(parents=True)
    file_name = book.get_title().replace('/', ' ') + ".png"
    with open(path/file_name, 'wb+') as imagefile:
        imagefile.write(soup)


def write_to_csv(list_for_csv, category_name):
    """Ecrit la list_for_csv dans un fichier csv portant le nom de sa catégorie d'ouvrages.

    Arg:
        list_for_csv : liste obtenue à l'aide de la fonction 'iterate_in_books'
        category_name : nom de la catégorie
    """

    path = Path('data/' + category_name)
    file_name = str(category_name) + ".csv"
    with open(path/file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(list_for_csv)


def main():
    home_url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
    all_url_category = find_all_url_category(home_url)
    for category_name, category_url in all_url_category.items():
        category = Category(category_url)
        books = category.books
        list_for_csv = iterate_in_books(books, category_name)
        write_to_csv(list_for_csv, category_name)


main()
