import ConfigParser
import sys

import game.map_loader
import multiplayer.main_loop

if __name__ != "__main__":
    exit("This is NOT a importable file!")

configuration = ConfigParser.ConfigParser()
configuration.read(tuple(["config\\{}.ini".format(config) for config in sys.argv[1:]]))

dmgp = multiplayer.main_loop.DMGPMultiplayer(game.map_loader.load_map(configuration.get("Game", "FirstMap")))

raw_connections = configuration.get("Game", "Connections")
connections = []

for line in raw_connections.split(" "):
    print "Adding {} to connection list...".format(line)

    try:

        connections.append((line.split(":")[0], int(line.split(":")[1])))
    except IndexError:
        pass

for connection in connections:
    dmgp.connect_to(connection[0], connection[1])
