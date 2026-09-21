import json
import requests
import re
from playwright.sync_api import sync_playwright
from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
from models import SearchResult
from parsers.base import Distributor
from read_excel import read_tender_excel
from dotenv import load_dotenv
import os

load_dotenv()
file_path = os.getenv("LOCAL_EXCEL") 

class SearchDNS(SearchResult):
    def __init__(self, article, specs, title_bd, **kwargs):
        super().__init__(**kwargs)
        self.distributor = Distributor
        self.article = article
        self.specs = specs
        self.title_bd = title_bd

class dns_distributor(Distributor):
    def __init__(self, name='DNS'):
            super().__init__('DNS')

    item_name = read_tender_excel(file_path)


    def _fetch_html(self, item_name):
        #запускаем браузер для поиска товара и возврата HTML результатов
        with Camoufox(headless=True) as browser: #False/True - с/без окна
            page = browser.new_page()
            try:
                #формирование URL-поиска по всему сайту
                base_url = self.search_url
                params = {
                    'q': item_name,
                    'stock': 'now-today-tomorrow-later-out_of_stock',
                    'order': 'popular'
                }
                query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
                full_url = f"{base_url}?{query_string}"

                #маскировка под пользователя
                page.goto(full_url, wait_until='domcontentloaded', timeout=60000)

                #ожидание появления главного контейнера с товарами вместо фиксированного таймаута
                page.wait_for_selector('.product-list, .catalog-products', timeout=30000) #для загрузки динамических элементов

                html = page.content()
            except Exception as e:
                print(f"[DNS] Ошбка Camoufox: {e}")
                html = ""
            finally:
                browser.close()
        return html
    
    def search(self, html=None):
        super().search()
        self.results = results

        soup = BeautifulSoup(html, "html.parser")

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
                title_bd = title_bd,
                shop = "DNS"

            )

            results.append(result)

        return results    
    