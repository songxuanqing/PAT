import models.orderQueue as OrderQueue
import models.kiwoomRealTimeData as KiwoomRealTimeData
from threading import Thread
import interface.observerOrderQueue as observer
import interface.observerOrder as observerOrder


class AutoTrading(observer.Observer, observerOrder.Subject):
    threadList = []
    def __init__(self,kiwoom,conditionList,accoutData):
        #accountData는 account Data를 수신하는 py 클래스 객체이다.
        self.orderQueue = OrderQueue.OrderQueue(kiwoom)
        self._observer_list = []
        self._subject_list = []
        #조건수만큼 Thread 생성
        for idx, row in conditionList.iterrows():
            #row = condition
            kiwoomRealTimeData = KiwoomRealTimeData.KiwoomRealTimeData(kiwoom,row,accoutData)
            self.addThread(kiwoomRealTimeData)
            self._subject_list.append(kiwoomRealTimeData)

        #관찰대상 등록
        for i in self._subject_list:
            self.register_subject(i)


    def update(self, order):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        self.notify_observers_order(order)
        self.orderQueue.add(order)

    def register_subject(self, subject):
        self.subject = subject
        self.subject.register_observer(self)

    def addThread(self, threadObj):
        th = Thread(target=threadObj.run(), args=())
        self.threadList.append(th)
        th.start()

    def register_observer_order(self, observer):
        if observer in self._observer_list:
            return "Already exist observer!"
        self._observer_list.append(observer)
        return "Success register!"

    def remove_observer_order(self, observer):
        if observer in self._observer_list:
            self._observer_list.remove(observer)
            return "Success remove!"
        return "observer does not exist."

    def notify_observers_order(self, order):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
        for observer in self._observer_list:
            observer.update_order(order)