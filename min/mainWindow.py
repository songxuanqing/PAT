_t='pats_piggle_dao_most_voted.csv'
_s='ilmock'
_r='mavg60'
_q='mavg20'
_p='mavg10'
_o='buyAmountPerTime'
_n='AIConditionList'
_m='kiwoomRealTimeData'
_l='rowName'
_k='displayFavoriteList'
_j='pats_setting_piggle_dao_most_voted.csv'
_i='pats_ai_condition.csv'
_h='pats_kiwoom_condition.csv'
_g='displayKiwwoomConditionTable'
_f='pats_condition.csv'
_e='pats_latest.csv'
_d='rsi'
_c='checkbox'
_b='type'
_a='pats_favorite.csv'
_Z='favorite'
_Y='favoriteButton'
_X=' : '
_W=False
_V='lossQtyPercent'
_U='profitQtyPercent'
_T='endTime'
_S='startTime'
_R='totalPrice'
_Q='price'
_P='candle'
_O='maxLossRate'
_N='lossRate'
_M='maxProfitRate'
_L='profitRate'
_K='name'
_J='createLatestVariablesFile'
_I=True
_H=None
_G='id'
_F='code'
_E='subIndex'
_D='displayKiwoomConditionTable'
_C='displayAIConditionTable'
_B='displayConditionTable'
_A='mainWindow'
import sys,datetime,re,matplotlib.ticker as ticker,numpy as np,pandas as pd,matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec
from plotly.subplots import make_subplots
import plotly.graph_objects as go,plotly.express as px
from threading import Thread
from PyQt5.QAxContainer import *
from PyQt5 import QtWidgets,uic,QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import models.accountData as AccountData,models.stockList as StockList,models.candleList as CandleList,models.subIndexList as SubIndexList,models.kiwoomData as KiwoomData,models.kiwoomConditionList as ConditionKW,models.kiwoomRealTimeData as KiwoomRealTimeData,models.subIndexData as SubIndexData,models.database as Database,interface.conditionRegistration as ConditionRegistration,interface.observer as observer,interface.observerOrder as observerOrder,interface.observerChejan as observerChejan,interface.observerSubIndexList as observerSubIndexList,interface.observerMainPrice as observerMainPrice,controls.checkableComboBox as CheckableComboBox,registerCondition,registerConditionKW,registerAICondition,editAICondition,editCondition,editConditionKW,settingPiggleDaoMostVoted,models.scheduler as Scheduler,os,openJson
class MainWindow(QMainWindow,ConditionRegistration.Observer,observer.Observer,observerOrder.Observer,observerSubIndexList.Observer,observerChejan.Observer,observerMainPrice.Observer):
	def __init__(self):super().__init__();self.kiwoom=QAxWidget('KHOPENAPI.KHOpenAPICtrl.1');self.kiwoom.OnEventConnect.connect(self._handler_login);self.CommmConnect()
	def setup(self):A='setup';self.msg,self.params=openJson.getJsonFiles();self.removeCondition=self.msg['removeCondition'];self.moreThanOneConditionForDelete=self.msg['moreThanOneConditionForDelete'];self.editConditionMsg=self.msg['editCondition'];self.selectConditionForEdit=self.msg['selectConditionForEdit'];self.onlyOneConditionForEdit=self.msg['onlyOneConditionForEdit'];self.stopCondition=self.msg['stopCondition'];self.stopAllConditionMsg=self.msg['stopAllCondition'];self.selectConditionForStop=self.msg['selectConditionForStop'];self.stoppedCondition=self.msg['stoppedCondition'];self.selectConditionForStart=self.msg['selectConditionForStart'];self.startCondition=self.msg['startCondition'];self.startedCondition=self.msg['startedCondition'];self.ui=uic.loadUi('main.ui',self);self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMinimizeButtonHint);frameGm=self.frameGeometry();screen=QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos());centerPoint=QApplication.desktop().screenGeometry(screen).center();frameGm.moveCenter(centerPoint);self.move(frameGm.topLeft());self.kiwoomData=KiwoomData.KiwoomData(self.kiwoom);self.accountBalanceInfo=self.kiwoomData.get_account_evaluation_balance();self.kiwoom.dynamicCall('GetConditionLoad()');self.kiwoom.OnReceiveConditionVer.connect(self._handler_condition_load);self.dataManager=Database.Database();self.createPiggleDaoMostVotedFile();self.createSettingPiggleDaoMostVotedFile();self.getPiggleDaoMostVotedScheduler();self.createConditionFile();self.createKiwoomConditionFile();self.createAIConditionFile();self.createFavoriteFile();self.createLatestVariablesFile();self.monitoredConditionList=self.getSavedConditionList();self.monitoredKiwoomConditionList=self.getSavedKiwoomConditionList();self.monitoredAIConditionList=self.getSavedAIConditionList();self.monitoredPiggleDaoMostVotedList=self.getSavedPiggleDaoMostVotedList();self.settingPiggleDaoMostVoted=self.getSavedSettingPiggleDaoMostVotedList();self.stocklist=StockList.StockList(self.kiwoom);self.stockList=self.stocklist.getList();self.candlelist=CandleList.CandleList();self.candleList=self.candlelist.getList();self.subindexlist=SubIndexList.SubIndexList();self.subIndexList=self.subindexlist.getList();self.selectedStock=self.params[_A][A]['selectedStockInit'];self.selectedCandle=self.params[_A][A]['selectedCandleInit'];self.selectedSubIndices=[];self.getLatestVariables();self.browser=QtWebEngineWidgets.QWebEngineView(self);self.bx_chartArea.addWidget(self.browser);self.cb_stockList.activated.connect(self.selectStock);self.cb_stockList.addItems(self.stockList);self.cb_candleList.activated.connect(self.selectCandle);self.cb_candleList.addItems(self.candleList);self.cb_subIndexList=CheckableComboBox.CheckableComboBox(self.subIndexList,self.selectedSubIndices);self.bx_subIndexListArea.addWidget(self.cb_subIndexList);self.cb_stockList.setCurrentIndex(self.stockList.index(self.selectedStock));self.cb_candleList.setCurrentIndex(self.candleList.index(self.selectedCandle));self.tv_atLog.setReadOnly(_I);self.displayRealPriceTable();self.displayChejanTable();self.displayBalanceTable();self.bt_updateAccount.clicked.connect(self.updateAccountTable);self.requestChartData();self.displayChart();self.tv_chartCurrentPage.setText(str(self.currentPage));self.tv_chartTotalPage.setText(str(self.totalPage));self.bt_chartPrev.clicked.connect(self.clickPrevChart);self.bt_chartNext.clicked.connect(self.clickNextChart);self.displayConditionTable();self.bt_addCondition.clicked.connect(self.openRegisterCondition);self.bt_stopAll_condition.clicked.connect(self.stopAllCondition);self.bt_stop_condition.clicked.connect(self.stopSelectedCondition);self.bt_stopAll_conditionKW.clicked.connect(self.stopAllKiwoomCondition);self.bt_stop_conditionKW.clicked.connect(self.stopSelectedKiwoomCondition);self.bt_start_condition.clicked.connect(self.startSelectedCondition);self.bt_start_conditionKW.clicked.connect(self.startSelectedKiwoomCondition);self.bt_deleteCondition.clicked.connect(self.deleteConditions);self.bt_editCondition.clicked.connect(self.editCondition);self.checkedConditionList=[];self.tbl_manageConditions.cellChanged.connect(self.conditionCheckboxChanged);self.displayKiwoomConditionTable();self.conditionListKW=self.GetConditionNameList();self.bt_addConditionKW.clicked.connect(self.openRegisterKiwoomCondition);self.bt_deleteConditionKW.clicked.connect(self.deleteKiwoomConditions);self.bt_editConditionKW.clicked.connect(self.editKiwoomCondition);self.checkedKiwoomConditionList=[];self.conditionList=[];self.tbl_manageKiwoomConditions.cellChanged.connect(self.kiwoomConditionCheckboxChanged);self.displayAIConditionTable();self.bt_stopAll_conditionAI.clicked.connect(self.stopAllAICondition);self.bt_stop_conditionAI.clicked.connect(self.stopSelectedAICondition);self.bt_start_conditionAI.clicked.connect(self.startSelectedAICondition);self.bt_addAICondition.clicked.connect(self.openRegisterAICondition);self.bt_deleteAICondition.clicked.connect(self.deleteAIConditions);self.bt_editAICondition.clicked.connect(self.editAICondition);self.checkedAIConditionList=[];self.tbl_manageAIConditions.cellChanged.connect(self.aiConditionCheckboxChanged);self.displayPiggleDaoMostVotedTable();self.bt_updatePiggleDaoMostVoted.clicked.connect(self.updatePiggleDaoMostVotedTable);self.bt_settingPiggleDaoMostVoted.clicked.connect(self.openSettingPiggleDaoMostVoted);self.favoriteList=self.getSavedFavoriteList();self.displayFavoriteList();self.setFavoriteIcon();self.bt_favorite.clicked.connect(self.favoriteButton);self.bt_favorite.setStyleSheet('background-color: transparent');self.ui.show();self.autoTrading=KiwoomRealTimeData.KiwoomRealTimeData(self.kiwoom,self.kiwoomData,self.monitoredConditionList,self.monitoredKiwoomConditionList,self.monitoredAIConditionList,self.settingPiggleDaoMostVoted);selectedStockStr=self.selectedStock.split(_X);self.autoTrading.getRealPriceData(selectedStockStr[0]);self.register_subject(self.kiwoomData);self.register_subject_order(self.autoTrading);self.register_subject_subIndex(self.cb_subIndexList);self.register_subject_chejan(self.autoTrading);self.register_subject_mainPrice(self.autoTrading)
	def _handler_login(self,err_code):
		if err_code==0:self.setup()
		else:
			failLogin=self.msg['failLogin'];checkLoginInfo=self.msg['checkLoginInfo'];choice=QtWidgets.QMessageBox.information(self,failLogin,checkLoginInfo,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:print('')
	def CommmConnect(self):self.kiwoom.dynamicCall('CommConnect()')
	def update_mainPrice(self,df):
		for i in range(self.tbl_realPrice.rowCount()):
			x=df.iloc[(0,i)];pattern='(\\d)(?=(\\d{3})+(?!\\d))';repl='\\1,';x=re.sub(pattern,repl,x);qtableWidgetItem=QtWidgets.QTableWidgetItem(str(x));self.tbl_realPrice.setItem(i,0,qtableWidgetItem)
			if'+'in str(x):self.tbl_realPrice.item(i,0).setForeground(QtGui.QBrush(QtGui.QColor(255,0,0)))
			elif'-'in str(x):self.tbl_realPrice.item(i,0).setForeground(QtGui.QBrush(QtGui.QColor(0,0,255)))
	def register_subject_mainPrice(self,subject_mainPrice):self.subject_mainPrice=subject_mainPrice;self.subject_mainPrice.register_observer_mainPrice(self)
	def update_order(self,data):self.tv_atLog.appendPlainText(data);print(str(data))
	def register_subject_order(self,subject_order):self.subject_order=subject_order;self.subject_order.register_observer_order(self)
	def update_chejan(self,df):self.updateChejanTable(df)
	def register_subject_chejan(self,subject):self.subject_chejan=subject;self.subject_chejan.register_observer_chejan(self)
	def update_subIndex(self):self.selectSubIndices()
	def register_subject_subIndex(self,subject_subIndex):self.subject_subIndex=subject_subIndex;self.subject_subIndex.register_observer_subIndex(self)
	def update_condition(self,source,conditionDf):
		if source=='register':self.autoTrading.addConditionDf(conditionDf);self.monitoredConditionList=self.getSavedConditionList();self.checkedConditionList.clear();self.displayConditionTable()
		elif source=='edit':self.autoTrading.editConditionDf(conditionDf);self.monitoredConditionList=self.getSavedConditionList();self.checkedConditionList.clear();self.displayConditionTable()
		elif source=='registerKW':self.autoTrading.addKiwoomConditionDf(conditionDf);self.monitoredKiwoomConditionList=self.getSavedKiwoomConditionList();self.checkedKiwoomConditionList.clear();self.displayKiwoomConditionTable()
		elif source=='editKW':self.autoTrading.editKiwoomConditionDf(conditionDf);self.monitoredKiwoomConditionList=self.getSavedKiwoomConditionList();self.checkedKiwoomConditionList.clear();self.displayKiwoomConditionTable()
		elif source=='registerAI':self.autoTrading.addAIConditionDf(conditionDf);self.monitoredAIConditionList=self.getSavedAIConditionList();self.checkedAIConditionList.clear();self.displayAIConditionTable()
		elif source=='editAI':self.autoTrading.editAIConditionDf(conditionDf);self.monitoredAIConditionList=self.getSavedAIConditionList();self.checkedAIConditionList.clear();self.displayAIConditionTable()
		elif source=='settingPiggleDaoMostVoted':self.settingPiggleDaoMostVoted=conditionDf;self.autoTrading.updateSettingPiggleDaoMostVoted(self.settingPiggleDaoMostVoted)
	def register_subject_condition(self,subject):self.subject_condition=subject;self.subject_condition.register_observer_condition(self)
	def displayFavoriteList(self):
		self.tv_favorite.clear()
		for (idx,row) in self.favoriteList.iterrows():name=self.params[_A][_k][_l];item=row[name];self.tv_favorite.addItem(item)
	def setFavoriteIcon(self):
		A='star-blank.png'
		if len(self.favoriteList)>0:
			for (idx,row) in self.favoriteList.iterrows():
				name=self.params[_A][_k][_l]
				if row[name]==self.selectedStock:isFavorite=_I;break
				else:isFavorite=_W
			if isFavorite:self.bt_favorite.setIcon(QIcon('star-yellow.png'))
			else:self.bt_favorite.setIcon(QIcon(A))
		else:self.bt_favorite.setIcon(QIcon(A))
	def displayChejanTable(self):
		A='displayChejanTable';code=self.params[_A][A][_F];name=self.params[_A][A][_K];type=self.params[_A][A][_b];price=self.params[_A][A][_Q];qty=self.params[_A][A]['qty'];currentProfitRate=self.params[_A][A]['currentProfitRate'];profitRate=self.params[_A][A][_L];maxProfitRate=self.params[_A][A][_M];lossRate=self.params[_A][A][_N];maxLossRate=self.params[_A][A][_O];headerList=[code,name,type,price,qty,currentProfitRate,profitRate,maxProfitRate,lossRate,maxLossRate];nRows=0;nColumns=len(headerList);self.tbl_chejan.setRowCount(nRows);self.tbl_chejan.setColumnCount(nColumns);self.tbl_chejan.setHorizontalHeaderLabels(headerList)
		for i in range(nColumns):self.tbl_chejan.setColumnWidth(i,115)
		self.tbl_chejan.resizeRowsToContents()
	def displayRealPriceTable(self):A='displayRealPriceTable';price=self.params[_A][A][_Q];compareToYesterday=self.params[_A][A]['compareToYesterday'];roc=self.params[_A][A]['roc'];accumulatedVolume=self.params[_A][A]['accumulatedVolume'];start=self.params[_A][A]['start'];high=self.params[_A][A]['high'];low=self.params[_A][A]['low'];headerList=[price,compareToYesterday,roc,accumulatedVolume,start,high,low];nColumns=1;nRows=len(headerList);self.tbl_realPrice.setRowCount(nRows);self.tbl_realPrice.setColumnCount(nColumns);self.tbl_realPrice.setVerticalHeaderLabels(headerList);self.tbl_realPrice.horizontalHeader().hide();self.tbl_realPrice.resizeRowsToContents()
	def updateChejanTable(self,df):
		rowPosition=self.tbl_chejan.rowCount();self.tbl_chejan.insertRow(rowPosition)
		for i in range(self.tbl_chejan.columnCount()):x=df.iloc[(0,i)];self.tbl_chejan.setItem(rowPosition,i,QtWidgets.QTableWidgetItem(x))
	def displayConditionTable(self):
		nRows=len(self.monitoredConditionList.index);nColumns=len(self.monitoredConditionList.columns)+1;self.tbl_manageConditions.setRowCount(nRows);self.tbl_manageConditions.setColumnCount(nColumns)
		for i in range(self.tbl_manageConditions.rowCount()):
			for j in range(self.tbl_manageConditions.columnCount()):
				if j==0:chkBoxItem=QtWidgets.QTableWidgetItem();chkBoxItem.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);chkBoxItem.setCheckState(Qt.Unchecked);self.tbl_manageConditions.setItem(i,j,chkBoxItem)
				else:x=self.monitoredConditionList.iloc[(i,j-1)];self.tbl_manageConditions.setItem(i,j,QtWidgets.QTableWidgetItem(str(x)))
		checkbox=self.params[_A][_B][_c];id=self.params[_A][_B][_G];code=self.params[_A][_B][_F];name=self.params[_A][_B][_K];price=self.params[_A][_B][_Q];totalPrice=self.params[_A][_B][_R];startTime=self.params[_A][_B][_S];endTime=self.params[_A][_B][_T];profitRate=self.params[_A][_B][_L];profitQtyPercent=self.params[_A][_B][_U];maxProfitRate=self.params[_A][_B][_M];lossRate=self.params[_A][_B][_N];lossQtyPercent=self.params[_A][_B][_V];maxLossRate=self.params[_A][_B][_O];self.tbl_manageConditions.setHorizontalHeaderLabels([checkbox,id,code,name,price,totalPrice,startTime,endTime,profitRate,profitQtyPercent,maxProfitRate,lossRate,lossQtyPercent,maxLossRate])
		for i in range(nColumns):
			if i==0 or i==1:self.tbl_manageConditions.setColumnWidth(i,20)
			else:self.tbl_manageConditions.setColumnWidth(i,115)
		self.tbl_manageConditions.resizeRowsToContents()
	def displayKiwoomConditionTable(self):
		nRows=len(self.monitoredKiwoomConditionList.index);nColumns=len(self.monitoredKiwoomConditionList.columns)+1;self.tbl_manageKiwoomConditions.setRowCount(nRows);self.tbl_manageKiwoomConditions.setColumnCount(nColumns)
		for i in range(self.tbl_manageKiwoomConditions.rowCount()):
			for j in range(self.tbl_manageKiwoomConditions.columnCount()):
				if j==0:chkBoxItem=QtWidgets.QTableWidgetItem();chkBoxItem.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);chkBoxItem.setCheckState(Qt.Unchecked);self.tbl_manageKiwoomConditions.setItem(i,j,chkBoxItem)
				else:x=self.monitoredKiwoomConditionList.iloc[(i,j-1)];self.tbl_manageKiwoomConditions.setItem(i,j,QtWidgets.QTableWidgetItem(str(x)))
		checkbox=self.params[_A][_D][_c];id=self.params[_A][_D][_G];code=self.params[_A][_D][_F];name=self.params[_A][_D][_K];totalPrice=self.params[_A][_D][_R];price=self.params[_A][_D][_Q];startTime=self.params[_A][_D][_S];endTime=self.params[_A][_D][_T];profitRate=self.params[_A][_D][_L];profitQtyPercent=self.params[_A][_D][_U];maxProfitRate=self.params[_A][_D][_M];lossRate=self.params[_A][_D][_N];lossQtyPercent=self.params[_A][_D][_V];maxLossRate=self.params[_A][_D][_O];self.tbl_manageKiwoomConditions.setHorizontalHeaderLabels([checkbox,id,code,name,totalPrice,price,startTime,endTime,profitRate,profitQtyPercent,maxProfitRate,lossRate,lossQtyPercent,maxLossRate])
		for i in range(nColumns):
			if i==0 or i==1:self.tbl_manageKiwoomConditions.setColumnWidth(i,20)
			else:self.tbl_manageKiwoomConditions.setColumnWidth(i,115)
		self.tbl_manageKiwoomConditions.resizeRowsToContents()
	def displayAIConditionTable(self):
		nRows=len(self.monitoredAIConditionList.index);nColumns=len(self.monitoredAIConditionList.columns)+1;self.tbl_manageAIConditions.setRowCount(nRows);self.tbl_manageAIConditions.setColumnCount(nColumns)
		for i in range(self.tbl_manageAIConditions.rowCount()):
			for j in range(self.tbl_manageAIConditions.columnCount()):
				if j==0:chkBoxItem=QtWidgets.QTableWidgetItem();chkBoxItem.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);chkBoxItem.setCheckState(Qt.Unchecked);self.tbl_manageAIConditions.setItem(i,j,chkBoxItem)
				else:x=self.monitoredAIConditionList.iloc[(i,j-1)];self.tbl_manageAIConditions.setItem(i,j,QtWidgets.QTableWidgetItem(str(x)))
		checkbox=self.params[_A][_C][_c];id=self.params[_A][_C][_G];code=self.params[_A][_C][_F];name=self.params[_A][_C][_K];buyType=self.params[_m][_n][_b];buyAmountPerTime=self.params[_A][_C][_o];totalPrice=self.params[_A][_C][_R];startTime=self.params[_A][_C][_S];endTime=self.params[_A][_C][_T];profitRate=self.params[_A][_C][_L];profitQtyPercent=self.params[_A][_C][_U];maxProfitRate=self.params[_A][_C][_M];lossRate=self.params[_A][_C][_N];lossQtyPercent=self.params[_A][_C][_V];maxLossRate=self.params[_A][_C][_O];self.tbl_manageAIConditions.setHorizontalHeaderLabels([checkbox,id,code,name,buyType,totalPrice,buyAmountPerTime,startTime,endTime,profitRate,profitQtyPercent,maxProfitRate,lossRate,lossQtyPercent,maxLossRate])
		for i in range(nColumns):
			if i==0 or i==1:self.tbl_manageAIConditions.setColumnWidth(i,20)
			else:self.tbl_manageAIConditions.setColumnWidth(i,115)
		self.tbl_manageAIConditions.resizeRowsToContents()
	def displayBalanceTable(self):
		nRows=len(self.accountBalanceInfo.index);nColumns=len(self.accountBalanceInfo.columns);self.tbl_totalBalance.setRowCount(nRows);self.tbl_totalBalance.setColumnCount(nColumns)
		for i in range(self.tbl_totalBalance.rowCount()):
			for j in range(self.tbl_totalBalance.columnCount()):x=self.accountBalanceInfo.iloc[(i,j)];self.tbl_totalBalance.setItem(i,j,QtWidgets.QTableWidgetItem(x))
		self.tbl_totalBalance.setHorizontalHeaderLabels(self.accountBalanceInfo.columns)
		for i in range(nColumns):self.tbl_totalBalance.setColumnWidth(i,115)
		self.tbl_totalBalance.resizeRowsToContents()
	def displayPiggleDaoMostVotedTable(self):
		nRows=len(self.monitoredPiggleDaoMostVotedList.index);nColumns=len(self.monitoredPiggleDaoMostVotedList.columns);self.tbl_piggleDaoMostVoted.setRowCount(nRows);self.tbl_piggleDaoMostVoted.setColumnCount(nColumns)
		for i in range(self.tbl_piggleDaoMostVoted.rowCount()):
			for j in range(self.tbl_piggleDaoMostVoted.columnCount()):x=self.monitoredPiggleDaoMostVotedList.iloc[(i,j)];self.tbl_piggleDaoMostVoted.setItem(i,j,QtWidgets.QTableWidgetItem(str(x)))
		self.tbl_piggleDaoMostVoted.setHorizontalHeaderLabels(self.monitoredPiggleDaoMostVotedList.columns)
		for i in range(nColumns):self.tbl_piggleDaoMostVoted.setColumnWidth(i,115)
		self.tbl_piggleDaoMostVoted.resizeRowsToContents()
	def displayChart(self):df=self.calcCurrentChartPageDataFrame();df=self.calcSubIndexChartDataFrame(df);self.drawChart(df);self.setChartPageLabel();self.setChartPrevNextButton()
	def setChartPageLabel(self):self.tv_chartCurrentPage.setText(str(self.currentPage))
	def setChartPrevNextButton(self):
		if self.currentPage==1:self.bt_chartPrev.setDisabled(_I)
		else:self.bt_chartPrev.setEnabled(_I)
		if self.currentPage==self.totalPage:self.bt_chartNext.setDisabled(_I)
		else:self.bt_chartNext.setEnabled(_I)
	def requestChartData(self):code=self.selectedStock.split(_X)[0];now=datetime.datetime.now();time=now.strftime('%Y%m%d');interval=self.selectedCandle.split(' ')[0];type=self.selectedCandle.split(' ')[1];self.totalChartData=self.kiwoomData.request_candle_data(code=code,date=time,nPrevNext=0,type=type,interval=interval);self.totalRow=len(self.totalChartData.index);self.currentStartIndex=0;self.currentEndIndex=60;self.totalPage=int(self.totalRow/60);self.currentPage=self.totalPage;self.tv_chartTotalPage.setText(str(self.totalPage))
	def calcCurrentChartPageDataFrame(self):A='index';df=self.totalChartData[self.totalChartData[A]>=self.currentStartIndex];df=df[df[A]<self.currentEndIndex];return df
	def calcSubIndexChartDataFrame(self,df):
		subIndex=SubIndexData.SubIndexData()
		if len(self.selectedSubIndices)>=1:
			mavg5=self.params[_A][_E]['mavg5'];mavg10=self.params[_A][_E][_p];mavg20=self.params[_A][_E][_q];mavg60=self.params[_A][_E][_r];rsi=self.params[_A][_E][_d];sc=self.params[_A][_E]['sc'];macd=self.params[_A][_E]['macd'];ilmock=self.params[_A][_E][_s];bb=self.params[_A][_E]['bb']
			for i in self.selectedSubIndices:
				if i==rsi:df=subIndex.calc_RSI(df)
				elif i==ilmock:df=subIndex.calc_ichimoku(df)
				elif i==mavg5:df=subIndex.calc_SMA(df,5)
				elif i==mavg10:df=subIndex.calc_SMA(df,10)
				elif i==mavg20:df=subIndex.calc_SMA(df,20)
				elif i==mavg60:df=subIndex.calc_SMA(df,60)
				elif i==sc:df=subIndex.calc_stochastic(df)
				elif i==macd:df=subIndex.calc_MACD(df)
				elif i==bb:df=subIndex.calc_BB(df)
		return df
	def drawChart(self,df):
		K='hour';J='mon';I='sat';H='orange';G='lines';F='green';E='volume';D='lightsteelblue';C='range';B='drawChart';A='date';mavg5=self.params[_A][_E]['mavg5'];mavg10=self.params[_A][_E][_p];mavg20=self.params[_A][_E][_q];mavg60=self.params[_A][_E][_r];rsi=self.params[_A][_E][_d];sc=self.params[_A][_E]['sc'];macd=self.params[_A][_E]['macd'];ilmock=self.params[_A][_E][_s];bb=self.params[_A][_E]['bb'];mavg=self.params[_A][B]['mavg'];volume=self.params[_A][B][C][E];span1=self.params[_A][B][C]['span1'];span2=self.params[_A][B][C]['span2'];stdLine=self.params[_A][B][C]['stdLine'];conversionLine=self.params[_A][B][C]['conversionLine'];highBand=self.params[_A][B][C]['highBand'];midLine=self.params[_A][B][C]['midLine'];lowBand=self.params[_A][B][C]['lowBand'];min=self.params[_A][B][_P]['min'];day=self.params[_A][B][_P]['day'];week=self.params[_A][B][_P]['week'];month=self.params[_A][B][_P]['month'];rows=2
		if rsi in self.selectedSubIndices or sc in self.selectedSubIndices:rows=rows+1
		if macd in self.selectedSubIndices:rows=rows+1
		if rows==2:row_width=[0.2,0.7]
		elif rows==3:row_width=[0.2,0.2,0.7]
		elif rows==4:row_width=[0.2,0.2,0.2,0.7]
		fig=make_subplots(rows=rows,cols=1,shared_xaxes=_I,vertical_spacing=0.03,row_width=row_width);fig.add_trace(go.Candlestick(x=df[A],open=df['open'],high=df['high'],low=df['low'],close=df['close'],showlegend=_W),row=1,col=1);fig.add_trace(go.Bar(x=df[A],y=df[E],name=volume,showlegend=_W),row=2,col=1)
		if len(self.selectedSubIndices)>=1:
			for i in self.selectedSubIndices:
				if i==ilmock:fig.add_trace(go.Scatter(x=df[A],y=df.span_a,fill=_H,line=dict(color='pink',width=1),name=span1),row=1,col=1);fig.add_trace(go.Scatter(x=df[A],y=df.span_b,fill='tonexty',line=dict(color=D,width=1),name=span2),row=1,col=1);fig.add_trace(go.Scatter(x=df[A],y=df.base_line,fill=_H,line=dict(color=F,width=3),name=stdLine),row=1,col=1);fig.add_trace(go.Scatter(x=df[A],y=df.conv_line,fill=_H,line=dict(color='darkorange',width=1),name=conversionLine),row=1,col=1)
				elif mavg in i:lenDays=len(i.split('-')[0]);col=i.split('-')[0][:lenDays]+'sma';fig.add_trace(go.Scatter(x=df[A],y=df[col],mode=G,name=i,showlegend=_I),row=1,col=1)
				elif i==bb:fig.add_trace(go.Scatter(x=df[A],y=df.bb_mavg,fill=_H,line=dict(color='red',width=1),name=highBand),row=1,col=1);fig.add_trace(go.Scatter(x=df[A],y=df.bb_h,fill=_H,line=dict(color=F,width=1),name=midLine),row=1,col=1);fig.add_trace(go.Scatter(x=df[A],y=df.bb_l,fill=_H,line=dict(color='blue',width=1),name=lowBand),row=1,col=1)
				elif i==rsi:fig.add_trace(go.Scatter(x=df[A],y=df[_d],mode=G,name='RSI',showlegend=_I),row=3,col=1)
				elif i==sc:fig.add_trace(go.Scatter(x=df[A],y=df.stoch_k,fill=_H,line=dict(color=D,width=1),name='stoch_k'),row=3,col=1);fig.add_trace(go.Scatter(x=df[A],y=df.stoch_d,fill=_H,line=dict(color=H,width=1),name='stoch_d'),row=3,col=1)
				elif i==macd:
					if rows==4:mac_row=4
					elif rows==3:mac_row=3
					fig.add_trace(go.Scatter(x=df[A],y=df.macd,fill=_H,line=dict(color=D,width=1),name='MACD'),row=mac_row,col=1);fig.add_trace(go.Scatter(x=df[A],y=df.macd_signal,fill=_H,line=dict(color=H,width=1),name='MACD_Signal'),row=mac_row,col=1)
		fig.update(layout_xaxis_rangeslider_visible=_W)
		if min in self.selectedCandle:fig.update_xaxes(rangebreaks=[dict(bounds=[I,J]),dict(bounds=[15.55,9],pattern=K),dict(bounds=[15.32,15.49],pattern=K)])
		else:fig.update_xaxes(rangebreaks=[dict(bounds=[I,J])])
		fig.update_layout(autosize=_I,margin=dict(l=10,r=10,b=10,t=10,pad=2));fig.update_layout(legend=dict(yanchor='top',y=0.99,xanchor='left',x=0.01));self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
	def selectStock(self):self.selectedStock=self.cb_stockList.currentText();selectedStockStr=self.selectedStock.split(_X);self.autoTrading.getRealPriceData(selectedStockStr[0]);self.requestChartData();self.displayChart();self.setFavoriteIcon();self.saveLatestVariables()
	def selectCandle(self):self.selectedCandle=self.cb_candleList.currentText();self.requestChartData();self.displayChart();self.saveLatestVariables()
	def selectSubIndices(self):self.selectedSubIndices=self.cb_subIndexList.currentData();self.requestChartData();self.displayChart();self.saveLatestVariables()
	def clickPrevChart(self):self.currentStartIndex=self.currentStartIndex+60;self.currentEndIndex=self.currentEndIndex+60;self.currentPage=int((self.totalRow-self.currentStartIndex)/60);self.displayChart()
	def clickNextChart(self):self.currentStartIndex=self.currentStartIndex-60;self.currentEndIndex=self.currentEndIndex-60;self.currentPage=int((self.totalRow-self.currentStartIndex)/60);self.displayChart()
	def createLatestVariablesFile(self):code=self.params[_A][_J][_F];candle=self.params[_A][_J][_P];subIndex=self.params[_A][_J][_E];latestList=[code,candle,subIndex];self.dataManager.createCSVFile(_e,latestList)
	def getLatestVariables(self):
		code=self.params[_A][_J][_F];candle=self.params[_A][_J][_P];subIndex=self.params[_A][_J][_E];df=self.dataManager.readCSVFile(_e)
		for (idx,row) in df.iterrows():
			if idx==0:
				self.selectedStock=row[code];self.selectedCandle=row[candle];subString=row[subIndex].replace('[','');subString=subString.replace(']','');subString=subString.replace("'",'');subStringList=subString.split(', ')
				for i in subStringList:self.selectedSubIndices.append(i)
	def saveLatestVariables(self):code=self.params[_A][_J][_F];candle=self.params[_A][_J][_P];subIndex=self.params[_A][_J][_E];df=pd.DataFrame([[self.selectedStock,self.selectedCandle,self.selectedSubIndices]],columns=[code,candle,subIndex]);self.dataManager.updateCSVFile(_e,df)
	def openRegisterCondition(self):
		if len(self.monitoredConditionList)>0:id=self.params[_A][_B][_G];lastConditionId=self.monitoredConditionList[id].iloc[-1]
		else:lastConditionId=0
		regCondi=registerCondition.RegisterCondition(self.dataManager,lastConditionId,self.stockList,self.monitoredConditionList);self.register_subject_condition(regCondi)
	def conditionCheckboxChanged(self,row,column):
		item=self.tbl_manageConditions.item(row,column)
		if self.tbl_manageConditions.item(row,1)!=_H:
			id=int(self.tbl_manageConditions.item(row,1).text());currentState=item.checkState()
			if currentState==Qt.Checked:self.checkedConditionList.append(id)
			elif len(self.checkedConditionList)>0:self.checkedConditionList.remove(id)
	def deleteConditions(self):
		if len(self.checkedConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.removeCondition,self.moreThanOneConditionForDelete,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			dropCodeList=[];id_table=self.params[_A][_B][_G];code=self.params[_A][_B][_F]
			for id in self.checkedConditionList:
				df=self.monitoredConditionList.loc[self.monitoredConditionList[id_table]!=id];dropDf=self.monitoredConditionList.loc[self.monitoredConditionList[id_table]==id]
				for (idx,row) in dropDf.iterrows():dropCodeList.append(row[code])
			self.autoTrading.deleteConditionDf(dropCodeList);self.dataManager.removeRows(_f,df);self.monitoredConditionList=self.getSavedConditionList();self.checkedConditionList.clear();self.displayConditionTable()
	def editCondition(self):
		if len(self.checkedConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.editConditionMsg,self.selectConditionForEdit,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		elif len(self.checkedConditionList)>1:
			choice=QtWidgets.QMessageBox.information(self,self.editConditionMsg,self.onlyOneConditionForEdit,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:id=self.checkedConditionList[0];id_table=self.params[_A][_B][_G];dataRow=self.monitoredConditionList[self.monitoredConditionList[id_table]==id];editCondi=editCondition.EditCondition(self.dataManager,dataRow,self.monitoredConditionList,self.stockList);self.register_subject_condition(editCondi)
	def createConditionFile(self):id=self.params[_A][_B][_G];code=self.params[_A][_B][_F];name=self.params[_A][_B][_K];price=self.params[_A][_B][_Q];totalPrice=self.params[_A][_B][_R];startTime=self.params[_A][_B][_S];endTime=self.params[_A][_B][_T];profitRate=self.params[_A][_B][_L];profitQtyPercent=self.params[_A][_B][_U];maxProfitRate=self.params[_A][_B][_M];lossRate=self.params[_A][_B][_N];lossQtyPercent=self.params[_A][_B][_V];maxLossRate=self.params[_A][_B][_O];conditionHeaderList=[id,code,name,price,totalPrice,startTime,endTime,profitRate,profitQtyPercent,maxProfitRate,lossRate,lossQtyPercent,maxLossRate];self.dataManager.createCSVFile(_f,conditionHeaderList)
	def getSavedConditionList(self):df=self.dataManager.readCSVFile(_f);return df
	def openRegisterKiwoomCondition(self):
		if len(self.monitoredKiwoomConditionList)>0:lastConditionId=self.monitoredKiwoomConditionList['ID'].iloc[-1]
		else:lastConditionId=0
		regCondi=registerConditionKW.RegisterConditionKW(self.dataManager,self.conditionListKW,lastConditionId,self.monitoredKiwoomConditionList);self.register_subject_condition(regCondi)
	def _handler_condition_load(self,ret,msg):print('handler condition load',ret,msg)
	def GetConditionNameList(self):
		data=self.kiwoom.dynamicCall('GetConditionNameList()');conditions=data.split(';')[:-1];self.condition_list=[]
		for condition in conditions:index,name=condition.split('^');self.condition_list.append(index+_X+name)
		return self.condition_list
	def kiwoomConditionCheckboxChanged(self,row,column):
		item=self.tbl_manageKiwoomConditions.item(row,column)
		if self.tbl_manageKiwoomConditions.item(row,1)!=_H:
			id=int(self.tbl_manageKiwoomConditions.item(row,1).text());currentState=item.checkState()
			if currentState==Qt.Checked:self.checkedKiwoomConditionList.append(id)
			elif len(self.checkedKiwoomConditionList)>0:self.checkedKiwoomConditionList.remove(id)
	def deleteKiwoomConditions(self):
		if len(self.checkedKiwoomConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.removeCondition,self.moreThanOneConditionForDelete,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			dropCodeList=[];id_table=self.params[_A][_g][_G];code=self.params[_A][_g][_F]
			for id in self.checkedKiwoomConditionList:
				df=self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList[id_table]!=id];dropDf=self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList[id_table]==id]
				for (idx,row) in dropDf.iterrows():dropCodeList.append(row[code])
			self.autoTrading.deleteKiwoomConditionDf(dropCodeList);self.dataManager.removeRows(_h,df);self.monitoredKiwoomConditionList=self.getSavedKiwoomConditionList();self.checkedKiwoomConditionList.clear();self.displayKiwoomConditionTable()
	def editKiwoomCondition(self):
		if len(self.checkedKiwoomConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.editConditionMsg,self.selectConditionForEdit,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		elif len(self.checkedKiwoomConditionList)>1:
			choice=QtWidgets.QMessageBox.information(self,self.editConditionMsg,self.onlyOneConditionForEdit,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:id=self.checkedKiwoomConditionList[0];id_table=self.params[_A][_g][_G];dataRow=self.monitoredKiwoomConditionList[self.monitoredKiwoomConditionList[id_table]==id];editCondi=editConditionKW.EditConditionKW(self.dataManager,dataRow,self.monitoredKiwoomConditionList,self.conditionListKW);self.register_subject_condition(editCondi)
	def createKiwoomConditionFile(self):id=self.params[_A][_D][_G];code=self.params[_A][_D][_F];name=self.params[_A][_D][_K];totalPrice=self.params[_A][_D][_R];price=self.params[_A][_D][_Q];startTime=self.params[_A][_D][_S];endTime=self.params[_A][_D][_T];profitRate=self.params[_A][_D][_L];profitQtyPercent=self.params[_A][_D][_U];maxProfitRate=self.params[_A][_D][_M];lossRate=self.params[_A][_D][_N];lossQtyPercent=self.params[_A][_D][_V];maxLossRate=self.params[_A][_D][_O];conditionHeaderList=[id,code,name,totalPrice,price,startTime,endTime,profitRate,profitQtyPercent,maxProfitRate,lossRate,lossQtyPercent,maxLossRate];self.dataManager.createCSVFile(_h,conditionHeaderList)
	def getSavedKiwoomConditionList(self):df=self.dataManager.readCSVFile(_h);return df
	def openRegisterAICondition(self):
		if len(self.monitoredAIConditionList)>0:id_table=self.params[_A][_C][_G];lastConditionId=self.monitoredAIConditionList[id_table].iloc[-1]
		else:lastConditionId=0
		regCondi=registerAICondition.RegisterAICondition(self.dataManager,lastConditionId,self.stockList,self.monitoredAIConditionList);self.register_subject_condition(regCondi)
	def aiConditionCheckboxChanged(self,row,column):
		item=self.tbl_manageAIConditions.item(row,column)
		if self.tbl_manageAIConditions.item(row,1)!=_H:
			id=int(self.tbl_manageAIConditions.item(row,1).text());currentState=item.checkState()
			if currentState==Qt.Checked:self.checkedAIConditionList.append(id)
			elif len(self.checkedAIConditionList)>0:self.checkedAIConditionList.remove(id)
	def deleteAIConditions(self):
		if len(self.checkedAIConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.removeCondition,self.moreThanOneConditionForDelete,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			dropCodeList=[];id_table=self.params[_A][_C][_G];code=self.params[_A][_C][_F]
			for id in self.checkedAIConditionList:
				df=self.monitoredAIConditionList.loc[self.monitoredAIConditionList[id_table]!=id];dropDf=self.monitoredAIConditionList.loc[self.monitoredAIConditionList[id_table]==id]
				for (idx,row) in dropDf.iterrows():dropCodeList.append(row[code])
			self.autoTrading.deleteAIConditionDf(dropCodeList);self.dataManager.removeRows(_i,df);self.monitoredAIConditionList=self.getSavedAIConditionList();self.checkedAIConditionList.clear();self.displayAIConditionTable()
	def editAICondition(self):
		if len(self.checkedAIConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.editConditionMsg,self.selectConditionForEdit,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		elif len(self.checkedAIConditionList)>1:
			choice=QtWidgets.QMessageBox.information(self,self.editConditionMsg,self.onlyOneConditionForEdit,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:id=self.checkedAIConditionList[0];id_table=self.params[_A][_C][_G];dataRow=self.monitoredAIConditionList[self.monitoredAIConditionList[id_table]==id];editCondi=editAICondition.EditCondition(self.dataManager,dataRow,self.monitoredAIConditionList,self.stockList);self.register_subject_condition(editCondi)
	def createAIConditionFile(self):id=self.params[_A][_C][_G];code=self.params[_A][_C][_F];name=self.params[_A][_C][_K];buyType=self.params[_m][_n][_b];buyAmountPerTime=self.params[_A][_C][_o];totalPrice=self.params[_A][_C][_R];startTime=self.params[_A][_C][_S];endTime=self.params[_A][_C][_T];profitRate=self.params[_A][_C][_L];profitQtyPercent=self.params[_A][_C][_U];maxProfitRate=self.params[_A][_C][_M];lossRate=self.params[_A][_C][_N];lossQtyPercent=self.params[_A][_C][_V];maxLossRate=self.params[_A][_C][_O];conditionHeaderList=[id,code,name,buyType,buyAmountPerTime,totalPrice,startTime,endTime,profitRate,profitQtyPercent,maxProfitRate,lossRate,lossQtyPercent,maxLossRate];self.dataManager.createCSVFile(_i,conditionHeaderList)
	def getSavedAIConditionList(self):df=self.dataManager.readCSVFile(_i);return df
	def openSettingPiggleDaoMostVoted(self):regSetting=settingPiggleDaoMostVoted.SettingPiggleDaoMostVoted(self.settingPiggleDaoMostVoted);self.register_subject_condition(regSetting)
	def createPiggleDaoMostVotedFile(self):A='createPiggleDaoMostVotedFile';code=self.params[_A][A][_F];name=self.params[_A][A][_K];expectedPrice=self.params[_A][A]['expectedPrice'];priceType=self.params[_A][A]['priceType'];expectedDate=self.params[_A][A]['expectedDate'];conditionHeaderList=[code,name,expectedPrice,priceType,expectedDate];self.dataManager.createCSVFile(_t,conditionHeaderList)
	def getSavedPiggleDaoMostVotedList(self):df=self.dataManager.readCSVFile(_t);return df
	def getPiggleDaoMostVotedScheduler(self):self.scheduler=Scheduler.Scheduler()
	def createSettingPiggleDaoMostVotedFile(self):
		A='createSettingPiggleDaoMostVotedFile';isAppliedVal=self.params[_A][A]['isApplied'];amountVal=self.params[_A][A]['amount'];conditionHeaderList=[isAppliedVal,amountVal];self.dataManager.createCSVFile(_j,conditionHeaderList);isApplied=_I;buyVolume=0;df=self.getSavedSettingPiggleDaoMostVotedList()
		for (idx,row) in df.iterrows():isApplied=row[isAppliedVal];buyVolume=row[amountVal];break
		arr=[isApplied,buyVolume];df=pd.DataFrame([arr],columns=[isAppliedVal,amountVal]);self.dataManager.updateCSVFile(_j,df)
	def getSavedSettingPiggleDaoMostVotedList(self):df=self.dataManager.readCSVFile(_j);return df
	def favoriteButton(self):
		favorite=self.params[_A][_Y][_Z]
		if len(self.favoriteList)>0:
			for (idx,row) in self.favoriteList.iterrows():
				if row[favorite]==self.selectedStock:isFavorite=_I;break
				else:isFavorite=_W
			if isFavorite:self.removeFavorite()
			else:self.addFavorite()
		else:self.addFavorite()
		self.favoriteList=self.getSavedFavoriteList();self.setFavoriteIcon();self.displayFavoriteList()
	def addFavorite(self):favorite=self.params[_A][_Y][_Z];df=pd.DataFrame([self.selectedStock],columns=[favorite]);self.dataManager.appendCSVFile(_a,df)
	def removeFavorite(self):favorite=self.params[_A][_Y][_Z];df=self.favoriteList.loc[self.favoriteList[favorite]!=self.selectedStock];self.dataManager.removeRows(_a,df)
	def createFavoriteFile(self):favorite=self.params[_A][_Y][_Z];favoriteHeader=[favorite];self.dataManager.createCSVFile(_a,favoriteHeader)
	def getSavedFavoriteList(self):df=self.dataManager.readCSVFile(_a);return df
	def stopAllCondition(self):
		self.autoTrading.stopAllCondition();choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.stopAllConditionMsg,QtWidgets.QMessageBox.Ok)
		if choice==QtWidgets.QMessageBox.Ok:0
	def stopSelectedCondition(self):
		if len(self.checkedConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.selectConditionForStop,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			dropCodeList=[];id_table=self.params[_A][_B][_G];code=self.params[_A][_B][_F]
			for id in self.checkedConditionList:
				dropDf=self.monitoredConditionList.loc[self.monitoredConditionList[id_table]==id]
				for (idx,row) in dropDf.iterrows():dropCodeList.append(row[code])
			self.autoTrading.stopSelectedCondition(dropCodeList);choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.stoppedCondition,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
			self.checkedConditionList.clear();self.displayConditionTable()
	def startSelectedCondition(self):
		if len(self.checkedConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.startCondition,self.selectConditionForStart,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			codeList=[];id_table=self.params[_A][_B][_G];code=self.params[_A][_B][_F]
			for id in self.checkedConditionList:
				startDf=self.monitoredConditionList.loc[self.monitoredConditionList[id_table]==id]
				for (idx,row) in startDf.iterrows():codeList.append(row[code])
			self.autoTrading.startSelectedCondition(codeList);choice=QtWidgets.QMessageBox.information(self,self.startCondition,self.startedCondition,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
			self.checkedConditionList.clear();self.displayConditionTable()
	def stopAllKiwoomCondition(self):
		self.autoTrading.stopAllKiwoomCondition();choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.stopAllConditionMsg,QtWidgets.QMessageBox.Ok)
		if choice==QtWidgets.QMessageBox.Ok:0
	def stopSelectedKiwoomCondition(self):
		if len(self.checkedKiwoomConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.selectConditionForStop,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			dropCodeList=[];id_table=self.params[_A][_D][_G];code=self.params[_A][_D][_F]
			for id in self.checkedKiwoomConditionList:
				dropDf=self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList[id_table]==id]
				for (idx,row) in dropDf.iterrows():dropCodeList.append(row[code])
			self.autoTrading.stopSelectedKiwoomCondition(dropCodeList);choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.stoppedCondition,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
			self.checkedKiwoomConditionList.clear();self.displayKiwoomConditionTable()
	def startSelectedKiwoomCondition(self):
		if len(self.checkedKiwoomConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.startCondition,self.selectConditionForStart,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			codeList=[];id_table=self.params[_A][_D][_G];code=self.params[_A][_D][_F]
			for id in self.checkedKiwoomConditionList:
				startDf=self.monitoredKiwoomConditionList.loc[self.monitoredKiwoomConditionList[id_table]==id]
				for (idx,row) in startDf.iterrows():codeList.append(row[code])
			self.autoTrading.startSelectedKiwoomCondition(codeList);choice=QtWidgets.QMessageBox.information(self,self.startCondition,self.startedCondition,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
			self.checkedKiwoomConditionList.clear();self.displayKiwoomConditionTable()
	def stopAllAICondition(self):
		self.autoTrading.stopAllAICondition();choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.stopAllConditionMsg,QtWidgets.QMessageBox.Ok)
		if choice==QtWidgets.QMessageBox.Ok:0
	def stopSelectedAICondition(self):
		if len(self.checkedAIConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.selectConditionForStop,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			dropCodeList=[];id_table=self.params[_A][_C][_G];code=self.params[_A][_C][_F]
			for id in self.checkedAIConditionList:
				dropDf=self.monitoredAIConditionList.loc[self.monitoredAIConditionList[id_table]==id]
				for (idx,row) in dropDf.iterrows():dropCodeList.append(row[code])
			self.autoTrading.stopSelectedAICondition(dropCodeList);choice=QtWidgets.QMessageBox.information(self,self.stopCondition,self.stoppedCondition,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
			self.checkedAIConditionList.clear();self.displayAIConditionTable()
	def startSelectedAICondition(self):
		if len(self.checkedAIConditionList)==0:
			choice=QtWidgets.QMessageBox.information(self,self.startCondition,self.selectConditionForStart,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
		else:
			codeList=[];id_table=self.params[_A][_C][_G];code=self.params[_A][_C][_F]
			for id in self.checkedAIConditionList:
				startDf=self.monitoredAIConditionList.loc[self.monitoredAIConditionList[id_table]==id]
				for (idx,row) in startDf.iterrows():codeList.append(row[code])
			self.autoTrading.startSelectedAICondition(codeList);choice=QtWidgets.QMessageBox.information(self,self.startCondition,self.startedCondition,QtWidgets.QMessageBox.Ok)
			if choice==QtWidgets.QMessageBox.Ok:0
			self.checkedAIConditionList.clear();self.displayAIConditionTable()
	def closeEvent(self,event):self.saveLatestVariables()
	def updateAccountTable(self):self.accountBalanceInfo=self.kiwoomData.get_account_evaluation_balance();self.displayBalanceTable()
	def updatePiggleDaoMostVotedTable(self):self.scheduler.job();self.monitoredPiggleDaoMostVotedList=self.getSavedPiggleDaoMostVotedList();self.displayPiggleDaoMostVotedTable()
class InstallAPIWindow(QMainWindow):
	def __init__(self):
		super().__init__();installKWAPI=self.msg['installKWAPI'];restartAfterKWAPI=self.msg['restartAfterKWAPI'];choice=QtWidgets.QMessageBox.information(self,installKWAPI,restartAfterKWAPI,QtWidgets.QMessageBox.Ok)
		if choice==QtWidgets.QMessageBox.Ok:0