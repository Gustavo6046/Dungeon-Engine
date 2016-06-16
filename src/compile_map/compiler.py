import struct
import sys


def compile_map(map_filename="current.dam", compiled_filename="result.dbm"):
    map_dict = current_map = {"tiles": [], "player_starts": []}

    for line in open(map_filename).readlines():
        if line.startswith("TILE "):
            map_dict["tiles"].append(tuple([int(coordinate) for coordinate in line.split(" ")[1:3]]))

        if line.startswith("PLAYERSTART "):
            map_dict["player_starts"].append(tuple([int(coordinate) for coordinate in line.split(" ")[1:3]]))

        if line.startswith("NEXTMAP "):
            map_dict["next_map"] = " ".join(line.split(" ")[1:])

        if line.startswith("EXIT "):
            map_dict["exit"] = tuple([int(coordinate) for coordinate in line.split(" ")[1:3]])

    for tile in map_dict["tiles"]:
        try:
            if tile[0] < leftmost:
                leftmost = tile[0]

        except UnboundLocalError:
            leftmost = tile[0]

        try:
            if tile[0] > rightmost:
                rightmost = tile[0]

        except UnboundLocalError:
            rightmost = tile[0]

        try:
            if tile[1] > bottom:
                bottom = tile[1]

        except UnboundLocalError:
            bottom = tile[1]

        try:
            if tile[1] < top:
                bottom = tile[1]

        except UnboundLocalError:
            top = tile[1]

    result_map = open(compiled_filename, "a")
    result_map.write(struct.pack("11s", "DUNGEON_MAP"))
    result_map.write(struct.pack("6l", leftmost, bottom, rightmost - leftmost, top - bottom, map_dict["exit"][0],
                                 map_dict["exit"][1]))
    result_map.write(struct.pack("I", struct.calcsize(str(len(map_dict["next_map"])) + "s")))
    result_map.write(
        struct.pack(str(struct.calcsize(str(len(map_dict["next_map"])) + "s")) + "s", map_dict["next_map"]))

    for y in xrange(leftmost, rightmost):
        for x in xrange(leftmost, rightmost):
            if (x, y) in map_dict["tiles"]:
                result_map.write(struct.pack("B", 1))

            if (x, y) in map_dict["player_starts"]:
                result_map.write(struct.pack("B", 2))

            result_map.write(struct.pack("B", 0))


if __name__ != "__main__":
    exit()

compile_map(*sys.argv[1:3])
