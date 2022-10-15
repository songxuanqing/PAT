class SubIndexList():
    arr = []
    def __init__(self):
        self.setList()

    def setList(self):
        self.arr.append("이평선 5일")
        self.arr.append("이평선 10일")
        self.arr.append("이평선 20일")
        self.arr.append("이평선 60일")
        self.arr.append("RSI")
        self.arr.append("스토캐스틱")
        self.arr.append("MACD")
        self.arr.append("일목균형표")
        self.arr.append("BB")

    def getList(self):
        return self.arr

    def add(self, item):
        self.arr.append(item)