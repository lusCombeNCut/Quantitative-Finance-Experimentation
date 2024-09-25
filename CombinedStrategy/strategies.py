# strategies.py

import backtrader as bt
from indicators import ConnorsRSI, VWAP
from parameters import *

# Mean Reversion Strategy class for Backtrader with Connors RSI and VWAP
class MeanReversionStrategy(bt.Strategy):
    params = (
        ('period', MEAN_REVERSION_PERIOD),
        ('dev_factor', MEAN_REVERSION_DEV_FACTOR),
        ('crsi_rsi_period', CRSI_RSI_PERIOD),
        ('crsi_streak_rsi_period', CRSI_STREAK_RSI_PERIOD),
        ('crsi_rank_period', CRSI_RANK_PERIOD),
        ('stop_loss', STOP_LOSS),
        ('take_profit', TAKE_PROFIT),
        ('crsi_lower_threshold', CRSI_LOWER_THRESHOLD),
        ('crsi_upper_threshold', CRSI_UPPER_THRESHOLD),
        ('vwap_condition', VWAP_CONDITION),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.period)
        self.stddev = bt.indicators.StandardDeviation(self.data, period=self.params.period)
        self.upper_band = self.sma + self.stddev * self.params.dev_factor
        self.lower_band = self.sma - self.stddev * self.params.dev_factor
        self.crsi = ConnorsRSI(self.data, 
                               rsi_period=self.params.crsi_rsi_period, 
                               streak_rsi_period=self.params.crsi_streak_rsi_period, 
                               rank_period=self.params.crsi_rank_period)
        self.vwap = VWAP(self.data)
        self.buy_price = None

    def next(self):
        if not self.position:
            if (self.data.close < self.lower_band and 
                self.crsi.crsi < self.params.crsi_lower_threshold and 
                (not self.params.vwap_condition or self.data.close < self.vwap)):
                self.buy()
                self.buy_price = self.data.close[0]
                self.log(f'BUY executed, Price: {self.data.close[0]}, Strategy: Mean Reversion')
        elif self.position:
            if self.buy_price and (
                self.data.close > self.upper_band or 
                self.crsi.crsi > self.params.crsi_upper_threshold or 
                (self.params.vwap_condition and self.data.close > self.vwap)):
                self.sell()
                self.buy_price = None
                self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Mean Reversion')
            elif self.buy_price and (
                self.data.close <= self.buy_price * (1 - self.params.stop_loss) or 
                self.data.close >= self.buy_price * (1 + self.params.take_profit)):
                self.sell()
                self.buy_price = None
                self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Mean Reversion (Stop Loss/Take Profit)')

    def log(self, text):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {text}')

# Trend Following Strategy class for Backtrader
class TrendFollowingStrategy(bt.Strategy):
    params = (
        ('period', TREND_FOLLOWING_PERIOD),
        ('stop_loss', STOP_LOSS),
        ('take_profit', TAKE_PROFIT),
        ('vwap_condition', VWAP_CONDITION),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.period)
        self.vwap = VWAP(self.data)
        self.buy_price = None

    def next(self):
        if not self.position:
            if self.data.close > self.sma and (not self.params.vwap_condition or self.data.close > self.vwap):
                self.buy()
                self.buy_price = self.data.close[0]
                self.log(f'BUY executed, Price: {self.data.close[0]}, Strategy: Trend Following')
        elif self.position:
            if self.buy_price and (self.data.close < self.sma or (self.params.vwap_condition and self.data.close < self.vwap)):
                self.sell()
                self.buy_price = None
                self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Trend Following')
            elif self.buy_price and (
                self.data.close <= self.buy_price * (1 - self.params.stop_loss) or 
                self.data.close >= self.buy_price * (1 + self.params.take_profit)):
                self.sell()
                self.buy_price = None
                self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Trend Following (Stop Loss/Take Profit)')

    def log(self, text):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {text}')

# Breakout Strategy class for Backtrader
class BreakoutStrategy(bt.Strategy):
    params = (
        ('period', BREAKOUT_PERIOD),
        ('stop_loss', STOP_LOSS),
        ('take_profit', TAKE_PROFIT),
        ('vwap_condition', VWAP_CONDITION),
    )

    def __init__(self):
        self.highest = bt.indicators.Highest(self.data.high, period=self.params.period)
        self.lowest = bt.indicators.Lowest(self.data.low, period=self.params.period)
        self.vwap = VWAP(self.data)
        self.buy_price = None

    def next(self):
        if not self.position:
            if self.data.close > self.highest[-1] and (not self.params.vwap_condition or self.data.close > self.vwap):
                self.buy()
                self.buy_price = self.data.close[0]
                self.log(f'BUY executed, Price: {self.data.close[0]}, Strategy: Breakout')
        elif self.position:
            if self.buy_price and (self.data.close < self.lowest[-1] or (self.params.vwap_condition and self.data.close < self.vwap)):
                self.sell()
                self.buy_price = None
                self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Breakout')
            elif self.buy_price and (
                self.data.close <= self.buy_price * (1 - self.params.stop_loss) or 
                self.data.close >= self.buy_price * (1 + self.params.take_profit)):
                self.sell()
                self.buy_price = None
                self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Breakout (Stop Loss/Take Profit)')

    def log(self, text):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {text}')

