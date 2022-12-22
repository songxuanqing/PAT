_N='maxLossRate'
_M='lossQtyPercent'
_L='lossRate'
_K='maxProfitRate'
_J='profitQtyPercent'
_I='profitRate'
_H='endTime'
_G='startTime'
_F='totalPrice'
_E='buyAmountPerTime'
_D='AIConditionList'
_C='kiwoomRealTimeData'
_B='displayAIConditionTable'
_A='mainWindow'
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import pandas as pd
from datetime import datetime
import interface.conditionRegistration as ConditionRegistration,interface.codeSearch as codeSearch,searchCode,openJson
class EditCondition(QtWidgets.QDialog,ConditionRegistration.Subject,codeSearch.Observer):
	def __init__(A,dataManager,rows,conditionDataFrame,stockList):
		D='%H:%M';C='button';super().__init__();A.msg,A.params=openJson.getJsonFiles();E=A.params[_C][_D]['dayBuy'];F=A.params[_C][_D]['minBuy'];G=A.params[_A][_B]['id'];H=A.params[_A][_B]['code'];I=A.params[_A][_B]['name'];J=A.params[_C][_D]['type'];K=A.params[_A][_B][_E];L=A.params[_A][_B][_F];M=A.params[_A][_B][_G];N=A.params[_A][_B][_H];O=A.params[_A][_B][_I];P=A.params[_A][_B][_J];Q=A.params[_A][_B][_K];R=A.params[_A][_B][_L];S=A.params[_A][_B][_M];T=A.params[_A][_B][_N];A.conditionDataFrame=conditionDataFrame;A.stockList=stockList;A.registerConditionDialog=uic.loadUi('register_ai_condition.ui',A);A.bt_searchCode.clicked.connect(A.clickSearch);A.typeList=[E,F];A.cb_dayMin.addItems(A.typeList);U=A.msg[C]['confirm'];V=A.msg[C]['cancel'];A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(U);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(V);W=QtCore.QRegExp('[0-9_]+');X=QtGui.QRegExpValidator(W);A.et_code.setValidator(X);A.et_profitRate.setPrefix('+ ');A.et_maxProfitRate.setPrefix('+ ');A.et_lossRate.setPrefix('- ');A.et_maxLossRate.setPrefix('- ')
		for (m,B) in rows.iterrows():A.id=B[G];A.originStockCode=B[H];Y=B[I];Z=B[J];a=B[K];b=B[L];c=B[M];d=datetime.strptime(c,D).time();e=B[N];f=datetime.strptime(e,D).time();g=B[O];h=B[P];i=B[Q];j=B[R]*-1;k=B[S];l=B[T]*-1;A.et_code.setText(A.originStockCode);A.tv_codeName.setText(Y);A.cb_dayMin.setCurrentIndex(A.typeList.index(Z));A.et_totalBuyAmountPerTime.setValue(a);A.et_totalBuyAmount.setValue(b);A.et_buyStartTime.setTime(d);A.et_buyEndTime.setTime(f);A.et_profitRate.setValue(g);A.et_profitRateVolume.setValue(h);A.et_maxProfitRate.setValue(i);A.et_lossRate.setValue(j);A.et_lossRateVolume.setValue(k);A.et_maxLossRate.setValue(l)
		A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(A.closeWindow);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda:A.saveCondition(dataManager));A.registerConditionDialog.show()
	def closeWindow(A):A.close()
	def saveCondition(A,dataManager):
		O='HH:mm';G=False;P=A.params[_A][_B]['id'];H=A.params[_A][_B]['code'];Q=A.params[_A][_B]['name'];R=A.params[_C][_D]['type'];S=A.params[_A][_B][_E];T=A.params[_A][_B][_F];U=A.params[_A][_B][_G];V=A.params[_A][_B][_H];W=A.params[_A][_B][_I];X=A.params[_A][_B][_J];Y=A.params[_A][_B][_K];Z=A.params[_A][_B][_L];a=A.params[_A][_B][_M];b=A.params[_A][_B][_N];A.saveCondition=A.msg['saveCondition'];A.nullCode=A.msg['nullCode'];A.alreadyRegistered=A.msg['alreadyRegistered'];A.notZeroForBuyPrice=A.msg['notZeroForBuyPrice'];A.notZeroForTotalBuyPrice=A.msg['notZeroForTotalBuyPrice'];A.endLaterThanStart=A.msg['endLaterThanStart'];A.maxMoreThanProfit=A.msg['maxMoreThanProfit'];A.maxMoreThanLoss=A.msg['maxMoreThanLoss'];id=A.id;D=A.et_code.text();c=A.tv_codeName.text();d=A.cb_dayMin.currentText();I=A.et_totalBuyAmountPerTime.value();J=A.et_totalBuyAmount.value();e=A.et_buyStartTime.dateTime().toString(O);f=A.et_buyEndTime.dateTime().toString(O);K=A.et_profitRate.value();g=A.et_profitRateVolume.value();L=A.et_maxProfitRate.value();M=A.et_lossRate.value()*-1;h=A.et_lossRateVolume.value();N=A.et_maxLossRate.value()*-1;E=G
		for (B,F) in A.conditionDataFrame.iterrows():
			if F[H]==D:
				if D==A.originStockCode:E=G
				else:E=True
			else:E=G
		if D=='':
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.nullCode,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif E:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.alreadyRegistered,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif I==0:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForBuyPrice,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif J==0:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForTotalBuyPrice,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif A.et_buyStartTime.dateTime()>A.et_buyEndTime.dateTime():
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.endLaterThanStart,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif K>=L:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanProfit,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif N>=M:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanLoss,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		else:
			for (B,F) in A.conditionDataFrame.iterrows():
				if F[P]==id:A.conditionDataFrame.at[(B,H)]=str(D);A.conditionDataFrame.at[(B,Q)]=c;A.conditionDataFrame.at[(B,R)]=d;A.conditionDataFrame.at[(B,S)]=I;A.conditionDataFrame.at[(B,T)]=J;A.conditionDataFrame.at[(B,U)]=e;A.conditionDataFrame.at[(B,V)]=f;A.conditionDataFrame.at[(B,W)]=K;A.conditionDataFrame.at[(B,X)]=g;A.conditionDataFrame.at[(B,Y)]=L;A.conditionDataFrame.at[(B,Z)]=M;A.conditionDataFrame.at[(B,a)]=h;A.conditionDataFrame.at[(B,b)]=N;dataManager.updateCSVFile('pats_ai_condition.csv',A.conditionDataFrame);A.notify_observers_condition(A.conditionDataFrame);A.closeWindow()
	def clickSearch(A):B=A.et_code.text();C=searchCode.SearchCode(B,A.stockList);A.register_subject_searchCode(C)
	def update_searchCode(A,code,name):A.et_code.setText(code);A.tv_codeName.setText(name)
	def register_subject_searchCode(A,subject):A.subject=subject;A.subject.register_observer_searchCode(A)
	def register_observer_condition(A,observer):A.observer=observer
	def notify_observers_condition(A,condition):A.observer.update_condition('editAI',condition)