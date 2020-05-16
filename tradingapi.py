import datetime
import nseapi
import zerodhaapi as za
import math

MARGIN = ()

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
    print(datetime.datetime.now(),'Stocks:\n')
    for stockkey,stockval in stocks.items():
        #print('',stockkey,'=>',stockval)
        print('  '+stockkey+':')
        print('             ',stockval[0])
        print('             ',stockval[1])
        print('             ',stockval[2])

def getTradeClosePoints(stock,stocktrade):
    stocksfinaltrades = {}
    DayTrade = nseapi.getDayTrade(stock)
    tradestarttime = datetime.datetime.now().replace(hour=int(TRADETIME[0:2]), minute=int(TRADETIME[3:5]), second=0, microsecond=0)
    marketclosetime = datetime.datetime.now().replace(hour=int(SQUAREOFFTIME[0:2]), minute=int(SQUAREOFFTIME[3:5]), second=0, microsecond=0)
    for pricepoint in DayTrade:
        pricetime = datetime.datetime.utcfromtimestamp(int(str(pricepoint[0])[:-3])).strftime('%Y-%m-%dT%H:%M:%SZ')
        pricetimedt = datetime.datetime.utcfromtimestamp(int(str(pricepoint[0])[:-3]))
        price = pricepoint[1]
        if 'BUY' in stocktrade['TYPE']:
            if (price >= stocktrade['TARGET'] or price <= stocktrade['STOPLOSS'] or pricetimedt >= marketclosetime) and pricetimedt>tradestarttime:
                difference = round(price - stocktrade['PRICE'],2)
                stocksfinaltrades[stock] = {'TYPE':'LONG','PROFITLOSS':difference,'CLOSETIME':pricetime,'CLOSEPRICE':stocktrade['PRICE']}
                #print(stock,'::',pricetime,difference)
                break
                
        if 'SELL' in stocktrade['TYPE']:
            if (price <= stocktrade['TARGET'] or price >= stocktrade['STOPLOSS'] or pricetimedt >= marketclosetime) and pricetimedt>tradestarttime:
                difference =  round(stocktrade['PRICE'] - price,2)                
                stocksfinaltrades[stock] = {'TYPE':'SHORT','PROFITLOSS':difference,'CLOSETIME':pricetime,'CLOSEPRICE':stocktrade['PRICE']}
                #print(stock,'::',pricetime,difference)
                break
            
    return stocksfinaltrades

def getTradeStartPoints(stock):
    price = None
    DayTrade = nseapi.getDayTrade(stock)
    tradestarttime = datetime.datetime.now().replace(hour=int(TRADETIME[0:2]), minute=int(TRADETIME[3:5]), second=0, microsecond=0)
    for pricepoint in DayTrade:
        pricetimedt = datetime.datetime.utcfromtimestamp(int(str(pricepoint[0])[:-3]))
        if pricetimedt >= tradestarttime:
            price = pricepoint[1]
            break
    return price

def getProfitLoss(stockstrade):
    stocksfinaltrades = {}
    for stock,stockval in stockstrade.items():
        stocksfinaltrades.update(getTradeClosePoints(stock,stockval[0]))
    return stocksfinaltrades

def getTotalProfitLoss(stocksfinaltrades):
    totalprofitloss = 0
    for stock,stockval in stocksfinaltrades.items():
        print(stock,'\n',stockval['CLOSETIME'],stockval['TYPE'],stockval['PROFITLOSS'])
        totalprofitloss  = totalprofitloss + stockval['PROFITLOSS']
    print('\nTOTALPROFITLOSS:',round(totalprofitloss,2))
    return round(totalprofitloss,2)

def getQuotesMargin():
    za.SessionStart()
    margin = za.getQuotesMargin()
    za.SessionClose()
    return margin

def getBuyQuantity():
    None

def getMinBuyQuantity(StocksTrade):
    print(MARGIN)
    minprice = 0
    for stock,stockval in StocksTrade.items():
        price = math.ceil(stockval[0]['PRICE']/float(MARGIN[stock]))
        minprice = minprice+price
    print('Min Buy Price:',minprice)
    return minprice


