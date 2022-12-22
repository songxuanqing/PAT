#-*- coding: utf-8 -*-
import openJson

class SubIndexList():
    arr = []
    def __init__(self):
        self.msg, self.params = openJson.getJsonFiles()
        self.setList()

    def setList(self):
        mavg5 = self.params["mainWindow"]["subIndex"]["mavg5"]
        mavg10 = self.params["mainWindow"]["subIndex"]["mavg10"]
        mavg20 = self.params["mainWindow"]["subIndex"]["mavg20"]
        mavg60 = self.params["mainWindow"]["subIndex"]["mavg60"]
        rsi = self.params["mainWindow"]["subIndex"]["rsi"]
        sc = self.params["mainWindow"]["subIndex"]["sc"]
        macd = self.params["mainWindow"]["subIndex"]["macd"]
        ilmock = self.params["mainWindow"]["subIndex"]["ilmock"]
        bb = self.params["mainWindow"]["subIndex"]["bb"]

        self.arr.append(mavg5)
        self.arr.append(mavg10)
        self.arr.append(mavg20)
        self.arr.append(mavg60)
        self.arr.append(rsi)
        self.arr.append(sc)
        self.arr.append(macd)
        self.arr.append(ilmock)
        self.arr.append(bb)

    def getList(self):
        return self.arr

    def add(self, item):
        self.arr.append(item)