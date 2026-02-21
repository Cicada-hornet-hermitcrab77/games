import pygame
import random
import sys

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 600, 800
FPS = 60
LANE_COUNT = 4
LANE_WIDTH = 100
ROAD_LEFT = (WIDTH - LANE_COUNT * LANE_WIDTH) // 2  # 100
ROAD_RIGHT = ROAD_LEFT + LANE_COUNT * LANE_WIDTH     # 500

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (80,  80,  80)
DARK_GRAY  = (50,  50,  50)
YELLOW     = (255, 220,  0)
RED        = (220,  30,  30)
BLUE       = (30,  100, 220)
GREEN      = (30,  180,  60)
ORANGE     = (255, 140,   0)
CYAN       = (0,   210, 210)
PURPLE     = (160,  30, 200)
SKY        = (135, 206, 235)
GRASS      = (34,  139,  34)
LINE_COLOR = (240, 230,  40)

CAR_W, CAR_H = 50, 90
PLAYER_SPEED = 6
INITIAL_OBSTACLE_SPEED = 5

ENEMY_COLORS = [RED, ORANGE, CYAN, PURPLE, GREEN]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Road Racer")
clock = pygame.time.Clock()

font_large  = pygame.font.SysFont("Arial", 64, bold=True)
font_medium = pygame.font.SysFont("Arial", 36, bold=True)
font_small  = pygame.font.SysFont("Arial", 24)


# --- Helper: draw a stylised car ---
def draw_car(surface, color, x, y, w, h, is_player=False):
    """Draw a simple top-down car centred at (x, y)."""
    bx, by = x - w // 2, y - h // 2

    # Body
    pygame.draw.rect(surface, color, (bx, by, w, h), border_radius=10)

    # Windshields (lighter rectangles)
    glass = tuple(min(255, c + 80) for c in color)
    if is_player:
        pygame.draw.rect(surface, glass, (bx + 6, by + 10, w - 12, 22), border_radius=4)
        pygame.draw.rect(surface, glass, (bx + 6, by + h - 30, w - 12, 18), border_radius=4)
    else:
        pygame.draw.rect(surface, glass, (bx + 6, by + h - 32, w - 12, 22), border_radius=4)
        pygame.draw.rect(surface, glass, (bx + 6, by + 10, w - 12, 18), border_radius=4)

    # Wheels
    wheel_color = (20, 20, 20)
    for wx, wy in [(bx - 4, by + 12), (bx + w - 8, by + 12),
                   (bx - 4, by + h - 24), (bx + w - 8, by + h - 24)]:
        pygame.draw.rect(surface, wheel_color, (wx, wy, 12, 20), border_radius=4)

    # Headlights / taillights
    if is_player:
        pygame.draw.circle(surface, YELLOW, (bx + 10, by + 8), 5)
        pygame.draw.circle(surface, YELLOW, (bx + w - 10, by + 8), 5)
    else:
        pygame.draw.circle(surface, RED, (bx + 10, by + h - 8), 5)
        pygame.draw.circle(surface, RED, (bx + w - 10, by + h - 8), 5)


# --- Road drawing ---
def draw_road(surface, stripe_offset):
    # Grass shoulders
    surface.fill(GRASS)
    # Road
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, LANE_COUNT * LANE_WIDTH, HEIGHT))

    # Lane dashes
    dash_h, gap_h = 40, 30
    period = dash_h + gap_h
    for lane in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane * LANE_WIDTH
        # offset loops over period
        start = int(stripe_offset % period) - period
        y = start
        while y < HEIGHT:
            pygame.draw.rect(surface, LINE_COLOR, (lx - 2, y, 4, dash_h))
            y += period

    # Road edges (solid white lines)
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT - 4, 0, 4, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT, 0, 4, HEIGHT))


