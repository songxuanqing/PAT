import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from datetime import datetime
import pandas
from PyQt5.QtCore import *
from time import sleep


class KiwoomData():
    kiwoom = None
    def __init__(self,kiwoom):
        super().__init__()
        self.kiwoom = kiwoom
        self.calculator_event_loop = QEventLoop()

        # 화면 번호
        self.screen_calculation_stock = "9000"

        #이벤트 TR슬롯 등록
        self.kiwoom.OnReceiveTrData.connect(self.tr_slot)



    def request_candle_data(self, code=None, date=None, nPrevNext=0, type=None,
                            interval=None):

        sleep(3)
        if nPrevNext == 0:
            self.calculator_list = {'index': [], 'date': [], 'open': [], 'high': [], 'low': [], 'close': [],
                                    'volume': []}
        else:
            self.calculator_list = self.calculator_list

        self.code = code
        self.time = date
        self.type = type
        self.interval = interval

        if type=="틱":
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "틱범위", interval)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)",
                                    "주식틱차트조회요청", "opt10079", nPrevNext, self.screen_calculation_stock)

        elif type=="분":
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


    #get slot datas and set data
    def tr_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if "봉차트조회요청" in sRQName:
            stock_code = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            stock_code = stock_code.strip()
            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            for i in range(cnt):
                if self.type == "분" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                    # format = yyyymmddHHMMSS
                    date = date.replace("      ","")
                    date_to_time = datetime.strptime(date,"%Y%m%d%H%M%S")
                elif self.type == "일" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    # format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                elif self.type == "주" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    # format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
                elif self.type == "달" :
                    date = self.kiwoom.dynamicCall(
                        "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                    #format = yyyymmdd
                    date = date.replace("            ", "")
                    date_to_time = datetime.strptime(date, "%Y%m%d")
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
                self.calculator_list['index'].append(i)
                self.calculator_list['date'].append(date_to_time)
                self.calculator_list['open'].append(int(open))
                self.calculator_list['high'].append(int(high))
                self.calculator_list['low'].append(int(low))
                self.calculator_list['close'].append(int(close))
                self.calculator_list['volume'].append(int(volume))

            print(str(self.calculator_list))

            if sPrevNext == "2":
                print("if" + sPrevNext)
                # QTest.qWait(3600)  # 3.6초마다 딜레이
                self.request_candle_data(code=self.code, date=self.time, nPrevNext=2, type=self.type,
                                         interval=self.interval)
            else:
                self.calculator_event_loop.exit()
                self.df = pandas.DataFrame(self.calculator_list,
                                           columns=['index', 'date', 'open', 'high', 'low', 'close', 'volume'])
                self.df.set_index(self.df['date'], inplace=True)