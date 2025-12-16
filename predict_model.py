import numpy as np

def simple_predict_next_price(prices, window=5):
    if len(prices) < window:
        window = len(prices)
    sma = np.mean(prices[-window:])
    std = np.std(prices[-window:])
    lower = sma - 1.96 * std
    upper = sma + 1.96 * std
    return sma, (lower, upper)
