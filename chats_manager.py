
class MessageUpdater:

    def __init__(self, chat_id, message_id, updater_func):
        self.__message_id = message_id
        self.__chat_id = chat_id
        self.__updater_func = updater_func

    def __call__(self):
        self.__updater_func(self.__chat_id, self.__message_id)

    def __del__(self):
        self.__updater_func(self.__chat_id, self.__message_id, True)

class ChatsManager:
    def __init__(self):
        self.__updaters = {}

    def set(self, chat_id, message_id, updater_func):
        print('ChatsManager processed set wit args chat_id = {0}, message_id = {1}'.format(chat_id, message_id))
        self.remove(chat_id)
        self.__updaters[chat_id] = MessageUpdater(chat_id, message_id, updater_func)

    def remove(self, chat_id):
        if chat_id in self.__updaters:
            del self.__updaters[chat_id]

    def update(self, chat_id):
        print('process update message in chat_id ', chat_id)

        if chat_id in self.__updaters:
            self.__updaters[chat_id]()
            print('message updated')
        else:
            print('message update error')
