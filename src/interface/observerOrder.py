from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer_order(self):
        pass

    @abstractmethod
    def remove_observer_order(self):
        pass

    @abstractmethod
    def notify_observers_order(self):
        pass

class Observer:

    @abstractmethod
    def update_order(self, data):
        pass

    @abstractmethod
    def register_subject_order(self, subject):
        pass