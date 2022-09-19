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


class Category:
    """Une catégorie"""

    def __init__(self, url_category):
        self.url_category = url_category
        self.all_url_pages = []
        self.books = []
        self.check_pages()
        self.find_books_in_category()

    def check_pages(self):
        """Trouve tous les url d'une catégorie et les inscrit dans une liste.

            Returns:
                all_url_pages : Une liste de tous les url d'une catégorie.
        """

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
        return self.all_url_pages

    def find_books_in_category(self):
        """Trouve tous les livres d'une catégorie et inscrit leurs noms et leurs urls
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


def iterate_in_books(books):
    """Pour chaque url d'ouvrages, cette fonction :
        - crée une instance de la classe 'Book'
        - ajoute les informations de l'instance de Book dans une liste

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
            book.get_category(),
            book.get_review_rating(),
            book.get_image_url(),
        ])

    return list_for_csv


def write_to_csv(list_for_csv):
    """Ajoute un ouvrage dans un fichier csv.

        Arg:
            list_for_csv : liste obtenue à l'aide de la fonction 'iterate_in_books'
    """

    with open('test.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(list_for_csv)


def main():
    url_mystery = 'http://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html'
    category = Category(url_mystery)
    books = category.books
    list_for_csv = iterate_in_books(books)
    write_to_csv(list_for_csv)


main()
