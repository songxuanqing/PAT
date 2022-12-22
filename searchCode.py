#-*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pandas as pd
import interface.codeSearch as codeSearch

class SearchCode(QtWidgets.QDialog, codeSearch.Subject):
    def __init__(self,inputCode,stockList):
        super().__init__()
        self.stockList = stockList
        self.inputCode = inputCode
        self.searchCodeDialog = uic.loadUi("searchCode.ui", self)  # ui 파일 불러오기
        self.bt_serachButton.clicked.connect(self.searchButtonClicked)
        self.bt_serachButton.setAutoDefault(True)
        self.bt_serachButton.setDefault(True)
        for i in self.stockList:
            self.tv_searchResult.addItem(i)
        self.et_searchCode.returnPressed.connect(self.searchButtonClicked)
        confirm = self.msg['button']['confirm']
        cancel = self.msg['button']['cancel']
        self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Ok).setText(confirm)
        self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Cancel).setText(cancel)
        self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.confirm)
        self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Ok).setDefault(False)
        self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Cancel).setDefault(False)
        if (self.inputCode != ""):
            self.et_searchCode.setText(self.inputCode)
            self.searchButtonClicked()
        self.searchCodeDialog.show()

    def confirm(self):
        code = self.tv_searchResult.currentItem().text().split(" : ")[0]
        name = self.tv_searchResult.currentItem().text().split(" : ")[1]
        self.notify_observers_searchCode(code,name)

    def searchButtonClicked(self):
        keyword = self.et_searchCode.text()
        self.tv_searchResult.clear()
        searchedResult = []
        if keyword == "":
            for i in self.stockList:
                searchedResult.append(i)
                self.tv_searchResult.addItem(i)
        #search result
        elif keyword != "":
            for i in self.stockList:
                if keyword in i:
                    searchedResult.append(i)
                    self.tv_searchResult.addItem(i)

    def register_observer_searchCode(self, observer):
        self.observer = observer

    def notify_observers_searchCode(self,code,name):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        self.observer.update_searchCode(code,name)