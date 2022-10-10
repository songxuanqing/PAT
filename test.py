import numpy as np
import pandas as pd
from trade.util.db_helper import *
from ta.trend import IchimokuIndicator
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib import rc, font_manager
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 종목코드
code = '010060'
db_name = 'RSIStrategy'

cols = [column[0] for column in cur.description]
df = pd.DataFrame.from_records(data=cur.fetchall(), columns=cols)
df = df.set_index('index')

# 일목균형표 데이터 생성
id_ichimoku = IchimokuIndicator(high=df['high'], low=df['low'], visual=True, fillna=True)
df['span_a'] = id_ichimoku.ichimoku_a()
df['span_b'] = id_ichimoku.ichimoku_b()
df['base_line'] = id_ichimoku.ichimoku_base_line()
df['conv_line'] = id_ichimoku.ichimoku_conversion_line()


fig = plt.figure(figsize=(12, 8))
fig.set_facecolor('w')
gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])

# fig, ax = plt.subplots(1, 1, figsize=(10, 6), constrained_layout=True)
axs = []
axs.append(plt.subplot(gs[0])) #위 차트 = 캔들
axs.append(plt.subplot(gs[1], sharex=axs[0])) #아래 차트 = 거래량

for ax in axs:
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 13)))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

# ax. 캔들 차트
ax = axs[0]
x = np.arange(len(df.index))
ohlc = df[['open', 'high', 'low', 'close']].astype(int).values
dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))
candlestick_ohlc(ax, dohlc, width=0.5, colorup='r', colordown='b')

# 일목균형표 추가
# ax.plot(df.close, label='close', linestyle='solid', color='purple', linewidth=2)
ax.plot(df.span_a, label='span_a', linestyle='solid', color='pink')
ax.plot(df.span_b, label='span_b', linestyle='solid', color='lightsteelblue')
ax.plot(df.base_line, label='base_line', linestyle='solid', color='green', linewidth=2)
ax.plot(df.conv_line, label='conv_line', linestyle='solid', color='darkorange')
ax.grid(True, axis='y', color='grey', alpha=0.5, linestyle='--')
ax.fill_between(df.index, df.span_a, df.span_b, alpha=0.3)

ax.set_title(f'OCI({code}) - 일목균형표')
ax.legend()

# ax2. 거래량 차트
ax2 = axs[1]
ax2.bar(x, df['volume'], color='k', width=0.6, align='center')

plt.tight_layout()
plt.show()
출처: https://lunadaddy.tistory.com/122 [하루y:티스토리]