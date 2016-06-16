import random

import map_loader


def clamp_number(num, min_number, max_number):
    if num < min_number:
        num = min_number

    if num > max_number:
        num = max_number

    return num


class Player(object):
    def __init__(self, address, game):
        self.address = address
        self.game = game
        self.coordinates = ()

    def move(self, x=0, y=0):
        old_coordinates = self.coordinates

        self.coordinates[0] += clamp_number(x, -1, 1)
        self.coordinates[1] += clamp_number(y, -1, 1)

        if self.coordinates in self.game.map["tiles"]:
            self.coordinates = old_coordinates
            print "Impossible move into solid tile at {},{}!".format(*self.coordinates)

        if self.coordinates == self.game.map["exit"]:
            print "Congratulations! You found the exit!"
            self.game.change_map(self.game.map["next_map"])

        print "Moved succesfully into square {},{}!".format(*self.coordinates)

    def __del__(self):
        self.game.player_list.remove(self)


class Game(object):
    def __init__(self, map_dict, players=[]):
        self.map = map_dict
        self.player_list = players

    def change_map(self, map_filename):
        self.map = map_loader.load_map(map_filename)

        for player in self.player_list:
            player.coords = random.choice(self.map["player_starts"])
