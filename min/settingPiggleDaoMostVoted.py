_E='amount'
_D='isApplied'
_C=True
_B='createSettingPiggleDaoMostVotedFile'
_A='mainWindow'
from PyQt5 import QtWidgets,uic
import pandas as pd,interface.conditionRegistration as ConditionRegistration,models.database as DataManager,openJson
class SettingPiggleDaoMostVoted(QtWidgets.QDialog,ConditionRegistration.Subject):
	def __init__(A,settingPiggleDaoMostVoted):
		D='button';super().__init__();A.msg,A.params=openJson.getJsonFiles();B=A.params[_A][_B][_D];I=A.params[_A][_B][_E];A.settingDialog=uic.loadUi('setting_piggle_dao_most_voted.ui',A)
		for (J,C) in settingPiggleDaoMostVoted.iterrows():
			E=C[B];F=C[B]
			if E:A.rbt_apply.setChecked(_C)
			else:A.rbt_noApply.setChecked(_C)
			A.et_buyVolume.setValue(F)
		G=A.msg[D]['confirm'];H=A.msg[D]['cancel'];A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(G);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(H);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(A.closeWindow);A.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(A.saveCondition);A.settingDialog.show()
	def closeWindow(A):A.close()
	def saveCondition(A):
		D=A.params[_A][_B][_D];E=A.params[_A][_B][_E];F=DataManager.Database();B=_C
		if A.rbt_apply.isChecked():B=_C
		elif A.rbt_noApply.isChecked():B=False
		G=A.et_buyVolume.value();H=[B,G];C=pd.DataFrame([H],columns=[D,E]);F.updateCSVFile('pats_setting_piggle_dao_most_voted.csv',C);A.notify_observers_condition(C);A.closeWindow()
	def register_observer_condition(A,observer):A.observer=observer
	def notify_observers_condition(A,conditionDf):A.observer.update_condition('settingPiggleDaoMostVoted',conditionDf)