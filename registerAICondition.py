#-*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5 import QtCore
import pandas as pd
import interface.conditionRegistration as ConditionRegistration
import interface.codeSearch as codeSearch
import searchCode
import openJson

class RegisterAICondition(QtWidgets.QDialog, ConditionRegistration.Subject, codeSearch.Observer):
    def __init__(self,dataManager,lastCondtiontionId,stockList,monitoredConditionList):
        super().__init__()
        self.msg, self.params = openJson.getJsonFiles()
        dayBuy = self.params['kiwoomRealTimeData']['AIConditionList']['dayBuy']
        minBuy = self.params['kiwoomRealTimeData']['AIConditionList']['minBuy']

        self.stockList = stockList
        self.monitoredConditionList = monitoredConditionList
        self.lastCondtiontionId = lastCondtiontionId
        self.registerConditionDialog = uic.loadUi("register_ai_condition.ui", self)  # ui 파일 불러오기
        self.bt_searchCode.clicked.connect(self.clickSearch)
        typeList = [dayBuy,minBuy]
        self.cb_dayMin.addItems(typeList)
        confirm = self.msg['button']['confirm']
        cancel = self.msg['button']['cancel']
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(confirm)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(cancel)
        #정규식 예외처리
        regexCode = QtCore.QRegExp("[0-9_]+")
        validatorCode = QtGui.QRegExpValidator(regexCode)
        self.et_code.setValidator(validatorCode)
        self.et_profitRate.setPrefix('+ ')
        self.et_maxProfitRate.setPrefix('+ ')
        self.et_lossRate.setPrefix('- ')
        self.et_maxLossRate.setPrefix('- ')
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.closeWindow)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.saveCondition(dataManager))
        self.registerConditionDialog.show()

    def closeWindow(self):
        self.close()

    def saveCondition(self,dataManager):
        idVal = self.params["mainWindow"]["displayAIConditionTable"]["id"]
        codeVal = self.params["mainWindow"]["displayAIConditionTable"]["code"]
        nameVal = self.params["mainWindow"]["displayAIConditionTable"]["name"]
        buyTypeVal = self.params['kiwoomRealTimeData']['AIConditionList']['type']
        buyAmountPerTimeVal = self.params["mainWindow"]["displayAIConditionTable"]["buyAmountPerTime"]
        totalPriceVal = self.params["mainWindow"]["displayAIConditionTable"]["totalPrice"]
        startTimeVal = self.params["mainWindow"]["displayAIConditionTable"]["startTime"]
        endTimeVal = self.params["mainWindow"]["displayAIConditionTable"]["endTime"]
        profitRateVal = self.params["mainWindow"]["displayAIConditionTable"]["profitRate"]
        profitQtyPercentVal = self.params["mainWindow"]["displayAIConditionTable"]["profitQtyPercent"]
        maxProfitRateVal = self.params["mainWindow"]["displayAIConditionTable"]["maxProfitRate"]
        lossRateVal = self.params["mainWindow"]["displayAIConditionTable"]["lossRate"]
        lossQtyPercentVal = self.params["mainWindow"]["displayAIConditionTable"]["lossQtyPercent"]
        maxLossRateVal = self.params["mainWindow"]["displayAIConditionTable"]["maxLossRate"]

        self.saveCondition = self.msg['saveCondition']
        self.nullCode = self.msg['nullCode']
        self.alreadyRegistered = self.msg['alreadyRegistered']
        self.notZeroForBuyPrice = self.msg['notZeroForBuyPrice']
        self.notZeroForTotalBuyPrice = self.msg['notZeroForTotalBuyPrice']
        self.endLaterThanStart = self.msg['endLaterThanStart']
        self.maxMoreThanProfit = self.msg['maxMoreThanProfit']
        self.maxMoreThanLoss = self.msg['maxMoreThanLoss']

        id = self.lastCondtiontionId + 1
        stockCode = self.et_code.text()
        stockName = self.tv_codeName.text()
        aiTradingType = self.cb_dayMin.currentText()
        totalBuyAmountPerTime = self.et_totalBuyAmountPerTime.value()
        totalBuyAmount = self.et_totalBuyAmount.value()
        buyStartTime = self.et_buyStartTime.dateTime().toString("HH:mm")
        buyEndTime = self.et_buyEndTime.dateTime().toString("HH:mm")
        profitRate = self.et_profitRate.value()
        profitRateVolume = self.et_profitRateVolume.value()
        maxProfitRate = self.et_maxProfitRate.value()
        # 손실은 음수로 저장
        lossRate = (self.et_lossRate.value()) * -1
        lossRateVolume = (self.et_lossRateVolume.value())
        maxLossRate = (self.et_maxLossRate.value()) * -1

        isAlreadyRegistered = False
        for idx,row in self.monitoredConditionList.iterrows():
            if row[codeVal] == stockCode:
                isAlreadyRegistered = True
            else:
                isAlreadyRegistered = False

        if stockCode == "":
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.nullCode,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif isAlreadyRegistered:
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.alreadyRegistered,
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif buyPrice == 0:
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                       self.notZeroForBuyPrice,
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
            arr = [id, str(stockCode), stockName, aiTradingType, totalBuyAmountPerTime, totalBuyAmount,
                   buyStartTime, buyEndTime,profitRate, profitRateVolume, maxProfitRate,
                   lossRate, lossRateVolume, maxLossRate]
            df = pd.DataFrame([arr],
                              columns=[idVal, codeVal, nameVal, buyTypeVal, buyAmountPerTimeVal,totalPriceVal,
                                       startTimeVal,endTimeVal,profitRateVal,profitQtyPercentVal,
                                       maxProfitRateVal,lossRateVal,lossQtyPercentVal,maxLossRateVal])
            # df['코드'] = df['코드'].apply('{}'.format)
            dataManager.appendCSVFile('pats_ai_condition.csv', df)
            self.notify_observers_condition(df)
            self.closeWindow()

    def clickSearch(self):
        keyword = self.et_code.text()
        searchCodeWindow = searchCode.SearchCode(keyword,self.stockList)
        self.register_subject_searchCode(searchCodeWindow)

    def update_searchCode(self, code, name):
        self.et_code.setText(code)
        self.tv_codeName.setText(name)

    def register_subject_searchCode(self, subject):
        self.subject = subject
        self.subject.register_observer_searchCode(self)

    def register_observer_condition(self, observer):
        self.observer = observer

    def notify_observers_condition(self,conditionDf):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_condition("registerAI",conditionDf)

