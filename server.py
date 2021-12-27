"""Manages games and pairings"""
from dataclasses import dataclass, field
from tablut import Tablut, GameStatus
from typing import List, MutableMapping, Optional
from helpers import TaflGamePrinter, TaflGameCreator, get_random_string
from random import choice


GAME_ID_LENGTH = 6
ChatId = str
GameId = str


@dataclass
class PlayerRecord:
    chat: ChatId
    name: str


@dataclass
class GameRecord:
    id: GameId
    attackers: PlayerRecord
    defenders: PlayerRecord
    game: Tablut

    @property
    def board(self) -> str:
        return TaflGamePrinter.str(self.game)

    @property
    def active(self) -> bool:
        return self.game.status == GameStatus.IN_PROGRESS

    def opponent(self, chat) -> PlayerRecord:
        return self.defenders if self.attackers.chat == chat else self.attackers

    def side(self, chat: ChatId) -> str:
        return 'attackers' if self.attackers.chat == chat else 'defenders'

    def check_my_turn(self, chat: ChatId) -> bool:
        am_attackers = self.side(chat) == 'attackers'
        return am_attackers == self.game.turn_attackers

    def move(self, chat: ChatId, move_str: str) -> None:
        if self.active and not self.check_my_turn(chat):
            raise NotYourTurnException("It is not your turn!")
        self.game.move(move_str)

    def check_i_won(self, chat: ChatId) -> bool:
        am_attackers = self.side(chat) == 'attackers'
        if am_attackers:
            return self.game.status == GameStatus.ATTACKERS_WIN
        else:
            return self.game.status == GameStatus.DEFENDERS_WIN


class NotYourTurnException(Exception):
    pass


@dataclass
class Lobby:
    """manages people who are waiting to get paired"""
    players: List[PlayerRecord] = field(default_factory=list)
    
    def empty(self):
        return len(self.players) == 0

    def add(self, p: PlayerRecord):
        self.players.append(p)

    def pick_one(self) -> PlayerRecord:
        p = self.players[0]
        self.players.pop(0)
        return p


@dataclass
class Server:
    """Manages games in progress"""
    games: MutableMapping[GameId, GameRecord] = field(default_factory=dict)
    chats_to_games: MutableMapping[ChatId, GameId] = field(default_factory=dict)
    lobby: Lobby = Lobby()

    def game(self, chat: ChatId) -> Optional[GameRecord]:
        try:
            return self.games[self.chats_to_games[chat]]
        except KeyError:
            pass

    def new(self, chat: ChatId, name: str) -> Optional[GameRecord]:
        g = self.game(chat)
        if g is not None and g.active:
            raise GameAlreadyExistsException('You need to finish existing game first!')

        p = PlayerRecord(chat, name)
        if self.lobby.empty():
            self.lobby.add(p)
            return None
        opp = self.lobby.pick_one()
        return self.create_game(p, opp)

    def generate_game_id(self) -> GameId:
        game_id = None
        while game_id in self.games:
            game_id = get_random_string(GAME_ID_LENGTH)
        return game_id

    def create_game(self, p1: PlayerRecord, p2: PlayerRecord) -> GameRecord:
        first_is_attacker = choice([0, 1]) == 1
        g = GameRecord(
            self.generate_game_id(),
            p1 if first_is_attacker else p2,
            p2 if first_is_attacker else p1,
            TaflGameCreator.create_basic(),
        )
        self.games[g.id] = g
        self.chats_to_games[p1.chat] = g.id
        self.chats_to_games[p2.chat] = g.id
        return g


class GameAlreadyExistsException(Exception):
    pass
