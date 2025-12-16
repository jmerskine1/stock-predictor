import yfinance as yf
import numpy as np
import pandas as pd

def get_stock_universe():
    # For now, a small list; replace with your full universe or API source
    return ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "F", "GE", "IBM"]


def calculate_volatility(ticker, period="1y"):
    data = yf.download(ticker, period=period, progress=False)
    # returns = data['Close'].pct_change().dropna()
    returns = pd.Series(data['Close'].dropna().values.squeeze(-1))
    print(f"{ticker} volatility calculated: {returns.std()}")
    return returns.std()

def select_stocks_by_metric(stock_list, metric_func, top_n=3, ascending=False):
    metrics = {}
    for stock in stock_list:
        val = metric_func(stock)
        print(f"Metric for {stock}: {val} (type: {type(val)})")
        # Check for scalar nan properly
        if isinstance(val, (float, int)):
            if not np.isnan(val):
                metrics[stock] = val
        else:
            print(f"Warning: metric for {stock} is not scalar, skipping.")
    sorted_stocks = sorted(metrics.items(), key=lambda x: x[1], reverse=not ascending)
    selected = [s for s, v in sorted_stocks[:top_n]]
    return selected


def fetch_historical_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if data.empty:
        raise ValueError(f"No data found for {ticker} in date range")
    return data
