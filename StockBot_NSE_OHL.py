import nseapi
import datetime
import time
import traceback

###############################################
##################Stratergy####################
def calcPricePoints(tradetype,stockval,stockinfo):
    GAINPCT = (abs(stockinfo['DAILYVOLATILITY'] - abs(stockval['PCT']))*0.75)/100
    #print('GAINPCT',GAINPCT,'DAILYVOLATILITY',stockinfo['DAILYVOLATILITY'],'PCT',stockval['PCT'])
    if 'BUY' in tradetype:
        BUY = stockval['LTP']
        TARGET = round(BUY+(GAINPCT*BUY),2)
        pricepoints = {'TYPE': tradetype, 'PRICE':BUY, 'TARGET':TARGET, 'STOPLOSS':stockval['LOW']}
    if 'SELL' in tradetype:
        SELL = stockval['LTP']
        TARGET = round(SELL-(GAINPCT*SELL),2)
        pricepoints = {'TYPE': tradetype, 'PRICE':SELL, 'TARGET':TARGET, 'STOPLOSS':stockval['HIGH']}
    return pricepoints


def getstockinfo(stock):
    stockinfo = {#'VWAP':nseapi.getPreviousDayData(session,stock)['VWAP'],
                 #'TOTALVOL':nseapi.getTradeInfo(session,stock)['TOTALVOL'],
                 'DAILYVOLATILITY':nseapi.getStockVolatility(session,stock)}
    return stockinfo

def processAlgo_OHL(stocklive):
    stockstrade,stocksfinal = {},{}
    try:
        for stock,stockval in stocklive.items():
            if stockval['OPEN'] == stockval['LOW'] or stockval['OPEN'] == stockval['HIGH']:
                stockinfo = getstockinfo(stock)
                if stockval['OPEN'] == stockval['LOW']:                    
                    tradetype = 'BUY'
                if stockval['OPEN'] == stockval['HIGH']:
                    tradetype = 'SELL'

                if stockinfo['DAILYVOLATILITY'] > abs(stockval['PCT'])/0.6:
                    tradetype = tradetype+'-STRONG-VOLATILITY'               
                    
                stockstrade[stock] = calcPricePoints(tradetype,stockval,stockinfo),stockval,stockinfo
                stocksfinal[stock] = stockval
    except:
        print(traceback.format_exc())
    return stockstrade, stocksfinal

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

def tradeSignalOHL():
    FINDTRADESIG = False
    #if monitorTimes('09:15','15:15'):    
    if monitorTimes('09:44','15:15'):
        print(datetime.datetime.now(),'Market Open & Algo Triggered.')
        FINDTRADESIG = True
    #if monitorTimes('00:00','09:14') or monitorTimes('15:15','23:59'):
    else:
        #print(datetime.datetime.now(),'Market Closed.')
        FINDTRADESIG = False
    return FINDTRADESIG

def PrettyPrint(stocks):
    print(datetime.datetime.now(),'Stocks:\n')
    for stockkey,stockval in stocks.items():
        #print('',stockkey,'=>',stockval)
        print('  '+stockkey+':')
        print('             ',stockval[0])
        print('             ',stockval[1])
        print('             ',stockval[2])
        
def findStocks():
    StocksLive, StocksTrade, StocksUpdate, StocksTradeEnter = {},{},{}, False
    try:
        StocksLive = nseapi.getLiveQuotes(session)
        StocksTrade,StocksUpdate = processAlgo_OHL(StocksLive)
        if len(StocksTrade) > 0:
            PrettyPrint(StocksTrade)
            StocksTradeEnter = True
        else:
            print(datetime.datetime.now(),'No Stocks to buy.')
            StocksTradeEnter = False
    except:
        print('ERROR')
    return StocksTradeEnter, StocksLive, StocksTrade, StocksUpdate


print('\n')
start = time.time()

if __name__ == "__main__":
    session = nseapi.SessionStart()
    StocksTradeEnter = False

    while not StocksTradeEnter:
        print(datetime.datetime.now(),'-----------------------------------')  
        TradeSignal = tradeSignalOHL()
        if TradeSignal:
            print(datetime.datetime.now(),'Finding Stocks to Buy.')	    
            StocksTradeEnter,StocksLive,StocksTrade,StocksUpdate = findStocks()
        if not StocksTradeEnter:
            time.sleep(5)
            
    nseapi.SessionClose(session)


print('\n')
print(datetime.datetime.now(),'End of Script.\n')
end = time.time()
print('Time taken:',round(end - start,2), 'Seconds')

input('Press Enter key to exit.. ')
