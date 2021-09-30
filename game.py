from player import Player
from settings import Settings

class Game:
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
        self._deck = deck
        self._turn = 0
        self._players = Game.__generate_players(self._deck, settings.number_of_players, settings.number_of_cards_per_player)

    def get_player_deck(self, user_id):
        return self._players[user_id].deck

    @property
    def deck(self):
        return self._deck

    @property
    def turn(self):
        return self._turn

class GameCreator:
    def check(self, no_players):
        return no_players > 0