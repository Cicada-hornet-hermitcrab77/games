import pygame
import random
import sys

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 600, 800
FPS = 60
LANE_COUNT = 4
LANE_WIDTH = 100
ROAD_LEFT = (WIDTH - LANE_COUNT * LANE_WIDTH) // 2   # 100
ROAD_RIGHT = ROAD_LEFT + LANE_COUNT * LANE_WIDTH      # 500

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (80,  80,  80)
DARK_GRAY  = (50,  50,  50)
YELLOW     = (255, 225,   0)
RED        = (220,  30,  30)
BLUE       = (30,  100, 220)
GREEN      = (30,  180,  60)
ORANGE     = (255, 140,   0)
CYAN       = (0,   210, 210)
PURPLE     = (160,  30, 200)
GRASS      = (34,  139,  34)
LINE_COLOR = (240, 230,  40)

CAR_W, CAR_H = 50, 90
PLAYER_SPEED = 6
INITIAL_OBSTACLE_SPEED = 5

ENEMY_COLORS = [RED, ORANGE, CYAN, PURPLE, GREEN, BLACK]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Road Racer — 2 Player")
clock = pygame.time.Clock()

font_large  = pygame.font.SysFont("Arial", 64, bold=True)
font_medium = pygame.font.SysFont("Arial", 36, bold=True)
font_small  = pygame.font.SysFont("Arial", 24)
font_tiny   = pygame.font.SysFont("Arial", 18)


# --- Helper: draw a stylised car ---
def draw_car(surface, color, x, y, w, h, is_player=False, crashed=False):
    bx, by = x - w // 2, y - h // 2

    draw_color = (100, 100, 100) if crashed else color
    pygame.draw.rect(surface, draw_color, (bx, by, w, h), border_radius=10)

    if not crashed:
        glass = tuple(min(255, c + 80) for c in color)
        if is_player:
            pygame.draw.rect(surface, glass, (bx + 6, by + 10, w - 12, 22), border_radius=4)
            pygame.draw.rect(surface, glass, (bx + 6, by + h - 30, w - 12, 18), border_radius=4)
        else:
            pygame.draw.rect(surface, glass, (bx + 6, by + h - 32, w - 12, 22), border_radius=4)
            pygame.draw.rect(surface, glass, (bx + 6, by + 10, w - 12, 18), border_radius=4)

    wheel_color = (20, 20, 20)
    for wx, wy in [(bx - 4, by + 12), (bx + w - 8, by + 12),
                   (bx - 4, by + h - 24), (bx + w - 8, by + h - 24)]:
        pygame.draw.rect(surface, wheel_color, (wx, wy, 12, 20), border_radius=4)

    if not crashed:
        if is_player:
            pygame.draw.circle(surface, YELLOW, (bx + 10, by + 8), 5)
            pygame.draw.circle(surface, YELLOW, (bx + w - 10, by + 8), 5)
        else:
            pygame.draw.circle(surface, RED, (bx + 10, by + h - 8), 5)
            pygame.draw.circle(surface, RED, (bx + w - 10, by + h - 8), 5)

    if crashed:
        x_surf = font_medium.render("X", True, RED)
        surface.blit(x_surf, (x - x_surf.get_width() // 2, y - x_surf.get_height() // 2))


# --- Road drawing ---
def draw_road(surface, stripe_offset):
    surface.fill(GRASS)
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, LANE_COUNT * LANE_WIDTH, HEIGHT))

    dash_h, gap_h = 40, 30
    period = dash_h + gap_h
    for lane in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane * LANE_WIDTH
        start = int(stripe_offset % period) - period
        y = start
        while y < HEIGHT:
            pygame.draw.rect(surface, LINE_COLOR, (lx - 2, y, 4, dash_h))
            y += period

    pygame.draw.rect(surface, WHITE, (ROAD_LEFT - 4, 0, 4, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT, 0, 4, HEIGHT))


