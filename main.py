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
from PyQt5.QtCore import Qt
import models.accountData as AccountData
import models.favoriteList as FavoriteList
import models.stockList as StockList
import models.candleList as CandleList
import models.subIndexList as SubIndexList
import models.kiwoomData as KiwoomData
import models.autoTrading as AutoTrading
import models.subIndexData as SubIndexData
import models.database as Database
import interface.conditionRegistration as ConditionRegistration
import interface.observer as observer
import interface.observerOrder as observerOrder
import interface.observerSubIndexList as observerSubIndexList
import controls.checkableComboBox as CheckableComboBox
import registerCondition
import editCondition

def OnEventConnect(err_code):
    if err_code == 0:  # err_code가 0이면 로그인 성공 그외 실패
        window = MainWindow(kiwoom)  # Window 클래스를 생성하여 Wondow 변수에 할당
    else:
        print("fail")


class MainWindow(QtWidgets.QMainWindow, ConditionRegistration.Observer, observer.Observer, observerOrder.Observer, observerSubIndexList.Observer):  # Window 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    def __init__(self,kiwoom):  # Window 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출
        self.kiwoom = kiwoom
        self.is_completed = False

        #계정정보 가져오기
        self.accountData = AccountData.AccountData(kiwoom)
        self.accountBalanceInfo = self.accountData.get_account_evaluation_balance()

        # 저장소 생성
        # 저장소에서  최근 데이터 가져오기
        #모니터링할 조건식 리스트 가져오기
        self.dataManager = Database.Database()
        self.createConditionFile()
        self.createFavoriteFile()
        self.monitoredConditionList = self.getSavedConditionList()
        self.autoTrading = AutoTrading.AutoTrading(kiwoom,self.monitoredConditionList)


        # 즐겨찾기 객체생성
        self.favoriteList = self.getSavedFavoriteList()

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
        self.selectedCandle = "1 달"
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

        #실시간데이터 로그
        # 주식체결 이벤트 발생시 tv_atLog에 appendPlainText(data)
        self.tv_atLog.setReadOnly(True)

        #계정 잔고 정보 나타내기
        self.displayBalanceTable()
        #차트 그리기
        self.displayChart()
        #조건테이블 나타내기
        self.displayConditionTable()
        # 자동매매 조건 관리탭 이벤트
        self.bt_addCondition.clicked.connect(self.openRegisterCondition)
        self.bt_stopAll.clicked.connect(self.stopAllAutoTrading)
        self.bt_deleteCondition.clicked.connect(self.deleteConditions)
        self.bt_editCondition.clicked.connect(self.editCondition)
        self.checkedConditionList = []
        self.tbl_manageConditions.cellChanged.connect(self.conditionCheckboxChanged)
        #즐겨찾기 준비
        self.displayFavoriteList()
        self.bt_favorite.clicked.connect(self.favoriteButton)

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

    def update_condition(self, source,condition):
        print("registered")
        self.monitoredConditionList = self.getSavedConditionList()
        self.displayConditionTable()
        #신규 등록일 경우 조건으로 Thread 추가하고, 조건 수정일 경우 모든 쓰레드를 중지했다가 다시 들록한다.
        if source == "register":
            self.autoTrading.addCondition(condition)
        elif source == "edit":
            self.autoTrading.resetConditions(self.monitoredConditionList)

    def register_subject_condition(self,subject):
        self.subject_condition = subject
        self.subject_condition.register_observer_condition(self)


    def displayFavoriteList(self):
        self.tv_favorite.clear()
        for i in self.favoriteList:
            self.tv_favorite.addItem(i)

    #조건 테이블 표시
    def displayConditionTable(self):
        nRows = len(self.monitoredConditionList.index)
        nColumns = len(self.monitoredConditionList.columns)+1 #체크박스 추가 위해 컬럼 수 하나 추가
        self.tbl_manageConditions.setRowCount(nRows)
        self.tbl_manageConditions.setColumnCount(nColumns)
        for i in range(self.tbl_manageConditions.rowCount()):
            for j in range(self.tbl_manageConditions.columnCount()):
                if j == 0:
                    chkBoxItem = QtWidgets.QTableWidgetItem()
                    chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    chkBoxItem.setCheckState(Qt.Unchecked)
                    self.tbl_manageConditions.setItem(i, j, chkBoxItem)
                    # x = self.monitoredConditionList.iloc[i, j]
                    # chkBoxItem = QtWidgets.QTableWidgetItem(x)
                    # chkBoxItem.setText(str(x))
                    # chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    # chkBoxItem.setCheckState(Qt.Unchecked)
                    # self.tbl_manageConditions.setItem(i, j, chkBoxItem)
                else:
                    x = self.monitoredConditionList.iloc[i, (j-1)] #체크박스 하나 추가되었으므로, 데이터는 컬럼 index 전부터 가져오기
                    self.tbl_manageConditions.setItem(i, j, QtWidgets.QTableWidgetItem(str(x)))
        self.tbl_manageConditions.setHorizontalHeaderLabels(["",'ID', '종목코드', '종목명', '매수가', '총금액', '시작시간', '종료시간', '부분익절율', '부분익절수량',
       '최대익절율', '부분손절율', '부분손절수량', '최대손절율'])
        self.tbl_manageConditions.resizeColumnsToContents()
        self.tbl_manageConditions.resizeRowsToContents()

        # 잔고 테이블 표시
    def displayBalanceTable(self):
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
        # fig.update(layout_xaxis2_rangeslider_visible=True)

        if "분" in self.selectedCandle :
            fig.update_xaxes(
                rangebreaks=[
                    # NOTE: Below values are bound (not single values), ie. hide x to y
                    dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                    dict(bounds=[15.55, 9], pattern="hour"),  # hide hours outside of 9.30am-4pm
                    dict(bounds=[15.32, 15.49], pattern="hour"),
                ]
            )
        else :
            fig.update_xaxes(
                rangebreaks=[
                    # NOTE: Below values are bound (not single values), ie. hide x to y
                    dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                ]
            )

        # fig.update_xaxes(tickmode='array',
        #                  tickvals=df['date'],
        #                  ticktext=[d[-4:] for d in df['date']])

        fig.update_layout(
            autosize=True,
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=10,
                pad=2
            ))
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        # Add range slider
        # fig.update_layout(
        #     xaxis2=dict(
        #         rangeselector=dict(
        #             buttons=list([
        #                 dict(count=1,
        #                      label="1m",
        #                      step="month",
        #                      stepmode="backward"),
        #                 dict(count=6,
        #                      label="6m",
        #                      step="month",
        #                      stepmode="backward"),
        #                 dict(count=1,
        #                      label="YTD",
        #                      step="year",
        #                      stepmode="todate"),
        #                 dict(count=1,
        #                      label="1y",
        #                      step="year",
        #                      stepmode="backward"),
        #                 dict(step="all")
        #             ])
        #         ),
        #         rangeslider=dict(
        #             visible=True
        #         ),
        #         type="date"
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
        #만약 현재 조건이 이미 있으면 마지막열 id가져오고, 아니라면 0으로 한다.
        if len(self.monitoredConditionList)>0:
            lastConditionId =self.monitoredConditionList['ID'].iloc[-1]
        else:
            lastConditionId = 0
        regCondi = registerCondition.RegisterCondition(self.dataManager,lastConditionId,self.stockList)
        self.register_subject_condition(regCondi)

    def conditionCheckboxChanged(self, row, column):
        item = self.tbl_manageConditions.item(row, column)
        if self.tbl_manageConditions.item(row, 1) != None:
            id = int(self.tbl_manageConditions.item(row, 1).text())
            currentState = item.checkState()
            if currentState == Qt.Checked:
                print("checked")
                print("is" + str(id))
                self.checkedConditionList.append(id)
            else:
                if len(self.checkedConditionList) > 0:
                    print("unchecked")
                    self.checkedConditionList.remove(id)

    def deleteConditions(self):
        if len(self.checkedConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 삭제',
                                                "삭제할 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            for id in self.checkedConditionList:
                print("is"+str(id))
                print(str(self.monitoredConditionList['ID']))
                df = self.monitoredConditionList.loc[self.monitoredConditionList['ID']!=id]
                print("shape"+str(df))
            self.dataManager.removeRows("pats_condition.csv",df)
            self.monitoredConditionList = self.getSavedConditionList()
            self.displayConditionTable()
            #모든 Thread를 stop, kiwoon실시간 객체 리스트 비우고, 다시 autoTrading 객체 리셋하기
            self.autoTrading.resetConditions(self.monitoredConditionList)
            print("delete")

    def editCondition(self):
        #self.checkedConditionList 아이템 갯수 확인 1개 아니면 진행하지 않는다. 노티피케이션 보인다.
        if len(self.checkedConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 수정',
                                                "수정할 조건을 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        elif len(self.checkedConditionList) > 1 :
            choice = QtWidgets.QMessageBox.information(self, '조건 수정',
                                                "수정할 조건을 하나만 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            id = self.checkedConditionList[0]
            #체크한 아이디와 동일한 id를 가진 조건을 가져와서(df 시리즈) 수정 페이지로 넘긴다.
            dataRow = self.monitoredConditionList[self.monitoredConditionList['ID'] == id]
            editCondi = editCondition.EditCondition(self.dataManager, dataRow, self.monitoredConditionList, self.stockList)
            self.register_subject_condition(editCondi)

    def createConditionFile(self):
        conditionHeaderList = ['ID','종목코드','종목명','매수가','총금액','시작시간','종료시간',
                     '부분익절율','부분익절수량','최대익절율','부분손절율','부분손절수량','최대손절율']
        self.dataManager.createCSVFile("pats_condition.csv",conditionHeaderList)

    def getSavedConditionList(self):
        df = self.dataManager.readCSVFile("pats_condition.csv")
        print(str(df))
        return df

    def favoriteButton(self):
        #만약 현재 선택된 종목이 즐겨찾기에 있을 경우
        for i in self.favoriteList:
            if self.selectedStock == i:
                self.removeFavorite()
            else :
                self.addFavorite()
        self.favoriteList = self.getSavedFavoriteList()
        self.displayFavoriteList()

    def addFavorite(self):
        self.dataManager.appendCSVFile("past_favorite.csv",self.favoriteList)

    def removeFavorite(self):
        df = self.monitoredConditionList.loc[self.favoriteList['즐겨찾기'] != self.selectedStock]
        self.dataManager.removeRows("pats_condition.csv", df)

    def createFavoriteFile(self):
        favoriteHeader = ['즐겨찾기']
        self.dataManager.createCSVFile("past_favorite.csv", favoriteHeader)

    def getSavedFavoriteList(self):
        df = self.dataManager.readCSVFile("past_favorite.csv")
        return df



    def stopAllAutoTrading(self):
        self.autoTrading.DisConnectRealData("5000")


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