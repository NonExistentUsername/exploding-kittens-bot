import random
from datetime import datetime
import threading

random.seed(datetime.now())

class EKDeck:
    __cards_per_player = 8
    __cards_in_deck = 56

    # def __init__(self):
    #     pass

    @staticmethod
    def generate_deck(number_of_players):
        __lock = threading.RLock()
        __lock.acquire()

        __temp_deck = [id for id in range(11, EKDeck.__cards_in_deck)]
        random.shuffle(__temp_deck)

        __end_of_deck = []
        for i in range(number_of_players):
            for k in range(EKDeck.__cards_per_player - 1):
                __end_of_deck.append(__temp_deck.pop())
            __end_of_deck.append(10 - i)

        if number_of_players == 2:
            __ek_n_cards = [5, 6]
        else:
            __ek_n_cards = [id for id in range(5, 11 - number_of_players)]
        __temp_deck.extend(__ek_n_cards)

        ################# CHANGE THIS
        __ek_cards = [id for id in range(1, number_of_players)]
        # __ek_cards = [id for id in range(1, 2)]
        # for id in range(1, 5):
        #     __ek_cards.append(id)
        # for id in range(1, 3):
        #     __ek_cards.append(id)
        __temp_deck.extend(__ek_cards)

        random.shuffle(__temp_deck)
        __temp_deck.extend(__end_of_deck)
        
        __lock.release()

        return __temp_deck

    @staticmethod
    def cards_per_player():
        return EKDeck.__cards_per_player

    @staticmethod
    def cards_in_deck():
        return EKDeck.__cards_in_deck
