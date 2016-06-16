import ConfigParser
import sys

import game.map_loader
import multiplayer.main_loop

if __name__ != "__main__":
    exit("This is NOT a importable file!")

configuration = ConfigParser.ConfigParser()
configuration.read(tuple(["config\\{}.ini".format(config) for config in sys.argv[1:]]))

dmgp = multiplayer.main_loop.DMGPMultiplayer(game.map_loader.load_map(configuration.get("Game", "FirstMap")))
