import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 900, 550
GROUND_Y = 430
FPS = 60

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (220,  40,  40)
BLUE   = (40,  100, 220)
GREEN  = (40,  180,  60)
YELLOW = (255, 220,   0)
GRAY   = (120, 120, 120)
DARK   = (30,   30,  30)
ORANGE = (255, 140,   0)
PURPLE = (160,  40, 200)
CYAN   = (0,   200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Fighter")
clock = pygame.time.Clock()

font_large  = pygame.font.SysFont("Arial", 72, bold=True)
font_medium = pygame.font.SysFont("Arial", 36, bold=True)
font_small  = pygame.font.SysFont("Arial", 24)
font_tiny   = pygame.font.SysFont("Arial", 18)

GRAVITY = 0.55

CHARACTERS = [
    {"name": "Brawler", "color": RED,    "speed": 4, "jump": -14,
     "punch_dmg": 12, "kick_dmg": 18, "max_hp": 130,
     "desc": "Tanky heavy hitter",   "double_jump": False},
    {"name": "Ninja",   "color": CYAN,   "speed": 7, "jump": -16,
     "punch_dmg":  7, "kick_dmg": 10, "max_hp":  90,
     "desc": "Fast & double jump",   "double_jump": True},
    {"name": "Boxer",   "color": GREEN,  "speed": 5, "jump": -13,
     "punch_dmg": 16, "kick_dmg":  8, "max_hp": 110,
     "desc": "Devastating punches",  "double_jump": False},
    {"name": "Phantom", "color": PURPLE, "speed": 6, "jump": -15,
     "punch_dmg": 10, "kick_dmg": 14, "max_hp": 100,
     "desc": "Balanced & evasive",   "double_jump": True},
    {"name": "Ares",    "color": ORANGE, "speed": 5,  "jump": -14,
     "punch_dmg": 21, "kick_dmg": 20, "max_hp": 90,
     "desc": "God of War",           "double_jump": False},

]

HEAD_R   = 18
BODY_LEN = 50
ARM_LEN  = 38
LEG_LEN  = 45
NECK_LEN = 5


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_stickman(surface, x, y, color, facing, action, action_t, flash=False):
    col = WHITE if flash else color

    def ln(p1, p2, w=3):
        pygame.draw.line(surface, col, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), w)

    def circ(cx, cy, r):
        pygame.draw.circle(surface, col, (int(cx), int(cy)), r)

    waist    = (x, y - LEG_LEN)
    shoulder = (waist[0], waist[1] - BODY_LEN)
    head_c   = (shoulder[0], shoulder[1] - NECK_LEN - HEAD_R)

    # Legs
    if action == 'walk':
        t = action_t * math.pi * 2
        ls, rs = math.sin(t) * 25, -math.sin(t) * 25
    elif action == 'kick':
        ls, rs = 0, -facing * action_t * 60
    elif action == 'jump':
        ls, rs = 15, -15
    else:
        ls, rs = 5, -5

    lf = (waist[0] - ls * facing, y)
    rf = (waist[0] + rs * facing, y)
    lk = ((waist[0] + lf[0]) / 2, waist[1] + 10)
    rk = ((waist[0] + rf[0]) / 2, waist[1] + 10)
    ln(waist, lk); ln(lk, lf)
    ln(waist, rk); ln(rk, rf)

    # Arms
    if action == 'punch':
        ext = int(action_t * ARM_LEN)
        la  = (shoulder[0] - facing * 10, shoulder[1] + 10)
        lh  = (la[0] - facing * 12, la[1] + 18)
        ra  = (shoulder[0] + facing * ext, shoulder[1])
        rh  = (ra[0] + facing * (ARM_LEN - ext) * 0.3, ra[1] + 5)
    elif action == 'kick':
        la = (shoulder[0] - facing * 10, shoulder[1] + 14)
        lh = (la[0], la[1] + 22)
        ra = (shoulder[0] + facing * 15, shoulder[1] + 5)
        rh = (ra[0] + facing * 10, ra[1] + 15)
    elif action == 'walk':
        t  = action_t * math.pi * 2
        sw = math.sin(t) * 20
        la = (shoulder[0] - sw * facing * 0.5, shoulder[1] + 10)
        lh = (la[0] - 10, la[1] + ARM_LEN * 0.7)
        ra = (shoulder[0] + sw * facing * 0.5, shoulder[1] + 10)
        rh = (ra[0] + 10,  ra[1] + ARM_LEN * 0.7)
    elif action == 'hurt':
        la = (shoulder[0] - facing * 20, shoulder[1] - 10)
        lh = (la[0] - 15, la[1] - 15)
        ra = (shoulder[0] + facing * 20, shoulder[1] - 10)
        rh = (ra[0] + 15, ra[1] - 15)
    else:
        la = (shoulder[0] - 10, shoulder[1] + 10)
        lh = (la[0] - 5,  la[1] + ARM_LEN * 0.8)
        ra = (shoulder[0] + 10, shoulder[1] + 10)
        rh = (ra[0] + 5,  ra[1] + ARM_LEN * 0.8)

    ln(shoulder, la); ln(la, lh)
    ln(shoulder, ra); ln(ra, rh)
    ln(waist, shoulder, 4)
    circ(head_c[0], head_c[1], HEAD_R)

    if not flash:
        ex, ey = head_c[0] + facing * 6, head_c[1] - 3
        pygame.draw.circle(surface, WHITE, (int(ex), int(ey)), 5)
        pygame.draw.circle(surface, BLACK, (int(ex + facing * 2), int(ey)), 3)
        if action == 'hurt':
            pygame.draw.arc(surface, BLACK,
                            (int(head_c[0]-8), int(head_c[1]+2), 16, 10), 0, math.pi, 2)
        else:
            pygame.draw.arc(surface, BLACK,
                            (int(head_c[0]-8), int(head_c[1]+4), 16, 8),
                            math.pi, math.pi * 2, 2)

    if action == 'punch':
        return (int(ra[0] + facing * 10), int(ra[1]))
    if action == 'kick':
        return (int(waist[0] + facing * int(action_t * 80)), int(y - 20))
    return None


