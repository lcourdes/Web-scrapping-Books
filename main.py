import requests
from bs4 import BeautifulSoup
import csv


def check_url(url):
    """Vérifie si une page de site web peut être consultée.
    Arg:
        url (str): Adresse URL

    Returns:
        bool
    """

    response = requests.get(url)
    return response.ok


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

    def get_category(self):
        """Trouve la catégorie d'un ouvrage.

        Returns:
            category = une string spécifiant la catégorie d'ouvrage
        """

        category_brut = self.soup.select("#default > div.container-fluid.page > div > ul > li:nth-child(3) > a")
        category = category_brut[0].text.strip()
        return category

    def get_description(self):
        """Trouve la description d'un ouvrage (h2)

        Returns:
            description = une string de la description d'un ouvrage
        """

        description_brut = self.soup.find('h2')
        description = description_brut.findNext("p").get_text()
        return description

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
        """Récupère le code de produit d'un ouvrage

        Returns:
            universal_product_code = une string spécifiant le code de produit d'un ouvrage
        """

        universal_product_code = self.data[0]
        return universal_product_code

    def get_price_including_tax(self):
        """Récupère le prix (taxes incluses) d'un ouvrage

        Returns:
            price_including_tax = une string spécifiant le prix (TTC) d'un ouvrage
        """

        price_including_tax_brut = self.data[3]
        price_including_tax = price_including_tax_brut.replace('Â£', '')
        return price_including_tax

    def get_price_excluding_tax(self):
        """Récupère le prix (taxes non incluses) d'un ouvrage

        Returns:
            price_excluding_tax = une string spécifiant le prix (HT) d'un ouvrage
        """

        price_excluding_tax_brut = self.data[2]
        price_excluding_tax = price_excluding_tax_brut.replace('Â£', '')
        return price_excluding_tax

    def get_number_available(self):
        """Récupère le nombre d'ouvrages encore disponible

        Returns:
            number_available = une string spécifiant le nombre d'ouvrages encore disponibles
        """

        number_available_brut = self.data[5]
        number_available = ''.join([caracter for caracter in number_available_brut if caracter.isdigit()])
        return number_available

    def get_review_rating(self):
        """Récupère la note des utilisateurs d'un ouvrage

        Returns:
            review_rating = une string spécifiant la note utilisateur d'un ouvrage
        """

        review_rating = self.data[6]
        return review_rating


def create_csv_file():
    """Crée un fichier csv dont les noms de colonnes correspondent aux informations des ouvrages.

        Returns:
            csvfile = un fichier csv
        """

    with open('test.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
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
        ])
    return csvfile


def add_book_to_csv(product_page_url, book):
    """Ajoute un ouvrage dans un fichier csv.

        Arg:
            book = instance de la classe Book
    """

    with open('test.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            product_page_url,
            book.get_universal_product_code(),
            book.get_title(),
            book.get_price_including_tax(),
            book.get_price_excluding_tax(),
            book.get_number_available(),
            book.get_description(),
            book.get_category(),
            book.get_review_rating(),
            book.get_image_url(),
        ])


def check_pages(url_category):
    """Trouve tous les url d'une catégorie et les inscrit dans une liste.

        Arg:
            url_category = adresse url de l'index d'une catégorie

        Returns:
            all_url_pages : Une liste de tous les url d'une catégorie.
    """
    all_url_pages = []
    number_of_page = 2
    while check_url(url_category):
        all_url_pages.append(url_category)
        if number_of_page == 2:
            url_category = url_category.replace('index.html', 'page-' + str(number_of_page) + '.html')
        else:
            url_category = url_category.replace('page-' + str(number_of_page - 1), 'page-' + str(number_of_page))
        number_of_page += 1
    return all_url_pages


def find_books_in_category(all_url_pages):
    """Trouve tous les livres d'une catégorie et inscrit leurs noms et leurs urls
    dans un dictionnaire.

        Arg:
            all_url_pages = liste obtenue à l'aide de la fonction 'check_pages'

        Returns:
            books : Un dictionnaire qui a pour clefs les titres des ouvrages de la catégorie
            sélectionnée et pour valeurs les urls des ouvrages correspondants.
    """

    books = {}
    for url in all_url_pages:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        all_h3_in_category_page = soup.find_all('h3')

        for h3 in all_h3_in_category_page:
            a_balise = h3.find("a")
            title = a_balise['title']
            link = "http://books.toscrape.com/catalogue/" + a_balise['href'].replace('../', '')
            books[title] = link

    return books


def iterate_in_books(books):
    """Pour chaque url d'ouvrages (valeur du dictionnaire books), cette fonction :
        - crée un objet soup à l'aide de la fonction 'create_soup'
        - crée une instance de la classe 'Book'
        - ajoute les informations de l'instance de Book dans le fichier csv

        Arg:
            books = dictionnaire obtenu à la l'aide de la fonction 'find books in category'
    """

    for url in books.values():
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        book = Book(soup)
        add_book_to_csv(url, book)


def main():
    url_mystery = 'http://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html'
    create_csv_file()
    all_url_pages = check_pages(url_mystery)
    books = find_books_in_category(all_url_pages)
    iterate_in_books(books)


main()
