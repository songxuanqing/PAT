#-*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import pandas
from time import sleep
import interface.observerAccount as observer
import threading

# class AccountData(observer.Subject):
#     kiwoom = None
#     arr = []
#
#     # def __new__(cls,kiwoom):
#     #     if not hasattr(cls, 'instance'):
#     #         print('create')
#     #         cls.instance = super(AccountData, cls).__new__(cls)
#     #     else:
#     #         print('recycle')
#     #     return cls.instance
#
#     def __init__(self,kiwoom):
#         super().__init__()
#
#
#     #계좌정보 얻어오기
#     def get_account_info(self):
#         account_list = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
#         account_number = account_list.split(';')[0]
#         self.account_number = account_number

