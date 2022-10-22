from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5 import QtCore
import pandas as pd
from datetime import datetime
import interface.conditionRegistration as ConditionRegistration
import interface.codeSearch as codeSearch
import searchCode

class EditCondition(QtWidgets.QDialog, ConditionRegistration.Subject, codeSearch.Observer):
    def __init__(self,dataManager,rows,conditionDataFrame,stockList):
        super().__init__()
        self.conditionDataFrame = conditionDataFrame
        self.stockList = stockList
        self.registerConditionDialog = uic.loadUi("register_condition_dao.ui", self)  # ui 파일 불러오기
        self.bt_searchCode.clicked.connect(self.clickSearch)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).setText("확인")
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).setText("취소")
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
            self.id = editingRowItem['ID']
            stockCode = editingRowItem['종목코드']
            print("code" + str(stockCode))
            stockName = editingRowItem['종목명']
            buyPrice = editingRowItem['매수가']
            totalBuyAmount = editingRowItem['총금액']
            buyStartTimeStr = editingRowItem['시작시간']
            buyStartTime = datetime.strptime(buyStartTimeStr, "%H:%M").time()
            buyEndTimeStr = editingRowItem['종료시간']
            buyEndTime = datetime.strptime(buyEndTimeStr, "%H:%M").time()
            print(buyEndTime)
            profitRate = editingRowItem['부분익절율']
            profitRateVolume = editingRowItem['부분익절수량']
            maxProfitRate = editingRowItem['최대익절율']
            lossRate = editingRowItem['부분손절율'] * -1 #음수를 양수로 바꿔 디스플레이하기
            print(lossRate)
            lossRateVolume = editingRowItem['부분손절수량']
            maxLossRate = editingRowItem['최대손절율'] * -1

            self.et_code.setText(stockCode)
            self.tv_codeName.setText(stockName)
            self.et_buyPrice.setValue(buyPrice)
            self.et_totalBuyAmout.setValue(totalBuyAmount)
            self.et_buyStartTime.setTime(buyStartTime)
            self.et_buyEndTime.setTime(buyEndTime)
            self.et_profitRate.setValue(profitRate)
            self.et_profitRateVolume.setValue(profitRateVolume)
            self.et_maxProfitRate.setValue(maxProfitRate)
            # 손실은 음수로 저장
            self.et_lossRate.setValue(lossRate)
            self.et_lossRateVolume.setValue(lossRateVolume)
            self.et_maxLossRate.setValue(maxLossRate)

        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.saveCondition(dataManager))
        self.registerConditionDialog.show()

    def saveCondition(self,dataManager):
        id = self.id
        stockCode = self.et_code.text()
        stockName = self.tv_codeName.text()
        buyPrice = self.et_buyPrice.value()
        totalBuyAmount = self.et_totalBuyAmout.value()
        buyStartTime = self.et_buyStartTime.dateTime().toString("HH:mm")
        buyEndTime = self.et_buyEndTime.dateTime().toString("HH:mm")
        profitRate = self.et_profitRate.value()
        profitRateVolume = self.et_profitRateVolume.value()
        maxProfitRate = self.et_maxProfitRate.value()
        #손실은 음수로 저장
        lossRate = (self.et_lossRate.value())* -1
        lossRateVolume = (self.et_lossRateVolume.value())
        maxLossRate = (self.et_maxLossRate.value())* -1

        # arr = [id,str(stockCode), stockName, buyPrice,totalBuyAmount,
        #                    buyStartTime,buyEndTime,profitRate,profitRateVolume,maxProfitRate,
        #                    lossRate,lossRateVolume,maxLossRate]
        # df = pd.DataFrame([arr],
        #                   columns=['ID','종목코드','종목명','매수가','총금액',
        #                            '시작시간','종료시간','부분익절율','부분익절수량','최대익절율',
        #                            '부분손절율','부분손절수량','최대손절율'])
        # df['종목코드'] = df['종목코드'].apply('{}'.format)
        for idx, row in self.conditionDataFrame.iterrows():
            if row['ID'] == id:
                self.conditionDataFrame.at[idx, '종목코드'] = str(stockCode)
                self.conditionDataFrame.at[idx, '종목명'] = stockName
                self.conditionDataFrame.at[idx, '매수가'] = buyPrice
                self.conditionDataFrame.at[idx, '총금액'] = totalBuyAmount
                self.conditionDataFrame.at[idx, '시작시간'] = buyStartTime
                self.conditionDataFrame.at[idx, '종료시간'] = buyEndTime
                self.conditionDataFrame.at[idx, '부분익절율'] = profitRate
                self.conditionDataFrame.at[idx, '부분익절수량'] = profitRateVolume
                self.conditionDataFrame.at[idx, '최대익절율'] = maxProfitRate
                self.conditionDataFrame.at[idx, '부분손절율'] = lossRate
                self.conditionDataFrame.at[idx, '부분손절수량'] = lossRateVolume
                self.conditionDataFrame.at[idx, '부분손절율'] = maxLossRate
                dataManager.updateCSVFile('pats_condition.csv', self.conditionDataFrame) #row가 업데이트된 전체 df 다시 저장
                self.notify_observers_condition(row)  # df = condition 변경된 조건 하나만 알림.
                print("save condition")
        # dataManager.updateCSVFile('pats_condition.csv',df)
        # for idx, row in df.iterrows():
        #     self.notify_observers_condition(row) #df = condition
        #     print("save condition")

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