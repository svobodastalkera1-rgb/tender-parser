import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from models import SearchResult
from parsers.dns import distributor

load_dotenv()

class SearchDNS(SearchResult):
    def __init__(self, article, specs, title_bd, **kwargs):
        super().__init__(**kwargs)
        self.distributor = distributor
        self.article = article
        self.specs = specs
        self.title_bd = title_bd

class dns_distributor(distributor):
    def __init__(self):
        super().__init__('DNS')

    def search(self):
        super().search()    

#open local file, instead of downloading it from the internet, for testing purposes
        with open(os.getenv("LOCAL_PATH"), "r", encoding='utf-8') as file:
            soup = BeautifulSoup(file, "html.parser")

        products = soup.find_all('div', class_='catalog-product')[:3]

        results = []

        for product in products:
            try:
                get_title = product.find('a', class_='catalog-product__name ui-link ui-link_black').get_text(strip=True)
                price = product.find('div', class_='product-buy__price').text.strip().replace('₽', '').replace(' ', '')
                availability = product.find('span', class_='available available-hard').text.strip()
            #this part will be replaced by a module that can open the product card (where partnumber is located) \ except not workin'
                try:
                    partnumber = product.find('div', class_='data-partnumber')
                except AttributeError:
                    partnumber = "None"
                article = product.get('data-code', 'None')
                specs = product.find('span', class_='catalog-product__short-specs').text.strip('[] ')
                url = product.find('a', class_='catalog-product__name ui-link ui-link_black').get('href')

            #temporary measure
                titles = get_title.split('[')
                title = titles[0]
                title_bd = titles[1].replace(']', '') if len(titles) > 1 else ''

            except Exception as e:
                 print(f'Ошибка при обработке элемента {e}')
                 continue
                 

            result = SearchDNS(

                title = title,
                price = price,
                currency = "RUB",
                availability = availability,
                partnumber = partnumber,
                url = url,
                article = article,
                specs = specs,
                title_bd = title_bd

            )

            results.append(result)

        return results    







        def print_items():
            print(
                f'Наименование: {title} |'
                f' Цена: {price} |'
                f' Наличие: {availability}'
                #f' Характеристики: {specs} |'
                #f' Артикул: {article} |'
                #f' URL: https://dns-shop.ru{url}'
            )

            if partnumber is not None: print(f' | Партномер: {partnumber} |')

            return[]

        print_items()