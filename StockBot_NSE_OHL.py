import nseapi
import datetime
import time
import traceback
import tradingapi as ta

TRADETIME = '09:45'
SQUAREOFFTIME = '14:45'
TARGETPCT = 0.8

###############################################
##################Stratergy####################
def calcPricePoints(tradetype,stockval,stockinfo):
    GAINPCT = (abs(stockinfo['DAILYVOLATILITY'] - abs(stockval['PCT']))*TARGETPCT)/100
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
    stockinfo = {#'VWAP':nseapi.getPreviousDayData(stock)['VWAP'],
                 #'TOTALVOL':nseapi.getTradeInfo(stock)['TOTALVOL'],
                 'DAILYVOLATILITY':nseapi.getStockVolatility(stock)}
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

                if stockinfo['DAILYVOLATILITY'] > abs(stockval['PCT'])/0.4:
                    tradetype = tradetype+'-STRONG-VOLATILITY'               
                    
                stockstrade[stock] = calcPricePoints(tradetype,stockval,stockinfo),stockval,stockinfo
                stocksfinal[stock] = stockval
    except:
        print(traceback.format_exc())
    return stockstrade, stocksfinal

def tradeSignalOHL():
    FINDTRADESIG = False
    #if ta.monitorTimes('09:15','15:15'):    
    if ta.monitorTimes(TRADETIME,'15:15'):
        print(datetime.datetime.now(),'Market Open & Algo Triggered.')
        FINDTRADESIG = True
    #if ta.monitorTimes('00:00','09:14') or monitorTimes('15:15','23:59'):
    else:
        #print(datetime.datetime.now(),'Market Closed.')
        FINDTRADESIG = True
    return FINDTRADESIG
        
def findStocks():
    StocksLive, StocksTrade, StocksUpdate, StocksTradeEnter = {},{},{}, False
    try:
        StocksLive = nseapi.getLiveQuotes()
        StocksTrade,StocksUpdate = processAlgo_OHL(StocksLive)
        if len(StocksTrade) > 0:
            ta.PrettyPrint(StocksTrade)
            StocksTradeEnter = True
        else:
            print(datetime.datetime.now(),'No Stocks to buy.')
            StocksTradeEnter = False
    except:
        print(traceback.format_exc())
    return StocksTradeEnter, StocksLive, StocksTrade, StocksUpdate

def getFinalResult(StocksTrade):
    stocksfinaltrades = ta.getProfitLoss(StocksTrade)
    totalprofitloss = ta.getTotalProfitLoss(stocksfinaltrades)
    return stocksfinaltrades,totalprofitloss

print('\n')
start = time.time()

if __name__ == "__main__":
    nseapi.SessionStart()
    StocksTradeEnter = False

    while not StocksTradeEnter:
        print(datetime.datetime.now(),'-----------------------------------')  
        TradeSignal = tradeSignalOHL()
        if TradeSignal:
            print(datetime.datetime.now(),'Finding Stocks to Buy.')	    
            StocksTradeEnter,StocksLive,StocksTrade,StocksUpdate = findStocks()
        if not StocksTradeEnter:
            time.sleep(5)

    
    nseapi.SessionClose()

#stocksfinaltrades, totalprofitloss = getFinalResult(StocksTrade)
 
print('\n')
print(datetime.datetime.now(),'End of Script.\n')
end = time.time()
print('Time taken:',round(end - start,2), 'Seconds')

input('Press Enter key to exit.. ')
