from openpyxl import load_workbook     #функция для чтения Excel файлов

def read_tender_excel(file_path):       #при вызове функции передается путь к файлу Excel
                           
    workbook = load_workbook(file_path, data_only=True)
    sheet = workbook.active             #получение активного листа Excel файла

    items = []
    for row in sheet.iter_rows(min_row=2, values_only=True): #min_row=2 = начало чтения со второй строки, va;ues_omly=True = получение значения, а не объекта ячеек
        if row[0] is None and row[1]:
            name = str(row[1]).strip()
            items.append({
                name
            })            

        if row[0] and row[1] is None:
            name = str(row[0]).strip()
            items.append({
                name
            })

        if row[0] and row[1]:
            name = str(row[0]).strip() + ' ' + str(row[1]).strip()

            items.append({
                name
            })
    return items