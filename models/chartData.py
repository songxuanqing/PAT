from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas


TR_REQ_TIME_INTERVAL = 0.2

class ChartData():
    arr = []

    def __init__(self,kiwoom):
        super().__init__()
        self.kiwoom = kiwoom
        self.setSignalSlots()

    def getChartData(self):
        return self.arr

    def setSignalSlots(self):
        self.kiwoom.OnReceiveTrData.connect(self.receiveTrData)

    def setInputValue(self, id, value):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", id, value)

    def commReqData(self, rqname, trcode, next, screen_no):
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.kiwoom.tr_event_loop = QEventLoop()
        self.kiwoom.tr_event_loop.exec_()

    def commGetData(self, code, real_type, field_name, index, item_name):
        ret = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def getRepeatCnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def receiveTrData(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
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
        return self.arr
        # while self.remainedData == True:
        #     time.sleep(TR_REQ_TIME_INTERVAL)
        #     self.setInputValue("종목코드", "039490")
        #     self.setInputValue("기준일자", "20170224")
        #     self.setInputValue("수정주가구분", 1)
        #     self.commReqData("opt10081_req", "opt10081", 2, "0101")
