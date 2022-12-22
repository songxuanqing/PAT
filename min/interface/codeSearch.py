from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer_searchCode(self):0
	@abstractmethod
	def notify_observers_searchCode(self):0
class Observer:
	@abstractmethod
	def update_searchCode(self,data):0
	@abstractmethod
	def register_subject_searchCode(self,subject):0