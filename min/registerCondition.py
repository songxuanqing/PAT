from PyQt5 import QtWidgets,uic,QtGui,QtCore
import pandas as pd,interface.conditionRegistration as ConditionRegistration,interface.codeSearch as codeSearch,searchCode,openJson
class RegisterCondition(QtWidgets.QDialog,ConditionRegistration.Subject,codeSearch.Observer):
	def __init__(A,dataManager,lastCondtiontionId,stockList,monitoredConditionList):B='button';super().__init__();A.msg,A.params=openJson.getJsonFiles();A.stockList=stockList;A.monitoredConditionList=monitoredConditionList;A.lastCondtiontionId=lastCondtiontionId;A.registerConditionDialog=uic.loadUi('register_dao_condition.ui',A);A.bt_searchCode.clicked.connect(A.clickSearch);C=A.msg[B]['confirm'];D=A.msg[B]['cancel'];A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(C);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(D);E=QtCore.QRegExp('[0-9_]+');F=QtGui.QRegExpValidator(E);A.et_code.setValidator(F);A.et_profitRate.setPrefix('+ ');A.et_maxProfitRate.setPrefix('+ ');A.et_lossRate.setPrefix('- ');A.et_maxLossRate.setPrefix('- ');A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(A.closeWindow);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda:A.saveCondition(dataManager));A.registerConditionDialog.show()
	def closeWindow(A):A.close()
	def saveCondition(A,dataManager):
		P=False;O='HH:mm';D='displayConditionTable';C='mainWindow';Q=A.params[C][D]['id'];G=A.params[C][D]['code'];R=A.params[C][D]['name'];S=A.params[C][D]['price'];T=A.params[C][D]['totalPrice'];U=A.params[C][D]['startTime'];V=A.params[C][D]['endTime'];W=A.params[C][D]['profitRate'];X=A.params[C][D]['profitQtyPercent'];Y=A.params[C][D]['maxProfitRate'];Z=A.params[C][D]['lossRate'];a=A.params[C][D]['lossQtyPercent'];b=A.params[C][D]['maxLossRate'];A.saveCondition=A.msg['saveCondition'];A.nullCode=A.msg['nullCode'];A.alreadyRegistered=A.msg['alreadyRegistered'];A.notZeroForBuyPrice=A.msg['notZeroForBuyPrice'];A.notZeroForTotalBuyPrice=A.msg['notZeroForTotalBuyPrice'];A.endLaterThanStart=A.msg['endLaterThanStart'];A.maxMoreThanProfit=A.msg['maxMoreThanProfit'];A.maxMoreThanLoss=A.msg['maxMoreThanLoss'];id=A.lastCondtiontionId+1;E=A.et_code.text();c=A.tv_codeName.text();H=A.et_buyPrice.value();I=A.et_totalBuyAmount.value();d=A.et_buyStartTime.dateTime().toString(O);e=A.et_buyEndTime.dateTime().toString(O);J=A.et_profitRate.value();f=A.et_profitRateVolume.value();K=A.et_maxProfitRate.value();L=A.et_lossRate.value()*-1;g=A.et_lossRateVolume.value();M=A.et_maxLossRate.value()*-1;F=P
		for (j,h) in A.monitoredConditionList.iterrows():
			if h[G]==E:F=True
			else:F=P
		if E=='':
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.nullCode,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif F:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.alreadyRegistered,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif H==0:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForBuyPrice,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif I==0:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForTotalBuyPrice,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif A.et_buyStartTime.dateTime()>A.et_buyEndTime.dateTime():
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.endLaterThanStart,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif J>=K:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanProfit,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif M>=L:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanLoss,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		else:i=[id,str(E),c,H,I,d,e,J,f,K,L,g,M];N=pd.DataFrame([i],columns=[Q,G,R,S,T,U,V,W,X,Y,Z,a,b]);dataManager.appendCSVFile('pats_condition.csv',N);A.notify_observers_condition(N);A.closeWindow()
	def clickSearch(A):B=A.et_code.text();C=searchCode.SearchCode(B,A.stockList);A.register_subject_searchCode(C)
	def update_searchCode(A,code,name):A.et_code.setText(code);A.tv_codeName.setText(name)
	def register_subject_searchCode(A,subject):A.subject=subject;A.subject.register_observer_searchCode(A)
	def register_observer_condition(A,observer):A.observer=observer
	def notify_observers_condition(A,conditionDf):A.observer.update_condition('register',conditionDf)