import pygame
from src.Game.GameState import GameState
from src.Ui.MazeRenderer import MazeRenderer
from src.Game.LevelLoader import LevelLoader
from src.Game.GameRules import GameRules
from src.Game.MovementController import MovementController
from src.Entities.MovementEntity import MovingDirection


class GameController:
    def __init__(self, game_state: GameState, renderer: MazeRenderer,
                 level_loader: LevelLoader, rules: GameRules,
                 movement_controller: MovementController) -> None:
        self.game_state = game_state
        self.renderer = renderer
        self.level_loader = level_loader
        self.rules = rules
        self.movement_controller = movement_controller

    def handle_pause_key(self, key: int) -> None:
        gs = self.game_state
        if key in (pygame.K_UP, pygame.K_w):
            gs.pause_index = (gs.pause_index - 1) % len(gs.pause_options)
        elif key in (pygame.K_DOWN, pygame.K_s):
            gs.pause_index = (gs.pause_index + 1) % len(gs.pause_options)
        elif key in (pygame.K_ESCAPE, pygame.K_p):
            gs.paused = False
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            gs.paused = False
            if gs.pause_index == 1:
                gs.back_to_menu = True
                gs.running = False

    def handle_animations(self, animations: dict[str, bool]) -> None:
        if (animations.get('extra_life')):
            self.renderer.extra_life_animation()
        if (animations.get('level_skip')):
            self.renderer.trigger_level_skip_effect()
            self.game_state.pacgums.clear()
            self.game_state.super_pacgums.clear()

    def run(self) -> None:
        clock = pygame.time.Clock()
        movement_interval = 35
        time_counter = 0
        self.game_state.running = True
        self.renderer.draw_maze()

        while self.game_state.running:
            dt = min(clock.tick(60), 100)
            animations = self.game_state.bind_events(self.handle_pause_key)

            if self.game_state.paused:
                self.renderer.draw_map()
                self.renderer.draw_pause_menu()
                pygame.display.flip()
                continue

            self.renderer.draw_map()
            self.rules.check_collisions()
            self.handle_animations(animations)
            self.rules.update_timers(dt)

            if (not self.game_state.pacgums and
                    not self.game_state.super_pacgums):
                self.level_loader.load_level()
                self.renderer.draw_maze()
                clock.tick()
                time_counter = 0

            time_counter += dt
            if time_counter >= movement_interval:
                player = self.game_state.player
                if player.current_direction == MovingDirection.NOT_MOVING:
                    player.update_direction()

                moving = (player.current_direction !=
                          MovingDirection.NOT_MOVING)
                if moving:
                    self.movement_controller.calculate_next_movement(player)
                    if player.current_direction == MovingDirection.NOT_MOVING:
                        self.rules.eat_pacgums()

                if not player.is_ghost_freeze():
                    player_pos = (player.x, player.y)
                    red_ghost_pos = self.game_state.get_red_ghost_pos()
                    for ghost in self.game_state.ghosts:
                        if ghost.is_eaten():
                            continue
                        if (ghost.current_direction !=
                                MovingDirection.NOT_MOVING):
                            self.movement_controller.calculate_next_movement(
                                ghost)
                        else:
                            blocked = (self.movement_controller.
                                       get_blocked_cells(ghost))
                            if ghost.is_scared():
                                ghost.run_to_home(blocked)
                            else:
                                ghost.catch_player(player_pos,
                                                   player.current_direction,
                                                   blocked,
                                                   red_ghost_pos)
                time_counter -= movement_interval

            pygame.display.flip()
