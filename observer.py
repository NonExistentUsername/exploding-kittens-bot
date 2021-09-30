
class Observer:
    def __init__(self, observable):
        self.__observable = observable
        self.__func = None
        observable.add_observer(self)

    @property
    def func(self):
        return self.__func

    @func.setter
    def func(self, func):
        self.__func = func

    def notify(self, notification, **data):
        if self.__func != None:
            self.__func(notification, **data)

    def __del__(self):
        self.__observable.remove_observer(self)

class MultiObserver:
    def __init__(self):
        self.__observables = []
        self.__func = None
        
    @property
    def func(self):
        return self.__func

    @func.setter
    def func(self, func):
        self.__func = func

    def add_observable(self, observable):
        observable.add_observer(self)
        self.__observables.append(observable)

    def remove_observable(self, observable):
        if observable in self.__observables:
            observable.remove_observer(self)
            del self.__observables[observable]

    def notify(self, notification, **data):
        if self.__func != None:
            self.__func(notification, **data)

    def __del__(self):
        for observable in self.__observables:
            observable.remove_observer(self)
