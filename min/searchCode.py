from PyQt5 import QtWidgets,uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pandas as pd,interface.codeSearch as codeSearch
class SearchCode(QtWidgets.QDialog,codeSearch.Subject):
	def __init__(self,inputCode,stockList):
		B=False;A='button';super().__init__();self.stockList=stockList;self.inputCode=inputCode;self.searchCodeDialog=uic.loadUi('searchCode.ui',self);self.bt_serachButton.clicked.connect(self.searchButtonClicked);self.bt_serachButton.setAutoDefault(True);self.bt_serachButton.setDefault(True)
		for i in self.stockList:self.tv_searchResult.addItem(i)
		self.et_searchCode.returnPressed.connect(self.searchButtonClicked);confirm=self.msg[A]['confirm'];cancel=self.msg[A]['cancel'];self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Ok).setText(confirm);self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Cancel).setText(cancel);self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.confirm);self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Ok).setDefault(B);self.bts_searchCode.button(QtWidgets.QDialogButtonBox.Cancel).setDefault(B)
		if self.inputCode!='':self.et_searchCode.setText(self.inputCode);self.searchButtonClicked()
		self.searchCodeDialog.show()
	def confirm(self):A=' : ';code=self.tv_searchResult.currentItem().text().split(A)[0];name=self.tv_searchResult.currentItem().text().split(A)[1];self.notify_observers_searchCode(code,name)
	def searchButtonClicked(self):
		keyword=self.et_searchCode.text();self.tv_searchResult.clear();searchedResult=[]
		if keyword=='':
			for i in self.stockList:searchedResult.append(i);self.tv_searchResult.addItem(i)
		elif keyword!='':
			for i in self.stockList:
				if keyword in i:searchedResult.append(i);self.tv_searchResult.addItem(i)
	def register_observer_searchCode(self,observer):self.observer=observer
	def notify_observers_searchCode(self,code,name):self.observer.update_searchCode(code,name)