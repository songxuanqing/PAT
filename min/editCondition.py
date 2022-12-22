_K='maxLossRate'
_J='lossQtyPercent'
_I='lossRate'
_H='maxProfitRate'
_G='profitQtyPercent'
_F='profitRate'
_E='endTime'
_D='startTime'
_C='totalPrice'
_B='displayConditionTable'
_A='mainWindow'
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import pandas as pd
from datetime import datetime
import interface.conditionRegistration as ConditionRegistration,interface.codeSearch as codeSearch,searchCode,openJson
class EditCondition(QtWidgets.QDialog,ConditionRegistration.Subject,codeSearch.Observer):
	def __init__(A,dataManager,rows,conditionDataFrame,stockList):
		D='%H:%M';C='button';super().__init__();A.msg,A.params=openJson.getJsonFiles();E=A.params[_A][_B]['id'];F=A.params[_A][_B]['code'];G=A.params[_A][_B]['name'];H=A.params[_A][_B]['price'];I=A.params[_A][_B][_C];J=A.params[_A][_B][_D];K=A.params[_A][_B][_E];L=A.params[_A][_B][_F];M=A.params[_A][_B][_G];N=A.params[_A][_B][_H];O=A.params[_A][_B][_I];P=A.params[_A][_B][_J];Q=A.params[_A][_B][_K];A.conditionDataFrame=conditionDataFrame;A.stockList=stockList;A.registerConditionDialog=uic.loadUi('register_dao_condition.ui',A);A.bt_searchCode.clicked.connect(A.clickSearch);R=A.msg[C]['confirm'];S=A.msg[C]['cancel'];A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(R);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(S);T=QtCore.QRegExp('[0-9_]+');U=QtGui.QRegExpValidator(T);A.et_code.setValidator(U);A.et_profitRate.setPrefix('+ ');A.et_maxProfitRate.setPrefix('+ ');A.et_lossRate.setPrefix('- ');A.et_maxLossRate.setPrefix('- ')
		for (i,B) in rows.iterrows():A.id=B[E];A.originStockCode=B[F];V=B[G];W=B[H];X=B[I];Y=B[J];Z=datetime.strptime(Y,D).time();a=B[K];b=datetime.strptime(a,D).time();c=B[L];d=B[M];e=B[N];f=B[O]*-1;g=B[P];h=B[Q]*-1;A.et_code.setText(A.originStockCode);A.tv_codeName.setText(V);A.et_buyPrice.setValue(W);A.et_totalBuyAmount.setValue(X);A.et_buyStartTime.setTime(Z);A.et_buyEndTime.setTime(b);A.et_profitRate.setValue(c);A.et_profitRateVolume.setValue(d);A.et_maxProfitRate.setValue(e);A.et_lossRate.setValue(f);A.et_lossRateVolume.setValue(g);A.et_maxLossRate.setValue(h)
		A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(A.closeWindow);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda:A.saveCondition(dataManager));A.registerConditionDialog.show()
	def closeWindow(A):A.close()
	def saveCondition(A,dataManager):
		O='HH:mm';G=False;P=A.params[_A][_B]['id'];H=A.params[_A][_B]['code'];Q=A.params[_A][_B]['name'];R=A.params[_A][_B]['price'];S=A.params[_A][_B][_C];T=A.params[_A][_B][_D];U=A.params[_A][_B][_E];V=A.params[_A][_B][_F];W=A.params[_A][_B][_G];X=A.params[_A][_B][_H];Y=A.params[_A][_B][_I];Z=A.params[_A][_B][_J];a=A.params[_A][_B][_K];A.saveCondition=A.msg['saveCondition'];A.nullCode=A.msg['nullCode'];A.alreadyRegistered=A.msg['alreadyRegistered'];A.notZeroForBuyPrice=A.msg['notZeroForBuyPrice'];A.notZeroForTotalBuyPrice=A.msg['notZeroForTotalBuyPrice'];A.endLaterThanStart=A.msg['endLaterThanStart'];A.maxMoreThanProfit=A.msg['maxMoreThanProfit'];A.maxMoreThanLoss=A.msg['maxMoreThanLoss'];id=A.id;D=A.et_code.text();b=A.tv_codeName.text();I=A.et_buyPrice.value();J=A.et_totalBuyAmount.value();c=A.et_buyStartTime.dateTime().toString(O);d=A.et_buyEndTime.dateTime().toString(O);K=A.et_profitRate.value();e=A.et_profitRateVolume.value();L=A.et_maxProfitRate.value();M=A.et_lossRate.value()*-1;f=A.et_lossRateVolume.value();N=A.et_maxLossRate.value()*-1;E=G
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
				if F[P]==id:A.conditionDataFrame.at[(B,H)]=str(D);A.conditionDataFrame.at[(B,Q)]=b;A.conditionDataFrame.at[(B,R)]=I;A.conditionDataFrame.at[(B,S)]=J;A.conditionDataFrame.at[(B,T)]=c;A.conditionDataFrame.at[(B,U)]=d;A.conditionDataFrame.at[(B,V)]=K;A.conditionDataFrame.at[(B,W)]=e;A.conditionDataFrame.at[(B,X)]=L;A.conditionDataFrame.at[(B,Y)]=M;A.conditionDataFrame.at[(B,Z)]=f;A.conditionDataFrame.at[(B,a)]=N;dataManager.updateCSVFile('pats_condition.csv',A.conditionDataFrame);A.notify_observers_condition(A.conditionDataFrame);A.closeWindow()
	def clickSearch(A):B=A.et_code.text();C=searchCode.SearchCode(B,A.stockList);A.register_subject_searchCode(C)
	def update_searchCode(A,code,name):A.et_code.setText(code);A.tv_codeName.setText(name)
	def register_subject_searchCode(A,subject):A.subject=subject;A.subject.register_observer_searchCode(A)
	def register_observer_condition(A,observer):A.observer=observer
	def notify_observers_condition(A,condition):A.observer.update_condition('edit',condition)