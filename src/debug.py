import game.game
import multiplayer.main_loop

if __name__ != "__main__":
    exit("This is NOT a importable file!")

dmgp = multiplayer.main_loop.DMGPMultiplayer(game.game.Map())
