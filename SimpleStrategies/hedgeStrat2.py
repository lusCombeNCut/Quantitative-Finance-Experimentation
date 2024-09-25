import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

# Step 1: Data Collection
tickers = [
    'XOM', 'DAL', 'CVX', 'AAL', 'AMZN', 'M', 'AAPL', 'JCP', 
    'NEE', 'CCL', 'DUK', 'TSLA', 'GOLD', 'JPM', 'NEM', 'BAC',
    'KO', 'PEP', 'PG', 'KHC', 'MO', 'PM', 'CL', 'COST', 'WMT',
    'XEL', 'ED', 'AEE', 'SO', 'DTE', 'DUK', 'NEE', 'EXC', 'EIX',
    'SPG', 'O', 'REG', 'PSA', 'VNO', 'SLG', 'BXP', 'EQR', 'AVB'
]
data = yf.download(tickers, start='2022-01-01', end='2023-01-01')['Adj Close']

# Step 2: Calculate Returns
daily_returns = data.pct_change().dropna()
weekly_returns = data.resample('W').ffill().pct_change().dropna()
monthly_returns = data.resample('M').ffill().pct_change().dropna()

# Step 3: Calculate Moving Averages
moving_avg_20 = data.rolling(window=20).mean()
moving_avg_50 = data.rolling(window=50).mean()

# Step 4: Compute Correlation Matrices
correlation_matrices = {
    'Daily Returns': daily_returns.corr(),
    'Weekly Returns': weekly_returns.corr(),
    'Monthly Returns': monthly_returns.corr(),
    '20-Day Moving Average': moving_avg_20.corr(),
    '50-Day Moving Average': moving_avg_50.corr()
}

# Step 5: Output Correlation Matrices to Terminal
for name, matrix in correlation_matrices.items():
    print(f"\nCorrelation Matrix: {name}")
    print(matrix)

# Step 6: Identify Negatively Correlated Pairs
threshold = -0.8  # Higher threshold for stronger negative correlation
neg_corr_pairs = {}
for name, matrix in correlation_matrices.items():
    neg_corr_pairs[name] = []
    for i in range(len(matrix.columns)):
        for j in range(i):
            if matrix.iloc[i, j] < threshold:
                neg_corr_pairs[name].append((matrix.columns[i], matrix.columns[j]))

# Output the negatively correlated pairs
for name, pairs in neg_corr_pairs.items():
    print(f"\nNegatively Correlated Pairs for {name}:")
    for pair in pairs:
        print(pair)

# Step 7: Adjusted Hedging Strategy with Reasonable Z-score and Risk Management Parameters
def calculate_zscore(spread):
    mean = spread.mean()
    std = spread.std()
    return (spread - mean) / std

def backtest_hedging_strategy(long_ticker, short_ticker, data, z_entry=2.5, z_exit=1.0, stop_loss=-0.4, take_profit=0.4, transaction_cost=0.00):
    # Calculate daily returns
    returns = data[[long_ticker, short_ticker]].pct_change().dropna()
    
    # Calculate the spread
    returns['Spread'] = returns[long_ticker] - returns[short_ticker]
    
    # Calculate the Z-score of the spread
    returns['Z-score'] = calculate_zscore(returns['Spread'])
    
    # Initialize position, signals, and P&L tracking
    position = 0
    signals = []
    pnl = []
    long_entries = []
    short_entries = []
    exits = []
    
    for i in range(len(returns)):
        z = returns['Z-score'].iloc[i]
        if position == 0:
            if z > z_entry:
                # Short both stocks when spread is high (expecting convergence)
                position = -1
                signals.append(position)
                short_entries.append(returns.index[i])
            elif z < -z_entry:
                # Long both stocks when spread is low (expecting divergence)
                position = 1
                signals.append(position)
                long_entries.append(returns.index[i])
            else:
                signals.append(0)
        elif position == 1:
            pnl.append(returns['Spread'].iloc[i])
            if z > -z_exit or sum(pnl) < stop_loss or sum(pnl) > take_profit:
                # Exit long position
                position = 0
                signals.append(position)
                exits.append(returns.index[i])
                pnl = []
            else:
                signals.append(position)
        elif position == -1:
            pnl.append(-returns['Spread'].iloc[i])
            if z < z_exit or sum(pnl) < stop_loss or sum(pnl) > take_profit:
                # Exit short position
                position = 0
                signals.append(position)
                exits.append(returns.index[i])
                pnl = []
            else:
                signals.append(position)
        else:
            signals.append(position)
    
    returns['Position'] = signals
    returns['Strategy'] = returns['Position'].shift(1) * returns['Spread']
    
    # Adjust for transaction costs
    returns['Strategy'] -= transaction_cost * np.abs(returns['Position'].diff()).fillna(0)
    
    # Calculate performance metrics
    strategy_returns = returns['Strategy'].dropna()
    expected_return = strategy_returns.mean()
    std_dev = strategy_returns.std()
    risk_free_rate = 0.01 / 252
    sharpe_ratio = (expected_return - risk_free_rate) / std_dev
    
    # Calculate cumulative strategy returns
    returns['Cumulative Strategy'] = (1 + strategy_returns).cumprod()
    
    # Calculate total return
    total_return = returns['Cumulative Strategy'].iloc[-1] - 1
    
    return expected_return, sharpe_ratio, returns, long_entries, short_entries, exits, total_return

