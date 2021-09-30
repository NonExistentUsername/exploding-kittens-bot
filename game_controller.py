from notifications import Notifications
from observable import Observable
from settings import Settings
from inline_answer import InlineAnswer
import random
from datetime import datetime

random.seed(datetime.now())

class GameController(Observable):
    class GameStarted(Exception):
        pass
    class GameNotStarted(Exception):
        pass
    class NOPlayersError(Exception):
        pass
    class UserError(Exception):
        pass

    def __throw_thru(self, notification, **data):
        if 'user_id' in data:
            user_id=self.__users[data['user_id']]
            del data['user_id']
            self._notify(notification, **data, user_id=user_id)
        else:
            self._notify(notification, **data)

    def __player_boom_controller(self, **data):
        self.__throw_thru(Notifications.PLAYER_BOOM, **data)

        user_id=self.__users[data['user_id']]

        self.__users.remove(user_id)
        # del self.__user_to_id[user_id]
        self.__user_to_id = {}
        for i in range(len(self.__users)):
            self.__user_to_id[self.__users[i]] = i

        print('game_controller.__player_boom_controller deleted user ', user_id)

    def notify(self, notification, **data):
        if notification in self.__notif_reactions:
            self.__notif_reactions[notification](**data)
        elif notification in self.__throw_thru_notifs:
            self.__throw_thru(notification, **data)
        else:
            self._notify(notification, **data)

    def __init_reactions(self):
        self.__notif_reactions = {}

        self.__notif_reactions[Notifications.PLAYER_BOOM] = self.__player_boom_controller

        self.__throw_thru_notifs = [
                                    Notifications.ANOTHER_PLAYER_TURN,
                                    Notifications.EXPLOSIVE_KITTEN_NEUTRALIZED,
                                    Notifications.EXPLOSIVE_KITTEN_PLACED,
                                    # Notifications.PLAYER_BOOM,
                                    Notifications.PLAYER_SHUFFLED_DECK,
                                    Notifications.PLAYER_RAN_AWAY,
                                    Notifications.NEXT_PLAYER_TURN,
                                    Notifications.PLAYER_ATTACKED,
                                    Notifications.SEE_THE_FUTURE,
                                    Notifications.PLAYER_CANCELED_LAST_ACTION,
                                    Notifications.FAVOR_PLAYER_CHOOSING,
                                    Notifications.FAVOR_CARD_CHOOSING,
                                    Notifications.FAVOR_PLAYER_CHOOSED_WITH_EMPTY_DECK,
                                    Notifications.GAME_END,
                                    Notifications.PLAYER_CHOOSING_CARDS_FOR_COMB,
                                    Notifications.SPECIAL2_DONE,
                                    Notifications.PLAYER_HAS_NO_CARD,
                                    Notifications.PLAYER_CHOOSED,
                                    Notifications.CARD_TYPE_CHOOSING,
                                    Notifications.SPECIAL3_FAILED_WITH_THIS_TYPE,
                                    Notifications.SPECIAL3_DONE,
                                    Notifications.TURN_CANCELED,
                                    Notifications.UNDO_SPECIAL_SUCCESSFULL,
                                    Notifications.CARD_TYPE_CHOOSED,
                                    Notifications.PLAYER_TAKING_CARD_FROM_DISCARD,
                                    Notifications.SPECIAL5_WAINTING,
                                    Notifications.PLAYER_TOOK_CARD_FROM_DISCARD,
                                    Notifications.YOURSELF_CAN_NOT_BE_CHOOSEN,
                                    ]

    def __init__(self):
        super().__init__()
        self.__users = []
        self.__user_to_id = {}
        self.__game = None

        self.__init_reactions()

    def start(self, game_creator):
        if self.__game != None:
            self._notify(Notifications.GAME_ALREADY_STARTED)
        elif not game_creator.check(len(self.__users)):
            self._notify(Notifications.NO_PLAYERS_NOT_VALID)
        else:
            random.shuffle(self.__users)
            for i in range(len(self.__users)):
                self.__user_to_id[self.__users[i]] = i

            __new_settings = Settings()
            __new_settings.number_of_players = len(self.__users)

            self.__game = game_creator(__new_settings)
            self.__game.add_observer(self)

            self._notify(Notifications.GAME_STARTED)
            self._notify(Notifications.NEXT_PLAYER_TURN, user_id=self.__users[self.__game.turn])

    def add_user(self, user_id):
        if self.__game != None:
            self._notify(Notifications.GAME_ALREADY_STARTED)
        else:
            self.__user_to_id[user_id] = len(self.__users)
            self.__users.append(user_id)

            self._notify(Notifications.PLAYER_JOINED)
    
    def remove_user(self, user_id):
        if not user_id in self.__users:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)
        else:
            if self.__game != None:
                self.__game.remove_user(self.__user_to_id[user_id])

            self.__users.remove(user_id)
            # del self.__user_to_id[user_id]
            self.__user_to_id = {}
            for i in range(len(self.__users)):
                self.__user_to_id[self.__users[i]] = i

            self._notify(Notifications.PLAYER_LEAVES)

    def get_users(self):
        return self.__users

    def card_choosen(self, user_id, card_id):
        if self.__game == None:
            raise GameController.GameNotStarted

        self.__game.card_choosen(self.__user_to_id[user_id], card_id)

    ################################################
    
    def take_card(self, user_id):
        if self.__game == None:
            self._notify(Notifications.GAME_NOT_STARTED)
        else:
            self.__game.take_card(self.__user_to_id[user_id])

    def choose_player(self, user_id, user_id_choosen):
        if self.__game != None:
            self.__game.choose_player(self.__user_to_id[user_id], self.__user_to_id[user_id_choosen])

    def choose_card(self, user_id, card_type):
        if self.__game != None:
            self.__game.choose_card(self.__user_to_id[user_id], card_type)

    def special2(self, user_id):
        if self.__game != None:
            self.__game.special2(self.__user_to_id[user_id])
        else:
            self._notify(Notifications.GAME_NOT_STARTED)

    def special3(self, user_id):
        if self.__game != None:
            self.__game.special3(self.__user_to_id[user_id])
        else:
            self._notify(Notifications.GAME_NOT_STARTED)

    def special5(self, user_id):
        if self.__game != None:
            self.__game.special5(self.__user_to_id[user_id])
        else:
            self._notify(Notifications.GAME_NOT_STARTED)

    def undo(self):
        if self.__game != None:
            self.__game.undo()

    @property
    def users(self):
        return self.__users

    def get_no_cards_in_decks(self):
        if self.__game != None:
            return self.__game.get_no_cards_in_decks()
        else:
            return None

    def get_deck_cards_count(self):
        if self.__game == None:
            return None
        else:
            return self.__game.get_deck_cards_count()

    def get_player_deck(self, user_id):
        return self.__game.get_player_deck(self.__user_to_id[user_id])

    def create_inline_answer(self, user_id):
        if self.__game == None:
            return None
        elif not user_id in self.__users:
            return None
        else:
            __answer = InlineAnswer()

            __p_deck = self.__game.get_player_deck(self.__user_to_id[user_id])
            __answer.deck = __p_deck[0]
            __answer.can_move = __p_deck[1]
            __answer.turn = self.__users[self.__game.turn]
            __answer.game_deck_size = self.__game.get_deck_cards_count()
            __answer.hidden = self.__game.is_hidden_stage(self.__user_to_id[user_id])

            return __answer

    def place_card(self, user_id, position):
        if self.__game == None:
            self._notify(Notifications.GAME_NOT_STARTED)
        else:
            self.__game.place_card(self.__user_to_id[user_id], position)

    def boom(self, user_id):
        if self.__game != None:
            self.__game.boom(self.__user_to_id[user_id])

    def see_the_future_successful(self, user_id):
        if self.__game != None:
            self.__game.see_the_future_successful(self.__user_to_id[user_id])

    def undo_special(self, user_id):
        if self.__game != None:
            self.__game.undo_special(self.__user_to_id[user_id])

    def get_deck(self):
        if self.__game != None:
            self._notify(Notifications.PRINT_DECK_SIZE, deck_size = len(self.__game.deck))
        else:
            self._notify(Notifications.GAME_NOT_STARTED)

    @property
    def users(self):
        return self.__users

    

    

