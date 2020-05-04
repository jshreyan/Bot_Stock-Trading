import requests
from bs4 import BeautifulSoup as soup
import datetime
import time
import json
import traceback

session = requests.session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
CHANGEPERCENT = 0.3

start = time.time() 
def getLiveQuotes():
    stocklive = {}
    try:
        url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json"
        resp = session.get(url,headers=headers)
        json_data = resp.json()
        resp.close()        
        stockdata = json_data['data']
        stocklive = FormatStockData(stockdata)
        return stocklive
    except:
        print(traceback.format_exc())         
        return stocklive

def UpdateLiveQuotes(updatestocks):
    stocklive = {}
    try:
        url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json"
        resp = session.get(url,headers=headers)
        json_data = resp.json()
        resp.close()        
        stockdata = json_data['data']
        stocklive = FormatStockData(stockdata)
        for stock in updatestocks:
            updatestocks[stock] = stocklive[stock]
        return updatestocks
    except:
        print(traceback.format_exc())         
        return updatestocks

def FormatStockData(stockdata):
    stocklive = {}
    for stock in stockdata:
        stocklive[stock['symbol']] = {'LTP':stock['ltP'].replace(',',''),'PCT':stock['per'].replace(',',''),
                                      'OPEN':stock['open'].replace(',',''),'HIGH':stock['high'],
                                      'LOW':stock['low'].replace(',',''),'VOL':str(int(float(stock['trdVol'].replace(',',''))*100000))}
    return stocklive

def getHistoricDataNSE(stock):
    stockHist = {}
    try:
        url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/getHistoricalData.jsp?symbol="+stock+"&series=EQ&fromDate=undefined&toDate=undefined&datePeriod=1day"
        resp = session.get(url, headers=headers)
        page_html = resp.text
        resp.close()        
        page_soup = soup (page_html, "html.parser")
        td = page_soup.find("table").find("tbody").find_all("td")
        openPrice = td[3].text.strip().replace(',','')
        dayHigh = td[4].text.strip().replace(',','')
        dayLow = td[5].text.strip().replace(',','')
        volume = td[8].text.strip().replace(',','')
        stockHist[stock] = {'OPEN':openPrice,'HIGH':dayHigh,'LOW':dayLow,'VOL':volume}
        return stockHist
    except:
        print(traceback.format_exc())
        stockHist[stock] = {'OPEN':'NA','HIGH':'NA','LOW':'NA','VOL':'NA'}
        return stockHist

def getHistoricDataNSEweek(stock):
    stockdataWeek = []
    try:
        url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/getHistoricalData.jsp?symbol="+stock+"&series=EQ&fromDate=undefined&toDate=undefined&datePeriod=week"
        resp = session.get(url, headers=headers)
        page_html = resp.text
        resp.close()        
        page_soup = soup (page_html, "html.parser")
        table_body = page_soup.find("table").find("tbody")
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            stockdataWeek.append([ele for ele in cols if ele])
        stockdataWeek = stockdataWeek[1:]
        return stockdataWeek
    except:
        print(traceback.format_exc())

def calcPricePoints(price,tradetype):
    if tradetype =='BUY':
        BUY = round(price+0.5,2)
        TARGET = round(BUY+0.003*BUY,2)
        STOPLOSS = round(BUY-0.003*BUY,2)
        pricepoints = {'TYPE': tradetype, 'PRICE':BUY, 'TARGET':TARGET, 'STOPLOSS':STOPLOSS}
    if tradetype =='SELL':
        SELL = round(price-0.5,2)
        TARGET = round(SELL-0.003*SELL,2)
        STOPLOSS = round(SELL+0.003*SELL,2)
        pricepoints = {'TYPE': tradetype, 'PRICE':SELL, 'TARGET':TARGET, 'STOPLOSS':STOPLOSS}
    return pricepoints

def process_ohl_algo():
    stocksval = {}
    try:
        stocklive = getLiveQuotes()
        for key,val in stocklive.items():
            if val['OPEN'] == val['LOW']:
                stocksval[key] = calcPricePoints(float(val['HIGH'].replace(',','')),'BUY'),val,findAVGPrice(key)
            if val['OPEN'] == val['HIGH']:
                stocksval[key] = calcPricePoints(float(val['LOW'].replace(',','')),'SELL'),val,findAVGPrice(key)
        return stocksval
    except:
        print(traceback.format_exc())
        return stocksval

def findAVGPrice(stock):
    try:
        url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol="+stock
        resp = session.get(url, headers=headers)
        req_html = resp.text
        resp.close() 
        req_soup = soup (req_html, "html.parser")
        jsonresp = req_soup.find("div",{'id':"responseDiv"}).text.strip()
        companydata = json.loads(jsonresp)
        averagePrice = companydata['data'][0]['averagePrice'].strip().replace(',','')
        return averagePrice
    except:
        #print(traceback.format_exc()) 
        return '0'
    
def monitorTimes(starttime,endtime):
    now = datetime.datetime.now()
    if starttime == 'NA':
        starttime = '00:00'
    if endtime == 'NA':
        endtime = '23:59'
    starttimedt = now.replace(hour=int(starttime[0:2]), minute=int(starttime[3:5]), second=0, microsecond=0)
    endtimedt =  now.replace(hour=int(endtime[0:2]), minute=int(endtime[3:5]), second=0, microsecond=0)   
    if starttimedt <= now <= endtimedt:
        return True
    else:
        return False

def PrettyPrint(stocks):
    for stockkey,stockval in stocks.items():
        print('',stockkey,'=>',stockval)

def findStocks():
    global FINDTRADESIG
    stocksval = {}
    print(datetime.datetime.now(),'-----------------------------------')
    if FINDTRADESIG:
        print(datetime.datetime.now(),'Finding Stocks to Buy.')
        stocksval = process_ohl_algo() 
        if len(stocksval) > 0:
            PrettyPrint(stocksval)  
        else:
            print(datetime.datetime.now(),'No Stocks to buy.')
    else:
        print(datetime.datetime.now(),'OHL Needs market to be closed.')
    return stocksval

FINDTRADESIG = False
if monitorTimes('09:15','15:15'):
    print(datetime.datetime.now(),'Market Open.')
    FINDTRADESIG = True
if monitorTimes('00:00','09:14') or monitorTimes('15:15','23:59'):
    print(datetime.datetime.now(),'Market Closed.')
    FINDTRADESIG = True

findStocks()


print("\n\nEnd of Script.")
session.close()
end = time.time()
print('Time taken:',end - start, 'Seconds')
input('Press Enter key to exit.. ')

