from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5 import QtCore
import pandas as pd
from datetime import datetime
import interface.conditionRegistration as ConditionRegistration
import interface.codeSearch as codeSearch
import searchCode

class EditConditionKW(QtWidgets.QDialog, ConditionRegistration.Subject):
    def __init__(self,dataManager,rows,conditionDataFrame,conditionList):
        super().__init__()
        self.conditionList = conditionList
        self.conditionDataFrame = conditionDataFrame
        self.registerConditionDialog = uic.loadUi("register_kiwoom_condition.ui", self)  # ui 파일 불러오기
        self.cb_conditionList.addItems(self.conditionList)

        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).setText("확인")
        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).setText("취소")
        # 정규식 예외처리
        self.et_profitRate.setPrefix('+ ')
        self.et_maxProfitRate.setPrefix('+ ')

        self.et_lossRate.setPrefix('- ')
        self.et_maxLossRate.setPrefix('- ')

        # row하나를 보냈으나 dataframe으로 들어왔으므로, 반복문(1회) 돌려서 그 안의 값을 빼온다. 반복문 없이는 시리즈값 반환환
        for idx, editingRowItem in rows.iterrows():
            self.id = editingRowItem['ID']
            self.originIdx = editingRowItem['코드']
            name = editingRowItem['조건명']
            selectedItem = str(str(self.originIdx)+" : "+name)
            buyPricePerStock = editingRowItem['종목당금액']
            totalBuyAmount = editingRowItem['총금액']
            buyStartTimeStr = editingRowItem['시작시간']
            buyStartTime = datetime.strptime(buyStartTimeStr, "%H:%M").time()
            buyEndTimeStr = editingRowItem['종료시간']
            buyEndTime = datetime.strptime(buyEndTimeStr, "%H:%M").time()
            profitRate = editingRowItem['부분익절율']
            profitRateVolume = editingRowItem['부분익절수량']
            maxProfitRate = editingRowItem['최대익절율']
            lossRate = editingRowItem['부분손절율'] * -1 #음수를 양수로 바꿔 디스플레이하기
            lossRateVolume = editingRowItem['부분손절수량']
            maxLossRate = editingRowItem['최대손절율'] * -1

            self.cb_conditionList.setCurrentIndex(self.conditionList.index(selectedItem))
            self.et_buyAmountPerCode.setValue(buyPricePerStock)
            self.et_totalBuyAmount.setValue(totalBuyAmount)
            self.et_buyStartTime.setTime(buyStartTime)
            self.et_buyEndTime.setTime(buyEndTime)
            self.et_profitRate.setValue(profitRate)
            self.et_profitRateVolume.setValue(profitRateVolume)
            self.et_maxProfitRate.setValue(maxProfitRate)
            # 손실은 음수로 저장
            self.et_lossRate.setValue(lossRate)
            self.et_lossRateVolume.setValue(lossRateVolume)
            self.et_maxLossRate.setValue(maxLossRate)

        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.closeWindow)
        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(
            lambda: self.saveCondition(dataManager))
        self.registerConditionDialog.show()

    def closeWindow(self):
        self.close()

    def saveCondition(self,dataManager):
        id = self.id
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
        for idx, row in self.conditionDataFrame.iterrows():
            if row['코드'] == selectedConditionId:
                if selectedConditionId == self.originIdx:
                    isAlreadyRegistered = False
                else:
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

        elif buyPricePerStock == 0:
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "종목당 매수가는 0보다 커야합니다. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif totalBuyAmount == 0:
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
            for idx, row in self.conditionDataFrame.iterrows():
                if row['ID'] == id:
                    self.conditionDataFrame.at[idx, '코드'] = selectedConditionId
                    self.conditionDataFrame.at[idx, '조건명'] = selectedConditionName
                    self.conditionDataFrame.at[idx, '총금액'] = totalBuyAmount
                    self.conditionDataFrame.at[idx, '종목당금액'] = buyPricePerStock
                    self.conditionDataFrame.at[idx, '시작시간'] = buyStartTime
                    self.conditionDataFrame.at[idx, '종료시간'] = buyEndTime
                    self.conditionDataFrame.at[idx, '부분익절율'] = profitRate
                    self.conditionDataFrame.at[idx, '부분익절수량'] = profitRateVolume
                    self.conditionDataFrame.at[idx, '최대익절율'] = maxProfitRate
                    self.conditionDataFrame.at[idx, '부분손절율'] = lossRate
                    self.conditionDataFrame.at[idx, '부분손절수량'] = lossRateVolume
                    self.conditionDataFrame.at[idx, '최대손절율'] = maxLossRate
                    dataManager.updateCSVFile('pats_kiwoom_condition.csv',
                                              self.conditionDataFrame)  # row가 업데이트된 전체 df 다시 저장
                    self.notify_observers_condition(self.conditionDataFrame)  # df = condition 변경된 조건 하나만 알림.
                    self.close()



    def register_observer_condition(self, observer):
        self.observer = observer

    def notify_observers_condition(self,condition):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_condition("editKW",condition)