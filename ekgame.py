import random
import time

from notifications import Notifications
from observable import Observable
from game import Game
from game import GameCreator
from ekdeck import EKDeck
from player import Player
from cards import *
import threading

class Locker:
    __cnt = 0

    def __init__(self, lock):
        self.__lock = lock
        self.__lock.acquire()
        Locker.__cnt += 1
        # print('Locker acquire() cnt: {0}'.format(Locker.__cnt))

    def __del__(self):
        self.__lock.release()
        Locker.__cnt -= 1
        # print('Locker release() cnt: {0}'.format(Locker.__cnt))

class GameStages(Enum):
    PLAYER_TURN = 0
    
    EXPLOSIVE_KITTEN = 1
    EXPLOSIVE_KITTEN_NEUTRALIZED = 2

    FAVOR_PLAYER_CHOOSING = 3
    FAVOR_CANCELING = 11
    FAVOR_CARD_CHOOSING = 4
    
    SPECIAL2_PLAYER_CARDS_CHOOSING = 5
    SPECIAL2_PLAYER_FAVOR_CHOOSING = 6
    SPECIAL2_PLAYER_CANCELING = 10

    SPECIAL3_PLAYER_CARDS_CHOOSING = 7
    SPECIAL3_PLAYER_FAVOR_CHOOSING = 8
    SPECIAL3_PLAYER_CARD_TYPE_CHOOSING = 9
    SPECIAL3_PLAYER_CANCELING = 12

    SPECIAL5_PLAYER_CARDS_CHOOSING = 13
    SPECIAL5_PLAYER_TAKING_CARD = 14
    SPECIAL5_PLAYER_CANCELING = 15

def thread_no_card_waiting(get_i_func, func_s, func_f):
    print('thread_no_card_waiting started with cnt = ', get_i_func())

    while time.time() < get_i_func()[1] + GameStatus.time_for_card_no:
        print('thread_no_card_waiting slipping {0}'.format(get_i_func()[1] + GameStatus.time_for_card_no - time.time()))
        time.sleep(get_i_func()[1] + GameStatus.time_for_card_no - time.time())

    print("thread_no_card_waiting cnt = ", get_i_func())
    if get_i_func()[0] % 2 == 1:
        print("thread_no_card_waiting process func_s() ")
        func_s()
    else:
        print("thread_no_card_waiting process func_f()")
        func_f()
    # cnt = 1

class GameStatus:
    time_for_card_no = 10

    def __init__(self):
        self.__active_player = 0
        self.__stage = GameStages.PLAYER_TURN
        self.__exp_kitten = None
        self.__favor = None
        self.__can_no_move = False
        self.__additional_turns = 0
        self.__special = []

        self.__no_card_cnt = 1
    
    @property
    def no_card_cnt(self):
        return self.__no_card_cnt

    @no_card_cnt.setter
    def no_card_cnt(self, val):
        self.__no_card_cnt = val

    @property
    def active_player(self):
        return self.__active_player
    
    @active_player.setter
    def active_player(self, val):
        self.__active_player = val

    @property
    def stage(self):
        return self.__stage
    
    @stage.setter
    def stage(self, val):
        self.__stage = val

    @property
    def explosive_kitten(self):
        return self.__exp_kitten

    @explosive_kitten.setter
    def explosive_kitten(self, val):
        self.__exp_kitten = val

    @property
    def favor(self):
        return self.__favor

    @favor.setter
    def favor(self, val):
        self.__favor = val

    @property
    def can_no_move(self):
        return self.__can_no_move

    @can_no_move.setter
    def can_no_move(self, val):
        self.__can_no_move = val

    @property
    def additional_turns(self):
        return self.__additional_turns
    
    @additional_turns.setter
    def additional_turns(self, val):
        self.__additional_turns = val

    @property
    def special(self):
        return self.__special

    @property
    def last_no_time(self):
        return self.__last_no_time

    @last_no_time.setter
    def last_no_time(self, val):
        self.__last_no_time = val

    def special_add(self, card_id):
        self.__special.append(card_id)

    def special_clear(self):
        self.__special.clear()

    def copy(self):
        __copy_game_status = GameStatus()
        __copy_game_status.__active_player = self.__active_player
        __copy_game_status.__stage = self.__stage
        __copy_game_status.__exp_kitten = self.__exp_kitten
        __copy_game_status.__favor = self.__favor
        __copy_game_status.__can_no_move = self.__can_no_move
        __copy_game_status.__additional_turns = self.__additional_turns
        return __copy_game_status

