from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer_chejan(self):0
	@abstractmethod
	def remove_observer_chejan(self):0
	@abstractmethod
	def notify_observers_chejan(self):0
class Observer:
	@abstractmethod
	def update_chejan(self,data):0
	@abstractmethod
	def register_subject_chejan(self,subject):0