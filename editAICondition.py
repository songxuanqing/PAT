#-*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5 import QtCore
import pandas as pd
from datetime import datetime
import interface.conditionRegistration as ConditionRegistration
import interface.codeSearch as codeSearch
import searchCode
import openJson

class EditCondition(QtWidgets.QDialog, ConditionRegistration.Subject, codeSearch.Observer):
    def __init__(self,dataManager,rows,conditionDataFrame,stockList):
        super().__init__()
        self.msg, self.params = openJson.getJsonFiles()
        dayBuy = self.params['kiwoomRealTimeData']['AIConditionList']['dayBuy']
        minBuy = self.params['kiwoomRealTimeData']['AIConditionList']['minBuy']

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

        self.conditionDataFrame = conditionDataFrame
        self.stockList = stockList
        self.registerConditionDialog = uic.loadUi("register_ai_condition.ui", self)  # ui ?????? ????????????
        self.bt_searchCode.clicked.connect(self.clickSearch)
        self.typeList = [dayBuy, minBuy]
        self.cb_dayMin.addItems(self.typeList)

        confirm = self.msg['button']['confirm']
        cancel = self.msg['button']['cancel']
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText(confirm)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText(cancel)
        #????????? ????????????
        regexCode = QtCore.QRegExp("[0-9_]+")
        validatorCode = QtGui.QRegExpValidator(regexCode)
        self.et_code.setValidator(validatorCode)
        self.et_profitRate.setPrefix('+ ')
        self.et_maxProfitRate.setPrefix('+ ')
        self.et_lossRate.setPrefix('- ')
        self.et_maxLossRate.setPrefix('- ')

        # row????????? ???????????? dataframe?????? ??????????????????, ?????????(1???) ????????? ??? ?????? ?????? ?????????. ????????? ????????? ???????????? ?????????
        for idx, editingRowItem in rows.iterrows():
            self.id = editingRowItem[idVal]
            self.originStockCode = editingRowItem[codeVal]
            stockName = editingRowItem[nameVal]
            aiTradingType = editingRowItem[buyTypeVal]
            totalBuyAmountPerTime = editingRowItem[buyAmountPerTimeVal]
            totalBuyAmount = editingRowItem[totalPriceVal]
            buyStartTimeStr = editingRowItem[startTimeVal]
            buyStartTime = datetime.strptime(buyStartTimeStr, "%H:%M").time()
            buyEndTimeStr = editingRowItem[endTimeVal]
            buyEndTime = datetime.strptime(buyEndTimeStr, "%H:%M").time()
            profitRate = editingRowItem[profitRateVal]
            profitRateVolume = editingRowItem[profitQtyPercentVal]
            maxProfitRate = editingRowItem[maxProfitRateVal]
            lossRate = editingRowItem[lossRateVal] * -1 #????????? ????????? ?????? ?????????????????????
            lossRateVolume = editingRowItem[lossQtyPercentVal]
            maxLossRate = editingRowItem[maxLossRateVal] * -1

            self.et_code.setText(self.originStockCode)
            self.tv_codeName.setText(stockName)
            self.cb_dayMin.setCurrentIndex(self.typeList.index(aiTradingType))
            self.et_totalBuyAmountPerTime.setValue(totalBuyAmountPerTime)
            self.et_totalBuyAmount.setValue(totalBuyAmount)
            self.et_buyStartTime.setTime(buyStartTime)
            self.et_buyEndTime.setTime(buyEndTime)
            self.et_profitRate.setValue(profitRate)
            self.et_profitRateVolume.setValue(profitRateVolume)
            self.et_maxProfitRate.setValue(maxProfitRate)
            # ????????? ????????? ??????
            self.et_lossRate.setValue(lossRate)
            self.et_lossRateVolume.setValue(lossRateVolume)
            self.et_maxLossRate.setValue(maxLossRate)

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

        id = self.id
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
        #????????? ????????? ??????
        lossRate = (self.et_lossRate.value())* -1
        lossRateVolume = (self.et_lossRateVolume.value())
        maxLossRate = (self.et_maxLossRate.value())* -1

        isAlreadyRegistered = False
        for idx,row in self.conditionDataFrame.iterrows():
            if row[codeVal] == stockCode:
                if stockCode == self.originStockCode:
                    isAlreadyRegistered = False
                else:
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

        elif totalBuyAmountPerTime == 0 :
            choice = QtWidgets.QMessageBox.information(self, self.saveCondition,
                                                self.notZeroForBuyPrice,
                                                QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif totalBuyAmount == 0 :
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
            for idx, row in self.conditionDataFrame.iterrows():
                if row[idVal] == id:
                    self.conditionDataFrame.at[idx, codeVal] = str(stockCode)
                    self.conditionDataFrame.at[idx, nameVal] = stockName
                    self.conditionDataFrame.at[idx, buyTypeVal] = aiTradingType
                    self.conditionDataFrame.at[idx, buyAmountPerTimeVal] = totalBuyAmountPerTime
                    self.conditionDataFrame.at[idx, totalPriceVal] = totalBuyAmount
                    self.conditionDataFrame.at[idx, startTimeVal] = buyStartTime
                    self.conditionDataFrame.at[idx, endTimeVal] = buyEndTime
                    self.conditionDataFrame.at[idx, profitRateVal] = profitRate
                    self.conditionDataFrame.at[idx, profitQtyPercentVal] = profitRateVolume
                    self.conditionDataFrame.at[idx, maxProfitRateVal] = maxProfitRate
                    self.conditionDataFrame.at[idx, lossRateVal] = lossRate
                    self.conditionDataFrame.at[idx, lossQtyPercentVal] = lossRateVolume
                    self.conditionDataFrame.at[idx, maxLossRateVal] = maxLossRate
                    dataManager.updateCSVFile('pats_ai_condition.csv', self.conditionDataFrame)  # row??? ??????????????? ?????? df ?????? ??????
                    # ????????? df??? ??????
                    # df = self.conditionDataFrame(self.conditionDataFrame['ID'] == id)
                    self.notify_observers_condition(self.conditionDataFrame)  # df = condition ????????? ?????? ????????? ??????.
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

    def notify_observers_condition(self,condition):  # ??????????????? ????????? ?????? (????????????????????? ?????? ?????? ??????????????? ???????????? ????????? ??????)
        self.observer.update_condition("editAI",condition)