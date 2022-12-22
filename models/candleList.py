#-*- coding: utf-8 -*-
import openJson

class CandleList():
    kiwoom = None
    arr = []

    def __init__(self):
        self.msg, self.params = openJson.getJsonFiles()
        self.setList()

    def setList(self):
        min1Val = self.params['candleList']['min1']
        min3Val = self.params['candleList']['min3']
        min5Val = self.params['candleList']['min5']
        min10Val = self.params['candleList']['min10']
        min30Val = self.params['candleList']['min30']
        min60Val = self.params['candleList']['min60']
        day1Val = self.params['candleList']['day1']
        week1Val = self.params['candleList']['week1']
        month1Val = self.params['candleList']['month1']

        self.arr.append(min1Val)
        self.arr.append(min3Val)
        self.arr.append(min5Val)
        self.arr.append(min10Val)
        self.arr.append(min30Val)
        self.arr.append(min60Val)
        self.arr.append(day1Val)
        self.arr.append(week1Val)
        self.arr.append(month1Val)


    def getList(self):
        return self.arr

    def add(self, item):
        self.arr.append(item)
