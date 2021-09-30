from game_controller import GameController
from ekgame import EKGameCreator
from notifications import Notifications
from observable import Observable

class GamesManager(Observable):
    class UserError(Exception):
        pass

    def __throw_thru(self, notification, **data):
        if 'user_id' in data:
            chat_id = self.__user_to_game[data['user_id']]
            self._notify(notification, **data, chat_id=chat_id)
        else:
            self._notify(notification, **data)

    def __player_leaves_controller(self):
        del self.__user_to_game[self.__user_id]
        self._notify(Notifications.PLAYER_LEAVES, chat_id = self.__game_id)

    def __player_joined_controller(self):
        self.__user_to_game[self.__user_id] = self.__game_id
        self._notify(Notifications.PLAYER_JOINED)

    def __player_boom_controller(self, **data):
        self._notify(Notifications.PLAYER_BOOM, chat_id=self.__user_to_game[data['user_id']])
        del self.__user_to_game[data['user_id']]
        print('games_manager.__player_boom_controller deleted user ', data['user_id'])

    def __game_end_controller(self, **data):
        game_id = self.__user_to_game[data['user_id']]
        
        self._notify(Notifications.GAME_END, **data, chat_id=self.__user_to_game[data['user_id']], users=self.__game_controllers[game_id].users)

        for user_id in self.__game_controllers[game_id].users:
            del self.__user_to_game[user_id]
        del self.__game_controllers[game_id]

    def notify(self, notification, **data):
        if notification in self.__notif_reactions:
            if notification == Notifications.PLAYER_CANCELED_LAST_ACTION:
                print(self.__notif_reactions)
            self.__notif_reactions[notification](**data)
        elif notification in self.__throw_thru_notifs:
            self.__throw_thru(notification, **data)
        else:
            self._notify(notification, **data)

    def __init_reactions(self):
        self.__notif_reactions = {}

        self.__notif_reactions[Notifications.PLAYER_LEAVES] = self.__player_leaves_controller
        self.__notif_reactions[Notifications.PLAYER_JOINED] = self.__player_joined_controller
        self.__notif_reactions[Notifications.PLAYER_BOOM] = self.__player_boom_controller
        self.__notif_reactions[Notifications.GAME_END] = self.__game_end_controller
        
        self.__throw_thru_notifs = [
                                    Notifications.NEXT_PLAYER_TURN,
                                    Notifications.PLAYER_RAN_AWAY,
                                    Notifications.PLAYER_SHUFFLED_DECK,
                                    Notifications.EXPLOSIVE_KITTEN_PLACED,
                                    Notifications.EXPLOSIVE_KITTEN_NEUTRALIZED,
                                    Notifications.PLAYER_ATTACKED,
                                    Notifications.SEE_THE_FUTURE,
                                    Notifications.PLAYER_CANCELED_LAST_ACTION,
                                    Notifications.FAVOR_PLAYER_CHOOSING,
                                    Notifications.FAVOR_CARD_CHOOSING,
                                    Notifications.FAVOR_PLAYER_CHOOSED_WITH_EMPTY_DECK,
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
        self.__game_controllers = {}
        self.__user_to_game = {}

        self.__init_reactions()

    def create_game(self, game_id):
        if game_id in self.__game_controllers:
            self._notify(Notifications.GAME_ALREADY_CREATED)
        else:
            self.__game_controllers[game_id] = GameController()
            self.__game_controllers[game_id].add_observer(self)

            self._notify(Notifications.GAME_CREATED)
        
    def close_game(self, game_id):
        if not game_id in self.__game_controllers:
            self._notify(Notifications.GAME_NOT_CREATED)
        else:
            self._notify(Notifications.GAME_CLOSED, users=self.__game_controllers[game_id].users)

            for user_id in self.__game_controllers[game_id].users:
                del self.__user_to_game[user_id]
            del self.__game_controllers[game_id]


    def join_game(self, game_id, user_id):
        if not game_id in self.__game_controllers:
            self._notify(Notifications.GAME_NOT_CREATED)
        elif user_id in self.__user_to_game:
            if game_id != self.__user_to_game[user_id]:
                self._notify(Notifications.PLAYER_IN_ANOTHER_GAME)
            else:
                self._notify(Notifications.PLAYER_ALREADY_IN_GAME)
        else:
            self.__game_id = game_id
            self.__user_id = user_id

            self.__game_controllers[game_id].add_user(user_id)
    
    def leave_game(self, game_id, user_id):
        if user_id in self.__user_to_game and game_id != self.__user_to_game[user_id]:
            self._notify(Notifications.PLAYER_IN_ANOTHER_GAME)
        elif not game_id in self.__game_controllers:
            self._notify(Notifications.GAME_NOT_CREATED)
        elif not user_id in self.__user_to_game:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)
        else: 
            self.__game_id = game_id
            self.__user_id = user_id
            
            self.__game_controllers[game_id].remove_user(user_id)

            # self._notify(Notifications.PLAYER_LEAVES, chat_id = game_id)

    def leave_all_games(self, user_id):
        if not user_id in self.__user_to_game:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)
        else:
            game_id = self.__user_to_game[user_id]

            self.__game_id = game_id
            self.__user_id = user_id
            
            self.__game_controllers[game_id].remove_user(user_id)
    
    ################################################

    def start_game(self, game_id):
        if not game_id in self.__game_controllers:
            self._notify(Notifications.GAME_NOT_CREATED)
        else:
            self.__game_controllers[game_id].start(EKGameCreator())

    def card_choosen(self, user_id, card_id):
        if not user_id in self.__user_to_game:
            return
        
        self.__game_controllers[self.__user_to_game[user_id]].card_choosen(user_id, card_id)

    ################################################

    def create_inline_answer(self, user_id):
        if not user_id in self.__user_to_game:
            return None
        else:
            return self.__game_controllers[self.__user_to_game[user_id]].create_inline_answer(user_id)
        
    def take_card(self, user_id):
        if not user_id in self.__user_to_game:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)
        else:
            self.__game_controllers[self.__user_to_game[user_id]].take_card(user_id)

    def undo(self, game_id):
        if game_id in self.__game_controllers:
            self.__game_controllers[game_id].undo()

    def get_game_id(self, user_id):
        if not user_id in self.__user_to_game:
            return None
        return self.__user_to_game[user_id]

    def special2(self, user_id):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].special2(user_id)
        else:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)

    def special3(self, user_id):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].special3(user_id)
        else:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)

    def special5(self, user_id):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].special5(user_id)
        else:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)

    def get_users_count(self, game_id):
        if game_id in self.__game_controllers:
            return len(self.__game_controllers[game_id].users)
        else:
            return None

    def get_users(self, game_id):
        if game_id in self.__game_controllers:
            return self.__game_controllers[game_id].get_users()
        else:
            return None

    def get_no_cards_in_decks(self, game_id):
        if game_id in self.__game_controllers:
            return self.__game_controllers[game_id].get_no_cards_in_decks()
        else:
            return None

    def get_deck_cards_count(self, game_id):
        print('get_deck_cards_count processed')
        if not game_id in self.__game_controllers:
            return None
        else:
            return self.__game_controllers[game_id].get_deck_cards_count()

    # def get_deck_cards_count_by_user_id(self, user_id):
    #     if not user_id in self.__user_to_game:
    #         # self._notify(Notifications.PLAYER_NOT_IN_GAME)
    #         return None
    #     else:
    #         return self.__game_controllers[self.__user_to_game[user_id]].get_deck_cards_count()

    def place_card(self, user_id, position):
        if not user_id in self.__user_to_game:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)
        else:
            self.__game_controllers[self.__user_to_game[user_id]].place_card(user_id, position)

    def boom(self, user_id):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].boom(user_id)

    def see_the_future_successful(self, user_id):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].see_the_future_successful(user_id)

    def choose_player(self, user_id, user_id_choosen):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].choose_player(user_id, user_id_choosen)

    def choose_card(self, user_id, card_type):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].choose_card(user_id, card_type)

    def undo_special(self, user_id):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].undo_special(user_id)

    def get_deck(self, user_id):
        if user_id in self.__user_to_game:
            self.__game_controllers[self.__user_to_game[user_id]].get_deck()
        else:
            self._notify(Notifications.PLAYER_NOT_IN_GAME)