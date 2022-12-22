from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer_subIndex(self):
        pass

    @abstractmethod
    def remove_observer_subIndex(self):
        pass

    @abstractmethod
    def notify_observers_subIndex(self):
        pass

class Observer:

    @abstractmethod
    def update_subIndex(self):
        pass

    @abstractmethod
    def register_subject_subIndex(self, subject):
        pass