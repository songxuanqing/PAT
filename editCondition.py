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
        idVal = self.params["mainWindow"]["displayConditionTable"]["id"]
        codeVal = self.params["mainWindow"]["displayConditionTable"]["code"]
        nameVal = self.params["mainWindow"]["displayConditionTable"]["name"]
        priceVal = self.params["mainWindow"]["displayConditionTable"]["price"]
        totalPriceVal = self.params["mainWindow"]["displayConditionTable"]["totalPrice"]
        startTimeVal = self.params["mainWindow"]["displayConditionTable"]["startTime"]
        endTimeVal = self.params["mainWindow"]["displayConditionTable"]["endTime"]
        profitRateVal = self.params["mainWindow"]["displayConditionTable"]["profitRate"]
        profitQtyPercentVal = self.params["mainWindow"]["displayConditionTable"]["profitQtyPercent"]
        maxProfitRateVal = self.params["mainWindow"]["displayConditionTable"]["maxProfitRate"]
        lossRateVal = self.params["mainWindow"]["displayConditionTable"]["lossRate"]
        lossQtyPercentVal = self.params["mainWindow"]["displayConditionTable"]["lossQtyPercent"]
        maxLossRateVal = self.params["mainWindow"]["displayConditionTable"]["maxLossRate"]

        self.conditionDataFrame = conditionDataFrame
        self.stockList = stockList
        self.registerConditionDialog = uic.loadUi("register_dao_condition.ui", self)  # ui 파일 불러오기
        self.bt_searchCode.clicked.connect(self.clickSearch)
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

        # row하나를 보냈으나 dataframe으로 들어왔으므로, 반복문(1회) 돌려서 그 안의 값을 빼온다. 반복문 없이는 시리즈값 반환환
        for idx, editingRowItem in rows.iterrows():
            self.id = editingRowItem[idVal]
            self.originStockCode = editingRowItem[codeVal]
            stockName = editingRowItem[nameVal]
            buyPrice = editingRowItem[priceVal]
            totalBuyAmount = editingRowItem[totalPriceVal]
            buyStartTimeStr = editingRowItem[startTimeVal]
            buyStartTime = datetime.strptime(buyStartTimeStr, "%H:%M").time()
            buyEndTimeStr = editingRowItem[endTimeVal]
            buyEndTime = datetime.strptime(buyEndTimeStr, "%H:%M").time()
            profitRate = editingRowItem[profitRateVal]
            profitRateVolume = editingRowItem[profitQtyPercentVal]
            maxProfitRate = editingRowItem[maxProfitRateVal]
            lossRate = editingRowItem[lossRateVal] * -1 #음수를 양수로 바꿔 디스플레이하기
            lossRateVolume = editingRowItem[lossQtyPercentVal]
            maxLossRate = editingRowItem[maxLossRateVal] * -1

            self.et_code.setText(self.originStockCode)
            self.tv_codeName.setText(stockName)
            self.et_buyPrice.setValue(buyPrice)
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

        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.closeWindow)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.saveCondition(dataManager))

        self.registerConditionDialog.show()

    def closeWindow(self):
        self.close()

    def saveCondition(self,dataManager):

        idVal = self.params["mainWindow"]["displayConditionTable"]["id"]
        codeVal = self.params["mainWindow"]["displayConditionTable"]["code"]
        nameVal = self.params["mainWindow"]["displayConditionTable"]["name"]
        priceVal = self.params["mainWindow"]["displayConditionTable"]["price"]
        totalPriceVal = self.params["mainWindow"]["displayConditionTable"]["totalPrice"]
        startTimeVal = self.params["mainWindow"]["displayConditionTable"]["startTime"]
        endTimeVal = self.params["mainWindow"]["displayConditionTable"]["endTime"]
        profitRateVal = self.params["mainWindow"]["displayConditionTable"]["profitRate"]
        profitQtyPercentVal = self.params["mainWindow"]["displayConditionTable"]["profitQtyPercent"]
        maxProfitRateVal = self.params["mainWindow"]["displayConditionTable"]["maxProfitRate"]
        lossRateVal = self.params["mainWindow"]["displayConditionTable"]["lossRate"]
        lossQtyPercentVal = self.params["mainWindow"]["displayConditionTable"]["lossQtyPercent"]
        maxLossRateVal = self.params["mainWindow"]["displayConditionTable"]["maxLossRate"]

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
        buyPrice = self.et_buyPrice.value()
        totalBuyAmount = self.et_totalBuyAmount.value()
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
            for idx, row in self.conditionDataFrame.iterrows():
                if row[idVal] == id:
                    self.conditionDataFrame.at[idx, codeVal] = str(stockCode)
                    self.conditionDataFrame.at[idx, nameVal] = stockName
                    self.conditionDataFrame.at[idx, priceVal] = buyPrice
                    self.conditionDataFrame.at[idx, totalPriceVal] = totalBuyAmount
                    self.conditionDataFrame.at[idx, startTimeVal] = buyStartTime
                    self.conditionDataFrame.at[idx, endTimeVal] = buyEndTime
                    self.conditionDataFrame.at[idx, profitRateVal] = profitRate
                    self.conditionDataFrame.at[idx, profitQtyPercentVal] = profitRateVolume
                    self.conditionDataFrame.at[idx, maxProfitRateVal] = maxProfitRate
                    self.conditionDataFrame.at[idx, lossRateVal] = lossRate
                    self.conditionDataFrame.at[idx, lossQtyPercentVal] = lossRateVolume
                    self.conditionDataFrame.at[idx, maxLossRateVal] = maxLossRate
                    dataManager.updateCSVFile('pats_condition.csv', self.conditionDataFrame)  # row가 업데이트된 전체 df 다시 저장
                    # 변경한 df만 추출
                    # df = self.conditionDataFrame(self.conditionDataFrame['ID'] == id)
                    self.notify_observers_condition(self.conditionDataFrame)  # df = condition 변경된 조건 하나만 알림.
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

    def notify_observers_condition(self,condition):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_condition("edit",condition)