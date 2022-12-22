_B='close'
_A=True
from ta.momentum import RSIIndicator,StochasticOscillator
from ta.trend import IchimokuIndicator,MACD,SMAIndicator
from ta.volatility import BollingerBands
class SubIndexData:
	def __init__(A):print('')
	def calc_SMA(D,df,period):A=period;B=SMAIndicator(close=df[_B],window=A,fillna=_A);C=str(A)+'sma';df[C]=B.sma_indicator();return df
	def calc_RSI(B,df):A=RSIIndicator(close=df[_B],fillna=_A);df['rsi']=A.rsi();return df
	def calc_stochastic(C,df):A=df;B=StochasticOscillator(high=A['high'],low=A['low'],close=A[_B],fillna=_A);A['stoch_k']=B.stoch();A['stoch_d']=B.stoch_signal();return A
	def calc_MACD(B,df):A=MACD(close=df[_B],fillna=_A);df['macd']=A.macd();df['macd_signal']=A.macd_signal();return df
	def calc_ichimoku(C,df):A=df;B=IchimokuIndicator(high=A['high'],low=A['low'],visual=_A,fillna=_A);A['span_a']=B.ichimoku_a();A['span_b']=B.ichimoku_b();A['base_line']=B.ichimoku_base_line();A['conv_line']=B.ichimoku_conversion_line();return A
	def calc_BB(C,df):A=df;B=BollingerBands(close=A[_B],fillna=_A);A['bb_mavg']=B.bollinger_mavg();A['bb_h']=B.bollinger_hband();A['bb_l']=B.bollinger_hband();return A