# Step 8: Multiple Positions Management and Combined Strategy
def combined_strategy(data, neg_corr_pairs, initial_cash=1000, max_investment_pct=0.1):
    cash = initial_cash
    portfolio_value = [initial_cash]
    positions = {}
    all_long_entries = {}
    all_short_entries = {}
    all_exits = {}
    total_returns = {}
    
    for name, pairs in neg_corr_pairs.items():
        for long_ticker, short_ticker in pairs:
            print(f"\nBacktesting strategy for {name} - {long_ticker} and {short_ticker}:")
            expected_return, sharpe_ratio, returns, long_entries, short_entries, exits, total_return = backtest_hedging_strategy(long_ticker, short_ticker, data)
            
            print(f"Parameters for {long_ticker} and {short_ticker}: z_entry=3.0, z_exit=1.0, stop_loss=-0.03, take_profit=0.03")
            print(f"Sharpe Ratio: {sharpe_ratio:.6f}")
            print(f"Total Return: {total_return:.6f}")
            
            investment_amount = min(cash * max_investment_pct, initial_cash * max_investment_pct)
            cash -= investment_amount
            positions[(long_ticker, short_ticker)] = investment_amount / returns['Cumulative Strategy'].iloc[-1]
            
            all_long_entries[(long_ticker, short_ticker)] = long_entries
            all_short_entries[(long_ticker, short_ticker)] = short_entries
            all_exits[(long_ticker, short_ticker)] = exits
            total_returns[(long_ticker, short_ticker)] = total_return
    
    # Update the portfolio value for each day
    for i in range(1, len(data)):
        daily_value = cash
        for pair, shares in positions.items():
            long_ticker, short_ticker = pair
            returns = data[[long_ticker, short_ticker]].pct_change().dropna().iloc[:i+1]
            spread = returns[long_ticker] - returns[short_ticker]
            zscore = calculate_zscore(spread)
            position = np.sign(zscore.iloc[-1])
            strategy_returns = position * spread.iloc[-1]
            daily_value += shares * (1 + strategy_returns)
        portfolio_value.append(daily_value)
    
    # Plot combined equity curve
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index[:len(portfolio_value)], y=portfolio_value, mode='lines', name='Combined Equity Curve'))
    fig.update_layout(title='Combined Equity Curve for All Pairs', xaxis_title='Date', yaxis_title='Portfolio Value')
    fig.show()
    
    # Plot entry and exit points for each pair
    for pair, long_entries in all_long_entries.items():
        long_ticker, short_ticker = pair
        short_entries = all_short_entries[pair]
        exits = all_exits[pair]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data[long_ticker], mode='lines', name=f'{long_ticker} Close Price', line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=data.index, y=data[short_ticker], mode='lines', name=f'{short_ticker} Close Price', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=long_entries, y=data.loc[long_entries][long_ticker], mode='markers', marker=dict(symbol='triangle-up', color='green', size=10), name='Long Entry'))
        fig.add_trace(go.Scatter(x=short_entries, y=data.loc[short_entries][short_ticker], mode='markers', marker=dict(symbol='triangle-down', color='red', size=10), name='Short Entry'))
        fig.add_trace(go.Scatter(x=exits, y=data.loc[exits][long_ticker], mode='markers', marker=dict(symbol='x', color='black', size=10), name='Exit'))
        fig.add_trace(go.Scatter(x=exits, y=data.loc[exits][short_ticker], mode='markers', marker=dict(symbol='x', color='black', size=10), name='Exit'))
        fig.update_layout(title=f'Stock History for {long_ticker} and {short_ticker} with Entry and Exit Points', xaxis_title='Date', yaxis_title='Price')
        fig.show()
    
    return total_returns

# Run combined strategy
total_returns = combined_strategy(data, neg_corr_pairs)

# Output the total returns for each pair
print("\nTotal Returns for Each Pair:")
for pair, total_return in total_returns.items():
    long_ticker, short_ticker = pair
    print(f"{long_ticker} and {short_ticker}: {total_return:.6f}")
