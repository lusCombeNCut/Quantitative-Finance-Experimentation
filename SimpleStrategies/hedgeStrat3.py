import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def rsi(series, period=14):
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def connors_rsi(df, period_rsi=3, period_streak=2, period_rank=100):
    rsi_close = rsi(df['Close'], period_rsi)
    
    streak = np.zeros(len(df['Close']))
    for i in range(1, len(df['Close'])):
        if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
            streak[i] = streak[i - 1] + 1 if streak[i - 1] > 0 else 1
        elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
            streak[i] = streak[i - 1] - 1 if streak[i - 1] < 0 else -1
        else:
            streak[i] = 0
    
    rsi_streak = rsi(pd.Series(streak), period_streak)
    
    def rank_within_window(x):
        return pd.Series(x).rank(pct=True).iloc[-1] * 100 if len(x.dropna()) > 1 else np.nan
    
    daily_changes = df['Close'].diff(1)
    rank = daily_changes.rolling(window=period_rank, min_periods=1).apply(rank_within_window, raw=False).fillna(0)
    
    return (rsi_close + rsi_streak + rank) / 3

def bollinger_bands(df, window=20, num_std_dev=2):
    rolling_mean = df['Close'].rolling(window).mean()
    rolling_std = df['Close'].rolling(window).std()
    df['Bollinger Upper'] = rolling_mean + (rolling_std * num_std_dev)
    df['Bollinger Lower'] = rolling_mean - (rolling_std * num_std_dev)

# List of 10 small-cap biotech stocks (hypothetical tickers)
tickers = ['AXSM', 'ADAP', 'ADMA', 'ADVM', 'AGTC', 'AKBA', 'ALDX', 'ALNA', 'ALRN', 'ALXO']

# Download stock data
data = {}
for ticker in tickers:
    try:
        df = yf.download(ticker, start='2020-01-01', end='2023-01-01')
        if not df.empty:
            data[ticker] = df
        else:
            print(f"No data for {ticker}")
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")

# Calculate indicators for each stock
for ticker, df in data.items():
    df['RSI'] = rsi(df['Close'])
    df['ConnorsRSI'] = connors_rsi(df)
    bollinger_bands(df)
    df['Buy Signal'] = ((df['Close'] < df['Bollinger Lower']) & (df['RSI'] < 30) & (df['ConnorsRSI'] < 20)).astype(int)

# Align data by date
aligned_data = pd.concat([df[['Close', 'Buy Signal']] for df in data.values()], axis=1, keys=data.keys())
aligned_data.columns = aligned_data.columns.map('_'.join)
aligned_data = aligned_data.dropna()

# Define take profit and stop loss percentages
take_profit_pct = 0.1  # 10% take profit
stop_loss_pct = 0.05   # 5% stop loss

# Backtesting
initial_cash = 10000
cash = initial_cash
positions = {ticker: 0 for ticker in data.keys()}
entry_prices = {ticker: 0 for ticker in data.keys()}
portfolio_value = []

for date, row in aligned_data.iterrows():
    total_value = cash + sum(positions[ticker] * row[f'{ticker}_Close'] for ticker in data.keys())
    
    for ticker in data.keys():
        if row[f'{ticker}_Buy Signal'] == 1 and cash > 0:
            max_position_value = 0.1 * total_value
            amount_to_invest = min(cash, max_position_value)
            positions[ticker] += amount_to_invest / row[f'{ticker}_Close']
            entry_prices[ticker] = row[f'{ticker}_Close']
            cash -= amount_to_invest
        
        # Implement take profit and stop loss
        elif positions[ticker] > 0:
            current_price = row[f'{ticker}_Close']
            if current_price >= entry_prices[ticker] * (1 + take_profit_pct) or current_price <= entry_prices[ticker] * (1 - stop_loss_pct):
                cash += positions[ticker] * current_price
                positions[ticker] = 0
    
    portfolio_value.append(total_value)

aligned_data['Portfolio Value'] = portfolio_value

# Plot results
plt.figure(figsize=(14, 7))
for ticker in data.keys():
    plt.plot(aligned_data.index, aligned_data[f'{ticker}_Close'], label=ticker)
plt.legend()
plt.title('Stock Prices')
plt.show()

plt.figure(figsize=(14, 7))
plt.plot(aligned_data.index, aligned_data['Portfolio Value'], label='Portfolio Value')
plt.legend()
plt.title('Portfolio Value Over Time')
plt.show()
