import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd

def backtest_strategy(strategy_module, prices):
    strategy_name = getattr(strategy_module, "NAME", "Unnamed Strategy")

    signals = strategy_module.run(prices)

    balance = 0
    position = 0
    pnl = []

    for i in range(1, len(prices)):
        if signals[i - 1] == "buy":
            position += 1
            balance -= prices[i]
        elif signals[i - 1] == "sell" and position > 0:
            position -= 1
            balance += prices[i]

        current_pnl = balance + position * prices[i]
        pnl.append(current_pnl)

    return pnl, strategy_name
