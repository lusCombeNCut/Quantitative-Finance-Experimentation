# Install required libraries if not already installed
try:
    import yfinance as yf
    import matplotlib.pyplot as plt
    from ta.momentum import RSIIndicator
    from ta.volatility import BollingerBands
    from ta.trend import MACD
except ModuleNotFoundError:
    import os
    os.system('pip install yfinance matplotlib ta')
    import yfinance as yf
    import matplotlib.pyplot as plt
    from ta.momentum import RSIIndicator
    from ta.volatility import BollingerBands
    from ta.trend import MACD

import pandas as pd
import numpy as np

# Connors RSI calculation
def connors_rsi(df, window_rsi=3, window_streak=2, window_rank=200):
    # Short-term RSI
    rsi = RSIIndicator(df['Close'], window=window_rsi).rsi()
    
    # Up/Down Streak
    df['Up_Down'] = np.where(df['Close'] > df['Close'].shift(1), 1, -1)
    df['Streak'] = df['Up_Down'].groupby((df['Up_Down'] != df['Up_Down'].shift()).cumsum()).cumsum()
    streak_rsi = RSIIndicator(df['Streak'], window=window_streak).rsi()
    
    # Percent Rank
    rank = 100 * df['Close'].rolling(window=window_rank).apply(lambda x: pd.Series(x).rank().iloc[-1] / window_rank)
    
    # Connors RSI
    connors_rsi = (rsi + streak_rsi + rank) / 3
    return connors_rsi

# Mean Reversion Strategy with Connors RSI and Bollinger Bands
def mean_reversion_strategy_with_connors_rsi_and_bb(df, initial_cash=1000, z_entry=35, z_exit=70, transaction_cost=0.001):
    df['Connors_RSI'] = connors_rsi(df)
    bb = BollingerBands(df['Close'])
    df['BB_Upper'] = bb.bollinger_hband()
    df['BB_Lower'] = bb.bollinger_lband()
    
    df['Position'] = 0
    cash = initial_cash
    shares = 0
    portfolio_value = [initial_cash]  # Initialize with initial cash value
    buy_dates = []
    sell_dates = []
    
    for i in range(1, len(df)):
        # Check if the stock has been in a downturn for at least 3 days and no more than 9 days
        downturn_days = 0
        for j in range(1, 10):
            if i - j < 0:
                break
            if df['Close'].iloc[i-j] < df['Close'].iloc[i-j-1]:
                downturn_days += 1
            else:
                break
        
        if df['Connors_RSI'].iloc[i-1] < z_entry and df['Close'].iloc[i-1] < df['BB_Lower'].iloc[i-1] and cash > 0 and 3 <= downturn_days <= 9:
            # Buy signal
            shares_bought = cash // df['Close'].iloc[i]
            cash -= shares_bought * df['Close'].iloc[i] * (1 + transaction_cost)
            shares += shares_bought
            buy_dates.append(df.index[i])
        elif df['Connors_RSI'].iloc[i-1] > z_exit and shares > 0:
            # Sell signal
            cash += shares * df['Close'].iloc[i] * (1 - transaction_cost)
            shares = 0
            sell_dates.append(df.index[i])
        
        portfolio_value.append(cash + shares * df['Close'].iloc[i])
    
    df['Portfolio Value'] = portfolio_value
    return df, buy_dates, sell_dates

# Performance Metrics Calculation
def calculate_performance_metrics(df):
    total_return = df['Portfolio Value'].iloc[-1] / df['Portfolio Value'].iloc[0] - 1
    annualized_return = (1 + total_return) ** (252 / len(df)) - 1
    daily_returns = df['Portfolio Value'].pct_change().dropna()
    annualized_volatility = daily_returns.std() * np.sqrt(252)
    sharpe_ratio = (annualized_return - 0.01) / annualized_volatility  # Assuming a risk-free rate of 1%
    max_drawdown = (df['Portfolio Value'] / df['Portfolio Value'].cummax() - 1).min()
    
    return {
        'Total Return': total_return,
        'Annualized Return': annualized_return,
        'Annualized Volatility': annualized_volatility,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown': max_drawdown
    }

# Step 1: Data Collection
tickers = ['TWST', 'CMPS', 'SIGA', 'ATAI', 'OPGN', 'MBRX', 'LCTX', 'AEMD', 'CKPT', 'WINT']# 'BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'BCH-USD']  # Small-cap biotech stocks and popular cryptocurrencies
data = yf.download(tickers, start='2016-01-01', end='2024-01-01')['Adj Close']

# Step 2: Apply Strategy to Each Ticker
results = {}
for ticker in tickers:
    print(f"\nBacktesting Mean Reversion Strategy for {ticker}:")
    df = data[[ticker]].copy()
    df.columns = ['Close']
    df, buy_dates, sell_dates = mean_reversion_strategy_with_connors_rsi_and_bb(df)
    
    # Calculate performance metrics
    metrics = calculate_performance_metrics(df)
    print(f"Performance Metrics for {ticker}:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # Plot equity curve
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Portfolio Value'], label='Equity Curve')
    plt.title(f'Equity Curve for {ticker} (Mean Reversion Strategy with Connors RSI and Bollinger Bands)')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid()
    plt.show()
    
    # Plot stock history with buy and sell points
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Close'], label='Close Price')
    plt.scatter(buy_dates, df.loc[buy_dates]['Close'], marker='^', color='g', label='Buy', alpha=1)
    plt.scatter(sell_dates, df.loc[sell_dates]['Close'], marker='v', color='r', label='Sell', alpha=1)
    plt.title(f'Stock History for {ticker} with Buy and Sell Points')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()
    
    results[ticker] = df

# Note: This script assumes you have matplotlib, yfinance, and ta installed. If not, install them using:
# pip install matplotlib yfinance ta