class EKGame(Observable):
    class NOPlayerError(Exception):
        pass

    @staticmethod
    def __generate_players(deck, no_players, no_cardsper_player):
        _result = []

        for i in range(no_players):
            _new_deck = []
            for j in range(no_cardsper_player):
                _new_deck.append(deck.pop())
            _result.append(Player(_new_deck))

        return _result
    
    def __init__(self, settings, deck):
        self.__lock = threading.RLock()

        lock = Locker(self.__lock)

        super().__init__()
        
        self.__previous_game_position = None
        self.__deck = deck
        self.__discard = []
        self.__status = GameStatus()
        self.__players = EKGame.__generate_players(self.__deck, settings.number_of_players, settings.number_of_cards_per_player)

        self.__init_cc_processors()
    
    def remove_user(self, user_id):
        lock = Locker(self.__lock)

        if user_id in self.__players:
            self.__status.can_no_move = False
            self.__status.stage = GameStages.PLAYER_TURN

            self.__players.remove(user_id)

            __deck_size = len(self.__deck)
            for i in range(__deck_size):
                __card_id = self.__deck[__deck_size - 1 - i]
                __type = convert_card_type_no_name(__card_id)
                if __type == CardTypes.EXPLOSIVE_KITTEN:
                    self.__deck.remove(__card_id)
                    break

            if len(self.__players) == 1:
                self._notify(Notifications.GAME_END, user_id=0)
            else:
                self._notify(Notifications.NEXT_PLAYER_TURN, user_id=min(user_id, len(self.__players) - 1))
        else:
            print('ERROR: game.remove_user(user_id) SKIPPED')

    ###########################################################################################
    
    def card_choosen(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.SPECIAL5_PLAYER_TAKING_CARD:
            self.__special5_take_card(user_id, card_id)
            return
        elif not card_id in self.__players[user_id].deck:
            print('ERROR: game.card_chosen(user_id, card_id) SKIPPED (TIP: player with user_id doesnt have card_id)')
            return
        else:
            print('card_choosen with id = ', card_id)

        if self.__status.stage in [
                                    GameStages.FAVOR_CARD_CHOOSING,
                                    GameStages.SPECIAL2_PLAYER_CARDS_CHOOSING,
                                    GameStages.SPECIAL3_PLAYER_CARDS_CHOOSING,
                                    GameStages.SPECIAL5_PLAYER_CARDS_CHOOSING,
                                    GameStages.SPECIAL5_PLAYER_TAKING_CARD,
                                    ]:
            self.__player_discard_card(user_id, card_id)
            return

        card_type = convert_card_id_to_type(card_id)
        if card_type in self.__cc_processors:
            self.__cc_processors[card_type](user_id, card_id)
        else:
            print('skipped card_choosen for card_type: ', card_type.name)

    def __init_cc_processors(self):
        lock = Locker(self.__lock)

        self.__cc_processors = {}

        self.__cc_processors[CardTypes.NEUTRALIZE] = self.__neutralize
        self.__cc_processors[CardTypes.SHUFFLE] = self.__shuffle
        self.__cc_processors[CardTypes.SEE_THE_FUTURE] = self.__see_the_future
        self.__cc_processors[CardTypes.ATTACK] = self.__attack
        self.__cc_processors[CardTypes.NO] = self.__no
        self.__cc_processors[CardTypes.RUN_AWAY] = self.__run_away
        self.__cc_processors[CardTypes.FAVOR] = self.__favor

        # self.__lock.release()
        # print("__init_cc_processors self.__lock.release()")
    
    ###########################################################################################

    def __next_turn(self):
        lock = Locker(self.__lock)

        self.__status.stage = GameStages.PLAYER_TURN

        if self.__status.additional_turns > 0:
            self.__status.additional_turns -= 1
        else:
            self.__status.active_player = (self.__status.active_player + 1) % len(self.__players)
            self._notify(Notifications.NEXT_PLAYER_TURN, user_id=self.__status.active_player)

        # self.__lock.release()
        # print("__next_turn self.__lock.release()")

    def __discard_card(self, user_id, card_id):
        lock = Locker(self.__lock)

        self.__players[user_id].remove_card(card_id)
        self.__discard.append(card_id)

        # self.__lock.release()
        # print("__discard_card self.__lock.release()")

    def take_card(self, user_id):
        lock = Locker(self.__lock)

        if self.__status.active_player != user_id:
            self._notify(Notifications.ANOTHER_PLAYER_TURN, user_id=self.__status.active_player)
        elif self.__status.stage == GameStages.PLAYER_TURN:
            self.__status.can_no_move = False

            card_id = self.__deck.pop()

            if convert_card_id_to_type(card_id) == CardTypes.EXPLOSIVE_KITTEN:
                self._notify(Notifications.EXPLOSIVE_KITTEN, card_id=card_id)
                self.__status.stage = GameStages.EXPLOSIVE_KITTEN
                self.__status.explosive_kitten = card_id
            else:
                self.__players[user_id].add_card(card_id)
                self._notify(Notifications.CARD_TAKEN)
                self.__next_turn()
        else:
            print('WARNING: game.take_card(user_id) SKIPPED (TIP: STAGE != PLAYER_TURN')

        # self.__lock.release()
        # print("take_card self.__lock.release()")

    def __choose_player_successful(self, user_id, user_id_choosen):
        print("__choose_player_successful waiting.............")

        lock = Locker(self.__lock)

        print("__choose_player_successful {0} {1}".format(user_id, user_id_choosen))

        self.__status.can_no_move = False

        if self.__status.stage == GameStages.FAVOR_CANCELING:
            self.__status.no_card_cnt = 1
            
            self.__status.stage = GameStages.FAVOR_CARD_CHOOSING

            self._notify(Notifications.FAVOR_CARD_CHOOSING, user_id=user_id_choosen)
        elif self.__status.stage == GameStages.SPECIAL2_PLAYER_CANCELING:
            __card_pos = random.randint(0, len(self.__players[user_id_choosen].deck) - 1)
            __card_id = self.__players[user_id_choosen].deck[__card_pos]
            self.__players[user_id].add_card(__card_id)
            self.__players[user_id_choosen].remove_card(__card_id)

            self.__status.stage = GameStages.PLAYER_TURN

            self._notify(Notifications.SPECIAL2_DONE, user_id=user_id_choosen)
        elif self.__status.stage == GameStages.SPECIAL3_PLAYER_CANCELING:
            __card_id = -1
            for card_id in self.__players[user_id_choosen].deck:
                if convert_card_id_to_type(card_id) == self.__card_type:
                    __card_id = card_id
                    break

            self.__players[user_id].add_card(__card_id)
            self.__players[user_id_choosen].remove_card(__card_id)

            self.__status.stage = GameStages.PLAYER_TURN

            self._notify(Notifications.SPECIAL3_DONE, user_id=user_id_choosen)

        # self.__lock.release()
        # print("__choose_player_successful self.__lock.release()")

    def __choose_player_failed(self, user_id):
        print("__choose_player_failed waiting.............")
        lock = Locker(self.__lock)

        print("__choose_player_failed")
        self.__status.can_no_move = False

        if self.__status.stage == GameStages.FAVOR_CANCELING:
            self.__status.stage = GameStages.PLAYER_TURN

            self.__status.no_card_cnt = 1
        elif self.__status.stage == GameStages.SPECIAL2_PLAYER_CANCELING:
            self.__status.stage = GameStages.PLAYER_TURN

            self.__status.no_card_cnt = 1
        elif self.__status.stage == GameStages.SPECIAL3_PLAYER_CANCELING:
            self.__status.stage = GameStages.PLAYER_TURN

            self.__status.no_card_cnt = 1

        self._notify(Notifications.TURN_CANCELED, user_id=user_id)

    def __get_info(self):
        lock = Locker(self.__lock)

        return [self.__status.no_card_cnt, self.__status.last_no_time]

    def choose_player(self, user_id, user_id_choosen):
        lock = Locker(self.__lock)

        if user_id == self.__status.active_player and self.__status.stage in [GameStages.FAVOR_PLAYER_CHOOSING, GameStages.SPECIAL2_PLAYER_FAVOR_CHOOSING, GameStages.SPECIAL3_PLAYER_FAVOR_CHOOSING] and user_id_choosen==user_id:
            self._notify(Notifications.YOURSELF_CAN_NOT_BE_CHOOSEN, user_id=user_id)
        elif self.__status.stage == GameStages.FAVOR_PLAYER_CHOOSING and user_id == self.__status.active_player:
            if len(self.__players[user_id_choosen].deck) == 0:
                self._notify(Notifications.FAVOR_PLAYER_CHOOSED_WITH_EMPTY_DECK, user_id=user_id)
            else:
                self.__status.can_no_move = True
                self.__status.no_card_cnt = 1
                self.__status.last_no_time = time.time()

                self.__status.favor = user_id_choosen
                self.__status.stage = GameStages.FAVOR_CANCELING

                
                __thread = threading.Thread(target=thread_no_card_waiting, args=(lambda: self.__get_info(), lambda: self.__choose_player_successful(user_id, user_id_choosen), lambda: self.__choose_player_failed(user_id)))
               
                self.__status.last_no_time = time.time()
                __thread.start()

                self._notify(Notifications.PLAYER_CHOOSED, user_id=user_id_choosen)

        elif self.__status.stage == GameStages.SPECIAL2_PLAYER_FAVOR_CHOOSING and user_id == self.__status.active_player:
            if len(self.__players[user_id_choosen].deck) == 0:
                self._notify(Notifications.FAVOR_PLAYER_CHOOSED_WITH_EMPTY_DECK, user_id=user_id)
            else:
                self.__status.can_no_move = True
                self.__status.no_card_cnt = 1
                self.__status.last_no_time = time.time()

                self.__status.stage = GameStages.SPECIAL2_PLAYER_CANCELING

                __thread = threading.Thread(target=thread_no_card_waiting, args=(lambda: self.__get_info(), lambda: self.__choose_player_successful(user_id, user_id_choosen), lambda: self.__choose_player_failed(user_id)))
                
                self.__status.last_no_time = time.time()
                __thread.start()

                self._notify(Notifications.PLAYER_CHOOSED, user_id=user_id_choosen)

        elif self.__status.stage == GameStages.SPECIAL3_PLAYER_FAVOR_CHOOSING and user_id == self.__status.active_player:
            if not EKGame.__check_card_type_is_in_deck(self.__players[user_id_choosen].deck, self.__card_type):
                self._notify(Notifications.SPECIAL3_FAILED_WITH_THIS_TYPE, user_id=user_id)

                self.__status.can_no_move = False
                self.__status.stage = GameStages.PLAYER_TURN
            else:
                self.__status.can_no_move = True
                self.__status.no_card_cnt = 1

                self.__status.stage = GameStages.SPECIAL3_PLAYER_CANCELING

                __thread = threading.Thread(target=thread_no_card_waiting, args=(lambda: self.__get_info(), lambda: self.__choose_player_successful(user_id, user_id_choosen), lambda: self.__choose_player_failed(user_id)))
                
                self.__status.last_no_time = time.time()
                __thread.start()

                self._notify(Notifications.PLAYER_CHOOSED, user_id=user_id_choosen)

        # self.__lock.release()
        # print("choose_player self.__lock.release()")

    @staticmethod
    def __check_card_type_is_in_deck(deck, card_type):
        for card_id in deck:
            if convert_card_id_to_type(card_id) == card_type:
                return True
        return False

    def choose_card(self, user_id, card_type):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.SPECIAL3_PLAYER_CARD_TYPE_CHOOSING and user_id == self.__status.active_player:
            self.__status.can_no_move = False

            self.__card_type = CardTypes(card_type)
            self.__status.stage = GameStages.SPECIAL3_PLAYER_FAVOR_CHOOSING

            # self._notify(Notifications.FAVOR_PLAYER_CHOOSING, user_id=user_id)
            self._notify(Notifications.CARD_TYPE_CHOOSED, user_id=user_id, card_type=card_type)
            self._notify(Notifications.FAVOR_PLAYER_CHOOSING, user_id=user_id)

        # self.__lock.release()
        # print("choose_card self.__lock.release()")

    def boom(self, user_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.EXPLOSIVE_KITTEN and user_id == self.__status.active_player:
            # self.__previous_game_position = self.__build_now_game_position()
            self.__status.can_no_move = False

            self.__discard.extend(self.__players[user_id].deck)
            # self.__discard.append(self.__status.explosive_kitten)
            del self.__players[user_id]

            self._notify(Notifications.PLAYER_BOOM, user_id=user_id)

            if len(self.__players) <= 1:
                self._notify(Notifications.GAME_END, user_id=0)
            else:
                self._notify(Notifications.NEXT_PLAYER_TURN, user_id=min(user_id, len(self.__players) - 1))
                self.__status.stage = GameStages.PLAYER_TURN
                
        # self.__lock.release()
        # print("boom self.__lock.release()")

    def place_card(self, user_id, position):
        lock = Locker(self.__lock)
        
        if self.__status.active_player != user_id:
            self._notify(Notifications.ANOTHER_PLAYER_TURN, user_id=self.__status.active_player)
            # self.__lock.release()
            # print("place_card self.__lock.release()")
        elif self.__status.stage == GameStages.EXPLOSIVE_KITTEN_NEUTRALIZED:
            try:
                position = int(position)
                
                # self.__previous_game_position = self.__build_now_game_position()
                self.__status.can_no_move = False

                if 1 <= position and position <= len(self.__deck) + 1:
                    self.__deck.insert(len(self.__deck) + 1 - position, self.__status.explosive_kitten)
                    self._notify(Notifications.EXPLOSIVE_KITTEN_PLACED, user_id=user_id)
                    self.__next_turn()
                else:
                    self._notify(Notifications.PLACE_CARD_FAILED)
            except Exception as e:
                self._notify(Notifications.PLACE_CARD_FAILED)
            # finally:
                # self.__lock.release()
                # print("place_card self.__lock.release()")

    ###########################################################################################
    #                                       CARDS
    ###########################################################################################

    def __neutralize(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.EXPLOSIVE_KITTEN and user_id == self.__status.active_player:
            self.__status.can_no_move = False

            self.__status.stage = GameStages.EXPLOSIVE_KITTEN_NEUTRALIZED

            self.__discard_card(user_id, card_id)
            
            self._notify(Notifications.EXPLOSIVE_KITTEN_NEUTRALIZED, user_id=user_id)

        # self.__lock.release()
        # print("__neutralize self.__lock.release()")

    def __shuffle(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            self.__previous_game_position = self.__build_now_game_position()
            self.__status.can_no_move = True
            
            random.shuffle(self.__deck)

            self.__discard_card(user_id, card_id)

            self._notify(Notifications.PLAYER_SHUFFLED_DECK, user_id=user_id)

        # self.__lock.release()
        # print("__shuffle self.__lock.release()")
    
    def __attack(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            self.__previous_game_position = self.__build_now_game_position()
            self.__status.can_no_move = True

            next_player_id = (self.__status.active_player + 1) % len(self.__players)
            if self.__status.additional_turns > 0:
                self.__status.additional_turns += 2
            else:
                self.__status.additional_turns = 1
            self.__status.active_player = next_player_id

            self.__discard_card(user_id, card_id)
            
            self._notify(Notifications.PLAYER_ATTACKED, user_id=user_id, turns_count=self.__status.additional_turns+1)
            self._notify(Notifications.NEXT_PLAYER_TURN, user_id=self.__status.active_player)
            # self.__next_turn()

        # self.__lock.release()
        # print("__attack self.__lock.release()")

    def __see_the_future(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            self.__status.can_no_move = False
            
            self.__card_id = card_id

            __cards = []
            for i in range(3):
                if len(self.__deck) - i - 1 >= 0:
                    __cards.append(self.__deck[len(self.__deck) - i - 1])

            self._notify(Notifications.SEE_THE_FUTURE, user_id=user_id, cards=__cards)
    
        # self.__lock.release()
        # print("__see_the_future self.__lock.release()")

    def see_the_future_successful(self, user_id):
        lock = Locker(self.__lock)

        self.__discard_card(user_id, self.__card_id)

        # self.__lock.release()
        # print("see_the_future_successful self.__lock.release()")

    def __no(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__check_no_can_move():
            if self.__status.stage in [GameStages.FAVOR_CANCELING, GameStages.SPECIAL2_PLAYER_CANCELING, GameStages.SPECIAL3_PLAYER_CANCELING, GameStages.SPECIAL5_PLAYER_CANCELING]:
                self.__status.no_card_cnt += 1
                self.__status.last_no_time = time.time()
                print("update self.__status.no_card_cnt {0}".format(self.__status.no_card_cnt))
            else:
                self.undo()
            
            # self.__previous_game_position = self.__build_now_game_position()
            self.__status.can_no_move = True

            self.__discard_card(user_id, card_id)

            self._notify(Notifications.PLAYER_CANCELED_LAST_ACTION, user_id=user_id)

        # self.__lock.release()
        # print("__no self.__lock.release()")

    def __run_away(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            self.__previous_game_position = self.__build_now_game_position()
            self.__status.can_no_move = True

            self.__discard_card(user_id, card_id)

            self._notify(Notifications.PLAYER_RAN_AWAY, user_id=user_id)
            self.__next_turn()

        # self.__lock.release()
        # print("__run_away self.__lock.release()")

    def __favor(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            self.__previous_game_position = self.__build_now_game_position()
            self.__status.can_no_move = False
            print("__favor card ")

            self.__discard_card(user_id, card_id)
            self.__status.stage = GameStages.FAVOR_PLAYER_CHOOSING

            self._notify(Notifications.FAVOR_PLAYER_CHOOSING, user_id=user_id)

        # self.__lock.release()
        # print("__favor self.__lock.release()")
            
    def __special5_successful(self, user_id):
        lock = Locker(self.__lock)

        self.__status.can_no_move = False
        
        self.__status.no_card_cnt = 1

        self.__status.stage = GameStages.SPECIAL5_PLAYER_TAKING_CARD

        self._notify(Notifications.PLAYER_TAKING_CARD_FROM_DISCARD, user_id=user_id)

    def __special5_failed(self, user_id):
        lock = Locker(self.__lock)

        self.__status.can_no_move = False
    
        self.__status.stage = GameStages.PLAYER_TURN

        self.__status.no_card_cnt = 1

        self._notify(Notifications.TURN_CANCELED, user_id=user_id)

    def __player_discard_card(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.FAVOR_CARD_CHOOSING and user_id == self.__status.favor:
            self.__status.can_no_move = False

            self.__players[self.__status.active_player].add_card(card_id)
            self.__players[self.__status.favor].remove_card(card_id)

            self.__status.stage = GameStages.PLAYER_TURN
        elif self.__status.stage == GameStages.SPECIAL2_PLAYER_CARDS_CHOOSING and user_id == self.__status.active_player:
            __cnt = 0
            __type = convert_card_id_to_type(card_id)

            __cards = []
            for card_id in self.__players[user_id].deck:
                if __type == convert_card_id_to_type(card_id):
                    __cnt += 1
                    __cards.append(card_id)

            if __cnt >= 2:
                for card_id in __cards:
                    self.__players[user_id].remove_card(card_id)
                    # self.__status.special_add(card_id)
                    self.__discard.append(card_id)

                    if len(self.__status.special) == 2:
                        break
                # self.__players[user_id].remove_card(card_id)
                # self.__status.special_add(card_id)

                self.__status.stage = GameStages.SPECIAL2_PLAYER_FAVOR_CHOOSING
                self._notify(Notifications.FAVOR_PLAYER_CHOOSING, user_id=user_id)

                # for card_id in self.__status.special:
                #     self.__discard.append(card_id)
                # self.__status.special_clear()
        
        elif self.__status.stage == GameStages.SPECIAL3_PLAYER_CARDS_CHOOSING and user_id == self.__status.active_player:
            __cnt = 0
            __type = convert_card_id_to_type(card_id)

            __cards = []
            for card_id in self.__players[user_id].deck:
                if __type == convert_card_id_to_type(card_id):
                    __cnt += 1
                    __cards.append(card_id)
            
            if __cnt >= 3:
                for card_id in __cards:
                    self.__players[user_id].remove_card(card_id)
                    # self.__status.special_add(card_id)
                    self.__discard.append(card_id)

                    if len(self.__status.special) == 2:
                        break

                print('SPECIAL3_PLAYER_CARDS_CHOOSING special == 3!!!')

                self.__status.stage = GameStages.SPECIAL3_PLAYER_CARD_TYPE_CHOOSING
                self._notify(Notifications.CARD_TYPE_CHOOSING, user_id=user_id)
        elif self.__status.stage == GameStages.SPECIAL5_PLAYER_CARDS_CHOOSING and user_id == self.__status.active_player:
            __f = True
            __type = convert_card_id_to_type(card_id)
            for _card_id in self.__status.special:
                if convert_card_id_to_type(_card_id) == __type:
                    __f = False
                    break
        
            if __f:
                print("removing card with id = ", card_id)
                self.__players[user_id].remove_card(card_id)
                self.__status.special_add(card_id)

                if len(self.__status.special) == 5:
                    # self.__status.stage = GameStages.SPECIAL5_PLAYER_TAKING_CARD

                    for card_id in self.__status.special:
                        self.__discard.append(card_id)
                    self.__status.special_clear()

                        
                    self.__status.can_no_move = True
                    self.__status.no_card_cnt = 1

                    self.__status.stage = GameStages.SPECIAL5_PLAYER_CANCELING

                    __thread = threading.Thread(target=thread_no_card_waiting, args=(lambda: self.__get_info(), lambda: self.__special5_successful(user_id), lambda: self.__special5_failed(user_id)))
                    
                    self.__status.last_no_time = time.time()
                    __thread.start()

                    self._notify(Notifications.SPECIAL5_WAINTING, user_id=user_id)
                    # self.__status.stage = GameStages.SPECIAL5_PLAYER_TAKING_CARD
        # elif self.__status.stage == GameStages.SPECIAL5_PLAYER_TAKING_CARD and user_id == self.__status.active_player:
        #     # self.__players[]
        #     pass

    def __special5_take_card(self, user_id, card_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.SPECIAL5_PLAYER_TAKING_CARD and user_id == self.__status.active_player:
            self.__players[user_id].add_card(card_id)
            self.__discard.remove(card_id)

            self.__status.can_no_move = False
            
            self.__status.stage = GameStages.PLAYER_TURN

            self._notify(Notifications.PLAYER_TOOK_CARD_FROM_DISCARD, user_id=user_id)

    ###########################################################################################
    #                                 SPECIAL
    ###########################################################################################

    @staticmethod
    def __check_special2(deck):
        __cards_count = {CardTypes(i): 0 for i in range(1, 14)}
        for card_id in deck:
            __cards_count[convert_card_id_to_type(card_id)] += 1

        for key, val in __cards_count.items():
            if val >= 2:
                return True
        
        return False

    @staticmethod
    def __check_special3(deck):
        __cards_count = {CardTypes(i): 0 for i in range(1, 14)}
        for card_id in deck:
            __cards_count[convert_card_id_to_type(card_id)] += 1

        for key, val in __cards_count.items():
            if val >= 3:
                return True
        
        return False

    @staticmethod
    def __check_special5(deck):
        __types = []
        __cnt_diff_types = 0
        for card_id in deck:
            __card_type = convert_card_id_to_type(card_id)
            if not __card_type in __types:
                __types.append(__card_type)
                __cnt_diff_types += 1
        
        return __cnt_diff_types >= 5

    def special2(self, user_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            if EKGame.__check_special2(self.__players[user_id].deck):
                self.__previous_game_position = self.__build_now_game_position()
                self.__status.can_no_move = False

                print("SPECIAL2 activated")

                self.__status.stage = GameStages.SPECIAL2_PLAYER_CARDS_CHOOSING

                self._notify(Notifications.PLAYER_CHOOSING_CARDS_FOR_COMB, user_id=user_id)
            else:
                self._notify(Notifications.PLAYER_CANT_USE_THIS_COMBINATION)
        elif self.__status.stage == GameStages.PLAYER_TURN:
            self._notify(Notifications.ANOTHER_PLAYER_TURN, user_id=self.__status.active_player)

        # self.__lock.release()
        # print("special2 self.__lock.release()")

    def special3(self, user_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            if EKGame.__check_special3(self.__players[user_id].deck):
                self.__previous_game_position = self.__build_now_game_position()
                self.__status.can_no_move = False

                print("SPECIAL3 activated")

                self.__status.stage = GameStages.SPECIAL3_PLAYER_CARDS_CHOOSING

                self._notify(Notifications.PLAYER_CHOOSING_CARDS_FOR_COMB, user_id=user_id)
            else:
                self._notify(Notifications.PLAYER_CANT_USE_THIS_COMBINATION)

        elif self.__status.stage == GameStages.PLAYER_TURN:
            self._notify(Notifications.ANOTHER_PLAYER_TURN, user_id=self.__status.active_player)

        # self.__lock.release()
        # print("special3 self.__lock.release()")

    def special5(self, user_id):
        lock = Locker(self.__lock)

        if self.__status.stage == GameStages.PLAYER_TURN and user_id == self.__status.active_player:
            if len(self.__discard) == 0:
                self._notify(Notifications.DISCARD_IS_EMPTY)
            elif EKGame.__check_special5(self.__players[user_id].deck):
                self.__previous_game_position = self.__build_now_game_position()
                self.__status.can_no_move = False

                print("SPECIAL5 activated special_size = {0}".format(len(self.__status.special)))
                # self.__status.special_clear()

                self.__status.stage = GameStages.SPECIAL5_PLAYER_CARDS_CHOOSING

                self._notify(Notifications.PLAYER_CHOOSING_CARDS_FOR_COMB, user_id=user_id)
            else:
                self._notify(Notifications.PLAYER_CANT_USE_THIS_COMBINATION)
        elif self.__status.stage == GameStages.PLAYER_TURN:
            self._notify(Notifications.ANOTHER_PLAYER_TURN, user_id=self.__status.active_player)

    def undo_special(self, user_id):
        lock = Locker(self.__lock)

        if user_id == self.__status.active_player and self.__status.stage in [
                                                                                GameStages.SPECIAL2_PLAYER_CARDS_CHOOSING,
                                                                                GameStages.SPECIAL3_PLAYER_CARDS_CHOOSING,
                                                                                GameStages.SPECIAL5_PLAYER_CARDS_CHOOSING,
                                                                                GameStages.SPECIAL2_PLAYER_FAVOR_CHOOSING,
                                                                                GameStages.SPECIAL3_PLAYER_FAVOR_CHOOSING,
                                                                                GameStages.SPECIAL3_PLAYER_CARD_TYPE_CHOOSING,
                                                                                ]:
            if self.__status.stage == GameStages.SPECIAL2_PLAYER_FAVOR_CHOOSING:
                for i in range(2):
                    card_id = self.__discard.pop()
                    self.__players[user_id].add_card(card_id)
            elif self.__status.stage in [GameStages.SPECIAL3_PLAYER_FAVOR_CHOOSING, GameStages.SPECIAL3_PLAYER_CARD_TYPE_CHOOSING]:
                for i in range(3):
                    card_id = self.__discard.pop()
                    self.__players[user_id].add_card(card_id)
            else:
                for card_id in self.__status.special:
                    self.__players[user_id].add_card(card_id)
                self.__status.special_clear()
            self.__status.can_no_move = False

            self.__status.stage = GameStages.PLAYER_TURN

            print('undo special successfull')
            self._notify(Notifications.UNDO_SPECIAL_SUCCESSFULL, user_id=user_id)
        else:
            self._notify(Notifications.UNDO_SPECIAL_FAILED)
        
        # self.__lock.release()
        # print("undo_special self.__lock.release()")

    ###########################################################################################

    def __build_now_game_position(self):
        lock = Locker(self.__lock)

        print("Build game_position on stage = ", self.__status.stage.name)

        __game_position = [] 
        __game_position.append(self.__status.copy())
        __game_position.append(self.__deck.copy())

        # self.__lock.release()
        # print("__build_now_game_position self.__lock.release()")

        return __game_position

    def __set_game_position(self, game_position):
        lock = Locker(self.__lock)

        self.__status = game_position[0]
        self.__deck = game_position[1]

        # self.__lock.release()
        # print("__set_game_position self.__lock.release()")

    def undo(self):
        lock = Locker(self.__lock)

        if self.__previous_game_position != None:
            __now_game_position = self.__build_now_game_position()
            self.__set_game_position(self.__previous_game_position)
            self.__previous_game_position = __now_game_position
            print('GAME: UNDO processed')
        else:
            print('ERROR: game.undo() SKIPPED (TIP: self.__previous_game_position is empty)')

        # self.__lock.release()
        # print("undo self.__lock.release()")

    ###########################################################################################
    
    def __check_no_can_move(self):
        lock = Locker(self.__lock)

        # self.__lock.release()
        # print("__check_no_can_move self.__lock.release()")

        return self.__status.can_no_move

    def __player_can_move_cards_pt(self, user_id):
        lock = Locker(self.__lock)

        __result = []
        for card_id in self.__players[user_id].deck:
            __f = True
            __card_type = convert_card_id_to_type(card_id)
            if __card_type in [CardTypes.NEUTRALIZE, 
                                CardTypes.SPECIAL_1, 
                                CardTypes.SPECIAL_2, 
                                CardTypes.SPECIAL_3, 
                                CardTypes.SPECIAL_4, 
                                CardTypes.SPECIAL_5]:
                __f = False
            elif __card_type == CardTypes.NO:
                __f = self.__check_no_can_move()

            __result.append(__f)

        # self.__lock.release()
        # print("__player_can_move_cards_pt self.__lock.release()")

        return __result

    def __player_can_move_cards_ek(self, user_id):
        lock = Locker(self.__lock)

        __result = []

        for card_id in self.__players[user_id].deck:
            __f = True
            __card_type = convert_card_id_to_type(card_id)
            if __card_type != CardTypes.NEUTRALIZE:
                __f = False

            __result.append(__f)

        # self.__lock.release()
        # print("__player_can_move_cards_ek self.__lock.release()")

        return __result

    def __player_can_move_cards_fcc(self, user_id):
        lock = Locker(self.__lock)

        print("__player_can_move_cards_fcc user_id = {0}, favor_id = {1}, active_player = {2}".format(user_id, self.__status.favor, self.__status.active_player))

        if user_id != self.__status.favor:
            __result = [False for i in range(len(self.__players[user_id].deck))]
        else:
            __result = [True for i in range(len(self.__players[user_id].deck))]

        # self.__lock.release()
        # print("__player_can_move_cards_fcc self.__lock.release()")

        return __result

    def __player_can_move_cards_default(self, user_id):
        lock = Locker(self.__lock)
        
        __result = []
        for card_id in self.__players[user_id].deck:
            if convert_card_id_to_type(card_id) == CardTypes.NO:
                __result.append(self.__check_no_can_move())
            else:
                __result.append(False)

        # self.__lock.release()
        # print("__player_can_move_cards_default self.__lock.release()")

        return __result

    def __player_can_move_cards_pc2cc(self, user_id):
        lock = Locker(self.__lock)

        __result = []

        if len(self.__status.special) == 0:        
            __cards_count = {CardTypes(i): 0 for i in range(1, 14)}
            for card_id in self.__players[user_id].deck:
                __cards_count[convert_card_id_to_type(card_id)] += 1

            for card_id in self.__players[user_id].deck:
                __result.append(__cards_count[convert_card_id_to_type(card_id)] >= 2)
            
        else:
            __bad_card_type = convert_card_id_to_type(self.__status.special[0])
            for card_id in self.__players[user_id].deck:
                __result.append(convert_card_id_to_type(card_id) == __bad_card_type)
        
        # self.__lock.release()
        # print("__player_can_move_cards_pc2cc self.__lock.release()")

        return __result

    @staticmethod
    def __check_special3(deck):
        __cards_count = {CardTypes(i): 0 for i in range(1, 14)}
        for card_id in deck:
            __cards_count[convert_card_id_to_type(card_id)] += 1

        __f = False
        for key, val in __cards_count.items():
            if val >= 3:
                __f = True
                break
        
        return __f

    def __player_can_move_cards_pc3cc(self, user_id):
        lock = Locker(self.__lock)

        __result = []

        if len(self.__status.special) == 0:        
            __cards_count = {CardTypes(i): 0 for i in range(1, 14)}
            for card_id in self.__players[user_id].deck:
                __cards_count[convert_card_id_to_type(card_id)] += 1

            for card_id in self.__players[user_id].deck:
                __result.append(__cards_count[convert_card_id_to_type(card_id)] >= 3)
        else:
            __bad_card_type = convert_card_id_to_type(self.__status.special[0])
            for card_id in self.__players[user_id].deck:
                __result.append(convert_card_id_to_type(card_id) == __bad_card_type)

        return __result

    def __player_can_move_cards_pc5cc(self, user_id):
        lock = Locker(self.__lock)

        __result = []

        if len(self.__status.special) == 0:
            __result = [True for i in range(len(self.__players[user_id].deck))]
        else:
            __types = []
            for card_id in self.__status.special:
                __types.append(convert_card_id_to_type(card_id))

            for card_id in self.__players[user_id].deck:
                if not convert_card_id_to_type(card_id) in __types:
                    __result.append(True)
                else:
                    __result.append(False)

        return __result

    def __player_can_move_cards(self, user_id):
        print("__player_can_move_cards waiting........")
        lock = Locker(self.__lock)

        print("__player_can_move_cards user_id = {0}, stage = {1}, active_player = {2}".format(user_id, self.__status.stage, self.__status.active_player))
        
        if self.__status.stage == GameStages.FAVOR_CARD_CHOOSING:
            __result = self.__player_can_move_cards_fcc(user_id)
        elif user_id != self.__status.active_player:
            __result = self.__player_can_move_cards_default(user_id)
            # return [False for i in range(len(self.__players[user_id].deck))]
        elif self.__status.stage == GameStages.PLAYER_TURN:
            __result = self.__player_can_move_cards_pt(user_id)
        elif self.__status.stage == GameStages.EXPLOSIVE_KITTEN:
            __result = self.__player_can_move_cards_ek(user_id)
        elif self.__status.stage == GameStages.SPECIAL2_PLAYER_CARDS_CHOOSING:
            __result = self.__player_can_move_cards_pc2cc(user_id)
        elif self.__status.stage == GameStages.SPECIAL3_PLAYER_CARDS_CHOOSING:
            __result = self.__player_can_move_cards_pc3cc(user_id)
        elif self.__status.stage == GameStages.SPECIAL5_PLAYER_CARDS_CHOOSING:
            __result = self.__player_can_move_cards_pc5cc(user_id)
        else:
            __result = self.__player_can_move_cards_default(user_id)


        return __result

    def is_hidden_stage(self, user_id):
        lock = Locker(self.__lock)

        __f = False
        if self.__status.stage in [
                                    GameStages.FAVOR_CARD_CHOOSING,
                                    GameStages.SPECIAL2_PLAYER_CARDS_CHOOSING,
                                    GameStages.SPECIAL3_PLAYER_CARDS_CHOOSING,
                                    GameStages.SPECIAL5_PLAYER_CARDS_CHOOSING,
                                    GameStages.SPECIAL5_PLAYER_TAKING_CARD,
                                    ]:
                __f = True

        return __f

    def get_no_cards_in_decks(self):
        lock = Locker(self.__lock)

        __result = []
        for i in self.__players:
            __result.append(len(i.deck))

        return __result

    def get_player_deck(self, user_id):
        lock = Locker(self.__lock)

        __answer = []

        if self.__status.stage == GameStages.SPECIAL5_PLAYER_TAKING_CARD:
            __answer.append(self.__discard)
            __answer.append([True for i in range(len(self.__discard))])
        else:
            __answer.append(self.__players[user_id].deck)
            __answer.append(self.__player_can_move_cards(user_id))

        return __answer

    def get_deck_cards_count(self):
        lock = Locker(self.__lock)

        print('get_deck_cards_count answer = ', len(self.__deck))

        return len(self.__deck)

    @property
    def turn(self):
        lock = Locker(self.__lock)

        return self.__status.active_player

    @property
    def deck(self):
        lock = Locker(self.__lock)

        return self.__deck
        
    ###########################################################################################

class EKGameCreator(GameCreator):
    def __call__(self, settings):
        __lock = threading.RLock()
        __lock.acquire()

        settings.number_of_cards_per_player = EKDeck.cards_per_player()
        __new_deck = EKDeck.generate_deck(settings.number_of_players)
        __new_game = EKGame(settings, __new_deck)

        __lock.release()

        return __new_game

    def check(self, number_of_players):
        return 0 < number_of_players and number_of_players < 6