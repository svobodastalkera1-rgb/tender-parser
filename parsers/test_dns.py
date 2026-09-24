from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
from models import SearchResult
from parsers.base import Distributor
from urllib.parse import urlencode

class SearchDNS(SearchResult):
    def __init__(self, article, specs, title_bd, shop, **kwargs):
        super().__init__(**kwargs)
        self.article = article
        self.specs = specs
        self.title_bd = title_bd
        self.shop = shop

class dns_distributor(Distributor):
    def __init__(self, name='DNS', search_url="https://www.dns-shop.ru/search/"):
            super().__init__(name)
            self.name = name
            self.search_url = search_url

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
                query_string = urlencode(params)
                full_url = f"{base_url}?{query_string}"

                #маскировка под пользователя
                page.goto(full_url, wait_until='domcontentloaded', timeout=60000)

                # Ждём именно карточку, которую затем ищет BeautifulSoup. При неудаче выдаем ошибку
                try:
                    page.wait_for_selector('div.catalog-product', timeout=30000)
                except Exception as wait_error:
                    print(f"Карточки товаров не были найдены: {wait_error}")

                # Цена встречается или текстом покупки, или в атрибуте data-price блока доставки, пробуем достать
                try:
                    page.wait_for_function(
                        """() => Array.from(document.querySelectorAll(
                            '.catalog-product__buy, .delivery-info-widget[data-price]'
                        )).some(element =>
                            element.textContent.trim().length > 0 ||
                            (element.getAttribute('data-price') || '').trim().length > 0
                        )""",
                        timeout=15000,
                    )
                except Exception as wait_error:
                    print(f"Блок с ценой не найден: {wait_error}")

                html = page.content()
            except Exception as e:
                print(f"[DNS] Ошбка Camoufox: {e}")
                html = ""
            finally:
                browser.close()
        return html
    
    def search(self, html):
        soup = BeautifulSoup(html, "html.parser")

        products = soup.find_all('div', class_='catalog-product')[:3]

        results = []
        printed_example_card = False

        for product in products:
            title_element = product.find(
                'a', class_='catalog-product__name ui-link ui-link_black'
            )
            price_element = product.find('div', class_='product-buy__price')
            delivery_price_element = product.find(
                'div', class_='delivery-info-widget', attrs={'data-price': True}
            )
            availability_element = product.find(
                'span', class_='available available-hard'
            )
            specs_element = product.find(
                'span', class_='catalog-product__short-specs'
            )

#продолжаем, если товар не найден
            if title_element is None:
                print(
                    "Карточка пропущена: не найдено название; "
                    f"код товара={product.get('data-code', 'не указан')}"
                )
                continue

            get_title = title_element.get_text(strip=True)
            if price_element:
                price = price_element.get_text(strip=True).replace('₽', '').replace(' ', '')
            elif delivery_price_element:
                price = delivery_price_element.get('data-price')
            else:
                price = None

            availability_status = product.get('data-avail-status')
            availability_names = {
                'now': 'В наличии',
                'today': 'Сегодня',
                'tomorrow': 'Завтра',
                'later': 'Позже',
                'out_of_stock': 'Нет в наличии',
            }
            availability = (
                availability_element.get_text(strip=True)
                if availability_element
                else availability_names.get(availability_status, availability_status or 'Не указано')
            )
            specs = (
                specs_element.get_text(strip=True).strip('[] ')
                if specs_element else ''
            )
            if (
                price_element is None and delivery_price_element is None
                or (not availability_status and availability_element is None)
                or specs_element is None
            ):
                missing = [
                    name for name, element in (
                        ('цена', price_element or delivery_price_element),
                        ('наличие', availability_element or availability_status),
                        ('характеристики', specs_element),
                    )
                    if element is None
                ]
                print(
                    f"В карточке '{get_title}' не найдены поля: "
                    f"{', '.join(missing)}"
                )

            if (
                price_element is None and delivery_price_element is None
            ) or (availability_element is None and not availability_status):
                if not printed_example_card:
                    print("HTML первой карточки с пропущенными полями:")
                    formatted_card = product.prettify()
                    print(formatted_card[:5000])
                    if len(formatted_card) > 5000:
                        print("Продолжение HTML карточки:")
                        print(formatted_card[-5000:])
                    printed_example_card = True
                continue

            partnumber_element = product.find('div', class_='data-partnumber')
            partnumber = (
                partnumber_element.get_text(strip=True)
                if partnumber_element else None
            )
            article = product.get('data-code', 'None')
            url = title_element.get('href')

#избавляемся от скобок 
            titles = get_title.split('[', maxsplit=1)
            title = titles[0].strip()
            title_bd = titles[1].replace(']', '').strip() if len(titles) > 1 else ''

            result = SearchDNS(

                title = title,
                price = price,
                currency = "RUB",
                availability = availability,
                partnumber = partnumber,
                url = url,
                distributor = self.name,
                article = article,
                specs = specs,
                title_bd = title_bd,
                shop = self.name

            )

            results.append(result)

        return results    
    
