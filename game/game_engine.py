
import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60


class GameEngine:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)

        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)

        self.player = Player(0, 0)

        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),  # Bottom-right
            Enemy(ROWS - 1, 0),         # Bottom-left
            Enemy(0, COLS - 1),         # Top-right
        ]

        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10,
        )

        # Task 3: Power pellet
        # Place it away from the player's starting position and exit.
        pellet_row = 2
        pellet_col = 2

        pellet_x = pellet_col * CELL + CELL // 2
        pellet_y = pellet_row * CELL + CELL // 2

        self.power_pellet_rect = pygame.Rect(
            pellet_x - 8,
            pellet_y - 8,
            16,
            16,
        )

        self.caught = False
        self.won = False

        # Task 2: Difficulty progression
        self.start_time = pygame.time.get_ticks()
        self.speed_tier = 1

        # Task 4: Survival score, measured in frames
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                self.reset()

        return True

    def update(self):
        if self.caught or self.won:
            return

        # Task 2: Increase difficulty every 15 seconds.
        elapsed = pygame.time.get_ticks() - self.start_time
        self.speed_tier = elapsed // 15000 + 1

        new_interval = max(
            5,
            20 - (self.speed_tier - 1) * 2,
        )

        for enemy in self.enemies:
            enemy.move_interval = new_interval

        # Move the player.
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)

        # Task 4: Award one point per active gameplay frame.
        self.score += 1

        # Task 3: Collect the power pellet.
        if (
            self.power_pellet_rect is not None
            and self.player.rect.colliderect(
                self.power_pellet_rect
            )
        ):
            # Freeze all enemies for five seconds.
            for enemy in self.enemies:
                enemy.frozen = True
                enemy.freeze_timer = FPS * 5

            # Remove the pellet after collection.
            self.power_pellet_rect = None

        # Update all enemies and check for collisions.
        for enemy in self.enemies:
            enemy.update(
                self.walls,
                self.player,
                ROWS,
                COLS,
            )

            if self.player.rect.colliderect(enemy.rect):
                self.caught = True
                break

        # Check whether the player has reached the exit.
        if (
            not self.caught
            and self.player.rect.colliderect(self.exit_rect)
        ):
            self.won = True

    def draw(self):
        self.screen.fill((230, 220, 210))
        wall_color = (50, 40, 60)

        # Draw the maze.
        for r in range(ROWS):
            for c in range(COLS):
                x = c * CELL
                y = r * CELL
                walls = self.walls[r][c]

                if walls[0]:
                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y),
                        (x + CELL, y),
                        3,
                    )

                if walls[1]:
                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        3,
                    )

                if walls[2]:
                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        3,
                    )

                if walls[3]:
                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y),
                        (x, y + CELL),
                        3,
                    )

        # Draw the exit.
        pygame.draw.rect(
            self.screen,
            (80, 200, 80),
            self.exit_rect,
            border_radius=4,
        )

        exit_label = self.font.render(
            "EXIT",
            True,
            (20, 80, 20),
        )

        self.screen.blit(
            exit_label,
            (self.exit_rect.x + 2, self.exit_rect.y + 6),
        )

        # Task 3: Draw the power pellet while it exists.
        if self.power_pellet_rect is not None:
            pygame.draw.circle(
                self.screen,
                (255, 220, 0),
                self.power_pellet_rect.center,
                9,
            )

            # Small highlight on the pellet.
            pygame.draw.circle(
                self.screen,
                (255, 250, 160),
                (
                    self.power_pellet_rect.centerx - 2,
                    self.power_pellet_rect.centery - 2,
                ),
                3,
            )

        # Draw the player and enemies.
        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        # HUD.
        hud = pygame.Rect(
            0,
            ROWS * CELL,
            WIDTH,
            50,
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud,
        )

        survival_seconds = self.score // FPS

        info = self.font.render(
            f"Tier:{self.speed_tier} "
            f"Survived:{survival_seconds}s R=Restart",
            True,
            (230, 230, 230),
        )

        self.screen.blit(
            info,
            (8, ROWS * CELL + 14),
        )

        # Game-over overlays.
        if self.caught:
            self._overlay("CAUGHT!", (220, 60, 60))

        elif self.won:
            self._overlay("ESCAPED!", (80, 220, 80))

        pygame.display.flip()

    def _overlay(self, message, color):
        overlay = pygame.Surface(
            (WIDTH, ROWS * CELL),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render(
            message,
            True,
            color,
        )

        final_score = self.font.render(
            f"Final score: {self.score}",
            True,
            (255, 255, 255),
        )

        survival_time = self.font.render(
            f"Survived: {self.score // FPS}s",
            True,
            (220, 220, 220),
        )

        restart = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200),
        )

        center_x = WIDTH // 2
        center_y = (ROWS * CELL) // 2

        self.screen.blit(
            title,
            (
                center_x - title.get_width() // 2,
                center_y - 65,
            ),
        )

        self.screen.blit(
            final_score,
            (
                center_x - final_score.get_width() // 2,
                center_y - 15,
            ),
        )

        self.screen.blit(
            survival_time,
            (
                center_x - survival_time.get_width() // 2,
                center_y + 15,
            ),
        )

        self.screen.blit(
            restart,
            (
                center_x - restart.get_width() // 2,
                center_y + 50,
            ),
        )

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
