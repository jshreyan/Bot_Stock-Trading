import datetime
import nseapi

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
    print('TOTALPROFITLOSS:',round(totalprofitloss,2))
    return round(totalprofitloss,2)
