from enum import Enum

class Notifications(Enum):
    GAME_CREATED = 0
    GAME_NOT_CREATED = 8
    GAME_ALREADY_CREATED = 6
    GAME_CLOSED = 1
    GAME_STARTED = 2
    GAME_NOT_STARTED = 11
    GAME_ALREADY_STARTED = 5

    PLAYER_JOINED = 3
    PLAYER_LEAVES = 4
    NO_PLAYERS_NOT_VALID = 7
    PLAYER_ALREADY_IN_GAME = 9
    PLAYER_IN_ANOTHER_GAME = 10
    PLAYER_NOT_IN_GAME = 12

    ANOTHER_PLAYER_TURN = 13
    NEXT_PLAYER_TURN = 16 
    CARD_TAKEN = 14
    EXPLOSIVE_KITTEN = 15
    EXPLOSIVE_KITTEN_NEUTRALIZED = 17
    EXPLOSIVE_KITTEN_PLACED = 18
    PLACE_CARD_FAILED = 19
    
    PLAYER_BOOM = 20
    PLAYER_SHUFFLED_DECK = 21
    PLAYER_RAN_AWAY = 22
    GAME_END = 23
    PLAYER_ATTACKED = 24
    SEE_THE_FUTURE = 25
    PLAYER_CANCELED_LAST_ACTION = 26
    FAVOR_PLAYER_CHOOSING = 27
    FAVOR_CARD_CHOOSING = 28
    FAVOR_PLAYER_CHOOSED_WITH_EMPTY_DECK = 29
    PLAYER_CANT_USE_THIS_COMBINATION = 30
    PLAYER_CHOOSING_CARDS_FOR_COMB = 31
    SPECIAL2_DONE = 32

    PLAYER_HAS_NO_CARD = 33
    PLAYER_CHOOSED = 34
    CARD_TYPE_CHOOSING = 35

    SPECIAL3_FAILED_WITH_THIS_TYPE = 36
    SPECIAL3_DONE = 37
    TURN_CANCELED = 38
    DISCARD_IS_EMPTY = 39
    UNDO_SPECIAL_SUCCESSFULL = 40
    UNDO_SPECIAL_FAILED = 41
    CARD_TYPE_CHOOSED = 42

    PLAYER_TAKING_CARD_FROM_DISCARD = 43
    SPECIAL5_WAINTING = 44
    PLAYER_TOOK_CARD_FROM_DISCARD = 45
    PRINT_DECK_SIZE = 46
    YOURSELF_CAN_NOT_BE_CHOOSEN = 47