#MARGIN = getQuotesMargin()
#StocksTrade = {'DRREDDY': ({'TYPE': 'BUY', 'PRICE': 3974, 'TARGET': 3995.16, 'STOPLOSS': 3900.1},{'LTP': 3974, 'PCT': 3.55, 'OPEN': 3900.1, 'HIGH': 4132.2, 'LOW': 3900.1, 'PREVCLOSE': 3837.65, 'VOL': 596873},{'DAILYVOLATILITY': 2.84}),'HINDUNILVR': ({'TYPE': 'SELL', 'PRICE': 2055.7, 'TARGET': 2049.69, 'STOPLOSS': 2074.95},{'LTP': 2055.7, 'PCT': 3.2, 'OPEN': 2074.95, 'HIGH': 2074.95, 'LOW': 2039, 'PREVCLOSE': 1992.05, 'VOL': 3143230},{'DAILYVOLATILITY': 3.59}),'BAJFINANCE':({'TYPE': 'SELL-STRONG-VOLATILITY', 'PRICE': 2112.25, 'TARGET': 2048.72, 'STOPLOSS': 2130},{'LTP': 2112.25, 'PCT': 2.51, 'OPEN': 2130, 'HIGH': 2130,'LOW': 2085.35, 'PREVCLOSE': 2060.55, 'VOL': 1207926},{'DAILYVOLATILITY': 6.52}),'ZEEL': ({'TYPE': 'SELL-STRONG-VOLATILITY', 'PRICE': 149.8, 'TARGET': 144.22, 'STOPLOSS': 152.85},{'LTP': 149.8, 'PCT': 1.66, 'OPEN': 152.85, 'HIGH': 152.85, 'LOW': 149.25, 'PREVCLOSE': 147.35, 'VOL': 1647043},{'DAILYVOLATILITY': 6.63}),'GAIL': ({'TYPE': 'SELL-STRONG-VOLATILITY', 'PRICE': 92.9, 'TARGET': 91.07, 'STOPLOSS': 94.75},{'LTP': 92.9, 'PCT': 1.53, 'OPEN': 94.75, 'HIGH': 94.75, 'LOW': 92.1, 'PREVCLOSE': 91.5, 'VOL': 1431257},{'DAILYVOLATILITY': 4.16}),'SUNPHARMA': ({'TYPE': 'SELL-STRONG-VOLATILITY', 'PRICE': 457.95, 'TARGET': 450.98, 'STOPLOSS': 460},{'LTP': 457.95, 'PCT': 1.27, 'OPEN': 460, 'HIGH': 460, 'LOW': 454.05, 'PREVCLOSE': 452.2, 'VOL': 1261681},{'DAILYVOLATILITY': 3.3}),'HEROMOTOCO': ({'TYPE': 'SELL-STRONG-VOLATILITY', 'PRICE': 2004.5, 'TARGET': 1938.65, 'STOPLOSS': 2040},{'LTP': 2004.5, 'PCT': 0.21, 'OPEN': 2040, 'HIGH': 2040, 'LOW': 2000.15, 'PREVCLOSE': 2000.3, 'VOL': 154473},{'DAILYVOLATILITY': 4.59}),'HCLTECH': ({'TYPE': 'SELL-STRONG-VOLATILITY', 'PRICE': 504.9, 'TARGET': 494.37, 'STOPLOSS': 520.85},{'LTP': 504.9, 'PCT': -1.34, 'OPEN': 520.85, 'HIGH': 520.85, 'LOW': 504, 'PREVCLOSE': 511.75, 'VOL': 1728771},{'DAILYVOLATILITY': 4.12}),'POWERGRID': ({'TYPE': 'SELL', 'PRICE': 159, 'TARGET': 157.94, 'STOPLOSS': 162.6},{'LTP': 159, 'PCT': -1.7, 'OPEN': 162.6, 'HIGH': 162.6, 'LOW': 158.85, 'PREVCLOSE': 161.75, 'VOL': 951584},{'DAILYVOLATILITY': 2.59})}


	


	



