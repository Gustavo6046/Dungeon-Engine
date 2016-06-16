import ConfigParser
import struct
import sys


class DungeonParsingException(BaseException):
    pass


class InvalidMapFormat(DungeonParsingException):
    pass


class UnpackingIndexError(DungeonParsingException):
    pass


class StringUnpacker(object):
    def __init__(self, data, initial_position=0):
        """Provide the data you'll unpack into values and the initial position if it should be bigger than zero."""
        self.position = initial_position
        self.data = data

    def read_format(self, byte_format):
        if self.position + struct.calcsize(byte_format) > len(self.data):
            raise UnpackingIndexError

        unpacked = struct.unpack(byte_format, self.data[self.position: self.position + struct.calcsize(byte_format)])
        self.position += struct.calcsize(byte_format)
        return unpacked


def load_map(filename="intro"):
    temp_config = ConfigParser.ConfigParser()
    temp_config.read(tuple(["config\\{}.ini".format(config) for config in sys.argv[1:]]))
    game_name = temp_config.get("Game", "GameDirectoryName")
    del temp_config

    data_unpacker = StringUnpacker(open("games\\{}\\maps\\{}.dbm".format(game_name, filename)).read())
    current_map = {"tiles": [], "player_starts": []}

    if data_unpacker.read_format("11s") != "DUNGEON_MAP":
        raise InvalidMapFormat("The map is corrupted or the file is in a invalid format!")

    top_left = data_unpacker.read_format("2l")
    map_width, map_height = data_unpacker.read_format("2l")
    current_parsing_position = (top_left[0], top_left[1])

    while True:
        try:
            byte_kind = data_unpacker.read_format("B")
            if byte_kind == 0:
                if current_parsing_position[1] > top_left[1] + map_height:
                    current_parsing_position[0] += 1
                    current_parsing_position[1] == top_left[1]

                    if current_parsing_position[0] == map_width + top_left[0]:
                        break

                else:
                    current_parsing_position[1] += 1

            elif byte_kind == 1:
                current_map["tiles"].append(data_unpacker.read_format("2l"))

            elif byte_kind == 2:
                current_map["player_starts"].append(data_unpacker.read_format("2l"))

            else:
                continue

        except UnpackingIndexError:
            raise InvalidMapFormat("The map is too small for the width and/or height specified in the header!")

    return current_map
