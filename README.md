# Dungeon-Engine
A CCTG rewrite and full multi-layered engine that allows for better socket connections and a simple tile-based map compiler and loader.
-----

# FAQ

## General

### What does this do?
Basically, loads binary maps (compiled from ASCII maps; see below for "How do I compile my ASCII map?") that are mapped to a 2D dungeon, then distributes game data around using two high-level socket-based classes.

The peer-to-peer protocol is very similiar to CCTG's, though it's more specialized towards games.

### Why is my map parsed with so many errors?
It's an [big bug](https://github.com/Gustavo6046/Dungeon-Engine/issues/1) we can't find a solution for, sorry :(

### What Python version is this for?
It was coded in 2.7.11 but I can't find out compatibility with other versions :/

## Mapping

### How do I make my own maps for this... "game"?
This is the format for the ASCII maps you should do:

    EXIT <x coordinate of map exit> <y coordinate of map exit>
    NEXTMAP <string containing name of the next map as the filename without extension of the compiled map>
    PLAYERSTART <x coordinate of player start> <y coordinate of player start>
    TILE <x coordinate of tile> <y coordinate of tile>
    
Currently, the uppercase is necessary.

After this you must compile your map so it can be loaded by the Map Loader.

### How do I compile my ASCII map?
Put your ASCII map file (.dam) inside any folder side-by-side with the map loader folder, and create a new folder (name it however you want) where you want the compiled map to be.
Then open your terminal, `cd` to the folder where both folders are located and run your map compiler like this:

    python compile_map "<folder of ASCII map file>\<filename of ASCII map file>.dam" "<folder where you want to store compiled result>\<mapname>.dbm"
