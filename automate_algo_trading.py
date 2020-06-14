import os
import alpaca_trade_api as tradeapi
import pandas as pd
import requests

def pairs_trading_algo():
    
    #Specify paper trading environment 
    # os.environ["APCA_API_BASE_URL"] = "https://paper-api.alpaca.markets"
    #Insert API Credentials 
    api = tradeapi.REST() # or use ENV Vars shown below
    account = api.get_account()
    print(account.status)
        
    #Selection of stocks
    days = 1000
    stock1 = 'MSFT'
    stock2 = 'AAPL'
    #Put Hisrorical Data into variables
    stock1_barset = api.get_barset(stock1,'day',limit=days)
    stock2_barset = api.get_barset(stock2,'day',limit=days)
    stock1_bars = stock1_barset[stock1]
    stock2_bars = stock2_barset[stock2]
    #Grab stock1 data and put in to a array
    data_1 = []
    times_1 = []
    for i in range(days):
        stock1_close = stock1_bars[i].c
        stock1_time = stock1_bars[i].t
        data_1.append(stock1_close)
        times_1.append(stock1_time)
    #Grab stock2 data and put in to an array
    data_2 = []
    times_2 = []
    for i in range(days):
        stock2_close = stock2_bars[i].c
        stock2_time = stock1_bars[i].t
        data_2.append(stock2_close)
        times_2.append(stock2_time)
    #Putting them together
    hist_close = pd.DataFrame(data_1, columns=[stock1])
    hist_close[stock2] = data_2
    #Current Spread between the two stocks
    stock1_curr = data_1[days-1]
    print('stock1_curr', stock1_curr)
    stock2_curr = data_2[days-1]
    print('stock2_curr', stock2_curr)    
    spread_curr = (stock1_curr-stock2_curr)
    print('spread_curr', spread_curr)
    #Moving Average of the two stocks
    move_avg_days = 5
    #Moving averge for stock1
    stock1_last = []
    for i in range(move_avg_days):
        stock1_last.append(data_1[(days-1)-i])
    print(stock1_last)
    stock1_hist = pd.DataFrame(stock1_last)
    print('stock1_hist', stock1_hist)
    stock1_mavg = stock1_hist.mean()
    print('stock1_mavg', stock1_mavg)
    #Moving average for stock2
    stock2_last = []
    for i in range(move_avg_days):
        stock2_last.append(data_2[(days-1)-i])
    print(stock2_last)
    stock2_hist = pd.DataFrame(stock2_last)
    print('stock2_hist', stock2_hist)
    stock2_mavg = stock2_hist.mean()
    print('stock2_mavg', stock2_mavg)
    #Sread_avg
    print(stock1_mavg - stock2_mavg)
    spread_avg = min(stock1_mavg - stock2_mavg)
    print('spread_avg', spread_avg)
    #Spread_factor
    spreadFactor = .01
    wideSpread = spread_avg*(1+spreadFactor)
    print('wideSpread', wideSpread)
    thinSpread = spread_avg*(1-spreadFactor)
    print('thinSpread', thinSpread)
    #Calc_of_shares_to_trade
    cash = float(account.buying_power)
    print('cash', cash)
    limit_stock1 = cash//stock1_curr
    print('limit_stock1', limit_stock1)
    limit_stock2 = cash//stock2_curr
    print('limit_stock2', limit_stock2)
    number_of_shares = int(min(limit_stock1, limit_stock2)/2)
    print('number_of_shares', number_of_shares)
    
    #Trading_algo
    portfolio = api.list_positions()
    clock = api.get_clock()
    
    if clock.is_open == True:
        if bool(portfolio) == False:
            #detect a wide spread
            if spread_curr > wideSpread:
                #short top stock
                api.submit_order(symbol = stock1,qty = number_of_shares,side = 'sell',type = 'market',time_in_force ='day')
                #Long bottom stock
                api.submit_order(symbol = stock2,qty = number_of_shares,side = 'buy',type = 'market',time_in_force = 'day')
                mail_content = "Trades have been made, short top stock and long bottom stock"
            #detect a tight spread
            elif spread_curr < thinSpread:
                #long top stock
                api.submit_order(symbol = stock1,qty = number_of_shares,side = 'buy',type = 'market',time_in_force = 'day')
                #short bottom stock
                api.submit_order(symbol = stock2,qty = number_of_shares,side = 'sell',type = 'market',time_in_force ='day')
                mail_content = "Trades have been made, long top stock and short bottom stock"
        else:
            wideTradeSpread = spread_avg *(1+spreadFactor + .03)
            thinTradeSpread = spread_avg *(1+spreadFactor - .03)
            if spread_curr <= wideTradeSpread and spread_curr >=thinTradeSpread:
                api.close_position(stock1)
                api.close_position(stock2)
                mail_content = "Position has been closed"
            else:
                mail_content = "No trades were made, position remains open"
                pass
    else:
        mail_content = "The Market is Closed"
        
    domain_name = os.environ.get('MAILGUN_DOMAIN')
    api_key = os.environ.get('MAILGUN_API_KEY')
    from_address = f"Trade Bot <mailgun@{domain_name}>"
    receiver_email_address = os.environ.get('RECEIVER_EMAIL')
    subject = 'Pairs Trading Algo'
    send_message(domain_name, api_key, from_address, receiver_email_address, subject, mail_content)
    return True

def send_message(domain_name, api_key, from_address, receiver_email_address, subject, mail_content):
    url = f"https://api.mailgun.net/v3/{domain_name}/messages"
    return requests.post(
        url,
        auth=("api", api_key),
        data={"from": from_address,
              "to": receiver_email_address,
              "subject": subject,
              "text": mail_content})