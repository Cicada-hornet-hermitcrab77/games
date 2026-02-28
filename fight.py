#!/usr/bin/python3
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
font_tiny   = pygame.font.SysFont("Arial", 13)

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
     {"name": "Zephyr",  "color": BLUE,  "speed": 9,  "jump": -18,
     "punch_dmg": 10, "kick_dmg": 14, "max_hp": 100,
     "desc": "Swift and agile",      "double_jump": True},
     {"name": "Titan",  "color": YELLOW,  "speed": 3,  "jump": -7,
     "punch_dmg": 18, "kick_dmg": 16, "max_hp": 155,
     "desc": "Enormous Health",      "double_jump": False},
    {"name": "Dancing Man",    "color": (100, 100, 255), "speed": 10,  "jump": -20,
     "punch_dmg": 10, "kick_dmg": 10, "max_hp": 100,
     "desc": "evasive",    "double_jump": True},
    {"name": "Tank",   "color": (30, 30, 30), "speed": 1,  "jump": -0,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 190,
     "desc": "Defensive",   "double_jump": False},
    {"name": "Mighty Medieval Man",  "color": GRAY, "speed": 4,  "jump": -18,
     "punch_dmg": 15, "kick_dmg": 15, "max_hp": 120,
     "desc": "Lord of chivalry",   "double_jump": False},
    {"name": "Samurai",   "color": BLACK, "speed": 6,  "jump": -15,
     "punch_dmg": 12, "kick_dmg": 19, "max_hp": 170,
     "desc": "Katana Master",   "double_jump": True},
    {"name": "Skeleton",   "color": WHITE,   "speed": 3, "jump": -5,
     "punch_dmg":  25, "kick_dmg": 20, "max_hp":  65,
     "desc": "Dead",   "double_jump": False},
    {"name": "Unknown",   "color": (100, 160, 220),   "speed": 5,  "jump": -5,
     "punch_dmg":  3, "kick_dmg": 5, "max_hp":  300,
     "desc": "Mysterious and powerful",   "double_jump": True},
    {"name": "Hardy", "color": (110, 120, 225), "speed": 3, "jump": -5,
     "punch_dmg": 3, "kick_dmg": 4, "max_hp": 65,
     "desc": "Pros should try him",   "double_jump": False},
    {"name": "Rogue", "color": (220, 180, 60), "speed": 8, "jump": -17,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 80,
     "desc": "Stealthy and agile",   "double_jump": True},
    {"name": "Gladiator", "color": (200, 80, 80), "speed": 4, "jump": -12,
     "punch_dmg": 14, "kick_dmg": 18, "max_hp": 140,
     "desc": "Arena Champion",   "double_jump": False},
    {"name": "Oni", "color": (80, 220, 200), "speed": 2, "jump": -1,
     "punch_dmg": 12, "kick_dmg": 14, "max_hp": 200,
     "desc": "Fat Demon",   "double_jump": False},
    {"name": "Cecalia",     "color": (50, 255, 255), "speed": 8,  "jump": -8,
     "punch_dmg": 8,  "kick_dmg": 8,  "max_hp": 300,
     "desc": "Octo hard",        "double_jump": False},
    {"name": "Acrobat",     "color": (255, 180, 80), "speed": 8,  "jump": -20,
     "punch_dmg": 8,  "kick_dmg": 12, "max_hp": 85,
     "desc": "Aerial specialist", "double_jump": True},
    {"name": "Shapeshifter", "color": (180, 80, 255), "seed": 6, "jump": -15,
     "punch_dmg": 14, "kick_dmg": 14, "max_hp": 105,
     "desc": "Unpredictable",    "double_jump": True},
    {"name": "Spring",   "color": (255, 100, 100), "speed": 10, "jump": -45,
     "punch_dmg": 1, "kick_dmg": 1, "max_hp": 400,
     "desc": "Bouncy",   "double_jump": True},
    {"name": "Harpy",   "color": (150, 0, 150), "speed": 9, "jump": -19,
     "punch_dmg": 20, "kick_dmg": 20, "max_hp": 40,
     "desc": "Blood-eater",   "double_jump": True},
    {"name": "Scarecrow",   "color": (50, 0, 50), "speed": 1, "jump": -0,
     "punch_dmg": 100, "kick_dmg": 100, "max_hp": 60,
     "desc": "Strong and Weak",   "double_jump": False},
    {"name": "Cactus", "color": (40, 180, 60), "speed": 4, "jump": -11,
     "punch_dmg": 4, "kick_dmg": 4, "max_hp": 135,
     "desc": "Poisons on contact", "double_jump": False, "contact_dmg": 8},
    {"name": "Medic", "color": (200, 255, 200), "speed": 5, "jump": -13,
     "punch_dmg": 7, "kick_dmg": 9, "max_hp": 120,
     "desc": "+2 HP every 5 seconds", "double_jump": False, "regen": True},
    {"name": "Arsonist", "color": (255, 80, 20), "speed": 6, "jump": -14,
     "punch_dmg": 10, "kick_dmg": 8, "max_hp": 100,
     "desc": "Punches set targets on fire", "double_jump": False, "fire_punch": True},
    {"name": "Cryogenisist", "color": (150, 220, 255), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 0, "max_hp": 110,
     "desc": "Kicks freeze opponents for 3s", "double_jump": False, "freeze_kick": True},
]

