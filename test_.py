import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

#href = "https://www.dns-shop.ru"

#open local file, instead of downloading it from the internet, for testing purposes
with open(os.getenv("LOCAL_PATH"), "r", encoding='utf-8') as file:
    soup = BeautifulSoup(file, "html.parser")

products = soup.find_all('div', class_='catalog-product')[:3]

for product in products:
    get_title = product.find('a', class_='catalog-product__name ui-link ui-link_black').get_text(strip=True)
    price = product.find('div', class_='product-buy__price').text.strip().replace(' ','')
    availability = product.find('span', class_='available available-hard').text.strip()
#this part will be replaced by a module that can open the product card (where partnumber is located)
    try:
        partnumber = product.find('div', class_='data-partnumber')
    except AttributeError:
        partnumber = "None"
    article = product.get('data-code', 'None')
    specs = product.find('span', class_='catalog-product__short-specs').text.strip('[] ')
    url = product.find('a', class_='catalog-product__name ui-link ui-link_black').get('href')

#temporary measure
    titles = get_title.split('[')
    title = titles[0]
    title_bd = titles[1].replace(']', '') if len(titles) > 1 else ''

    def print_items():
        print(
            f'Наименование: {title} |'
            f' Цена: {price} |'
            f' Наличие: {availability}'
            #f' Характеристики: {specs} |'
            #f' Артикул: {article} |'
            #f' URL: https://dns-shop.ru{url}'
        )

        if partnumber is not None: print(f' | Партномер: {partnumber} |')

        return[]

    print_items()



#def junk():
    #products = [prod.extract() for prod in soup.find_all(attrs={'data-id': 'product'})[:3]]
    #soup.clear()

    #for prod in products:
        #soup.append(prod)

    #points = soup.find_all(
        #class_=['catalog-product__name ui-link ui-link_black', 'available available-hard', 'product-buy__price'])[:3]
    #soup.clear()

    #for point in points:
        #soup.append(point)

    #print(soup.prettify())



#   for junk in soup([
#                    'picture', 'img', 'svg', 'script', 'style', 'span', 'i',
#                   'header', 'footer', 'nav', 'aside', 'form', 'input', 'button',
#                    'link', 'meta', 'noscript', 'iframe', 'video', 'audio', 'canvas',
#                    'object', 'embed', 'param', 'source', 'track', 'map', 'area',
#                    'details', 'summary', 'dialog', 'menu', 'menuitem', 'fieldset',
#                    'legend', 'label', 'select', 'option', 'textarea', 'datalist',
#                    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'col', 'colgroup',
#                    'caption', 'figure', 'figcaption', 'blockquote', 'q', 'cite', 'abbr', 'address',
#                    'bdo', 'bdi', 'mark', 'progress', 'meter', 'time', 'wbr', 'ruby', 'rt', 'rp',
#                    's', 'u', 'small', 'sub', 'sup', 'code', 'pre', 'var', 'samp', 'kbd', 'dfn',
#                    'abbr', 'acronym', 'b', 'strong', 'i', 'em', 'tt', 'big', 'small', 'strike',
#                    'del', 'ins', 'image', 'map', 'area', 'canvas', 'svg', 'math', 'script', 'noscript', 'template',
#                    'slider', 'status', ''        
#   ]):
#   junk.decompose()