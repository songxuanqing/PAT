from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer_condition(self):0
	@abstractmethod
	def notify_observers_condition(self):0
class Observer:
	@abstractmethod
	def update_condition(self,data):0
	@abstractmethod
	def register_subject_condition(self,subject):0