from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
import pandas as pd
import interface.conditionRegistration as ConditionRegistration

class RegisterCondition(QtWidgets.QDialog, ConditionRegistration.Subject):
    def __init__(self,dataManager,currentConditionLength):
        super().__init__()
        self.currentConditionLength = currentConditionLength
        self.registerConditionDialog = uic.loadUi("register_condition_dao.ui", self)  # ui 파일 불러오기
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText("확인")
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText("취소")
        self.et_code.setInputMask("000000")
        #range validation넣기
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.saveCondition(dataManager))
        self.registerConditionDialog.show()

    def saveCondition(self,dataManager):
        id = self.currentConditionLength+1
        stockCode = self.et_code.toPlainText()
        stockName = self.tv_codeName.toPlainText()
        buyPrice = self.et_buyPrice.toPlainText()
        totalBuyAmount = self.et_totalBuyAmout.toPlainText()
        buyStartTime = self.et_buyStartTime.dateTime().toString("HH:mm")
        buyEndTime = self.et_buyEndTime.dateTime().toString("HH:mm")
        profitRate = self.et_profitRate.toPlainText()
        profitRateVolume = self.et_profitRateVolume.toPlainText()
        maxProfitRate = self.et_maxProfitRate.toPlainText()
        lossRate = self.et_lossRate.toPlainText()
        lossRateVolume = self.et_lossRateVolume.toPlainText()
        maxLossRate = self.et_maxLossRate.toPlainText()
        arr = [id,str(stockCode), stockName, buyPrice,totalBuyAmount,
                           buyStartTime,buyEndTime,profitRate,profitRateVolume,maxProfitRate,
                           lossRate,lossRateVolume,maxLossRate]
        df = pd.DataFrame([arr],
                          columns=['ID','종목코드','종목명','매수가','총금액',
                                   '시작시간','종료시간','부분익절율','부분익절수량','최대익절율',
                                   '부분손절율','부분손절수량','최대손절율'])
        # df['종목코드'] = df['종목코드'].apply('{}'.format)
        dataManager.appendCSVFile('pats_condition.csv',df)
        self.notify_observers_condition(df) #df = condition
        print("save condition")

    def register_observer_condition(self, observer):
        self.observer = observer

    def notify_observers_condition(self,condition):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_condition(condition)