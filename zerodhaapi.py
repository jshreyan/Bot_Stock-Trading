import requests
from bs4 import BeautifulSoup as soup
import traceback
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
URL = "https://zerodha.com"

SESSION = None

def SessionStart():
    global SESSION
    SESSION = requests.session()

def SessionClose():
    SESSION.close()

def requestURLdata(URLEXT):
    page_soup = None
    try:
        time.sleep(0.2)
        url = URL + URLEXT
        #print('URL:',url)
        resp = SESSION.get(url,headers=headers)
        page_soup = soup (resp.text, "html.parser")
        resp.close()
    except:
        print(traceback.format_exc())
        
    return page_soup

def getQuotesMargin():
    margin = {}
    try:
        url='/margin-calculator/Equity/'
        page_soup = requestURLdata(url)
        table = page_soup.find("table", {"id": "table"})
        tbody = table.find("tbody")
        tr = tbody.findAll('tr')
        for td in tr:
            eq = td.findAll("td")[1].text.strip().replace(':EQ','')
            mult = td.findAll("td")[3].text.strip().replace('x','')
            margin[eq] = mult     
    except:
        print(traceback.format_exc())         

    return margin


if __name__ == "__main__":
    SessionStart()
    margin = getQuotesMargin()
