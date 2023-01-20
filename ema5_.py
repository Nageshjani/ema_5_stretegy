import yfinance as yf
import pandas as pd
import talib
import copy
import numpy as np


df = yf.Ticker("^NSEBANK").history(period="1mo", interval="5m")
df["EMA_5"] = talib.EMA(df["Close"], timeperiod=5)
trade = {"Symbol": None, "Buy/Sell": None, "Entry": None, "Entry Date": None, "Exit": None, "Exit Date": None,"maxx_possible":None}
trades_list=[]



pos='deactivated'
breakout_to_sell=None
breakout_to_buy=None


for i in df.index[6:]:
    if pos=='deactivated':
        if breakout_to_sell:
            #EntryToSell
            if df['Low'][i]<breakout_to_sell:
                trade["Symbol"] = "^NSEBANK"
                trade["Buy/Sell"] = "Sell" 
                trade["Entry"] = breakout_to_sell
                trade["Entry Date"] = i

                target=trade["Entry"]-300
                sl=trade["Entry"]+50
                pos='activated'
                maxx_possible=breakout_to_sell
        if breakout_to_buy:
            #EntryToBuy
            if df['High'][i]>breakout_to_buy:
                trade["Symbol"] = "^NSEBANK"
                trade["Buy/Sell"] = "Buy"
                trade["Entry"] = breakout_to_buy
                trade["Entry Date"] = i
                
                
                target=trade["Entry"]+300
                sl=trade["Entry"]-50
                pos='activated'
                maxx_possible=breakout_to_buy
                
        
        #BreakoutSell
        if df['Low'][i]>df['EMA_5'][i]:
            breakout_to_sell=df['Low'][i]
        
        #BreakoutBuy
        if df['High'][i]<df['EMA_5'][i]:
            breakout_to_buy=df['High'][i]
    else:
        
        if breakout_to_sell:
            maxx_possible=min(maxx_possible,df['Low'][i])
            #Exit+Profit(Sold)
            if df['Low'][i]<=target:
                trade["Exit"] = target
                trade["Exit Date"] = i
                trades_list.append(copy.deepcopy(trade))
                pos='deactivated'
                breakout_to_sell=None



                if maxx_possible<trade["Entry"]:
                    trade['maxx_possible']=trade["Entry"]-maxx_possible
                else:trade['maxx_possible']=0
        
            if df['High'][i]>=sl:
                #Exit+Lose(Sold)
                trade["Exit"] = sl
                trade["Exit Date"] = i
                trades_list.append(copy.deepcopy(trade))
                pos='deactivated'
                breakout_to_sell=None

                
                if maxx_possible<trade["Entry"]:
                    trade['maxx_possible']=trade["Entry"]-maxx_possible
                else:trade['maxx_possible']=0
        else:

            maxx_possible=max(maxx_possible,df['High'][i])
            #Exit+Profit(Bought)
            if df['High'][i]>=target:
                trade["Exit"] = target
                trade["Exit Date"] = i
                trades_list.append(copy.deepcopy(trade))
                pos='deactivated'
                breakout_to_buy=None


                if maxx_possible>trade["Entry"]:
                    trade['maxx_possible']=maxx_possible-trade["Entry"]
                else:trade['maxx_possible']=0
            #Exit+Lose(Bought)
            if df['Low'][i]<=sl:
                trade["Exit"] = sl
                trade["Exit Date"] = i
                trades_list.append(copy.deepcopy(trade))
                pos='deactivated'
                breakout_to_buy=None


                if maxx_possible>trade["Entry"]:
                    trade['maxx_possible']=maxx_possible-trade["Entry"]
                else:trade['maxx_possible']=0




df=pd.DataFrame(trades_list)

df["P/L"] = np.where(df["Buy/Sell"] == "Buy", 
                    ((df["Exit"] - df["Entry"])),
                    ((df["Entry"] - df["Exit"])))

df["Return"] = df["P/L"].cumsum()
print(df.tail(20))

print(df['maxx_possible'].mean())