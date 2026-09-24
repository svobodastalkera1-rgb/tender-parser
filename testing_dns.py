import os

from dotenv import load_dotenv

from database import get_item, save_data
from parsers.test_dns import dns_distributor
from read_excel import read_tender_excel


def main():
    load_dotenv()
    file_path = os.getenv("LOCAL_EXCEL")

    dns = dns_distributor("DNS")
    item_names = read_tender_excel(file_path)

    for item in item_names:
        if not item:
            continue

        try:
            existing_items = get_item(None, item)
        except Exception as error:
            print(f"Отсутствует в базе: '{item}': {error}")
            continue

        if existing_items:
            print(f"Найдено в базе: {item}")
            continue

        try:
            html = dns._fetch_html(item)
            if not html:
                print(f"Сайт не вернул страницу для: '{item}')")
                continue

            results = dns.search(html)
            if not results:
                print(f"Отсутствует страница с товаром: '{item}'")
                continue

            save_data(results)
            print(f"Сохраненные результаты для '{item}': {len(results)}")
        except Exception as error:
            print(f"Ошибка при обработке товара '{item}': {error}")


main()
