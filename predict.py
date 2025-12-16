import datetime
from data_fetch import get_stock_universe, calculate_volatility, select_stocks_by_metric, fetch_historical_data
from backtest import backtest_strategy
from predict_model import simple_predict_next_price
from visualize import plot_pnl_with_dates

import strategies.strategy_a as strategy_a
import strategies.strategy_b as strategy_b

STRATEGIES = [strategy_a, strategy_b]

def main():
    # Parameters
    n_stocks = 3
    lookback_period = "1y"
    backtest_start = "2022-01-01"
    backtest_end = "2023-01-01"

    universe = get_stock_universe()
    print("Calculating volatility and selecting stocks...")
    selected_stocks = select_stocks_by_metric(universe, lambda t: calculate_volatility(t, period=lookback_period), n_stocks)
    print(f"Selected stocks: {selected_stocks}")

    for ticker in selected_stocks:
        print(f"\nFetching data for {ticker} from {backtest_start} to {backtest_end}...")
        data = fetch_historical_data(ticker, backtest_start, backtest_end)
        prices = list(data['Close'].to_numpy().squeeze(-1))
        dates = list(data.index)

        for strat in STRATEGIES:
            print(f"Backtesting strategy {strat.NAME} on {ticker}...")
            pnl, strategy_name = backtest_strategy(strat, prices)

            pred, conf_int = simple_predict_next_price(prices)

            plot_pnl_with_dates(pnl, dates, strategy_name, ticker, pred, conf_int)

            final_pnl = pnl[-1] if pnl else 0
            total_trades = sum(1 for s in strat.run(prices) if s in ["buy", "sell"])

            print(f"Results for {ticker} - {strategy_name}: Final P&L={final_pnl:.2f}, Trades={total_trades}, Prediction={pred:.2f}, 95% CI=({conf_int[0]:.2f}, {conf_int[1]:.2f})")

if __name__ == "__main__":
    main()
