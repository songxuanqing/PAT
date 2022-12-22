from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer_subIndex(self):0
	@abstractmethod
	def remove_observer_subIndex(self):0
	@abstractmethod
	def notify_observers_subIndex(self):0
class Observer:
	@abstractmethod
	def update_subIndex(self):0
	@abstractmethod
	def register_subject_subIndex(self,subject):0