POWERUPS = [
    # --- existing ---
    {'name': 'Swiftness',     'type': 'speed',     'mult': 1.6,  'duration': 360, 'color': (80, 200, 250)},
    {'name': 'Rage',      'type': 'kick_dmg',  'amount': 10, 'duration': 500, 'color': (240,120,  40)},
    {'name': 'Drugs',     'type': 'punch_dmg', 'amount': 10, 'duration': 540, 'color': (180,240, 180)},
    {'name': 'Heal',      'type': 'heal',       'amount': 30, 'duration': 0,   'color': (200,255, 120)},
    {'name': 'Poison',    'type': 'heal',       'amount':-30, 'duration': 0,   'color': (200,160, 255)},
    # --- new ---
    {'name': 'Turbo',     'type': 'speed',     'mult': 2.4,  'duration': 180, 'color': (255,230,   0)},
    {'name': 'Forcefield',    'type': 'shield',    'reduction': 0.5, 'duration': 360, 'color': (100,150, 255)},
    {'name': 'Leech',     'type': 'leech',     'amount':  8, 'duration': 360, 'color': (200,  0, 200)},
    {'name': 'MegaHeal',  'type': 'heal',      'amount': 60, 'duration': 0,   'color': (0,   220,  80)},
    {'name': 'Bomb',      'type': 'heal',      'amount':-60, 'duration': 0,   'color': (255,  60,   0)},
    {'name': 'Wither',      'type': 'speed',     'amount':  -2, 'duration': 420, 'color': (255,  0,  0)},
    {'name': '2x Trouble',  'type': 'clone',     'duration': 0,                  'color': (255, 80, 200)},
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


STAGES = [
    # Grasslands: stepped hillside — wide low left, medium right, wide slow mover up top
    {"name": "Grasslands", "platforms": [
        (60,  GROUND_Y-90,  200, 0,   0),
        (640, GROUND_Y-140, 140, 0,   0),
        (310, GROUND_Y-215, 210, 1.5, 140),
    ], "springs": [
        (310, -22), (620, -22),   # two normal springs
    ]},
    # Volcano: all platforms move, narrow center pillar is static and high
    {"name": "Volcano", "platforms": [
        (70,  GROUND_Y-120, 130, 2,   80),
        (630, GROUND_Y-150, 120, -2,  70),
        (395, GROUND_Y-240, 100, 0,   0),
    ], "springs": [
        (450, -30),   # one super-launch spring (blast off like lava)
    ]},
    # Dojo: symmetric sides at the same height, fast mover in center
    {"name": "Dojo", "platforms": [
        (50,  GROUND_Y-115, 155, 0,   0),
        (695, GROUND_Y-115, 155, 0,   0),
        (355, GROUND_Y-205, 145, 2.5, 100),
    ], "springs": [
        (230, -22), (670, -22),   # symmetric springs matching dojo layout
    ]},
    # Desert: two wide low dunes (static), one slow wide drifter
    {"name": "Desert", "platforms": [
        (80,  GROUND_Y-75,  220, 0,   0),
        (590, GROUND_Y-110, 190, 0,   0),
        (330, GROUND_Y-185, 180, 1,   160),
    ], "springs": [
        (180, -20), (450, -20), (720, -20),   # three weak springs spread across open desert
    ]},
    # Arena: all three platforms move, two springs for chaos
    {"name": "Arena", "platforms": [
        (80,  GROUND_Y-110, 140, 2,   120),
        (620, GROUND_Y-110, 140, -2,  120),
        (350, GROUND_Y-210, 160, 3,   160),
    ], "springs": [
        (250, -24), (640, -24),
    ]},
    # Dream Land: 4 static cloud platforms, 6 springs everywhere
    {"name": "Dream Land", "platforms": [
        (55,  GROUND_Y-95,  175, 0,   0),
        (670, GROUND_Y-95,  175, 0,   0),
        (195, GROUND_Y-190, 155, 0,   0),
        (550, GROUND_Y-190, 155, 0,   0),
    ], "springs": [
        (80,  -22), (235, -22), (390, -22),
        (530, -22), (680, -22), (820, -22),
    ]},
]

# Stage-specific character advantages and disadvantages.
# adv gets +25% speed & +25% damage; dis gets -20% speed & -20% damage.
STAGE_MATCHUPS = {
    "Grasslands": {"adv": "Scarecrow",   "dis": "Titan"},
    "Volcano":    {"adv": "Arsonist",    "dis": "Cryogenisist"},
    "Dojo":       {"adv": "Ninja",       "dis": "Oni"},
    "Desert":     {"adv": "Cactus",      "dis": "Tank"},
    "Arena":      {"adv": "Gladiator",   "dis": "Rogue"},
    "Dream Land": {"adv": "Spring",      "dis": "Brawler"},
}


def draw_bg(surface, stage_idx=0):
    s = stage_idx % len(STAGES)

    if s == 0:  # Grasslands
        surface.fill((100, 160, 220))
        for hx, hw, hh, hc in [(0,300,120,(70,120,70)),(220,280,100,(60,110,60)),(440,340,130,(75,125,75))]:
            pygame.draw.ellipse(surface, hc, (hx, GROUND_Y-hh+10, hw, hh*2))
        pygame.draw.rect(surface, (60,140,60), (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (80, 60,40), (0, GROUND_Y+24, WIDTH, HEIGHT-GROUND_Y))
        pygame.draw.line(surface, (40,100,40), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)

    elif s == 1:  # Volcano
        surface.fill((60, 20, 10))
        pygame.draw.polygon(surface, (30,15,5), [(310,GROUND_Y+2),(420,170),(530,GROUND_Y+2)])
        pygame.draw.polygon(surface, (30,15,5), [(60,GROUND_Y+2),(140,240),(220,GROUND_Y+2)])
        pygame.draw.circle(surface, (255,120,0), (420, 172), 18)
        pygame.draw.circle(surface, (255,200,50), (420, 172), 8)
        pygame.draw.rect(surface, (40,20,10), (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.line(surface, (180,60,0), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)

    elif s == 2:  # Dojo
        surface.fill((15, 10, 30))
        for sx, sy in [(80,40),(180,80),(300,30),(450,60),(600,20),(750,70),(850,45)]:
            pygame.draw.circle(surface, WHITE, (sx, sy), 2)
        pygame.draw.circle(surface, (240,240,200), (750, 80), 40)
        pygame.draw.circle(surface, (15,10,30), (770, 70), 35)
        for tx in [120, 680]:
            pygame.draw.rect(surface, (160,30,30), (tx-5,  GROUND_Y-160, 10, 160))
            pygame.draw.rect(surface, (160,30,30), (tx+45, GROUND_Y-160, 10, 160))
            pygame.draw.rect(surface, (160,30,30), (tx-15, GROUND_Y-160, 80, 12))
        pygame.draw.rect(surface, (100,65,30), (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.line(surface, (60,38,15), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)

    elif s == 3:  # Desert
        surface.fill((220, 150, 60))
        pygame.draw.circle(surface, (255,230,80), (120, 80), 50)
        pygame.draw.circle(surface, (255,245,150), (120, 80), 38)
        for hx, hw, hh, hc in [(0,400,70,(210,165,80)),(280,380,55,(200,158,75)),(580,400,80,(215,168,82))]:
            pygame.draw.ellipse(surface, hc, (hx, GROUND_Y-hh+10, hw, hh*2))
        for cx in [150, 400, 680]:
            pygame.draw.rect(surface, (40,110,40), (cx-6,  GROUND_Y-80, 12, 82))
            pygame.draw.rect(surface, (40,110,40), (cx-22, GROUND_Y-60, 16, 10))
            pygame.draw.rect(surface, (40,110,40), (cx+6,  GROUND_Y-55, 16, 10))
        pygame.draw.rect(surface, (210,175,90), (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.line(surface, (170,135,55), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)

    elif s == 4:  # Arena
        surface.fill((10, 10, 20))
        # crowd stands on both sides
        for bx, bw in [(0, 160), (740, 160)]:
            pygame.draw.rect(surface, (30, 30, 50), (bx, 80, bw, GROUND_Y - 80))
            for row in range(4):
                for col in range(bw // 22):
                    hx = bx + col * 22 + 4
                    hy = 100 + row * 40
                    hcol = [(200,60,60),(60,60,200),(60,200,60),(200,200,60)][((hx+hy)//22) % 4]
                    pygame.draw.circle(surface, hcol, (hx, hy), 7)
        # arena floor
        pygame.draw.rect(surface, (50, 50, 70),  (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (35, 35, 55),  (0, GROUND_Y+20, WIDTH, HEIGHT-GROUND_Y))
        pygame.draw.line(surface, (80, 80, 120), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)
        for tx in range(0, WIDTH, 60):
            pygame.draw.line(surface, (60, 60, 85), (tx, GROUND_Y+2), (tx, HEIGHT), 1)
        # spotlight beams
        for lx in [200, 450, 700]:
            pygame.draw.polygon(surface, (40, 40, 60),
                                [(lx, 0), (lx-60, GROUND_Y), (lx+60, GROUND_Y)])

    elif s == 5:  # Dream Land
        surface.fill((210, 180, 255))   # lavender sky
        # pastel gradient band near horizon
        pygame.draw.rect(surface, (255, 210, 240), (0, GROUND_Y - 120, WIDTH, 120))
        # fluffy clouds
        for cx, cy, cr in [(130,80,38),(200,70,28),(160,82,24),
                           (420,55,42),(500,50,30),(455,65,26),
                           (700,90,36),(775,80,26),(730,95,22)]:
            pygame.draw.circle(surface, WHITE, (cx, cy), cr)
        # sparkle stars
        for sx, sy in [(60,30),(250,15),(370,40),(540,22),(660,35),(820,18),(850,60)]:
            pygame.draw.circle(surface, (255, 240, 80), (sx, sy), 3)
            pygame.draw.line(surface, (255, 240, 80), (sx-6, sy), (sx+6, sy), 1)
            pygame.draw.line(surface, (255, 240, 80), (sx, sy-6), (sx, sy+6), 1)
        # cotton-candy ground
        pygame.draw.rect(surface, (255, 182, 220), (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (240, 150, 200), (0, GROUND_Y+22, WIDTH, HEIGHT-GROUND_Y))
        pygame.draw.line(surface, (255, 140, 200), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)


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
        self.active_powerups = {}   # name -> frames remaining
        self.speed_boost  = 1.0
        self.punch_boost  = 0
        self.kick_boost   = 0
        self.shield       = False
        self.leech        = False
        self.color        = char_data["color"]
        self.poison_frames    = 0   # frames of poison remaining
        self.poison_tick      = 0   # frames until next poison damage
        self.contact_cooldown = 0   # frames before can take contact damage again
        self.punch_cooldown   = 0   # 1 second cooldown between punches
        self.kick_cooldown    = 0   # 2 second cooldown between kicks
        self.regen_tick       = 300 if char_data.get("regen") else 0
        self.fire_frames      = 0   # frames of fire remaining
        self.fire_tick        = 0   # frames until next fire damage
        self.freeze_frames    = 0   # frames of freeze remaining

    def apply_powerup(self, spec):
        t    = spec['type']
        name = spec['name']
        if t == 'speed':
            # supports 'mult' (multiplier) or 'amount' (additive delta, e.g. Wither)
            if 'mult' in spec:
                self.speed_boost = spec['mult']
            else:
                self.speed_boost = max(0.1, 1.0 + spec.get('amount', 0) * 0.15)
            self.active_powerups[name] = spec['duration']
        elif t == 'punch_dmg':
            self.punch_boost += spec['amount']
            self.active_powerups[name] = spec['duration']
        elif t == 'kick_dmg':
            self.kick_boost += spec['amount']
            self.active_powerups[name] = spec['duration']
        elif t == 'heal':
            self.hp = max(0, min(self.max_hp, self.hp + spec['amount']))
        elif t == 'shield':
            self.shield = True
            self.active_powerups[name] = spec['duration']
        elif t == 'leech':
            self.leech = True
            self.active_powerups[name] = spec['duration']

    def tick_powerups(self):
        done = [n for n, t in self.active_powerups.items() if t <= 1]
        for name in done:
            spec = next((p for p in POWERUPS if p['name'] == name), None)
            if spec:
                t = spec['type']
                if t == 'speed':     self.speed_boost  = 1.0
                elif t == 'punch_dmg': self.punch_boost = max(0, self.punch_boost - spec['amount'])
                elif t == 'kick_dmg':  self.kick_boost  = max(0, self.kick_boost  - spec['amount'])
                elif t == 'shield':    self.shield = False
                elif t == 'leech':     self.leech  = False
            del self.active_powerups[name]
        for name in list(self.active_powerups):
            self.active_powerups[name] -= 1

    def tick_status(self):
        if self.poison_frames > 0:
            self.poison_frames -= 1
            self.poison_tick   -= 1
            if self.poison_tick <= 0:
                self.hp          = max(0, self.hp - 1)
                self.poison_tick = 180   # 1 dmg every 3 seconds
        if self.contact_cooldown > 0: self.contact_cooldown -= 1
        if self.punch_cooldown   > 0: self.punch_cooldown   -= 1
        if self.kick_cooldown    > 0: self.kick_cooldown    -= 1
        if self.regen_tick > 0:
            self.regen_tick -= 1
            if self.regen_tick == 0:
                self.hp = min(self.max_hp, self.hp + 2)
                self.regen_tick = 300   # reset for next tick
        if self.fire_frames > 0:
            self.fire_frames -= 1
            self.fire_tick   -= 1
            if self.fire_tick <= 0:
                self.hp        = max(0, self.hp - 3)
                self.fire_tick = 480   # 3 dmg every 8 seconds
        if self.freeze_frames > 0:
            self.freeze_frames -= 1

    def update(self, keys, other, platforms=()):
        self.tick_powerups()
        self.tick_status()
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

        prev_y = self.y
        self.vy += GRAVITY
        self.y  += self.vy
        landed = False
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            landed = True
        else:
            for plat in platforms:
                if (self.vy >= 0 and prev_y <= plat.y and self.y >= plat.y
                        and plat.x - 25 <= self.x <= plat.x + plat.w + 25):
                    self.y = plat.y
                    self.vy = 0
                    self.x += plat.vx
                    landed = True
                    break
        if landed:
            self.on_ground = True
            self.jumps_left = 2 if self.char["double_jump"] else 1
        else:
            self.on_ground = False

        self.x = max(50.0, min(float(WIDTH - 50), self.x))
        self.facing = 1 if other.x > self.x else -1

        spd = self.char["speed"] * self.speed_boost

        if self.hurt_timer == 0 and self.freeze_frames == 0:
            ctrl = self.controls
            can_atk = not self.attacking or self.action in ('idle', 'walk', 'jump')

            if can_atk and keys[ctrl['punch']] and self.punch_cooldown == 0:
                self._start('punch', 0.07)
                self.punch_cooldown = FPS        # 1 second
            elif can_atk and keys[ctrl['kick']] and self.kick_cooldown == 0:
                self._start('kick', 0.06)
                self.kick_cooldown = FPS * 2     # 2 seconds
            elif keys[ctrl['jump']]:
                if self.jumps_left > 0:
                    self.vy = self.char["jump"]
                    self.on_ground = False
                    self.jumps_left -= 1
                    self.action = 'jump'
                    self.attacking = False
            elif keys[ctrl['left']]:
                self.x -= spd
                if self.on_ground and not self.attacking:
                    self.action = 'walk'
                    self.walk_t = (self.walk_t + 0.12) % 1.0
                    self.action_t = self.walk_t
            elif keys[ctrl['right']]:
                self.x += spd
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
            if self.action == 'punch':
                dmg = self.char["punch_dmg"] + self.punch_boost
            else:
                dmg = self.char["kick_dmg"] + self.kick_boost
            if other.shield:
                dmg = max(1, int(dmg * 0.5))
            other.hp = max(0, other.hp - dmg)
            if self.leech:
                self.hp = min(self.max_hp, self.hp + 8)
            other.action = 'hurt'
            other.hurt_timer = 22
            other.flash_timer = 10
            other.attacking = False
            other.knockback = self.facing * 6
            self.attack_hit = True
            if other.char["name"] == "Shapeshifter":
                other.color = (random.randint(60,255), random.randint(60,255), random.randint(60,255))
            if self.char.get("fire_punch") and self.action == 'punch':
                if other.fire_frames == 0:
                    other.fire_tick = 480
                other.fire_frames = max(other.fire_frames, 960)  # 16 sec burn
            if self.char.get("freeze_kick") and self.action == 'kick':
                other.freeze_frames = 180  # 3 seconds

    def draw(self, surface):
        pygame.draw.ellipse(surface, (0,0,0),
                            (int(self.x)-25, int(self.y)-6, 50, 12))
        flash = (self.flash_timer % 4) < 2 and self.flash_timer > 0
        result = draw_stickman(surface, self.x, self.y, self.color,
                               self.facing, self.action, self.action_t, flash=flash)
        if self.poison_frames > 0:
            top_y = int(self.y) - LEG_LEN - BODY_LEN - NECK_LEN - HEAD_R * 2 - 14
            for i, dx in enumerate((-10, 0, 10)):
                pulse = (self.poison_frames // 10 + i) % 2 == 0
                col = (60, 240, 80) if pulse else (30, 160, 50)
                pygame.draw.circle(surface, col, (int(self.x) + dx, top_y), 4)
        if self.fire_frames > 0:
            top_y = int(self.y) - LEG_LEN - BODY_LEN - NECK_LEN - HEAD_R * 2 - 26
            for i, dx in enumerate((-10, 0, 10)):
                pulse = (self.fire_frames // 8 + i) % 2 == 0
                col = (255, 140, 0) if pulse else (220, 50, 0)
                pygame.draw.circle(surface, col, (int(self.x) + dx, top_y), 4)
        if self.freeze_frames > 0:
            top_y = int(self.y) - LEG_LEN - BODY_LEN - NECK_LEN - HEAD_R * 2 - 38
            for i, dx in enumerate((-10, 0, 10)):
                pulse = (self.freeze_frames // 6 + i) % 2 == 0
                col = (180, 230, 255) if pulse else (80, 160, 240)
                pygame.draw.circle(surface, col, (int(self.x) + dx, top_y), 4)
        return result


# ---------------------------------------------------------------------------
# AI Fighter
# ---------------------------------------------------------------------------

class AIFighter(Fighter):
    """Fighter driven by a simple state-machine AI instead of keyboard input."""

    SETTINGS = {
        'easy':       dict(decision_delay=38, aggression=0.35, jump_chance=0.005, dodge_chance=0.0),
        'medium':     dict(decision_delay=22, aggression=0.62, jump_chance=0.015, dodge_chance=0.1),
        'hard':       dict(decision_delay=10, aggression=0.88, jump_chance=0.030, dodge_chance=0.3),
        'super_hard':       dict(decision_delay=2,  aggression=0.98, jump_chance=0.060, dodge_chance=0.7),
        'super_super_hard': dict(decision_delay=1,  aggression=1.00, jump_chance=0.100, dodge_chance=0.95),
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

    def update(self, keys, other, platforms=()):
        # --- Physics (same as parent, no key input) ---
        self.tick_powerups()
        self.tick_status()
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

        prev_y = self.y
        self.vy += GRAVITY
        self.y  += self.vy
        landed = False
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            landed = True
        else:
            for plat in platforms:
                if (self.vy >= 0 and prev_y <= plat.y and self.y >= plat.y
                        and plat.x - 25 <= self.x <= plat.x + plat.w + 25):
                    self.y = plat.y
                    self.vy = 0
                    self.x += plat.vx
                    landed = True
                    break
        if landed:
            self.on_ground = True
            self.jumps_left = 2 if self.char["double_jump"] else 1
        else:
            self.on_ground = False

        self.x = max(50.0, min(float(WIDTH - 50), self.x))
        self.facing = 1 if other.x > self.x else -1

        # --- Advance attack animation ---
        if self.attacking and self.action in ('punch', 'kick'):
            self.action_t = min(1.0, self.action_t + self._attack_speed)
            if self.action_t >= 1.0:
                self.action = 'idle'
                self.action_t = 0.0
                self.attacking = False

        if self.hurt_timer > 0 or self.freeze_frames > 0:
            return  # don't make decisions while staggered or frozen

        # --- AI decision tick ---
        self.react_timer -= 1
        if self.react_timer <= 0:
            self.react_timer = self.decision_delay + random.randint(0, 8)
            self._decide(other)

        # --- Execute decision ---
        dist = abs(other.x - self.x)
        can_atk = not self.attacking or self.action in ('idle', 'walk', 'jump')

        if self.ai_attack and can_atk:
            cd = self.punch_cooldown if self.ai_attack == 'punch' else self.kick_cooldown
            if cd == 0:
                self._start(self.ai_attack, 0.07 if self.ai_attack == 'punch' else 0.06)
                if self.ai_attack == 'punch':
                    self.punch_cooldown = FPS
                else:
                    self.kick_cooldown = FPS * 2
            self.ai_attack = None
        elif self.ai_move != 0:
            self.x += self.ai_move * self.char["speed"] * self.speed_boost
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
# Powerup pickup
# ---------------------------------------------------------------------------

PICKUP_RADIUS = 28

class Powerup:
    def __init__(self):
        spec = random.choice(POWERUPS)
        self.spec  = spec
        self.name  = spec['name']
        self.color = spec['color']
        self.x     = float(random.randint(80, WIDTH - 80))
        self.y     = float(GROUND_Y - 14)
        self.age   = 0           # for bobbing animation
        self.picked_up = False

    def update(self):
        self.age += 1

    def draw(self, surface):
        bob = math.sin(self.age * 0.08) * 6
        cx, cy = int(self.x), int(self.y + bob)

        # Glow ring (pulsing)
        glow_r = PICKUP_RADIUS + 4 + int(math.sin(self.age * 0.12) * 3)
        glow_col = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.circle(surface, glow_col, (cx, cy), glow_r, 3)

        # Main circle
        pygame.draw.circle(surface, self.color, (cx, cy), PICKUP_RADIUS)
        pygame.draw.circle(surface, WHITE,      (cx, cy), PICKUP_RADIUS, 2)

        # Label
        lbl = font_tiny.render(self.name[0], True, WHITE)   # first letter
        surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < PICKUP_RADIUS + 22


def draw_active_powerups(surface, fighter, side):
    """Draw small powerup icons above the fighter's health bar area."""
    if not fighter.active_powerups:
        return
    x_start = 20 if side == 'left' else WIDTH - 20
    dx = 44 if side == 'left' else -44
    for i, (name, frames) in enumerate(fighter.active_powerups.items()):
        spec = next((p for p in POWERUPS if p['name'] == name), None)
        if not spec:
            continue
        cx = x_start + dx * i + (22 if side == 'left' else -22)
        cy = 90
        ratio = frames / spec['duration']
        # background
        pygame.draw.circle(surface, (60, 60, 60), (cx, cy), 18)
        # arc showing time left
        if ratio > 0:
            pygame.draw.arc(surface, spec['color'],
                            (cx-18, cy-18, 36, 36),
                            math.pi/2 - ratio*2*math.pi, math.pi/2, 4)
        pygame.draw.circle(surface, WHITE, (cx, cy), 18, 2)
        lbl = font_tiny.render(name[0], True, WHITE)
        surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))


# ---------------------------------------------------------------------------
# Platform
# ---------------------------------------------------------------------------

class Platform:
    H = 16

    def __init__(self, x, y, w, vx=0, move_range=0):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.vx = float(vx)
        self.move_range = move_range
        self.start_x = float(x)

    def update(self):
        if self.vx:
            self.x += self.vx
            if abs(self.x - self.start_x) >= self.move_range:
                self.vx = -self.vx

    def draw(self, surface, stage_idx):
        styles = [
            ((139, 90, 43),  (80,  50, 15)),   # Grasslands: wood
            ((70,  45, 35),  (200, 80,  0)),   # Volcano: rock + lava edge
            ((90,  60, 25),  (150, 30, 30)),   # Dojo: wood + red trim
            ((190, 160, 90), (140, 110, 50)),  # Desert: sandstone
            ((60,  60, 100), (120, 120, 220)), # Arena: stone + blue glow
        ]
        fill, border = styles[stage_idx % len(styles)]
        rx, ry = int(self.x), int(self.y)
        pygame.draw.rect(surface, fill,   (rx, ry, self.w, self.H), border_radius=4)
        pygame.draw.rect(surface, border, (rx, ry, self.w, self.H), 2, border_radius=4)
        if self.vx:  # moving platform: dashed top stripe
            for dx in range(4, self.w - 4, 12):
                pygame.draw.rect(surface, WHITE, (rx + dx, ry + 2, 6, 3))


class Spring:
    W        = 22
    H_IDLE   = 22
    H_COMP   = 8
    COOLDOWN = 28

    def __init__(self, x, bounce_vy=-22):
        self.x         = float(x)
        self.bounce_vy = bounce_vy
        self.anim      = 0   # counts down after trigger; > 12 = compressed
        self.cooldown  = 0

    def update(self):
        if self.anim     > 0: self.anim     -= 1
        if self.cooldown > 0: self.cooldown -= 1

    def trigger(self, fighter):
        if self.cooldown > 0:
            return
        if fighter.on_ground and abs(fighter.x - self.x) < self.W + 14:
            fighter.vy        = self.bounce_vy
            fighter.on_ground = False
            fighter.jumps_left = 2 if fighter.char["double_jump"] else 1
            fighter.action    = 'jump'
            fighter.attacking = False
            self.anim     = 25
            self.cooldown = self.COOLDOWN

    def draw(self, surface):
        compressed = self.anim > 12
        h  = self.H_COMP if compressed else self.H_IDLE
        cx = int(self.x)
        by = GROUND_Y   # base sits on ground line

        col  = (255, 240, 0) if self.anim > 0 else (180, 200, 40)
        dark = (120, 140, 20)

        # base plate
        pygame.draw.rect(surface, (110, 110, 110), (cx - 14, by - 5, 28, 6), border_radius=2)

        # coil: zigzag lines
        segs = 4
        for i in range(segs):
            y1 = by - 5 - int((i / segs) * h)
            y2 = by - 5 - int(((i + 1) / segs) * h)
            x1 = cx - 9 if i % 2 == 0 else cx + 9
            x2 = cx + 9 if i % 2 == 0 else cx - 9
            pygame.draw.line(surface, dark, (x1, y1), (x2, y2), 4)
            pygame.draw.line(surface, col,  (x1, y1), (x2, y2), 2)

        # top pad
        top_y = by - 5 - h
        pygame.draw.rect(surface, (220, 220, 220), (cx - 12, top_y - 5, 24, 6), border_radius=3)
        pygame.draw.rect(surface, WHITE,            (cx - 12, top_y - 5, 24, 6), 1, border_radius=3)


# ---------------------------------------------------------------------------
# Stage select screen
# ---------------------------------------------------------------------------

def stage_select():
    idx = 0
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT,  pygame.K_a): idx = (idx - 1) % len(STAGES)
                if event.key in (pygame.K_RIGHT, pygame.K_d): idx = (idx + 1) % len(STAGES)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE): return idx

        draw_bg(screen, idx)
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 120))
        screen.blit(ov, (0, 0))

        title = font_large.render("SELECT STAGE", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        nm = font_medium.render(STAGES[idx]["name"], True, WHITE)
        screen.blit(nm, (WIDTH//2 - nm.get_width()//2, HEIGHT//2 - 30))

        match = STAGE_MATCHUPS.get(STAGES[idx]["name"], {})
        if match:
            adv_s = font_small.render(f"★ ADV: {match['adv']}", True, (100, 255, 100))
            dis_s = font_small.render(f"✗ DIS: {match['dis']}", True, (255, 100, 100))
            screen.blit(adv_s, (WIDTH//2 - adv_s.get_width() - 12, HEIGHT//2 + 12))
            screen.blit(dis_s, (WIDTH//2 + 12, HEIGHT//2 + 12))

        for di in range(len(STAGES)):
            col = WHITE if di == idx else GRAY
            pygame.draw.circle(screen, col, (WIDTH//2 + (di - len(STAGES)//2)*30, HEIGHT//2 + 40), 6)

        hint = font_small.render("◄ ► to browse   ENTER to confirm", True, (180, 180, 180))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))
        pygame.display.flip()


# ---------------------------------------------------------------------------
# Mode select screen
# ---------------------------------------------------------------------------

def mode_select():
    """Returns ('1p', difficulty) or '2p'."""
    selected = 0   # 0 = 1P, 1 = 2P
    difficulty_idx = 1   # 0=easy, 1=medium, 2=hard, 3=super_hard, 4=super_super_hard
    difficulties = ['easy', 'medium', 'hard', 'super_hard', 'super_super_hard']
    diff_colors  = [GREEN, YELLOW, RED, PURPLE, CYAN]
    scroll_offset = 0   # index of first visible difficulty in the scrollable list
    VISIBLE = 3         # how many difficulties show at once
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
                        difficulty_idx = (difficulty_idx - 1) % len(difficulties)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        difficulty_idx = (difficulty_idx + 1) % len(difficulties)
                    # keep selection inside the visible window
                    if difficulty_idx < scroll_offset:
                        scroll_offset = difficulty_idx
                    elif difficulty_idx >= scroll_offset + VISIBLE:
                        scroll_offset = difficulty_idx - VISIBLE + 1
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

            list_x = WIDTH//2 - 230
            list_y = 428
            row_h  = 30

            # scroll-up arrow
            if scroll_offset > 0:
                up = font_small.render("▲", True, GRAY)
                screen.blit(up, (list_x, list_y - 22))

            # visible rows
            for row, di in enumerate(range(scroll_offset, scroll_offset + VISIBLE)):
                if di >= len(difficulties):
                    break
                dname, dcol = difficulties[di], diff_colors[di]
                marker = "► " if di == difficulty_idx else "  "
                dt = font_small.render(f"{marker}{dname.replace('_', ' ').capitalize()}", True,
                                       dcol if di == difficulty_idx else GRAY)
                screen.blit(dt, (list_x, list_y + row * row_h))

            # scroll-down arrow
            if scroll_offset + VISIBLE < len(difficulties):
                dn = font_small.render("▼", True, GRAY)
                screen.blit(dn, (list_x, list_y + VISIBLE * row_h + 2))

            hint = font_tiny.render("↑/↓ or W/S to scroll", True, GRAY)
            screen.blit(hint, (WIDTH//2 - 240, list_y + VISIBLE * row_h + 22))

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

def run_fight(p1_idx, p2_idx, vs_ai=False, ai_difficulty='medium', stage_idx=0):
    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l)

    p1 = Fighter(200, CHARACTERS[p1_idx],  1, P1_CTRL)
    if vs_ai:
        p2 = AIFighter(700, CHARACTERS[p2_idx], -1, ai_difficulty)
    else:
        p2 = Fighter(700, CHARACTERS[p2_idx], -1, P2_CTRL)

    stage_data = STAGES[stage_idx % len(STAGES)]
    platforms  = [Platform(*p) for p in stage_data["platforms"]]
    springs    = [Spring(*s)   for s in stage_data["springs"]]

    # Apply stage advantage / disadvantage stat modifiers
    matchup = STAGE_MATCHUPS.get(stage_data["name"], {})
    for f in (p1, p2):
        if f.char["name"] == matchup.get("adv"):
            f.speed_boost *= 1.25
            f.punch_boost += f.char["punch_dmg"] // 4
            f.kick_boost  += f.char["kick_dmg"]  // 4
        elif f.char["name"] == matchup.get("dis"):
            f.speed_boost *= 0.8
            f.punch_boost -= f.char["punch_dmg"] // 5
            f.kick_boost  -= f.char["kick_dmg"]  // 5

    def _stage_tag(fighter):
        name = fighter.char["name"]
        if name == matchup.get("adv"): return ("★ ADVANTAGE", (100, 255, 100))
        if name == matchup.get("dis"): return ("✗ DISADVANTAGE", (255, 100, 100))
        return (None, None)

    p1_stag, p1_stag_col = _stage_tag(p1)
    p2_stag, p2_stag_col = _stage_tag(p2)
    announce_timer = 180   # 3 seconds

    game_over    = False
    winner       = None
    timer        = 90 * FPS
    powerups     = []
    clones       = []   # list of {'fighter': AIFighter, 'timer': int, 'target': Fighter}
    spawn_timer  = 300   # first spawn after 5 seconds

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
            for plat in platforms:
                plat.update()
            for sp in springs:
                sp.update()
                sp.trigger(p1)
                sp.trigger(p2)
                for cd in clones:
                    sp.trigger(cd['fighter'])

            # Update clones
            new_clones = []
            for cd in clones:
                cd['timer'] -= 1
                if cd['timer'] > 0 and cd['fighter'].hp > 0:
                    cd['fighter'].update(None, cd['target'], platforms)
                    new_clones.append(cd)
            clones = new_clones

            # Cactus contact damage + poison
            for cactus, victim in [(p1, p2), (p2, p1)]:
                if (cactus.char.get("contact_dmg") and
                        victim.contact_cooldown == 0 and
                        abs(cactus.x - victim.x) < 55):
                    victim.hp = max(0, victim.hp - cactus.char["contact_dmg"])
                    victim.contact_cooldown = 60
                    victim.flash_timer = 8
                    if victim.poison_frames == 0:
                        victim.poison_tick = 180
                    victim.poison_frames = max(victim.poison_frames, 600)  # 10 sec

            keys = pygame.key.get_pressed()
            p1.update(keys, p2, platforms)
            p2.update(keys, p1, platforms)
            timer -= 1
            if timer <= 0 or p1.hp <= 0 or p2.hp <= 0:
                game_over = True
                winner = p1 if p1.hp >= p2.hp else p2

            # Spawn powerups
            spawn_timer -= 1
            if spawn_timer <= 0 and len(powerups) < 3:
                powerups.append(Powerup())
                spawn_timer = random.randint(480, 720)   # 8-12 seconds

            # Update & pickup
            for pu in powerups:
                pu.update()
                for fighter, foe in [(p1, p2), (p2, p1)]:
                    if not pu.picked_up and pu.collides(fighter):
                        if pu.spec['type'] == 'clone':
                            cf = AIFighter(fighter.x + 60 * fighter.facing,
                                           fighter.char, fighter.facing, 'hard')
                            cf.hp    = 80
                            cf.color = fighter.color
                            clones.append({'fighter': cf, 'timer': 30 * FPS, 'target': foe})
                        else:
                            fighter.apply_powerup(pu.spec)
                        pu.picked_up = True
                        break
            powerups = [pu for pu in powerups if not pu.picked_up]

        draw_bg(screen, stage_idx)
        for plat in platforms:
            plat.draw(screen, stage_idx)
        for sp in springs:
            sp.draw(screen)
        for pu in powerups:
            pu.draw(screen)
        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen)
        clone_draws = [(cd, cd['fighter'].draw(screen)) for cd in clones]

        if not game_over:
            if p1.attacking and not p1.attack_hit:
                p1.check_hit(p1_hit, p2)
            if p2.attacking and not p2.attack_hit:
                p2.check_hit(p2_hit, p1)
            for cd, cf_hit in clone_draws:
                cf = cd['fighter']
                # clone attacks its target
                if cf.attacking and not cf.attack_hit:
                    cf.check_hit(cf_hit, cd['target'])
                # opponent can hit the clone
                if cd['target'] is p2:
                    if p2.attacking and not p2.attack_hit:
                        p2.check_hit(p2_hit, cf)
                else:
                    if p1.attacking and not p1.attack_hit:
                        p1.check_hit(p1_hit, cf)
            # draw clone timer above each clone
            for cd in clones:
                cf = cd['fighter']
                secs = cd['timer'] // FPS
                tag = font_tiny.render(f"2x [{secs}s]", True, (255, 80, 200))
                screen.blit(tag, (int(cf.x) - tag.get_width()//2,
                                  int(cf.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        # Draw AI tag above CPU fighter
        if vs_ai:
            diff_col = {
                'easy': GREEN, 'medium': YELLOW, 'hard': RED,
                'super_hard': PURPLE, 'super_super_hard': CYAN
            }[ai_difficulty]
            cpu_tag = font_tiny.render(f"CPU [{ai_difficulty.upper()}]", True, diff_col)
            screen.blit(cpu_tag, (int(p2.x) - cpu_tag.get_width()//2,
                                  int(p2.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        p2_label = f"CPU — {p2.char['name']}" if vs_ai else f"P2 — {p2.char['name']}"
        draw_health_bars_labeled(screen, p1, p2, p2_label)
        draw_active_powerups(screen, p1, 'left')
        draw_active_powerups(screen, p2, 'right')

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

        # Stage advantage / disadvantage announcement (first 3 seconds)
        if announce_timer > 0 and not game_over:
            announce_timer -= 1
            if p1_stag:
                s = font_small.render(p1_stag, True, p1_stag_col)
                screen.blit(s, (10, 80))
            if p2_stag:
                s = font_small.render(p2_stag, True, p2_stag_col)
                screen.blit(s, (WIDTH - s.get_width() - 10, 80))

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

        s_idx = stage_select()

        while True:
            result = run_fight(p1_idx, p2_idx, vs_ai=vs_ai, ai_difficulty=difficulty, stage_idx=s_idx)
            if result == 'rematch':
                continue
            break   # 'select' — go back to mode select

if __name__ == "__main__":
    main()
