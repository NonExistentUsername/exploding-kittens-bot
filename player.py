
class Player:
    def __init__(self, deck = []):
        self.__deck = deck

    def add_card(self, card):
        self.__deck.append(card)

    def remove_card(self, card):
        self.__deck.remove(card)

    @property
    def deck(self):
        return self.__deck

    # @property
    # def additional_turns(self):
    #     return self.__additional_turns

    # @additional_turns.setter
    # def additional_turns(self, val):
    #     self.__additional_turns = val

    def copy(self):
        return Player(self.deck.copy())