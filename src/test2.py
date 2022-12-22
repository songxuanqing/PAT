import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import datetime
import pandas
from PyQt5.QtCore import *
from time import sleep
import test

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real")
        self.setGeometry(300, 300, 300, 400)

        btn = QPushButton("불러오기", self)
        btn.move(20, 20)
        btn.clicked.connect(self.btn_clicked)

        btn2 = QPushButton("DisConnect", self)
        btn2.move(20, 100)
        btn2.clicked.connect(self.btn2_clicked)

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self._handler_login)
        self.kiwoom.OnReceiveRealData.connect(self._handler_real_data)
        self.CommmConnect()
        self.kiwoomData = test.KiwoomData(self.kiwoom)


    def btn_clicked(self):
        code = ["005930"]
        now = datetime.datetime.now()
        time = now.strftime("%Y%m%d")
        time = "20211031"
        interval = "3"
        type = "틱"
        for i in code:
            self.totalChartData = self.kiwoomData.request_candle_data(code=i, date=time, nPrevNext=0, type=type,
                                                                  interval=interval)
            filename = i+"_1틱봉.csv"
            self.totalChartData.to_csv(filename, mode='w', encoding='cp949', header=True, index=False)
    def btn2_clicked(self):
        self.DisConnectRealData("1000")

    def CommmConnect(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.statusBar().showMessage("login 중 ...")

    def _handler_login(self, err_code):
        if err_code == 0:
            self.statusBar().showMessage("login 완료")


    def _handler_real_data(self, code, real_type, data):
        if real_type == "장시작시간":
            gubun =  self.GetCommRealData(code, 215)
            remained_time =  self.GetCommRealData(code, 214)


    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                              screen_no, code_list, fid_list, real_type)

    def DisConnectRealData(self, screen_no):
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", screen_no)

    def GetCommRealData(self, code, fid):
        data = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()