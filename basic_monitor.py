import yfinance as yf
from alpaca_trade_api.rest import REST
import pandas as pd

# Alpaca credentials
API_KEY = "PKW4LLSXOPYNFAA07JXV"
API_SECRET = "NnyuphuEdY0HOzW2W0dNImpNfJz85IjoQYBcULpX"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)

# Parameters
symbol = "AAPL"
cash_threshold = 100
ma_window = 10

def fetch_price_data(symbol):
    df = yf.download(symbol, period="20d", interval="1d")
    
    if df.empty or 'Close' not in df.columns:
        print("❌ Data fetch failed or missing 'Close' column")
        return pd.DataFrame()
    
    df['MA', symbol] = df['Close'].rolling(window=ma_window).mean().shift(1)
    
    if 'MA' not in df.columns:
        print("❌ MA column creation failed")
    
    return df

def should_buy(df):
    
    if 'MA' not in df.columns:
        print("❌ MA column not present")
        return False
    
    df = df.dropna(subset=[('MA',symbol)])

    if df.empty:
        print("❌ Not enough data after dropping NaNs")
        return False

    latest = df.iloc[-1]
    print(f"✅ Close: {latest[('Close',symbol)]:.2f}, MA: {latest[('MA',symbol)]:.2f}")
    return latest[('Close',symbol)] > latest[('MA',symbol)]

def make_trade(symbol, qty):
    try:
        account = api.get_account()
        print('check1')
        cash = float(account.cash)
        price = yf.Ticker(symbol).info.get('regularMarketPrice', 0)

        if price == 0:
            print("❌ Failed to fetch price from yfinance")
            return

        if cash >= qty * price:
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            print(f"✅ Bought {qty} shares of {symbol} at ~${price:.2f}")
        else:
            print(f"❌ Not enough cash. Available: ${cash:.2f}, Needed: ${qty * price:.2f}")
    except Exception as e:
        print(f"❌ Trade failed: {e}")

def run():
    df = fetch_price_data(symbol)
    if not df.empty and should_buy(df):
        make_trade(symbol, 1)

if __name__ == "__main__":
    run()
