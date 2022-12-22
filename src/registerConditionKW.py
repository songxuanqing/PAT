from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5 import QtCore
import pandas as pd
import interface.conditionRegistration as ConditionRegistration

class RegisterConditionKW(QtWidgets.QDialog, ConditionRegistration.Subject):
    def __init__(self,dataManager,conditionList,lastCondtiontionId, monitoredConditionList):
        super().__init__()
        self.conditionList = conditionList
        self.monitoredConditionList = monitoredConditionList
        self.lastConditionId = lastCondtiontionId
        self.registerConditionDialog = uic.loadUi("register_kiwoom_condition.ui", self)  # ui 파일 불러오기
        self.cb_conditionList.addItems(self.conditionList)

        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).setText("확인")
        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).setText("취소")
        #정규식 예외처리
        self.et_profitRate.setPrefix('+ ')
        self.et_maxProfitRate.setPrefix('+ ')

        self.et_lossRate.setPrefix('- ')
        self.et_maxLossRate.setPrefix('- ')

        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.closeWindow)
        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.saveCondition(dataManager))
        self.registerConditionDialog.show()

    def closeWindow(self):
        self.close()

    def saveCondition(self,dataManager):
        id = self.lastConditionId+1
        selectedConditionStr = self.cb_conditionList.currentText().split(" : ")
        selectedConditionId = str(selectedConditionStr[0])
        selectedConditionName = selectedConditionStr[1]
        totalBuyAmount = self.et_totalBuyAmount.value()
        buyPricePerStock = self.et_buyAmountPerCode.value()
        buyStartTime = self.et_buyStartTime.dateTime().toString("HH:mm")
        buyEndTime = self.et_buyEndTime.dateTime().toString("HH:mm")
        profitRate = self.et_profitRate.value()
        profitRateVolume = self.et_profitRateVolume.value()
        maxProfitRate = self.et_maxProfitRate.value()
        #손실은 음수로 저장
        lossRate = (self.et_lossRate.value())* -1
        lossRateVolume = (self.et_lossRateVolume.value())
        maxLossRate = (self.et_maxLossRate.value())* -1

        isAlreadyRegistered = False
        for idx,row in self.monitoredConditionList.iterrows():
            if row['코드'] == selectedConditionId:
                isAlreadyRegistered = True
            else:
                isAlreadyRegistered = False

        if self.cb_conditionList.currentText() == "":
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "조건을 선택하세요. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif isAlreadyRegistered:
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "이미 자동매매로 등록된 조건입니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif buyPricePerStock == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                "종목당 매수가는 0보다 커야합니다. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif totalBuyAmount == 0 :
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                "총 금액은 0보다 커야합니다. ",
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif self.et_buyStartTime.dateTime() > self.et_buyEndTime.dateTime():
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "시작 시간은 끝시간보다 앞서야합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif profitRate >= maxProfitRate:
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "최대익절율은 부분익절율보다 커야합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif maxLossRate >= lossRate:
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "최대손절율은 부분손절율보다 커야합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        else:
            arr = [id, selectedConditionId, selectedConditionName, totalBuyAmount, buyPricePerStock,
                   buyStartTime, buyEndTime, profitRate, profitRateVolume, maxProfitRate,
                   lossRate, lossRateVolume, maxLossRate]
            df = pd.DataFrame([arr],
                              columns=['ID', '코드', '조건명', '총금액', '종목당금액',
                                       '시작시간', '종료시간', '부분익절율', '부분익절수량', '최대익절율',
                                       '부분손절율', '부분손절수량', '최대손절율'])
            # df['코드'] = df['코드'].apply('{}'.format)
            dataManager.appendCSVFile('pats_kiwoom_condition.csv', df)
            self.notify_observers_condition(df)  # df = condition
            self.close()
            # for idx, row in df.iterrows():
            #     self.notify_observers_condition(row) #df = condition
            #     print("save condition")

    def register_observer_condition(self, observer):
        self.observer = observer

    def notify_observers_condition(self,conditionDf):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_condition("registerKW",conditionDf)