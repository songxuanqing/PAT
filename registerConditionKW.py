#-*- coding: utf-8 -*-
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
        confirm = self.msg['button']['confirm']
        cancel = self.msg['button']['cancel']
        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Ok).setText(confirm)
        self.bts_oneCondition.button(QtWidgets.QDialogButtonBox.Cancel).setText(cancel)
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
        idVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["id"]
        codeVal = self.params["mainWindow"]["displayConditionTable"]["code"]
        nameVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["name"]
        totalPriceVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["totalPrice"]
        priceVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["price"]
        startTimeVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["startTime"]
        endTimeVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["endTime"]
        profitRateVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["profitRate"]
        profitQtyPercentVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["profitQtyPercent"]
        maxProfitRateVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["maxProfitRate"]
        lossRateVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["lossRate"]
        lossQtyPercentVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["lossQtyPercent"]
        maxLossRateVal = self.params["mainWindow"]["displayKiwoomConditionTable"]["maxLossRate"]

        self.saveCondition = self.msg['saveCondition']
        self.selectCondiCode = self.msg['selectCondiCode']
        self.alreadyRegisteredCondition = self.msg['alreadyRegisteredCondition']
        self.noZeroForBuyPricePerStock = self.msg['noZeroForBuyPricePerStock']
        self.notZeroForTotalBuyPrice = self.msg['notZeroForTotalBuyPrice']
        self.endLaterThanStart = self.msg['endLaterThanStart']
        self.maxMoreThanProfit = self.msg['maxMoreThanProfit']
        self.maxMoreThanLoss = self.msg['maxMoreThanLoss']

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
            if row[codeVal] == selectedConditionId:
                isAlreadyRegistered = True
            else:
                isAlreadyRegistered = False

        if self.cb_conditionList.currentText() == "":
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.selectCondiCode,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif isAlreadyRegistered:
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.alreadyRegisteredCondition,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif buyPricePerStock == 0:
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.noZeroForBuyPricePerStock,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif totalBuyAmount == 0:
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.notZeroForTotalBuyPrice,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif self.et_buyStartTime.dateTime() > self.et_buyEndTime.dateTime():
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.endLaterThanStart,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif profitRate >= maxProfitRate:
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.maxMoreThanProfit,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif maxLossRate >= lossRate:
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.maxMoreThanLoss,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        else:
            arr = [id, selectedConditionId, selectedConditionName, totalBuyAmount, buyPricePerStock,
                   buyStartTime, buyEndTime, profitRate, profitRateVolume, maxProfitRate,
                   lossRate, lossRateVolume, maxLossRate]
            df = pd.DataFrame([arr],
                              columns=[idVal, codeVal, nameVal, totalPriceVal, priceVal,
                                       startTimeVal,endTimeVal,profitRateVal,profitQtyPercentVal,
                                       maxProfitRateVal,lossRateVal,lossQtyPercentVal,maxLossRateVal])
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