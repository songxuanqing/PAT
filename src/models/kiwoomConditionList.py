import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import pandas


class KiwoomConditionList():
    def __init__(self,kiwoom):
        self.kiwoom = kiwoom
        self.GetConditionLoad()
        self.kiwoom.OnReceiveConditionVer.connect(self._handler_condition_load)
        self.kiwoomConditionList = self.GetConditionNameList()

    def _handler_condition_load(self, ret, msg):
        print("")

    def GetConditionLoad(self):
        self.kiwoom.dynamicCall("GetConditionLoad()")

    def GetConditionNameList(self):
        data = self.kiwoom.dynamicCall("GetConditionNameList()")
        conditions = data.split(";")[:-1]
        self.condition_list = []
        for condition in conditions:
            index, name = condition.split('^')
            self.condition_list.append(index + " : " + name)
        return self.condition_list

