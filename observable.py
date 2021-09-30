

class Observable:
    def _notify(self, notification, **data):
        for observer in self.__observers:
            observer.notify(notification, **data)

    def __init__(self):
        self.__observers = []

    def add_observer(self, observer):
        self.__observers.append(observer)

    def remove_observer(self, observer):
        self.__observers.remove(observer)