import models.orderQueue as OrderQueue
import models.kiwoomRealTimeData as KiwoomRealTimeData
from threading import Thread
import interface.observerOrderQueue as observer
import interface.observerOrder as observerOrder


class AutoTrading(observer.Observer, observerOrder.Subject):
    threadList = []
    kiwoom = None
    def __init__(self,kiwoom,conditionList,accoutData):
        #accountData는 account Data를 수신하는 py 클래스 객체이다.
        self.orderQueue = OrderQueue.OrderQueue(kiwoom)
        self.register_subject(self.orderQueue)
        self.kiwoom = kiwoom
        self._observer_list = []
        self._subject_list = []
        self.conditionList = conditionList
        #조건수만큼 Thread 생성
        for idx, row in conditionList.iterrows():
            #row = condition
            self.addCondition(row)
            # kiwoomRealTimeData = KiwoomRealTimeData.KiwoomRealTimeData(self.kiwoom, row)
            # self.addThread(kiwoomRealTimeData)
            # self._subject_list.append(kiwoomRealTimeData)

        #관찰대상 등록
        for i in self._subject_list:
            self.register_subject(i)


    def update(self, source, order):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
        if source == "kiwoomRealTimeData":
            self.orderQueue.add(order)
        elif source == "orderQueue":
            msg = "종목명"+str(order.종목명)+"\n"+"주문유형:"+str(order.주문유형)+"\n"\
                  +"주문가격:"+str(order.주문가격)+"\n"+"주문수량:"+str(order.주문수량)+"\n"\
                  +"현재수익율:"+str(order.현재수익율)+"\n"+"목표익절율:"+str(order.목표익절율)+"\n"\
                  +"목표손절율:"+str(order.목표손절율)
            self.notify_observers_order(msg)

    def register_subject(self, subject):
        self.subject = subject
        self.subject.register_observer(self)

    def addThread(self, kiwoomRealTimeData):
        # self.worker = Worker()  # 백그라운드에서 돌아갈 인스턴스 소환
        # self.worker_thread = QThread()  # 따로 돌아갈 thread를 하나 생성
        # self.worker.moveToThread(self.worker_thread)  # worker를 만들어둔 쓰레드에 넣어줍니다
        # self.worker_thread.start()  # 쓰레드를 실행합니다.
        th = Thread(target=kiwoomRealTimeData.run(), args=())
        self.threadList.append(th)
        th.daemon = True
        th.start()

    def addCondition(self,condition):
        self.conditionList.append(condition)
        kiwoomRealTimeData = KiwoomRealTimeData.KiwoomRealTimeData(self.kiwoom, condition)
        self.addThread(kiwoomRealTimeData)
        self._subject_list.append(kiwoomRealTimeData)

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

    def DisConnectRealData(self, screen_no):
        print("DisConnectRealData")
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", screen_no)

