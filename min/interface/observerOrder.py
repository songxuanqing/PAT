from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer_order(self):0
	@abstractmethod
	def remove_observer_order(self):0
	@abstractmethod
	def notify_observers_order(self):0
class Observer:
	@abstractmethod
	def update_order(self,data):0
	@abstractmethod
	def register_subject_order(self,subject):0