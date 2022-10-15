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

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from PyQt5.QAxContainer import *
from PyQt5 import QtWidgets, uic, QtWebEngineWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import QUrl
import models.accountData as AccountData
import models.favoriteList as FavoriteList
import models.stockList as StockList
import models.candleList as CandleList
import models.subIndexList as SubIndexList
import models.kiwoomData as KiwoomData
import models.autoTrading as AutoTrading
import models.subIndexData as SubIndexData
import interface.observer as observer
import interface.observerOrder as observerOrder

def OnEventConnect(err_code):
    if err_code == 0:  # err_code가 0이면 로그인 성공 그외 실패
        window = MainWindow(kiwoom)  # Window 클래스를 생성하여 Wondow 변수에 할당
    else:
        print("fail")


class MainWindow(QtWidgets.QMainWindow, observer.Observer, observerOrder.Observer):  # Window 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    def __init__(self,kiwoom):  # Window 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출
        self.kiwoom = kiwoom

        self.is_completed = False
        arr = []


        # 저장소 생성
        # 저장소에서  최근 데이터 가져오기

        #모니터링할 조건식 리스트 가져오기
        self.monitoredConditionList = []
        self.autoTrading = AutoTrading.AutoTrading(kiwoom)
        #조건수 갯수만큼 for문해서 조건만큼 Thread 생성(조건을 변수로 넘긴다)
        self.autoTrading.addThread()


        # 즐겨찾기 객체생성
        self.favoriteList = FavoriteList.FavoriteList()
        self.favoriteList.setList(arr)

        self.accountData = AccountData.AccountData(kiwoom)
        self.accountBalanceInfo = self.accountData.getBalanceInfo()
        self.stocklist = StockList.StockList(kiwoom)
        self.stockList = self.stocklist.getList()
        self.candlelist = CandleList.CandleList()
        self.candleList = self.candlelist.getList()
        self.subindexlist = SubIndexList.SubIndexList()
        self.subIndexList = self.subindexlist.getList()


        #옵저버 대상(항목) 등록
        self.kiwoomData = KiwoomData.KiwoomData(kiwoom)
        self.register_subject(self.kiwoomData)
        self.register_subject_order(self.autoTrading)



        self.selectedStock = "005930 : 삼성전자"
        self.selectedCandle = "1 일"
        self.selectedSubIndices = ["RSI"]

        self.ui = uic.loadUi("main.ui",self) #ui 파일 불러오기
        #차트영역 준비
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.bx_chartArea.addWidget(self.browser)
        #종목 콤보박스 변경 이벤트 수신
        self.cb_stockList.activated.connect(self.selectStock)
        self.cb_stockList.addItems(self.stockList)
        self.cb_candleList.activated.connect(self.selectCandle)
        self.cb_candleList.addItems(self.candleList)
        self.cb_subIndexList.activated.connect(self.selectSubIndices)
        self.cb_subIndexList.addItems(self.subIndexList)



        #실시간데이터 로그
        # 주식체결 이벤트 발생시 tv_atLog에 appendPlainText(data)
        self.tv_atLog.setReadOnly(True)

        #계정 잔고 정보 나타내기
        self.displayBalanceTable()
        #차트 그리기
        self.displayChart()

        #보조지표 선택에 변경이 있을 경우, df 데이터 변경
        self.ui.show()

    #캔들데이터 옵저버
    def update(self, is_completed,data):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        self.is_completed = is_completed
        self.dfFromModule = data


    def register_subject(self, subject):
        self.subject = subject
        self.subject.register_observer(self)

    # 주문데이터 옵저버
    def update_order(self, data):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        print("주문완료 data"+data)
        self.tv_atLog.appendPlainText(data)

    def register_subject_order(self, subject_order):
        self.subject_order = subject_order
        self.subject_order.register_observer_order(self)

    #잔고 테이블 표시
    def displayBalanceTable(self):
        print("account"+str(self.accountBalanceInfo))

        nRows = len(self.accountBalanceInfo.index)
        nColumns = len(self.accountBalanceInfo.columns)
        self.tbl_totalBalance.setRowCount(nRows)
        self.tbl_totalBalance.setColumnCount(nColumns)
        # self.setItemDelegate(FloatDelegate())

        for i in range(self.tbl_totalBalance.rowCount()):
            for j in range(self.tbl_totalBalance.columnCount()):
                x = self.accountBalanceInfo.iloc[i, j]
                self.tbl_totalBalance.setItem(i, j, QtWidgets.QTableWidgetItem(x))

        self.tbl_totalBalance.setHorizontalHeaderLabels(self.accountBalanceInfo.columns)
        self.tbl_totalBalance.resizeColumnsToContents()
        self.tbl_totalBalance.resizeRowsToContents()

    def displayChart(self):
        # 차트 그리기
        df = self.requestChartData()
        # 만약 보조지표를 선택하고 있을 경우
        subIndex = SubIndexData.SubIndexData()
        if len(self.selectedSubIndices) >= 1:
            for i in self.selectedSubIndices:
                if (i == "RSI"):
                    df = subIndex.calc_RSI(df)
                elif (i == "일목균형표"):
                    df = subIndex.calc_ichimoku(df)

        self.drawChart(df)


    def requestChartData(self):
        #종목코드 가져오기
        code = self.selectedStock.split(" : ")[0]
        now = datetime.datetime.now()
        time = now.strftime("%Y%m%d")
        interval = self.selectedCandle.split(" ")[0]
        type = self.selectedCandle.split(" ")[1]

        self.kiwoomData.request_candle_data(code=code, date=time, nPrevNext=0, type=type,
                            interval=interval)
        while(self.is_completed == False):
            print("대기중")

        print("대기끝")
        self.is_completed = False
        df = self.dfFromModule
        df = df[df["index"] < 20]
        return df

    def drawChart(self,df):
        # Create subplots and mention plot grid size
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03,
                            row_width=[0.2, 0.2, 0.7])

        # Plot OHLC on 1st row
        fig.add_trace(go.Candlestick(x=df['date'],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'],showlegend=False),row=1, col=1)

        # #if문으로 보조지표 선택시 차트 그리기
        if "일목균형표" in self.selectedSubIndices :
            fig.add_trace(go.Scatter(x=df['date'],
                                     y=df.span_a,
                                     fill=None,
                                     line=dict(color='pink', width=1),
                                     name='스팬 1'
                                     ), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date'],
                                     y=df.span_b,
                                     fill='tonexty', #스팬 a , b 사이에 컬러 채우기
                                     line=dict(color='lightsteelblue', width=1),
                                     name='스팬 2'
                                     ), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date'],
                                     y=df.base_line,
                                     fill=None,
                                     line=dict(color='green', width=3),
                                     name='기준선'
                                     ), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['date'],
                                     y=df.conv_line,
                                     fill=None,
                                     line=dict(color='darkorange', width=1),
                                     name='전환선'
                                     ), row=1, col=1)

        if "RSI" in self.selectedSubIndices :
            fig.add_trace(go.Scatter(x=df['date'], y=df['rsi'], mode="lines", name="RSI", showlegend=True), row=2, col=1)

        # Bar trace for volumes on 2nd row without legend
        fig.add_trace(go.Bar(x=df['date'], y=df['volume'], name="거래량", showlegend=False), row=3, col=1)

        # Do not show OHLC's rangeslider plot
        fig.update(layout_xaxis_rangeslider_visible=False)
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

        # ----------------------------------------------------------------------------------#
        # 그래프 구역 나누기
        # fig = plt.figure(figsize=(11, 8))
        # fig.set_facecolor('w')
        # self.canvas = FigureCanvas(fig)
        # self.toolbar = NavigationToolbar(self.canvas, self)
        # self.bx_chartArea.addWidget(self.canvas)
        # self.bx_chartArea.addWidget(self.toolbar)
        #
        # gs = gridspec.GridSpec(3, 1, height_ratios=[3, 1, 1])
        # axs = []
        # axs.append(plt.subplot(gs[0]))  # 위 차트 = 캔들
        # axs.append(plt.subplot(gs[1], sharex=axs[0]))  # 아래 차트 = RSI 등 백분율
        # axs.append(plt.subplot(gs[2], sharex=axs[0]))  # 아래 차트 = 거래량
        # for ax in axs:
        #     ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 13)))
        #     ax.xaxis.set_minor_locator(mdates.MonthLocator())
        # # ax. 캔들 차트
        # ax = axs[0]
        # x = np.arange(len(df.index))
        # ohlc = df[['open', 'high', 'low', 'close']].astype(int).values
        # dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))
        # candlestick_ohlc(ax, dohlc, width=0.5, colorup='r', colordown='b')
        #
        # ax1 = axs[1]
        #
        # #if문으로 보조지표 선택시 차트 그리기
        # if "일목균형표" in self.selectedSubIndices :
        #     # ax. 일목균형차트
        #     ax.plot(df.span_a, label='span_a', linestyle='solid', color='pink')
        #     ax.plot(df.span_b, label='span_b', linestyle='solid', color='lightsteelblue')
        #     ax.plot(df.base_line, label='base_line', linestyle='solid', color='green', linewidth=2)
        #     ax.plot(df.conv_line, label='conv_line', linestyle='solid', color='darkorange')
        #     ax.fill_between(df.index, df.span_a, df.span_b, alpha=0.3)
        # if "RSI" in self.selectedSubIndices :
        #     ax1.plot(df.rsi, label="rsi", linestyle="solid",color="red")
        #
        # ax.grid(True, axis='y', color='grey', alpha=0.5, linestyle='--')
        # ax.legend()
        #
        #
        #
        # # ax3. 거래량 차트
        # ax2 = axs[2]
        # color_fuc = lambda x: 'r' if x >= 0 else 'b'
        # color_list = list(df['volume'].diff().fillna(0).apply(color_fuc))
        # ax2.bar(x, df['volume'], width=0.5,
        #                 align='center',
        #                 color=color_list)
        # # ----------------------------------------------------------------------------------#
        # # 그래프 title 지정
        # # X축 티커 숫자 20개로 제한
        # ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        # # X축 라벨 지정
        # # bottom_axes.set_xlabel('Date', fontsize=15)
        # ax.legend()
        # plt.tight_layout()

    #콤보박스 변경 이벤트
    def selectStock(self):
        self.selectedStock = self.cb_stockList.currentText()
        print(self.selectedStock)
        self.displayChart()

    def selectCandle(self,item):
        self.selectedCandle = self.cb_candleList.currentText()
        self.displayChart()
        
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