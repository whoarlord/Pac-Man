PAC-MAN
=======

This project has been created as part of the 42 curriculum by iarrien- and agomez-a.

A recreation of the arcade game Pac-Man in Python. Eat all the pacgums of
every level, avoid the ghosts and save your score in the top 10.

This is the packaged (Linux) build of the game.


CONTENTS OF THE PACKAGE
-----------------------

  pac-man       The game (executable, with its support files and images).
  config.json   Configuration file of the game (see CONFIGURATION).
  launch.sh     Script that starts the game with config.json.
  README.txt    This file.


HOW TO START THE GAME
---------------------

1. Unzip the package and open a terminal in the pac-man folder.
2. Start the game with:

       sh launch.sh

   or, directly:

       ./pac-man config.json

The game must be started with exactly one argument: a configuration file that
ends in ".json". You can use your own file instead of config.json:

       ./pac-man my_config.json

The game opens a window of 1920x1080 pixels.

The highscores are saved in the file named in the configuration
(highscores.json by default), which is created in the folder from which the
game is started. launch.sh starts the game from the folder of the package.


CONTROLS
--------

  Move Pac-Man          Arrow keys or W A S D
  Pause / resume        ESC or P

  Menus                 Up/W and Down/S to choose, Enter to select,
                        ESC to go back.
  End screens           Type your name (letters, digits and spaces, up to
                        10 characters), Backspace to delete, Enter to save.

Main menu options: Start Game, View Highscores, Instructions and Exit.
Pause menu options: Resume and Return to Main Menu.


RULES
-----

- Eat all the pacgums and super pacgums to clear the level. When you clear
  the last level, you win the game.
- A super pacgum makes the ghosts edible for 7 seconds. Eating a ghost gives
  points. An eaten ghost goes back to its corner and comes back after 5
  seconds.
- Touching a ghost that is not edible costs a life. You go back to the
  center of the maze. When you have no lives left, the game is over.
- Each level has a time limit. If it reaches 0, you lose the game.
- You keep your score and your lives between levels.
- The screen shows the score, the lives, the level and the remaining time.


CHEATS
------

These keys work during the game:

  I   Invincibility on/off (ghosts do not take lives).
  V   Adds one life (the maximum is 10).
  B   Speed boost on/off.
  F   Ghost freeze on/off (ghosts stop moving).
  L   Skips the current level.

The icons of the active cheats are shown on the screen.


CONFIGURATION
-------------

config.json is a JSON file. Lines that start with # are comments. Every key
is optional. If a key is missing or its value is not valid, a message is
printed in the terminal and the default value is used. Unknown keys are
ignored.

  Key                       Meaning                          Default
  ------------------------  -------------------------------  ----------------
  highscore_filename        File where scores are saved      highscores.json
  levels                    List of levels, each one with    10 levels of
                            "width" and "height" in cells    20x20
                            (between 5 and 100). The game
                            has at least 10 levels: if
                            there are fewer, they are
                            completed with default ones.
  lives                     Lives at the start (1 to 10)     3
  pacgum                    Pacgums per level (> 0)          90% of the free
                                                             cells
  points_per_pacgum         Points for a pacgum (1-99999)    10
  points_per_super_pacgum   Points for a super pacgum        50
                            (1-99999)
  points_per_ghost          Points for an edible ghost       200
                            (1-99999)
  seed                      Seed of the maze of level 1      42
                            (> 0). The other levels are
                            random.
  level_max_time            Seconds per level (> 0)          90

Example:

  {
    "highscore_filename": "highscores.json",
    "levels": [
      { "width": 25, "height": 25 },
      { "width": 16, "height": 16 }
    ],
    "lives": 3,
    "seed": 43,
    "level_max_time": 90
  }
