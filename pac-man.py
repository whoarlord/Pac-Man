"""Launcher script for the Pac-Man game.

This file is the executable entry point of the project. It only delegates
to :func:`src.__main__.main`, which handles argument parsing and the game
loop.
"""

from src.__main__ import main

if __name__ == "__main__":
    main()
