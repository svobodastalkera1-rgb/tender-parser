class Distributor:
    #базовый класс для всех дистрибов, функция ниже принимает имя дистрибьютора и возвращает объект класса дистрибьютора
    def __init__(self, name):
        self.name = name

    #поиск товара по наименованию, возвращает список объектов SearchResult
    def search(self, item_name: str):
        raise NotImplementedError("Метод search должен быть переопределен в населеднике")

    