_L='maxLossRate'
_K='lossQtyPercent'
_J='lossRate'
_I='maxProfitRate'
_H='profitQtyPercent'
_G='profitRate'
_F='endTime'
_E='startTime'
_D='totalPrice'
_C='displayConditionTable'
_B='displayKiwoomConditionTable'
_A='mainWindow'
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import pandas as pd
from datetime import datetime
import interface.conditionRegistration as ConditionRegistration,interface.codeSearch as codeSearch,searchCode,openJson
class EditConditionKW(QtWidgets.QDialog,ConditionRegistration.Subject):
	def __init__(A,dataManager,rows,conditionDataFrame,conditionList):
		D='%H:%M';C='button';super().__init__();A.msg,A.params=openJson.getJsonFiles();E=A.params[_A][_B]['id'];F=A.params[_A][_C]['code'];G=A.params[_A][_B]['name'];H=A.params[_A][_B][_D];I=A.params[_A][_B]['price'];J=A.params[_A][_B][_E];K=A.params[_A][_B][_F];L=A.params[_A][_B][_G];M=A.params[_A][_B][_H];N=A.params[_A][_B][_I];O=A.params[_A][_B][_J];P=A.params[_A][_B][_K];Q=A.params[_A][_B][_L];A.conditionList=conditionList;A.conditionDataFrame=conditionDataFrame;A.registerConditionDialog=uic.loadUi('register_kiwoom_condition.ui',A);A.cb_conditionList.addItems(A.conditionList);R=A.msg[C]['confirm'];S=A.msg[C]['cancel'];A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).setText(R);A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).setText(S);A.et_profitRate.setPrefix('+ ');A.et_maxProfitRate.setPrefix('+ ');A.et_lossRate.setPrefix('- ');A.et_maxLossRate.setPrefix('- ')
		for (h,B) in rows.iterrows():A.id=B[E];A.originIdx=B[F];T=B[G];U=str(str(A.originIdx)+' : '+T);V=B[I];W=B[H];X=B[J];Y=datetime.strptime(X,D).time();Z=B[K];a=datetime.strptime(Z,D).time();b=B[L];c=B[M];d=B[N];e=B[O]*-1;f=B[P];g=B[Q]*-1;A.cb_conditionList.setCurrentIndex(A.conditionList.index(U));A.et_buyAmountPerCode.setValue(V);A.et_totalBuyAmount.setValue(W);A.et_buyStartTime.setTime(Y);A.et_buyEndTime.setTime(a);A.et_profitRate.setValue(b);A.et_profitRateVolume.setValue(c);A.et_maxProfitRate.setValue(d);A.et_lossRate.setValue(e);A.et_lossRateVolume.setValue(f);A.et_maxLossRate.setValue(g)
		A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(A.closeWindow);A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda:A.saveCondition(dataManager));A.registerConditionDialog.show()
	def closeWindow(A):A.close()
	def saveCondition(A,dataManager):
		P='HH:mm';G=False;Q=A.params[_A][_B]['id'];H=A.params[_A][_C]['code'];R=A.params[_A][_B]['name'];S=A.params[_A][_B][_D];T=A.params[_A][_B]['price'];U=A.params[_A][_B][_E];V=A.params[_A][_B][_F];W=A.params[_A][_B][_G];X=A.params[_A][_B][_H];Y=A.params[_A][_B][_I];Z=A.params[_A][_B][_J];a=A.params[_A][_B][_K];b=A.params[_A][_B][_L];A.saveCondition=A.msg['saveCondition'];A.selectCondiCode=A.msg['selectCondiCode'];A.alreadyRegisteredCondition=A.msg['alreadyRegisteredCondition'];A.noZeroForBuyPricePerStock=A.msg['noZeroForBuyPricePerStock'];A.notZeroForTotalBuyPrice=A.msg['notZeroForTotalBuyPrice'];A.endLaterThanStart=A.msg['endLaterThanStart'];A.maxMoreThanProfit=A.msg['maxMoreThanProfit'];A.maxMoreThanLoss=A.msg['maxMoreThanLoss'];id=A.id;I=A.cb_conditionList.currentText().split(' : ');E=str(I[0]);c=I[1];J=A.et_totalBuyAmount.value();K=A.et_buyAmountPerCode.value();d=A.et_buyStartTime.dateTime().toString(P);e=A.et_buyEndTime.dateTime().toString(P);L=A.et_profitRate.value();f=A.et_profitRateVolume.value();M=A.et_maxProfitRate.value();N=A.et_lossRate.value()*-1;g=A.et_lossRateVolume.value();O=A.et_maxLossRate.value()*-1;D=G
		for (B,F) in A.conditionDataFrame.iterrows():
			if F[H]==E:
				if E==A.originIdx:D=G
				else:D=True
			else:D=G
		if A.cb_conditionList.currentText()=='':
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.selectCondiCode,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif D:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.alreadyRegisteredCondition,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif K==0:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.noZeroForBuyPricePerStock,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif J==0:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForTotalBuyPrice,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif A.et_buyStartTime.dateTime()>A.et_buyEndTime.dateTime():
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.endLaterThanStart,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif L>=M:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanProfit,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		elif O>=N:
			C=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanLoss,QtWidgets.QMessageBox.Ok)
			if C==QtWidgets.QMessageBox.Ok:0
		else:
			for (B,F) in A.conditionDataFrame.iterrows():
				if F[Q]==id:A.conditionDataFrame.at[(B,H)]=E;A.conditionDataFrame.at[(B,R)]=c;A.conditionDataFrame.at[(B,S)]=J;A.conditionDataFrame.at[(B,T)]=K;A.conditionDataFrame.at[(B,U)]=d;A.conditionDataFrame.at[(B,V)]=e;A.conditionDataFrame.at[(B,W)]=L;A.conditionDataFrame.at[(B,X)]=f;A.conditionDataFrame.at[(B,Y)]=M;A.conditionDataFrame.at[(B,Z)]=N;A.conditionDataFrame.at[(B,a)]=g;A.conditionDataFrame.at[(B,b)]=O;dataManager.updateCSVFile('pats_kiwoom_condition.csv',A.conditionDataFrame);A.notify_observers_condition(A.conditionDataFrame);A.close()
	def register_observer_condition(A,observer):A.observer=observer
	def notify_observers_condition(A,condition):A.observer.update_condition('editKW',condition)