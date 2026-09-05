from openpyxl import load_workbook
import os
from dotenv import load_dotenv

load_dotenv()


with open (os.getenv("LOCAL_EXCEL")) as file:
    wb = load_workbook(file)
    sheet = wb.active

items = []

for item in items:
    items.append(item)


wb.save('actual.xlsx')