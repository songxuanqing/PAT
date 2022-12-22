from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer_mainPrice(self):0
	@abstractmethod
	def remove_observer_mainPrice(self):0
	@abstractmethod
	def notify_observers_mainPrice(self):0
class Observer:
	@abstractmethod
	def update_mainPrice(self,data):0
	@abstractmethod
	def register_subject_mainPrice(self,subject):0