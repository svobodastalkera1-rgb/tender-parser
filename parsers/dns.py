import json
import requests
import re
from playwright.sync_api import sync_playwright
from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
from models import SearchResult
from parsers.base import Distributor

class DnsDistributor(Distributor):
    #вызов конструктора родителя + перелача имени дистрибьютора + llm
    def __init__(self, ollama_model="qwen3:8b", search_url="https://www.dns-shop.ru/search/"):
        super().__init__("DNS")
        self.ollama_model = ollama_model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.search_url = search_url

    #формируем url и параметры 
    def search(self, item_name: str):
        #получаем HTML через playwright
        html = self._fetch_html(item_name)
        if not html:
            print("[DNS]Не удалось получить HTML")
            return []

        #отправляем html в LLM для извлечения данных
        extracted = self._extract_data_with_llm(html, item_name)
        print("DEBUG extracted:", extracted)
        print("DEBUG type:", type(extracted))
        if extracted and isinstance(extracted, list) and len(extracted) > 0:
            print("DEBUG first item:", extracted[0])
            print("DEBUG first item type:", type(extracted[0]))

        # if not extracted:
        #    print("[DNS]LLM не вернула данные")
        #    return []

        #превращаем словари в объекты SearchResult
        results = []
        for item in extracted:
            #если не словарь, пропускаем
            if not isinstance(item, dict):
                continue
            for key in ['product', 'item', 'data']:
                if key in item and isinstance(item[key], dict):
                    item = item[key]
                    break

            #извелкаем поля
            title = item.get('title') or item.get('name') or ''
            price_raw = item.get('price', 0)
            availability = item.get('availability', '')
            partnumber = item.get('partnumber', '')
            url = item.get('url', '')

            if not title or price_raw is None:
                continue

            try:
                price_str = str(price_raw).replace(',', '.').replace('₽', '').replace(' ', '')
                price = float(price_str)
            except:
                price = 0.0

            result = SearchResult(
                title=title,
                price=price,
                currency="RUB",
                availability=availability,
                partnumber=partnumber,
                url=url,
                distributor=self.name
            )
            results.append(result)

        return results



    def _fetch_html(self, item_name: str) -> str:
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
    

    def _extract_data_with_llm(self, html: str, query: str) -> list[dict]:
        soup = BeautifulSoup(html, 'html.parser')

        #чистим код от мусора по максимуму
        for trash in soup(
            [
                'picture', 'img', 'svg', 'script', 'style', 'span', 'i',
                'header', 'footer', 'nav', 'aside', 'form', 'input', 'button',
                'link', 'meta', 'noscript', 'iframe', 'video', 'audio', 'canvas',
            ]
        ):
            trash.decompose()

        #чистка тегов от мусора
        for tag in soup.find_all(True): 
            valid_attrs = {}
            for attr in ['id', 'class']:
                if attr in tag.attrs:
                    attr_value = tag[attr]
                    valid_attrs[attr] = (
                        " ".join(attr_value)
                        if isinstance(attr_value, list)
                        else attr_value
                    )
            tag.attrs = valid_attrs

        #структурируем очищенное
        cleaned_html = str(soup)
        cleaned_html = re.sub(r'\n\s*\n', '\n', cleaned_html)  #удаляем пустые строки 
        cleaned_html = cleaned_html[:35000] #лимит контекста

        #промт и JSON-схема
        json_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Название товара"},
                    "price": {
                        "type": "integer",
                        "description": "Цена в рублях (только число)",
                    },
                    "availability": {
                        "type": "string",
                        "description": "Статус наличия",
                    },
                    "partnumber": {
                        "type": "string",
                        "description": "Партномер производителя",
                    },
                    "url": {
                        "type": "string",
                        "description": "Полная ссылка на карточку товара",
                    },
                },
                "required": ["title", "price"],
            },
        }
                        
        system_prompt = (
            "Ты - эксперт по извлечению данных из HTML-кода и возвращению их в виде JSON-массива."
            "Твоя задача: извлеки информцию О ПЕРВЫХ ТРЁХ ТОВАРАХ из предоставленного кода"
            "Верни ТОЛЬКО JSON-МАССИВ плоских объектов (БЕЗ ВЛОЖЕННЫХ ОБЪЕКТОВ И ЛИШНИХ ПОЛЕЙ)"
            f"JSON-массив должен строго соответствовать следующей схеме:\n{{json.dumps(json_schema, indent=4, ensure_ascii=False)}}\n"
            f"и каждый объект ДОЛЖЕН СОДЕРЖАТЬ СТРОГО СЛЕДУЮЩИЕ ПОЛЯ:\ntitle (строка), price (целое число), availability (строка), partnumber (строка), url (строка).\n"
            f"НИКАКИХ ДРУГИХ ПОЛЕЙ (name, rating, specs, reviews_count и т.п.) ДОБАВЛЯТЬ НЕЛЬЗЯ"
            f"ПОВТОРЯЮ, пример корректного ответа:\n'[{{'title': 'Монитор MSI 27', 'price': 14999, 'availability': 'В наличии', 'partnumber': '', 'url': 'https://...'}}]\n'"
            "Если поле отсутствует, используй цифру 0. НЕ ДОБАВЛЯЙ КОММЕНТАРИЕВ, ВЕРНИ ТОЛЬКО МАССИВ"
            f"УДАЛЯЙ ВСЕ ЛИШНИЕ ДАННЫЕ, ОСТАЛВЯЙ ТОЛЬКО \ntitle (строка), price (целое число), availability (строка), partnumber (строка), url (строка).\n!!!!!!!!!!!!!"
        )

        user_message = f"HTML-код (после очистки) для запроса '{query}':\n\n{cleaned_html}"

        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "format": "json", #гарантия возврата JSON
            "options": {
                "temperature": 0.1,
            }
        }

        try:
            url = self.ollama_url.replace("api/generate", "api/chat")
            response = requests.post(url, json=payload, timeout=120)

            if response.status_code != 200:
                print(f"Ошибка Ollama: {response.status_code} {response.text}")
                return []

            result_text = response.json().get('message', {}).get('content', '')
            print("DEBUG LLM raw response:", result_text[:500])

        except Exception as e:
            print(f"Ошибка связи с Ollama: {e}")
            return []

        #парсинг и коррекция ответа
        cleaned = result_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            #логика распаковки если LLM завернула массив в словарь
            if isinstance(data, dict):
                unwrapped = False
                for key in ['products', 'items', 'data', 'results']:
                    if key in data:
                        data = data[key]
                        unwrapped = True
                        break
                if not unwrapped: #одиночный товар оборачиваем в список
                    data = [data]

            #если вернулись не 3 товара
            if isinstance(data, list):
                return data[:3]
            else:
                print(f"LLM вернула не список и не словарь: {type(data)}")
                return []   

        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            print("Ответ Ollama:", cleaned[:500])
            return []





    #def _extract_data_with_llm(self, html: str, query: str) -> list [dict]:
        soup = BeautifulSoup(html, 'html.parser')

        catalog = soup.find_all('div', class_="catalog-product") #поиск контейнера
        if catalog:
            top_three = catalog[:3]

            for prod in top_three:
                for trash in prod.fina_all(['picture', 'img', 'svg', 'script', 'style', 'span', 'i']):
                    trash.decompose()

            catalog_html = "".join(str(prod) for prod in top_three)
        else:
            catalog_html = html[:30000]



        #отправка HTML в LLM и получаем список словарей с товарами
        
        system_promt = (
            
        )

        user_message = f""

        payload = {
            "model": self.ollama_model,
            "prompt": f"{system_promt}\n\n{user_message}",
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
            }
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code != 200:
                print(f"[DNS] Ошибка Ollama: {response.status_code} {response.text}")
                return []
            result_text = response.json().get('response', '')
            print("DEBUG LLM raw response:", result_text[:500])

        except Exception as e:
            print(f"[DNS] Ошибка связи с Ollama: {e}")
            return[]

        #очищение ответа от маркдауна
        cleaned = result_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        #попытка распарсить JSON
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                for key in ['products', 'items', 'data', 'results']:
                    if key in data:
                        data = data[key]
                        break
                    else:
                        data = [data]
            if isinstance(data, list):
                return data
            else:
                print(f"[DNS] Ollama вернула не список и не словарь: {type(data)}")
                return []
            
        except json.JSONDecodeError as e:
            print(f"[DNS] Ошибка парсинга JSON: {e}")
            print("Ответ Ollama:", cleaned[:500])
            return []