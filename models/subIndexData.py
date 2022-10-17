from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import IchimokuIndicator, MACD, SMAIndicator
from ta.volatility import BollingerBands


class SubIndexData():
    def __init__(self):
        print("보조지표 생성자")

    def calc_SMA(self,df,period):
        id_sma = SMAIndicator(close=df['close'],window=period,fillna=True)
        col = str(period)+'sma'
        df[col] = id_sma.sma_indicator()
        return df

    def calc_RSI(self,df):
        id_rsi = RSIIndicator(close=df['close'],fillna=True)
        df['rsi'] = id_rsi.rsi()
        return df

    def calc_stochastic(self, df):
        id_stc = StochasticOscillator(high=df['high'],low=df['low'],close=df['close'],fillna=True)
        df['stoch_k'] = id_stc.stoch()
        df['stoch_d'] = id_stc.stoch_signal()
        return df

    def calc_MACD(self,df):
        id_macd = MACD(close=df['close'], fillna=True)
        df['macd'] = id_macd.macd()
        df['macd_signal'] = id_macd.macd_signal()
        return df

    def calc_ichimoku(self, df):
        # 일목균형표 데이터 생성
        id_ichimoku = IchimokuIndicator(high=df['high'], low=df['low'], visual=True, fillna=True)
        df['span_a'] = id_ichimoku.ichimoku_a()
        df['span_b'] = id_ichimoku.ichimoku_b()
        df['base_line'] = id_ichimoku.ichimoku_base_line()
        df['conv_line'] = id_ichimoku.ichimoku_conversion_line()
        return df

    def calc_BB(self,df):
        id_bb = BollingerBands(close=df['close'], fillna=True)
        df['bb_mavg'] = id_bb.bollinger_mavg()
        df['bb_h'] = id_bb.bollinger_hband()
        df['bb_l'] = id_bb.bollinger_hband()
        return df



