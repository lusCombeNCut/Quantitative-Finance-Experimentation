#### Personal Quantative Finance Project

Given I am now applying for oppourtunites in the quant industry I have collated my personal experiments in this reop.

# Trading Strategies

This repository implements multiple trading strategies using Backtrader, leveraging indicators like ConnorsRSI and VWAP. It includes mean reversion, trend following, and breakout strategies.

## Indicators

- **ConnorsRSI**: Combines RSI, streak RSI, and rank period for relative strength.
- **VWAP**: Volume-weighted average price as a benchmark.
- **SMA**: Simple moving average for trend-following.
- **Standard Deviation**: Used in mean reversion for calculating price bands.
- **Highest/Lowest**: Identifies price extremes for breakout strategy.

## Strategies

### 1. Mean Reversion
- **Buy**: When the price is below the lower band and ConnorsRSI is low.
- **Sell**: When the price exceeds the upper band or ConnorsRSI is high, or stop loss/take profit conditions are met.

### 2. Trend Following
- **Buy**: When the price is above the SMA.
- **Sell**: When the price falls below the SMA or meets stop loss/take profit conditions.

### 3. Breakout
- **Buy**: When the price breaks above the highest point in a given period.
- **Sell**: When it falls below the lowest point or meets stop loss/take profit conditions.

### 4. Combined Strategy
- Merges Mean Reversion, Trend Following, and Breakout strategies, executing based on the strongest signal.

## Risk Management
- **Stop Loss**: Exits when the price drops by a specified percentage.
- **Take Profit**: Exits when the price rises by a specified percentage.
