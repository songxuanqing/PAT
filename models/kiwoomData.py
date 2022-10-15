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

TR_REQ_TIME_INTERVAL = 0.2

class KiwoomData(observer.Subject):
    kiwoom = None

    def __init__(self,kiwoom):
        super().__init__()
        self.kiwoom = kiwoom
        self._observer_list = []
        self.calculator_list = {'index':[],'date':[],'open':[],'high':[],'low':[],'close':[],'volume':[]}
        self.calculator_event_loop = QEventLoop()

        # 화면 번호
        self.screen_calculation_stock = "2000"

        #이벤트 TR슬롯 등록
        self.kiwoom.OnReceiveTrData.connect(self.tr_slot)

        self.is_completed_request = False


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

        elif type=="월":
            # opt10083 TR 요청(주식 월봉차트)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "끝일자", "")
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    "주식월봉차트조회요청", "opt10083", nPrevNext, self.screen_calculation_stock)

        if not self.calculator_event_loop.isRunning():
                self.calculator_event_loop.exec_()

    #get slot datas and set data
    def tr_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if "봉차트조회요청" in sRQName:
            stock_code = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            stock_code = stock_code.strip()
            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            for i in range(cnt):
                # self.calculator_list = []
                close = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                volume = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                if self.type == "분" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    # format = yyyymmddHHMM
                    # date_to_time = datetime.strptime(date,"%Y%m%d%H%M")
                    # date = date_to_time.strftime("%H:%M")
                    date = date[-4:]
                elif self.type == "일" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    # format = yyyymmdd
                    # date_to_time = datetime.strptime(date, "%Y%m%d")
                    # date = date_to_time.strftime("%m/%d")
                    date = date[-4:]
                elif self.type == "주" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    # format = yyyymmdd
                    # date_to_time = datetime.strptime(date, "%Y%m%d%H%M")
                    # date = date_to_time.strftime("%m/%d")
                    date = date[-4:]
                elif self.type == "월" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    #format = yyyymm
                    # date_to_time = datetime.strptime(date, "%Y%m")
                    # date = date_to_time.strftime("%y/%m")
                    date = date[-4:]
                open = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")
                self.calculator_list['index'].append(i)
                self.calculator_list['date'].append(date)
                self.calculator_list['open'].append(int(open))
                self.calculator_list['high'].append(int(high))
                self.calculator_list['low'].append(int(low))
                self.calculator_list['close'].append(int(close))
                self.calculator_list['volume'].append(int(volume))

        # if sPrevNext == "2":
        #     print("if" + sPrevNext)
        #     # QTest.qWait(3600)  # 3.6초마다 딜레이
        #     self.request_candle_data(code=self.code, date=self.time, nPrevNext=2, type=self.type,
        #                 interval=self.interval)
        # else:
            self.calculator_event_loop.exit()
            df = pandas.DataFrame(self.calculator_list,
                                  columns=['index','date', 'open', 'high', 'low', 'close', 'volume'])
            df.set_index(df['date'],inplace=True)
            self.is_completed_request = True
            self.notify_observers(df)
            print(df)
            print("notify_observers()")


    def cancel_screen_number(self, sScrNo):
        self.kiwoon.dynamicCall("DisconnectRealData(QString)", sScrNo)
