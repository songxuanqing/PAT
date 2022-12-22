#-*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import pandas
from datetime import datetime
import os, sys
import openJson
print(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import interface.observer as observer

class KiwoomData(observer.Subject):
    kiwoom = None
    def __init__(self,kiwoom):
        super().__init__()
        self.msg, self.params = openJson.getJsonFiles()
        self.kiwoom = kiwoom
        self._observer_list = []
        self.calculator_event_loop = QEventLoop()
        self.account_event_loop = QEventLoop()

        # 화면 번호
        self.screen_calculation_stock = "2000"
        self.screen_my_account = "1000"
        self.account_stock_dict = {}

        #이벤트 TR슬롯 등록
        self.kiwoom.OnReceiveTrData.connect(self.tr_slot)
        self.is_completed_request = False

        self.account_number = self.get_account_info()



    def register_observer(self, observer):
        if observer in self._observer_list:
            return "Already exist observer!"
        self._observer_list.append(observer)
        return "Success register!"

    def remove_observer(self, observer):
        if observer in self._observer_list:
            self._observer_list.remove(observer)
            return "Success remove!"
        return "observer does not exist."

    def notify_observers(self,df):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        for observer in self._observer_list:
            observer.update(self.is_completed_request,df)

    def getChartData(self):
        return self.calculator_list

    def get_account_evaluation_balance(self, nPrevNext=0):
        accountNumVal = self.params['kiwoomData']['get_account_evaluation_balance']['accountNum']
        passwordVal = self.params['kiwoomData']['get_account_evaluation_balance']['password']
        inputPasswordVal = self.params['kiwoomData']['get_account_evaluation_balance']['inputPassword']
        searchTypeVal = self.params['kiwoomData']['get_account_evaluation_balance']['searchType']
        requestAccountVal = self.params['kiwoomData']['request_candle_data']['requestAccount']
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)",accountNumVal, self.account_number)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", passwordVal, " ")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", inputPasswordVal, "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", searchTypeVal, "1")
        returnCode =self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                requestAccountVal, "opw00018", nPrevNext, self.screen_my_account)

        if not self.account_event_loop.isRunning():
            self.account_event_loop.exec_()
        else:
            print("")
        return self.accountBalance

    def get_account_info(self):
        account_list = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
        account_number = account_list.split(';')[0]
        return account_number

    def request_candle_data(self, code=None, date=None, nPrevNext=0, type=None,
                            interval=None):
        typeMinVal = self.params['kiwoomData']['request_candle_data']['typeMin']
        typeDayVal = self.params['kiwoomData']['request_candle_data']['typeDay']
        typeWeekVal = self.params['kiwoomData']['request_candle_data']['typeWeek']
        typeMonthVal = self.params['kiwoomData']['request_candle_data']['typeMonth']
        codeVal = self.params['kiwoomData']['request_candle_data']['code']
        tickVal = self.params['kiwoomData']['request_candle_data']['tick']
        stdDateVal = self.params['kiwoomData']['request_candle_data']['stdDate']
        editedPriceVal = self.params['kiwoomData']['request_candle_data']['editedPrice']
        endDateVal = self.params['kiwoomData']['request_candle_data']['endDate']
        requestMinVal = self.params['kiwoomData']['request_candle_data']['requestMin']
        requestDayVal = self.params['kiwoomData']['request_candle_data']['requestDay']
        requestWeekVal = self.params['kiwoomData']['request_candle_data']['requestWeek']
        requestMonthVal = self.params['kiwoomData']['request_candle_data']['requestMonth']

        self.code = code
        self.time = date
        self.type = type
        self.interval = interval
        if type==typeMinVal:
            # opt10080 TR 요청(주식 분봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", codeVal, code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", tickVal, interval)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", editedPriceVal, 1)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    requestMinVal, "opt10080", nPrevNext, self.screen_calculation_stock)

        elif type==typeDayVal:
            # opt10080 TR 요청(주식 일봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", codeVal, code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", stdDateVal, date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", editedPriceVal, 1)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    requestDayVal, "opt10081", nPrevNext, self.screen_calculation_stock)
        elif type==typeWeekVal:
            # opt10082 TR 요청(주식 주봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", codeVal, code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", stdDateVal, date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", editedPriceVal, 1)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", endDateVal, "")
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    requestWeekVal, "opt10082", nPrevNext, self.screen_calculation_stock)

        elif type==typeMonthVal:
            # opt10083 TR 요청(주식 월봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", codeVal, code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", stdDateVal, date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", editedPriceVal, 1)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", endDateVal, "")
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    requestMonthVal, "opt10083", nPrevNext, self.screen_calculation_stock)

        if not self.calculator_event_loop.isRunning():
                self.calculator_event_loop.exec_()

        return self.df

    def req_account_data(self):
        self.total_buy_money = 0
        self.total_evaluation_money = 0
        self.total_evaluation_profit_and_loss_money = 0
        self.total_yield = 0
        self.account_stock_dict = {}


    #get slot datas and set data
    def tr_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        requestCandleVal = self.params['kiwoomData']['request_candle_data']['requestCandle']
        requestAccountVal = self.params['kiwoomData']['request_candle_data']['requestAccount']
        codeVal = self.params['kiwoomData']['request_candle_data']['code']
        typeMinVal = self.params['kiwoomData']['request_candle_data']['typeMin']
        typeDayVal = self.params['kiwoomData']['request_candle_data']['typeDay']
        typeWeekVal = self.params['kiwoomData']['request_candle_data']['typeWeek']
        typeMonthVal = self.params['kiwoomData']['request_candle_data']['typeMonth']
        chejanTimeVal = self.params['kiwoomData']['request_candle_data']['chejanTime']
        dateVal = self.params['kiwoomData']['request_candle_data']['date']
        openVal = self.params['kiwoomData']['request_candle_data']['open']
        highVal = self.params['kiwoomData']['request_candle_data']['high']
        lowVal = self.params['kiwoomData']['request_candle_data']['low']
        volumeVal = self.params['kiwoomData']['request_candle_data']['volume']
        currentPriceVal = self.params['kiwoomData']['request_candle_data']['currentPrice']

        if requestCandleVal in sRQName:
            stock_code = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, codeVal)
            stock_code = stock_code.strip()
            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            calculator_list = {'index': [], 'date': [], 'open': [], 'high': [], 'low': [], 'close': [],
                               'volume': []}

            for i in range(cnt):
                if self.type == typeMinVal :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, chejanTimeVal)
                    # format = yyyymmddHHMMSS
                    date = date.replace("      ","")
                    date_to_time = datetime.strptime(date,"%Y%m%d%H%M%S")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m-%d %H:%M')
                    # date = date_to_time.strftime("%H:%M")
                    # date = date[-4:]
                elif self.type == typeDayVal :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, dateVal)
                    # format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m-%d')
                    # date = date_to_time.strftime("%m/%d")
                    # date = date[-4:]
                elif self.type == typeWeekVal :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, dateVal)
                    # format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m-%d')
                    # date = date_to_time.strftime("%m/%d")
                    # date = date[-4:]
                elif self.type == typeMonthVal :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, dateVal)
                    #format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m')
                    # date = date_to_time.strftime("%y/%m")
                    # date = date[-4:]
                open = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, openVal)
                open = open.replace("-","")
                high = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, highVal)
                high = high.replace("-", "")
                low = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, lowVal)
                low = low.replace("-", "")
                close = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, currentPriceVal)
                close = close.replace("-","")
                volume = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, volumeVal)
                calculator_list['index'].append(i)
                calculator_list['date'].append(date_to_time)
                calculator_list['open'].append(int(open))
                calculator_list['high'].append(int(high))
                calculator_list['low'].append(int(low))
                calculator_list['close'].append(int(close))
                calculator_list['volume'].append(int(volume))

            self.calculator_event_loop.exit()
            self.df = pandas.DataFrame(calculator_list,
                                  columns=['index','date', 'open', 'high', 'low', 'close', 'volume'])
            self.df.set_index(self.df['date'],inplace=True)


        elif sRQName == requestAccountVal:
            noVal = self.params['kiwoomData']['request_candle_data']['No']
            accountCodeVal = self.params['kiwoomData']['request_candle_data']['accountCode']
            evalAmountVal = self.params['kiwoomData']['request_candle_data']['evalAmount']
            profitRateVal = self.params['kiwoomData']['request_candle_data']['profitRate']
            buyPriceVal = self.params['kiwoomData']['request_candle_data']['buyPrice']
            buyAmountVal = self.params['kiwoomData']['request_candle_data']['buyAmount']
            holdQtyVal = self.params['kiwoomData']['request_candle_data']['holdQty']
            canSellQtyVal = self.params['kiwoomData']['request_candle_data']['canSellQty']
            currentPriceVal = self.params['kiwoomData']['request_candle_data']['currentPrice']
            totalBuyAmountVal = self.params['kiwoomData']['request_candle_data']['totalBuyAmount']
            totalEvalAmountVal = self.params['kiwoomData']['request_candle_data']['totalEvalAmount']
            totalEvalProfitAmountVal = self.params['kiwoomData']['request_candle_data']['totalEvalProfitAmount']
            totalProfitRateVal = self.params['kiwoomData']['request_candle_data']['totalProfitRate']
            codeNumVal = self.params['kiwoomData']['request_candle_data']['codeNum']
            codeNameVal = self.params['kiwoomData']['request_candle_data']['codeName']
            evalProfitVal = self.params['kiwoomData']['request_candle_data']['evalProfit']

            self.balance_list = {noVal: [], accountCodeVal: [], codeNameVal: [], evalAmountVal: [],
                                 profitRateVal: [], buyPriceVal: [], buyAmountVal: [],
                                 holdQtyVal: [],
                                 canSellQtyVal: [], currentPriceVal: []}
            total_buy_money = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, totalBuyAmountVal)
            self.total_buy_money = int(total_buy_money)

            total_evaluation_money = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, totalEvalAmountVal)
            self.total_evaluation_money = int(total_evaluation_money)

            total_evaluation_profit_and_loss_money = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, totalEvalProfitAmountVal)
            self.total_evaluation_profit_and_loss_money = int(
                total_evaluation_profit_and_loss_money)

            total_yield = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, totalProfitRateVal)
            self.total_yield = float(total_yield)

            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(cnt):
                stock_code = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, codeNumVal)
                stock_code = stock_code.strip()[1:]

                stock_name = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, codeNameVal)
                stock_name = stock_name.strip()  # 필요 없는 공백 제거.

                stock_evaluation_profit_and_loss = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, evalProfitVal)
                stock_evaluation_profit_and_loss = int(
                    stock_evaluation_profit_and_loss)

                stock_yield = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, profitRateVal)
                stock_yield = float(stock_yield)

                stock_buy_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, buyPriceVal)
                stock_buy_money = int(stock_buy_money)

                stock_buy_total_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, buyAmountVal)
                stock_buy_total_money = int(stock_buy_total_money)

                stock_quantity = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, holdQtyVal)
                stock_quantity = int(stock_quantity)

                stock_trade_quantity = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, canSellQtyVal)
                stock_trade_quantity = int(stock_trade_quantity)

                stock_present_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, currentPriceVal)
                stock_present_price = int(stock_present_price)

                if not stock_code in self.account_stock_dict:
                    self.account_stock_dict[stock_code] = {}

                self.balance_list[noVal].append(i)
                self.balance_list[accountCodeVal].append(stock_code)
                self.balance_list[codeNameVal].append(stock_name)
                self.balance_list[evalAmountVal].append(str(stock_evaluation_profit_and_loss))
                self.balance_list[profitRateVal].append(str(stock_yield))
                self.balance_list[buyPriceVal].append(str(stock_buy_money))
                self.balance_list[buyAmountVal].append(str(stock_buy_total_money))
                self.balance_list[holdQtyVal].append(str(stock_quantity))
                self.balance_list[canSellQtyVal].append(str(stock_trade_quantity))
                self.balance_list[currentPriceVal].append(str(stock_present_price))

            if sPrevNext == "2":
                self.get_account_evaluation_balance(2)
            else:
                self.cancel_screen_number(self.screen_my_account)
                self.account_event_loop.exit()


                df = pandas.DataFrame(self.balance_list,
                                      columns=[noVal, accountCodeVal, codeNameVal, evalAmountVal,
                                               profitRateVal, buyPriceVal, buyAmountVal,holdQtyVal,
                                               canSellQtyVal, currentPriceVal])
                df.set_index(noVal, inplace=True)
                self.accountBalance = df



    def cancel_screen_number(self, sScrNo):
        self.kiwoom.dynamicCall("DisconnectRealData(QString)", sScrNo)