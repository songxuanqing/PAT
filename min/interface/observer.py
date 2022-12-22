from abc import ABCMeta,abstractmethod
class Subject:
	__metaclass__=ABCMeta
	@abstractmethod
	def register_observer(self):0
	@abstractmethod
	def remove_observer(self):0
	@abstractmethod
	def notify_observers(self):0
class Observer:
	@abstractmethod
	def update(self,data):0
	@abstractmethod
	def register_subject(self,subject):0