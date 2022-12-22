

class CandleList():
    kiwoom = None
    arr = []

    def __init__(self):
        self.setList()

    def setList(self):
        self.arr.append("1 분")
        self.arr.append("3 분")
        self.arr.append("5 분")
        self.arr.append("10 분")
        self.arr.append("30 분")
        self.arr.append("60 분")
        self.arr.append("1 일")
        self.arr.append("1 주")
        self.arr.append("1 달")


    def getList(self):
        return self.arr

    def add(self, item):
        self.arr.append(item)
