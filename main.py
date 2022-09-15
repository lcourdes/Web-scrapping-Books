import requests
from bs4 import BeautifulSoup
import csv


def create_soup(url):
    """Vérifie si une page de site web peut être consultée. Si tel est
    le cas, la page web est parsée.
    Arg:
        url (str): Adresse URL

    Returns:
        soup: un objet BeautifulSoup
    """

    response = requests.get(url)
    soup = ""
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
    return soup


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

        Returns:
            data = une liste des informations contenues dans le tableau de données de l'ouvrage
        """

        table_data = self.soup.findAll('td')
        for cell in table_data:
            self.data.append(cell.text)

    def get_universal_product_code(self):
        """Récupère le code de produit d'un ouvrage
        Arg:
            data = une liste obtenue à l'aide de la méthode 'get_table_data()'

        Returns:
            universal_product_code = une string spécifiant le code de produit d'un ouvrage
        """

        universal_product_code = self.data[0]
        return universal_product_code

    def get_price_including_tax(self):
        """Récupère le prix (taxes incluses) d'un ouvrage
        Arg:
            data = une liste obtenue à l'aide de la méthode 'get_table_data()'

        Returns:
            price_including_tax = une string spécifiant le prix (TTC) d'un ouvrage
        """

        price_including_tax_brut = self.data[3]
        price_including_tax = price_including_tax_brut.replace('Â£', '')
        return price_including_tax

    def get_price_excluding_tax(self):
        """Récupère le prix (taxes non incluses) d'un ouvrage
        Arg:
            data = une liste obtenue à l'aide de la méthode 'get_table_data()'

        Returns:
            price_excluding_tax = une string spécifiant le prix (HT) d'un ouvrage
        """

        price_excluding_tax_brut = self.data[2]
        price_excluding_tax = price_excluding_tax_brut.replace('Â£', '')
        return price_excluding_tax

    def get_number_available(self):
        """Récupère le nombre d'ouvrages encore disponible
        Arg:
            data = une liste obtenue à l'aide de la méthode 'get_table_data()'

        Returns:
            number_available = une string spécifiant le nombre d'ouvrages encore disponibles
        """

        number_available_brut = self.data[5]
        number_available = ''.join([caracter for caracter in number_available_brut if caracter.isdigit()])
        return number_available

    def get_review_rating(self):
        """Récupère la note des utilisateurs d'un ouvrage
        Arg:
            data = une liste obtenue à l'aide de la méthode 'get_table_data()'

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


def find_books_in_category(url_mystery):
    """Trouve tous les livres d'une catégorie et inscrit leurs noms et leurs urls
    dans un dictionnaire.

        Arg:
            url_mystery = adresse url d'une catégorie

        Returns:
            books : Un dictionnaire qui a pour clefs les titres des ouvrages de la catégorie
            sélectionnée et pour valeurs les urls des ouvrages correspondants.
    """

    soup = create_soup(url_mystery)
    books = {}
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

    for value in books.values():
        soup = create_soup(value)
        book = Book(soup)
        add_book_to_csv(value, book)


def main():
    url = 'http://books.toscrape.com/catalogue/feathers-displays-of-brilliant-plumage_695/index.html'
    soup = create_soup(url)
    book = Book(soup)
    create_csv_file()
    add_book_to_csv(url, book)


main()
