from threading import Thread
from time import sleep
import interface.observerOrderQueue as observer

class OrderQueue(observer.Subject):
    list = []
    _observer_list = []
    def __init__(self,kiwoom):
        self.kiwoom = kiwoom

    def register_observer(self, observer):
        if observer in self._observer_list:
            return "Already exist observer!"
        self._observer_list.append(observer)
        return "Success register!"

    def remove_observer(self, observer):
        if observer in self._observer_list:
            self._observer_list.remove(observer)
            return "Success remove!"
        return "observer does not exist."

    def notify_observers(self,type,order):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        source = "orderQueue"
        for observer in self._observer_list:
            observer.update(source,type,order)

    def add(self,order):
        self.list.append(order)

    def order(self,type,order):
        self.list.append(order)
        if self.list:
            order = self.list.pop()
            returnCode = self.kiwoom.dynamicCall(
                "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                [order.사용자구분명, order.화면번호, order.계좌번호, order.주문유형,
                 order.종목코드, order.주문수량, order.주문가격, order.거래구분, order.원주문번호])
            if returnCode != 0:
                print("")
            else:
                self.notify_observers(type,order)

