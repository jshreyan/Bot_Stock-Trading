import requests
import json
import traceback
import time
import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
URL = "https://www.nseindia.com/api"
INDEX = "NIFTY 50"

SESSION = None


def SessionStart():
    global SESSION
    SESSION = requests.session()

def SessionClose():
    SESSION.close()

###############################################
##################NSE API######################

def requestURLdata(URLEXT):
    try:
        time.sleep(0.2)
        #url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        url = URL + URLEXT
        #print('URL:',url)
        resp = SESSION.get(url,headers=headers)
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

def getStockVolatility(stock):
    dailyvolatility = 0
    try:       
        api_url = "/quote-derivative?symbol="+formatURL(stock)
        json_data = requestURLdata(api_url)        
        dailyvolatility = json_data['stocks'][0]['marketDeptOrderBook']['otherInfo']['dailyvolatility']
    except:
        print(traceback.format_exc())
    return dailyvolatility

def getDayTrade(stock):
    DayTrade = {}
    try: 
        api_url = '/chart-databyindex?index='+formatURL(stock)+'EQN'
        json_data = requestURLdata(api_url)
        DayTrade = json_data['grapthData']
    except:
        print(traceback.format_exc())        
    return DayTrade

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
    

if __name__ == "__main__":
    SessionStart()















