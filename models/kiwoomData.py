from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas


TR_REQ_TIME_INTERVAL = 0.2

class KiwoomData():
    kiwoom = None
    arr = []
    def __init__(self,kiwoom):
        super().__init__()
        self.kiwoom = kiwoom

        # 화면 번호
        self.screen_calculation_stock = "2000"

        #이벤트 TR슬롯 등록록
        self.event_collection()

    def event_collection(self):
        self.kiwoom.OnReceiveTrData.connect(self.tr_slot)  # 트랜잭션 요청 관련 이벤트

    def day_kiwoom_db(self, stock_code=None, date=None, nPrevNext=0):
        QTest.qWait(3600)  # 3.6초마다 딜레이

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)

        if date != None:  # date가 None일 경우 date는 오늘 날짜 기준
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "주식일봉차트조회요청", "opt10081", nPrevNext, self.screen_calculation_stock)

        if not self.calculator_event_loop.isRunning():
            self.calculator_event_loop.exec_()

    #get slot datas and set data
    def tr_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "주식일봉차트조회요청":
            stock_code = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            stock_code = stock_code.strip()
            cnt = self.kiwoom.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            for i in range(cnt):
                calculator_list = []

                current_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                volume = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trade_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.kiwoom.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                calculator_list.append("")
                calculator_list.append(int(current_price))
                calculator_list.append(int(volume))
                calculator_list.append(int(trade_price))
                calculator_list.append(int(date))
                calculator_list.append(int(start_price))
                calculator_list.append(int(high_price))
                calculator_list.append(int(low_price))
                calculator_list.append("")

                self.calculator_list.append(calculator_list.copy())

            if sPrevNext == "2":

            else:
                self.calculator_event_loop.exit()

    def cancel_screen_number(self, sScrNo):
        self.kiwoon.dynamicCall("DisconnectRealData(QString)", sScrNo)



    def getChartData(self):
        return self.arr

    def setSignalSlots(self):
        self.kiwoom.OnReceiveTrData.connect(self.receiveTrData)

    def setInputValue(self, id, value):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", id, value)

    def commReqData(self, rqname, trcode, next, screen_no):
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        if not self.calculator_event_loop.isRunning():
            self.calculator_event_loop.exec_()

    def commGetData(self, code, real_type, field_name, index, item_name):
        ret = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def getRepeatCnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def receiveTrData(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        print("receiveTrData")
        if next == '2':
            self.kiwoom.remained_data = True
        else:
            self.kiwoom.remained_data = False

        if rqname == "opt10081_req":
            self._opt(rqname, trcode)

        try:
            self.kiwoom.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt(self, rqname, trcode):
        data_cnt = self.getRepeatCnt(trcode, rqname)

        for i in range(data_cnt):
            date = self.commGetData(trcode, "", rqname, i, "일자")
            open = self.commGetData(trcode, "", rqname, i, "시가")
            high = self.commGetData(trcode, "", rqname, i, "고가")
            low = self.commGetData(trcode, "", rqname, i, "저가")
            close = self.commGetData(trcode, "", rqname, i, "현재가")
            volume = self.commGetData(trcode, "", rqname, i, "거래량")
            print(date, open, high, low, close, volume)
            self.data["index"].append(i)
            self.data["date"].append(date)
            self.data["open"].append(open)
            self.data["high"].append(high)
            self.data["low"].append(low)
            self.data["close"].append(close)
            self.data["volume"].append(volume)

        df = pandas.DataFrame(self.data, columns=['index','date','open','high','low','close','volume'])
        df = df.set_index('index')
        self.arr = df

    def requestTR(self,code,time,type,interval):
        if type=="분":
            # opt10080 TR 요청(주식 분봉차트)
            self.setInputValue("종목코드", code)
            self.setInputValue("틱범위", interval)
            self.setInputValue("수정주가구분", 1)
            self.commReqData("opt10080_req", "opt10080", 0, "0101")
            print(code+time+type+interval+"reqTR")
        elif type=="일":
            # opt10080 TR 요청(주식 일봉차트)
            self.setInputValue("종목코드", code)
            self.setInputValue("기준일자", time)
            self.setInputValue("수정주가구분", 1)
            self.commReqData("opt10081_req", "opt10081", 0, "0101")
        elif type=="주":
            # opt10082 TR 요청(주식 주봉차트)
            self.setInputValue("종목코드", code)
            self.setInputValue("기준일자", time)
            self.setInputValue("끝일자", "")
            self.setInputValue("수정주가구분", 1)
            self.commReqData("opt10082_req", "opt10082", 0, "0101")
        elif type=="월":
            # opt10083 TR 요청(주식 월봉차트)
            self.setInputValue("종목코드", code)
            self.setInputValue("기준일자", time)
            self.setInputValue("끝일자", "")
            self.setInputValue("수정주가구분", 1)
            self.commReqData("opt10083_req", "opt10083", 0, "0101")

            self.kiwoom.tr_event_loop.exec_()
            ohlcv = self.kiwoom.tr_data
            while self.has_next_tr_data:
                if type == "분":
                    # opt10080 TR 요청(주식 분봉차트)
                    self.setInputValue("종목코드", code)
                    self.setInputValue("틱범위", interval)
                    self.setInputValue("수정주가구분", 1)
                    self.commReqData("opt10080_req", "opt10080", 0, "0101")
                    print(code + time + type + interval + "reqTR")
                elif type == "일":
                    # opt10080 TR 요청(주식 일봉차트)
                    self.setInputValue("종목코드", code)
                    self.setInputValue("기준일자", time)
                    self.setInputValue("수정주가구분", 1)
                    self.commReqData("opt10081_req", "opt10081", 0, "0101")
                elif type == "주":
                    # opt10082 TR 요청(주식 주봉차트)
                    self.setInputValue("종목코드", code)
                    self.setInputValue("기준일자", time)
                    self.setInputValue("끝일자", "")
                    self.setInputValue("수정주가구분", 1)
                    self.commReqData("opt10082_req", "opt10082", 0, "0101")
                elif type == "월":
                    # opt10083 TR 요청(주식 월봉차트)
                    self.setInputValue("종목코드", code)
                    self.setInputValue("기준일자", time)
                    self.setInputValue("끝일자", "")
                    self.setInputValue("수정주가구분", 1)
                    self.commReqData("opt10083_req", "opt10083", 0, "0101")
                self.kiwoom.tr_event_loop.exec_()

                for key, val in self.kiwoom.tr_data.items():
                    ohlcv[key][-1:] = val

            df = pd.DataFrame(ohlcv, columns=['open', 'high', 'low', 'close', 'volume'], index=ohlcv['date'])
            return df[::-1]
        return self.arr
