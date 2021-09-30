from enum import Enum

class Commands(Enum):
    CREATE = 1
    CLOSE = 2
    JOIN = 3
    LEAVE = 4
    LEAVE_ALL = 5
    PLAY = 6
    TAKE_CARD = 7
    PLACE_CARD = 8
    SPECIAL2 = 9
    SPECIAL3 = 10
    SPECIAL5 = 11
    UNDO = 12
    CARDS = 13
    MENU = 14