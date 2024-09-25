# main.py

import yfinance as yf
import backtrader as bt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from parameters import *
from strategies import CombinedStrategy

# Fetch historical stock data for a single stock
def fetch_data(ticker, start, end):
    stock_data = yf.download(ticker, start=start, end=end)
    stock_data['Open Interest'] = 0  # Backtrader requires this column
    return stock_data

# Performance metrics calculation
def calculate_performance_metrics(strategy):
    start_value = strategy.broker.startingcash
    end_value = strategy.broker.getvalue()
    pnl = end_value - start_value
    returns = pnl / start_value

    # Handle negative returns correctly for annualized return calculation
    if returns >= -1:
        annualized_return = (1 + returns) ** (1 / 10) - 1
    else:
        annualized_return = float('nan')  # If returns are less than -100%, annualized return is not defined

    sharpe_ratio = strategy.analyzers.sharpe.get_analysis().get('sharperatio')
    max_drawdown = strategy.analyzers.drawdown.get_analysis()['max']['drawdown']
    
    print(f"Final Portfolio Value: ${end_value:.2f}")
    print(f"Cumulative Returns: {returns:.2%}")
    if not np.isnan(annualized_return):
        print(f"Annualized Returns: {annualized_return:.2%}")
    else:
        print("Annualized Returns: NaN")
    if sharpe_ratio is not None:
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    else:
        print("Sharpe Ratio: None")
    print(f"Max Drawdown: {max_drawdown:.2%}")

# Main script execution
if __name__ == '__main__':
    # Fetch data
    data = fetch_data(TICKER, start=START_DATE, end=END_DATE)

    # Backtesting with combined strategy
    cerebro = bt.Cerebro()
    start_value = cerebro.broker.getvalue()
    data_feed = bt.feeds.PandasData(dataname=data, name=TICKER)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(CombinedStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    results = cerebro.run()

    # Calculate and display performance metrics
    strategy = results[0]
    calculate_performance_metrics(strategy)

    # Plot results
    cerebro.plot()
