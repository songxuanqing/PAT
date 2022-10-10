from PyQt5 import QtWidgets ,uic
from PyQt5.QtGui import *
from PyQt5 import uic
import models.favoriteList as FavoriteList
import models.stockList as StockList


class MainWindow(QtWidgets.QMainWindow):  # Window 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    form_class = uic.loadUiType("main.ui")
    ocx = None
    #저장소 생성
    #저장소에서  최근 데이터 가져오기
    arr = []
    #즐겨찾기 객체생성
    # favoriteList = FavoriteList.FavoriteList()
    # stocklist = StockList.StockList(ocx)
    # stockList = stocklist.getList()
    # favoriteList.setList(arr)


    def __init__(self,ocx):  # Window 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출
        MainWindow.ocx = ocx
        self.setupUi(self)  # ui 파일 화면 출력
        # self.btnLogin.clicked.connect(self.btn_login)

