import matplotlib.pyplot as plt
import os
import datetime

def plot_pnl_with_dates(pnl, dates, strategy_name, ticker, prediction=None, conf_int=None):
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join("results", f"{ticker}_{strategy_name}_{timestamp}.png")

    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(dates[1:], pnl, label="P&L")
    ax.set_title(f"P&L Over Time - {strategy_name} on {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("P&L ($)")
    plt.xticks(rotation=45)
    plt.grid(True)

    if prediction and conf_int:
        textstr = f"Predicted next price: {prediction:.2f}\n95% CI: [{conf_int[0]:.2f}, {conf_int[1]:.2f}]"
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    print(f"Saved plot to {filepath}")
