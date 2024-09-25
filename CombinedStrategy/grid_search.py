# grid_search.py

import itertools
import random
import backtrader as bt
from main import fetch_data
from strategies import CombinedStrategy
from parameters import TICKER, START_DATE, END_DATE
import pandas as pd
import matplotlib.pyplot as plt

# Define the parameter grid without VWAP condition, stop_loss, and take_profit
param_grid = {
    'mean_reversion_period': [10, 20, 30],
    'mean_reversion_dev_factor': [2, 3, 4],
    'crsi_rsi_period': [2, 3, 5],
    'crsi_streak_rsi_period': [2, 3, 5],
    'crsi_rank_period': [50, 100, 200],
    'trend_following_period': [50, 100, 150],
    'breakout_period': [20, 50, 100],
    'crsi_lower_threshold': [10, 20, 30],
    'crsi_upper_threshold': [70, 80, 90]
}

# Select a subset of 20 different combinations
all_combinations = list(itertools.product(*param_grid.values()))
selected_combinations = random.sample(all_combinations, 20)

# Run the grid search
def grid_search(combinations, data):
    best_sharpe = -float('inf')
    best_params = None
    results_list = []
    equity_curves = {}

    for param_comb in combinations:
        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=data, name=TICKER)
        cerebro.adddata(data_feed)
        cerebro.addstrategy(
            CombinedStrategy,
            mean_reversion_period=param_comb[0],
            mean_reversion_dev_factor=param_comb[1],
            crsi_rsi_period=param_comb[2],
            crsi_streak_rsi_period=param_comb[3],
            crsi_rank_period=param_comb[4],
            trend_following_period=param_comb[5],
            breakout_period=param_comb[6],
            stop_loss=0.02,
            take_profit=0.04,
            crsi_lower_threshold=param_comb[7],
            crsi_upper_threshold=param_comb[8],
            vwap_condition=False
        )
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn')

        results = cerebro.run()

        sharpe_ratio = results[0].analyzers.sharpe.get_analysis().get('sharperatio')
        drawdown = results[0].analyzers.drawdown.get_analysis()
        trade_analysis = results[0].analyzers.tradeanalyzer.get_analysis()
        timereturn = results[0].analyzers.timereturn.get_analysis()

        if sharpe_ratio is None:
            sharpe_ratio = float('-inf')

        # Calculate total returns
        initial_value = list(timereturn.values())[0]
        if initial_value == 0:
            total_returns = 0
        else:
            final_value = list(timereturn.values())[-1]
            total_returns = (final_value - initial_value) / initial_value

        metrics = {
            'params': param_comb,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': drawdown['max']['drawdown'],
            'total_trades': trade_analysis.total.closed,
            'winning_trades': trade_analysis.won.total,
            'losing_trades': trade_analysis.lost.total,
            'avg_trade_duration': trade_analysis.len.average,
            'total_returns': total_returns
        }

        results_list.append(metrics)
        equity_curves[param_comb] = timereturn

        if sharpe_ratio > best_sharpe:
            best_sharpe = sharpe_ratio
            best_params = param_comb

        print(f"Tested params: {param_comb}, Sharpe Ratio: {sharpe_ratio}")

    print(f"Best params: {best_params}, Best Sharpe Ratio: {best_sharpe:.2f}")

    # Create a DataFrame to display the results
    results_df = pd.DataFrame(results_list)
    print(results_df)

    # Plot the equity curve for the best parameters
    if best_params:
        plot_equity_curve(equity_curves[best_params])

    return best_params, best_sharpe, results_df

def plot_equity_curve(timereturn):
    plt.figure(figsize=(12, 8))
    plt.plot(timereturn.keys(), timereturn.values(), label='Equity Curve')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.title('Equity Curve')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__':
    best_params, best_sharpe, results_df = grid_search(selected_combinations, data)
    print(f"Best Parameters: {best_params}")
    print(f"Best Sharpe Ratio: {best_sharpe}")

    # Save the results to a CSV file
    results_df.to_csv('grid_search_results.csv', index=False)
