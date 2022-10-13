

class OrderQueue():
    list = []
    def __init__(self,kiwoom):
        self.kiwoom = kiwoom

    def add(self,order):
        #주문큐에 주문등록 > 하나씩 순차적으로 pop해서 오더할 것(loop로 계속 확인)
        self.list.append(order)

    def order(self):
        print("주문하기")

