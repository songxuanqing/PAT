from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pandas as pd
import interface.conditionRegistration as ConditionRegistration
import interface.codeSearch as codeSearch
import searchCode

class RegisterCondition(QtWidgets.QDialog, ConditionRegistration.Subject, codeSearch.Observer):
    def __init__(self,dataManager,currentConditionLength,stockList):
        super().__init__()
        self.stockList = stockList
        self.currentConditionLength = currentConditionLength
        self.registerConditionDialog = uic.loadUi("register_condition_dao.ui", self)  # ui 파일 불러오기
        self.bt_searchCode.clicked.connect(self.clickSearch)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText("확인")
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText("취소")
        self.et_code.setInputMask("000000")
        #range validation넣기
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.saveCondition(dataManager))
        self.registerConditionDialog.show()

    def saveCondition(self,dataManager):
        id = self.currentConditionLength+1
        stockCode = self.et_code.text()
        stockName = self.tv_codeName.text()
        buyPrice = self.et_buyPrice.text()
        totalBuyAmount = self.et_totalBuyAmout.text()
        buyStartTime = self.et_buyStartTime.dateTime().toString("HH:mm")
        buyEndTime = self.et_buyEndTime.dateTime().toString("HH:mm")
        profitRate = self.et_profitRate.text()
        profitRateVolume = self.et_profitRateVolume.text()
        maxProfitRate = self.et_maxProfitRate.text()
        lossRate = self.et_lossRate.text()
        lossRateVolume = self.et_lossRateVolume.text()
        maxLossRate = self.et_maxLossRate.text()
        arr = [id,str(stockCode), stockName, buyPrice,totalBuyAmount,
                           buyStartTime,buyEndTime,profitRate,profitRateVolume,maxProfitRate,
                           lossRate,lossRateVolume,maxLossRate]
        df = pd.DataFrame([arr],
                          columns=['ID','종목코드','종목명','매수가','총금액',
                                   '시작시간','종료시간','부분익절율','부분익절수량','최대익절율',
                                   '부분손절율','부분손절수량','최대손절율'])
        # df['종목코드'] = df['종목코드'].apply('{}'.format)
        dataManager.appendCSVFile('pats_condition.csv',df)
        for idx, row in df.iterrows():
            self.notify_observers_condition(row) #df = condition
            print("save condition")

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
        self.observer.update_condition(condition)