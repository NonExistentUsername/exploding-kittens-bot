from observable import Observable
from observer import Observer, MultiObserver
from notifications import Notifications

class NotificationsProcessor:
    def __notify_processor(self, notification, **data):
        if notification in self.__reactions:
            print('Notification process reactions: ', notification.name)
            self.__reactions[notification](**data)
        else:
            print('Notification skipped: ', notification.name)

    def __init__(self, observable):
        self.__observer = Observer(observable)
        self.__observer.func = self.__notify_processor
        self.__reactions = {}

    def bind(self, notification, func):
        self.__reactions[notification] = func
        
    def unbind(self, notification):
        if notification in self.__reactions:
            del self.__reactions[notification]

class MultiNotificationsProcessor:
    def __notify_processor(self, notification, **data):
        if notification in self.__reactions:
            self.__reactions[notification](**data)
        else:
            print('(Multi)Notification skipped: ', notification.name)

    def __init__(self):
        self.__multiobserver = MultiObserver()
        self.__multiobserver.func = self.__notify_processor
        self.__reactions = {}

    def add(self, observable):
        self.__multiobserver.add_observable(observable)

    def remove(self, observable):
        self.__multiobserver.remove_observable(observable)

    def bind(self, notification, func):
        self.__reactions[notification] = func
        
    def unbind(self, notification):
        if notification in self.__reactions:
            del self.__reactions[notification]