# --- Player ---
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 120
        self.w = CAR_W
        self.h = CAR_H
        self.speed = PLAYER_SPEED

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        # Clamp to road
        self.x = max(ROAD_LEFT + self.w // 2, min(ROAD_RIGHT - self.w // 2, self.x))

    def rect(self):
        return pygame.Rect(self.x - self.w // 2 + 6, self.y - self.h // 2 + 10,
                           self.w - 12, self.h - 20)

    def draw(self, surface):
        draw_car(surface, BLUE, self.x, self.y, self.w, self.h, is_player=True)


# --- Obstacle ---
class Obstacle:
    def __init__(self, speed):
        lane = random.randint(0, LANE_COUNT - 1)
        self.x = ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = -CAR_H
        self.w = CAR_W
        self.h = CAR_H
        self.speed = speed
        self.color = random.choice(ENEMY_COLORS)

    def update(self):
        self.y += self.speed

    def off_screen(self):
        return self.y > HEIGHT + self.h

    def rect(self):
        return pygame.Rect(self.x - self.w // 2 + 6, self.y - self.h // 2 + 10,
                           self.w - 12, self.h - 20)

    def draw(self, surface):
        draw_car(surface, self.color, self.x, self.y, self.w, self.h)


# --- HUD ---
def draw_hud(surface, score, best, speed_level):
    # Score
    s = font_medium.render(f"Score: {score}", True, WHITE)
    surface.blit(s, (10, 10))
    # Best
    b = font_small.render(f"Best: {best}", True, (200, 200, 200))
    surface.blit(b, (10, 52))
    # Speed level
    lv = font_small.render(f"Speed Lv {speed_level}", True, YELLOW)
    surface.blit(lv, (WIDTH - lv.get_width() - 10, 10))


def draw_game_over(surface, score, best):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    title = font_large.render("GAME OVER", True, RED)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 - 40))

    sc = font_medium.render(f"Score: {score}", True, WHITE)
    surface.blit(sc, (WIDTH // 2 - sc.get_width() // 2, HEIGHT // 2))

    be = font_medium.render(f"Best:  {best}", True, YELLOW)
    surface.blit(be, (WIDTH // 2 - be.get_width() // 2, HEIGHT // 2 + 48))

    restart = font_small.render("Press R to restart  |  Q to quit", True, (200, 200, 200))
    surface.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT * 2 // 3 + 20))


def draw_start_screen(surface):
    surface.fill(DARK_GRAY)
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, LANE_COUNT * LANE_WIDTH, HEIGHT))
    for lane in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane * LANE_WIDTH
        pygame.draw.rect(surface, LINE_COLOR, (lx - 2, 0, 4, HEIGHT))

    title = font_large.render("ROAD RACER", True, YELLOW)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

    draw_car(surface, BLUE,  WIDTH // 2,       HEIGHT // 2,      CAR_W, CAR_H, is_player=True)
    draw_car(surface, RED,   WIDTH // 2 - 110, HEIGHT // 2 - 80, CAR_W, CAR_H)
    draw_car(surface, GREEN, WIDTH // 2 + 110, HEIGHT // 2 - 40, CAR_W, CAR_H)

    sub = font_medium.render("Press SPACE to start", True, WHITE)
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT * 3 // 4))

    ctrl = font_small.render("Arrow keys or A / D to steer", True, (180, 180, 180))
    surface.blit(ctrl, (WIDTH // 2 - ctrl.get_width() // 2, HEIGHT * 3 // 4 + 50))


# --- Main game loop ---
def run_game(best_score):
    player = Player()
    obstacles = []
    score = 0
    speed_level = 1
    obstacle_speed = INITIAL_OBSTACLE_SPEED
    stripe_offset = 0.0

    spawn_timer = 0
    spawn_interval = 80   # frames between spawns
    score_timer = 0

    game_over = False

    while True:
        dt = clock.tick(FPS)

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        return best_score   # caller re-starts
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)

            # Scroll stripes
            stripe_offset += obstacle_speed

            # Spawn obstacles
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                obstacles.append(Obstacle(obstacle_speed))
                # Sometimes spawn a second car in a different lane
                if random.random() < 0.3:
                    obstacles.append(Obstacle(obstacle_speed))

            # Update obstacles
            for obs in obstacles:
                obs.update()
            obstacles = [o for o in obstacles if not o.off_screen()]

            # Score
            score_timer += 1
            if score_timer >= 10:
                score_timer = 0
                score += 1

            # Level up every 20 points
            new_level = 1 + score // 20
            if new_level != speed_level:
                speed_level = new_level
                obstacle_speed = INITIAL_OBSTACLE_SPEED + (speed_level - 1) * 1.2
                spawn_interval = max(35, 80 - speed_level * 5)
                for o in obstacles:
                    o.speed = obstacle_speed

            # Collision
            for obs in obstacles:
                if player.rect().colliderect(obs.rect()):
                    game_over = True
                    if score > best_score:
                        best_score = score

        # --- Draw ---
        draw_road(screen, stripe_offset)
        for obs in obstacles:
            obs.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, best_score, speed_level)

        if game_over:
            draw_game_over(screen, score, best_score)

        pygame.display.flip()

    return best_score


def main():
    best_score = 0

    # Start screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    best_score = run_game(best_score)
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        draw_start_screen(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
