from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5 import QtCore
import pandas as pd
import interface.conditionRegistration as ConditionRegistration
import interface.codeSearch as codeSearch
import searchCode

class RegisterAICondition(QtWidgets.QDialog, ConditionRegistration.Subject, codeSearch.Observer):
    def __init__(self,dataManager,lastCondtiontionId,stockList,monitoredConditionList):
        super().__init__()
        self.stockList = stockList
        self.monitoredConditionList = monitoredConditionList
        self.lastCondtiontionId = lastCondtiontionId
        self.registerConditionDialog = uic.loadUi("register_ai_condition.ui", self)  # ui 파일 불러오기
        self.bt_searchCode.clicked.connect(self.clickSearch)
        typeList = ["일봉 매매","분봉 매매"]
        self.cb_dayMin.addItems(typeList)
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
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.closeWindow)
        self.bts_oneStock.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.saveCondition(dataManager))
        self.registerConditionDialog.show()

    def closeWindow(self):
        self.close()

    def saveCondition(self,dataManager):
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
            if row['코드'] == stockCode:
                isAlreadyRegistered = True
            else:
                isAlreadyRegistered = False

        if stockCode == "":
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "종목 코드를 입력하세요. ",
                                                       QtWidgets.QMessageBox.Ok)
            if choice == QtWidgets.QMessageBox.Ok:
                pass

        elif isAlreadyRegistered:
            choice = QtWidgets.QMessageBox.information(self, '조건 저장',
                                                       "이미 자동매매로 등록된 종목입니다. ",
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
            arr = [id, str(stockCode), stockName, aiTradingType, totalBuyAmountPerTime, totalBuyAmount,
                   buyStartTime, buyEndTime,profitRate, profitRateVolume, maxProfitRate,
                   lossRate, lossRateVolume, maxLossRate]
            df = pd.DataFrame([arr],
                              columns=['ID', '코드', '종목명', 'AI매매구분', '회당매수액','총금액',
                                       '시작시간', '종료시간', '부분익절율', '부분익절수량', '최대익절율',
                                       '부분손절율', '부분손절수량', '최대손절율'])
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

