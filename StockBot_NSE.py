import requests
from bs4 import BeautifulSoup as soup
import datetime
import time
import json
import traceback

session = requests.session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
BUYCHANGEPERCENT = 1.5
BUYVOLPERCENT = 7

start = time.time() 
def getLiveQuotes():
    stocklive = {}
    try:
        url = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json"
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
        url = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json"
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
                                      'OPEN':stock['open'].replace(',',''),'HIGH':stock['high'].replace(',',''),
                                      'LOW':stock['low'].replace(',',''),'VOL':str(int(float(stock['trdVol'].replace(',',''))*100000))}
    return stocklive

def getHistoricDataQ(stock):
    stockHist = {}
    try:
        url = "https://www.quandl.com/api/v3/datasets/NSE/"+stock+".json?api_key=Wfet2ExkKrxgKg8n-w4q&limit=1"
        resp = session.get(url, headers=headers)
        json_data =  resp.json()
        resp.close()        
        openPrice = json_data['dataset']['data'][0][1].replace(',','')
        dayLow = json_data['dataset']['data'][0][3].replace(',','')
        dayHigh = json_data['dataset']['data'][0][2].replace(',','')
        volume = json_data['dataset']['data'][0][6].replace(',','')
        
        stockHist[stock] = {'OPEN':openPrice,'HIGH':dayHigh,'LOW':dayLow,'VOL':volume}
        return stockHist
    except:
        print(traceback.format_exc())
        stockHist[stock] = {'OPEN':'NA','HIGH':'NA','LOW':'NA','VOL':'NA'}
        return stockHist

def getHistoricDataNSE(stock):
    stockHist = {}
    try:
        url = "https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/getHistoricalData.jsp?symbol="+stock+"&series=EQ&fromDate=undefined&toDate=undefined&datePeriod=1day"
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
    volume,AVGVolume = 0,0
    try:
        url = "https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/getHistoricalData.jsp?symbol="+stock+"&series=EQ&fromDate=undefined&toDate=undefined&datePeriod=week"
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
        for stockVol in stockdataWeek:
            volume += int(stockVol[8].strip().replace(',',''))
        AVGVolume = volume/ len(stockdataWeek)
        return AVGVolume
    except:
        #print(traceback.format_exc()) 
        return AVGVolume

def process_stocks_pct(stocklive):
    stocksval1 = {}
    for stock in stocklive.items():
        if float(stock[1]['PCT']) >= BUYCHANGEPERCENT:
            #print(stock[0],float(stock[1]['PCT']))
            stocksval1[stock[0]] = stock[1]
    return stocksval1

def process_stocks_vol(stocksval1):
    stocksval2 = {}
    for stock in stocksval1.items():
        stockHist = getHistoricDataNSE(stock[0])
        #print(stock[0],int(stock[1]['VOL']),'>', int(stockHist[stock[0]]['VOL']))
        if int(stock[1]['VOL']) >= int(stockHist[stock[0]]['VOL']):
            stocksval2[stock[0]] = stock[1]
    return stocksval2

def process_stocks_volAVG(stocksval1):
    stocksval2 = {}
    for stock in stocksval1.items():
        stockAVGVol = getHistoricDataNSEweek(stock[0])
        if stockAVGVol == 0:
            STOCKPCTVOLAVG = 0
        else:
            STOCKPCTVOLAVG = (int(stock[1]['VOL'])*100)/stockAVGVol
            
        if STOCKPCTVOLAVG >= BUYVOLPERCENT:
            stocksval2[stock[0]] = stock[1]
    return stocksval2

def process_quora_algo():
    stocksval2tmp,stockvalREM = {},{}
    try:
        stocklive = getLiveQuotes()
        stocksval1 = process_stocks_pct(stocklive)
        #print('-------------------------1:',stocksval1)
        stocksval2tmp = process_stocks_volAVG(stocksval1)
        #print('-------------------------2:',stocksval1)
        return stocksval2tmp
    except:
        print(traceback.format_exc())
        return stocksval2tmp

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

def findAVGPrice(stock):
    try:
        url = "https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol="+stock
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

def PrettyPrint(stocks):
    try:
        for stockkey,stockval in stocks.items():
            #print('                           ',stockkey,'=>',stockval)
            print(' ',stockkey,'=>',stockval)
    except:
        print(traceback.format_exc())

              
stocksFINAL,stocksTOBUY,stocksBUY,stocksSELL = {},{},{},{}
VALTIME ='20:00' #'09:28'
MONITORTIME = '23:35' #'09:30'
MONITORTILL = '23:50'#'15:15'

if monitorTimes('09:15','15:15'):
    print(datetime.datetime.now(),'Market Open.')
if monitorTimes('00:00','09:14') or monitorTimes('15:15','23:59'):
    print(datetime.datetime.now(),'Market Closed.')

stockREMBUY,stockREMSELL,stocksFINALtmp,stocksFINALREM, MYSTOCKS = {},{},{},{},{}
#time.sleep(22000)    
while 1:
    print(datetime.datetime.now(),'-----------------------------------')  
	
    if monitorTimes(VALTIME,MONITORTIME):
        print(datetime.datetime.now(),'Finding Stocks to Buy.')
        stocksFINALtmp = process_quora_algo()
        stocksFINALREM = {k:v for k,v in stocksFINALtmp.items() if k not in stocksFINAL}
        stocksFINAL.update(stocksFINALtmp)     
        if len(stocksFINALREM) > 0:
            stocksFINALREM = UpdateLiveQuotes(stocksFINALREM)
            for stock in stocksFINALREM.items():
                stocksTOBUY[stock[0]] = {'LTP':stock[1]['LTP'],'OPEN':stock[1]['OPEN'],'HIGH':stock[1]['HIGH'],'STOPLOSS':findAVGPrice(stock[0])}
            PrettyPrint(stocksTOBUY)
            stockREMBUY = stocksTOBUY
        else:
            print(datetime.datetime.now(),'No Stocks to buy.')
            
    if monitorTimes(MONITORTIME,MONITORTILL):
        print(datetime.datetime.now(),'------------Monitoring-------------')
        ##BUY
        stockREMBUY = UpdateLiveQuotes(stockREMBUY)
        #PrettyPrint(stockREMBUY)
        for stock in stockREMBUY.items():
            if float(stock[1]['LTP']) >= float(stock[1]['HIGH']):
                print(datetime.datetime.now(),'BUYING')
                PrettyPrint(stock)
                stockREMBUY.pop(stock)
                stockREMSELL.update(stock)
                MYSTOCKS = {}
        ##SELL
        stockREMSELL = UpdateLiveQuotes(stockREMSELL)
        #PrettyPrint(stockREMSELL)
        for stock in stockREMSELL.items():                
            if float(stock[1]['LTP']) >= float(findAVGPrice(stock[0])):
                print(datetime.datetime.now(),'SELLING')
                PrettyPrint(stock)
                stockREMSELL.pop(stock)
            if float(stock[1]['LTP']) >= float(findAVGPrice(stock[0])):
                print(datetime.datetime.now(),'SELLING')
                PrettyPrint(stock)
                stockREMSELL.pop(stock)
        stocksSELL.update(stockREMSELL)
    time.sleep(10)

print("\n\nEnd of Script.")
session.close()
end = time.time()
print('Time taken:',end - start, 'Seconds')
input('Press Enter key to exit.. ')

