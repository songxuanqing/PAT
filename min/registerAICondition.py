_B='AIConditionList'
_A='kiwoomRealTimeData'
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import pandas as pd,interface.conditionRegistration as ConditionRegistration,interface.codeSearch as codeSearch,searchCode,openJson
class RegisterAICondition(QtWidgets.QDialog,ConditionRegistration.Subject,codeSearch.Observer):
	def __init__(A,dataManager,lastCondtiontionId,stockList,monitoredConditionList):B='button';super().__init__();A.msg,A.params=openJson.getJsonFiles();C=A.params[_A][_B]['dayBuy'];D=A.params[_A][_B]['minBuy'];A.stockList=stockList;A.monitoredConditionList=monitoredConditionList;A.lastCondtiontionId=lastCondtiontionId;A.registerConditionDialog=uic.loadUi('register_ai_condition.ui',A);A.bt_searchCode.clicked.connect(A.clickSearch);E=[C,D];A.cb_dayMin.addItems(E);F=A.msg[B]['confirm'];G=A.msg[B]['cancel'];A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(F);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(G);H=QtCore.QRegExp('[0-9_]+');I=QtGui.QRegExpValidator(H);A.et_code.setValidator(I);A.et_profitRate.setPrefix('+ ');A.et_maxProfitRate.setPrefix('+ ');A.et_lossRate.setPrefix('- ');A.et_maxLossRate.setPrefix('- ');A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(A.closeWindow);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda:A.saveCondition(dataManager));A.registerConditionDialog.show()
	def closeWindow(A):A.close()
	def saveCondition(A,dataManager):
		O=False;N='HH:mm';D='displayAIConditionTable';C='mainWindow';P=A.params[C][D]['id'];G=A.params[C][D]['code'];Q=A.params[C][D]['name'];R=A.params[_A][_B]['type'];S=A.params[C][D]['buyAmountPerTime'];T=A.params[C][D]['totalPrice'];U=A.params[C][D]['startTime'];V=A.params[C][D]['endTime'];W=A.params[C][D]['profitRate'];X=A.params[C][D]['profitQtyPercent'];Y=A.params[C][D]['maxProfitRate'];Z=A.params[C][D]['lossRate'];a=A.params[C][D]['lossQtyPercent'];b=A.params[C][D]['maxLossRate'];A.saveCondition=A.msg['saveCondition'];A.nullCode=A.msg['nullCode'];A.alreadyRegistered=A.msg['alreadyRegistered'];A.notZeroForBuyPrice=A.msg['notZeroForBuyPrice'];A.notZeroForTotalBuyPrice=A.msg['notZeroForTotalBuyPrice'];A.endLaterThanStart=A.msg['endLaterThanStart'];A.maxMoreThanProfit=A.msg['maxMoreThanProfit'];A.maxMoreThanLoss=A.msg['maxMoreThanLoss'];id=A.lastCondtiontionId+1;E=A.et_code.text();c=A.tv_codeName.text();d=A.cb_dayMin.currentText();e=A.et_totalBuyAmountPerTime.value();H=A.et_totalBuyAmount.value();f=A.et_buyStartTime.dateTime().toString(N);g=A.et_buyEndTime.dateTime().toString(N);I=A.et_profitRate.value();h=A.et_profitRateVolume.value();J=A.et_maxProfitRate.value();K=A.et_lossRate.value()*-1;i=A.et_lossRateVolume.value();L=A.et_maxLossRate.value()*-1;F=O
		for (l,j) in A.monitoredConditionList.iterrows():
			if j[G]==E:F=True
			else:F=O
		if E=='':
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.nullCode,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif F:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.alreadyRegistered,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif buyPrice==0:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForBuyPrice,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif H==0:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForTotalBuyPrice,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif A.et_buyStartTime.dateTime()>A.et_buyEndTime.dateTime():
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.endLaterThanStart,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif I>=J:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanProfit,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif L>=K:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanLoss,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		else:k=[id,str(E),c,d,e,H,f,g,I,h,J,K,i,L];M=pd.DataFrame([k],columns=[P,G,Q,R,S,T,U,V,W,X,Y,Z,a,b]);dataManager.appendCSVFile('pats_ai_condition.csv',M);A.notify_observers_condition(M);A.closeWindow()
	def clickSearch(A):B=A.et_code.text();C=searchCode.SearchCode(B,A.stockList);A.register_subject_searchCode(C)
	def update_searchCode(A,code,name):A.et_code.setText(code);A.tv_codeName.setText(name)
	def register_subject_searchCode(A,subject):A.subject=subject;A.subject.register_observer_searchCode(A)
	def register_observer_condition(A,observer):A.observer=observer
	def notify_observers_condition(A,conditionDf):A.observer.update_condition('registerAI',conditionDf)