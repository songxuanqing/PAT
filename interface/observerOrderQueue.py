from abc import ABCMeta, abstractmethod

class Subject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def register_observer(self):
        pass

    @abstractmethod
    def remove_observer(self):
        pass

    @abstractmethod
    def notify_observers(self):
        pass

class Observer:

    @abstractmethod
    def update(self, temperature, humidity, pressure):
        pass

    @abstractmethod
    def register_subject(self, subject):
        pass