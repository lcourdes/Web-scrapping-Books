from MyExceptions import InvalidUrlAddress
from Utiles import create_soup


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


class Category:
    """Une catégorie"""

    def __init__(self, url_category):
        self.url_category = url_category
        self.all_soup_pages = []
        self.books = []
        self.check_pages()
        self.find_books_in_category()

    def check_pages(self):
        """Trouve tous les url d'une catégorie, en fait des objets soup et inscrit ces derniers dans une liste."""

        number_of_page = 2
        while True:
            try:
                soup = create_soup(self.url_category)
            except InvalidUrlAddress:
                break
            self.all_soup_pages.append(soup)
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

        for soup in self.all_soup_pages:
            all_h3_in_category_page = soup.find_all('h3')

            for h3 in all_h3_in_category_page:
                a_balise = h3.find("a")
                link = "http://books.toscrape.com/catalogue/" + a_balise['href'].replace('../', '')
                self.books.append(link)
