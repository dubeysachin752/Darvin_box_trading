import os 
import pandas as pd
import streamlit as st
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

os.chdir(r'C:\Sachin_Dubey\finance\Darvin Box')


file_path = 'nifty_200.csv'
stocks_df = pd.read_csv(file_path)

# Create a list of stock symbols from the DataFrame
stock_symbols = stocks_df['Symbol'].tolist()


def get_stock_data(stock_ticker):
    try:
        # Fetch stock data
        stock = yf.Ticker(stock_ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            raise ValueError(f"No data found for {stock_ticker}")
        
        # Fetch financial data
        market_cap = stock.info.get('marketCap', 'N/A')  # Market Cap
        
        # Calculate 52-week high and low
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Get the date of the 52-week high and low
        high_52w_date = hist[hist['High'] == high_52w].index[0].strftime('%Y-%m-%d')
        low_52w_date = hist[hist['Low'] == low_52w].index[0].strftime('%Y-%m-%d')
        
        # Get the current market price (CMP)
        cmp = stock.history(period="1d")['Close'][0]
        
        return {
            "Stock Ticker": stock_ticker,
            'Market Cap': market_cap,
            "CMP": cmp,
            "52 Week High": high_52w,
            "52 Week High Date": high_52w_date,
            "52 Week Low": low_52w,
            "52 Week Low Date": low_52w_date
        }
    
    except Exception as e:
        # If data is not found, return N/A for all fields
        print(f"Error fetching data for {stock_ticker}: {e}")
        return {
            "Stock Ticker": stock_ticker,
            'Market Cap': 'N/A',
            "CMP": 'N/A',
            "52 Week High": 'N/A',
            "52 Week High Date": 'N/A',
            "52 Week Low": 'N/A',
            "52 Week Low Date": 'N/A'
        }

# List of NSE stocks
nse_stocks = stock_symbols

# Fetch data for each stock and store in a list
stock_data_list = [get_stock_data(stock_ticker) for stock_ticker in nse_stocks]

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(stock_data_list)
df['flag']=np.where(df['52 Week High Date']<df['52 Week Low Date'], "Suitable for Darvas Box Strategy","Avoid")

df_final= df[df['flag']=="Suitable for Darvas Box Strategy"]
df1_sort=df_final.sort_values(by=['Market Cap'],ascending=False).head(100)
res=df1_sort[['Stock Ticker','CMP']]

# Function to calculate start and end dates of the previous week
def get_previous_week_dates():
    today = datetime.now()
    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - timedelta(weeks=1)
    end_of_last_week = start_of_this_week - timedelta(days=1)
    return start_of_last_week, end_of_last_week

start_date, end_date = get_previous_week_dates()
last_week_df = []
stock_symbols= res['Stock Ticker'].tolist()

for symbol in stock_symbols:
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    
    if not data.empty:
        max_high = data['High'].max()
        last_week_df.append({ 'Stock': symbol,'GTT_price': max_high})
    else:
        last_week_df.append({'Stock': symbol,'GTT_price': 'N/A'})

max_high_df = pd.DataFrame(last_week_df)

final=pd.merge(res,max_high_df,left_on='Stock Ticker',right_on='Stock',how='left')
result =final[['Stock Ticker','CMP','GTT_price']].sort_values(by=['CMP'],ascending=False)

# Streamlit app
st.title('Stock Information')

st.write("Nifty top 200 stocks:")
st.table(result)


###python -m streamlit run darvin_box.py
