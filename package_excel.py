import os
from dotenv import load_dotenv
from openpyxl import load_workbook, Workbook
from models import OutputResult
from database import get_item
from read_excel import read_tender_excel


load_dotenv()
file_path = os.getenv("LOCAL_EXCEL")

class Excel_output(OutputResult):
    def __init__(self, price, availability, **kwargs):
        super().__init__(**kwargs)
        self.price = price,
        self.availability = availability

def package_excel():

    wb = Workbook()
    ws = wb.active
    ws.title = "Actual Results"

    ws.append(['Наименование', 'Цена', 'Наличие'])

    results = read_tender_excel(file_path)

    objects = []

    for result in results:
        name = get_item(None, 'name')

        if not name:
            continue

        name= name.get('name'),
        price= name.get('price'),
        availability= name.get('availability')

        items = Excel_output(
            name = name,
            price = price,
            availability = availability
        )

        objects.append(items) 

        ws.append([name, price, availability])


    wb.save('actual.xlsx')

    return objects