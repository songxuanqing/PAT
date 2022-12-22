#-*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
import pandas as pd
import interface.conditionRegistration as ConditionRegistration
import models.database as DataManager
import openJson

class SettingPiggleDaoMostVoted(QtWidgets.QDialog, ConditionRegistration.Subject):
    def __init__(self, settingPiggleDaoMostVoted):
        super().__init__()
        self.msg, self.params = openJson.getJsonFiles()
        isAppliedVal = self.params["mainWindow"]["createSettingPiggleDaoMostVotedFile"]["isApplied"]
        amountVal = self.params["mainWindow"]["createSettingPiggleDaoMostVotedFile"]["amount"]

        self.settingDialog = uic.loadUi("setting_piggle_dao_most_voted.ui", self)  # ui 파일 불러오기
        for idx, row in settingPiggleDaoMostVoted.iterrows():
            isApplied = row[isAppliedVal]
            buyVoulume = row[isAppliedVal]
            if isApplied:
                self.rbt_apply.setChecked(True)
            else:
                self.rbt_noApply.setChecked(True)
            self.et_buyVolume.setValue(buyVoulume)
        confirm = self.msg['button']['confirm']
        cancel = self.msg['button']['cancel']
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(confirm)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(cancel)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.closeWindow)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.saveCondition)
        self.settingDialog.show()

    def closeWindow(self):
        self.close()

    def saveCondition(self):
        isAppliedVal = self.params["mainWindow"]["createSettingPiggleDaoMostVotedFile"]["isApplied"]
        amountVal = self.params["mainWindow"]["createSettingPiggleDaoMostVotedFile"]["amount"]

        dataManager = DataManager.Database()
        isApplied = True
        if self.rbt_apply.isChecked():
            isApplied = True
        elif self.rbt_noApply.isChecked():
            isApplied = False
        buyVolume = self.et_buyVolume.value()
        arr = [isApplied, buyVolume]
        df = pd.DataFrame([arr],
                          columns=[isAppliedVal, amountVal])
        dataManager.updateCSVFile('pats_setting_piggle_dao_most_voted.csv', df)
        self.notify_observers_condition(df)
        self.closeWindow()

    def register_observer_condition(self, observer):
        self.observer = observer

    def notify_observers_condition(self,conditionDf):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_condition("settingPiggleDaoMostVoted",conditionDf)

