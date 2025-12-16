NAME = "buy even days, sell odd days"


def run(prices):
    # Another simple strategy: buy on even days, sell on odd days
    signals = ["buy" if i % 2 == 0 else "sell" for i in range(len(prices))]
    return signals
