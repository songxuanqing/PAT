# import models.orderQueue as OrderQueue
# import models.kiwoomRealTimeData as KiwoomRealTimeData
# import models.kiwoomSendCondition as KiwoomSendCondition
# import models.accountData as AccountData
# from threading import Thread
# import interface.observerOrderQueue as observer
# import interface.observerOrder as observerOrder
# import interface.observerChejan as observerChejan
# import interface.observerMainPrice as observerMainPrice
#
#
# class AutoTrading(observer.Observer, observerOrder.Subject, observerChejan.Observer,
#                   observerChejan.Subject, observerMainPrice.Observer, observerMainPrice.Subject):
#     threadList = []
#     kiwoom = None
#     def __init__(self,kiwoom,kiwoomData,conditionList,kiwoomConditionList, AIConditionList):
#         #accountData는 account Data를 수신하는 py 클래스 객체이다.
#         self.orderQueue = OrderQueue.OrderQueue(kiwoom)
#         self.register_subject(self.orderQueue)
#         self.kiwoom = kiwoom
#         self._observer_list = []
#         self._observer_list_chejan = []
#         self._observer_list_mainPrice = []
#         self.conditionList = conditionList
#         self.kiwoomConditionList = kiwoomConditionList
#         self.AIConditionList = AIConditionList
#         self.accountData = kiwoomData
#         self.kiwoomRealTimeData = KiwoomRealTimeData.KiwoomRealTimeData(self.kiwoom,self.accountData,self.conditionList,self.kiwoomConditionList,self.AIConditionList)
#         self.register_subject(self.kiwoomRealTimeData)
#         self.register_subject_chejan(self.kiwoomRealTimeData)
#         self.register_subject_mainPrice(self.kiwoomRealTimeData)
#
#
#     def update(self, source, order):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
#         if source == "kiwoomRealTimeData":
#             self.orderQueue.order(order)
#
#         elif source == "orderQueue":
#             msg = "종목명"+str(order.종목명)+"\n"+"주문유형:"+str(order.주문유형)+"\n"\
#                   +"주문가격:"+str(order.주문가격)+"\n"+"주문수량:"+str(order.주문수량)+"\n"\
#                   +"현재수익율"+str(order.현재수익율)+"\n"\
#                   +"목표익절율:"+str(order.목표익절율)+"\n"\
#                   +"목표손절율:"+str(order.목표손절율)
#             self.notify_observers_order(msg)
#
#     def register_subject_mainPrice(self, subject):
#         # self.subject_mainPrice = subject
#         self.subject_mainPrice.register_observer_mainPrice(self)
#
#     def update_mainPrice(self, df):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
#         self.notify_observers_mainPrice(df)
#
#     def register_subject(self, subject):
#         self.subject = subject
#         self.subject.register_observer(self)
#
#     def update_chejan(self, df):  # 업데이트 메서드가 실행되면 변화된 내용을 출력
#         self.notify_observers_chejan(df)
#
#     def register_subject_chejan(self, subject):
#         self.subject_chejan = subject
#         self.subject_chejan.register_observer_chejan(self)
#
#     def addCondition(self,conditionDf):
#         self.kiwoomRealTimeData.addConditionDf(conditionDf)
#
#     def addKiwoomCondition(self,conditionDf):
#         self.kiwoomRealTimeData.addKiwoomConditionDf(conditionDf)
#
#     def editCondition(self,conditionDf):
#         self.kiwoomRealTimeData.editConditionDf(conditionDf)
#
#     def editKiwoomCondition(self,conditionDf):
#         self.kiwoomRealTimeData.editKiwoomConditionDf(conditionDf)
#
#     def deleteCondition(self,codeList):
#         self.kiwoomRealTimeData.deleteConditionDf(codeList)
#
#     def deleteKiwoomCondition(self, codeList):
#         self.kiwoomRealTimeData.deleteKiwoomConditionDf(codeList)
#
#
#     def register_observer_mainPrice(self, observer):
#         if observer in self._observer_list_mainPrice:
#             return "Already exist observer!"
#         self._observer_list_mainPrice.append(observer)
#         return "Success register!"
#
#     def remove_observer_mainPrice(self, observer):
#         if observer in self._observer_list_mainPrice:
#             self._observer_list_mainPrice.remove(observer)
#             return "Success remove!"
#         return "observer does not exist."
#
#     def notify_observers_mainPrice(self, data):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
#         for observer in self._observer_list_mainPrice:
#             observer.update_mainPrice(data)
#
#     def register_observer_order(self, observer):
#         if observer in self._observer_list:
#             return "Already exist observer!"
#         self._observer_list.append(observer)
#         return "Success register!"
#
#     def remove_observer_order(self, observer):
#         if observer in self._observer_list:
#             self._observer_list.remove(observer)
#             return "Success remove!"
#         return "observer does not exist."
#
#     def notify_observers_order(self, order):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
#         for observer in self._observer_list:
#             observer.update_order(order)
#
#
#     def register_observer_chejan(self, observer):
#         if observer in self._observer_list_chejan:
#             return "Already exist observer!"
#         self._observer_list_chejan.append(observer)
#         return "Success register!"
#
#     def remove_observer_chejan(self, observer):
#         if observer in self._observer_list_chejan:
#             self._observer_list_chejan.remove(observer)
#             return "Success remove!"
#         return "observer does not exist."
#
#     def notify_observers_chejan(self, df):  # 옵저버에게 알리는 부분 (옵저버리스트에 있는 모든 옵저버들의 업데이트 메서드 실행)
#         for observer in self._observer_list_chejan:
#             observer.update_chejan(df)
#
#     def stopAllCondition(self):
#         self.kiwoomRealTimeData.stopAllCondition()
#
#     def stopSelectedCondition(self,codeList):
#         self.kiwoomRealTimeData.stopSelectedCondition(codeList)
#
#     def stopAllKiwoomCondition(self):
#         self.kiwoomRealTimeData.stopAllKiwoomCondition()
#
#     def stopSelectedKiwoomCondition(self,codeList):
#         self.kiwoomRealTimeData.stopSelectedKiwoomCondition(codeList)
#
#     def startSelectedCondition(self,codeList):
#         self.kiwoomRealTimeData.startSelectedCondition(codeList)
#
#     def startSelectedKiwoomCondition(self, codeList):
#         self.kiwoomRealTimeData.startSelectedKiwoomCondition(codeList)
#
#     def getRealPriceData(self,code):
#         self.kiwoomRealTimeData.getRealPriceData(code)