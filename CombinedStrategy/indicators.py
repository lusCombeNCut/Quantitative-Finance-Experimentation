# indicators.py

import backtrader as bt

# Connors RSI indicator
class ConnorsRSI(bt.Indicator):
    lines = ('crsi',)
    params = (('rsi_period', 3), ('streak_rsi_period', 2), ('rank_period', 100))

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data, period=self.params.rsi_period)
        self.streak = bt.indicators.RSI(self.data.close - self.data.close(-1), period=self.params.streak_rsi_period)
        self.rank = bt.indicators.PercentRank(self.data.close, period=self.params.rank_period)

    def next(self):
        self.lines.crsi[0] = (self.rsi[0] + self.streak[0] + self.rank[0]) / 3

# Custom VWAP indicator
class VWAP(bt.Indicator):
    lines = ('vwap',)
    params = (('period', 0),)

    def __init__(self):
        self.addminperiod(1)
        self.plotinfo.ploty = True

    def next(self):
        typical_price = (self.data.high[0] + self.data.low[0] + self.data.close[0]) / 3
        volume = self.data.volume[0]
        
        if len(self) == 1:
            self.lines.vwap[0] = typical_price
        else:
            cumulative_tpv = typical_price * volume
            cumulative_volume = volume
            for i in range(1, len(self)):
                cumulative_tpv += (self.data.high[-i] + self.data.low[-i] + self.data.close[-i]) / 3 * self.data.volume[-i]
                cumulative_volume += self.data.volume[-i]
            self.lines.vwap[0] = cumulative_tpv / cumulative_volume