def draw_bg(surface):
    surface.fill((100, 160, 220))
    for hx, hw, hh, hc in [(0, 300, 120, (70,120,70)),
                             (220, 280, 100, (60,110,60)),
                             (440, 340, 130, (75,125,75))]:
        pygame.draw.ellipse(surface, hc, (hx, GROUND_Y - hh + 10, hw, hh * 2))
    pygame.draw.rect(surface, (60,140, 60), (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
    pygame.draw.rect(surface, (80, 60, 40), (0, GROUND_Y+24, WIDTH, HEIGHT-GROUND_Y))
    pygame.draw.line(surface, (40,100,40), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)
    for i in range(0, WIDTH, 28):
        bh = 28 + (i * 7 % 22)
        pygame.draw.ellipse(surface, (50,50,80), (i, GROUND_Y+26-bh, 22, bh))


def draw_health_bars(surface, p1, p2):
    draw_health_bars_labeled(surface, p1, p2, f"P2 — {p2.char['name']}")

def draw_health_bars_labeled(surface, p1, p2, p2_label):
    bar_w, bar_h = 300, 22

    def bar(x, y, hp, max_hp, color, name, flip=False):
        ratio = max(0, hp / max_hp)
        pygame.draw.rect(surface, (60,60,60), (x, y, bar_w, bar_h), border_radius=5)
        fw = int(bar_w * ratio)
        bx = x + bar_w - fw if flip else x
        pygame.draw.rect(surface, color, (bx, y, fw, bar_h), border_radius=5)
        pygame.draw.rect(surface, WHITE, (x, y, bar_w, bar_h), 2, border_radius=5)
        nm = font_small.render(name, True, WHITE)
        surface.blit(nm, (x + bar_w - nm.get_width() if flip else x, y - 26))
        ht = font_tiny.render(f"{max(0,hp)}/{max_hp}", True, WHITE)
        surface.blit(ht, (x + bar_w//2 - ht.get_width()//2, y + 3))

    bar(20, 40, p1.hp, p1.max_hp, p1.char["color"], f"P1 — {p1.char['name']}")
    bar(WIDTH-bar_w-20, 40, p2.hp, p2.max_hp, p2.char["color"], p2_label, flip=True)
    vs = font_medium.render("VS", True, YELLOW)
    surface.blit(vs, (WIDTH//2 - vs.get_width()//2, 35))


def draw_win_screen(surface, winner, p1, p2, vs_ai=False):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surface.blit(ov, (0, 0))
    if vs_ai:
        label = "YOU WIN!" if winner is p1 else "YOU LOSE!"
        label_color = GREEN if winner is p1 else RED
    else:
        label = "PLAYER 1 WINS!" if winner is p1 else "PLAYER 2 WINS!"
        label_color = winner.char["color"]
    t = font_large.render(label, True, label_color)
    surface.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//3 - 20))
    sub = font_medium.render(winner.char["name"], True, WHITE)
    surface.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//3 + 70))
    hint = font_small.render("R — rematch     C — char select     Q — quit", True, (200,200,200))
    surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT*2//3 + 20))


# ---------------------------------------------------------------------------
# Fighter
# ---------------------------------------------------------------------------

class Fighter:
    def __init__(self, x, char_data, facing, controls):
        self.x = float(x)
        self.y = float(GROUND_Y)
        self.vy = 0.0
        self.on_ground = True
        self.jumps_left = 2 if char_data["double_jump"] else 1
        self.char = char_data
        self.facing = facing
        self.controls = controls
        self.hp = char_data["max_hp"]
        self.max_hp = char_data["max_hp"]
        self.action = 'idle'
        self.action_t = 0.0
        self._attack_speed = 0.07
        self.attacking = False
        self.attack_hit = False
        self.hurt_timer = 0
        self.flash_timer = 0
        self.walk_t = 0.0
        self.knockback = 0.0

    def update(self, keys, other):
        if self.flash_timer > 0:
            self.flash_timer -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            if self.hurt_timer == 0 and self.action == 'hurt':
                self.action = 'idle'
                self.attacking = False

        if abs(self.knockback) > 0.1:
            self.x += self.knockback
            self.knockback *= 0.65

        self.vy += GRAVITY
        self.y  += self.vy
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            self.on_ground = True
            self.jumps_left = 2 if self.char["double_jump"] else 1

        self.x = max(50.0, min(float(WIDTH - 50), self.x))
        self.facing = 1 if other.x > self.x else -1

        if self.hurt_timer == 0:
            ctrl = self.controls
            can_atk = not self.attacking or self.action in ('idle', 'walk', 'jump')

            if can_atk and keys[ctrl['punch']]:
                self._start('punch', 0.07)
            elif can_atk and keys[ctrl['kick']]:
                self._start('kick', 0.06)
            elif keys[ctrl['jump']]:
                if self.jumps_left > 0:
                    self.vy = self.char["jump"]
                    self.on_ground = False
                    self.jumps_left -= 1
                    self.action = 'jump'
                    self.attacking = False
            elif keys[ctrl['left']]:
                self.x -= self.char["speed"]
                if self.on_ground and not self.attacking:
                    self.action = 'walk'
                    self.walk_t = (self.walk_t + 0.12) % 1.0
                    self.action_t = self.walk_t
            elif keys[ctrl['right']]:
                self.x += self.char["speed"]
                if self.on_ground and not self.attacking:
                    self.action = 'walk'
                    self.walk_t = (self.walk_t + 0.12) % 1.0
                    self.action_t = self.walk_t
            else:
                if self.on_ground and not self.attacking:
                    self.action = 'idle'

        if self.attacking and self.action in ('punch', 'kick'):
            self.action_t = min(1.0, self.action_t + self._attack_speed)
            if self.action_t >= 1.0:
                self.action = 'idle'
                self.action_t = 0.0
                self.attacking = False

    def _start(self, act, spd):
        self.action = act
        self.action_t = 0.0
        self.attacking = True
        self.attack_hit = False
        self._attack_speed = spd

    def check_hit(self, hit_pos, other):
        if hit_pos is None or self.attack_hit:
            return
        dist = math.hypot(hit_pos[0] - other.x, hit_pos[1] - (other.y - 70))
        if dist < 58:
            dmg = self.char["punch_dmg"] if self.action == 'punch' else self.char["kick_dmg"]
            other.hp = max(0, other.hp - dmg)
            other.action = 'hurt'
            other.hurt_timer = 22
            other.flash_timer = 10
            other.attacking = False
            other.knockback = self.facing * 6
            self.attack_hit = True

    def draw(self, surface):
        pygame.draw.ellipse(surface, (0,0,0),
                            (int(self.x)-25, int(self.y)-6, 50, 12))
        flash = (self.flash_timer % 4) < 2 and self.flash_timer > 0
        return draw_stickman(surface, self.x, self.y, self.char["color"],
                              self.facing, self.action, self.action_t, flash=flash)


# ---------------------------------------------------------------------------
# AI Fighter
# ---------------------------------------------------------------------------

class AIFighter(Fighter):
    """Fighter driven by a simple state-machine AI instead of keyboard input."""

    SETTINGS = {
        'easy':   dict(decision_delay=38, aggression=0.35, jump_chance=0.005, dodge_chance=0.0),
        'medium': dict(decision_delay=22, aggression=0.62, jump_chance=0.015, dodge_chance=0.1),
        'hard':   dict(decision_delay=10, aggression=0.88, jump_chance=0.030, dodge_chance=0.3),
    }

    def __init__(self, x, char_data, facing, difficulty='medium'):
        super().__init__(x, char_data, facing, controls={})
        cfg = self.SETTINGS[difficulty]
        self.decision_delay  = cfg['decision_delay']
        self.aggression      = cfg['aggression']
        self.jump_chance     = cfg['jump_chance']
        self.dodge_chance    = cfg['dodge_chance']
        self.react_timer     = self.decision_delay
        self.ai_move         = 0   # -1 left, 0 still, 1 right
        self.ai_attack       = None  # 'punch' or 'kick' or None

    def update(self, keys, other):
        # --- Physics (same as parent, no key input) ---
        if self.flash_timer > 0:
            self.flash_timer -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            if self.hurt_timer == 0 and self.action == 'hurt':
                self.action = 'idle'
                self.attacking = False

        if abs(self.knockback) > 0.1:
            self.x += self.knockback
            self.knockback *= 0.65

        self.vy += GRAVITY
        self.y  += self.vy
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            self.on_ground = True
            self.jumps_left = 2 if self.char["double_jump"] else 1

        self.x = max(50.0, min(float(WIDTH - 50), self.x))
        self.facing = 1 if other.x > self.x else -1

        # --- Advance attack animation ---
        if self.attacking and self.action in ('punch', 'kick'):
            self.action_t = min(1.0, self.action_t + self._attack_speed)
            if self.action_t >= 1.0:
                self.action = 'idle'
                self.action_t = 0.0
                self.attacking = False

        if self.hurt_timer > 0:
            return  # don't make decisions while staggered

        # --- AI decision tick ---
        self.react_timer -= 1
        if self.react_timer <= 0:
            self.react_timer = self.decision_delay + random.randint(0, 8)
            self._decide(other)

        # --- Execute decision ---
        dist = abs(other.x - self.x)
        can_atk = not self.attacking or self.action in ('idle', 'walk', 'jump')

        if self.ai_attack and can_atk:
            self._start(self.ai_attack, 0.07 if self.ai_attack == 'punch' else 0.06)
            self.ai_attack = None
        elif self.ai_move != 0:
            self.x += self.ai_move * self.char["speed"]
            if self.on_ground and not self.attacking:
                self.action = 'walk'
                self.walk_t = (self.walk_t + 0.12) % 1.0
                self.action_t = self.walk_t
        else:
            if self.on_ground and not self.attacking:
                self.action = 'idle'

    def _decide(self, other):
        dist = abs(other.x - self.x)
        direction = 1 if other.x > self.x else -1

        # Dodge incoming attack
        if other.attacking and random.random() < self.dodge_chance:
            if self.on_ground and self.jumps_left > 0:
                self.vy = self.char["jump"]
                self.on_ground = False
                self.jumps_left -= 1
                self.action = 'jump'
                self.attacking = False
                return

        ATTACK_RANGE  = 115
        PREFERRED_GAP = 70

        if dist <= ATTACK_RANGE and random.random() < self.aggression:
            # In range — attack
            self.ai_move = 0
            self.ai_attack = random.choice(['punch', 'kick'])
        elif dist > ATTACK_RANGE:
            # Too far — close in
            self.ai_move = direction
        elif dist < PREFERRED_GAP:
            # Too close — back off
            self.ai_move = -direction
        else:
            self.ai_move = 0

        # Random jump
        if self.on_ground and self.jumps_left > 0 and random.random() < self.jump_chance:
            self.vy = self.char["jump"]
            self.on_ground = False
            self.jumps_left -= 1
            self.action = 'jump'
            self.attacking = False


# ---------------------------------------------------------------------------
# Mode select screen
# ---------------------------------------------------------------------------

def mode_select():
    """Returns ('1p', difficulty) or '2p'."""
    selected = 0   # 0 = 1P, 1 = 2P
    difficulty_idx = 1   # 0=easy, 1=medium, 2=hard
    difficulties = ['easy', 'medium', 'hard']
    diff_colors  = [GREEN, YELLOW, RED]
    preview_t = 0.0

    while True:
        clock.tick(FPS)
        preview_t = (preview_t + 0.02) % 1.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                    selected = 1 - selected
                if selected == 0:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        difficulty_idx = (difficulty_idx - 1) % 3
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        difficulty_idx = (difficulty_idx + 1) % 3
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected == 0:
                        return ('1p', difficulties[difficulty_idx])
                    else:
                        return '2p'

        screen.fill(DARK)
        title = font_large.render("STICKMAN FIGHTER", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        card_w, card_h = 200, 240
        cards = [
            (WIDTH//2 - 240, "1 PLAYER",  "vs CPU", BLUE),
            (WIDTH//2 +  40, "2 PLAYERS", "local",  ORANGE),
        ]
        for ci, (cx, top, sub, col) in enumerate(cards):
            border = WHITE if ci == selected else GRAY
            pygame.draw.rect(screen, (50,50,50), (cx, 140, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, border,     (cx, 140, card_w, card_h), 3, border_radius=12)

            lbl = font_medium.render(top, True, col)
            screen.blit(lbl, (cx + card_w//2 - lbl.get_width()//2, 150))
            sl = font_small.render(sub, True, GRAY)
            screen.blit(sl, (cx + card_w//2 - sl.get_width()//2, 190))

            # preview stickmen
            draw_stickman(screen, cx + card_w//2 - 30, 140 + card_h - 30,
                          BLUE, 1, 'walk', preview_t)
            draw_stickman(screen, cx + card_w//2 + 30, 140 + card_h - 30,
                          RED, -1, 'idle', 0.0)

            if ci == selected:
                sel_txt = font_tiny.render("ENTER / SPACE to select", True, WHITE)
                screen.blit(sel_txt, (cx + card_w//2 - sel_txt.get_width()//2, 390))

        # Difficulty picker (only visible when 1P selected)
        if selected == 0:
            diff_lbl = font_small.render("Difficulty:", True, WHITE)
            screen.blit(diff_lbl, (WIDTH//2 - 240, 400))
            for di, (dname, dcol) in enumerate(zip(difficulties, diff_colors)):
                marker = "► " if di == difficulty_idx else "  "
                dt = font_small.render(f"{marker}{dname.capitalize()}", True,
                                       dcol if di == difficulty_idx else GRAY)
                screen.blit(dt, (WIDTH//2 - 230, 428 + di * 28))
            hint = font_tiny.render("↑/↓ or W/S to change", True, GRAY)
            screen.blit(hint, (WIDTH//2 - 240, 516))

        nav = font_tiny.render("◄ ► to switch mode", True, GRAY)
        screen.blit(nav, (WIDTH//2 - nav.get_width()//2, HEIGHT - 24))

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Character select screen
# ---------------------------------------------------------------------------

def character_select(vs_ai=False):
    """
    Returns (p1_idx, p2_idx).
    In vs_ai mode only P1 picks; P2 is chosen randomly after P1 confirms.
    """
    p1_idx, p2_idx = 0, 1
    p1_ready = False
    p2_ready = vs_ai   # AI doesn't need to pick
    preview_t = 0.0

    while True:
        clock.tick(FPS)
        preview_t = (preview_t + 0.02) % 1.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return None, None   # back to mode select
                if not p1_ready:
                    if event.key == pygame.K_a:     p1_idx = (p1_idx - 1) % len(CHARACTERS)
                    if event.key == pygame.K_d:     p1_idx = (p1_idx + 1) % len(CHARACTERS)
                    if event.key == pygame.K_LEFT:  p1_idx = (p1_idx - 1) % len(CHARACTERS)
                    if event.key == pygame.K_RIGHT: p1_idx = (p1_idx + 1) % len(CHARACTERS)
                    if event.key in (pygame.K_s, pygame.K_DOWN, pygame.K_RETURN, pygame.K_SPACE):
                        p1_ready = True
                        if vs_ai:
                            p2_idx = random.randint(0, len(CHARACTERS) - 1)
                if not vs_ai and p1_ready and not p2_ready:
                    if event.key == pygame.K_LEFT:  p2_idx = (p2_idx - 1) % len(CHARACTERS)
                    if event.key == pygame.K_RIGHT: p2_idx = (p2_idx + 1) % len(CHARACTERS)
                    if event.key == pygame.K_DOWN:  p2_ready = True

        if p1_ready and p2_ready:
            return p1_idx, p2_idx

        screen.fill(DARK)
        title = font_large.render("SELECT FIGHTER", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 18))

        if vs_ai:
            positions  = [WIDTH//2 - 95]
            idxs       = [p1_idx]
            readys     = [p1_ready]
            p_colors   = [BLUE]
            hints      = ["A/D or ←/→ browse   ENTER confirm"]
            labels     = ["YOU"]
        else:
            positions  = [WIDTH//2 - 260, WIDTH//2 + 70]
            idxs       = [p1_idx, p2_idx]
            readys     = [p1_ready, p2_ready]
            p_colors   = [BLUE, ORANGE]
            hints      = ["A/D browse  S confirm", "←/→ browse  ↓ confirm"]
            labels     = ["P1", "P2"]

        for pi, (cx, ch_idx, ready) in enumerate(zip(positions, idxs, readys)):
            ch = CHARACTERS[ch_idx]
            bc = GREEN if ready else p_colors[pi]
            cw, ch_h = 190, 290

            pygame.draw.rect(screen, (50,50,50), (cx, 110, cw, ch_h), border_radius=12)
            pygame.draw.rect(screen, bc,          (cx, 110, cw, ch_h), 3, border_radius=12)

            draw_stickman(screen, cx + cw//2, 110 + ch_h - 28,
                          ch["color"], 1, 'walk', preview_t)

            nm = font_medium.render(ch["name"], True, ch["color"])
            screen.blit(nm, (cx + cw//2 - nm.get_width()//2, 116))

            for si, (lbl, val) in enumerate([
                ("HP",      ch["max_hp"]),
                ("Speed",   ch["speed"]),
                ("Punch",   ch["punch_dmg"]),
                ("Kick",    ch["kick_dmg"]),
                ("2x Jump", "Yes" if ch["double_jump"] else "No"),
            ]):
                row = font_tiny.render(f"{lbl:<8}{val}", True, WHITE)
                screen.blit(row, (cx + 14, 160 + si * 22))

            desc = font_tiny.render(ch["desc"], True, YELLOW)
            screen.blit(desc, (cx + cw//2 - desc.get_width()//2, 278))

            ph = font_small.render(labels[pi], True, p_colors[pi])
            screen.blit(ph, (cx + cw//2 - ph.get_width()//2, 310))

            ht = font_tiny.render(hints[pi], True, GRAY)
            screen.blit(ht, (cx + cw//2 - ht.get_width()//2, 334))

            if ready:
                rdy = font_medium.render("READY!", True, GREEN)
                screen.blit(rdy, (cx + cw//2 - rdy.get_width()//2, 360))

        if vs_ai:
            cpu_lbl = font_medium.render("VS  CPU", True, RED)
            screen.blit(cpu_lbl, (WIDTH//2 + 60, 230))
            draw_stickman(screen, WIDTH//2 + 160, 380, RED, -1, 'idle', 0.0)

        esc_hint = font_tiny.render("ESC — back to menu", True, GRAY)
        screen.blit(esc_hint, (WIDTH//2 - esc_hint.get_width()//2, HEIGHT - 22))

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Fight loop
# ---------------------------------------------------------------------------

def run_fight(p1_idx, p2_idx, vs_ai=False, ai_difficulty='medium'):
    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l)

    p1 = Fighter(200, CHARACTERS[p1_idx],  1, P1_CTRL)
    if vs_ai:
        p2 = AIFighter(700, CHARACTERS[p2_idx], -1, ai_difficulty)
    else:
        p2 = Fighter(700, CHARACTERS[p2_idx], -1, P2_CTRL)

    game_over = False
    winner    = None
    timer     = 90 * FPS

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r: return 'rematch'
                    if event.key == pygame.K_c: return 'select'
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit(); sys.exit()
                else:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        return 'select'

        if not game_over:
            keys = pygame.key.get_pressed()
            p1.update(keys, p2)
            p2.update(keys, p1)
            timer -= 1
            if timer <= 0 or p1.hp <= 0 or p2.hp <= 0:
                game_over = True
                winner = p1 if p1.hp >= p2.hp else p2

        draw_bg(screen)
        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen)

        if not game_over:
            if p1.attacking and not p1.attack_hit:
                p1.check_hit(p1_hit, p2)
            if p2.attacking and not p2.attack_hit:
                p2.check_hit(p2_hit, p1)

        # Draw AI tag above CPU fighter
        if vs_ai:
            diff_col = {
                'easy': GREEN, 'medium': YELLOW, 'hard': RED
            }[ai_difficulty]
            cpu_tag = font_tiny.render(f"CPU [{ai_difficulty.upper()}]", True, diff_col)
            screen.blit(cpu_tag, (int(p2.x) - cpu_tag.get_width()//2,
                                  int(p2.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        p2_label = f"CPU — {p2.char['name']}" if vs_ai else f"P2 — {p2.char['name']}"
        draw_health_bars_labeled(screen, p1, p2, p2_label)

        secs = max(0, timer // FPS)
        t_surf = font_medium.render(str(secs), True, RED if secs <= 10 else WHITE)
        screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 40))

        if vs_ai:
            hint = font_tiny.render("WASD + F punch  G kick", True, (140, 140, 140))
        else:
            hint = font_tiny.render(
                "P1: WASD + F punch  G kick        P2: Arrows + K punch  L kick",
                True, (140, 140, 140))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 22))

        if game_over:
            draw_win_screen(screen, winner, p1, p2, vs_ai=vs_ai)

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    while True:
        mode = mode_select()
        if mode == '2p':
            vs_ai, difficulty = False, 'medium'
        else:
            vs_ai, difficulty = True, mode[1]

        p1_idx, p2_idx = character_select(vs_ai=vs_ai)
        if p1_idx is None:
            continue   # ESC back to mode select

        while True:
            result = run_fight(p1_idx, p2_idx, vs_ai=vs_ai, ai_difficulty=difficulty)
            if result == 'rematch':
                continue
            break   # 'select' — go back to mode select

if __name__ == "__main__":
    main()
