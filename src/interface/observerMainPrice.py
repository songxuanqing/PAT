from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer_mainPrice(self):
        pass

    @abstractmethod
    def remove_observer_mainPrice(self):
        pass

    @abstractmethod
    def notify_observers_mainPrice(self):
        pass

class Observer:

    @abstractmethod
    def update_mainPrice(self, data):
        pass

    @abstractmethod
    def register_subject_mainPrice(self, subject):
        pass