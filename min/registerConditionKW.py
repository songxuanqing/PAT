from PyQt5 import QtWidgets,uic,QtGui,QtCore
import pandas as pd,interface.conditionRegistration as ConditionRegistration
class RegisterConditionKW(QtWidgets.QDialog,ConditionRegistration.Subject):
	def __init__(A,dataManager,conditionList,lastCondtiontionId,monitoredConditionList):B='button';super().__init__();A.conditionList=conditionList;A.monitoredConditionList=monitoredConditionList;A.lastConditionId=lastCondtiontionId;A.registerConditionDialog=uic.loadUi('register_kiwoom_condition.ui',A);A.cb_conditionList.addItems(A.conditionList);C=A.msg[B]['confirm'];D=A.msg[B]['cancel'];A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).setText(C);A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).setText(D);A.et_profitRate.setPrefix('+ ');A.et_maxProfitRate.setPrefix('+ ');A.et_lossRate.setPrefix('- ');A.et_maxLossRate.setPrefix('- ');A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(A.closeWindow);A.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda:A.saveCondition(dataManager));A.registerConditionDialog.show()
	def closeWindow(A):A.close()
	def saveCondition(A,dataManager):
		Q=False;P='HH:mm';D='displayKiwoomConditionTable';C='mainWindow';R=A.params[C][D]['id'];F=A.params[C]['displayConditionTable']['code'];S=A.params[C][D]['name'];T=A.params[C][D]['totalPrice'];U=A.params[C][D]['price'];V=A.params[C][D]['startTime'];W=A.params[C][D]['endTime'];X=A.params[C][D]['profitRate'];Y=A.params[C][D]['profitQtyPercent'];Z=A.params[C][D]['maxProfitRate'];a=A.params[C][D]['lossRate'];b=A.params[C][D]['lossQtyPercent'];c=A.params[C][D]['maxLossRate'];A.saveCondition=A.msg['saveCondition'];A.selectCondiCode=A.msg['selectCondiCode'];A.alreadyRegisteredCondition=A.msg['alreadyRegisteredCondition'];A.noZeroForBuyPricePerStock=A.msg['noZeroForBuyPricePerStock'];A.notZeroForTotalBuyPrice=A.msg['notZeroForTotalBuyPrice'];A.endLaterThanStart=A.msg['endLaterThanStart'];A.maxMoreThanProfit=A.msg['maxMoreThanProfit'];A.maxMoreThanLoss=A.msg['maxMoreThanLoss'];id=A.lastConditionId+1;G=A.cb_conditionList.currentText().split(' : ');H=str(G[0]);d=G[1];I=A.et_totalBuyAmount.value();J=A.et_buyAmountPerCode.value();e=A.et_buyStartTime.dateTime().toString(P);f=A.et_buyEndTime.dateTime().toString(P);K=A.et_profitRate.value();g=A.et_profitRateVolume.value();L=A.et_maxProfitRate.value();M=A.et_lossRate.value()*-1;h=A.et_lossRateVolume.value();N=A.et_maxLossRate.value()*-1;E=Q
		for (k,i) in A.monitoredConditionList.iterrows():
			if i[F]==H:E=True
			else:E=Q
		if A.cb_conditionList.currentText()=='':
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.selectCondiCode,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif E:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.alreadyRegisteredCondition,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif J==0:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.noZeroForBuyPricePerStock,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif I==0:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.notZeroForTotalBuyPrice,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif A.et_buyStartTime.dateTime()>A.et_buyEndTime.dateTime():
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.endLaterThanStart,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif K>=L:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanProfit,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		elif N>=M:
			B=QtWidgets.QMessageBox.information(A,A.saveCondition,A.maxMoreThanLoss,QtWidgets.QMessageBox.Ok)
			if B==QtWidgets.QMessageBox.Ok:0
		else:j=[id,H,d,I,J,e,f,K,g,L,M,h,N];O=pd.DataFrame([j],columns=[R,F,S,T,U,V,W,X,Y,Z,a,b,c]);dataManager.appendCSVFile('pats_kiwoom_condition.csv',O);A.notify_observers_condition(O);A.close()
	def register_observer_condition(A,observer):A.observer=observer
	def notify_observers_condition(A,conditionDf):A.observer.update_condition('registerKW',conditionDf)