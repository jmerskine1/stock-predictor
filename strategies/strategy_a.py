NAME = "buy increase, sell decrease"

def run(prices):
    # Simple strategy: buy if price increased, sell if decreased
    signals = []
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            signals.append("buy")
        else:
            signals.append("sell")
    return signals
