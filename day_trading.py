import yfinance as yf
import alpaca_trade_api as tradeapi
import json
import os
from datetime import datetime
import time
import numpy as np

# -------- Alpaca paper trading setup --------
# Alpaca credentials

API_KEY = str(input("Enter your Alpaca API Key: "))
API_SECRET = str(input("Enter your Alpaca API Secret: "))
BASE_URL = str(input("Enter Alpaca base url: ")) #https://paper-api.alpaca.markets"
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# -------- Settings --------
SYMBOLS = ['AAPL', 'TSLA', 'MSFT']  # Replace with your list
CONFIDENCE_THRESHOLD = 0.65
TRADE_LOG_FILE = "trade_log.json"
MA_SHORT = 5
MA_LONG = 10

# -------- Helper functions --------

def fetch_price_data(symbol, period="20d", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    return df

def compute_confidence(df):
    # Simple momentum-based confidence: 1 if MA5 > MA10 else 0
    df['MA5'] = df['Close'].rolling(MA_SHORT).mean()
    df['MA10'] = df['Close'].rolling(MA_LONG).mean()
    if df['MA5'].iloc[-1] > df['MA10'].iloc[-1]:
        return 0.7  # confident uptrend
    else:
        return 0.3  # less confident

def load_trade_log():
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, 'r') as f:
            return json.load(f)
    else:
        return []

def save_trade_log(trades):
    with open(TRADE_LOG_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

def find_open_trade(trades, symbol):
    for t in trades:
        if t['symbol'] == symbol and t['status'] == 'open':
            return t
    return None

def place_buy_order(symbol, qty):
    print(f"Placing buy order: {symbol} qty {qty}")
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(f"Buy order submitted for {symbol}")
        return order
    except Exception as e:
        print(f"Error placing buy order for {symbol}: {e}")
        return None

def place_sell_order(symbol, qty):
    print(f"Placing sell order: {symbol} qty {qty}")
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        print(f"Sell order submitted for {symbol}")
        return order
    except Exception as e:
        print(f"Error placing sell order for {symbol}: {e}")
        return None


def determine_qty(symbol):
    # Buy as many shares as possible with $100 or up to cash available
    account = api.get_account()
    cash = float(account.cash)
    portfolio_value = float(account.portfolio_value)
    max_per_share = portfolio_value * 0.05  # 5% of portfolio
    max_cash = min(cash, max_per_share)     # whichever is less

    price = yf.Ticker(symbol).info.get('regularMarketPrice', None)
    if price is None:
        print(f"Could not get price for {symbol}")
        return 0
    
    if max_cash < price:
        print(f"Not enough cash (${max_cash:.2f}) to buy 1 share of {symbol} at ${price:.2f}")
        return 0
    
    qty = int(np.floor(max_cash / price))
    return qty

# -------- Main daily check --------

def daily_check():
    trades = load_trade_log()

    for symbol in SYMBOLS:
        print(f"Checking {symbol}...")
        df = fetch_price_data(symbol)
        if df.empty or len(df) < MA_LONG:
            print(f"Not enough data for {symbol}")
            continue

        confidence = compute_confidence(df)
        print(f"Confidence for {symbol}: {confidence:.2f}")

        open_trade = find_open_trade(trades, symbol)

        if confidence >= CONFIDENCE_THRESHOLD and not open_trade:
            qty = determine_qty(symbol)
            if qty == 0:
                print(f"Not enough cash to buy {symbol}")
                continue
            order = place_buy_order(symbol, qty)
            if order:
                trades.append({
                    "symbol": symbol,
                    "qty": qty,
                    "buy_time": datetime.now().isoformat(),
                    "status": "open"
                })
                save_trade_log(trades)

        elif confidence < CONFIDENCE_THRESHOLD and open_trade:
            order = place_sell_order(symbol, open_trade['qty'])
            if order:
                open_trade['status'] = 'closed'
                open_trade['sell_time'] = datetime.now().isoformat()
                save_trade_log(trades)

    print("Daily check complete.")

if __name__ == "__main__":
    daily_check()
