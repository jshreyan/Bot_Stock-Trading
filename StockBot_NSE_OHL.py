import nseapi
import datetime
import time
import traceback

###############################################
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
        for stock,val in stocklive.items():
            if val['OPEN'] == val['LOW']:              
                stocksval[stock] = calcPricePoints(val['HIGH'],'BUY'),val,{'VWAP':nseapi.getPreviousDayData(session,stock)['VWAP'],
                                                                         'TOTALVOL':nseapi.getTradeInfo(session,stock)['TOTALVOL']}
                stocksUpd[stock] = val
            if val['OPEN'] == val['HIGH']:              
                stocksval[stock] = calcPricePoints(val['LOW'],'SELL'),val,{'VWAP':nseapi.getPreviousDayData(session,stock)['VWAP'],
                                                                         'TOTALVOL':nseapi.getTradeInfo(session,stock)['TOTALVOL']}
                stocksUpd[stock] = val
            
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

start = time.time()

if __name__ == "__main__":

    session = nseapi.SessionStart()
    
    FINDTRADESIG = False
    if monitorTimes('09:15','15:15'):
        print(datetime.datetime.now(),'Market Open.')
        FINDTRADESIG = False
    if monitorTimes('00:00','09:14') or monitorTimes('15:15','23:59'):
        print(datetime.datetime.now(),'Market Closed.')
        FINDTRADESIG = True

    StocksLive = nseapi.getLiveQuotes(session)
    StocksTrade,StocksUpdate = findStocks(StocksLive)
    if len(StocksTrade) > 0:
        PrettyPrint(StocksTrade)  
    else:
        print(datetime.datetime.now(),'No Stocks to buy.')

    nseapi.SessionClose(session)


print("\n\nEnd of Script.")
end = time.time()
print('Time taken:',round(end - start,2), 'Seconds')

input('Press Enter key to exit.. ')
