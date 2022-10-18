from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer_condition(self):
        pass
    @abstractmethod
    def notify_observers_condition(self):
        pass

class Observer:
    @abstractmethod
    def update_condition(self, data):
        pass

    @abstractmethod
    def register_subject_condition(self, subject):
        pass