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


def get_title(soup):
    """Trouve le titre (h1) d'un objet BeautifulSoup parsé.
    Arg:
        soup = un objet BeautifulSoup obtenu à l'aide de la fonction
        "is_url_responsive()"

    Returns:
        title = une string spécifiant le titre (h1)
    """

    title = str(soup.find('h1').text)
    return title


def get_category(soup):
    """Trouve la catégorie d'ouvrage d'un objet BeautifulSoup parsé.
    Arg:
        soup = un objet BeautifulSoup obtenu à l'aide de la fonction
        "is_url_responsive()"

    Returns:
        category = une string spécifiant la catégorie d'ouvrage
    """

    category_brut = soup.select("#default > div.container-fluid.page > div > ul > li:nth-child(3) > a")
    category = category_brut[0].text.strip()
    return category


def get_description(soup):
    """Trouve la description d'un ouvrage (h2) d'un objet BeautifulSoup parsé.
    Arg:
        soup = un objet BeautifulSoup obtenu à l'aide de la fonction
        "is_url_responsive()"

    Returns:
        description = une string de la description d'un ouvrage
    """

    description_brut = soup.find('h2')
    description = description_brut.findNext("p").get_text()
    return description


def get_image_url(soup):
    """Trouve l'url de l'image d'un ouvrage d'un objet BeautifulSoup parsé.
    Arg:
        soup = un objet BeautifulSoup obtenu à l'aide de la fonction
        "is_url_responsive()"

    Returns:
        image_url = une string spécifiant l'url de l'image d'un ouvrage
    """

    image_url_brut = soup.find('img')['src']
    image_url = "http://books.toscrape.com/" + image_url_brut.replace('../', '', 2)
    return image_url


def get_table_data(soup):
    """Récupère le tableau de données d'un ouvrage à partir d'un objet BeautifulSoup parsé.
    Puis, stocke les informations récoltées dans une liste intitulée 'data'
    Arg:
        soup = un objet BeautifulSoup obtenu à l'aide de la fonction
        "is_url_responsive()"

    Returns:
        data = une liste des informations contenues dans le tableau de données de l'objet
            BeautifulSoup
    """

    table_data = soup.findAll('td')
    data = []
    for cell in table_data:
        data.append(cell.text)
    return data


def get_universal_product_code(data):
    """Récupère le code de produit d'un ouvrage
    Arg:
        data = une liste obtenue à l'aide de la fonction 'get_table_data()'

    Returns:
        universal_product_code = une string spécifiant le code de produit d'un ouvrage
    """

    universal_product_code = data[0]
    return universal_product_code


def get_price_including_tax(data):
    """Récupère le prix (taxes incluses) d'un ouvrage
    Arg:
        data = une liste obtenue à l'aide de la fonction 'get_table_data()'

    Returns:
        price_including_tax = une string spécifiant le prix (TTC) d'un ouvrage
    """

    price_including_tax_brut = data[3]
    price_including_tax = price_including_tax_brut.replace('Â£', '', )
    return price_including_tax


def get_price_excluding_tax(data):
    """Récupère le prix (taxes non incluses) d'un ouvrage
    Arg:
        data = une liste obtenue à l'aide de la fonction 'get_table_data()'

    Returns:
        price_excluding_tax = une string spécifiant le prix (HT) d'un ouvrage
    """

    price_excluding_tax_brut = data[2]
    price_excluding_tax = price_excluding_tax_brut.replace('Â£', '', )
    return price_excluding_tax


def get_number_available(data):
    """Récupère le nombre d'ouvrages encore disponible
    Arg:
        data = une liste obtenue à l'aide de la fonction 'get_table_data()'

    Returns:
        number_available = une string spécifiant le nombre d'ouvrages encore disponibles
    """

    number_available_brut = data[5]
    number_available = ''.join([caracter for caracter in number_available_brut if caracter.isdigit()])
    return number_available


def get_review_rating(data):
    """Récupère la note des utilisateurs d'un ouvrage
    Arg:
        data = une liste obtenue à l'aide de la fonction 'get_table_data()'

    Returns:
        review_rating = une string spécifiant la note utilisateur d'un ouvrage
    """

    review_rating = data[6]
    return review_rating


def create_csv_file():
    """Crée un fichier csv dont les noms de colonnes correspondent aux informations des ouvrages.

        Returns:
            csvfile = un fichier csv
        """

    with open('test.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Product_page_url',
                         'universal_product_code',
                         'title',
                         'price_including_tax',
                         'price_excluding_tax',
                         'number_available',
                         'product_description',
                         'category',
                         'review_rating',
                         'image_url'])
    return csvfile


def main():
    url = 'http://books.toscrape.com/catalogue/feathers-displays-of-brilliant-plumage_695/index.html'
    soup = create_soup(url)
    title = get_title(soup)
    category = get_category(soup)
    description = get_description(soup)
    image_url = get_image_url(soup)
    data = get_table_data(soup)
    universal_product_code = get_universal_product_code(data)
    price_including_tax = get_price_including_tax(data)
    price_excluding_tax = get_price_excluding_tax(data)
    number_available = get_number_available(data)
    review_rating = get_review_rating(data)

    csvfile = create_csv_file()


    print("product_page_url : " + url + "\n" +
          "universal_product_code (upc) : " + universal_product_code + "\n" +
          "title : " + title + "\n" +
          "price_including_tax : " + price_including_tax + "\n" +
          "price_excluding_tax : " + price_excluding_tax + "\n" +
          "number_available : " + number_available + "\n" +
          "product_description : " + description + "\n" +
          "category : " + category + "\n" +
          "review_rating : " + review_rating + "\n" +
          "image_url : " + image_url + "\n"
          )


main()
