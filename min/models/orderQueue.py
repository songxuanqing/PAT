from threading import Thread
from time import sleep
import interface.observerOrderQueue as observer
class OrderQueue(observer.Subject):
	list=[];_observer_list=[]
	def __init__(A,kiwoom):A.kiwoom=kiwoom
	def register_observer(A,observer):
		B=observer
		if B in A._observer_list:return'Already exist observer!'
		A._observer_list.append(B);return'Success register!'
	def remove_observer(A,observer):
		B=observer
		if B in A._observer_list:A._observer_list.remove(B);return'Success remove!'
		return'observer does not exist.'
	def notify_observers(A,type,order):
		B='orderQueue'
		for C in A._observer_list:C.update(B,type,order)
	def add(A,order):A.list.append(order)
	def order(B,type,order):
		A=order;B.list.append(A)
		if B.list:
			A=B.list.pop();C=B.kiwoom.dynamicCall('SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)',[A.sRQName,A.sScreenNo,A.sAccNo,A.nOrderType,A.sCode,A.nQty,A.nPrice,A.sHogaGb,A.sOrgOrderNo])
			if C!=0:print('')
			else:B.notify_observers(type,A)