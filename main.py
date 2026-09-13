import os
import parsers.dns
from dotenv import load_dotenv
from package_excel import package_excel
from database import save_data, get_item
from read_excel import read_tender_excel

load_dotenv()
file_path = os.getenv("LOCAL_EXCEL")
dns = parsers.dns.dns_distributor()

def main():
    read_tender_excel(file_path)
    get_item(None, 'title')


    if not items:
        dns.search()
        save_data(dns.results)
        get_item(None, 'title')

    package_excel()

    return

main()




