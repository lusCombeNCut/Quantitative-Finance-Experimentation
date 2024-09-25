# Install yfinance if not already installed
try:
    import yfinance as yf
except ModuleNotFoundError:
    import os
    os.system('pip install yfinance')
    import yfinance as yf

import pandas as pd

# Step 1: Data Collection
tickers = [
    'XOM', 'DAL', 'CVX', 'AAL', 'AMZN', 'M', 'AAPL', 'JCP', 
    'NEE', 'CCL', 'DUK', 'TSLA', 'GOLD', 'JPM', 'NEM', 'BAC'
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

# Step 5: Output Correlation Matrices
for name, matrix in correlation_matrices.items():
    print(f"\nCorrelation Matrix: {name}")
    print(matrix)
    matrix.to_csv(f'{name.replace(" ", "_").lower()}_correlation_matrix.csv')

# Step 6: Identify Negatively Correlated Pairs
threshold = -0.5
for name, matrix in correlation_matrices.items():
    neg_corr_pairs = []
    for i in range(len(matrix.columns)):
        for j in range(i):
            if matrix.iloc[i, j] < threshold:
                neg_corr_pairs.append((matrix.columns[i], matrix.columns[j]))
    print(f"\nNegatively Correlated Pairs for {name}:")
    for pair in neg_corr_pairs:
        print(pair)
