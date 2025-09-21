## Personal Quantitative Finance Project

These strategies focus on financial indicators, which are unlikely to provide considerable alpha on their own. However, this project allowed me to practice back testing multiple strategies with different risk profiles and methodologies. 

More recently I have completed a project that demonstrated a time delayed correlation with twitter sentiment and Bitcoin price, potentially offering a valuable trading signal. This project can be accessed here [ADS-US_Election](https://github.com/lusCombeNCut/ADS-US-Election). In the future I will look to explore more diverse data sources such as weather or satellite imagery for commodities trading.

### Trading Strategies

This repository implements a set of systematic trading strategies using **Backtrader**, designed to test distinct sources of return premia. The strategies primarily exploit statistical relationships in price and volume data, with implementations of **mean reversion**, **trend-following**, and **breakout-style** models, alongside a correlation-based relative value strategy. Each strategy incorporates explicit entry/exit rules, stop-loss/take-profit constraints, and can be evaluated under varying leverage and transaction cost assumptions.  

#### Indicators and Features

- **ConnorsRSI**: A composite oscillator combining standard RSI, streak length of price changes, and percentile rank of returns. Applied to capture short-term overbought/oversold conditions.  
- **VWAP (Volume-Weighted Average Price)**: Serves as an intraday benchmark and liquidity proxy, used to assess relative execution efficiency and potential reversion signals.  
- **SMA (Simple Moving Average)**: Captures medium- to long-term trend direction, forming the basis for cross-sectional momentum signals.  
- **Rolling Standard Deviation**: Used to estimate volatility bands for mean reversion strategies, effectively implementing a dynamic Bollinger-style framework.  
- **Rolling Highs/Lows**: Identify breakout thresholds by detecting regime shifts in local extrema over a predefined lookback horizon.  

#### Strategy Implementations  

##### 1. **Mean Reversion**  
- **Entry Condition**: Long exposure initiated when the asset trades below a volatility-adjusted lower band and ConnorsRSI indicates extreme oversold conditions.  
- **Exit Condition**: Position closed when price reverts toward the upper band, ConnorsRSI enters overbought territory, or risk management triggers (stop-loss/take-profit) are hit.  

##### 2. **Trend Following**  
- **Entry Condition**: Long exposure initiated when price closes above a defined SMA threshold, signalling persistent momentum.  
- **Exit Condition**: Position unwound when price crosses back below the SMA or hits predefined stop-loss/take-profit levels.  
- This strategy is designed to capture medium-horizon momentum consistent with empirical evidence of trend persistence in asset returns.  

##### 3. **Breakout Strategy**  
- **Entry Condition**: Long exposure initiated when price breaches the trailing maximum over a specified lookback period, signalling a potential structural regime shift.  
- **Exit Condition**: Position closed if price declines below the trailing minimum or risk constraints are breached.  
- This strategy attempts to exploit volatility expansions following periods of consolidation.  

##### 4. **Relative Value / Negative Correlation Strategy**  
- Pairs of assets are selected based on empirically observed negative correlation in returns.  
- **Entry Condition**: When asset A demonstrates upward momentum, initiate a short position in asset B, and vice versa.  
- **Exit Condition**: Positions are closed when correlation relationships break down or stop-loss thresholds are hit.  
- This strategy approximates a form of statistical arbitrage, exploiting mean-reverting relative value mispricings across correlated instruments.  

