import interface.observerOrderQueue as observer
import datetime
import time as Time
import models.accountData as AccountData
import models.order as Order
import models.orderQueue as OrderQueue
import interface.observerOrder as observerOrder
import interface.observerAccount as observerAccount
import interface.observerChejan as observerChejan
import interface.observerMainPrice as observerMainPrice
import pandas
import os, sys
import json
from PyQt5.QtCore import *
from PyQt5 import QtNetwork
import requests
import asyncio
import models.database as Database

class KiwoomRealTimeData(observer.Observer, observerAccount.Observer, observerOrder.Subject, observerChejan.Subject, observerMainPrice.Subject):
    kiwoom = None
    def __init__(self,kiwoom,kiwoomData,conditionList,kiwoomConditionList,AIConditionList,settingPiggleDaoMostVoted):
        super().__init__()
        # 초기화
        self.dataManager = Database.Database()
        self.kiwoom = kiwoom
        self.selectedStock = 0
        self.networkAccessManager = QtNetwork.QNetworkAccessManager()
        self.networkAccessManager.finished.connect(self.handleNetworkResponse)
        self.id = 0
        aiTradingVals = {}
        self.predictRequestDf = pandas.DataFrame({'id': [self.id],
                                                  'aiTradingVals': [aiTradingVals]})
        #주문 목록
        self.orderQueue = OrderQueue.OrderQueue(kiwoom)
        self.register_subject(self.orderQueue)

        # 평가잔고 정보 가져오기
        self.accountData = kiwoomData
        self.balanceInfo = self.accountData.get_account_evaluation_balance()
        self.screen_main = '3000'
        self.screen_condition = '5000'
        self.screen_kiwoom_condition = '6000'
        self.screen_code_kiwoom_condition = '7000'
        self.screen_AI_condition = '8000'
        self.scrren_piggle_dao_most_voted = '9000'

        # self.updateAccountData()
        self.register_subject_account(self.accountData)
        self._observer_list_chejan = []
        self._observer_list_mainPrice = []
        self.chejan_event_loop = QEventLoop()

        self.conditionList = conditionList
        self.conditionStatusList = {'코드': [], 'isBuyOrdered': [], 'isSellOrdered': [],
                      'buyChejan': [],
                      'sellChejan': [],
                      'accumulatedAmount': [],
                      'buyPrice': [], 'buyVolume': [], 'currentProfitRate': []}
        self.conditionStatusDf = self.prepareConditionStatusDf(self.conditionList, self.screen_condition,1)

        self.kiwoomConditionList = kiwoomConditionList
        self.kiwoomConditionStatusList = {'조건코드': [],'코드':[],'isBuyOrdered': [],
                                          'isSellOrdered': [], 'buyChejan':[],'sellChejan':[],
                                          'accumulatedAmount':[],'buyPrice':[],'buyVolume':[],'currentProfitRate':[]}
        self.kiwoomConditionStatusDf = pandas.DataFrame(self.kiwoomConditionStatusList,
                                                  columns=['코드', 'isBuyOrdered', 'isSellOrdered',
                                                           'buyChejan', 'sellChejan', 'accumulatedAmount','buyPrice', 'buyVolume','currentProfitRate'])
        for idx, row in self.kiwoomConditionList.iterrows():
            code = row['코드']
            name = row['조건명']
            self.SendCondition(self.screen_kiwoom_condition, name, code, 1)

        self.AIConditionList = AIConditionList
        self.AIConditionStatusList = {'코드': [], 'isBuyOrdered': [], 'isSellOrdered': [],
                                    'buyChejan': [],
                                    'sellChejan': [],
                                    'accumulatedAmount': [],
                                    'buyPrice': [], 'buyVolume': [], 'currentProfitRate': []}
        self.AIConditionStatusDf = self.prepareConditionStatusDf(self.AIConditionList, self.screen_AI_condition,2)
        self.AIPastDataList = {}
        for idx, row in self.AIConditionList.iterrows():
            totalPastData = None
            code = row['코드']
            if row['AI매매구분']=="일봉 매매":
                now = datetime.datetime.now()
                time = now.strftime("%Y%m%d")
                # AI 자동매매 등록한 순간 과거 데이터에 대한 데이터 프레임 생성
                totalPastData = self.accountData.request_candle_data(code=code,
                                                                     date=time,
                                                                     nPrevNext=0,
                                                                     type="일",
                                                                     interval=1)
            elif row['AI매매구분']=='분봉 매매':
                now = datetime.datetime.now()
                time = now.strftime("%Y%m%d")
                # AI 자동매매 등록한 순간 과거 데이터에 대한 데이터 프레임 생성
                totalPastData = self.accountData.request_candle_data(code=code,
                                                                     date=time,
                                                                     nPrevNext=0,
                                                                     type="분",
                                                                     interval=1)

            totalPastData = totalPastData.drop('index', axis=1)
            totalPastData = totalPastData.drop('date', axis=1)
            totalPastData = totalPastData.drop('open', axis=1)
            totalPastData = totalPastData.drop('high', axis=1)
            totalPastData = totalPastData.drop('low', axis=1)
            totalPastData = totalPastData.drop('volume', axis=1)
            self.AIPastDataList[code] = totalPastData

        #piggle_dao_most_voted 파일 읽어봐서 코드 subscribe_stock_conclusion 화면 등록
        self.piggleDaoMostVotedDf = self.dataManager.readCSVFile("pats_piggle_dao_most_voted.csv")
        self.piggleDaoMostVotedStatusList = {'코드': [], 'isBuyOrdered': [], 'isSellOrdered': [],
                                      'buyChejan': [],
                                      'sellChejan': [],
                                      'accumulatedAmount': [],
                                      'buyPrice': [], 'buyVolume': [], 'currentProfitRate': []}
        self.piggleDaoMostVotedStatusDf = self.prepareConditionStatusDf(self.piggleDaoMostVotedDf, self.scrren_piggle_dao_most_voted,3)
        self.settingPiggleDaoMostVoted = settingPiggleDaoMostVoted

        self._observer_list = []
        self._subject_list = []

        # 실시간 데이터 슬롯 등록
        self.kiwoom.OnReceiveRealData.connect(self._handler_real_data)
        self.kiwoom.OnReceiveRealCondition.connect(self._handler_real_condition)
        self.kiwoom.OnReceiveChejanData.connect(self._receive_chejan_data)

        # self.trading('095570', 5970)

    def SetRemoveReg(self, screen_no, code_list):
        self.kiwoom.dynamicCall("SetRealRemove(QString,QString)",screen_no,code_list)

    def SendConditionStop(self, screen, cond_name, cond_index):
        ret = self.kiwoom.dynamicCall("SendConditionStop(QString, QString, int)", screen, cond_name, cond_index)

    def register_observer_mainPrice(self, observer):
        if observer in self._observer_list_mainPrice:
            return "Already exist observer!"
        self._observer_list_mainPrice.append(observer)
        return "Success register!"

    def remove_observer_mainPrice(self, observer):
        if observer in self._observer_list_mainPrice:
            self._observer_list_mainPrice.remove(observer)
            return "Success remove!"
        return "observer does not exist."

    def notify_observers_mainPrice(self, df):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        for observer in self._observer_list_mainPrice:
            observer.update_mainPrice(df)

    def register_subject(self, subject):
        self.subject = subject
        self.subject.register_observer(self)

    def update(self, source, type, order):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        if source == "kiwoomRealTimeData":
            self.orderQueue.order(type,order)
        elif source == "orderQueue":
            msg = "매매방식: "+str(type)+"\n"+"종목명: "+str(order.sCodeName)+"\n"\
                  +"주문유형:"+str(order.nOrderType)+"\n"\
                      +"주문가격: "+str(order.nPrice)+"\n"+"주문수량: "+str(order.nQty)+"\n"\
                      +"현재수익율: "+str(order.currentProfitRate)+"\n"\
                      +"목표익절율: "+str(order.targetProfitRate)+"\n"\
                      +"목표손절율: "+str(order.targetLossRate)
            self.notify_observers_order(msg)

    def register_observer_chejan(self, observer):
        if observer in self._observer_list_chejan:
            return "Already exist observer!"
        self._observer_list_chejan.append(observer)
        return "Success register!"

    def remove_observer_chejan(self, observer):
        if observer in self._observer_list_chejan:
            self._observer_list_chejan.remove(observer)
            return "Success remove!"
        return "observer does not exist."

    def notify_observers_chejan(self, df):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        for observer in self._observer_list_chejan:
            observer.update_chejan(df)

    def register_observer_order(self, observer):
        if observer in self._observer_list:
            return "Already exist observer!"
        self._observer_list.append(observer)
        return "Success register!"

    def remove_observer_order(self, observer):
        if observer in self._observer_list:
            self._observer_list.remove(observer)
            return "Success remove!"
        return "observer does not exist."

    def notify_observers_order(self, order):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        for observer in self._observer_list:
            observer.update_order(order)



    def get_chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret

    def addConditionDf(self,conditionDf):
        if self.conditionList.empty:
            self.conditionList = conditionDf
        else:
            self.conditionList = pandas.concat([self.conditionList,conditionDf],ignore_index=True) #조건 추가시 기존 df에 추가
        self.conditionStatusDf = self.prepareConditionStatusDf(conditionDf,self.screen_condition,1)

    def editConditionDf(self,conditionDf):
        #self.conditionList 변경한다 df는 그대로 둔다.
        self.conditionList = conditionDf

    def deleteConditionDf(self,codeList):
        for i in codeList:
            for idx, row in self.conditionList.iterrows():
                if row['코드'] == i:
                    self.conditionList = self.conditionList.drop(self.conditionList.index[idx])
            for idx, row in self.conditionStatusDf.iterrows():
                if row['코드'] == i:
                    self.conditionStatusDf = self.conditionStatusDf.drop(self.conditionStatusDf.index[idx])
        self.SetRemoveReg(self.screen_condition,codeList)

    def addKiwoomConditionDf(self,conditionDf):
        if self.kiwoomConditionList.empty:
            self.kiwoomConditionList = conditionDf
        else:
            self.kiwoomConditionList = pandas.concat([self.kiwoomConditionList, conditionDf],ignore_index=True)  # 조건 추가시 기존 df에 추가

        for idx, row in conditionDf.iterrows():
            code = row['코드']
            name = row['조건명']
            self.SendCondition(self.screen_kiwoom_condition, name, code, 1)

    def editKiwoomConditionDf(self,conditionDf):
        self.kiwoomConditionList = conditionDf
        #self.conditionList 변경한다 df는 그대로 둔다.

    def deleteKiwoomConditionDf(self,codeList):
        for i in codeList:
            for idx, row in self.kiwoomConditionList.iterrows():
                if row['코드'] == i:
                    self.kiwoomConditionList = self.kiwoomConditionList.drop(self.kiwoomConditionList.index[idx])
                    self.SendConditionStop(self.screen_kiwoom_condition, row['조건명'], row['코드'])
            for idx, row in self.kiwoomConditionStatusDf.iterrows():
                if row['코드'] == i:
                    self.kiwoomConditionStatusDf = self.kiwoomConditionStatusDf.drop(self.kiwoomConditionStatusDf.index[idx])
                    self.SetRemoveReg(self.screen_code_kiwoom_condition,row['코드'])


    def addAIConditionDf(self,conditionDf):
        if self.AIConditionList.empty:
            self.AIConditionList = conditionDf
        else:
            self.AIConditionList = pandas.concat([self.AIConditionList,conditionDf],ignore_index=True) #조건 추가시 기존 df에 추가
        self.AIConditionStatusDf = self.prepareConditionStatusDf(conditionDf, self.screen_AI_condition, 2)
        for idx, row in conditionDf.iterrows():
            totalPastData = None
            code = row['코드']
            if row['AI매매구분']=="일봉 매매":
                now = datetime.datetime.now()
                time = now.strftime("%Y%m%d")
                # AI 자동매매 등록한 순간 과거 데이터에 대한 데이터 프레임 생성
                totalPastData = self.accountData.request_candle_data(code=code,
                                                                     date=time,
                                                                     nPrevNext=0,
                                                                     type="일",
                                                                     interval=1)
            elif row['AI매매구분']=='분봉 매매':
                now = datetime.datetime.now()
                time = now.strftime("%Y%m%d")
                # AI 자동매매 등록한 순간 과거 데이터에 대한 데이터 프레임 생성
                totalPastData = self.accountData.request_candle_data(code=code,
                                                                     date=time,
                                                                     nPrevNext=0,
                                                                     type="분",
                                                                     interval=1)

            totalPastData = totalPastData.drop('index', axis=1)
            totalPastData = totalPastData.drop('date', axis=1)
            totalPastData = totalPastData.drop('open', axis=1)
            totalPastData = totalPastData.drop('high', axis=1)
            totalPastData = totalPastData.drop('low', axis=1)
            totalPastData = totalPastData.drop('volume', axis=1)
            self.AIPastDataList[code] = totalPastData


    def editAIConditionDf(self,conditionDf):
        #self.conditionList 변경한다 df는 그대로 둔다.
        self.AIConditionList = conditionDf

    def deleteAIConditionDf(self,codeList):
        for i in codeList:
            for idx, row in self.AIConditionList.iterrows():
                if row['코드'] == i:
                    self.AIConditionList = self.AIConditionList.drop(self.AIConditionList.index[idx])
            for idx, row in self.AIConditionStatusDf.iterrows():
                if row['코드'] == i:
                    self.AIConditionStatusDf = self.AIConditionStatusDf.drop(self.AIConditionStatusDf.index[idx])
        self.SetRemoveReg(self.screen_AI_condition,codeList)

    def updateSettingPiggleDaoMostVoted(self,df):
        self.settingPiggleDaoMostVoted = df



    def SendCondition(self, screen, cond_name, cond_index, search):
        ret = self.kiwoom.dynamicCall("SendCondition(QString, QString, int, int)", screen, cond_name, cond_index, search)

    def subscribe_stock_conclusion(self, screen_no,code):
        self.SetRealReg(screen_no, code, "20", 1)
        #fid 20는 주식체결 관련 체결시간

    # 실시간 데이터 연결
    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                              screen_no, code_list, fid_list, real_type)

    # 실시간 데이터 가져오기
    def GetCommRealData(self, code, fid):
        data = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, fid) 
        return data

    # 일반 자동매매 조건 일시정지/시작
    def stopAllCondition(self):
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", self.screen_condition)

    def stopSelectedCondition(self,codeList):
        self.SetRemoveReg(self.screen_condition, codeList)

    def startSelectedCondition(self,codeList):
        for i in codeList:
            self.subscribe_stock_conclusion(self.screen_condition, i)

    # 키움자동매매 조건 일시정지/시작
    def stopAllKiwoomCondition(self):
        for idx, row in self.kiwoomConditionList.iterrows():
            self.SendConditionStop(self.screen_kiwoom_condition, row['조건명'], row['코드'])
        for idx, row in self.kiwoomConditionStatusDf.iterrows():
            self.SetRemoveReg(self.screen_code_kiwoom_condition, row['코드'])

    def stopSelectedKiwoomCondition(self,codeList):
        for i in codeList:
            for idx, row in self.kiwoomConditionList.iterrows():
                if row['코드'] == i:
                    self.SendConditionStop(self.screen_kiwoom_condition, row['조건명'], row['코드'])
            for idx, row in self.kiwoomConditionStatusDf.iterrows():
                if row['코드'] == i:
                    self.SetRemoveReg(self.screen_code_kiwoom_condition,row['코드'])

    def startSelectedKiwoomCondition(self,codeList):
        for i in codeList:
            for idx, row in self.kiwoomConditionList.iterrows():
                if row['코드'] == i:
                    self.SendCondition(self.screen_kiwoom_condition, row['조건명'], row['코드'], 1)

    # AI 자동매매 조건 일시정지/시작
    def stopAllAICondition(self):
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", self.screen_AI_condition)

    def stopSelectedAICondition(self,codeList):
        self.SetRemoveReg(self.screen_AI_condition, codeList)

    def startSelectedAICondition(self,codeList):
        for i in codeList:
            self.subscribe_stock_conclusion(self.screen_AI_condition, i)

    #메인 화면 선택 종목의 실시간 데이터 가져오기
    def getRealPriceData(self,code):
        self.selectedStock = code
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", self.screen_main)
        self.subscribe_stock_conclusion(self.screen_main,code)

    #체결 데이터 받아오기
    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        code = self.get_chejan_data(9001)[1:]
        status = self.get_chejan_data(913)
        chejanPrice = self.get_chejan_data(910)
        chejanVolume = self.get_chejan_data(911)
        buySell = self.get_chejan_data(907)

        if status == "체결": #접수 및 체결
            for idx, row in self.conditionStatusDf.iterrows():
                if row['코드'] == code:
                    if buySell == '1': #매도
                        self.conditionStatusDf.at[idx, 'buyChejan'] = False
                        self.conditionStatusDf.at[idx, 'sellChejan'] = True
                        self.conditionStatusDf.at[idx, 'buyPrice'] = 0
                        self.conditionStatusDf.at[idx, 'buyVolume'] = 0
                    elif buySell == '2': #매수
                        self.conditionStatusDf.at[idx, 'buyChejan'] = True
                        self.conditionStatusDf.at[idx, 'sellChejan'] = False
                        self.conditionStatusDf.at[idx, 'buyPrice'] = chejanPrice
                        self.conditionStatusDf.at[idx, 'buyVolume'] = chejanVolume

            if not self.kiwoomConditionStatusDf.empty:
                for idx, row in self.kiwoomConditionStatusDf.iterrows():
                    if row['코드'] == code:
                        if buySell == '1':
                            self.kiwoomConditionStatusDf.at[idx, 'buyChejan'] = False
                            self.kiwoomConditionStatusDf.at[idx, 'sellChejan'] = True
                            self.kiwoomConditionStatusDf.at[idx, 'buyPrice'] = 0
                            self.kiwoomConditionStatusDf.at[idx, 'buyVolume'] = 0
                        elif buySell == '2':
                            self.kiwoomConditionStatusDf.at[idx, 'buyChejan'] = True
                            self.kiwoomConditionStatusDf.at[idx, 'sellChejan'] = False
                            self.kiwoomConditionStatusDf.at[idx, 'buyPrice'] = chejanPrice
                            self.kiwoomConditionStatusDf.at[idx, 'buyVolume'] = chejanVolume

            for idx, row in self.AIConditionStatusDf.iterrows():
                if row['코드'] == code:
                    if buySell == '1': #매도
                        self.AIConditionStatusDf.at[idx, 'buyChejan'] = False
                        self.AIConditionStatusDf.at[idx, 'sellChejan'] = True
                        self.AIConditionStatusDf.at[idx, 'buyPrice'] = 0
                        self.AIConditionStatusDf.at[idx, 'buyVolume'] = 0
                    elif buySell == '2': #매수
                        self.AIConditionStatusDf.at[idx, 'buyChejan'] = True
                        self.AIConditionStatusDf.at[idx, 'sellChejan'] = False
                        self.AIConditionStatusDf.at[idx, 'buyPrice'] = chejanPrice
                        self.AIConditionStatusDf.at[idx, 'buyVolume'] = chejanVolume

            for idx, row in self.piggleDaoMostVotedStatusDf.iterrows():
                if row['코드'] == code:
                    if buySell == '1': #매도
                        self.piggleDaoMostVotedStatusDf.at[idx, 'buyChejan'] = False
                        self.piggleDaoMostVotedStatusDf.at[idx, 'sellChejan'] = True
                        self.piggleDaoMostVotedStatusDf.at[idx, 'buyPrice'] = 0
                        self.piggleDaoMostVotedStatusDf.at[idx, 'buyVolume'] = 0
                    elif buySell == '2': #매수
                        self.piggleDaoMostVotedStatusDf.at[idx, 'buyChejan'] = True
                        self.piggleDaoMostVotedStatusDf.at[idx, 'sellChejan'] = False
                        self.piggleDaoMostVotedStatusDf.at[idx, 'buyPrice'] = chejanPrice
                        self.piggleDaoMostVotedStatusDf.at[idx, 'buyVolume'] = chejanVolume

            #update_chejan
            for idx, row in self.conditionList.iterrows():
                if row['코드'] == code:
                    name = row['종목명']
                    if buySell == '1':
                        type = "매도"
                    elif buySell == '2':
                        type = "매수"
                    price = str(chejanPrice)
                    volume = str(chejanVolume)
                    profitRate = str(row['부분익절율'])
                    maxProfitRate = str(row['최대익절율'])
                    lossRate = str(row['부분손절율'])
                    maxLossRate = str(row['최대손절율'])
                    currentProfitRate = "0"
                    for idx, row in self.conditionStatusDf.iterrows():
                        if row['코드'] == code:
                            currentProfitRate = str(row['currentProfitRate'])
                        df = pandas.DataFrame([[code, name, type, price, volume, currentProfitRate, profitRate,
                                                maxProfitRate, lossRate, maxLossRate]],
                                              columns=['종목코드', '종목명', '매매구분', '매매가', '매매량', '현재수익율', '부분익절율',
                                                       '최대익절율', '부분손절율', '최대손전율'])
                        self.notify_observers_chejan(df)
                        break

            for idx, row in self.AIConditionList.iterrows():
                if row['코드'] == code:
                    name = row['종목명']
                    if buySell == '1':
                        type = "매도"
                    elif buySell == '2':
                        type = "매수"
                    price = str(chejanPrice)
                    volume = str(chejanVolume)
                    profitRate = str(0.0)
                    maxProfitRate = str(0.0)
                    lossRate = str(0.0)
                    maxLossRate = str(0.0)
                    currentProfitRate = "0"
                    for idx, row in self.AIConditionStatusDf.iterrows():
                        if row['코드'] == code:
                            currentProfitRate = str(row['currentProfitRate'])
                        df = pandas.DataFrame([[code, name, type, price, volume, currentProfitRate, profitRate,
                                                maxProfitRate, lossRate, maxLossRate]],
                                              columns=['종목코드', '종목명', '매매구분', '매매가', '매매량', '현재수익율', '부분익절율',
                                                       '최대익절율', '부분손절율', '최대손전율'])
                        self.notify_observers_chejan(df)
                        break

            for idx, row in self.piggleDaoMostVotedDf.iterrows():
                if row['코드'] == code:
                    name = row['종목명']
                    if buySell == '1':
                        type = "매도"
                    elif buySell == '2':
                        type = "매수"
                    price = str(chejanPrice)
                    volume = str(chejanVolume)
                    profitRate = str(0.0)
                    maxProfitRate = str(0.0)
                    lossRate = str(0.0)
                    maxLossRate = str(0.0)
                    currentProfitRate = "0"
                    for idx, row in self.piggleDaoMostVotedStatusDf.iterrows():
                        if row['코드'] == code:
                            currentProfitRate = str(row['currentProfitRate'])
                        df = pandas.DataFrame([[code, name, type, price, volume, currentProfitRate, profitRate,
                                                maxProfitRate, lossRate, maxLossRate]],
                                              columns=['종목코드', '종목명', '매매구분', '매매가', '매매량', '현재수익율', '부분익절율',
                                                       '최대익절율', '부분손절율', '최대손전율'])
                        self.notify_observers_chejan(df)
                        break


    def _handler_real_condition(self, code, type, cond_name, cond_index):
        if type == 'I':
            self.kiwoomConditionStatusList['조건코드'].append(cond_index)
            self.kiwoomConditionStatusList['코드'].append(code)
            self.kiwoomConditionStatusList['isBuyOrdered'].append(False)
            self.kiwoomConditionStatusList['isSellOrdered'].append(True)
            self.kiwoomConditionStatusList['buyChejan'].append(False)
            self.kiwoomConditionStatusList['sellChejan'].append(False)
            self.kiwoomConditionStatusList['accumulatedAmount'].append(0)
            self.kiwoomConditionStatusList['buyPrice'].append(0)
            self.kiwoomConditionStatusList['buyVolume'].append(0)
            self.kiwoomConditionStatusList['currentProfitRate'].append("0")
            df = pandas.DataFrame(self.kiwoomConditionStatusList,
                                                      columns=['조건코드','코드', 'isBuyOrdered',
                                                               'isSellOrdered','buyChejan','sellChejan',
                                                               'accumulatedAmount','buyPrice','buyVolume','currentProfitRate'])
            self.kiwoomConditionStatusDf = df
            data = self.kiwoomConditionList[self.kiwoomConditionList['코드'] == code]
            for idx,condition in data.iterrows():
                totalBuyAmount = int(condition['종목당금액'])
                buyStartTime = str(condition['시작시간'])
                buyEndTime = str(condition['종료시간'])
                profitRate = float(condition['부분익절율'])
                profitSellVolume = int(condition['부분익절수량']) * 0.01
                maxProfitRate = float(condition['최대익절율'])
                lossRate = float(condition['부분손절율'])
                lossSellVolume = int(condition['부분손절수량']) * 0.01
                maxLossRate = float(condition['최대손절율'])

                # 단일 종목 모니터링 df 만들기
                id = 0
                arr = [id, str(code), "", 0, totalBuyAmount,
                       buyStartTime, buyEndTime, profitRate, profitSellVolume, maxProfitRate,
                       lossRate, lossSellVolume, maxLossRate]
                df = pandas.DataFrame([arr],
                                      columns=['ID', '코드', '종목명', '매수가', '총금액',
                                               '시작시간', '종료시간', '부분익절율', '부분익절수량', '최대익절율',
                                               '부분손절율', '부분손절수량', '최대손절율'])
                pandas.concat([self.self.conditionList, df])
                self.subscribe_stock_conclusion(self.screen_code_kiwoom_condition, code)

    # 실시간 이벤트 처리 핸들러
    def _handler_real_data(self, code, real_type, real_data):

        if code == self.selectedStock:
            # 10 = 현재가, 체결가, 실시간종가
            # 11 = 전일대비
            # 12 = 등락율
            # 13 = 누적거래량
            # 16, 17, 18 = 시가, 고가, 저가
            currentPrice = self.GetCommRealData(code, 10)
            compareToYesterday = self.GetCommRealData(code, 11)
            goDownRate = self.GetCommRealData(code, 12)
            accumulatedVolume = self.GetCommRealData(code, 13)
            startPrice = self.GetCommRealData(code, 16)
            highPrice = self.GetCommRealData(code, 17)
            lowPrice = self.GetCommRealData(code, 18)
            arr = [currentPrice, compareToYesterday, goDownRate, accumulatedVolume, startPrice, highPrice, lowPrice]
            df = pandas.DataFrame([arr], columns=['현재가', '전일대비', '등락율', '누적거래량', '시가', '고가', '저가', ])
            self.notify_observers_mainPrice(df)

        currentPrice = self.GetCommRealData(code, 10)
        if currentPrice!="":
            currentPrice = abs(int(currentPrice))  # +100, -100
            time = self.GetCommRealData(code, 20)
            print("실시간 수신 가격 | " + "코드 : " + str(code) + " 현재가 : " + str(currentPrice))
            self.trading(code, currentPrice)



    def trading(self,code,currentPrice):
        # AI 조건 목록 중에서 종목코드가 맞는 조건만 가져온다.
        AIConditionDf = self.AIConditionList[self.AIConditionList['코드'] == code]
        if not AIConditionDf.empty:
            for idx, condition in AIConditionDf.iterrows():
                # 현재가격 가져오기
                code = str(condition['코드'])
                codeName = condition['종목명']
                dayOrMin = condition['AI매매구분']  # 일봉 매매, 분봉 매매
                totalBuyAmountPerTime = int(condition['회당매수액'])
                totalBuyAmount = int(condition['총금액'])
                buyStartTime = str(condition['시작시간'])
                buyEndTime = str(condition['종료시간'])
                profitRate = float(condition['부분익절율'])
                profitSellVolume = int(condition['부분익절수량']) * 0.01
                maxProfitRate = float(condition['최대익절율'])
                lossRate = float(condition['부분손절율'])
                lossSellVolume = int(condition['부분손절수량']) * 0.01
                maxLossRate = float(condition['최대손절율'])
                startTime = datetime.datetime.strptime(buyStartTime, '%H:%M')
                endTime = datetime.datetime.strptime(buyEndTime, '%H:%M')
                now = datetime.datetime.now()
                isBuyOrdered = False
                isSellOrdered = True

                status = self.AIConditionStatusDf[self.AIConditionStatusDf['코드'] == code]
                if not status.empty:
                    for idx, row in status.iterrows():
                        isBuyOrdered = row['isBuyOrdered']
                        isSellOrdered = row['isSellOrdered']
                        buyChejan = row['buyChejan']
                        sellChejan = row['sellChejan']
                        accumulatedAmount = row['accumulatedAmount']

                if not isBuyOrdered:
                    if (startTime.time() < now.time()) and (now.time() < endTime.time()):
                        if dayOrMin == "일봉 매매":
                            timeFormat = "%Y-%m-%d"
                            url = "day"
                            currentProfitRate = 0.0
                            if(len(self.AIPastDataList[code])>=499):
                                i_num = 499
                            else:
                                i_num = len(self.AIPastDataList[code])-101
                            print(i_num)
                            self.AIFirstBuy(isBuyOrdered,isSellOrdered,buyChejan,
                                            code, codeName, currentPrice,
                                            timeFormat, totalBuyAmountPerTime,totalBuyAmount,
                                            accumulatedAmount, currentProfitRate, profitRate,
                                            lossRate, i_num, url)

                        elif dayOrMin == "분봉 매매":
                            timeFormat = "%Y-%m-%d %H:%M:%S"
                            url = "min"
                            currentProfitRate = 0.0
                            if (len(self.AIPastDataList[code]) >= 799):
                                i_num = 799
                            else:
                                i_num = len(self.AIPastDataList[code])-101
                            self.AIFirstBuy(isBuyOrdered, isSellOrdered, buyChejan,
                                            code, codeName, currentPrice,
                                            timeFormat, totalBuyAmountPerTime, totalBuyAmount,
                                            accumulatedAmount, currentProfitRate, profitRate,
                                            lossRate, i_num, url)

                # 매수를 완료했고, 아직 매도를 하지 않았다면,
                # 오늘 마감 시점에 가격보다 다음날 가격이 더 높아질 것이고, 그 가격이 구매가격 보다 높으면 추가매수
                # 오른 마감 시점에 가격보다 다음날 가격이 더 떨어질 경우, 매도
                if not isSellOrdered and buyChejan:
                    if (startTime.time() < now.time()) and (now.time() < endTime.time()):
                        currentProfitRate = 0.0
                        canSellVolume = 0
                        for idx, row in self.AIConditionStatusDf.iterrows():
                            if row['코드'] == code:
                                prevPrice = int(row['buyPrice'])
                                currentProfitRate = float(((currentPrice - prevPrice) / currentPrice) * 100)
                                canSellVolume = row['buyVolume']
                        if dayOrMin == "일봉 매매":
                            timeFormat = "%Y-%m-%d"
                            url = "day"
                            if (len(self.AIPastDataList[code]) >= 499):
                                i_num = 499
                            else:
                                i_num = len(self.AIPastDataList[code])-101
                            # 시간이 오후 3시 20분 이상일 때만 매매할지 체크한다.
                            dueTime = datetime.datetime.strptime('1998-01-01 15:20:00', '%Y-%m-%d %H:%M:%S')
                            if now.time() >= dueTime.time():
                                self.AISecondBuySell(isBuyOrdered,isSellOrdered,buyChejan,
                                                     code, codeName, currentPrice,
                                                     timeFormat, totalBuyAmountPerTime, totalBuyAmount,
                                                     accumulatedAmount, currentProfitRate, profitRate, lossRate,
                                                     maxProfitRate,
                                                     maxLossRate, profitSellVolume, lossSellVolume, canSellVolume, i_num,
                                                     url)


                        elif dayOrMin == "분봉 매매":
                            timeFormat = "%Y-%m-%d %H:%M:%S"
                            url = "min"
                            if (len(self.AIPastDataList[code]) >= 799):
                                i_num = 799
                            else:
                                i_num = len(self.AIPastDataList[code])-101
                            self.AISecondBuySell(isBuyOrdered, isSellOrdered, buyChejan,
                                                 code, codeName, currentPrice,
                                                 timeFormat, totalBuyAmountPerTime, totalBuyAmount,
                                                 accumulatedAmount, currentProfitRate, profitRate, lossRate,
                                                 maxProfitRate,
                                                 maxLossRate, profitSellVolume, lossSellVolume, canSellVolume, i_num,
                                                 url)

        # 조건 목록 중에서 종목코드가 맞는 조건만 가져온다.
        conditionDf = self.conditionList[self.conditionList['코드'] == code]
        if not conditionDf.empty:
            for idx, condition in conditionDf.iterrows():
                # 현재가격 가져오기
                code = str(condition['코드'])
                codeName = condition['종목명']
                buyPrice = condition['매수가']
                totalBuyAmount = int(condition['총금액'])
                buyStartTime = str(condition['시작시간'])
                buyEndTime = str(condition['종료시간'])
                profitRate = float(condition['부분익절율'])
                profitSellVolume = int(condition['부분익절수량']) * 0.01
                maxProfitRate = float(condition['최대익절율'])
                lossRate = float(condition['부분손절율'])
                lossSellVolume = int(condition['부분손절수량']) * 0.01
                maxLossRate = float(condition['최대손절율'])

                startTime = datetime.datetime.strptime(buyStartTime, '%H:%M')
                endTime = datetime.datetime.strptime(buyEndTime, '%H:%M')
                now = datetime.datetime.now()

                isBuyOrdered = False
                isSellOrdered = True

                if buyPrice == 0:
                    status = self.kiwoomConditionStatusDf[self.kiwoomConditionStatusDf['코드'] == code]
                    if not status.empty:
                        for idx, row in status.iterrows():
                            isBuyOrdered = row['isBuyOrdered']
                            isSellOrdered = row['isSellOrdered']
                            buyChejan = row['buyChejan']
                            sellChejan = row['sellChejan']
                            condi_code = row['조건코드']
                            accumulatedAmount = row['accumulatedAmount']

                else:
                    status = self.conditionStatusDf[self.conditionStatusDf['코드'] == code]
                    if not status.empty:
                        for idx, row in status.iterrows():
                            isBuyOrdered = row['isBuyOrdered']
                            isSellOrdered = row['isSellOrdered']
                            buyChejan = row['buyChejan']
                            sellChejan = row['sellChejan']
                            condi_code = None
                            accumulatedAmount = 0

                if not isBuyOrdered:
                    # 매수로직
                    # 1. 현재시간이 시작과 종료시간 사이인지
                    # 2. 총보유금액이 총금액 조건 미만인지
                    # 3. 현재가격이 목표가(매수가)보다 크거나 같은지.
                    # 4. 목표가로 구매하는 주문 생성
                    if (startTime.time() < now.time()) and (now.time() < endTime.time()):
                        self.conditionBuy(code, codeName, currentPrice, buyPrice,
                                          accumulatedAmount, condi_code, totalBuyAmount, 0.0, profitRate,
                                          lossRate)

                if not isSellOrdered and buyChejan:
                    # 매도로직
                    # 1. 수익율이 최대수익율보다 크거나 같으면 거래량은 매매가능수량
                    # 2. 수익율이 최대익절율보다 작고 부분익절율보다 크거나 같으면 거래량은 매매가능수량 * 부분익절량
                    # 3. 수익율이 최대손절율보다 크거나 같고 부분손절율보다 작으면 거래량은 매매가능수량 * 부분손절량
                    # 4. 수익율이 최대손절율보다 작거나 같으면 거래량은 매매가능수량
                    currentProfitRate = 0.0
                    canSellVolume = 0
                    if buyPrice == 0:
                        for idx, row in self.kiwoomConditionStatusDf.iterrows():
                            if row['코드'] == code:
                                prevPrice = row['buyPrice']
                                currentProfitRate = float(((currentPrice - prevPrice) / currentPrice) * 100)
                                canSellVolume = row['buyVolume']
                    else:
                        for idx, row in self.conditionStatusDf.iterrows():
                            if row['코드'] == code:
                                prevPrice = row['buyPrice']
                                currentProfitRate = float(((currentPrice - int(prevPrice)) / currentPrice) * 100)
                                canSellVolume = row['buyVolume']

                    self.conditionSell(code, codeName, currentPrice, buyPrice, accumulatedAmount, currentProfitRate, profitRate,
                                       lossRate, maxProfitRate, maxLossRate, profitSellVolume, lossSellVolume,
                                       canSellVolume)
        # for i in range(5):
        #     self.tradingForPiggleDaoMostVoted("시가", code, currentPrice)

        now = datetime.datetime.now()
        #피글 DAO 인기 예측 값으로 자동 매매
        openTimeStart = datetime.datetime.strptime('08:50', '%H:%M')
        openTimeEnd = datetime.datetime.strptime('08:59', '%H:%M')
        closeTimeStart = datetime.datetime.strptime('15:20', '%H:%M')
        closeTimeEnd = datetime.datetime.strptime('15:29', '%H:%M')
        #시가 동시호가 시간 내면 시가매수, 종가 동시호가 시간 내면 종가매수
        #예상가격은 piggleDaoMostVotedDf에서 가져오기
        if (openTimeStart.time() < now.time()) and (openTimeEnd.time() > now.time()):
            self.tradingForPiggleDaoMostVoted("시가",code,currentPrice)
        elif (closeTimeStart.time() < now.time()) and (closeTimeEnd.time() > now.time()):
            self.tradingForPiggleDaoMostVoted("종가", code, currentPrice)


    def prepareConditionStatusDf(self,conditionDf,screen_num,type):
        if type == 1:
            statusList = self.conditionStatusList
        elif type == 2:
            statusList = self.AIConditionStatusList
        elif type == 3:
            statusList = self.piggleDaoMostVotedStatusList
        for idx, row in conditionDf.iterrows():
            code = row['코드']
            statusList['코드'].append(code)
            # 실시간 가격 정보 요청
            self.subscribe_stock_conclusion(screen_num, code)
            statusList['isBuyOrdered'].append(False)
            statusList['isSellOrdered'].append(True)
            statusList['buyChejan'].append(False)
            statusList['sellChejan'].append(False)
            statusList['buyPrice'].append(0)
            statusList['buyVolume'].append(0)
            statusList['currentProfitRate'].append("0")
            statusList['accumulatedAmount'].append(0)
        df = pandas.DataFrame(statusList,columns=['코드', 'isBuyOrdered', 'isSellOrdered',
                                                  'buyChejan','sellChejan','accumulatedAmount', 'buyPrice', 'buyVolume',
                                                   'currentProfitRate'])
        if type == 1:
            self.conditionStatusList = statusList
        elif type == 2:
            self.AIConditionStatusList = statusList
        elif type == 3:
            self.piggleDaoMostVotedStatusList = statusList
        return df


    def tradingForPiggleDaoMostVoted(self,type,code,currentPrice):
        isApplied = None
        buyVolume = None
        for idx, row in self.settingPiggleDaoMostVoted.iterrows():
            isApplied = row['적용여부']
            buyVolume = row['매수량']
            break
        if isApplied:
            now = datetime.datetime.now()
            if type == "시가":
                comparisonTime = now.day
                comparisonType = "종가"
            elif type == "종가":
                comparisonTime = now.day + 1
                comparisonType = "시가"
            conditionDf = self.piggleDaoMostVotedDf[self.piggleDaoMostVotedDf['코드'] == code]
            if not conditionDf.empty:
                isBuyOrdered = False
                isSellOrdered = True
                status = self.piggleDaoMostVotedStatusDf[self.piggleDaoMostVotedStatusDf['코드'] == code]
                if not status.empty:
                    for idx, row in status.iterrows():
                        isBuyOrdered = row['isBuyOrdered']
                        isSellOrdered = row['isSellOrdered']
                        buyChejan = row['buyChejan']
                        sellChejan = row['sellChejan']
                        condi_code = None
                        accumulatedAmount = None

                    # 오늘 종가가 오를 것을 예측해야 시가에 매수
                    conditionDf = conditionDf[conditionDf['시종가구분'] == comparisonType]
                    if not conditionDf.empty:
                        for idx, condition in conditionDf.iterrows():
                            forecastDate = condition['예측일']
                            price = condition['예상가']
                            codeName = condition['종목명']
                            if not isBuyOrdered:
                                # 오늘 날짜의 종가를 확인한다.
                                forecast_date = datetime.datetime.strptime(forecastDate, '%Y-%m-%d')
                                if now.year == forecast_date.year and now.month == forecast_date.month and comparisonTime == forecast_date.day:
                                    if (price > currentPrice):
                                        self.piggleDaoMostVotedBuy(code, codeName, currentPrice,
                                                                   currentPrice,
                                                                   buyVolume, 0.0, 0.0)
                                        self.piggleDaoMostVotedDf = self.dataManager.readCSVFile(
                                            "pats_piggle_dao_most_voted.csv")
                                        piggleDaoMostVotedStatusDf = self.prepareConditionStatusDf(
                                            self.piggleDaoMostVotedDf, self.scrren_piggle_dao_most_voted, 3)
                                        # self.piggleDaoMostVotedStatusDf = pandas.concat(
                                        #     [self.piggleDaoMostVotedStatusDf, piggleDaoMostVotedStatusDf])

                            if not isSellOrdered and buyChejan:
                                currentProfitRate = 0.0
                                canSellVolume = 0
                                for idx, row in self.piggleDaoMostVotedStatusDf.iterrows():
                                    if row['코드'] == code:
                                        prevPrice = row['buyPrice']
                                        currentProfitRate = float(
                                            ((currentPrice - int(prevPrice)) / currentPrice) * 100)
                                        canSellVolume = row['buyVolume']
                                self.piggleDaoMostVotedSell(code, codeName, currentPrice, canSellVolume,
                                                            currentProfitRate, 0.0, 0.0)
                                # 새로 파일을 읽어서 업데이트하기
                                self.piggleDaoMostVotedDf = self.dataManager.readCSVFile(
                                    "pats_piggle_dao_most_voted.csv")
                                piggleDaoMostVotedStatusDf = self.prepareConditionStatusDf(self.piggleDaoMostVotedDf,
                                                                                           self.scrren_piggle_dao_most_voted,
                                                                                           3)
                                # self.piggleDaoMostVotedStatusDf = pandas.concat(
                                #     [self.piggleDaoMostVotedStatusDf, piggleDaoMostVotedStatusDf])

    def piggleDaoMostVotedSell(self, code, codeName, currentPrice, sellVolume,currentProfitRate, profitRate, lossRate):
        now = datetime.datetime.now()
        sell_order = Order.Order("현재가매도", "0102", self.accountData.get_account_info(), 2,
                                     code,
                                     codeName, sellVolume, currentPrice, "00", "", profitRate,
                                     lossRate, str(currentProfitRate), now)
        # 주문생성시만 어카운트 정보 업데이트
        self.update("kiwoomRealTimeData", "피글DAO 연동 매매", sell_order)
        self.updatePiggleDaoMostVotedDf(code, currentPrice, None, False, True, False, None, currentProfitRate)

    def piggleDaoMostVotedBuy(self, code, codeName, currentPrice, buyPrice, buyVolume, profitRate, lossRate):
        now = datetime.datetime.now()
        if currentPrice >= buyPrice:
            if buyVolume >= 1:
                buy_order = Order.Order("현재가매수", "0101", self.accountData.get_account_info(), 1,
                                            code,
                                            codeName, buyVolume,
                                            currentPrice, "00", "", profitRate, lossRate,
                                            0.0, now)
                # 주문생성시만 어카운트 정보 업데이트
                self.update("kiwoomRealTimeData", "피글DAO 연동 매매", buy_order)
                self.updatePiggleDaoMostVotedDf(code, currentPrice, buyVolume, True, False, True, None, 0.0)

    def updatePiggleDaoMostVotedDf(self, code, currentPrice, buyVolume, isBuyOrdered, isSellOrdered,
                          sellChejan, buyChejan, currentProfitRate):
        for idx, row in self.piggleDaoMostVotedStatusDf.iterrows():
            if row['코드'] == code:
                self.piggleDaoMostVotedStatusDf.at[idx, 'isBuyOrdered'] = isBuyOrdered
                self.piggleDaoMostVotedStatusDf.at[idx, 'isSellOrdered'] = isSellOrdered
                self.piggleDaoMostVotedStatusDf.at[idx, 'currentProfitRate'] = "{:.3f}".format(currentProfitRate)
                if not isBuyOrdered:
                    self.piggleDaoMostVotedStatusDf.at[idx, 'sellChejan'] = sellChejan
                    self.piggleDaoMostVotedStatusDf.at[idx, 'buyPrice'] = currentPrice
                    self.piggleDaoMostVotedStatusDf.at[idx, 'buyVolume'] = buyVolume
                else:
                    self.piggleDaoMostVotedStatusDf.at[idx, 'buyChejan'] = buyChejan



    def checkSell(self,currentProfitRate, profitRate,
                      lossRate, maxProfitRate, maxLossRate, profitSellVolume, lossSellVolume, canSellVolume):
        sellVolume = 0
        trySell = False
        if currentProfitRate >= maxProfitRate:
            sellVolume = canSellVolume
            trySell = True
        elif (currentProfitRate < maxProfitRate) and (
                currentProfitRate >= profitRate):
            sellVolume = int(canSellVolume * profitSellVolume)
            trySell = True
        elif (currentProfitRate >= maxLossRate) and (currentProfitRate < lossRate):
            sellVolume = int(canSellVolume * lossSellVolume)
            trySell = True
        elif currentProfitRate <= maxLossRate:
            sellVolume = canSellVolume
            trySell = True
        return trySell, sellVolume


    def conditionSell(self, code, codeName, currentPrice, buyPrice, accumulatedAmount, currentProfitRate, profitRate,
                      lossRate, maxProfitRate, maxLossRate, profitSellVolume, lossSellVolume, canSellVolume):
        now = datetime.datetime.now()
        trySell,sellVolume = self.checkSell(currentProfitRate, profitRate,
                      lossRate, maxProfitRate, maxLossRate, profitSellVolume, lossSellVolume, canSellVolume)

        if trySell:
            sell_order = Order.Order("현재가매도", "0102", self.accountData.get_account_info(), 2,
                                     code,
                                     codeName, sellVolume, currentPrice, "00", "", profitRate,
                                     lossRate, str(currentProfitRate), now)
            # 주문생성시만 어카운트 정보 업데이트
            self.update("kiwoomRealTimeData", "단일종목 매매", sell_order)
            if buyPrice == 0:
                self.updateKiwoomConditionDf(code, currentPrice, None, sellVolume, True, False, True, None, currentProfitRate, accumulatedAmount)

            else:
                self.updateConditionDf(code, currentPrice, None, False, True, False, None, currentProfitRate)

    def conditionBuy(self, code, codeName, currentPrice, buyPrice,
                     accumulatedAmount, condi_code, totalBuyAmount, currentProfitRate, profitRate,
                     lossRate):
        now = datetime.datetime.now()
        if buyPrice == 0:
            status = self.kiwoomConditionStatusDf[self.kiwoomConditionStatusDf['코드'] == code]
            if not status.empty:
                df = self.kiwoomConditionList[self.kiwoomConditionList['조건코드'] == condi_code]
                if not df.empty:
                    totalConditionBuyAmount = df['총금액']
                    if totalConditionBuyAmount > accumulatedAmount:
                        # 최대 구매할수 있는 금액에서 현재보유하고 있는량을 제외하고 남은 금액을 현재가로 나눈만큼 구매
                        buyVolume = int(totalBuyAmount / currentPrice)
                        if buyVolume > 1:
                            buy_order = Order.Order("현재가매수", "0101", self.accountData.getAccountInfo(),
                                                    1,
                                                    code,
                                                    codeName, buyVolume,
                                                    currentPrice, "00", "", profitRate, lossRate,
                                                    currentProfitRate, now)
                            # 주문생성시만 어카운트 정보 업데이트
                            self.update("kiwoomRealTimeData","단일종목 매매", buy_order)
                            self.updateKiwoomConditionDf(code, currentPrice, buyVolume, None, True, False, True, None,
                                                         0.0,
                                                         accumulatedAmount)

        else:
            if currentPrice >= buyPrice:
                # 최대 구매할수 있는 금액에서 현재보유하고 있는량을 제외하고 남은 금액을 현재가로 나눈만큼 구매
                buyVolume = int(totalBuyAmount / currentPrice)
                if buyVolume > 1:
                    buy_order = Order.Order("현재가매수", "0101", self.accountData.get_account_info(), 1,
                                            code,
                                            codeName, buyVolume,
                                            currentPrice, "00", "", profitRate, lossRate,
                                            0.0, now)
                    # 주문생성시만 어카운트 정보 업데이트
                    self.update("kiwoomRealTimeData","단일종목 매매", buy_order)
                    self.updateConditionDf(code, currentPrice, buyVolume, True, False, True, None, 0.0)

    def updateConditionDf(self, code, currentPrice, buyVolume, isBuyOrdered, isSellOrdered,
                          sellChejan, buyChejan, currentProfitRate):
        for idx, row in self.conditionStatusDf.iterrows():
            if row['코드'] == code:
                self.conditionStatusDf.at[idx, 'isBuyOrdered'] = isBuyOrdered
                self.conditionStatusDf.at[idx, 'isSellOrdered'] = isSellOrdered
                self.conditionStatusDf.at[idx, 'currentProfitRate'] = "{:.3f}".format(currentProfitRate)

                if not isBuyOrdered:
                    self.conditionStatusDf.at[idx, 'sellChejan'] = sellChejan
                    self.conditionStatusDf.at[idx, 'buyPrice'] = currentPrice
                    self.conditionStatusDf.at[idx, 'buyVolume'] = buyVolume
                else:
                    self.conditionStatusDf.at[idx, 'buyChejan'] = buyChejan

    def updateKiwoomConditionDf(self, code, currentPrice, buyVolume, sellVolume, isBuyOrdered, isSellOrdered,
                                sellChejan, buyChejan, currentProfitRate, accumulatedAmount):
        for idx, row in self.kiwoomConditionStatusDf.iterrows():
            if row['코드'] == code:
                self.kiwoomConditionStatusDf.at[idx, 'isBuyOrdered'] = isBuyOrdered
                self.kiwoomConditionStatusDf.at[idx, 'isSellOrdered'] = isSellOrdered
                self.kiwoomConditionStatusDf.at[idx, 'currentProfitRate'] = "{:.3f}".format(currentProfitRate)

                if not isBuyOrdered:
                    self.kiwoomConditionStatusDf.at[idx, 'sellChejan'] = sellChejan
                    self.kiwoomConditionStatusDf.at[idx, 'buyPrice'] = currentPrice
                    self.kiwoomConditionStatusDf.at[idx, 'buyVolume'] = buyVolume
                    self.kiwoomConditionStatusDf.at[idx, 'accumulatedAmount'] = (
                            accumulatedAmount + (currentPrice * buyVolume))

                else:
                    self.kiwoomConditionStatusDf.at[idx, 'buyChejan'] = buyChejan
                    self.kiwoomConditionStatusDf.at[idx, 'accumulatedAmount'] = (
                            accumulatedAmount - (currentPrice * sellVolume))

    def AIFirstBuy(self, isBuyOrdered,isSellOrdered,buyChejan,code, codeName, currentPrice,
                   timeFormat, totalBuyAmountPerTime,totalBuyAmount,
                   accumulatedAmount, currentProfitRate, profitRate,
                   lossRate, i_num, url):
        print("ai first buy"+str(i_num))
        first, xhat = self.prepareInputData(code, currentPrice, timeFormat, i_num)
        self.id = self.id + 1
        aiTradingVals = {"currentPrice": currentPrice,
                         "totalBuyAmountPerTime": totalBuyAmountPerTime,
                         "totalBuyAmount": totalBuyAmount,
                         "first": first,
                         "code": code, "codeName": codeName,
                         "profitRate": profitRate, "lossRate": lossRate,
                         "currentProfitRate": currentProfitRate,
                         "accumulatedAmount": accumulatedAmount,
                         "isBuyOrdered":isBuyOrdered,"isSellOrdered":isSellOrdered,"buyChejan":buyChejan,
                         "canSellVolume":0,
                         "timeFormat": timeFormat,
                         "i_num": i_num, "url": url}

        payload = {"input": xhat, "id": self.id}
        qJsonDocument = QJsonDocument(payload)
        input = qJsonDocument.toJson()
        newPredictRequestDf = pandas.DataFrame({'id': [self.id],
                                                'aiTradingVals': [aiTradingVals]})
        self.predictRequestDf = pandas.concat([self.predictRequestDf, newPredictRequestDf])
        self.predictRequestDf.set_index(self.predictRequestDf['id'], inplace=True)
        # api = 'http://3.39.84.115:9000/'+url
        api = 'http://localhost:9000/'+url
        self.networkAccessManager.post(QtNetwork.QNetworkRequest(QUrl(api)), input)


    def AISecondBuySell(self, isBuyOrdered,isSellOrdered,buyChejan,code, codeName, currentPrice,
                    timeFormat, totalBuyAmountPerTime, totalBuyAmount,
                    accumulatedAmount, currentProfitRate, profitRate,lossRate,  maxProfitRate,
                    maxLossRate, profitSellVolume, lossSellVolume, canSellVolume, i_num, url):

        now = datetime.datetime.now()

        trySell, sellVolume = self.checkSell(currentProfitRate, profitRate,
                                             lossRate, maxProfitRate, maxLossRate, profitSellVolume, lossSellVolume,
                                             canSellVolume)
        if trySell:
            sell_order = Order.Order("현재가매도", "0102", self.accountData.get_account_info(), 2,
                                     code,
                                     codeName, sellVolume, currentPrice, "00", "", profitRate,
                                     lossRate, str(currentProfitRate), now)
            # 주문생성시만 어카운트 정보 업데이트
            self.update("kiwoomRealTimeData","AI자동 매매", sell_order)
            self.updateAIConditionDf(code, currentPrice, 0, False, True, None, False, currentProfitRate,
                                     accumulatedAmount)
        else:
            first, xhat = self.prepareInputData(code, currentPrice, timeFormat, i_num)
            self.id = self.id + 1
            aiTradingVals = {"currentPrice": currentPrice,
                             "totalBuyAmountPerTime": totalBuyAmountPerTime,
                             "totalBuyAmount": totalBuyAmount,
                             "first": first,
                             "code": code, "codeName": codeName,
                             "profitRate": profitRate, "lossRate": lossRate,
                             "currentProfitRate": currentProfitRate,
                             "accumulatedAmount": accumulatedAmount,
                             "isBuyOrdered": isBuyOrdered, "isSellOrdered": isSellOrdered, "buyChejan": buyChejan,
                             "canSellVolume": canSellVolume,
                             "timeFormat": timeFormat,
                             "i_num": i_num, "url": url}

            payload = {"input": xhat, "id": self.id}
            qJsonDocument = QJsonDocument(payload)
            input = qJsonDocument.toJson()
            newPredictRequestDf = pandas.DataFrame({'id': [self.id],
                                                    'aiTradingVals': [aiTradingVals]})
            self.predictRequestDf = pandas.concat([self.predictRequestDf, newPredictRequestDf])
            self.predictRequestDf.set_index(self.predictRequestDf['id'], inplace=True)
            # api = 'http://3.39.84.115:9000/' + url
            api = 'http://localhost:9000/' + url
            self.networkAccessManager.post(QtNetwork.QNetworkRequest(QUrl(api)), input)


    def updateAIConditionDf(self, code, currentPrice, buyVolume, isBuyOrdered, isSellOrdered,
                            sellChejan, buyChejan, currentProfitRate, accumulatedAmount):
        for idx, row in self.AIConditionStatusDf.iterrows():
            if row['코드'] == code:
                self.AIConditionStatusDf.at[idx, 'isBuyOrdered'] = isBuyOrdered
                self.AIConditionStatusDf.at[idx, 'isSellOrdered'] = isSellOrdered
                self.AIConditionStatusDf.at[idx, 'currentProfitRate'] = "{:.3f}".format(
                    currentProfitRate)
                self.AIConditionStatusDf.at[idx, 'accumulatedAmount'] = (
                        accumulatedAmount + (currentPrice * buyVolume))

                if not isBuyOrdered:
                    self.AIConditionStatusDf.at[idx, 'sellChejan'] = sellChejan
                    self.AIConditionStatusDf.at[idx, 'buyPrice'] = currentPrice
                    self.AIConditionStatusDf.at[idx, 'buyVolume'] = buyVolume

                else:
                    self.AIConditionStatusDf.at[idx, 'buyChejan'] = buyChejan


    def prepareInputData(self,code, currentPrice, timeFormat, i_num):
        now = datetime.datetime.now()
        newDate = now.strftime(timeFormat)
        pastData = self.AIPastDataList[code]
        arr = {'date': [], 'close': []}
        arr['date'].append(newDate)
        arr['close'].append(currentPrice)
        df = pandas.DataFrame(arr, columns=['date', 'close'])
        df.set_index(df['date'], inplace=True)
        df = df.drop('date', axis=1)
        print(len(pastData))
        pastData = pandas.concat([pastData, df]) # 새로운 가격을 데이터프레임에 추가
        print(len(pastData))
        pastData = pastData.iloc[:-1]  # 마지막 데이터프레임 로우를 삭제
        print(len(pastData))
        print(i_num)
        # 예측가 계산
        # 과거데이터 100일치 가져오기>차이값계산 (xhat) 1번에 600개, 0이 가장 최근 값
        window_size = 100
        k = 0
        i = i_num
        first = pastData.iloc[i, k]
        xhat = []
        for j in range(window_size):
            if first != 0:
                datume1 = (pastData.iloc[i + j, k] - first) / first
            else:
                datume1 = 0
            xhat.append(datume1)
        return first, xhat

    # 예측가 계산
    # 과거데이터 100일치 가져오기>차이값계산 (xhat) 1번에 600/900개, 0이 가장 최근 값
    # def getExpectedValue(self, xhat, url):
    #     payload = {"input": xhat}
    #     r = requests.post('http://127.0.0.1:5000/' + url, data=json.dumps(payload))
    #     response = r.json()
    #     yhat = response['output']
    #     print(yhat)
    #     return yhat


    def handleNetworkResponse(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            str1 = reply.readAll()
            parse_doucment = QJsonDocument.fromJson(str1)
            obj = parse_doucment.object()
            id = obj['id']
            output = obj['output']
            yhat = output.toDouble()
            print("yhat"+str(yhat))
            s = self.predictRequestDf['aiTradingVals']
            v = s[id.toInt()]
            self.predictRequestDf = self.predictRequestDf.drop(id.toInt())

            now = datetime.datetime.now()
            currentPrice = v['currentPrice']
            totalBuyAmount = v['totalBuyAmount']
            totalBuyAmountPerTime = v['totalBuyAmountPerTime']
            first = v['first']
            code = v['code']
            codeName = v['codeName']
            profitRate = v['profitRate']
            lossRate = v['lossRate']
            currentProfitRate = v['currentProfitRate']
            accumulatedAmount = v['accumulatedAmount']
            isBuyOrdered = v['isBuyOrdered']
            isSellOrdered = v['isSellOrdered']
            buyChejan = v['buyChejan']
            canSellVolume = v['canSellVolume']

            expected_value = (yhat * first) + first
            status = self.AIConditionStatusDf[self.AIConditionStatusDf['코드'] == code]
            if not status.empty:
                for idx, row in status.iterrows():
                    accumulatedAmount = row['accumulatedAmount']

            if not isBuyOrdered:
                # 만약 예상 가격이 현재가격보다 크면 매매 (미래에 오를 것으로 예상되면 현재 매매)
                if expected_value > currentPrice:
                    if totalBuyAmount > accumulatedAmount:
                        # 최대 구매할수 있는 금액에서 현재보유하고 있는량을 제외하고 남은 금액을 현재가로 나눈만큼 구매
                        buyVolume = int(totalBuyAmountPerTime / currentPrice)
                        if buyVolume > 1:
                            buy_order = Order.Order("현재가매수", "0101", self.accountData.get_account_info(), 1,
                                                    code,
                                                    codeName, buyVolume,
                                                    currentPrice, "00", "", profitRate, lossRate,
                                                    currentProfitRate, now)
                            # 주문생성시만 어카운트 정보 업데이트
                            self.update("kiwoomRealTimeData","AI자동 매매", buy_order)
                            self.updateAIConditionDf(code, currentPrice, buyVolume, True, False, True, None,
                                                     currentProfitRate,
                                                     accumulatedAmount)
            if not isSellOrdered and buyChejan:
                # 만약 예상 가격이 매매가격보다 크면 매매 (미래에 오를 것으로 예상되면 현재 매매) => 추가 매수
                prevPrice = 0
                for idx, row in self.AIConditionStatusDf.iterrows():
                    if row['코드'] == code:
                        prevPrice = int(row['buyPrice'])

                if expected_value > prevPrice and expected_value > currentPrice:
                    if totalBuyAmount > accumulatedAmount:
                        # 최대 구매할수 있는 금액에서 현재보유하고 있는량을 제외하고 남은 금액을 현재가로 나눈만큼 구매
                        buyVolume = int(totalBuyAmountPerTime / currentPrice)
                        if buyVolume > 1:
                            buy_order = Order.Order("현재가매수", "0101",
                                                    self.accountData.get_account_info(), 1,
                                                    code,
                                                    codeName, buyVolume,
                                                    currentPrice, "00", "", profitRate, lossRate,
                                                    str(currentProfitRate), now)
                            # 주문생성시만 어카운트 정보 업데이트
                            self.update("kiwoomRealTimeData","AI자동 매매", buy_order)
                            self.updateAIConditionDf(code, currentPrice, buyVolume, True, False, True, None,
                                                     currentProfitRate,
                                                     accumulatedAmount)

                elif expected_value < currentPrice:
                    sell_order = Order.Order("현재가매도", "0102", self.accountData.get_account_info(),
                                             2,
                                             code,
                                             codeName, canSellVolume, currentPrice, "00", "",
                                             profitRate,
                                             lossRate, str(currentProfitRate), now)
                    # 주문생성시만 어카운트 정보 업데이트
                    self.update("kiwoomRealTimeData","AI자동 매매", sell_order)
                    self.updateAIConditionDf(code, currentPrice, 0, False, True, None, False, currentProfitRate,
                                             accumulatedAmount)
                else:
                    print("")


        else:
            print("Error occured: ", er)
            print(reply.errorString())