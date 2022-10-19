from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer_searchCode(self):
        pass
    @abstractmethod
    def notify_observers_searchCode(self):
        pass

class Observer:
    @abstractmethod
    def update_searchCode(self, data):
        pass

    @abstractmethod
    def register_subject_searchCode(self, subject):
        pass