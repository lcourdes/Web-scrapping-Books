"""
Ce Proof Of Concept permet de récupérer et de printer des informations relatives à un ouvrage du site
http://books.toscrape.com

Les informations recueillies relatives à chaque ouvrage sont : 1) l'adresse url, 2) le code produit universel (upc),
3) le titre, 4) le prix toutes taxes comprises, 5) le prix hors taxes, 6) nombre d'unités disponibles, 7) description du
produit, 8) la catégorie, 9) la note utilisateur, 10) l'adresse url de l'image.
"""

from models import Book
from utils import create_soup

url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

soup = create_soup(url)

category_brut = soup.select("#default > div.container-fluid.page > div > ul > li:nth-child(3) > a")
category = category_brut[0].text.strip()

book = Book(soup)
print("product_page_url : " + url + "\n" +
      "universal_product_code (upc) : " + book.get_universal_product_code() + "\n" +
      "title : " + book.get_title() + "\n" +
      "price_including_tax : " + book.get_price_including_tax() + "\n" +
      "price_excluding_tax : " + book.get_price_excluding_tax() + "\n" +
      "number_available : " + book.get_number_available() + "\n" +
      "product_description : " + book.get_description() + "\n" +
      "category : " + category + "\n" +
      "review_rating : " + book.get_review_rating() + "\n" +
      "image_url : " + book.get_image_url() + "\n"
      )
