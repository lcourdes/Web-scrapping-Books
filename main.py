import requests
from bs4 import BeautifulSoup
import csv
from pathlib2 import Path


def check_url(url):
    """Vérifie si une page de site web peut être consultée.
    Arg:
        url (str): Adresse Url

    Returns:
        bool
    """

    response = requests.get(url)
    return response.ok


def find_all_url_category(url):
    """Trouve tous les noms et adresses url des catégories d'ouvrages.

    Arg:
        url (str): Adresse Url du site 'Books to scrape'

    Returns:
        all_url_category (dict) = Les clés sont les noms des catégories d'ouvrages, les valeurs sont les adresses url
            des index des ouvrages respectifs.
    """

    if check_url(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        nav_list_ul = soup.find("ul", class_="nav nav-list")
        a_in_ul_nav = nav_list_ul.find_all("a")

        all_url_category = {}
        for a in a_in_ul_nav:
            name_of_category = a.text.strip()
            link = "http://books.toscrape.com/catalogue/category/" + a['href'].replace('../', '')
            all_url_category[name_of_category] = link
        del all_url_category['Books']
        return all_url_category


class Category:
    """Une catégorie"""

    def __init__(self, url_category):
        self.url_category = url_category
        self.all_url_pages = []
        self.books = []
        self.check_pages()
        self.find_books_in_category()

    def check_pages(self):
        """Trouve tous les url d'une catégorie et les inscrit dans une liste."""

        number_of_page = 2
        while check_url(self.url_category):
            self.all_url_pages.append(self.url_category)
            if number_of_page == 2:
                self.url_category = self.url_category.replace('index.html', 'page-' + str(number_of_page) + '.html')
            else:
                self.url_category = self.url_category.replace(
                                                    'page-' + str(number_of_page - 1),
                                                    'page-' + str(number_of_page))
            number_of_page += 1

    def find_books_in_category(self):
        """Trouve tous les livres d'une catégorie et inscrit leurs urls
            dans une liste.

        Returns:
                books : Une liste des urls de tous les ouvrages de la catégorie.
        """

        for url in self.all_url_pages:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            all_h3_in_category_page = soup.find_all('h3')

            for h3 in all_h3_in_category_page:
                a_balise = h3.find("a")
                link = "http://books.toscrape.com/catalogue/" + a_balise['href'].replace('../', '')
                self.books.append(link)


class Book:
    """Un ouvrage"""

    def __init__(self, soup):
        self.soup = soup
        self.data = []
        self.get_table_data()

    def get_title(self):
        """Trouve le titre (h1) de l'ouvrage.

        Returns:
            title = une string spécifiant le titre de l'ouvrage
        """

        title = str(self.soup.find('h1').text)
        return title

    def get_description(self):
        """Trouve la description d'un ouvrage (h2).

        Returns:
            description = une string de la description d'un ouvrage
        """

        description_brut = self.soup.find('h2')
        if str(description_brut.text) == "Product Description":
            description = description_brut.findNext("p").get_text()
            return description
        else:
            return None

    def get_image_url(self):
        """Trouve l'url de l'image d'un ouvrage

        Returns:
            image_url = une string spécifiant l'url de l'image d'un ouvrage
        """

        image_url_brut = self.soup.find('img')['src']
        image_url = "http://books.toscrape.com/" + image_url_brut.replace('../', '', 2)
        return image_url

    def get_table_data(self):
        """Récupère le tableau de données d'un ouvrage, puis, stocke les informations
            récoltées dans une liste intitulée 'data'.
        """

        table_data = self.soup.findAll('td')
        for cell in table_data:
            self.data.append(cell.text)

    def get_universal_product_code(self):
        """Récupère le code de produit d'un ouvrage.

        Returns:
            universal_product_code = une string spécifiant le code de produit d'un ouvrage
        """

        universal_product_code = self.data[0]
        return universal_product_code

    def get_price_including_tax(self):
        """Récupère le prix (taxes incluses) d'un ouvrage.

        Returns:
            price_including_tax = une string spécifiant le prix (TTC) d'un ouvrage
        """

        price_including_tax_brut = self.data[3]
        price_including_tax = price_including_tax_brut.replace('Â£', '')
        return price_including_tax

    def get_price_excluding_tax(self):
        """Récupère le prix (taxes non incluses) d'un ouvrage.

        Returns:
            price_excluding_tax = une string spécifiant le prix (HT) d'un ouvrage
        """

        price_excluding_tax_brut = self.data[2]
        price_excluding_tax = price_excluding_tax_brut.replace('Â£', '')
        return price_excluding_tax

    def get_number_available(self):
        """Récupère le nombre d'ouvrages encore disponible.

        Returns:
            number_available = une string spécifiant le nombre d'ouvrages encore disponibles
        """

        number_available_brut = self.data[5]
        number_available = ''.join([caracter for caracter in number_available_brut if caracter.isdigit()])
        return number_available

    def get_review_rating(self):
        """Récupère la note des utilisateurs d'un ouvrage.

        Returns:
            review_rating = une string spécifiant la note utilisateur d'un ouvrage
        """

        review_rating = self.data[6]
        return review_rating


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

    if check_url(book.get_image_url()):
        response = requests.get(book.get_image_url()).content
        path = Path('data/' + category_name)

        if not path.exists():
            path.mkdir(parents=True)

        file_name = book.get_title().replace('/', ' ') + ".png"
        print(file_name)
        with open(path/file_name, 'wb+') as imagefile:
            imagefile.write(response)


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
