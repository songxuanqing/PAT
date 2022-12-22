from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import pandas
from datetime import datetime
import os, sys
print(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import interface.observer as observer

class KiwoomData(observer.Subject):
    kiwoom = None
    def __init__(self,kiwoom):
        super().__init__()
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

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)",
                                "계좌번호", self.account_number)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", " ")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        returnCode =self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                "계좌평가잔고내역요청", "opw00018", nPrevNext, self.screen_my_account)

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
        self.code = code
        self.time = date
        self.type = type
        self.interval = interval
        if type=="분":
            # opt10080 TR 요청(주식 분봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "틱범위", interval)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    "주식분봉차트조회요청", "opt10080", nPrevNext, self.screen_calculation_stock)

        elif type=="일":
            # opt10080 TR 요청(주식 일봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    "주식일봉차트조회요청", "opt10081", nPrevNext, self.screen_calculation_stock)
        elif type=="주":
            # opt10082 TR 요청(주식 주봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "끝일자", "")
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    "주식주봉차트조회요청", "opt10082", nPrevNext, self.screen_calculation_stock)

        elif type=="달":
            # opt10083 TR 요청(주식 월봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "끝일자", "")
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    "주식월봉차트조회요청", "opt10083", nPrevNext, self.screen_calculation_stock)

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
        if "봉차트조회요청" in sRQName:
            stock_code = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            stock_code = stock_code.strip()
            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            calculator_list = {'index': [], 'date': [], 'open': [], 'high': [], 'low': [], 'close': [],
                               'volume': []}

            for i in range(cnt):
                if self.type == "분" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    # format = yyyymmddHHMMSS
                    date = date.replace("      ","")
                    date_to_time = datetime.strptime(date,"%Y%m%d%H%M%S")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m-%d %H:%M')
                    # date = date_to_time.strftime("%H:%M")
                    # date = date[-4:]
                elif self.type == "일" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    # format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m-%d')
                    # date = date_to_time.strftime("%m/%d")
                    # date = date[-4:]
                elif self.type == "주" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    # format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m-%d')
                    # date = date_to_time.strftime("%m/%d")
                    # date = date[-4:]
                elif self.type == "달" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    #format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                    # date_to_str = datetime.strftime(date_to_time, '%Y-%m')
                    # date = date_to_time.strftime("%y/%m")
                    # date = date[-4:]
                open = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                open = open.replace("-","")
                high = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                high = high.replace("-", "")
                low = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")
                low = low.replace("-", "")
                close = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                close = close.replace("-","")
                volume = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
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


        elif sRQName == "계좌평가잔고내역요청":
            self.balance_list = {'No': [], '코드': [], '종목명': [], '평가금액': [], '수익율(%)': [], '매입가': [], '매입금액': [],
                                 '보유량': [],
                                 '매매가능수량': [], '현재가': []}
            total_buy_money = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            self.total_buy_money = int(total_buy_money)

            total_evaluation_money = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액")
            self.total_evaluation_money = int(total_evaluation_money)

            total_evaluation_profit_and_loss_money = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
            self.total_evaluation_profit_and_loss_money = int(
                total_evaluation_profit_and_loss_money)

            total_yield = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            self.total_yield = float(total_yield)

            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(cnt):
                stock_code = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                stock_code = stock_code.strip()[1:]

                stock_name = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_name = stock_name.strip()  # 필요 없는 공백 제거.

                stock_evaluation_profit_and_loss = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평가손익")
                stock_evaluation_profit_and_loss = int(
                    stock_evaluation_profit_and_loss)

                stock_yield = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                stock_yield = float(stock_yield)

                stock_buy_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                stock_buy_money = int(stock_buy_money)

                stock_buy_total_money = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                stock_buy_total_money = int(stock_buy_total_money)

                stock_quantity = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                stock_quantity = int(stock_quantity)

                stock_trade_quantity = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")
                stock_trade_quantity = int(stock_trade_quantity)

                stock_present_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                stock_present_price = int(stock_present_price)

                if not stock_code in self.account_stock_dict:
                    self.account_stock_dict[stock_code] = {}

                self.balance_list['No'].append(i)
                self.balance_list['코드'].append(stock_code)
                self.balance_list['종목명'].append(stock_name)
                self.balance_list['평가금액'].append(str(stock_evaluation_profit_and_loss))
                self.balance_list['수익율(%)'].append(str(stock_yield))
                self.balance_list['매입가'].append(str(stock_buy_money))
                self.balance_list['매입금액'].append(str(stock_buy_total_money))
                self.balance_list['보유량'].append(str(stock_quantity))
                self.balance_list['매매가능수량'].append(str(stock_trade_quantity))
                self.balance_list['현재가'].append(str(stock_present_price))

            if sPrevNext == "2":
                self.get_account_evaluation_balance(2)
            else:
                self.cancel_screen_number(self.screen_my_account)
                self.account_event_loop.exit()

                df = pandas.DataFrame(self.balance_list,
                                      columns=['No', '코드', '종목명', '평가금액', '수익율(%)', '매입가', '매입금액', '보유량', '매매가능수량',
                                               '현재가'])
                df.set_index("No", inplace=True)
                self.accountBalance = df



    def cancel_screen_number(self, sScrNo):
        self.kiwoom.dynamicCall("DisconnectRealData(QString)", sScrNo)