import requests
from bs4 import BeautifulSoup as soup
import datetime
import time
import json
import traceback

session = requests.session()

URL = "https://www.nseindia.com/api"
INDEX = "NIFTY 50"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
CHANGEPERCENT = 0.3

start = time.time()

session = requests.Session() 

##################NSE API####################

def requestURLdata(URLEXT):
    try:
        time.sleep(0.2)
        #url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        url = URL + URLEXT
        #print('URL:',url)
        resp = session.get(url,headers=headers)
        json_data = resp.json()
        resp.close()
    except:
        print(traceback.format_exc())         

    return json_data

def formatURL(keyword):
    keyword = keyword.replace('&','%26')
    keyword = keyword.replace(' ','%20')
    return keyword

def getLiveQuotes():
    stocklive = {}
    try:
        api_url = "/equity-stockIndices?index="+formatURL(INDEX)
        json_data = requestURLdata(api_url)
        stockdata = json_data['data']
        stocklive = FormatStockData(stockdata,'LIVE')
    except:
        print(traceback.format_exc())         

    return stocklive

def UpdateLiveQuotes(updatestocks):
    try:
        stocklive = getLiveQuotes()
        for stock in updatestocks:
            updatestocks[stock] = stocklive[stock]
    except:
        print(traceback.format_exc())         

    return updatestocks

def getTradeInfo(stock):
    tradeinfo = {}
    try:
        api_url = "/quote-equity?symbol="+formatURL(stock)+"&section=trade_info"
        json_data = requestURLdata(api_url)
        stockdata = json_data['marketDeptOrderBook']
        tradeinfo = FormatStockData(stockdata,'TRADE')
    except:
        print(traceback.format_exc())         
    return tradeinfo

def getHistoricDataNSE(stock):
    stockHist = {}
    try:       
        api_url = "/historical/cm/equity?symbol="+formatURL(stock)
        json_data = requestURLdata(api_url)        
        stockdata = json_data['data']
        stockHist = FormatStockData(stockdata,'HIST')
    except:
        print(traceback.format_exc())
    return stockHist

def getPreviousDayData(stock):
    previousdaydata = {}
    try:
        stockHist = getHistoricDataNSE(stock)
        previousdaydata = stockHist[0]   
    except:
        print(traceback.format_exc()) 
    return previousdaydata

def FormatStockData(stockdata,formattype):
    formatteddata = {}
    if formattype == 'LIVE':
        for i,stock in enumerate(stockdata):
            if stock['symbol'] == INDEX:
                continue
            formatteddata[stock['symbol']] = {'LTP':stock['lastPrice'],
                                              'PCT':stock['pChange'],
                                              'OPEN':stock['open'],
                                              'HIGH':stock['dayHigh'],
                                              'LOW':stock['dayLow'],
                                              'PREVCLOSE':stock['previousClose'],
                                              'VOL':stock['totalTradedVolume']}

    elif  formattype == 'HIST':
        for i,stock in enumerate(stockdata):
            formatteddata[i] = {'OPEN':stock['CH_OPENING_PRICE'],
                                'CLOSE':stock['CH_CLOSING_PRICE'],
                                'HIGH':stock['CH_TRADE_HIGH_PRICE'],
                                'LOW':stock['CH_TRADE_LOW_PRICE'],
                                'VOL':stock['CH_TOT_TRADED_VAL'],
                                'VWAP':stock['VWAP'],
                                'DATE':stock['CH_TIMESTAMP']}

    elif  formattype == 'TRADE':
        formatteddata = {'BUYQUAN':stockdata['totalBuyQuantity'],
                         'SELLQUAN':stockdata['totalSellQuantity'],
                         'TOTALVOL':stockdata['tradeInfo']['totalTradedVolume']}
        
    return formatteddata



##################Stratergy####################
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

def process_ohl_algo(stocklive):
    stocksval = {}
    stocksUpd = {}
    try:
        for key,val in stocklive.items():
            if val['OPEN'] == val['LOW']:              
                stocksval[key] = calcPricePoints(val['HIGH'],'BUY'),val,{'VWAP':getPreviousDayData(key)['VWAP'],'TOTALVOL':getTradeInfo(key)['TOTALVOL']}
                stocksUpd[key] = val
            if val['OPEN'] == val['HIGH']:              
                stocksval[key] = calcPricePoints(val['LOW'],'SELL'),val,{'VWAP':getPreviousDayData(key)['VWAP'],'TOTALVOL':getTradeInfo(key)['TOTALVOL']}
                stocksUpd[key] = val
            
    except:
        print(traceback.format_exc())
    return stocksval, stocksUpd
    
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

def PrettyPrint_old(stocks):
    print('\n',datetime.datetime.now(),'\n')
    for stockkey,stockval in stocks.items():
        print('',stockkey,'=>',stockval)

def PrettyPrint(stocks):
    print(datetime.datetime.now(),'Stocks:\n')
    for stockkey,stockval in stocks.items():
        print('  '+stockkey+':')
        print('             ',stockval[0])
        print('             ',stockval[1])
        print('             ',stockval[2])

        
def findStocks(stocklive):
    global FINDTRADESIG
    stocksval,stocksUpd = {},{}
    print(datetime.datetime.now(),'-----------------------------------')
    if FINDTRADESIG:
        print(datetime.datetime.now(),'Finding Stocks to Buy.')
        stocksval,stocksUpd = process_ohl_algo(stocklive) 
    else:
        print(datetime.datetime.now(),'OHL Needs market to be closed.')
    return stocksval,stocksUpd


if __name__ == "__main__":
    
    FINDTRADESIG = False
    if monitorTimes('09:15','15:15'):
        print(datetime.datetime.now(),'Market Open.')
        FINDTRADESIG = False
    if monitorTimes('00:00','09:14') or monitorTimes('15:15','23:59'):
        print(datetime.datetime.now(),'Market Closed.')
        FINDTRADESIG = True
       
    StocksLive = getLiveQuotes()
    StocksTrade,StocksUpdate = findStocks(StocksLive)
    if len(StocksTrade) > 0:
        PrettyPrint(StocksTrade)  
    else:
        print(datetime.datetime.now(),'No Stocks to buy.')


print("\n\nEnd of Script.")
session.close()
end = time.time()
print('Time taken:',round(end - start,2), 'Seconds')

input('Press Enter key to exit.. ')


