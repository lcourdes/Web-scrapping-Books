from domain import *
from myexceptions import *

if __name__ == '__main__':
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
                try:
                    full_process_category(all_category, choosen_category_id)
                except InvalidUrlAddress:
                    raise
            print("Extraction terminée.\n\nSouhaitez-vous choisir une autre catégorie ?")
            print("(Entrez 'O' si vous voulez continuer. Toute autre entrée terminera le programme.)\n")
            want_to_continue = input()
            if want_to_continue.lower() != 'oui':
                break
        print("Extraction terminée.")
    except InvalidUrlAddress:
        print("L'adresse Url n'est pas valide.")
