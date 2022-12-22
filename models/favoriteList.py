#-*- coding: utf-8 -*-
class FavoriteList():
    arr = []
    def __init__(self):
        print("")

    def setList(self, array):
        self.arr = array

    def getList(self):
        return self.arr

    def add(self, item):
        self.arr.append(item)
