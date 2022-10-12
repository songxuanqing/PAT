

class StockList():
    kiwoom = None
    arr = []
    arr.append("039490:삼성전자")
    arr.append("039491:LG전자")
    def __init__(self,kiwoom):
        self.kiwoom = kiwoom
        self.setList("0")

    def setList(self, market):
        #request 종목 코드
        ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", [market])
        code_list = ret.split(';')

        for x in code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            self.arr.append(x + " : " + name)


    def getList(self):
        return self.arr

    def add(self, item):
        self.arr.append(item)
