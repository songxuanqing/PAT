from PyQt5 import QtWidgets, uic
import pandas as pd
import interface.conditionRegistration as ConditionRegistration
import models.database as DataManager

class SettingPiggleDaoMostVoted(QtWidgets.QDialog, ConditionRegistration.Subject):
    def __init__(self, settingPiggleDaoMostVoted):
        super().__init__()
        self.settingDialog = uic.loadUi("setting_piggle_dao_most_voted.ui", self)  # ui 파일 불러오기
        for idx, row in settingPiggleDaoMostVoted.iterrows():
            isApplied = row['적용여부']
            buyVoulume = row['매수량']
            if isApplied:
                self.rbt_apply.setChecked(True)
            else:
                self.rbt_noApply.setChecked(True)
            self.et_buyVolume.setValue(buyVoulume)

        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText("확인")
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText("취소")
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.closeWindow)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.saveCondition)
        self.settingDialog.show()

    def closeWindow(self):
        self.close()

    def saveCondition(self):
        dataManager = DataManager.Database()
        isApplied = True
        if self.rbt_apply.isChecked():
            isApplied = True
        elif self.rbt_noApply.isChecked():
            isApplied = False
        buyVolume = self.et_buyVolume.value()
        arr = [isApplied, buyVolume]
        df = pd.DataFrame([arr],
                          columns=['적용여부', '매수량'])
        dataManager.updateCSVFile('pats_setting_piggle_dao_most_voted.csv', df)
        self.notify_observers_condition(df)
        self.closeWindow()

    def register_observer_condition(self, observer):
        self.observer = observer

    def notify_observers_condition(self,conditionDf):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_condition("settingPiggleDaoMostVoted",conditionDf)

