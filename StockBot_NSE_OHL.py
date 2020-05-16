import nseapi
import datetime
import time
import traceback
import tradingapi as ta
import math

TRADETIME = '09:45'
ta.TRADETIME = TRADETIME
SQUAREOFFTIME = '10:00'
ta.SQUAREOFFTIME = SQUAREOFFTIME

TARGETPCT = 0.8
STOPLOSSPCT = TARGETPCT/2
TRADESTRENGTH = 0.4

#TEST = True

###############################################
##################Stratergy####################

def calcPricePoints(stock,tradetype,stockval,stockinfo):
    LTPATNINE = ta.getTradeStartPoints(stock)
    ltppct = round((LTPATNINE - stockval['PREVCLOSE'])/stockval['PREVCLOSE']*100,2)
    if abs(ltppct)/0.8 > stockinfo['DAILYVOLATILITY']:
        GAINPCT = 0
    else:
        GAINPCT = math.ceil((abs(stockinfo['DAILYVOLATILITY'] - abs(ltppct))*TARGETPCT)) #TARGETPCT

    if 'STRONG' in tradetype:
        PRIORITY = 1
    elif GAINPCT != 0:
        PRIORITY = 2
    elif GAINPCT == 0:
        PRIORITY = 3
  
    #print('GAINPCT',GAINPCT,'DAILYVOLATILITY',stockinfo['DAILYVOLATILITY'],'PCT',stockval['PCT'])
    if 'BUY' in tradetype:
        BUY = LTPATNINE
        STOPLOSS = stockval['LOW'] #round(BUY-((STOPLOSSPCT/100)*BUY),2)
        TARGET = round(BUY+((GAINPCT/100)*BUY),2)
        pricepoints = {'PRIORITY':PRIORITY,'TYPE': tradetype, 'PRICE':BUY, 'TARGET':TARGET, 'STOPLOSS':stockval['LOW'],'TRADEPCT':ltppct,'EXPECTEDGAIN':GAINPCT}
    if 'SELL' in tradetype:
        SELL = LTPATNINE
        STOPLOSS = stockval['HIGH'] #round(SELL+((STOPLOSSPCT/100)*SELL),2)
        TARGET = round(SELL-((GAINPCT/100)*SELL),2)
        pricepoints = {'PRIORITY':PRIORITY,'TYPE': tradetype, 'PRICE':SELL, 'TARGET':TARGET, 'STOPLOSS':stockval['HIGH'],'TRADEPCT':ltppct,'EXPECTEDGAIN':GAINPCT}
    return pricepoints

def calcPricePointsLive(tradetype,stockval,stockinfo):
    GAINPCT = (abs(stockinfo['DAILYVOLATILITY'] - abs(stockval['PCT']))*TARGETPCT)/100

    if abs(stockval['PCT'])/0.8 > stockinfo['DAILYVOLATILITY']:
        GAINPCT = 0
    else:
        GAINPCT = math.ceil((abs(stockinfo['DAILYVOLATILITY'] - abs(stockval['PCT']))*TARGETPCT)) #TARGETPCT

    if 'STRONG' in tradetype:
        PRIORITY = 1
    elif GAINPCT != 0:
        PRIORITY = 2
    elif GAINPCT == 0:
        PRIORITY = 3

    if 'BUY' in tradetype:
        BUY = stockval['LTP']
        TARGET = round(BUY+((GAINPCT/100)*BUY),2)
        pricepoints = {'PRIORITY':PRIORITY,'TYPE': tradetype, 'PRICE':BUY, 'TARGET':TARGET, 'STOPLOSS':stockval['LOW'],'TRADEPCT':stockval['PCT'],'EXPECTEDGAIN':GAINPCT}
    if 'SELL' in tradetype:
        SELL = stockval['LTP']
        TARGET = round(SELL-((GAINPCT/100)*SELL),2)
        pricepoints = {'PRIORITY':PRIORITY,'TYPE': tradetype, 'PRICE':SELL, 'TARGET':TARGET, 'STOPLOSS':stockval['HIGH'],'TRADEPCT':stockval['PCT'],'EXPECTEDGAIN':GAINPCT}
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

                if stockinfo['DAILYVOLATILITY'] > abs(stockval['PCT'])/TRADESTRENGTH:
                    tradetype = tradetype+'-STRONG-VOLATILITY'               
                    
                stockstrade[stock] = calcPricePointsLive(tradetype,stockval,stockinfo),stockval,stockinfo
                #stockstrade[stock] = calcPricePoints(stock,tradetype,stockval,stockinfo),stockval,stockinfo
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

    #nseapi.SessionClose()
print('\nStocksTrade:',datetime.datetime.now(),'\n',StocksTrade)

print('\nProfit and Loss:')
MARGIN = ta.getQuotesMargin()
ta.MARGIN = MARGIN 
#minprice = ta.getMinBuyQuantity(StocksTrade)
stocksfinaltrades, totalprofitloss = getFinalResult(StocksTrade)


print('\n')
print(datetime.datetime.now(),'End of Script.\n')
end = time.time()
print('Time taken:',round(end - start,2), 'Seconds')

input('Press Enter key to exit.. ')
