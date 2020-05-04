import requests
from bs4 import BeautifulSoup as soup
import datetime
import time
import json
import traceback

session = requests.session()

URL = "https://www.nseindia.com/api"
INDEX = "NIFTY 200"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
CHANGEPERCENT = 0.3

start = time.time() 

def requestURLdata(URLEXT):
    try:    
        #url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        url = URL + URLEXT
        resp = session.get(url,headers=headers)
        json_data = resp.json()
        resp.close()
    except:
        print(traceback.format_exc())         

    return json_data

def getLiveQuotes():
    stocklive = {}
    try:
        api_url = "/equity-stockIndices?index="+INDEX
        json_data = requestURLdata(api_url)
        stockdata = json_data['data']
        stocklive = FormatStockData(stockdata,'LIVE')
    except:
        print(traceback.format_exc())         

    return stocklive

def UpdateLiveQuotes(updatestocks):
    stocklive = {}
    try:
        api_url = "/equity-stockIndices?index="+INDEX
        json_data = requestURLdata(api_url)
        stockdata = json_data['data']
        stocklive = FormatStockData(stockdata,'LIVE')
        for stock in updatestocks:
            updatestocks[stock] = stocklive[stock]
    except:
        print(traceback.format_exc())         

    return updatestocks

def FormatStockData(stockdata,formattype):
    formatteddata = {}
    for i,stock in enumerate(stockdata):
        if formattype == 'LIVE':
            formatteddata[stock['symbol']] = {'LTP':stock['lastPrice'],
                                              'PCT':stock['pChange'],
                                              'OPEN':stock['open'],
                                              'HIGH':stock['dayHigh'],
                                              'LOW':stock['dayLow'],
                                              'VOL':stock['totalTradedVolume']}
        elif  formattype == 'HIST':
            formatteddata[i] = {'OPEN':stock['CH_OPENING_PRICE'],
                                              'CLOSE':stock['CH_CLOSING_PRICE'],
                                              'HIGH':stock['CH_TRADE_HIGH_PRICE'],
                                              'LOW':stock['CH_TRADE_LOW_PRICE'],
                                              'VOL':stock['CH_TOT_TRADED_VAL'],
                                              'VWAP':stock['VWAP'],
                                              'DATE':stock['CH_TIMESTAMP']}    
    return formatteddata

def getHistoricDataNSE(stock):
    stockHist = {}
    try:       
        api_url = "/historical/cm/equity?symbol="+stock
        json_data = requestURLdata(api_url)        
        stockdata = json_data['data']
        stockHist = FormatStockData(stockdata,'HIST')
    except:
        print(traceback.format_exc())
    return stockHist

def findAVGPrice(stock):
    try:
        stockHist = getHistoricDataNSE(stock)
        averagePrice = stockHist[0]['VWAP']     
    except:
        print(traceback.format_exc()) 
    return averagePrice

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
            vwap = findAVGPrice(key)
            if val['OPEN'] == val['LOW']:
                stocksval[key] = calcPricePoints(float(val['HIGH'].replace(',','')),'BUY'),val,vwap
            if val['OPEN'] == val['HIGH']:
                stocksval[key] = calcPricePoints(float(val['LOW'].replace(',','')),'SELL'),val,vwap
    except:
        print(traceback.format_exc())
    return stocksval
    
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
"""

url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
#url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200"
resp = session.get(url,headers=headers)
json_data = resp.json()
resp.close()        
stockdata = json_data['data']
stocklive = {}
for stock in stockdata:
    stocklive[stock['symbol']] = {'LTP':stock['lastPrice'],'PCT':stock['pChange'],
                                  'OPEN':stock['open'],'HIGH':stock['dayHigh'],
                                  'LOW':stock['dayLow'],'VOL':stock['totalTradedVolume']}




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

"""
input('Press Enter key to exit.. ')

