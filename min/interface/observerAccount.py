from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer_account(self):0
	@abstractmethod
	def remove_observer_account(self):0
	@abstractmethod
	def notify_observers_account(self):0
class Observer:
	@abstractmethod
	def update_account(self,data):0
	@abstractmethod
	def register_subject_account(self,subject):0