# --- Player ---
class Player:
    def __init__(self, start_x, color, left_key, right_key):
        self.x = start_x
        self.y = HEIGHT - 120
        self.w = CAR_W
        self.h = CAR_H
        self.speed = PLAYER_SPEED
        self.color = color
        self.left_key = left_key
        self.right_key = right_key
        self.alive = True
        self.score = 0

    def move(self, keys):
        if not self.alive:
            return
        if keys[self.left_key]:
            self.x -= self.speed
        if keys[self.right_key]:
            self.x += self.speed
        self.x = max(ROAD_LEFT + self.w // 2, min(ROAD_RIGHT - self.w // 2, self.x))

    def rect(self):
        return pygame.Rect(self.x - self.w // 2 + 6, self.y - self.h // 2 + 10,
                           self.w - 12, self.h - 20)

    def draw(self, surface):
        draw_car(surface, self.color, self.x, self.y, self.w, self.h,
                 is_player=True, crashed=not self.alive)


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
def draw_hud(surface, p1, p2, speed_level):
    # P1 label + score (left, blue)
    tag1 = font_tiny.render("P1  ◄ ►", True, BLUE)
    surface.blit(tag1, (10, 10))
    sc1 = font_medium.render(str(p1.score), True, BLUE if p1.alive else (100, 100, 180))
    surface.blit(sc1, (10, 32))

    # P2 label + score (right, orange)
    tag2 = font_tiny.render("P2  A D", True, ORANGE)
    surface.blit(tag2, (WIDTH - tag2.get_width() - 10, 10))
    sc2 = font_medium.render(str(p2.score), True, ORANGE if p2.alive else (180, 120, 50))
    surface.blit(sc2, (WIDTH - sc2.get_width() - 10, 32))

    # Speed level centred
    lv = font_tiny.render(f"Speed Lv {speed_level}", True, YELLOW)
    surface.blit(lv, (WIDTH // 2 - lv.get_width() // 2, 10))

    # "CRASHED" banner under dead players
    if not p1.alive:
        cr = font_tiny.render("CRASHED", True, RED)
        surface.blit(cr, (10, 68))
    if not p2.alive:
        cr = font_tiny.render("CRASHED", True, RED)
        surface.blit(cr, (WIDTH - cr.get_width() - 10, 68))


def draw_game_over(surface, p1, p2):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    # Determine winner
    if p1.score > p2.score:
        winner_text = "PLAYER 1 WINS!"
        winner_color = BLUE
    elif p2.score > p1.score:
        winner_text = "PLAYER 2 WINS!"
        winner_color = ORANGE
    else:
        winner_text = "IT'S A DRAW!"
        winner_color = YELLOW

    title = font_large.render("GAME OVER", True, RED)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))

    win = font_medium.render(winner_text, True, winner_color)
    surface.blit(win, (WIDTH // 2 - win.get_width() // 2, HEIGHT // 5 + 80))

    # Score breakdown
    s1 = font_medium.render(f"P1: {p1.score}", True, BLUE)
    s2 = font_medium.render(f"P2: {p2.score}", True, ORANGE)
    surface.blit(s1, (WIDTH // 2 - 130, HEIGHT // 2 + 20))
    surface.blit(s2, (WIDTH // 2 + 20,  HEIGHT // 2 + 20))

    restart = font_small.render("R — restart   Q — quit", True, (200, 200, 200))
    surface.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT * 2 // 3 + 30))


def draw_start_screen(surface):
    surface.fill(DARK_GRAY)
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, LANE_COUNT * LANE_WIDTH, HEIGHT))
    for lane in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane * LANE_WIDTH
        pygame.draw.rect(surface, LINE_COLOR, (lx - 2, 0, 4, HEIGHT))

    title = font_large.render("ROAD RACER", True, YELLOW)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 6))

    sub = font_medium.render("2 PLAYER", True, WHITE)
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 6 + 72))

    mid_y = HEIGHT // 2
    draw_car(surface, BLUE,   ROAD_LEFT + LANE_WIDTH,               mid_y, CAR_W, CAR_H, is_player=True)
    draw_car(surface, ORANGE, ROAD_LEFT + LANE_COUNT * LANE_WIDTH - LANE_WIDTH, mid_y, CAR_W, CAR_H, is_player=True)
    draw_car(surface, RED,    ROAD_LEFT + 2 * LANE_WIDTH,           mid_y - 120, CAR_W, CAR_H)

    ctrl1 = font_small.render("P1:  ◄ ► Arrow keys", True, BLUE)
    ctrl2 = font_small.render("P2:  A / D", True, ORANGE)
    surface.blit(ctrl1, (WIDTH // 2 - ctrl1.get_width() // 2, HEIGHT * 3 // 4 - 10))
    surface.blit(ctrl2, (WIDTH // 2 - ctrl2.get_width() // 2, HEIGHT * 3 // 4 + 30))

    go = font_small.render("Press SPACE to start", True, WHITE)
    surface.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT * 3 // 4 + 80))


# --- Main game loop ---
def run_game():
    p1 = Player(ROAD_LEFT + LANE_WIDTH,                            BLUE,   pygame.K_LEFT,  pygame.K_RIGHT)
    p2 = Player(ROAD_LEFT + LANE_COUNT * LANE_WIDTH - LANE_WIDTH,  ORANGE, pygame.K_a,     pygame.K_d)

    obstacles = []
    speed_level = 1
    obstacle_speed = INITIAL_OBSTACLE_SPEED
    stripe_offset = 0.0

    spawn_timer = 0
    spawn_interval = 80
    score_timer = 0
    game_over = False

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    return
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        if not game_over:
            keys = pygame.key.get_pressed()
            p1.move(keys)
            p2.move(keys)

            stripe_offset += obstacle_speed

            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                obstacles.append(Obstacle(obstacle_speed))
                if random.random() < 0.4:
                    obstacles.append(Obstacle(obstacle_speed))

            for obs in obstacles:
                obs.update()
            obstacles = [o for o in obstacles if not o.off_screen()]

            score_timer += 1
            if score_timer >= 10:
                score_timer = 0
                if p1.alive:
                    p1.score += 1
                if p2.alive:
                    p2.score += 1

            # Level based on highest score
            top_score = max(p1.score, p2.score)
            new_level = 1 + top_score // 20
            if new_level != speed_level:
                speed_level = new_level
                obstacle_speed = INITIAL_OBSTACLE_SPEED + (speed_level - 1) * 1.2
                spawn_interval = max(35, 80 - speed_level * 5)
                for o in obstacles:
                    o.speed = obstacle_speed

            # Obstacle collisions
            for obs in obstacles:
                if p1.alive and p1.rect().colliderect(obs.rect()):
                    p1.alive = False
                if p2.alive and p2.rect().colliderect(obs.rect()):
                    p2.alive = False

            # Player-vs-player collision — both crash
            if p1.alive and p2.alive and p1.rect().colliderect(p2.rect()):
                p1.alive = False
                p2.alive = False

            if not p1.alive and not p2.alive:
                game_over = True

        # --- Draw ---
        draw_road(screen, stripe_offset)
        for obs in obstacles:
            obs.draw(screen)
        p1.draw(screen)
        p2.draw(screen)
        draw_hud(screen, p1, p2, speed_level)

        if game_over:
            draw_game_over(screen, p1, p2)

        pygame.display.flip()


def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run_game()
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        draw_start_screen(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
