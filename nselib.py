from nsetools import Nse

stocks = ("TATASTEEL","SUNPHARMA","UPL","TECHM","VEDL","AUROPHARMA","HINDALCO","YESBANK","ONGC","BHARTIARTL","INFRATEL","BAJFINANCE","ICICIBANK","DRREDDY","POWERGRID","AMBUJACEM","INDUSINDBK","NTPC","SBIN","AXISBANK","IOC","HCLTECH","HDFCBANK","LUPIN","IBULHSGFIN","RELIANCE","BAJAJ-AUTO","TCS","KOTAKBANK","LT","MARUTI","ADANIPORTS","CIPLA","BPCL","HINDPETRO","ITC","TATAMOTORS","ZEEL","WIPRO","HEROMOTOCO","ULTRACEMCO","BOSCHLTD","HDFC","COALINDIA","M&M","HINDUNILVR","EICHERMOT","INFY","GAIL","ASIANPAINT")
nse = Nse()
buysig = None
sellsig = None

for stock in stocks:
    q = nse.get_quote(stock)
    
    lastPrice = q['lastPrice']
    openPrice = q['open']
    dayLow = q['dayLow']
    dayHigh = q['dayHigh']
    previousClose = q['previousClose']

    if openPrice == dayLow:
        buysig = "FAIR BUY"
        if openPrice > previousClose:
            buysig = "STRONG BUY"
        print(stock+":"+buysig)
        print(" lastPrice:"+str(lastPrice))
        print(" Open:"+str(openPrice))
        print(" dayLow:"+str(dayLow))
        print(" dayHigh:"+str(dayHigh))
        print(" previousClose:"+str(previousClose))
        print("\n")         
    if openPrice == dayHigh:
        sellsig = "FAIR SELL"
        if openPrice < previousClose:
            sellsig = "STRONG SELL"
        print(stock+":"+sellsig)            
        print(" lastPrice:"+str(lastPrice))
        print(" Open:"+str(openPrice))
        print(" dayLow:"+str(dayLow))
        print(" dayHigh:"+str(dayHigh))
        print(" previousClose:"+str(previousClose))
        print("\n") 



