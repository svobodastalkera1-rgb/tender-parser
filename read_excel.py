import sys                              #модуль для работы с аргументами командной строки
from openpyxl import load_workbook     #функция для чтения Excel файлов
from dotenv import load_dotenv
import os

load_dotenv()
file_path = os.getenv("LOCAL_EXCEL") 

def read_tender_excel(file_path):       #при вызове функции передается путь к файлу Excel
                           
    workbook = load_workbook(file_path, data_only=True)
    sheet = workbook.active             #получение активного листа Excel файла

    items = []
    for row in sheet.iter_rows(min_row=2, values_only=True): #min_row=2 = начало чтения со второй строки, va;ues_omly=True = получение значения, а не объекта ячеек
        if row[0] and row[1]:
            name = str(row[0]).strip()

            #составляем словарь с данными по позиции
            items.append({
                'name': name
            })
    return items

#data = read_tender_excel(file_path)     #вызываем функцию и получаем список позиций