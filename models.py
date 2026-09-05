class SearchResult:
    def __init__(self, title: str, price: float, currency: str, availability: str, partnumber: str, url: str, distributor: str):
        self.title = title
        self.price = price
        self.currency = currency
        self.availability = availability
        self.partnumber = partnumber
        self.url = url
        self.distributor = distributor