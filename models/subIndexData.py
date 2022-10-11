from ta.momentum import RSIIndicator
from ta.trend import IchimokuIndicator


class SubIndexData():
    def __init__(self):
        print("보조지표 생성자")

    def calc_ichimoku(self, df):
        # 일목균형표 데이터 생성
        id_ichimoku = IchimokuIndicator(high=df['high'], low=df['low'], visual=True, fillna=True)
        df['span_a'] = id_ichimoku.ichimoku_a()
        df['span_b'] = id_ichimoku.ichimoku_b()
        df['base_line'] = id_ichimoku.ichimoku_base_line()
        df['conv_line'] = id_ichimoku.ichimoku_conversion_line()
        return df

    def calc_RSI(self,df):
        id_rsi = RSIIndicator(close=df['close'],fillna=True)
        df['rsi'] = id_rsi.rsi()
        return df