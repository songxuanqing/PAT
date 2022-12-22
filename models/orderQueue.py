#-*- coding: utf-8 -*-
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
                [order.sRQName, order.sScreenNo, order.sAccNo, order.nOrderType,
                 order.sCode, order.nQty, order.nPrice, order.sHogaGb, order.sOrgOrderNo])
            if returnCode != 0:
                print("")
            else:
                self.notify_observers(type,order)