# Combined Strategy class for Backtrader
class CombinedStrategy(bt.Strategy):
    params = (
        ('mean_reversion_period', MEAN_REVERSION_PERIOD),
        ('mean_reversion_dev_factor', MEAN_REVERSION_DEV_FACTOR),
        ('crsi_rsi_period', CRSI_RSI_PERIOD),
        ('crsi_streak_rsi_period', CRSI_STREAK_RSI_PERIOD),
        ('crsi_rank_period', CRSI_RANK_PERIOD),
        ('trend_following_period', TREND_FOLLOWING_PERIOD),
        ('breakout_period', BREAKOUT_PERIOD),
        ('stop_loss', STOP_LOSS),
        ('take_profit', TAKE_PROFIT),
        ('crsi_lower_threshold', CRSI_LOWER_THRESHOLD),
        ('crsi_upper_threshold', CRSI_UPPER_THRESHOLD),
        ('vwap_condition', VWAP_CONDITION),
    )

    def __init__(self):
        # Mean Reversion Strategy
        self.sma_mr = bt.indicators.SimpleMovingAverage(self.data, period=self.params.mean_reversion_period)
        self.stddev_mr = bt.indicators.StandardDeviation(self.data, period=self.params.mean_reversion_period)
        self.upper_band_mr = self.sma_mr + self.stddev_mr * self.params.mean_reversion_dev_factor
        self.lower_band_mr = self.sma_mr - self.stddev_mr * self.params.mean_reversion_dev_factor
        self.crsi = ConnorsRSI(self.data, 
                               rsi_period=self.params.crsi_rsi_period, 
                               streak_rsi_period=self.params.crsi_streak_rsi_period, 
                               rank_period=self.params.crsi_rank_period)
        self.vwap = VWAP(self.data)

        # Trend Following Strategy
        self.sma_tf = bt.indicators.SimpleMovingAverage(self.data, period=self.params.trend_following_period)

        # Breakout Strategy
        self.highest_bo = bt.indicators.Highest(self.data.high, period=self.params.breakout_period)
        self.lowest_bo = bt.indicators.Lowest(self.data.low, period=self.params.breakout_period)

        self.buy_price = None

    def next(self):
        if not self.position:
            # Check for Mean Reversion
            if (self.data.close < self.lower_band_mr and 
                self.crsi.crsi < self.params.crsi_lower_threshold and 
                (not self.params.vwap_condition or self.data.close < self.vwap)):
                self.buy()
                self.buy_price = self.data.close[0]
                self.log(f'BUY executed, Price: {self.data.close[0]}, Strategy: Mean Reversion')
            elif self.data.close > self.upper_band_mr or self.crsi.crsi > self.params.crsi_upper_threshold or (self.params.vwap_condition and self.data.close > self.vwap):
                if self.position:
                    self.sell()
                    self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Mean Reversion')
            # Check for Trend Following
            elif self.data.close > self.sma_tf and (not self.params.vwap_condition or self.data.close > self.vwap):
                self.buy()
                self.buy_price = self.data.close[0]
                self.log(f'BUY executed, Price: {self.data.close[0]}, Strategy: Trend Following')
            elif self.data.close < self.sma_tf or (self.params.vwap_condition and self.data.close < self.vwap):
                if self.position:
                    self.sell()
                    self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Trend Following')
            # Check for Breakout
            elif self.data.close > self.highest_bo[-1] and (not self.params.vwap_condition or self.data.close > self.vwap):
                self.buy()
                self.buy_price = self.data.close[0]
                self.log(f'BUY executed, Price: {self.data.close[0]}, Strategy: Breakout')
            elif self.data.close < self.lowest_bo[-1] or (self.params.vwap_condition and self.data.close < self.vwap):
                if self.position:
                    self.sell()
                    self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Breakout')
        elif self.position:
            # Managing positions once in a trade based on highest priority strategy
            if self.buy_price and (
                self.data.close <= self.buy_price * (1 - self.params.stop_loss) or 
                self.data.close >= self.buy_price * (1 + self.params.take_profit)):
                self.sell()
                self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Exit Position (Stop Loss/Take Profit)')
            elif self.position.size > 0:  # Long position
                if self.data.close < self.lower_band_mr or self.data.close < self.sma_tf or self.data.close < self.lowest_bo[-1]:
                    self.sell()
                    self.log(f'SELL executed, Price: {self.data.close[0]}, Strategy: Exit Position')
            elif self.position.size < 0:  # Short position
                if self.data.close > self.upper_band_mr or self.data.close > self.sma_tf or self.data.close > self.highest_bo[-1]:
                    self.buy()
                    self.log(f'BUY executed, Price: {self.data.close[0]}, Strategy: Exit Position')

    def log(self, text):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {text}')
