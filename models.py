
#один найденный товар у дистрибьютора
class SearchResult:
    def __init__(self, title: str, price: float, currency: str, availability: str, partnumber: str, url: str, distributor: str):
        self.title = title
        self.price = price
        self.currency = currency
        self.availability = availability
        self.partnumber = partnumber
        self.url = url
        self.distributor = distributor

#вывод ключевой информации о товаре в консоль
    def __repr__(self):
        return f"self.distributor: {self.title} | {self.price} {self.currency} | {self.availability}"