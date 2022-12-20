import sys
import datetime
import re
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
from threading import Thread

from PyQt5.QAxContainer import *
from PyQt5 import QtWidgets, uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import models.accountData as AccountData
import models.stockList as StockList
import models.candleList as CandleList
import models.subIndexList as SubIndexList
import models.kiwoomData as KiwoomData
import models.kiwoomConditionList as ConditionKW
import models.kiwoomRealTimeData as KiwoomRealTimeData
import models.subIndexData as SubIndexData
import models.database as Database
import interface.conditionRegistration as ConditionRegistration
import interface.observer as observer
import interface.observerOrder as observerOrder
import interface.observerChejan as observerChejan
import interface.observerSubIndexList as observerSubIndexList
import interface.observerMainPrice as observerMainPrice
import controls.checkableComboBox as CheckableComboBox
import registerCondition
import registerConditionKW
import registerAICondition
import editAICondition
import editCondition
import editConditionKW
import settingPiggleDaoMostVoted
import models.scheduler as Scheduler
import os



class MainWindow(QMainWindow, ConditionRegistration.Observer, observer.Observer, observerOrder.Observer, observerSubIndexList.Observer, observerChejan.Observer, observerMainPrice.Observer):  # Window 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    def __init__(self):  # Window 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self._handler_login)
        self.CommmConnect()

    def setup(self):
        self.ui = uic.loadUi("main.ui", self)  # ui 파일 불러오기

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

        # 계정정보 가져오기
        # self.accountData = AccountData.AccountData(kiwoom)
        self.kiwoomData = KiwoomData.KiwoomData(self.kiwoom)
        self.accountBalanceInfo = self.kiwoomData.get_account_evaluation_balance()


        # 키움조건 로드
        self.kiwoom.dynamicCall("GetConditionLoad()")
        self.kiwoom.OnReceiveConditionVer.connect(self._handler_condition_load)

        # 저장소 생성
        # 저장소에서  최근 데이터 가져오기
        # 모니터링할 조건식 리스트 가져오기
        self.dataManager = Database.Database()
        #피글 DAO 값 연동하기
        self.createPiggleDaoMostVotedFile()
        self.createSettingPiggleDaoMostVotedFile()
        self.getPiggleDaoMostVotedScheduler()
        self.createConditionFile()
        self.createKiwoomConditionFile()
        self.createAIConditionFile()
        self.createFavoriteFile()
        self.createLatestVariablesFile()
        self.monitoredConditionList = self.getSavedConditionList()
        self.monitoredKiwoomConditionList = self.getSavedKiwoomConditionList()
        self.monitoredAIConditionList = self.getSavedAIConditionList()
        self.monitoredPiggleDaoMostVotedList = self.getSavedPiggleDaoMostVotedList()
        self.settingPiggleDaoMostVoted = self.getSavedSettingPiggleDaoMostVotedList()

        self.stocklist = StockList.StockList(self.kiwoom)
        self.stockList = self.stocklist.getList()
        self.candlelist = CandleList.CandleList()
        self.candleList = self.candlelist.getList()
        self.subindexlist = SubIndexList.SubIndexList()
        self.subIndexList = self.subindexlist.getList()


        self.selectedStock = "005930 : 삼성전자"
        self.selectedCandle = "1 일"
        self.selectedSubIndices = []
        self.getLatestVariables()

        # 차트영역 준비
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.bx_chartArea.addWidget(self.browser)
        # 종목 콤보박스 변경 이벤트 수신
        self.cb_stockList.activated.connect(self.selectStock)
        self.cb_stockList.addItems(self.stockList)
        # 캔들 콤보박스 변경 이벤트
        self.cb_candleList.activated.connect(self.selectCandle)
        self.cb_candleList.addItems(self.candleList)
        # 보조지표 목록 준비
        self.cb_subIndexList = CheckableComboBox.CheckableComboBox(self.subIndexList,self.selectedSubIndices)
        # self.cb_subIndexList.addItems(self.subIndexList)
        self.bx_subIndexListArea.addWidget(self.cb_subIndexList)

        self.cb_stockList.setCurrentIndex(self.stockList.index(self.selectedStock))
        self.cb_candleList.setCurrentIndex(self.candleList.index(self.selectedCandle))

        # 실시간데이터 로그
        # 주식체결 이벤트 발생시 tv_atLog에 appendPlainText(data)
        self.tv_atLog.setReadOnly(True)

        #실시간가격 데이터 테이블
        self.displayRealPriceTable()

        #자동 매매 체결 태이블
        self.displayChejanTable()

        # 계정 잔고 정보 나타내기
        self.displayBalanceTable()

        #계정잔고 테이블 새로고침 이벤트
        self.bt_updateAccount.clicked.connect(self.updateAccountTable)

        # 차트 그리기
        self.requestChartData()
        self.displayChart()
        #차트 페이지 라벨과 페이지 이동 버튼 이벤트 등록
        self.tv_chartCurrentPage.setText(str(self.currentPage))
        self.tv_chartTotalPage.setText(str(self.totalPage))
        self.bt_chartPrev.clicked.connect(self.clickPrevChart)
        self.bt_chartNext.clicked.connect(self.clickNextChart)

        # 조건테이블 나타내기
        self.displayConditionTable()
        # 단일 종목 조건 관리탭 이벤트
        self.bt_addCondition.clicked.connect(self.openRegisterCondition)
        self.bt_stopAll_condition.clicked.connect(self.stopAllCondition)
        self.bt_stop_condition.clicked.connect(self.stopSelectedCondition)
        self.bt_stopAll_conditionKW.clicked.connect(self.stopAllKiwoomCondition)
        self.bt_stop_conditionKW.clicked.connect(self.stopSelectedKiwoomCondition)
        self.bt_start_condition.clicked.connect(self.startSelectedCondition)
        self.bt_start_conditionKW.clicked.connect(self.startSelectedKiwoomCondition)

        self.bt_deleteCondition.clicked.connect(self.deleteConditions)
        self.bt_editCondition.clicked.connect(self.editCondition)
        self.checkedConditionList = []
        self.tbl_manageConditions.cellChanged.connect(self.conditionCheckboxChanged)

        # 키움조건 탭 테이블
        self.displayKiwoomConditionTable()

        # 키움 조건 관리탭 이벤트
        self.conditionListKW = self.GetConditionNameList()
        self.bt_addConditionKW.clicked.connect(self.openRegisterKiwoomCondition)
        self.bt_deleteConditionKW.clicked.connect(self.deleteKiwoomConditions)
        self.bt_editConditionKW.clicked.connect(self.editKiwoomCondition)
        self.checkedKiwoomConditionList = []
        self.conditionList = []
        self.tbl_manageKiwoomConditions.cellChanged.connect(self.kiwoomConditionCheckboxChanged)

        # AI자동매매 탭 테이블
        self.displayAIConditionTable()

        #AI자동매매 관리탭 이벤트
        self.bt_stopAll_conditionAI.clicked.connect(self.stopAllAICondition)
        self.bt_stop_conditionAI.clicked.connect(self.stopSelectedAICondition)
        self.bt_start_conditionAI.clicked.connect(self.startSelectedAICondition)

        self.bt_addAICondition.clicked.connect(self.openRegisterAICondition)
        self.bt_deleteAICondition.clicked.connect(self.deleteAIConditions)
        self.bt_editAICondition.clicked.connect(self.editAICondition)
        self.checkedAIConditionList = []
        self.tbl_manageAIConditions.cellChanged.connect(self.aiConditionCheckboxChanged)

        # 피글 DAO 투표수 많은 주가 정보 나타내기
        self.displayPiggleDaoMostVotedTable()

        # 피글DAO 자동매매 관리탭 이벤트
        self.bt_updatePiggleDaoMostVoted.clicked.connect(self.updatePiggleDaoMostVotedTable)
        self.bt_settingPiggleDaoMostVoted.clicked.connect(self.openSettingPiggleDaoMostVoted)

        # 즐겨찾기 준비
        self.favoriteList = self.getSavedFavoriteList()
        self.displayFavoriteList()
        self.setFavoriteIcon()
        self.bt_favorite.clicked.connect(self.favoriteButton)
        self.bt_favorite.setStyleSheet("background-color: transparent")

        self.ui.show()

        self.autoTrading = KiwoomRealTimeData.KiwoomRealTimeData(self.kiwoom, self.kiwoomData, self.monitoredConditionList,
                                                   self.monitoredKiwoomConditionList, self.monitoredAIConditionList, self.settingPiggleDaoMostVoted)

        #실시간 가격데이터 초기 셋팅
        selectedStockStr = self.selectedStock.split(" : ")
        self.autoTrading.getRealPriceData(selectedStockStr[0])

        # 옵저버 대상 등록
        self.register_subject(self.kiwoomData)
        self.register_subject_order(self.autoTrading)
        self.register_subject_subIndex(self.cb_subIndexList)
        self.register_subject_chejan(self.autoTrading)
        self.register_subject_mainPrice(self.autoTrading)


    def _handler_login(self, err_code):
        if err_code == 0:
            self.setup()
        else:
            choice = QtWidgets.QMessageBox.information(self, '로그인 실패',
                                                       "로그인 정보를 확인해주세요. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                print("로그인 성공")


    def CommmConnect(self):
        self.kiwoom.dynamicCall("CommConnect()")


    #실시간 가격 데이터 옵저버
    def update_mainPrice(self, df):
        for i in range(self.tbl_realPrice.rowCount()):
            x = df.iloc[0, i]
            pattern = "(\d)(?=(\d{3})+(?!\d))"
            repl = r"\1,"
            x = re.sub(pattern, repl, x)
            qtableWidgetItem = QtWidgets.QTableWidgetItem(str(x))
            self.tbl_realPrice.setItem(i, 0, qtableWidgetItem)
            if "+" in str(x):
                self.tbl_realPrice.item(i,0).setForeground(QtGui.QBrush(QtGui.QColor(255,0,0)))
            elif "-" in str(x):
                self.tbl_realPrice.item(i,0).setForeground(QtGui.QBrush(QtGui.QColor(0,0,255)))


    def register_subject_mainPrice(self, subject_mainPrice):
        self.subject_mainPrice = subject_mainPrice
        self.subject_mainPrice.register_observer_mainPrice(self)


    # 주문데이터 옵저버
    def update_order(self, data):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        self.tv_atLog.appendPlainText(data)
        print(str(data))

    def register_subject_order(self, subject_order):
        self.subject_order = subject_order
        self.subject_order.register_observer_order(self)

    #체결 데이터 옵저버
    def update_chejan(self, df):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        self.updateChejanTable(df)

    def register_subject_chejan(self, subject):
        self.subject_chejan = subject
        self.subject_chejan.register_observer_chejan(self)

    # 보조지표 선택 데이터 옵저버
    def update_subIndex(self):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        self.selectSubIndices()

    def register_subject_subIndex(self, subject_subIndex):
        self.subject_subIndex = subject_subIndex
        self.subject_subIndex.register_observer_subIndex(self)

    def update_condition(self, source,conditionDf):
        #신규 등록일 경우 조건으로 Thread 추가하고, 조건 수정일 경우 모든 쓰레드를 중지했다가 다시 들록한다.
        if source == "register":
            self.autoTrading.addConditionDf(conditionDf)
            self.monitoredConditionList = self.getSavedConditionList()
            self.checkedConditionList.clear()
            self.displayConditionTable()

        elif source == "edit":
            self.autoTrading.editConditionDf(conditionDf)
            self.monitoredConditionList = self.getSavedConditionList()
            self.checkedConditionList.clear()
            self.displayConditionTable()

        elif source == "registerKW":
            self.autoTrading.addKiwoomConditionDf(conditionDf)
            self.monitoredKiwoomConditionList = self.getSavedKiwoomConditionList()
            self.checkedKiwoomConditionList.clear()
            self.displayKiwoomConditionTable()

        elif source == "editKW":
            self.autoTrading.editKiwoomConditionDf(conditionDf)
            self.monitoredKiwoomConditionList = self.getSavedKiwoomConditionList()
            self.checkedKiwoomConditionList.clear()
            self.displayKiwoomConditionTable()

        elif source == "registerAI":
            self.autoTrading.addAIConditionDf(conditionDf)
            self.monitoredAIConditionList = self.getSavedAIConditionList()
            self.checkedAIConditionList.clear()
            self.displayAIConditionTable()

        elif source == "editAI":
            self.autoTrading.editAIConditionDf(conditionDf)
            self.monitoredAIConditionList = self.getSavedAIConditionList()
            self.checkedAIConditionList.clear()
            self.displayAIConditionTable()

        elif source == "settingPiggleDaoMostVoted":
            self.settingPiggleDaoMostVoted = conditionDf
            self.autoTrading.updateSettingPiggleDaoMostVoted(self.settingPiggleDaoMostVoted)


    def register_subject_condition(self,subject):
        self.subject_condition = subject
        self.subject_condition.register_observer_condition(self)


    def displayFavoriteList(self):
        self.tv_favorite.clear()
        for idx,row in self.favoriteList.iterrows():
            item = row['즐겨찾기']
            self.tv_favorite.addItem(item)

    def setFavoriteIcon(self):
        if len(self.favoriteList)>0:
            for idx,row in self.favoriteList.iterrows():
                if row['즐겨찾기'] == self.selectedStock:
                    isFavorite = True
                    break
                else :
                    isFavorite = False
            if isFavorite:
                self.bt_favorite.setIcon(QIcon('star-yellow.png'))
            else:
                self.bt_favorite.setIcon(QIcon('star-blank.png'))
        else:
            self.bt_favorite.setIcon(QIcon('star-blank.png'))

    def displayChejanTable(self):
        headerList = ['종목코드','종목명','매매구분','매매가','매매량','현재수익율','부분익절율',
                                            '최대익절율','부분손절율','최대손전율']
        nRows = 0
        nColumns = len(headerList)
        self.tbl_chejan.setRowCount(nRows)
        self.tbl_chejan.setColumnCount(nColumns)
        self.tbl_chejan.setHorizontalHeaderLabels(headerList)
        for i in range(nColumns):
            self.tbl_chejan.setColumnWidth(i,115)
        # self.tbl_chejan.resizeColumnsToContents()
        self.tbl_chejan.resizeRowsToContents()

    def displayRealPriceTable(self):
        headerList = ['현재가', '전일대비', '등락율', '누적거래량', '시가', '고가', '저가']
        nColumns = 1
        nRows = len(headerList)

        self.tbl_realPrice.setRowCount(nRows)
        self.tbl_realPrice.setColumnCount(nColumns)
        self.tbl_realPrice.setVerticalHeaderLabels(headerList)
        self.tbl_realPrice.horizontalHeader().hide()
        # self.tbl_realPrice.resizeColumnsToContents()
        self.tbl_realPrice.resizeRowsToContents()

    def updateChejanTable(self,df):
        rowPosition = self.tbl_chejan.rowCount()
        self.tbl_chejan.insertRow(rowPosition)
        for i in range(self.tbl_chejan.columnCount()):
            #새로운 열이 추가되므로, 데이터 프레임에서 row는 항상 0
            x = df.iloc[0, i]
            self.tbl_chejan.setItem(rowPosition, i, QtWidgets.QTableWidgetItem(x))

    def displayConditionTable(self):
        nRows = len(self.monitoredConditionList.index)
        nColumns = len(self.monitoredConditionList.columns) + 1  # 체크박스 추가 위해 컬럼 수 하나 추가
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
                    x = self.monitoredConditionList.iloc[i, (j - 1)]  # 체크박스 하나 추가되었으므로, 데이터는 컬럼 index 전부터 가져오기
                    self.tbl_manageConditions.setItem(i, j, QtWidgets.QTableWidgetItem(str(x)))
        self.tbl_manageConditions.setHorizontalHeaderLabels(
            ["", 'ID', '코드', '종목명', '매수가', '총금액', '시작시간', '종료시간', '부분익절율', '부분익절수량',
             '최대익절율', '부분손절율', '부분손절수량', '최대손절율'])
        for i in range(nColumns):
            if i == 0 or i == 1:
                self.tbl_manageConditions.setColumnWidth(i, 20)
            else:
                self.tbl_manageConditions.setColumnWidth(i,115)
        # self.tbl_manageConditions.resizeColumnsToContents()
        self.tbl_manageConditions.resizeRowsToContents()

    #조건 테이블 표시
    def displayKiwoomConditionTable(self):
        nRows = len(self.monitoredKiwoomConditionList.index)
        nColumns = len(self.monitoredKiwoomConditionList.columns)+1 #체크박스 추가 위해 컬럼 수 하나 추가
        self.tbl_manageKiwoomConditions.setRowCount(nRows)
        self.tbl_manageKiwoomConditions.setColumnCount(nColumns)
        for i in range(self.tbl_manageKiwoomConditions.rowCount()):
            for j in range(self.tbl_manageKiwoomConditions.columnCount()):
                if j == 0:
                    chkBoxItem = QtWidgets.QTableWidgetItem()
                    chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    chkBoxItem.setCheckState(Qt.Unchecked)
                    self.tbl_manageKiwoomConditions.setItem(i, j, chkBoxItem)
                else:
                    x = self.monitoredKiwoomConditionList.iloc[i, (j-1)] #체크박스 하나 추가되었으므로, 데이터는 컬럼 index 전부터 가져오기
                    self.tbl_manageKiwoomConditions.setItem(i, j, QtWidgets.QTableWidgetItem(str(x)))
        self.tbl_manageKiwoomConditions.setHorizontalHeaderLabels(["",'ID','조건코드','조건명','총금액','종목당금액',
                                   '시작시간','종료시간','부분익절율','부분익절수량','최대익절율',
                                   '부분손절율','부분손절수량','최대손절율'])
        for i in range(nColumns):
            if i == 0 or i == 1:
                self.tbl_manageKiwoomConditions.setColumnWidth(i, 20)
            else:
                self.tbl_manageKiwoomConditions.setColumnWidth(i,115)
        # self.tbl_manageKiwoomConditions.resizeColumnsToContents()
        self.tbl_manageKiwoomConditions.resizeRowsToContents()

    def displayAIConditionTable(self):
        nRows = len(self.monitoredAIConditionList.index)
        nColumns = len(self.monitoredAIConditionList.columns) + 1  # 체크박스 추가 위해 컬럼 수 하나 추가
        self.tbl_manageAIConditions.setRowCount(nRows)
        self.tbl_manageAIConditions.setColumnCount(nColumns)
        for i in range(self.tbl_manageAIConditions.rowCount()):
            for j in range(self.tbl_manageAIConditions.columnCount()):
                if j == 0:
                    chkBoxItem = QtWidgets.QTableWidgetItem()
                    chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    chkBoxItem.setCheckState(Qt.Unchecked)
                    self.tbl_manageAIConditions.setItem(i, j, chkBoxItem)
                else:
                    x = self.monitoredAIConditionList.iloc[i, (j - 1)]  # 체크박스 하나 추가되었으므로, 데이터는 컬럼 index 전부터 가져오기
                    self.tbl_manageAIConditions.setItem(i, j, QtWidgets.QTableWidgetItem(str(x)))
        self.tbl_manageAIConditions.setHorizontalHeaderLabels(
            ["", 'ID', '코드', '종목명', '구분', '회당매수액','총금액', '시작시간', '종료시간', '부분익절율', '부분익절수량', '최대익절율',
                                       '부분손절율', '부분손절수량', '최대손절율'])
        for i in range(nColumns):
            if i == 0 or i == 1:
                self.tbl_manageAIConditions.setColumnWidth(i, 20)
            else:
                self.tbl_manageAIConditions.setColumnWidth(i,115)
        # self.tbl_manageAIConditions.resizeColumnsToContents()
        self.tbl_manageAIConditions.resizeRowsToContents()

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
        for i in range(nColumns):
            self.tbl_totalBalance.setColumnWidth(i,115)
        # self.tbl_totalBalance.resizeColumnsToContents()
        self.tbl_totalBalance.resizeRowsToContents()

    def displayPiggleDaoMostVotedTable(self):
        nRows = len(self.monitoredPiggleDaoMostVotedList.index)
        nColumns = len(self.monitoredPiggleDaoMostVotedList.columns)
        self.tbl_piggleDaoMostVoted.setRowCount(nRows)
        self.tbl_piggleDaoMostVoted.setColumnCount(nColumns)
        for i in range(self.tbl_piggleDaoMostVoted.rowCount()):
            for j in range(self.tbl_piggleDaoMostVoted.columnCount()):
                x = self.monitoredPiggleDaoMostVotedList.iloc[i, j]
                self.tbl_piggleDaoMostVoted.setItem(i, j, QtWidgets.QTableWidgetItem(str(x)))

        self.tbl_piggleDaoMostVoted.setHorizontalHeaderLabels(self.monitoredPiggleDaoMostVotedList.columns)
        for i in range(nColumns):
            self.tbl_piggleDaoMostVoted.setColumnWidth(i,115)
        # self.tbl_piggleDaoMostVoted.resizeColumnsToContents()
        self.tbl_piggleDaoMostVoted.resizeRowsToContents()

    def displayChart(self):
        # 차트 그리기
        df = self.calcCurrentChartPageDataFrame()
        # 만약 보조지표를 선택하고 있을 경우
        df = self.calcSubIndexChartDataFrame(df)
        self.drawChart(df)
        self.setChartPageLabel()
        self.setChartPrevNextButton()

    def setChartPageLabel(self):
        self.tv_chartCurrentPage.setText(str(self.currentPage))

    def setChartPrevNextButton(self):
        if self.currentPage == 1:
            self.bt_chartPrev.setDisabled(True)
        else:
            self.bt_chartPrev.setEnabled(True)
        if self.currentPage == self.totalPage:
            self.bt_chartNext.setDisabled(True)
        else:
            self.bt_chartNext.setEnabled(True)

    def requestChartData(self):
        #종목코드 가져오기
        code = self.selectedStock.split(" : ")[0]
        now = datetime.datetime.now()
        time = now.strftime("%Y%m%d")
        interval = self.selectedCandle.split(" ")[0]
        type = self.selectedCandle.split(" ")[1]

        self.totalChartData = self.kiwoomData.request_candle_data(code=code, date=time, nPrevNext=0, type=type,
                            interval=interval)

        self.totalRow = len(self.totalChartData.index)
        self.currentStartIndex = 0
        self.currentEndIndex = 60
        self.totalPage = int(self.totalRow/60)
        self.currentPage = self.totalPage
        self.tv_chartTotalPage.setText(str(self.totalPage))

    def calcCurrentChartPageDataFrame(self):
        df = self.totalChartData[self.totalChartData["index"] >= self.currentStartIndex]
        df = df[df["index"] < self.currentEndIndex]
        return df

    def calcSubIndexChartDataFrame(self,df):
        subIndex = SubIndexData.SubIndexData()
        if len(self.selectedSubIndices) >= 1:
            for i in self.selectedSubIndices:
                if (i == "RSI"):
                    df = subIndex.calc_RSI(df)
                elif (i == "일목균형표"):
                    df = subIndex.calc_ichimoku(df)
                elif (i == "5-이평선"):
                    df = subIndex.calc_SMA(df, 5)
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
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

    #콤보박스 변경 이벤트
    def selectStock(self):
        self.selectedStock = self.cb_stockList.currentText()
        selectedStockStr = self.selectedStock.split(" : ")
        self.autoTrading.getRealPriceData(selectedStockStr[0])
        self.requestChartData()
        self.displayChart()
        self.setFavoriteIcon()
        self.saveLatestVariables()

    def selectCandle(self):
        self.selectedCandle = self.cb_candleList.currentText()
        self.requestChartData()
        self.displayChart()
        self.saveLatestVariables()

    def selectSubIndices(self):
        self.selectedSubIndices = self.cb_subIndexList.currentData()
        self.requestChartData()
        self.displayChart()
        self.saveLatestVariables()

    def clickPrevChart(self):
        self.currentStartIndex = self.currentStartIndex + 60
        self.currentEndIndex = self.currentEndIndex + 60
        self.currentPage = int((self.totalRow - self.currentStartIndex)/60)
        self.displayChart()

    def clickNextChart(self):
        self.currentStartIndex = self.currentStartIndex - 60
        self.currentEndIndex = self.currentEndIndex - 60
        self.currentPage = int((self.totalRow - self.currentStartIndex)/60)
        self.displayChart()

    def createLatestVariablesFile(self):
        latestList = ['종목','캔들','보조지표']
        self.dataManager.createCSVFile("pats_latest.csv",latestList)

    def getLatestVariables(self):
        df = self.dataManager.readCSVFile("pats_latest.csv")
        for idx, row in df.iterrows():
            if idx == 0:
                self.selectedStock = row['종목']
                self.selectedCandle = row['캔들']
                subString = row['보조지표'].replace("[","")
                subString = subString.replace("]", "")
                subString = subString.replace("'","")
                subStringList = subString.split(", ")
                for i in subStringList:
                    self.selectedSubIndices.append(i)

    def saveLatestVariables(self):
        df = pd.DataFrame([[self.selectedStock,self.selectedCandle,self.selectedSubIndices]],columns=['종목','캔들','보조지표'])
        self.dataManager.updateCSVFile("pats_latest.csv",df)

    def openRegisterCondition(self):
        #만약 현재 조건이 이미 있으면 마지막열 id가져오고, 아니라면 0으로 한다.
        if len(self.monitoredConditionList)>0:
            lastConditionId =self.monitoredConditionList['ID'].iloc[-1]
        else:
            lastConditionId = 0
        regCondi = registerCondition.RegisterCondition(self.dataManager,lastConditionId,self.stockList,self.monitoredConditionList)
        self.register_subject_condition(regCondi)

    def conditionCheckboxChanged(self, row, column):
        item = self.tbl_manageConditions.item(row, column)
        if self.tbl_manageConditions.item(row, 1) != None:
            id = int(self.tbl_manageConditions.item(row, 1).text())
            currentState = item.checkState()
            if currentState == Qt.Checked:
                self.checkedConditionList.append(id)
            else:
                if len(self.checkedConditionList) > 0:
                    self.checkedConditionList.remove(id)

    def deleteConditions(self):
        if len(self.checkedConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 삭제',
                                                "삭제할 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            dropCodeList = []
            for id in self.checkedConditionList:
                df = self.monitoredConditionList.loc[self.monitoredConditionList['ID']!=id]
                dropDf = self.monitoredConditionList.loc[self.monitoredConditionList['ID']==id]
                for idx,row in dropDf.iterrows():
                    dropCodeList.append(row['코드'])
            self.autoTrading.deleteConditionDf(dropCodeList)
            self.dataManager.removeRows("pats_condition.csv",df)
            self.monitoredConditionList = self.getSavedConditionList()
            self.checkedConditionList.clear()
            self.displayConditionTable()

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
        conditionHeaderList = ['ID','코드','종목명','매수가','총금액','시작시간','종료시간',
                     '부분익절율','부분익절수량','최대익절율','부분손절율','부분손절수량','최대손절율']
        self.dataManager.createCSVFile("pats_condition.csv",conditionHeaderList)

    def getSavedConditionList(self):
        df = self.dataManager.readCSVFile("pats_condition.csv")
        return df


    def openRegisterKiwoomCondition(self):
        #만약 현재 조건이 이미 있으면 마지막열 id가져오고, 아니라면 0으로 한다.
        if len(self.monitoredKiwoomConditionList)>0:
            lastConditionId =self.monitoredKiwoomConditionList['ID'].iloc[-1]
        else:
            lastConditionId = 0
        # conditionList = ConditionKW.KiwoomConditionList(self.kiwoom).getKiwoomConditionList()
        regCondi = registerConditionKW.RegisterConditionKW(self.dataManager,self.conditionListKW,lastConditionId,self.monitoredKiwoomConditionList)
        self.register_subject_condition(regCondi)


    def _handler_condition_load(self, ret, msg):
        print("handler condition load", ret, msg)

    def GetConditionNameList(self):
        data = self.kiwoom.dynamicCall("GetConditionNameList()")
        conditions = data.split(";")[:-1]
        self.condition_list = []
        for condition in conditions:
            index, name = condition.split('^')
            self.condition_list.append(index + " : " + name)
        return self.condition_list

    def kiwoomConditionCheckboxChanged(self, row, column):
        item = self.tbl_manageKiwoomConditions.item(row, column)
        if self.tbl_manageKiwoomConditions.item(row, 1) != None:
            id = int(self.tbl_manageKiwoomConditions.item(row, 1).text())
            currentState = item.checkState()
            if currentState == Qt.Checked:
                self.checkedKiwoomConditionList.append(id)
            else:
                if len(self.checkedKiwoomConditionList) > 0:
                    self.checkedKiwoomConditionList.remove(id)

    def deleteKiwoomConditions(self):
        if len(self.checkedKiwoomConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 삭제',
                                                "삭제할 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            dropCodeList = []
            for id in self.checkedKiwoomConditionList:
                df = self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList['ID'] != id]
                dropDf = self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList['ID'] == id]
                for idx, row in dropDf.iterrows():
                    dropCodeList.append(row['코드'])
            self.autoTrading.deleteKiwoomConditionDf(dropCodeList)
            self.dataManager.removeRows("pats_kiwoom_condition.csv", df)
            self.monitoredKiwoomConditionList = self.getSavedKiwoomConditionList()
            self.checkedKiwoomConditionList.clear()
            self.displayKiwoomConditionTable()


    def editKiwoomCondition(self):
        #self.checkedConditionList 아이템 갯수 확인 1개 아니면 진행하지 않는다. 노티피케이션 보인다.
        if len(self.checkedKiwoomConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 수정',
                                                "수정할 조건을 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        elif len(self.checkedKiwoomConditionList) > 1 :
            choice = QtWidgets.QMessageBox.information(self, '조건 수정',
                                                "수정할 조건을 하나만 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            id = self.checkedKiwoomConditionList[0]
            #체크한 아이디와 동일한 id를 가진 조건을 가져와서(df 시리즈) 수정 페이지로 넘긴다.
            dataRow = self.monitoredKiwoomConditionList[self.monitoredKiwoomConditionList['ID'] == id]
            editCondi = editConditionKW.EditConditionKW(self.dataManager, dataRow, self.monitoredKiwoomConditionList,self.conditionListKW)
            self.register_subject_condition(editCondi)

    def createKiwoomConditionFile(self):
        conditionHeaderList = ['ID','코드','조건명','총금액','종목당금액',
                                   '시작시간','종료시간','부분익절율','부분익절수량','최대익절율',
                                   '부분손절율','부분손절수량','최대손절율']
        self.dataManager.createCSVFile("pats_kiwoom_condition.csv",conditionHeaderList)

    def getSavedKiwoomConditionList(self):
        df = self.dataManager.readCSVFile("pats_kiwoom_condition.csv")
        return df


    def openRegisterAICondition(self):
        #만약 현재 조건이 이미 있으면 마지막열 id가져오고, 아니라면 0으로 한다.
        if len(self.monitoredAIConditionList)>0:
            lastConditionId =self.monitoredAIConditionList['ID'].iloc[-1]
        else:
            lastConditionId = 0
        regCondi = registerAICondition.RegisterAICondition(self.dataManager,lastConditionId,self.stockList,self.monitoredAIConditionList)
        self.register_subject_condition(regCondi)

    def aiConditionCheckboxChanged(self, row, column):
        item = self.tbl_manageAIConditions.item(row, column)
        if self.tbl_manageAIConditions.item(row, 1) != None:
            id = int(self.tbl_manageAIConditions.item(row, 1).text())
            currentState = item.checkState()
            if currentState == Qt.Checked:
                self.checkedAIConditionList.append(id)
            else:
                if len(self.checkedAIConditionList) > 0:
                    self.checkedAIConditionList.remove(id)

    def deleteAIConditions(self):
        if len(self.checkedAIConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 삭제',
                                                "삭제할 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            dropCodeList = []
            for id in self.checkedAIConditionList:
                df = self.monitoredAIConditionList.loc[self.monitoredAIConditionList['ID']!=id]
                dropDf = self.monitoredAIConditionList.loc[self.monitoredAIConditionList['ID']==id]
                for idx,row in dropDf.iterrows():
                    dropCodeList.append(row['코드'])
            self.autoTrading.deleteAIConditionDf(dropCodeList)
            self.dataManager.removeRows("pats_ai_condition.csv",df)
            self.monitoredAIConditionList = self.getSavedAIConditionList()
            self.checkedAIConditionList.clear()
            self.displayAIConditionTable()

    def editAICondition(self):
        #self.checkedConditionList 아이템 갯수 확인 1개 아니면 진행하지 않는다. 노티피케이션 보인다.
        if len(self.checkedAIConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 수정',
                                                "수정할 조건을 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        elif len(self.checkedAIConditionList) > 1 :
            choice = QtWidgets.QMessageBox.information(self, '조건 수정',
                                                "수정할 조건을 하나만 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            id = self.checkedAIConditionList[0]
            #체크한 아이디와 동일한 id를 가진 조건을 가져와서(df 시리즈) 수정 페이지로 넘긴다.
            dataRow = self.monitoredAIConditionList[self.monitoredAIConditionList['ID'] == id]
            editCondi = editAICondition.EditCondition(self.dataManager, dataRow, self.monitoredAIConditionList, self.stockList)
            self.register_subject_condition(editCondi)

    def createAIConditionFile(self):
        conditionHeaderList = ['ID', '코드', '종목명', 'AI매매구분', '회당매수액','총금액',
                                       '시작시간', '종료시간', '부분익절율', '부분익절수량', '최대익절율',
                                       '부분손절율', '부분손절수량', '최대손절율']
        self.dataManager.createCSVFile("pats_ai_condition.csv",conditionHeaderList)

    def getSavedAIConditionList(self):
        df = self.dataManager.readCSVFile("pats_ai_condition.csv")
        return df

    def openSettingPiggleDaoMostVoted(self):
        regSetting = settingPiggleDaoMostVoted.SettingPiggleDaoMostVoted(self.settingPiggleDaoMostVoted)
        self.register_subject_condition(regSetting)

    def createPiggleDaoMostVotedFile(self):
        conditionHeaderList = ['코드', '종목명', '예상가', '시종가구분', '예측일']
        self.dataManager.createCSVFile("pats_piggle_dao_most_voted.csv",conditionHeaderList)

    def getSavedPiggleDaoMostVotedList(self):
        df = self.dataManager.readCSVFile("pats_piggle_dao_most_voted.csv")
        return df

    def getPiggleDaoMostVotedScheduler(self):
        self.scheduler = Scheduler.Scheduler()
        # self.scheduler.job()
        # th = Thread(target=self.scheduler.run)
        # th.start()

    def createSettingPiggleDaoMostVotedFile(self):
        conditionHeaderList = ['적용여부', '매수수량']
        self.dataManager.createCSVFile("pats_setting_piggle_dao_most_voted.csv",conditionHeaderList)
        isApplied = True
        buyVolume = 0
        df = self.getSavedSettingPiggleDaoMostVotedList()
        for idx, row in df.iterrows():
            isApplied = row['적용여부']
            buyVolume = row['매수량']
            break
        arr = [isApplied, buyVolume]
        df = pd.DataFrame([arr],
                          columns=['적용여부', '매수량'])
        self.dataManager.updateCSVFile('pats_setting_piggle_dao_most_voted.csv', df)

    def getSavedSettingPiggleDaoMostVotedList(self):
        df = self.dataManager.readCSVFile("pats_setting_piggle_dao_most_voted.csv")
        return df

    def favoriteButton(self):
        #만약 현재 선택된 종목이 즐겨찾기에 있을 경우
        if len(self.favoriteList)>0:
            for idx,row in self.favoriteList.iterrows():
                if row['즐겨찾기'] == self.selectedStock:
                    isFavorite=True
                    break
                else :
                    isFavorite = False
            if isFavorite:
                self.removeFavorite()
            else:
                self.addFavorite()
        else:
            self.addFavorite()
        self.favoriteList = self.getSavedFavoriteList()
        self.setFavoriteIcon()
        self.displayFavoriteList()

    def addFavorite(self):
        df = pd.DataFrame([self.selectedStock],columns=['즐겨찾기'])
        self.dataManager.appendCSVFile("pats_favorite.csv",df)

    def removeFavorite(self):
        df = self.favoriteList.loc[self.favoriteList['즐겨찾기'] != self.selectedStock]
        self.dataManager.removeRows("pats_favorite.csv", df)

    def createFavoriteFile(self):
        favoriteHeader = ['즐겨찾기']
        self.dataManager.createCSVFile("pats_favorite.csv", favoriteHeader)

    def getSavedFavoriteList(self):
        df = self.dataManager.readCSVFile("pats_favorite.csv")
        return df

    def stopAllCondition(self):
        self.autoTrading.stopAllCondition()
        choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                   "모든 조건 자동매매를 중지합니다. ",
                                                   QtWidgets.QMessageBox.Ok)
        if choice == QtWidgets.QMessageBox.Ok:
            pass

    def stopSelectedCondition(self):
        if len(self.checkedConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                "멈출 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            dropCodeList = []
            for id in self.checkedConditionList:
                dropDf = self.monitoredConditionList.loc[self.monitoredConditionList['ID']==id]
                for idx,row in dropDf.iterrows():
                    dropCodeList.append(row['코드'])
            self.autoTrading.stopSelectedCondition(dropCodeList)
            choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                       "선택한 조건 자동매매를 중지합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
            self.checkedConditionList.clear()
            self.displayConditionTable()

    def startSelectedCondition(self):
        if len(self.checkedConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 시작',
                                                "시작할 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            codeList = []
            for id in self.checkedConditionList:
                startDf = self.monitoredConditionList.loc[self.monitoredConditionList['ID']==id]
                for idx,row in startDf.iterrows():
                    codeList.append(row['코드'])
            self.autoTrading.startSelectedCondition(codeList)
            choice = QtWidgets.QMessageBox.information(self, '조건 시작',
                                                       "선택한 조건 자동매매를 시작합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
            self.checkedConditionList.clear()
            self.displayConditionTable()


    def stopAllKiwoomCondition(self):
        self.autoTrading.stopAllKiwoomCondition()
        choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                   "모든 조건 자동매매를 중지합니다. ",
                                                   QtWidgets.QMessageBox.Ok)
        if choice == QtWidgets.QMessageBox.Ok:
            pass

    def stopSelectedKiwoomCondition(self):
        if len(self.checkedKiwoomConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                "멈출 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            dropCodeList = []
            for id in self.checkedKiwoomConditionList:
                dropDf = self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList['ID'] == id]
                for idx, row in dropDf.iterrows():
                    dropCodeList.append(row['코드'])
            self.autoTrading.stopSelectedKiwoomCondition(dropCodeList)
            choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                       "선택한 조건 자동매매를 중지합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
            self.checkedKiwoomConditionList.clear()
            self.displayKiwoomConditionTable()

    def startSelectedKiwoomCondition(self):
        if len(self.checkedKiwoomConditionList) == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 시작',
                                                "시작할 조건을 하나 이상 선택해주세요. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            codeList = []
            for id in self.checkedKiwoomConditionList:
                startDf = self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList['ID'] == id]
                for idx, row in startDf.iterrows():
                    codeList.append(row['코드'])
            self.autoTrading.startSelectedKiwoomCondition(codeList)
            choice = QtWidgets.QMessageBox.information(self, '조건 시작',
                                                       "선택한 조건 자동매매를 시작합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
            self.checkedKiwoomConditionList.clear()
            self.displayKiwoomConditionTable()

    def stopAllAICondition(self):
        self.autoTrading.stopAllAICondition()
        choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                   "모든 조건 자동매매를 중지합니다. ",
                                                   QtWidgets.QMessageBox.Ok)
        if choice == QtWidgets.QMessageBox.Ok:
            pass

    def stopSelectedAICondition(self):
        if len(self.checkedAIConditionList) == 0:
            choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                       "멈출 조건을 하나 이상 선택해주세요. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            dropCodeList = []
            for id in self.checkedAIConditionList:
                dropDf = self.monitoredAIConditionList.loc[self.monitoredAIConditionList['ID'] == id]
                for idx, row in dropDf.iterrows():
                    dropCodeList.append(row['코드'])
            self.autoTrading.stopSelectedAICondition(dropCodeList)
            choice = QtWidgets.QMessageBox.information(self, '조건 중지',
                                                       "선택한 조건 자동매매를 중지합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
            self.checkedAIConditionList.clear()
            self.displayAIConditionTable()

    def startSelectedAICondition(self):
        if len(self.checkedAIConditionList) == 0:
            choice = QtWidgets.QMessageBox.information(self, '조건 시작',
                                                       "시작할 조건을 하나 이상 선택해주세요. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
        else:
            codeList = []
            for id in self.checkedAIConditionList:
                startDf = self.monitoredAIConditionList.loc[self.monitoredAIConditionList['ID'] == id]
                for idx, row in startDf.iterrows():
                    codeList.append(row['코드'])
            self.autoTrading.startSelectedAICondition(codeList)
            choice = QtWidgets.QMessageBox.information(self, '조건 시작',
                                                       "선택한 조건 자동매매를 시작합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass
            self.checkedAIConditionList.clear()
            self.displayAIConditionTable()

    def closeEvent(self,event):
        self.saveLatestVariables()

    def updateAccountTable(self):
        self.accountBalanceInfo = self.kiwoomData.get_account_evaluation_balance()
        self.displayBalanceTable()

    def updatePiggleDaoMostVotedTable(self):
        self.scheduler.job()
        self.monitoredPiggleDaoMostVotedList = self.getSavedPiggleDaoMostVotedList()
        self.displayPiggleDaoMostVotedTable()

class InstallAPIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        choice = QtWidgets.QMessageBox.information(self,'키움 증권 API 설치',
                                               "키움 증권 Open API 설치 완료 후 다시 시작하세요. ",
                                               QtWidgets.QMessageBox.Ok)
        if choice == QtWidgets.QMessageBox.Ok:
            pass