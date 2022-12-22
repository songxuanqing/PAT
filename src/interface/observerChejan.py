from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer_chejan(self):
        pass

    @abstractmethod
    def remove_observer_chejan(self):
        pass

    @abstractmethod
    def notify_observers_chejan(self):
        pass

class Observer:

    @abstractmethod
    def update_chejan(self, data):
        pass

    @abstractmethod
    def register_subject_chejan(self, subject):
        pass