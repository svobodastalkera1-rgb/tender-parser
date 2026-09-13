import os
from dotenv import load_dotenv
from openpyxl import load_workbook
from models import OutputResult
from database import get_item
from read_excel import read_tender_excel


load_dotenv()
file_path = os.getenv("LOCAL_EXCEL")

class Excel_output(OutputResult):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

def package_excel():

    results = read_tender_excel(file_path)

    for result in results:
        name = get_item(None, 'name')

        if not name:
            continue

        items = Excel_output(
            name= name,
            price= price,
            availability= availability
        )

    results.append(items)


    wb.save('actual.xlsx')