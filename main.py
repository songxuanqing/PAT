import sys
import datetime
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec
from PyQt5.QAxContainer import *
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5 import uic
import models.favoriteList as FavoriteList
import models.stockList as StockList
import models.candleList as CandleList
import models.subIndexList as SubIndexList
import models.kiwoomData as KiwoomData
import models.subIndexData as SubIndexData
import interface.observer as observer


def OnEventConnect(err_code):
    if err_code == 0:  # err_code가 0이면 로그인 성공 그외 실패
        window = MainWindow(kiwoom)  # Window 클래스를 생성하여 Wondow 변수에 할당
    else:
        print("fail")


class MainWindow(QtWidgets.QMainWindow, observer.Observer):  # Window 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    def __init__(self,kiwoom):  # Window 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출
        self.kiwoom = kiwoom

        self.is_completed = False
        arr = []


        # 저장소 생성
        # 저장소에서  최근 데이터 가져오기


        # 즐겨찾기 객체생성
        self.favoriteList = FavoriteList.FavoriteList()
        self.favoriteList.setList(arr)

        self.stocklist = StockList.StockList(kiwoom)
        self.stockList = self.stocklist.getList()
        self.candlelist = CandleList.CandleList()
        self.candleList = self.candlelist.getList()
        self.subindexlist = SubIndexList.SubIndexList()
        self.subIndexList = self.subindexlist.getList()
        self.kiwoomData = KiwoomData.KiwoomData(kiwoom)
        self.register_subject(self.kiwoomData)

        self.selectedStock = "039490:삼성전기"
        self.selectedCandle = "1 주"
        self.selectedSubIndices = ["일목균형표"]

        self.ui = uic.loadUi("main.ui",self) #ui 파일 불러오기
        #종목 콤보박스 변경 이벤트 수신
        self.cb_stockList.currentTextChanged.connect(self.selectStock)
        self.cb_stockList.addItems(self.stockList)
        self.cb_candleList.currentTextChanged.connect(self.selectCandle)
        self.cb_candleList.addItems(self.candleList)
        self.cb_subIndexList.currentTextChanged.connect(self.selectSubIndices)
        self.cb_subIndexList.addItems(self.subIndexList)

        #차트 그리기
        df = self.requestChartData()
        #만약 보조지표를 선택하고 있을 경우
        subIndex = SubIndexData.SubIndexData()
        if len(self.selectedSubIndices)>1 :
            for i in self.selectedSubIndices :
                if(i=="RSI") :
                    self.df = subIndex.calc_RSI(df)
                elif(i=="일목균형표") :
                    self.df = subIndex.calc_ichimoku(df)

        self.drawChart(df)

        #보조지표 선택에 변경이 있을 경우, df 데이터 변경
        self.ui.show()

    def update(self, is_completed,data):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        self.is_completed = is_completed
        self.dfFromModule = data


    def register_subject(self, subject):
        self.subject = subject
        self.subject.register_observer(self)

    def requestChartData(self):
        #종목코드 가져오기
        code = self.selectedStock.split(":")[0]
        now = datetime.datetime.now()
        time = now.strftime("%Y%m%d")
        interval = self.selectedCandle.split(" ")[0]
        type = self.selectedCandle.split(" ")[1]
        self.kiwoomData.request_candle_data(code=code, date=time, nPrevNext=0, type=type,
                            interval=interval)
        while(self.is_completed == False):
            print("대기중")

        print("대기끝")
        df = self.dfFromModule
        return df

    def drawChart(self,df):
        # ----------------------------------------------------------------------------------#
        # 그래프 구역 나누기
        fig = plt.figure(figsize=(12, 8))
        fig.set_facecolor('w')
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.bx_chartArea.addWidget(self.toolbar)
        self.bx_chartArea.addWidget(self.canvas)

        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        axs = []
        axs.append(plt.subplot(gs[0]))  # 위 차트 = 캔들
        axs.append(plt.subplot(gs[1], sharex=axs[0]))  # 아래 차트 = 거래량
        for ax in axs:
            ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 13)))
            ax.xaxis.set_minor_locator(mdates.MonthLocator())
        # ax. 캔들 차트
        ax = axs[0]
        x = np.arange(len(df.index))
        ohlc = df[['open', 'high', 'low', 'close']].astype(int).values
        dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))
        candlestick_ohlc(ax, dohlc, width=0.5, colorup='r', colordown='b')

        #if문으로 보조지표 선택시 차트 그리기
        if "일목균형표" in self.selectedSubIndices :
            # ax. 일목균형차트
            ax.plot(df.span_a, label='span_a', linestyle='solid', color='pink')
            ax.plot(df.span_b, label='span_b', linestyle='solid', color='lightsteelblue')
            ax.plot(df.base_line, label='base_line', linestyle='solid', color='green', linewidth=2)
            ax.plot(df.conv_line, label='conv_line', linestyle='solid', color='darkorange')
            ax.fill_between(df.index, df.span_a, df.span_b, alpha=0.3)
        if "RSI" in self.selectedSubIndices :
            ax.plot(df.rsi, label="rsi", linestyle="solid",color="red")

        ax.grid(True, axis='y', color='grey', alpha=0.5, linestyle='--')
        ax.legend()

        # ax2. 거래량 차트
        ax2 = axs[1]
        color_fuc = lambda x: 'r' if x >= 0 else 'b'
        color_list = list(df['volume'].diff().fillna(0).apply(color_fuc))
        ax2.bar(x, df['volume'], width=0.5,
                        align='center',
                        color=color_list)
        # ----------------------------------------------------------------------------------#
        # 그래프 title 지정
        # X축 티커 숫자 20개로 제한
        ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        # X축 라벨 지정
        # bottom_axes.set_xlabel('Date', fontsize=15)
        ax.legend()
        plt.tight_layout()

    def selectStock(self,item):
        self.selectedStock = item
    def selectCandle(self,item):
        self.selectedCandle = item
    def selectSubIndices(self,item):
        self.selectedSubIndices.append(item)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
    kiwoom.dynamicCall("CommConnect()")
    kiwoom.OnEventConnect.connect(OnEventConnect)
    app.exec_()  # 메인 이벤트 루프에 진입 후 프로그램이 종료될 때까지 무한 루프 상태 대기


# import sys
# from PyQt5.QtWidgets import *
# from PyQt5.QAxContainer import *
# import mainWindow
#
# ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
#
# def OnEventConnect(err_code):
#     if err_code == 0:  # err_code가 0이면 로그인 성공 그외 실패
#         window = mainWindow.MainWindow(ocx)  # Window 클래스를 생성하여 Wondow 변수에 할당
#         window.show()  # Window 클래스를 노출
#     else:
#         print("fail")
#
# # py 파일 실행시 제일 먼저 동작
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # ocx.dynamicCall("CommConnect()")
#     # ocx.OnEventConnect.connect(OnEventConnect)
#     window = mainWindow.MainWindow(ocx)  # Window 클래스를 생성하여 Wondow 변수에 할당
#     window.show()  # Window 클래스를 노출
#     app.exec_()  # 메인 이벤트 루프에 진입 후 프로그램이 종료될 때까지 무한 루프 상태 대기