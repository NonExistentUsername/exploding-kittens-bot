
class InlineAnswer:
    def __init__(self):
        pass

    @property
    def deck(self):
        return self.__deck

    @deck.setter
    def deck(self, deck):
        self.__deck = deck

    @property
    def turn(self):
        return self.__turn

    @turn.setter
    def turn(self, turn):
        self.__turn = turn

    @property
    def game_deck_size(self):
        return self.__game_deck_size

    @game_deck_size.setter
    def game_deck_size(self, game_deck_size):
        self.__game_deck_size = game_deck_size

    @property
    def can_move(self):
        return self.__can_move

    @can_move.setter
    def can_move(self, val):
        self.__can_move = val

    @property
    def hidden(self):
        return self.__hidden

    @hidden.setter
    def hidden(self, val):
        self.__hidden = val