from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer_account(self):
        pass

    @abstractmethod
    def remove_observer_account(self):
        pass

    @abstractmethod
    def notify_observers_account(self):
        pass

class Observer:

    @abstractmethod
    def update_account(self, data):
        pass

    @abstractmethod
    def register_subject_account(self, subject):
        pass