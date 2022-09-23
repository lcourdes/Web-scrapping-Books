import requests
import csv
from pathlib2 import Path
import re
from myexceptions import *
from models import Book, Category
from utils import create_soup


def find_all_category(url):
    """Trouve tous les noms et adresses url des catégories d'ouvrages.

    Arg:
        url (str): Adresse Url du site 'Books to scrape'

    Returns:
        all_category (list) = Cette liste est composée de sous-listes. Ces sous-listes sont toutes identiques
            à savoir : ["nom de la catégorie", "Url de la catégorie"]
    """

    try:
        soup = create_soup(url)
    except InvalidUrlAddress:
        raise
    nav_list_ul = soup.find("ul", class_="nav nav-list")
    a_in_ul_nav = nav_list_ul.find_all("a")
    all_category = []
    for a in a_in_ul_nav:
        name_of_category = a.text.strip()
        link = "http://books.toscrape.com/catalogue/category/" + a['href'].replace('../', '')
        all_category.append([name_of_category, link])
    all_category[0][0] = "All Books"
    return all_category


def choose_category(all_category):
    """Permet à l'utilisateur de choisir la catégorie pour laquelle il souhaite extraire les données.

    Arg:
        all_category : Liste obtenue à l'aide de la fonction 'find_all_category'.

    Returns:
        int(choosen_category) : id de la catégorie choisie.

    """

    for category_id, category_informations in enumerate(all_category):
        print(str(category_id) + ": " + category_informations[0])
    print("\n\n Entrez le numéro de la catégorie choisie.")
    print("(Entrez 0 pour récupérer les données de toutes les catégories.)")

    while True:
        choosen_category = input()
        if not choosen_category.isdigit():
            print("Entrez un chiffre.")
        elif int(choosen_category) > 50:
            print("Entrez un chiffre entre 0 et 50.")
        else:
            break
    print("\n-> Vous avez choisi la catégorie : " +
          choosen_category +
          "-" +
          all_category[int(choosen_category)][0] +
          ".\n"
          )
    return int(choosen_category)


def iterate_in_books(books, category_name, category_id):
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
        try:
            soup = create_soup(url)
        except InvalidUrlAddress:
            raise
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
        download_image(book, category_name, category_id, url)

    return list_for_csv


def download_image(book, category_name, category_id, url_product):
    """Télécharge l'image de chaque ouvrage

    Arg:
        book : instance de Book
        category_name (str) : nom de la catégorie de l'ouvrage
    """

    response = requests.get(book.get_image_url())
    if response.ok is False:
        raise InvalidUrlAddress
    soup = response.content

    path = Path('data/' + str(category_id) + "_" + category_name)
    if not path.exists():
        path.mkdir(parents=True)
    file_name = book.get_title().replace('/', '_') + ".png"
    file_name = file_name.replace(' ', '_')
    file_name = file_name.lower()
    find_id_book = re.search("_(\d*)/index", url_product)
    id_book = find_id_book.group(1)
    file_name = str(id_book) + "_" + file_name

    with open(path / file_name, 'wb+') as imagefile:
        imagefile.write(soup)


def write_to_csv(list_for_csv, category_name, category_id):
    """Ecrit la list_for_csv dans un fichier csv portant le nom de sa catégorie d'ouvrages.

    Arg:
        list_for_csv : liste obtenue à l'aide de la fonction 'iterate_in_books'
        category_name : nom de la catégorie
    """

    path = Path('data/' + str(category_id) + "_" + category_name)
    file_name = str(category_id) + "_" + str(category_name) + ".csv"
    with open(path / file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(list_for_csv)


def full_process_category(all_category, choosen_category_id):
    """Cette fonction permet de :
        - instancier la catégorie choisie
        - faire une liste d'ouvrages pour cette catégorie
        - Récupérer les informations de chacun de ces ouvrages
        - Ecrire ces informations dans un fichier csv

    Arg:
        all_category: Liste obtenue à l'aide de la fonction 'find_all_category'.
        choosen_category_id: indice de la catégorie choisie grâce à la fonction 'choose_category'
    """

    print("Extraction en cours de la catégorie : " +
          all_category[choosen_category_id][0] +
          ".  Veuillez attendre..."
          )
    category = Category(all_category[choosen_category_id][1])
    books = category.books
    try:
        list_for_csv = iterate_in_books(books, all_category[choosen_category_id][0], choosen_category_id)
        write_to_csv(list_for_csv, all_category[choosen_category_id][0], choosen_category_id)
    except InvalidUrlAddress:
        raise


def main():
    home_url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
    try:
        all_category = find_all_category(home_url)
        while True:
            choosen_category_id = choose_category(all_category)
            if choosen_category_id == 0:
                for choosen_category_id in range(1, 51):
                    try:
                        full_process_category(all_category, choosen_category_id)
                    except InvalidUrlAddress:
                        raise
                break
            else:
                full_process_category(all_category, choosen_category_id)
            print("Extraction terminée.\n\nSouhaitez-vous choisir une autre catégorie ?")
            print("(Entrez 'Oui' si vous voulez continuer. Toute autre entrée terminera le programme.)\n")
            want_to_continue = input()
            if want_to_continue.lower() != 'oui':
                break
        print("Extraction terminée.")
    except InvalidUrlAddress:
        print("L'adresse Url n'est pas valide.")


main()
