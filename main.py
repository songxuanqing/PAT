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
import models.accountData as AccountData
import models.favoriteList as FavoriteList
import models.stockList as StockList
import models.candleList as CandleList
import models.subIndexList as SubIndexList
import models.kiwoomData as KiwoomData
import models.autoTrading as AutoTrading
import models.subIndexData as SubIndexData
import models.database as Database
import interface.observer as observer
import interface.observerOrder as observerOrder
import interface.observerSubIndexList as observerSubIndexList
import controls.checkableComboBox as CheckableComboBox
import registerCondition

def OnEventConnect(err_code):
    if err_code == 0:  # err_code가 0이면 로그인 성공 그외 실패
        window = MainWindow(kiwoom)  # Window 클래스를 생성하여 Wondow 변수에 할당
    else:
        print("fail")


class MainWindow(QtWidgets.QMainWindow, observer.Observer, observerOrder.Observer, observerSubIndexList.Observer):  # Window 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    def __init__(self,kiwoom):  # Window 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출
        self.kiwoom = kiwoom
        self.is_completed = False
        arr = []

        #계정정보 가져오기
        self.accountData = AccountData.AccountData(kiwoom)
        self.accountBalanceInfo = self.accountData.getBalanceInfo()

        # 저장소 생성
        # 저장소에서  최근 데이터 가져오기
        #모니터링할 조건식 리스트 가져오기
        self.dataManager = Database.Database()
        self.createConditionFile()
        self.monitoredConditionList = self.getSavedConditionList()
        self.autoTrading = AutoTrading.AutoTrading(kiwoom,self.monitoredConditionList,self.accountData)


        # 즐겨찾기 객체생성
        self.favoriteList = FavoriteList.FavoriteList()
        self.favoriteList.setList(arr)
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
        self.cb_subIndexList = CheckableComboBox.CheckableComboBox()
        self.register_subject_subIndex(self.cb_subIndexList)

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
        #캔들 콤보박스 변경 이벤트
        self.cb_candleList.activated.connect(self.selectCandle)
        self.cb_candleList.addItems(self.candleList)
        #보조지표 목록 준비
        self.cb_subIndexList.addItems(self.subIndexList)
        self.bx_subIndexListArea.addWidget(self.cb_subIndexList)
        #자동매매 조건 관리탭 이벤트
        self.bt_addCondition.clicked.connect(self.openRegisterCondition)


        #실시간데이터 로그
        # 주식체결 이벤트 발생시 tv_atLog에 appendPlainText(data)
        self.tv_atLog.setReadOnly(True)

        #계정 잔고 정보 나타내기
        self.displayBalanceTable()
        #차트 그리기
        self.displayChart()

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

    # 보조지표 선택 데이터 옵저버
    def update_subIndex(self):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        self.selectSubIndices()

    def register_subject_subIndex(self, subject_subIndex):
        self.subject_subIndex = subject_subIndex
        self.subject_subIndex.register_observer_subIndex(self)

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
                elif (i == "5-이평선"):
                    df = subIndex.calc_SMA(df,5)
                elif (i == "10-이평선"):
                    df = subIndex.calc_SMA(df, 10)
                elif (i == "20-이평선"):
                    df = subIndex.calc_SMA(df, 20)
                elif (i == "60-이평선"):
                    df = subIndex.calc_SMA(df, 60)
                elif (i == "스토캐스틱"):
                    df = subIndex.calc_stochastic(df)
                elif (i == "MACD"):
                    df = subIndex.calc_MACD(df)
                elif (i == "BB"):
                    df = subIndex.calc_BB(df)
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
        df = df[df["index"] < 60]
        print(df)
        return df

    def drawChart(self,df):
        #rows 계산하기
        rows = 2
        if ("RSI" in self.selectedSubIndices) or ("스토캐스틱" in self.selectedSubIndices) :
            rows = rows + 1
        if ("MACD" in self.selectedSubIndices) :
            rows = rows + 1
        if rows == 2 :
            row_width = [0.2, 0.7]
        elif rows == 3 :
            row_width = [0.2, 0.2, 0.7]
        elif rows == 4 :
            row_width = [0.2, 0.2, 0.2, 0.7]
        # Create subplots and mention plot grid size
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03,
                            row_width=row_width)

        # Plot OHLC on 1st row
        fig.add_trace(go.Candlestick(x=df['date'],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'],showlegend=False),row=1, col=1)

        # Bar trace for volumes on 2nd row without legend
        fig.add_trace(go.Bar(x=df['date'], y=df['volume'], name="거래량", showlegend=False), row=2, col=1)

        # #if문으로 보조지표 선택시 차트 그리기
        if len(self.selectedSubIndices) >= 1:
            for i in self.selectedSubIndices:
                #일목균형표, 이평선, BB는 가격차트(1), RSI, 스토캐스틱은 3번차트, MACD는 4번 차트
                if (i == "일목균형표"):
                    fig.add_trace(go.Scatter(x=df['date'],
                                             y=df.span_a,
                                             fill=None,
                                             line=dict(color='pink', width=1),
                                             name='스팬 1'
                                             ), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df['date'],
                                             y=df.span_b,
                                             fill='tonexty',  # 스팬 a , b 사이에 컬러 채우기
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
                elif "이평선" in i:
                    lenDays = len(i.split("-")[0]) #이평선 날짜수 구하기 ex)이평선 x일 or xx일 따라서 len - 1만큼 파싱
                    col = i.split("-")[0][:lenDays]+"sma"
                    fig.add_trace(go.Scatter(x=df['date'], y=df[col],
                                             mode="lines", name=i, showlegend=True), row=1, col=1)
                elif (i == "BB"):
                    fig.add_trace(go.Scatter(x=df['date'],
                                             y=df.bb_mavg,
                                             fill=None,
                                             line=dict(color='red', width=1),
                                             name='상단밴드'
                                             ), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df['date'],
                                             y=df.bb_h,
                                             fill=None,
                                             line=dict(color='green', width=1),
                                             name='중심선'
                                             ), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df['date'],
                                             y=df.bb_l,
                                             fill=None,
                                             line=dict(color='blue', width=1),
                                             name='하단밴드'
                                             ), row=1, col=1)
                elif (i == "RSI"):
                    fig.add_trace(go.Scatter(x=df['date'], y=df['rsi'],
                                             mode="lines", name="RSI", showlegend=True), row=3, col=1)
                elif (i == "스토캐스틱"):
                    fig.add_trace(go.Scatter(x=df['date'], y=df.stoch_k,
                                             fill=None,
                                             line=dict(color='lightsteelblue', width=1),
                                             name='stoch_k'), row=3, col=1)
                    fig.add_trace(go.Scatter(x=df['date'], y=df.stoch_d,
                                             fill=None,
                                             line=dict(color='orange', width=1),
                                             name='stoch_d'), row=3, col=1)
                elif (i == "MACD"):
                    if rows == 4 :
                        mac_row = 4
                    elif rows == 3 :
                        mac_row = 3
                    fig.add_trace(go.Scatter(x=df['date'], y=df.macd,
                                             fill=None,
                                             line=dict(color='lightsteelblue', width=1),
                                             name='MACD'), row=mac_row, col=1)
                    fig.add_trace(go.Scatter(x=df['date'], y=df.macd_signal,
                                             fill=None,
                                             line=dict(color='orange', width=1),
                                             name='MACD_Signal'), row=mac_row, col=1)

        # Do not show OHLC's rangeslider plot
        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.update_xaxes(nticks=5)

        # fig.update_layout(
        #     xaxis=dict(
        #         tickmode='array',
        #         tickvals=df['date'],
        #         ticktext=[self.computeFormat(date) for date in df['date']],
        #     )
        # )
        # if "분" in self.selectedCandle:
        #     fig.update_xaxes(
        #         tickformat="%H%M\n%m%d")
        # if ("일" in self.selectedCandle) or ("주" in self.selectedCandle):
        #     fig.update_xaxes(
        #         tickformat="%d\n%m")
        # if "달" in self.selectedCandle:
        #     fig.update_xaxes(
        #         tickformat="%m\n%Y")
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

    # def computeFormat(self,date):
    #     date_to_time = datetime.datetime.strptime(date, "%Y%m%d")
    #     date_to_str = datetime.datetime.strftime(date_to_time, '%Y-%m-%d')
    #     print("date_to_str"+date_to_str)
    #     return date_to_str

    #콤보박스 변경 이벤트
    def selectStock(self):
        self.selectedStock = self.cb_stockList.currentText()
        print(self.selectedStock)
        self.displayChart()

    def selectCandle(self,item):
        self.selectedCandle = self.cb_candleList.currentText()
        self.displayChart()

    def selectSubIndices(self):
        self.selectedSubIndices = self.cb_subIndexList.currentData()
        self.displayChart()

    def openRegisterCondition(self):
        registerCondition.RegisterCondition(self.dataManager)

    def createConditionFile(self):
        conditionHeaderList = ['종목코드','종목명','매수가','총금액','시작시간','종료시간',
                     '부분익절율','부분익절수량','최대익절율','부분손절율','부분손절수량','최대손절율']
        self.dataManager.createCSVFile("pats_condition.csv",conditionHeaderList)

    def getSavedConditionList(self):
        df = self.dataManager.readCSVFile("pats_condition.csv")
        return df

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