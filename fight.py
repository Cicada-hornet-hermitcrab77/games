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
     "punch_dmg": 12, "kick_dmg": 18, "max_hp": 130, "block": 6,
     "desc": "Tanky heavy hitter",   "double_jump": False},
    {"name": "Ninja",   "color": CYAN,   "speed": 7, "jump": -16,
     "punch_dmg":  7, "kick_dmg": 10, "max_hp":  90, "block": 8,
     "desc": "Fast & double jump",   "double_jump": True},
    {"name": "Boxer",   "color": GREEN,  "speed": 5, "jump": -13,
     "punch_dmg": 16, "kick_dmg":  8, "max_hp": 110, "block": 9,
     "desc": "Devastating punches",  "double_jump": False},
    {"name": "Phantom", "color": PURPLE, "speed": 6, "jump": -15,
     "punch_dmg": 10, "kick_dmg": 14, "max_hp": 100, "block": 7,
     "desc": "Balanced & evasive",   "double_jump": True},
    {"name": "Ares",    "color": ORANGE, "speed": 5,  "jump": -14,
     "punch_dmg": 21, "kick_dmg": 20, "max_hp": 90, "block": 3,
     "desc": "God of War",           "double_jump": False},
    {"name": "Zephyr",  "color": BLUE,  "speed": 9,  "jump": -18,
     "punch_dmg": 10, "kick_dmg": 14, "max_hp": 100, "block": 7,
     "desc": "Swift and agile",      "double_jump": True},
    {"name": "Titan",  "color": YELLOW,  "speed": 3,  "jump": -7,
     "punch_dmg": 18, "kick_dmg": 16, "max_hp": 155, "block": 3,
     "desc": "Enormous Health",      "double_jump": False},
    {"name": "Dancing Man",    "color": (100, 100, 255), "speed": 10,  "jump": -20,
     "punch_dmg": 10, "kick_dmg": 10, "max_hp": 100, "block": 6,
     "desc": "evasive",    "double_jump": True},
    {"name": "Tank",   "color": (30, 30, 30), "speed": 1,  "jump": -0,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 190, "block": 9,
     "desc": "Defensive",   "double_jump": False},
    {"name": "Mighty Medieval Man",  "color": GRAY, "speed": 4,  "jump": -18,
     "punch_dmg": 15, "kick_dmg": 15, "max_hp": 120, "block": 8,
     "desc": "Lord of chivalry",   "double_jump": False},
    {"name": "Samurai",   "color": BLACK, "speed": 6,  "jump": -15,
     "punch_dmg": 12, "kick_dmg": 19, "max_hp": 170, "block": 7,
     "desc": "Katana Master",   "double_jump": True},
    {"name": "Skeleton",   "color": WHITE,   "speed": 3, "jump": -5,
     "punch_dmg":  25, "kick_dmg": 20, "max_hp":  65, "block": 2,
     "desc": "Dead",   "double_jump": False},
    {"name": "Unknown",   "color": (100, 160, 220),   "speed": 5,  "jump": -5,
     "punch_dmg":  3, "kick_dmg": 5, "max_hp":  300, "block": 5,
     "desc": "Mysterious and powerful",   "double_jump": True},
    {"name": "Hardy", "color": (110, 120, 225), "speed": 3, "jump": -5,
     "punch_dmg": 3, "kick_dmg": 4, "max_hp": 65, "block": 2,
     "desc": "Pros should try him",   "double_jump": False},
    {"name": "Rogue", "color": (220, 180, 60), "speed": 8, "jump": -17,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 80, "block": 6,
     "desc": "Stealthy and agile",   "double_jump": True},
    {"name": "Gladiator", "color": (200, 80, 80), "speed": 4, "jump": -12,
     "punch_dmg": 14, "kick_dmg": 18, "max_hp": 140, "block": 7,
     "desc": "Arena Champion",   "double_jump": False},
    {"name": "Oni", "color": (80, 220, 200), "speed": 2, "jump": -1,
     "punch_dmg": 12, "kick_dmg": 14, "max_hp": 200, "block": 3,
     "desc": "Fat Demon",   "double_jump": False},
    {"name": "Cecalia",     "color": (50, 255, 255), "speed": 8,  "jump": -8,
     "punch_dmg": 8,  "kick_dmg": 8,  "max_hp": 300, "block": 4,
     "desc": "Octo hard",        "double_jump": False},
    {"name": "Acrobat",     "color": (255, 180, 80), "speed": 8,  "jump": -20,
     "punch_dmg": 8,  "kick_dmg": 12, "max_hp": 85, "block": 6,
     "desc": "Aerial specialist", "double_jump": True},
    {"name": "Shapeshifter", "color": (180, 80, 255), "speed": 6, "jump": -15,
     "punch_dmg": 14, "kick_dmg": 14, "max_hp": 105, "block": 5,
     "desc": "Unpredictable",    "double_jump": True},
    {"name": "Spring",   "color": (255, 100, 100), "speed": 10, "jump": -45,
     "punch_dmg": 1, "kick_dmg": 1, "max_hp": 400, "block": 1,
     "desc": "Bouncy",   "double_jump": True},
    {"name": "Harpy",   "color": (150, 0, 150), "speed": 9, "jump": -19,
     "punch_dmg": 20, "kick_dmg": 20, "max_hp": 40, "block": 3,
     "desc": "Blood-eater",   "double_jump": True},
    {"name": "Scarecrow",   "color": (50, 0, 50), "speed": 1, "jump": -0,
     "punch_dmg": 100, "kick_dmg": 100, "max_hp": 60, "block": 1,
     "desc": "Strong and Weak",   "double_jump": False},
    {"name": "Cactus", "color": (40, 180, 60), "speed": 4, "jump": -11,
     "punch_dmg": 4, "kick_dmg": 4, "max_hp": 135, "block": 4,
     "desc": "Poisons on contact", "double_jump": False, "contact_dmg": 8},
    {"name": "Medic", "color": (200, 255, 200), "speed": 5, "jump": -13,
     "punch_dmg": 7, "kick_dmg": 9, "max_hp": 120, "block": 6,
     "desc": "+2 HP every 5 seconds", "double_jump": False, "regen": True},
    {"name": "Arsonist", "color": (255, 80, 20), "speed": 6, "jump": -14,
     "punch_dmg": 10, "kick_dmg": 8, "max_hp": 100, "block": 4,
     "desc": "Punches set targets on fire", "double_jump": False, "fire_punch": True},
    {"name": "Cryogenisist", "color": (150, 220, 255), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 0, "max_hp": 110, "block": 6,
     "desc": "Kicks freeze opponents for 3s", "double_jump": False, "freeze_kick": True},
    {"name": "Magician", "color": (180, 80, 255), "speed": 5, "jump": -13,
     "punch_dmg": 8, "kick_dmg": 10, "max_hp": 105, "block": 7,
     "desc": "Powerups drift toward him", "double_jump": True, "magnet": True},
    {"name": "Charger", "color": (255, 220, 0), "speed": 5, "jump": -13,
     "punch_dmg": 7, "kick_dmg": 9, "max_hp": 115, "block": 5,
     "desc": "Punches shock: halves speed for 8 sec", "double_jump": False, "shock_punch": True},
    {"name": "Psychopath", "color": (180, 0, 180), "speed": 6, "jump": -14,
     "punch_dmg": 9, "kick_dmg": 10, "max_hp": 100, "block": 2,
     "desc": "Kick teleports to random spot", "double_jump": False, "teleport_kick": True},
    {"name": "Ran-Doom", "color": (128, 128, 128), "speed": 5, "jump": -13,
     "punch_dmg": 10, "kick_dmg": 10, "max_hp": 110, "block": 5,
     "desc": "All stats randomized each match", "double_jump": False, "random_stats": True},
    {"name": "Outbacker", "color": (200, 130, 50), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 7, "max_hp": 115, "block": 5,
     "desc": "Kick throws orbiting boomerang", "double_jump": False, "boomerang_kick": True},
    {"name": "Gunner", "color": (60, 180, 80), "speed": 5, "jump": -13,
     "punch_dmg": 8, "kick_dmg": 0, "max_hp": 110, "block": 4,
     "desc": "Kicks shoot a ball (10 dmg)", "double_jump": False, "shoot_kick": True},
    {"name": "Bazooka Man", "color": (180, 60, 60), "speed": 1, "jump": -0,
     "punch_dmg": 8, "kick_dmg": 0, "max_hp": 75, "block": 1,
     "desc": "Kick fires exploding orb (35 dmg)", "double_jump": False, "bazooka_kick": True},
    {"name": "Pinball", "color": (255, 80, 200), "speed": 5, "jump": -13,
     "punch_dmg": 8, "kick_dmg": 0, "max_hp": 110, "block": 5,
     "desc": "Kick shoots a bouncing ball (10 dmg)", "double_jump": False, "bounce_kick": True},
    {"name": "Giant", "color": (100, 160, 100), "speed": 2, "jump": -8,
     "punch_dmg": 20, "kick_dmg": 18, "max_hp": 260, "block": 4,
     "desc": "Very big and very strong", "double_jump": False, "giant": True},
    {"name": "Morph", "color": (80, 200, 220), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 10, "max_hp": 110, "block": 5,
     "desc": "Kick cycles size: normal → big → small", "double_jump": False, "size_kick": True},
    {"name": "Ghost", "color": (210, 210, 255), "speed": 5, "jump": -15,
     "punch_dmg": 8, "kick_dmg": 9, "max_hp": 105, "block": 8,
     "desc": "Phases through platforms", "double_jump": True, "phase": True},
    {"name": "Vampire", "color": (120, 0, 40), "speed": 6, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 10, "max_hp": 90, "block": 5,
     "desc": "Heals 8 HP on every hit", "double_jump": False, "vampire": True},
    {"name": "Astronaut", "color": (220, 230, 255), "speed": 5, "jump": -10,
     "punch_dmg": 8, "kick_dmg": 9, "max_hp": 105, "block": 5,
     "desc": "Anti-gravity on every map", "double_jump": True, "anti_gravity": True},
    {"name": "Spooderman", "color": (180, 20, 20), "speed": 7, "jump": -16,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 100, "block": 7,
     "desc": "Clings to walls, wall-jumps", "double_jump": True, "wall_cling": True},
    {"name": "Hooker", "color": (40, 160, 60), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 0, "max_hp": 110, "block": 5,
     "desc": "Kick fires a snake grappling hook", "double_jump": False, "grapple_kick": True},
    {"name": "Mouse", "color": (200, 180, 160), "speed": 9, "jump": -17,
     "punch_dmg": 6, "kick_dmg": 8, "max_hp": 65, "block": 8,
     "desc": "Tiny and very hard to hit", "double_jump": True, "tiny": True},
    {"name": "Sumo", "color": (255, 200, 100), "speed": 1, "jump": -2,
     "punch_dmg": 1, "kick_dmg": 1, "max_hp": 600, "block": 10,
     "desc": "Enormous health, barely moves", "double_jump": False},
    {"name": "Headless Horseman", "color": (80, 40, 15), "speed": 7, "jump": -11,
     "punch_dmg": 13, "kick_dmg": 0, "max_hp": 145, "block": 5,
     "desc": "Kicks throw a physics pumpkin that explodes", "double_jump": False, "pumpkin_kick": True},
    {"name": "Ink Brush", "color": (20, 20, 40), "speed": 6, "jump": -14,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 110, "block": 6,
     "desc": "Kick spawns a moving clone that distracts enemies", "double_jump": True, "ink_kick": True},
    {"name": "Pencil", "color": (245, 220, 50), "speed": 6, "jump": -14,
     "punch_dmg": 9, "kick_dmg": 11, "max_hp": 105, "block": 5,
     "desc": "Kick draws a temporary platform", "double_jump": True, "pencil_kick": True},
    {"name": "Eraser", "color": (240, 160, 150), "speed": 5, "jump": -13,
     "punch_dmg": 11, "kick_dmg": 13, "max_hp": 115, "block": 6,
     "desc": "Kick erases nearby platforms", "double_jump": False, "eraser_kick": True},
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
    {'name': 'Cleanse',     'type': 'cleanse',   'duration': 0,                  'color': (205, 205, 155)},
]


HEAD_R   = 18
BODY_LEN = 50
ARM_LEN  = 38
LEG_LEN  = 45
NECK_LEN = 5


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_costume(surface, char_name, head_c, hd, shoulder, waist, lh, rh, facing, s, col):
    """Draw character-specific hat / mask / weapon on top of the base stickman."""
    hx, hy = int(head_c[0]), int(head_c[1])
    sx, sy = int(shoulder[0]), int(shoulder[1])
    wx, wy = int(waist[0]), int(waist[1])
    lhx, lhy = int(lh[0]), int(lh[1])
    rhx, rhy = int(rh[0]), int(rh[1])

    def ln(p1, p2, w=2):
        pygame.draw.line(surface, col, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), max(1, int(w * s)))

    if char_name == "Brawler":
        # Red headband across forehead
        band_y = hy + int(hd * 0.2)
        pygame.draw.line(surface, (210, 0, 0), (hx - hd, band_y), (hx + hd, band_y), max(2, int(4*s)))

    elif char_name == "Ninja":
        # Dark mask over lower face + white headband
        mask_y = hy + int(hd * 0.05)
        pygame.draw.rect(surface, (25, 25, 25), (hx - hd + 3, mask_y, hd*2 - 6, int(hd * 0.85)))
        band_y = hy - int(hd * 0.25)
        pygame.draw.line(surface, WHITE, (hx - hd, band_y), (hx + hd, band_y), max(2, int(3*s)))

    elif char_name == "Boxer":
        # Big boxing gloves at both hands
        for gx, gy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (0, 180, 0), (gx, gy), max(5, int(9*s)))
            pygame.draw.circle(surface, (0, 120, 0), (gx, gy), max(5, int(9*s)), 2)

    elif char_name == "Phantom":
        # Purple eye-mask over upper face
        pygame.draw.ellipse(surface, (90, 0, 180), (hx - hd + 2, hy - hd + 2, hd*2 - 4, int(hd * 0.9)))
        pygame.draw.ellipse(surface, (160, 60, 255), (hx - hd + 2, hy - hd + 2, hd*2 - 4, int(hd * 0.9)), 2)

    elif char_name == "Ares":
        # Greek war helmet + red horsehair crest
        pts = [(hx - hd, hy), (hx - int(hd*.8), hy - int(hd*1.3)),
               (hx, hy - int(hd*1.6)), (hx + int(hd*.8), hy - int(hd*1.3)),
               (hx + hd, hy)]
        pygame.draw.polygon(surface, (190, 95, 0), pts)
        pygame.draw.polygon(surface, (255, 140, 0), pts, 2)
        pygame.draw.line(surface, RED, (hx, hy - int(hd*1.6)), (hx, hy - int(hd*2.3)), max(2, int(4*s)))

    elif char_name == "Zephyr":
        # Goggles
        gy = hy - int(hd * 0.1)
        for gx_off in [-int(hd*.38), int(hd*.38)]:
            pygame.draw.circle(surface, (0, 70, 180), (hx + gx_off, gy), int(hd*.33))
            pygame.draw.circle(surface, CYAN, (hx + gx_off, gy), int(hd*.33), 2)
        pygame.draw.line(surface, (80, 140, 255), (hx - int(hd*.72), gy), (hx + int(hd*.72), gy), 2)

    elif char_name == "Titan":
        # Gold crown
        cb = hy - hd
        ct = hy - int(hd * 1.8)
        pygame.draw.polygon(surface, YELLOW, [
            (hx - hd, cb), (hx - hd, ct + int(hd*.5)),
            (hx - int(hd*.5), ct + int(hd*.8)), (hx, ct),
            (hx + int(hd*.5), ct + int(hd*.8)), (hx + hd, ct + int(hd*.5)),
            (hx + hd, cb)])
        pygame.draw.polygon(surface, (200, 155, 0), [
            (hx - hd, cb), (hx - hd, ct + int(hd*.5)),
            (hx - int(hd*.5), ct + int(hd*.8)), (hx, ct),
            (hx + int(hd*.5), ct + int(hd*.8)), (hx + hd, ct + int(hd*.5)),
            (hx + hd, cb)], 2)

    elif char_name == "Dancing Man":
        # Top hat
        brim_y = hy - hd
        hw = int(hd * 1.5)
        hh = int(hd * 1.2)
        pygame.draw.rect(surface, (20, 20, 20), (hx - int(hw*.6), brim_y - hh, int(hw*1.2), hh))
        pygame.draw.line(surface, (20, 20, 20), (hx - hw, brim_y), (hx + hw, brim_y), max(3, int(5*s)))
        pygame.draw.rect(surface, (60, 60, 60), (hx - int(hw*.6), brim_y - hh, int(hw*1.2), hh), 2)

    elif char_name == "Tank":
        # Military helmet dome over head
        pygame.draw.circle(surface, (35, 75, 35), (hx, hy), int(hd * 1.28))
        pygame.draw.circle(surface, (20, 50, 20), (hx, hy), int(hd * 1.28), 2)
        pygame.draw.line(surface, (15, 40, 15), (hx - int(hd*.7), hy + int(hd*.1)), (hx + int(hd*.7), hy + int(hd*.1)), max(2, int(3*s)))

    elif char_name == "Mighty Medieval Man":
        # Knight helmet with visor slit
        pygame.draw.rect(surface, GRAY, (hx - hd, hy - int(hd*1.25), hd*2, int(hd*2.3)), border_radius=3)
        pygame.draw.rect(surface, (40, 40, 40), (hx - int(hd*.6), hy - int(hd*.1), int(hd*1.2), int(hd*.28)))
        pygame.draw.rect(surface, (90, 90, 90), (hx - hd, hy - int(hd*1.25), hd*2, int(hd*2.3)), 2, border_radius=3)
        # Sword in forward hand (blade up, crossguard at hand)
        sword_tip = (rhx + facing * int(6*s), rhy - int(58*s))
        pygame.draw.line(surface, (185, 185, 200), (rhx, rhy), sword_tip, max(2, int(3*s)))
        pygame.draw.line(surface, (115, 78, 28), (rhx, rhy), (rhx - facing*int(5*s), rhy + int(13*s)), max(3, int(5*s)))
        pygame.draw.line(surface, (155, 125, 48), (rhx - int(10*s), rhy - int(4*s)), (rhx + int(10*s), rhy - int(4*s)), max(2, int(3*s)))
        # Kite shield in back hand
        sh_pts = [
            (lhx - facing*int(5*s),  lhy - int(24*s)),
            (lhx - facing*int(22*s), lhy - int(8*s)),
            (lhx - facing*int(22*s), lhy + int(14*s)),
            (lhx - facing*int(8*s),  lhy + int(26*s)),
            (lhx + facing*int(4*s),  lhy + int(14*s)),
            (lhx + facing*int(4*s),  lhy - int(8*s)),
        ]
        pygame.draw.polygon(surface, (85, 88, 98), sh_pts)
        pygame.draw.polygon(surface, (175, 178, 192), sh_pts, 2)
        sh_cx = lhx - facing*int(9*s)
        pygame.draw.line(surface, RED, (sh_cx, lhy - int(20*s)), (sh_cx, lhy + int(20*s)), max(2, int(3*s)))
        pygame.draw.line(surface, RED, (lhx - facing*int(20*s), lhy + int(2*s)), (lhx + facing*int(2*s), lhy + int(2*s)), max(2, int(3*s)))

    elif char_name == "Samurai":
        # Kabuto helmet
        pts = [(hx - int(hd*1.1), hy), (hx - int(hd*1.1), hy - int(hd*.8)),
               (hx - int(hd*.7), hy - int(hd*1.65)), (hx, hy - int(hd*1.85)),
               (hx + int(hd*.7), hy - int(hd*1.65)), (hx + int(hd*1.1), hy - int(hd*.8)),
               (hx + int(hd*1.1), hy)]
        pygame.draw.polygon(surface, (28, 28, 28), pts)
        pygame.draw.polygon(surface, (80, 80, 80), pts, 2)
        pygame.draw.ellipse(surface, BLACK, (hx - int(hd*.7), hy - int(hd*.95), int(hd*1.4), int(hd*1.1)))
        # Katana
        k_end = (lhx - facing * int(48*s), lhy - int(28*s))
        pygame.draw.line(surface, (200, 200, 210), (lhx, lhy), k_end, max(2, int(3*s)))
        pygame.draw.line(surface, (100, 65, 20), (lhx, lhy), (lhx + facing*int(10*s), lhy + int(5*s)), max(3, int(5*s)))

    elif char_name == "Skeleton":
        # Dark eye sockets + teeth
        ey = hy - int(hd * .2)
        for ex_off in [-int(hd*.4), int(hd*.4)]:
            pygame.draw.circle(surface, BLACK, (hx + ex_off, ey), int(hd*.28))
        ty = hy + int(hd * .48)
        for i in range(-2, 3):
            tx = hx + i * int(hd * .26)
            pygame.draw.line(surface, BLACK, (tx, ty - int(hd*.1)), (tx, ty + int(hd*.22)), max(2, int(3*s)))

    elif char_name == "Unknown":
        # Dark hood
        pygame.draw.polygon(surface, (25, 50, 90), [
            (hx - int(hd*1.35), hy + int(hd*.25)), (hx - int(hd*1.1), hy - int(hd*1.55)),
            (hx, hy - int(hd*2.1)), (hx + int(hd*1.1), hy - int(hd*1.55)),
            (hx + int(hd*1.35), hy + int(hd*.25))])
        pygame.draw.ellipse(surface, (10, 18, 45), (hx - int(hd*.75), hy - int(hd*.55), int(hd*1.5), int(hd*1.2)))
        pygame.draw.polygon(surface, (55, 90, 160), [
            (hx - int(hd*1.35), hy + int(hd*.25)), (hx - int(hd*1.1), hy - int(hd*1.55)),
            (hx, hy - int(hd*2.1)), (hx + int(hd*1.1), hy - int(hd*1.55)),
            (hx + int(hd*1.35), hy + int(hd*.25))], 2)

    elif char_name == "Hardy":
        # Yellow hard hat
        pygame.draw.ellipse(surface, (220, 200, 0), (hx - hd, hy - int(hd*1.85), hd*2, int(hd*1.4)))
        pygame.draw.line(surface, (180, 160, 0), (hx - int(hd*1.35), hy - int(hd*.5)), (hx + int(hd*1.35), hy - int(hd*.5)), max(3, int(5*s)))

    elif char_name == "Rogue":
        # Tan hood
        pygame.draw.polygon(surface, (145, 115, 28), [
            (hx - int(hd*1.25), hy + int(hd*.3)), (hx, hy - int(hd*2.05)),
            (hx + int(hd*1.25), hy + int(hd*.3))])
        pygame.draw.polygon(surface, (200, 160, 50), [
            (hx - int(hd*1.25), hy + int(hd*.3)), (hx, hy - int(hd*2.05)),
            (hx + int(hd*1.25), hy + int(hd*.3))], 2)
        for ex_off in [-int(hd*.3), int(hd*.3)]:
            pygame.draw.circle(surface, (70, 55, 10), (hx + ex_off, hy), int(hd*.15))

    elif char_name == "Gladiator":
        # Crested Roman helmet
        pts = [(hx - int(hd*1.05), hy + int(hd*.2)), (hx - int(hd*1.05), hy - int(hd*.7)),
               (hx - int(hd*.8), hy - int(hd*1.25)), (hx + int(hd*.8), hy - int(hd*1.25)),
               (hx + int(hd*1.05), hy - int(hd*.7)), (hx + int(hd*1.05), hy + int(hd*.2))]
        pygame.draw.polygon(surface, (155, 45, 45), pts)
        pygame.draw.polygon(surface, (220, 75, 75), pts, 2)
        # Horsehair crest
        for i in range(max(1, int(hd*.8))):
            cx = hx - int(hd*.4) + i
            pygame.draw.line(surface, RED, (cx, hy - int(hd*1.25)), (cx, hy - int(hd*2.1)), max(1, int(3*s)))
        pygame.draw.rect(surface, (40, 18, 18), (hx - int(hd*.72), hy - int(hd*.08), int(hd*1.44), int(hd*.28)))

    elif char_name == "Oni":
        # Red demon horns + angry brows
        for hd_off, curve in [(-int(hd*.7), -1), (int(hd*.7), 1)]:
            pygame.draw.polygon(surface, (200, 15, 15), [
                (hx + hd_off, hy - hd),
                (hx + hd_off + curve * int(hd*.35), hy - int(hd*2.05)),
                (hx + hd_off + curve * int(hd*.12), hy - int(hd*1.5))])
        brow_y = hy - int(hd * .35)
        pygame.draw.line(surface, (100, 0, 0), (hx - int(hd*.62), brow_y - int(hd*.2)), (hx - int(hd*.1), brow_y), max(2, int(3*s)))
        pygame.draw.line(surface, (100, 0, 0), (hx + int(hd*.1), brow_y), (hx + int(hd*.62), brow_y - int(hd*.2)), max(2, int(3*s)))

    elif char_name == "Cecalia":
        # Tentacles hanging from waist
        for i in range(4):
            tx = wx + int((i - 1.5) * 18 * s)
            for seg in range(4):
                t1 = i / (coils := 4)
                y1 = wy + seg * int(16*s)
                y2 = wy + (seg+1) * int(16*s)
                wave = int(math.sin(seg * 1.5 + i) * 8 * s)
                pygame.draw.line(surface, (30, 200, 200), (tx + wave, y1), (tx - wave, y2), max(2, int(3*s)))

    elif char_name == "Acrobat":
        # Colorful top hat
        brim_y = hy - hd
        hw, hh = int(hd * 1.4), int(hd * 1.1)
        pygame.draw.rect(surface, (190, 70, 190), (hx - int(hw*.55), brim_y - hh, int(hw*1.1), hh))
        pygame.draw.line(surface, (210, 90, 210), (hx - hw, brim_y), (hx + hw, brim_y), max(3, int(5*s)))
        pygame.draw.rect(surface, WHITE, (hx - int(hw*.55), brim_y - int(hh*.72), int(hw*1.1), int(hd*.28)))

    elif char_name == "Shapeshifter":
        # Dashed purple glow ring
        for angle in range(0, 360, 30):
            a1, a2 = math.radians(angle), math.radians(angle + 20)
            r = (hd + int(5*s))
            p1 = (hx + int(math.cos(a1)*r), hy + int(math.sin(a1)*r))
            p2 = (hx + int(math.cos(a2)*r), hy + int(math.sin(a2)*r))
            pygame.draw.line(surface, (175, 75, 255), p1, p2, max(2, int(3*s)))

    elif char_name == "Spring":
        # Coiled spring on head
        sbot, stop = hy - hd, hy - int(hd * 2.2)
        coils = 4
        for i in range(coils * 4):
            t1, t2 = i / (coils*4), (i+1) / (coils*4)
            y1 = sbot + int((stop - sbot) * t1)
            y2 = sbot + int((stop - sbot) * t2)
            x1 = hx + int(math.sin(t1 * math.pi * 2 * coils) * hd * .5)
            x2 = hx + int(math.sin(t2 * math.pi * 2 * coils) * hd * .5)
            pygame.draw.line(surface, (255, 120, 120), (x1, y1), (x2, y2), max(2, int(3*s)))

    elif char_name == "Harpy":
        # Wings from shoulders
        for side in [-1, 1]:
            wing_pts = [
                (sx, sy),
                (sx + side*int(52*s), sy - int(18*s)),
                (sx + side*int(62*s), sy + int(22*s)),
                (sx + side*int(36*s), sy + int(36*s)),
                (sx + side*int(15*s), sy + int(20*s))]
            pygame.draw.polygon(surface, (115, 0, 115), wing_pts)
            pygame.draw.polygon(surface, (175, 0, 175), wing_pts, 2)

    elif char_name == "Scarecrow":
        # Straw hat
        hat_y = hy - hd
        hw = int(hd * 2.0)
        pygame.draw.polygon(surface, (75, 50, 8), [
            (hx, hat_y - int(hd * 1.0)), (hx - hw, hat_y), (hx + hw, hat_y)])
        # X eyes
        for ex_off in [-int(hd*.38), int(hd*.38)]:
            ex, ey = hx + ex_off, hy - int(hd*.2)
            r = int(hd * .22)
            pygame.draw.line(surface, (8, 0, 8), (ex-r, ey-r), (ex+r, ey+r), max(2, int(3*s)))
            pygame.draw.line(surface, (8, 0, 8), (ex+r, ey-r), (ex-r, ey+r), max(2, int(3*s)))

    elif char_name == "Cactus":
        # Spines around head
        for i in range(8):
            angle = math.radians(-120 + i * 35)
            spine_x = hx + int(math.cos(angle) * hd)
            spine_y = hy + int(math.sin(angle) * hd)
            tip_x = hx + int(math.cos(angle) * (hd + int(13*s)))
            tip_y = hy + int(math.sin(angle) * (hd + int(13*s)))
            pygame.draw.line(surface, (20, 140, 40), (spine_x, spine_y), (tip_x, tip_y), max(2, int(3*s)))

    elif char_name == "Medic":
        # White hat with red cross
        brim_y = hy - hd
        hw, hh = int(hd * 1.1), int(hd * 1.1)
        pygame.draw.rect(surface, WHITE, (hx - hw, brim_y - hh, hw*2, hh), border_radius=3)
        pygame.draw.line(surface, WHITE, (hx - int(hw*1.3), brim_y), (hx + int(hw*1.3), brim_y), max(3, int(5*s)))
        cs = int(hd * .35)
        pygame.draw.line(surface, RED, (hx, brim_y - hh + int(hd*.18)), (hx, brim_y - int(hd*.2)), max(3, int(4*s)))
        pygame.draw.line(surface, RED, (hx - cs, brim_y - hh//2 - int(hd*.08)), (hx + cs, brim_y - hh//2 - int(hd*.08)), max(3, int(4*s)))

    elif char_name == "Arsonist":
        # Flames on head
        for i in range(5):
            fx = hx + int((i - 2) * hd * .33)
            fh = int(hd * (.58 + (i % 2) * .5))
            fc = (255, 50, 0) if i % 2 == 0 else YELLOW
            pygame.draw.ellipse(surface, fc, (fx - int(hd*.17), hy - hd - fh, int(hd*.34), fh))

    elif char_name == "Cryogenisist":
        # Ice spike crown
        for i in range(5):
            angle = math.radians(-90 + (i - 2) * 32)
            bx = hx + int(math.cos(angle) * hd * .85)
            by = hy + int(math.sin(angle) * hd * .85)
            tx = hx + int(math.cos(angle) * (hd + int(17*s)))
            ty = hy + int(math.sin(angle) * (hd + int(17*s)))
            pygame.draw.line(surface, (175, 225, 255), (bx, by), (tx, ty), max(2, int(4*s)))

    elif char_name == "Magician":
        # Tall wizard hat
        brim_y = hy - hd
        hw, hh = int(hd * 1.1), int(hd * 2.0)
        pygame.draw.polygon(surface, (95, 0, 195), [
            (hx, brim_y - hh), (hx - hw, brim_y), (hx + hw, brim_y)])
        pygame.draw.line(surface, (95, 0, 195), (hx - int(hw*1.4), brim_y), (hx + int(hw*1.4), brim_y), max(3, int(5*s)))
        pygame.draw.circle(surface, YELLOW, (hx, brim_y - int(hh*.55)), int(hd*.22))

    elif char_name == "Charger":
        # Lightning bolt on chest
        mid_x = sx + int(facing * 6 * s)
        mid_y = (sy + wy) // 2
        pygame.draw.lines(surface, YELLOW, False, [
            (mid_x + int(6*s), sy + int(5*s)), (mid_x - int(4*s), mid_y),
            (mid_x + int(3*s), mid_y), (mid_x - int(6*s), wy - int(5*s))
        ], max(2, int(3*s)))

    elif char_name == "Psychopath":
        # Knife at forward hand
        pygame.draw.line(surface, (195, 195, 215), (rhx, rhy), (rhx + facing*int(22*s), rhy - int(10*s)), max(2, int(3*s)))
        pygame.draw.line(surface, (95, 55, 15), (rhx, rhy), (rhx - facing*int(8*s), rhy + int(5*s)), max(3, int(5*s)))

    elif char_name == "Ran-Doom":
        # Dice on head: draw dots
        die_size = int(hd * .85)
        die_x = hx - die_size // 2
        die_y = hy - hd - die_size - int(4*s)
        pygame.draw.rect(surface, (220, 220, 220), (die_x, die_y, die_size, die_size), border_radius=3)
        pygame.draw.rect(surface, (80, 80, 80), (die_x, die_y, die_size, die_size), 1, border_radius=3)
        for dx, dy in [(die_size//4, die_size//4), (die_size*3//4, die_size//4),
                       (die_size//2, die_size//2),
                       (die_size//4, die_size*3//4), (die_size*3//4, die_size*3//4)]:
            pygame.draw.circle(surface, (20, 20, 20), (die_x + dx, die_y + dy), max(2, int(3*s)))

    elif char_name == "Outbacker":
        # Wide bush hat
        brim_y = hy - hd
        hw, hh = int(hd * 1.8), int(hd * .9)
        pygame.draw.ellipse(surface, (155, 95, 25), (hx - int(hw*.6), brim_y - hh, int(hw*1.2), hh))
        pygame.draw.arc(surface, (130, 75, 15), (hx - hw, brim_y - int(hd*.4), hw*2, int(hd*.6)),
                        math.radians(200), math.radians(340), max(3, int(5*s)))

    elif char_name == "Gunner":
        # Pistol at forward hand
        gx1, gy1 = rhx, rhy
        bx = gx1 + facing * int(22*s)
        pygame.draw.rect(surface, (45, 45, 45), (min(gx1, bx) - 2, gy1 - int(4*s), int(26*s), int(8*s)))
        pygame.draw.rect(surface, (65, 45, 25), (gx1 - facing*int(4*s), gy1, int(8*s), int(12*s)))

    elif char_name == "Bazooka Man":
        # Bazooka on shoulder
        baz_x1 = sx - facing * int(5*s)
        baz_x2 = baz_x1 + facing * int(58*s)
        baz_y = sy + int(5*s)
        pygame.draw.line(surface, (75, 75, 75), (baz_x1, baz_y), (baz_x2, baz_y), max(5, int(9*s)))
        pygame.draw.circle(surface, (45, 45, 45), (baz_x2, baz_y), max(4, int(6*s)))
        pygame.draw.line(surface, (95, 55, 15), (baz_x1 + facing*int(14*s), baz_y),
                         (baz_x1 + facing*int(14*s), baz_y + int(12*s)), max(3, int(5*s)))

    elif char_name == "Pinball":
        # Pinball logo on chest
        mid_y = (sy + wy) // 2
        pygame.draw.circle(surface, (255, 80, 200), (sx, mid_y), int(hd * .32))
        pygame.draw.circle(surface, WHITE, (sx, mid_y), int(hd * .32), 2)

    elif char_name == "Giant":
        # Crown
        cb, ct = hy - hd, hy - int(hd * 1.85)
        pygame.draw.polygon(surface, YELLOW, [
            (hx - hd, cb), (hx - hd, ct + int(hd*.52)),
            (hx - int(hd*.5), ct + int(hd*.82)), (hx, ct),
            (hx + int(hd*.5), ct + int(hd*.82)), (hx + hd, ct + int(hd*.52)),
            (hx + hd, cb)])
        pygame.draw.polygon(surface, (195, 155, 0), [
            (hx - hd, cb), (hx - hd, ct + int(hd*.52)),
            (hx - int(hd*.5), ct + int(hd*.82)), (hx, ct),
            (hx + int(hd*.5), ct + int(hd*.82)), (hx + hd, ct + int(hd*.52)),
            (hx + hd, cb)], 2)

    elif char_name == "Morph":
        # Double-ended resize arrows on chest
        mid_y = (sy + wy) // 2
        arr = int(20 * s)
        pygame.draw.line(surface, CYAN, (sx - arr, mid_y), (sx + arr, mid_y), max(2, int(3*s)))
        for dx in [-arr, arr]:
            sign = 1 if dx > 0 else -1
            pygame.draw.line(surface, CYAN, (sx + dx, mid_y), (sx + dx - sign*int(6*s), mid_y - int(5*s)), max(2, int(3*s)))
            pygame.draw.line(surface, CYAN, (sx + dx, mid_y), (sx + dx - sign*int(6*s), mid_y + int(5*s)), max(2, int(3*s)))

    elif char_name == "Ghost":
        # Sheet draped from shoulders
        sheet_pts = [
            (sx - int(hd*1.25), sy + int(5*s)), (sx - int(hd*1.45), wy + int(28*s)),
            (sx - int(hd*.8), wy + int(18*s)), (sx, wy + int(33*s)),
            (sx + int(hd*.8), wy + int(18*s)), (sx + int(hd*1.45), wy + int(28*s)),
            (sx + int(hd*1.25), sy + int(5*s))]
        pygame.draw.polygon(surface, (170, 170, 210), sheet_pts)
        pygame.draw.polygon(surface, (205, 205, 250), sheet_pts, 2)
        # Redraw head so it shows above the sheet
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Vampire":
        # Cape
        cape_pts = [
            (sx - int(hd*.55), sy + int(8*s)), (sx - int(hd*1.85), wy + int(18*s)),
            (sx - int(hd*.8), wy + int(8*s)), (sx, wy + int(28*s)),
            (sx + int(hd*.8), wy + int(8*s)), (sx + int(hd*1.85), wy + int(18*s)),
            (sx + int(hd*.55), sy + int(8*s))]
        pygame.draw.polygon(surface, (75, 0, 18), cape_pts)
        pygame.draw.polygon(surface, (115, 0, 38), cape_pts, 2)
        # Fangs
        for fx_off in [-int(hd*.3), int(hd*.3)]:
            pygame.draw.polygon(surface, WHITE, [
                (hx + fx_off - int(hd*.12), hy + int(hd*.42)),
                (hx + fx_off + int(hd*.12), hy + int(hd*.42)),
                (hx + fx_off, hy + int(hd*.72))])
        # Redraw head
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Astronaut":
        # Space helmet (dome around head)
        pygame.draw.circle(surface, (175, 195, 235), (hx, hy), int(hd * 1.38))
        pygame.draw.circle(surface, (95, 135, 195), (hx, hy), int(hd * 1.38), max(3, int(4*s)))
        # Visor
        pygame.draw.ellipse(surface, (55, 115, 195), (hx - int(hd*.88), hy - int(hd*.72), int(hd*1.76), int(hd*1.18)))
        pygame.draw.ellipse(surface, (100, 160, 230), (hx - int(hd*.88), hy - int(hd*.72), int(hd*1.76), int(hd*1.18)), 2)
        # Redraw head inside
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Spooderman":
        # Web lines on face
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            pygame.draw.line(surface, (140, 8, 8), (hx, hy),
                             (hx + int(math.cos(a)*hd), hy + int(math.sin(a)*hd)), 1)
        for r in [int(hd*.34), int(hd*.65), hd]:
            pygame.draw.circle(surface, (140, 8, 8), (hx, hy), r, 1)
        # White eye lenses
        for ex_off in [-int(hd*.38), int(hd*.38)]:
            pygame.draw.ellipse(surface, WHITE, (hx + ex_off - int(hd*.22), hy - int(hd*.46), int(hd*.44), int(hd*.34)))

    elif char_name == "Hooker":
        # Rope + hook at forward hand
        pygame.draw.line(surface, (130, 92, 42), (sx, sy + int(12*s)), (rhx, rhy), max(1, int(2*s)))
        pygame.draw.arc(surface, (175, 175, 175),
                        (rhx + facing*int(2*s), rhy - int(10*s), int(15*s), int(15*s)),
                        math.radians(0), math.radians(270), max(2, int(3*s)))

    elif char_name == "Mouse":
        # Round mouse ears on top of head
        for ex_off in [-int(hd*.72), int(hd*.72)]:
            pygame.draw.circle(surface, col, (hx + ex_off, hy - int(hd*1.02)), int(hd*.56))
            pygame.draw.circle(surface, (225, 165, 155), (hx + ex_off, hy - int(hd*1.02)), int(hd*.3))

    elif char_name == "Sumo":
        # Topknot
        pygame.draw.ellipse(surface, (45, 25, 8), (hx - int(hd*.36), hy - int(hd*1.52), int(hd*.72), int(hd*.62)))
        # Mawashi belt at waist
        bh = max(4, int(8*s))
        pygame.draw.rect(surface, (195, 148, 48), (wx - int(hd*.92), wy - bh//2, int(hd*1.84), bh))
        pygame.draw.rect(surface, (175, 118, 18), (wx - int(hd*.92), wy - bh//2, int(hd*1.84), bh), 2)

    elif char_name == "Headless Horseman":
        ground_y = wy + int(LEG_LEN * s)
        # ── Horse body ──────────────────────────────────────────────────────
        hb_cx, hb_cy = wx, wy + int(18 * s)
        hb_w, hb_h   = int(92 * s), int(34 * s)
        pygame.draw.ellipse(surface, (98, 68, 36),  (hb_cx - hb_w//2, hb_cy - hb_h//2, hb_w, hb_h))
        pygame.draw.ellipse(surface, (68, 44, 20),  (hb_cx - hb_w//2, hb_cy - hb_h//2, hb_w, hb_h), 2)
        # Saddle blanket
        pygame.draw.ellipse(surface, (55, 30, 60), (hb_cx - int(hb_w*.35), hb_cy - hb_h//2 - 2, int(hb_w*.7), int(hb_h*.7)))
        # ── Horse legs (4) ──────────────────────────────────────────────────
        for leg_off in [-int(28*s), -int(10*s), int(10*s), int(28*s)]:
            ltop = (hb_cx + leg_off, hb_cy + hb_h//2)
            lbot = (hb_cx + leg_off + facing * int(3*s), ground_y)
            pygame.draw.line(surface, (78, 50, 26), ltop, lbot, max(3, int(5*s)))
            pygame.draw.ellipse(surface, (38, 24, 12), (lbot[0] - int(7*s), lbot[1] - int(4*s), int(14*s), int(8*s)))
        # ── Horse neck & head ────────────────────────────────────────────────
        nk_base = (hb_cx + facing * int(hb_w//2 - int(4*s)), hb_cy - int(4*s))
        nk_top  = (nk_base[0] + facing * int(20*s), hb_cy - int(42*s))
        pygame.draw.line(surface, (98, 68, 36), nk_base, nk_top, max(6, int(11*s)))
        horse_head_pts = [
            nk_top,
            (nk_top[0] + facing*int(30*s), nk_top[1] + int(6*s)),
            (nk_top[0] + facing*int(32*s), nk_top[1] + int(20*s)),
            (nk_top[0] + facing*int(16*s), nk_top[1] + int(24*s)),
            (nk_top[0],                    nk_top[1] + int(16*s)),
        ]
        pygame.draw.polygon(surface, (108, 74, 42), horse_head_pts)
        pygame.draw.polygon(surface, (68, 44, 20),  horse_head_pts, 2)
        pygame.draw.circle(surface, (28, 18, 8), (nk_top[0] + facing*int(20*s), nk_top[1] + int(13*s)), max(2, int(4*s)))  # eye
        pygame.draw.circle(surface, (68, 40, 14), (nk_top[0] + facing*int(28*s), nk_top[1] + int(20*s)), max(1, int(3*s)))  # nostril
        # Mane
        for mi in range(4):
            mx = nk_base[0] + (nk_top[0] - nk_base[0]) * mi // 4
            my = nk_base[1] + (nk_top[1] - nk_base[1]) * mi // 4
            pygame.draw.line(surface, (42, 26, 8), (mx, my), (mx - facing*int(10*s), my + int(10*s)), max(2, int(3*s)))
        # ── Horse tail ──────────────────────────────────────────────────────
        tb = (hb_cx - facing*int(hb_w//2), hb_cy - int(8*s))
        te = (tb[0] - facing*int(28*s), tb[1] - int(28*s))
        pygame.draw.line(surface, (48, 28, 10), tb, te, max(3, int(5*s)))
        for ts in [(te[0], te[1] + int(22*s)), (te[0] - facing*int(10*s), te[1] + int(14*s))]:
            pygame.draw.line(surface, (48, 28, 10), te, ts, max(2, int(3*s)))
        # ── Rider's dark cloak ───────────────────────────────────────────────
        cloak_pts = [
            (sx - int(hd*.5),  sy + int(6*s)),
            (sx - int(hd*2.0), wy + int(12*s)),
            (sx - int(hd*1.0), wy + int(4*s)),
            (sx + int(hd*1.0), wy + int(4*s)),
            (sx + int(hd*2.0), wy + int(12*s)),
            (sx + int(hd*.5),  sy + int(6*s)),
        ]
        pygame.draw.polygon(surface, (28, 18, 28), cloak_pts)
        pygame.draw.polygon(surface, (58, 38, 58), cloak_pts, 2)
        # ── Pumpkin "head" carried in forward hand ───────────────────────────
        pr = int(hd * 0.78)
        pygame.draw.circle(surface, (215, 118, 0), (rhx, rhy), pr)
        # Pumpkin ridges
        for ridge in range(-1, 2):
            pygame.draw.arc(surface, (190, 95, 0),
                            (rhx + ridge*int(pr*.35) - int(pr*.22), rhy - pr, int(pr*.44), pr*2),
                            math.radians(55), math.radians(125), max(1, int(2*s)))
        # Carved face
        eye_r = max(2, int(pr * .18))
        for eye_off in [-int(pr*.3), int(pr*.3)]:
            pygame.draw.polygon(surface, BLACK, [
                (rhx + eye_off,        rhy - int(pr*.18)),
                (rhx + eye_off - eye_r, rhy + eye_r//2),
                (rhx + eye_off + eye_r, rhy + eye_r//2)])
        mouth_pts = [(rhx - int(pr*.42) + i*int(pr*.21),
                      rhy + int(pr*.35) + (int(pr*.14) if i % 2 == 0 else 0))
                     for i in range(5)]
        pygame.draw.lines(surface, BLACK, False, mouth_pts, max(1, int(2*s)))
        pygame.draw.line(surface, (45, 95, 28), (rhx, rhy - pr), (rhx, rhy - pr - int(7*s)), max(2, int(3*s)))  # stem

    elif char_name == "Pencil":
        # Yellow hexagonal pencil body in forward hand, pointing downward
        px, py = rhx, rhy
        body_h = int(32 * s)
        tip_h  = int(10 * s)
        pw     = max(5, int(7 * s))
        # Pencil body (yellow rectangle)
        pygame.draw.rect(surface, (245, 220, 50), (px - pw, py - body_h, pw*2, body_h))
        pygame.draw.rect(surface, (180, 140, 20), (px - pw, py - body_h, pw*2, body_h), 1)
        # Pink eraser at top
        pygame.draw.rect(surface, (240, 130, 130), (px - pw, py - body_h - int(7*s), pw*2, int(7*s)))
        # Silver ferrule (band)
        pygame.draw.rect(surface, (180, 180, 180), (px - pw, py - body_h, pw*2, int(4*s)))
        # Wood cone tip
        pygame.draw.polygon(surface, (210, 170, 100), [
            (px - pw, py), (px + pw, py), (px, py + tip_h)])
        # Graphite point
        pygame.draw.polygon(surface, (50, 50, 50), [
            (px - int(pw*.4), py + int(tip_h*.5)),
            (px + int(pw*.4), py + int(tip_h*.5)),
            (px, py + tip_h)])

    elif char_name == "Eraser":
        # Pink rectangular eraser block in forward hand
        ew, eh = max(6, int(20*s)), max(4, int(12*s))
        ex, ey = rhx - ew//2, rhy - eh
        pygame.draw.rect(surface, (240, 160, 150), (ex, ey, ew, eh), border_radius=2)
        pygame.draw.rect(surface, (180, 80, 80),   (ex, ey, ew, eh), 1, border_radius=2)
        # Blue label stripe
        stripe_h = max(2, int(4*s))
        pygame.draw.rect(surface, (80, 120, 220), (ex, ey + (eh - stripe_h)//2, ew, stripe_h))
        # Eraser dust specks below
        for dx, dy in [(-int(6*s), int(4*s)), (int(2*s), int(7*s)), (int(5*s), int(3*s))]:
            pygame.draw.circle(surface, (240, 160, 150), (rhx+dx, rhy+dy), max(1, int(2*s)))

    elif char_name == "Ink Brush":
        # Black beret
        beret_r = int(hd * 1.1)
        pygame.draw.ellipse(surface, (15, 15, 15),
                            (hx - beret_r, hy - hd - int(7*s), beret_r*2, int(beret_r*0.7)))
        pygame.draw.circle(surface, (15, 15, 15), (hx + facing*int(hd*.25), hy - hd - int(5*s)), int(hd*.55))
        # Ink splatter on torso
        for dx, dy, r in [(-int(6*s), int(12*s), int(4*s)), (int(5*s), int(18*s), int(3*s)), (int(2*s), int(6*s), int(2*s))]:
            pygame.draw.circle(surface, (10, 10, 30), (sx+dx, sy+dy), max(1, r))
        # Large ink brush in forward hand
        bx, by = rhx + facing*int(4*s), rhy
        tip_y = by + int(22*s)
        pygame.draw.line(surface, (140, 100, 60), (bx, by), (bx, by + int(16*s)), max(2, int(3*s)))  # handle
        pygame.draw.polygon(surface, (10, 10, 30), [
            (bx - int(4*s), by + int(16*s)),
            (bx + int(4*s), by + int(16*s)),
            (bx, tip_y)])  # bristles
        pygame.draw.circle(surface, (5, 5, 20), (bx, tip_y), max(2, int(3*s)))  # ink drop


def draw_stickman(surface, x, y, color, facing, action, action_t, flash=False, scale=1.0, char_name=""):
    col = WHITE if flash else color
    s = scale

    hd = int(HEAD_R   * s)
    bl = int(BODY_LEN * s)
    al = int(ARM_LEN  * s)
    ll = int(LEG_LEN  * s)
    nl = int(NECK_LEN * s)

    def ln(p1, p2, w=3):
        pygame.draw.line(surface, col, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), max(1, int(w * s)))

    def circ(cx, cy, r):
        pygame.draw.circle(surface, col, (int(cx), int(cy)), r)

    # ── Dead pose: stickman lying flat on the ground ────────────────────────
    if action == 'dead':
        # Head lies to the side (opposite of facing), body horizontal
        hx_d = int(x) - facing * int((hd + bl + al // 2) * s)
        hy_d = int(y) - hd              # head center just above ground
        if char_name != "Headless Horseman":
            circ(hx_d, hy_d, hd)       # head
        neck  = (hx_d + facing * hd,   hy_d)
        hip   = (int(x) + facing * int(20 * s), hy_d)
        ln(neck, hip, 4)               # horizontal torso
        mid   = ((neck[0] + hip[0]) // 2, hy_d)
        ln(mid, (mid[0], mid[1] - int(al * 0.55)),     3)   # arm upward
        ln(mid, (mid[0] + facing * int(al * 0.4), mid[1] + int(al * 0.3)), 3)  # arm drooping
        ln(hip, (hip[0] + facing * int(25 * s), int(y)), 3)   # leg 1
        ln(hip, (hip[0] + facing * int(40 * s), int(y - 10 * s)), 3)           # leg 2
        if char_name:
            draw_costume(surface, char_name, (hx_d, hy_d), hd,
                         (neck[0], hy_d), hip, mid, mid, facing, s, col)
        return None

    waist    = (x, y - ll)
    shoulder = (waist[0], waist[1] - bl)
    head_c   = (shoulder[0], shoulder[1] - nl - hd)

    # Legs — lx/rx are absolute foot offsets from waist centre
    if action == 'walk':
        t = action_t * math.pi * 2
        lx = -math.sin(t) * 22 * s
        rx =  math.sin(t) * 22 * s
    elif action == 'kick':
        lx = -8 * s
        rx = facing * action_t * 60 * s
    elif action == 'jump':
        lx, rx = -16 * s, 16 * s
    elif action == 'duck':
        lx, rx = -28 * s, 28 * s
    else:
        lx, rx = -10 * s, 10 * s

    lf = (waist[0] + lx, y)
    rf = (waist[0] + rx, y)
    lk = (waist[0] + lx * 0.5, waist[1] + 20 * s)
    rk = (waist[0] + rx * 0.5, waist[1] + 20 * s)
    ln(waist, lk); ln(lk, lf)
    ln(waist, rk); ln(rk, rf)

    # Arms
    if action == 'punch':
        ext = int(action_t * al)
        la  = (shoulder[0] - facing * 10 * s, shoulder[1] + 10 * s)
        lh  = (la[0] - facing * 12 * s, la[1] + 18 * s)
        ra  = (shoulder[0] + facing * ext, shoulder[1])
        rh  = (ra[0] + facing * (al - ext) * 0.3, ra[1] + 5 * s)
    elif action == 'kick':
        la = (shoulder[0] - facing * 10 * s, shoulder[1] + 14 * s)
        lh = (la[0], la[1] + 22 * s)
        ra = (shoulder[0] + facing * 15 * s, shoulder[1] + 5 * s)
        rh = (ra[0] + facing * 10 * s, ra[1] + 15 * s)
    elif action == 'walk':
        t  = action_t * math.pi * 2
        sw = math.sin(t) * 20 * s
        la = (shoulder[0] - sw * facing * 0.5, shoulder[1] + 10 * s)
        lh = (la[0] - 10 * s, la[1] + al * 0.7)
        ra = (shoulder[0] + sw * facing * 0.5, shoulder[1] + 10 * s)
        rh = (ra[0] + 10 * s, ra[1] + al * 0.7)
    elif action == 'hurt':
        la = (shoulder[0] - facing * 20 * s, shoulder[1] - 10 * s)
        lh = (la[0] - 15 * s, la[1] - 15 * s)
        ra = (shoulder[0] + facing * 20 * s, shoulder[1] - 10 * s)
        rh = (ra[0] + 15 * s, ra[1] - 15 * s)
    elif action == 'duck':
        la = (shoulder[0] - 14 * s, shoulder[1] + 22 * s)
        lh = (la[0] - 6 * s,  la[1] + 16 * s)
        ra = (shoulder[0] + 14 * s, shoulder[1] + 22 * s)
        rh = (ra[0] + 6 * s,  ra[1] + 16 * s)
    else:
        la = (shoulder[0] - 10 * s, shoulder[1] + 10 * s)
        lh = (la[0] - 5 * s,  la[1] + al * 0.8)
        ra = (shoulder[0] + 10 * s, shoulder[1] + 10 * s)
        rh = (ra[0] + 5 * s,  ra[1] + al * 0.8)

    ln(shoulder, la); ln(la, lh)
    ln(shoulder, ra); ln(ra, rh)
    ln(waist, shoulder, 4)
    if char_name != "Headless Horseman":
        circ(head_c[0], head_c[1], hd)

    if char_name:
        draw_costume(surface, char_name, head_c, hd, shoulder, waist, lh, rh, facing, s, col)

    if action == 'punch':
        return (int(ra[0] + facing * 10 * s), int(ra[1]))
    if action == 'kick':
        return (int(waist[0] + facing * int(action_t * 80 * s)), int(y - 20 * s))
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
    # Underworld: 2 static stone ledges + 2 slow drifters, 3 springs
    {"name": "Underworld", "platforms": [
        (55,  GROUND_Y-105, 165, 0,   0),
        (680, GROUND_Y-105, 165, 0,   0),
        (270, GROUND_Y-175, 135, 1.5, 110),
        (495, GROUND_Y-175, 135, -1.5,110),
    ], "springs": [
        (200, -22), (450, -22), (700, -22),
    ]},
    # Space: 3 drifting asteroid platforms, 2 launch pads
    {"name": "Space", "platforms": [
        (80,  GROUND_Y-120, 150, 1.5, 110),
        (630, GROUND_Y-120, 150, -1.5,110),
        (355, GROUND_Y-230, 130, 2.5, 100),
    ], "springs": [
        (280, -26), (620, -26),
    ]},
    # Jungle: tangled canopy, two tree-trunk platforms and a vine bridge
    {"name": "Jungle", "platforms": [
        (55,  GROUND_Y-110, 175, 0,   0),
        (670, GROUND_Y-110, 175, 0,   0),
        (340, GROUND_Y-210, 150, 1.2, 120),
    ], "springs": [
        (450, -22),
    ]},
    # Computer: circuit-board ground, keyboard-key platforms, roaming mouse platform
    {"name": "Computer", "platforms": [
        (60,  GROUND_Y-105, 160, 0,   0),
        (680, GROUND_Y-105, 160, 0,   0),
        (330, GROUND_Y-200, 140, 1.5, 120),
    ], "springs": []},
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
    "Underworld": {"adv": "Skeleton",    "dis": "Boxer"},
    "Space":      {"adv": "Astronaut",    "dis": "Giant"},
    "Jungle":     {"adv": "Hooker",       "dis": "Gunner"},
    "Computer":   {"adv": "Charger",      "dis": "Headless Horseman"},
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

    elif s == 6:  # Underworld
        surface.fill((8, 0, 12))   # near-black void
        # glowing lava horizon band
        pygame.draw.rect(surface, (80, 10, 0),  (0, GROUND_Y - 60, WIDTH, 60))
        pygame.draw.rect(surface, (130, 30, 0), (0, GROUND_Y - 20, WIDTH, 20))
        # lava cracks in ground
        for cx in [120, 260, 420, 580, 740, 860]:
            pygame.draw.line(surface, (220, 80, 0), (cx, GROUND_Y+2), (cx+30, GROUND_Y+30), 2)
            pygame.draw.line(surface, (255, 140, 0), (cx+10, GROUND_Y+2), (cx+10, GROUND_Y+18), 1)
        # stalactites hanging from top
        for sx, sw, sh in [(60,22,70),(160,18,55),(290,24,90),(430,20,65),(560,26,80),(700,18,50),(820,22,75)]:
            pygame.draw.polygon(surface, (25, 5, 35), [(sx, 0), (sx+sw, 0), (sx+sw//2, sh)])
            pygame.draw.polygon(surface, (50, 10, 60), [(sx+4, 0), (sx+sw-4, 0), (sx+sw//2, sh-12)])
        # floating skulls (decorative)
        for skx, sky in [(180, 180), (500, 140), (760, 200)]:
            pygame.draw.circle(surface, (200, 200, 190), (skx, sky), 10)
            pygame.draw.circle(surface, (8, 0, 12), (skx-4, sky-2), 3)
            pygame.draw.circle(surface, (8, 0, 12), (skx+4, sky-2), 3)
            pygame.draw.line(surface, (8, 0, 12), (skx-3, sky+4), (skx+3, sky+4), 2)
        # dark stone ground
        pygame.draw.rect(surface, (20, 5, 25),  (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (10, 2, 15),  (0, GROUND_Y+22, WIDTH, HEIGHT-GROUND_Y))
        pygame.draw.line(surface, (160, 40, 0), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)

    elif s == 7:  # Space
        surface.fill((2, 2, 18))   # deep space black
        # stars
        for sx, sy in [(45,15),(100,60),(175,28),(240,80),(310,12),(380,55),(460,30),
                       (530,72),(610,18),(680,50),(755,35),(820,75),(870,20),(50,200),
                       (150,160),(290,190),(440,145),(590,175),(730,155),(850,200),
                       (20,320),(200,300),(370,330),(520,310),(700,290),(880,325)]:
            r = 2 if (sx + sy) % 5 == 0 else 1
            pygame.draw.circle(surface, WHITE, (sx, sy), r)
        # large planet (orange/red gas giant) top-right
        pygame.draw.circle(surface, (210, 100, 40), (760, 90), 72)
        pygame.draw.circle(surface, (230, 130, 60), (760, 90), 60)
        for band_y, band_h, band_c in [
            (50, 8,  (190, 80, 30)),
            (72, 6,  (240, 150, 70)),
            (96, 10, (185, 75, 25)),
            (116, 5, (220, 120, 55)),
        ]:
            pygame.draw.ellipse(surface, band_c, (700, band_y, 120, band_h))
        # planet ring
        pygame.draw.ellipse(surface, (180, 130, 60), (698, 80, 124, 22), 3)
        # small distant moon
        pygame.draw.circle(surface, (170, 170, 160), (140, 70), 20)
        pygame.draw.circle(surface, (130, 130, 120), (148, 64), 5)
        pygame.draw.circle(surface, (130, 130, 120), (136, 78), 3)
        # nebula glow (soft blobs)
        for nx, ny, nr, nc in [(300, 200, 80, (30, 0, 60)), (600, 250, 65, (0, 20, 55))]:
            pygame.draw.circle(surface, nc, (nx, ny), nr)
        # space station metal floor
        pygame.draw.rect(surface, (30, 35, 50),  (0, GROUND_Y+2,  WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (20, 24, 38),  (0, GROUND_Y+20, WIDTH, HEIGHT-GROUND_Y))
        for gx in range(0, WIDTH, 40):
            pygame.draw.line(surface, (40, 48, 65), (gx, GROUND_Y+2), (gx, HEIGHT), 1)
        pygame.draw.line(surface, (80, 120, 180), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 2)

    elif s == 8:  # Jungle
        surface.fill((30, 70, 20))   # dark canopy sky
        # background foliage blobs
        for bx, by, br, bc in [
            (0,   200, 140, (20, 80, 15)), (180, 160, 120, (25, 95, 18)),
            (360, 180, 130, (18, 75, 12)), (540, 170, 125, (22, 88, 16)),
            (720, 190, 135, (20, 82, 14)), (860, 160, 110, (24, 90, 17)),
            (100, 100,  90, (15, 65, 10)), (450,  90,  85, (17, 70, 12)),
            (750, 110,  95, (16, 68, 11)),
        ]:
            pygame.draw.circle(surface, bc, (bx, by), br)
        # tree trunks
        for tx in [60, 200, 420, 650, 830]:
            pygame.draw.rect(surface, (60, 35, 10), (tx - 10, GROUND_Y - 180, 20, 182))
            pygame.draw.rect(surface, (80, 50, 15), (tx - 7,  GROUND_Y - 180, 7,  182))
        # hanging vines
        for vx in [130, 280, 390, 520, 700, 810]:
            for seg in range(10):
                vy1 = seg * 30
                vy2 = vy1 + 28
                pygame.draw.line(surface, (40, 120, 20), (vx + int(math.sin(seg * 0.9) * 6), vy1),
                                 (vx + int(math.sin((seg + 1) * 0.9) * 6), vy2), 2)
        # foreground bush silhouettes
        for bx, bw in [(0, 220), (180, 180), (430, 200), (650, 170), (790, 200)]:
            pygame.draw.ellipse(surface, (15, 55, 8), (bx, GROUND_Y - 35, bw, 55))
        # jungle floor
        pygame.draw.rect(surface, (35, 85, 15), (0, GROUND_Y + 2,  WIDTH, HEIGHT - GROUND_Y - 2))
        pygame.draw.rect(surface, (25, 60, 10), (0, GROUND_Y + 22, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(surface, (50, 130, 20), (0, GROUND_Y + 2), (WIDTH, GROUND_Y + 2), 3)

    elif s == 9:  # Computer — desktop screen
        # Wallpaper gradient (light blue sky)
        for gy in range(HEIGHT):
            t = gy / HEIGHT
            r = int(30  + t * 80)
            g = int(100 + t * 60)
            b = int(180 + t * 40)
            pygame.draw.line(surface, (r, g, b), (0, gy), (WIDTH, gy))
        # Desktop icons (folder-style)
        for ix, iy, ic in [(60, 60, (255, 200, 60)), (130, 60, (80, 160, 255)),
                           (200, 60, (255, 100, 80)), (60, 130, (120, 220, 120)),
                           (130, 130, (200, 80, 220))]:
            pygame.draw.rect(surface, ic, (ix, iy, 36, 30), border_radius=3)
            pygame.draw.rect(surface, (255, 255, 255), (ix, iy, 36, 30), 1, border_radius=3)
            pygame.draw.rect(surface, ic, (ix, iy - 10, 18, 12), border_radius=2)  # folder tab
            lbl = font_tiny.render("File", True, (240, 240, 240))
            surface.blit(lbl, (ix + 18 - lbl.get_width()//2, iy + 32))
        # Browser window in background
        wx, wy, ww, wh = 280, 40, 360, 200
        pygame.draw.rect(surface, (220, 220, 220), (wx, wy, ww, wh), border_radius=4)
        pygame.draw.rect(surface, (180, 180, 180), (wx, wy, ww, wh), 2, border_radius=4)
        pygame.draw.rect(surface, (60, 120, 200), (wx, wy, ww, 24), border_radius=4)  # title bar
        for btn_x, btn_col in [(wx+ww-14, (255,80,80)), (wx+ww-32,(255,200,60)), (wx+ww-50,(80,200,80))]:
            pygame.draw.circle(surface, btn_col, (btn_x, wy+12), 7)
        pygame.draw.rect(surface, (245, 245, 250), (wx+4, wy+28, ww-8, wh-32))
        pygame.draw.rect(surface, (200, 200, 200), (wx+4, wy+28, ww-8, 18))  # URL bar
        for line_y in range(wy+56, wy+wh-8, 14):
            lw = 280 if line_y % 28 == 0 else 180
            pygame.draw.rect(surface, (200, 210, 220), (wx+8, line_y, lw, 8), border_radius=2)
        # Taskbar
        pygame.draw.rect(surface, (30, 30, 30), (0, GROUND_Y + 2, WIDTH, HEIGHT - GROUND_Y - 2))
        pygame.draw.line(surface, (80, 80, 80), (0, GROUND_Y + 2), (WIDTH, GROUND_Y + 2), 2)
        # Start button
        pygame.draw.rect(surface, (0, 120, 212), (4, GROUND_Y + 6, 60, HEIGHT - GROUND_Y - 10), border_radius=3)
        st = font_tiny.render("Start", True, WHITE)
        surface.blit(st, (8, GROUND_Y + 8))
        # Taskbar icons
        for ti, tc in enumerate([(255,80,80),(80,180,255),(255,200,60)]):
            pygame.draw.rect(surface, tc, (72 + ti*36, GROUND_Y + 7, 28, HEIGHT - GROUND_Y - 12), border_radius=2)
        # Clock
        import time as _t
        clk = font_tiny.render(_t.strftime("%H:%M"), True, (220, 220, 220))
        surface.blit(clk, (WIDTH - clk.get_width() - 8, GROUND_Y + 8))


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
# Projectile
# ---------------------------------------------------------------------------

class Projectile:
    RADIUS = 9
    SPEED  = 9

    def __init__(self, x, y, facing, owner):
        self.x      = float(x)
        self.y      = float(y)
        self.vx     = self.SPEED * facing
        self.owner  = owner
        self.alive  = True

    def update(self):
        self.x += self.vx
        if self.x < 0 or self.x > WIDTH:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (30, 120, 50),  (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (80, 220, 120), (cx, cy), self.RADIUS - 3)
        pygame.draw.circle(surface, (180, 255, 200),(cx, cy), self.RADIUS - 6)

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 28


# ---------------------------------------------------------------------------
# Orb (bazooka — explodes after 2 seconds)
# ---------------------------------------------------------------------------

class Orb:
    SPEED          = 5
    FUSE           = 120   # 2 seconds
    EXPLODE_RADIUS = 90
    EXPLODE_DMG    = 35
    EXPLODE_DUR    = 24   # frames explosion visual lasts

    def __init__(self, x, y, facing, owner):
        self.x            = float(x)
        self.y            = float(y)
        self.vx           = self.SPEED * facing
        self.owner        = owner
        self.fuse         = self.FUSE
        self.exploding    = False
        self.explode_timer = 0
        self.damaged      = False   # damage applied flag
        self.alive        = True

    def update(self):
        if not self.exploding:
            self.x    += self.vx
            self.fuse -= 1
            if self.fuse <= 0 or self.x < 0 or self.x > WIDTH:
                self.exploding     = True
                self.explode_timer = self.EXPLODE_DUR
        else:
            self.explode_timer -= 1
            if self.explode_timer <= 0:
                self.alive = False

    def draw(self, surface):
        if not self.exploding:
            cx, cy = int(self.x), int(self.y)
            pulse = (self.fuse // 8) % 2 == 0
            pygame.draw.circle(surface, (200, 60, 20) if pulse else (240, 100, 30), (cx, cy), 11)
            pygame.draw.circle(surface, (255, 180, 60), (cx, cy), 6)
            pygame.draw.circle(surface, (255, 240, 120), (cx, cy), 3)
        else:
            prog = 1.0 - self.explode_timer / self.EXPLODE_DUR
            r    = int(self.EXPLODE_RADIUS * prog)
            w    = max(1, int(8 * (1 - prog)))
            pygame.draw.circle(surface, (255, 160, 0),  (int(self.x), int(self.y)), r, w)
            if r > 12:
                pygame.draw.circle(surface, (255, 80, 0), (int(self.x), int(self.y)), r - 10, max(1, w-2))


# ---------------------------------------------------------------------------
# BouncingBall (Pinball character)
# ---------------------------------------------------------------------------

class BouncingBall:
    RADIUS   = 9
    SPEED    = 8
    LIFETIME = 300   # 5 seconds at 60fps
    HIT_CD   = 30   # 0.5s cooldown between hits on the same target

    def __init__(self, x, y, facing, owner):
        self.x       = float(x)
        self.y       = float(y)
        self.vx      = self.SPEED * facing
        self.vy      = -4.0          # slight upward angle on launch
        self.owner   = owner
        self.alive   = True
        self.frames  = 0
        self.hit_cd  = 0             # cooldown before can damage again

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # Bounce off left/right walls
        if self.x - self.RADIUS < 0:
            self.x  = float(self.RADIUS)
            self.vx = abs(self.vx)
        elif self.x + self.RADIUS > WIDTH:
            self.x  = float(WIDTH - self.RADIUS)
            self.vx = -abs(self.vx)

        # Bounce off ground
        if self.y + self.RADIUS >= GROUND_Y:
            self.y  = float(GROUND_Y - self.RADIUS)
            self.vy = -abs(self.vy)

        # Bounce off ceiling
        if self.y - self.RADIUS < 0:
            self.y  = float(self.RADIUS)
            self.vy = abs(self.vy)

        if self.hit_cd > 0:
            self.hit_cd -= 1

        self.frames += 1
        if self.frames >= self.LIFETIME:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (160, 0, 100),   (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (255, 80, 200),  (cx, cy), self.RADIUS - 3)
        pygame.draw.circle(surface, (255, 200, 240), (cx, cy), self.RADIUS - 6)

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 28


# ---------------------------------------------------------------------------
# Fighter
# ---------------------------------------------------------------------------

class Fighter:
    def __init__(self, x, char_data, facing, controls):
        if char_data.get("random_stats"):
            char_data = dict(char_data)   # copy so CHARACTERS list is unchanged
            char_data["speed"]       = random.randint(3, 9)
            char_data["jump"]        = random.randint(-17, -10)
            char_data["punch_dmg"]   = random.randint(4, 22)
            char_data["kick_dmg"]    = random.randint(4, 22)
            char_data["max_hp"]      = random.randint(75, 160)
            char_data["double_jump"] = random.choice([True, False])
            char_data["color"]       = (random.randint(80,255), random.randint(80,255), random.randint(80,255))
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
        self.leech        = bool(char_data.get("vampire"))
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
        self.is_crit          = False  # current punch is a critical hit
        self.crit_display_timer = 0   # frames to show CRIT! popup
        self.ducking          = False  # currently ducking (immune to punches)
        self.blocking         = False  # currently holding block
        self.shock_frames     = 0   # frames of speed-halving shock remaining
        self.boomerang_timer    = 0   # frames boomerang is active
        self.boomerang_cooldown = 0   # frames until can throw again
        self.boomerang_angle    = 0.0 # current orbit angle in radians
        self.boomerang_hit_cd   = 0   # per-hit cooldown to avoid rapid damage
        self.pending_ball       = False  # shoot_kick: spawn a ball this frame
        self.pending_orb        = False  # bazooka_kick: spawn an orb this frame
        self.bazooka_cooldown   = 0      # 5-second cooldown between orb shots
        self.pending_bounce     = False  # bounce_kick: spawn a bouncing ball this frame
        self.draw_scale         = 2.0 if char_data.get("giant") else (0.45 if char_data.get("tiny") else 1.0)
        self._size_state        = 0    # for size_kick: 0=normal, 1=big, 2=small
        self.angle              = 0.0  # visual rotation angle (degrees)
        self.angle_vel          = 0.0  # degrees per frame
        self.float_timer        = random.randint(20, 50)  # frames until next drift impulse
        self.wall_cling_active  = False  # Spooderman: currently clinging to a wall
        self.wall_dir           = 0      # -1 = left wall, 1 = right wall
        self.pending_hook       = False  # Hooker: spawn a snake hook this frame
        self.pending_pumpkin    = False  # Headless Horseman: throw pumpkin this frame
        self.pumpkin_cooldown   = 0      # cooldown between throws
        self.pending_ink_clone       = False  # Ink Brush: spawn a clone this frame
        self.ink_clone_cooldown      = 0      # cooldown between clones
        self.pending_draw_platform   = False  # Pencil: draw a platform this frame
        self.draw_platform_cooldown  = 0      # cooldown between draws
        self.pending_erase           = False  # Eraser: erase nearby platforms this frame
        self.erase_cooldown          = 0      # cooldown between erases
        self.dash_tap_left      = 0     # frames remaining in double-tap window (left)
        self.dash_tap_right     = 0     # frames remaining in double-tap window (right)
        self.dash_cd            = 0     # cooldown between dashes
        self.dash_frames        = 0     # frames of active dash remaining
        self.dash_dir           = 0     # direction of current dash
        self._prev_left         = False # was left key held last frame
        self._prev_right        = False # was right key held last frame

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
        elif t == 'cleanse':
            self.poison_frames = 0
            self.poison_tick   = 0
            self.fire_frames   = 0
            self.fire_tick     = 0
            self.shock_frames  = 0

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
        if self.shock_frames > 0:
            self.shock_frames -= 1
        if self.bazooka_cooldown > 0:
            self.bazooka_cooldown -= 1
        if self.pumpkin_cooldown > 0:
            self.pumpkin_cooldown -= 1
        if self.ink_clone_cooldown > 0:
            self.ink_clone_cooldown -= 1
        if self.draw_platform_cooldown > 0:
            self.draw_platform_cooldown -= 1
        if self.erase_cooldown > 0:
            self.erase_cooldown -= 1
        if self.boomerang_timer > 0:
            self.boomerang_timer -= 1
            self.boomerang_angle = (self.boomerang_angle + 0.09) % (2 * math.pi)
            if self.boomerang_hit_cd > 0: self.boomerang_hit_cd -= 1
            if self.boomerang_timer == 0:
                self.boomerang_cooldown = 240   # 4s cooldown after expiry
        elif self.boomerang_cooldown > 0:
            self.boomerang_cooldown -= 1

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
        eff_grav = 0.13 if self.char.get("anti_gravity") else GRAVITY
        self.vy += eff_grav
        self.y  += self.vy
        landed = False
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            landed = True
        elif not self.char.get("phase"):
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
            self.wall_cling_active = False
        else:
            self.on_ground = False

        # Wall cling (Spooderman)
        self.wall_cling_active = False
        if self.char.get("wall_cling") and not self.on_ground:
            if self.x <= 52:
                self.wall_cling_active = True
                self.wall_dir = -1
                self.vy = min(self.vy, 1.2)   # slow wall-slide
            elif self.x >= WIDTH - 52:
                self.wall_cling_active = True
                self.wall_dir = 1
                self.vy = min(self.vy, 1.2)
        if not self.wall_cling_active:
            self.wall_dir = 0

        self.x = max(50.0, min(float(WIDTH - 50), self.x))
        self.facing = 1 if other.x > self.x else -1

        # Floating drift + rotation (Space stage or Astronaut)
        if GRAVITY < 0.3 or self.char.get("anti_gravity"):
            self.angle += self.angle_vel
            self.float_timer -= 1
            if self.float_timer <= 0:
                self.vy        = random.uniform(-5.0, 2.5)
                self.angle_vel = random.uniform(-4.0, 4.0)
                self.float_timer = random.randint(35, 85)
        else:
            self.angle     = 0.0
            self.angle_vel = 0.0

        spd = self.char["speed"] * self.speed_boost * (0.5 if self.shock_frames > 0 else 1.0)

        duck_key  = self.controls.get('duck')
        block_key = self.controls.get('block')
        self.ducking  = (bool(duck_key  and keys[duck_key])  and
                         self.on_ground and self.hurt_timer == 0 and not self.attacking)
        self.blocking = (bool(block_key and keys[block_key]) and
                         self.on_ground and self.hurt_timer == 0 and not self.attacking and not self.ducking)
        if self.ducking:
            self.action = 'duck'

        # Dash timers
        if self.dash_cd        > 0: self.dash_cd        -= 1
        if self.dash_tap_left  > 0: self.dash_tap_left  -= 1
        if self.dash_tap_right > 0: self.dash_tap_right -= 1
        if self.dash_frames    > 0:
            self.dash_frames -= 1
            self.x += self.dash_dir * 9
        else:
            self.dash_dir = 0

        if self.hurt_timer == 0 and self.freeze_frames == 0 and not self.ducking and not self.blocking:
            ctrl = self.controls
            can_atk = not self.attacking or self.action in ('idle', 'walk', 'jump')

            if can_atk and keys[ctrl['punch']] and self.punch_cooldown == 0:
                moving_toward = ((keys[ctrl['right']] and self.facing == 1) or
                                 (keys[ctrl['left']]  and self.facing == -1))
                self._start('punch', 0.07)
                self.punch_cooldown = FPS        # 1 second
                self.is_crit = moving_toward
            elif can_atk and keys[ctrl['kick']] and self.kick_cooldown == 0:
                self._start('kick', 0.06)
                self.kick_cooldown = FPS * 2     # 2 seconds
                if self.char.get("teleport_kick"):
                    self.x = float(random.randint(80, WIDTH - 80))
                    self.flash_timer = 12
                if self.char.get("boomerang_kick") and self.boomerang_timer == 0 and self.boomerang_cooldown == 0:
                    self.boomerang_timer = 240   # 4 seconds
                    self.boomerang_angle = 0.0
                if self.char.get("shoot_kick"):
                    self.pending_ball = True
                if self.char.get("bazooka_kick") and self.bazooka_cooldown == 0:
                    self.pending_orb      = True
                    self.bazooka_cooldown = FPS * 5   # 5 second cooldown
                if self.char.get("bounce_kick"):
                    self.pending_bounce = True
                if self.char.get("size_kick"):
                    self._size_state = (self._size_state + 1) % 3
                    self.draw_scale = (1.0, 2.0, 0.55)[self._size_state]
                if self.char.get("grapple_kick"):
                    self.pending_hook = True
                if self.char.get("pumpkin_kick") and self.pumpkin_cooldown == 0:
                    self.pending_pumpkin  = True
                    self.pumpkin_cooldown = FPS * 3   # 3-second cooldown
                if self.char.get("ink_kick") and self.ink_clone_cooldown == 0:
                    self.pending_ink_clone  = True
                    self.ink_clone_cooldown = FPS * 5  # 5-second cooldown
                if self.char.get("pencil_kick") and self.draw_platform_cooldown == 0:
                    self.pending_draw_platform  = True
                    self.draw_platform_cooldown = FPS * 4
                if self.char.get("eraser_kick") and self.erase_cooldown == 0:
                    self.pending_erase  = True
                    self.erase_cooldown = FPS * 2
            elif keys[ctrl['jump']]:
                if self.wall_cling_active:
                    # wall jump: push away from wall and launch upward
                    self.vy = self.char["jump"]
                    self.x += -self.wall_dir * 30
                    self.wall_cling_active = False
                    self.jumps_left = 2 if self.char["double_jump"] else 1
                    self.action = 'jump'
                    self.attacking = False
                elif self.jumps_left > 0:
                    self.vy = self.char["jump"]
                    self.on_ground = False
                    self.jumps_left -= 1
                    self.action = 'jump'
                    self.attacking = False
            elif keys[ctrl['left']]:
                # Double-tap left = dash left
                if not self._prev_left and self.dash_cd == 0 and self.dash_frames == 0:
                    if self.dash_tap_left > 0:
                        self.dash_frames    = 8
                        self.dash_dir       = -1
                        self.dash_cd        = 40
                        self.dash_tap_left  = 0
                        self.action = 'jump'
                    else:
                        self.dash_tap_left = 18
                self.x -= spd
                if self.on_ground and not self.attacking:
                    self.action = 'walk'
                    self.walk_t = (self.walk_t + 0.12) % 1.0
                    self.action_t = self.walk_t
            elif keys[ctrl['right']]:
                # Double-tap right = dash right
                if not self._prev_right and self.dash_cd == 0 and self.dash_frames == 0:
                    if self.dash_tap_right > 0:
                        self.dash_frames    = 8
                        self.dash_dir       = 1
                        self.dash_cd        = 40
                        self.dash_tap_right = 0
                        self.action = 'jump'
                    else:
                        self.dash_tap_right = 18
                self.x += spd
                if self.on_ground and not self.attacking:
                    self.action = 'walk'
                    self.walk_t = (self.walk_t + 0.12) % 1.0
                    self.action_t = self.walk_t
            else:
                if self.on_ground and not self.attacking:
                    self.action = 'idle'

        self._prev_left  = bool(self.controls and keys[self.controls.get('left',  0)])
        self._prev_right = bool(self.controls and keys[self.controls.get('right', 0)])

        if self.attacking and self.action in ('punch', 'kick'):
            self.action_t = min(1.0, self.action_t + self._attack_speed)
            if self.action_t >= 1.0:
                self.action = 'idle'
                self.action_t = 0.0
                self.attacking = False
                self.is_crit = False

    def _start(self, act, spd):
        self.action = act
        self.action_t = 0.0
        self.attacking = True
        self.attack_hit = False
        self._attack_speed = spd

    def check_hit(self, hit_pos, other):
        if hit_pos is None or self.attack_hit:
            return
        if other.ducking and self.action == 'punch':
            return  # punches miss ducking opponents
        hit_cy = other.y - 70 * other.draw_scale
        hit_r  = 58 * other.draw_scale
        dist = math.hypot(hit_pos[0] - other.x, hit_pos[1] - hit_cy)
        if dist < hit_r:
            if self.action == 'punch':
                dmg = self.char["punch_dmg"] + self.punch_boost
                if self.is_crit:
                    dmg += 10
                    other.crit_display_timer = 70
            else:
                dmg = self.char["kick_dmg"] + self.kick_boost
            if other.shield:
                dmg = max(1, int(dmg * 0.5))
            if other.blocking:
                bsk = other.char.get("block", 5)
                perfect_p = bsk * 0.025   # block=10 → 25%, block=1 → 2.5%
                partial_p = bsk * 0.05    # block=10 → 50%, block=1 → 5%
                r = random.random()
                if r < perfect_p:
                    dmg = 0
                elif r < perfect_p + partial_p:
                    dmg = max(1, dmg // 2)
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
            if self.char.get("shock_punch") and self.action == 'punch':
                other.shock_frames = 480   # 8 seconds

    def draw(self, surface):
        _scale = self.draw_scale
        flash = (self.flash_timer % 4) < 2 and self.flash_timer > 0

        if self.angle != 0.0:
            # Draw stickman onto a temp surface, rotate it, blit to screen
            tmp_w = int(320 * _scale)
            tmp_h = int(340 * _scale)
            tmp = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
            cx = tmp_w // 2
            cy = int(tmp_h * 0.72)
            draw_stickman(tmp, cx, cy, self.color, self.facing, self.action, self.action_t,
                          flash=flash, scale=_scale, char_name=self.char["name"])
            rotated = pygame.transform.rotate(tmp, self.angle)
            bx = int(self.x) - rotated.get_width()  // 2
            by = int(self.y) - int(tmp_h * 0.72)    - (rotated.get_height() - tmp_h) // 2
            surface.blit(rotated, (bx, by))
            result = (int(self.x + self.facing * 40 * _scale), int(self.y - 70 * _scale))
        else:
            _sw = int(50 * _scale)
            _sh = int(12 * _scale)
            pygame.draw.ellipse(surface, (0, 0, 0),
                                (int(self.x) - _sw//2, int(self.y) - _sh//2, _sw, _sh))
            result = draw_stickman(surface, self.x, self.y, self.color,
                                   self.facing, self.action, self.action_t, flash=flash, scale=_scale,
                                   char_name=self.char["name"])
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
        if self.shock_frames > 0:
            top_y = int(self.y) - LEG_LEN - BODY_LEN - NECK_LEN - HEAD_R * 2 - 50
            for i, dx in enumerate((-10, 0, 10)):
                pulse = (self.shock_frames // 4 + i) % 2 == 0
                col = (255, 240, 0) if pulse else (200, 160, 0)
                pygame.draw.circle(surface, col, (int(self.x) + dx, top_y), 4)
        if self.boomerang_timer > 0:
            bx = int(self.x + math.cos(self.boomerang_angle) * 85)
            by = int(self.y - 60 + math.sin(self.boomerang_angle) * 55)
            pygame.draw.circle(surface, (180, 100, 20), (bx, by), 9)
            pygame.draw.circle(surface, (230, 160, 60), (bx, by), 6)
            pygame.draw.circle(surface, (255, 200, 100), (bx, by), 3)
        if self.blocking:
            sx = int(self.x) + self.facing * 22
            sy = int(self.y) - LEG_LEN - BODY_LEN // 2
            pygame.draw.polygon(surface, (60, 120, 220),
                                [(sx, sy - 28), (sx + self.facing * 18, sy - 14),
                                 (sx + self.facing * 18, sy + 14), (sx, sy + 28),
                                 (sx - self.facing * 4, sy + 22), (sx - self.facing * 4, sy - 22)])
            pygame.draw.polygon(surface, (140, 190, 255),
                                [(sx, sy - 28), (sx + self.facing * 18, sy - 14),
                                 (sx + self.facing * 18, sy + 14), (sx, sy + 28),
                                 (sx - self.facing * 4, sy + 22), (sx - self.facing * 4, sy - 22)], 2)
        if self.crit_display_timer > 0:
            self.crit_display_timer -= 1
            rise = (70 - self.crit_display_timer) // 2
            top_y = int(self.y) - LEG_LEN - BODY_LEN - NECK_LEN - HEAD_R * 2 - 20 - rise
            crit_surf = font_medium.render("CRIT!", True, (255, 60, 60))
            surface.blit(crit_surf, (int(self.x) - crit_surf.get_width() // 2, top_y))
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
        'mega_hard':        dict(decision_delay=0,  aggression=1.00, jump_chance=0.150, dodge_chance=1.0),
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
        eff_grav = 0.13 if self.char.get("anti_gravity") else GRAVITY
        self.vy += eff_grav
        self.y  += self.vy
        landed = False
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            landed = True
        elif not self.char.get("phase"):
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

        # Floating drift + rotation (Space stage or Astronaut)
        if GRAVITY < 0.3 or self.char.get("anti_gravity"):
            self.angle += self.angle_vel
            self.float_timer -= 1
            if self.float_timer <= 0:
                self.vy        = random.uniform(-5.0, 2.5)
                self.angle_vel = random.uniform(-4.0, 4.0)
                self.float_timer = random.randint(35, 85)
        else:
            self.angle     = 0.0
            self.angle_vel = 0.0

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

        if getattr(self, 'no_attack', False):
            self.ai_attack = None
        if self.ai_attack and can_atk:
            cd = self.punch_cooldown if self.ai_attack == 'punch' else self.kick_cooldown
            if cd == 0:
                self._start(self.ai_attack, 0.07 if self.ai_attack == 'punch' else 0.06)
                if self.ai_attack == 'punch':
                    self.punch_cooldown = FPS
                    self.is_crit = (self.ai_move == self.facing)  # running toward enemy
                else:
                    self.kick_cooldown = FPS * 2
                    if self.char.get("teleport_kick"):
                        self.x = float(random.randint(80, WIDTH - 80))
                        self.flash_timer = 12
                    if self.char.get("boomerang_kick") and self.boomerang_timer == 0 and self.boomerang_cooldown == 0:
                        self.boomerang_timer = 240
                        self.boomerang_angle = 0.0
                    if self.char.get("shoot_kick"):
                        self.pending_ball = True
                    if self.char.get("bazooka_kick") and self.bazooka_cooldown == 0:
                        self.pending_orb      = True
                        self.bazooka_cooldown = FPS * 5
                    if self.char.get("bounce_kick"):
                        self.pending_bounce = True
                    if self.char.get("size_kick"):
                        self._size_state = (self._size_state + 1) % 3
                        self.draw_scale = (1.0, 2.0, 0.55)[self._size_state]
                    if self.char.get("pumpkin_kick") and self.pumpkin_cooldown == 0:
                        self.pending_pumpkin  = True
                        self.pumpkin_cooldown = FPS * 3
                    if self.char.get("ink_kick") and self.ink_clone_cooldown == 0:
                        self.pending_ink_clone  = True
                        self.ink_clone_cooldown = FPS * 5
                    if self.char.get("pencil_kick") and self.draw_platform_cooldown == 0:
                        self.pending_draw_platform  = True
                        self.draw_platform_cooldown = FPS * 4
                    if self.char.get("eraser_kick") and self.erase_cooldown == 0:
                        self.pending_erase  = True
                        self.erase_cooldown = FPS * 2
            self.ai_attack = None
        elif self.ai_move != 0:
            self.x += self.ai_move * self.char["speed"] * self.speed_boost * (0.5 if self.shock_frames > 0 else 1.0)
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


class DrawnPlatform:
    """Temporary platform drawn by the Pencil character."""
    H = 14

    def __init__(self, x, y, w=120):
        self.x      = float(x)
        self.y      = float(y)
        self.w      = w
        self.vx     = 0.0
        self.alive  = True
        self.max_t  = FPS * 9
        self.timer  = self.max_t

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False

    def draw(self, surface, _stage_idx=0):
        if not self.alive:
            return
        rx, ry = int(self.x), int(self.y)
        ratio = self.timer / self.max_t
        alpha = int(255 * ratio)
        col   = (max(20, int(80 * ratio)), max(20, int(60 * ratio)), 10)
        # Sketchy hand-drawn look: a few slightly wobbly lines
        import random as _r; _seed = int(self.x + self.y)
        for off in range(3):
            y_off = off * 3
            wobble = _r.Random(_seed + off).randint(-2, 2)
            pygame.draw.line(surface, col,
                             (rx + off,           ry + y_off + wobble),
                             (rx + self.w - off,  ry + y_off),
                             max(1, 3 - off))
        # Fading timer indicator: thin bright top line
        bright = int(220 * ratio)
        pygame.draw.line(surface, (bright, bright, 20),
                         (rx, ry), (int(rx + self.w * ratio), ry), 2)


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
        if fighter.on_ground and fighter.y >= GROUND_Y - 2 and abs(fighter.x - self.x) < self.W:
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
# Snake grappling hook (Hooker character)
# ---------------------------------------------------------------------------

class SnakeHook:
    SPEED     = 11
    MAX_RANGE = 400

    def __init__(self, ox, oy, tx, ty, owner):
        self.ox    = float(ox)
        self.oy    = float(oy)
        self.x     = float(ox)
        self.y     = float(oy)
        dx, dy     = tx - ox, ty - oy
        dist       = math.hypot(dx, dy) or 1
        self.vx    = dx / dist * self.SPEED
        self.vy    = dy / dist * self.SPEED
        self.owner = owner
        self.alive = True
        self.t     = 0

    def update(self):
        self.t += 1
        if not self.alive:
            return
        self.x += self.vx
        self.y += self.vy
        if math.hypot(self.x - self.ox, self.y - self.oy) > self.MAX_RANGE:
            self.alive = False
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < 35

    def draw(self, surface):
        hx, hy = int(self.x), int(self.y)
        ox, oy = int(self.ox), int(self.oy)
        num_segs = 14
        pts = []
        for i in range(num_segs + 1):
            ti = i / num_segs
            sx = ox + (hx - ox) * ti
            sy = oy + (hy - oy) * ti
            dx = hx - ox
            dy = hy - oy
            length = math.hypot(dx, dy) or 1
            perp_x = -dy / length
            perp_y =  dx / length
            wave = math.sin(ti * math.pi * 4 + self.t * 0.35) * 9 * math.sin(ti * math.pi)
            pts.append((int(sx + perp_x * wave), int(sy + perp_y * wave)))
        for i in range(len(pts) - 1):
            col = (20, 150, 25) if i % 2 == 0 else (55, 200, 50)
            pygame.draw.line(surface, col, pts[i], pts[i + 1], 5)
        # snake head
        pygame.draw.circle(surface, (10, 170, 20), (hx, hy), 8)
        # forked tongue
        tx2 = hx + int(self.vx / self.SPEED * 13)
        ty2 = hy + int(self.vy / self.SPEED * 13)
        pygame.draw.line(surface, (220, 30, 30), (hx, hy), (tx2 - 3, ty2 + 3), 2)
        pygame.draw.line(surface, (220, 30, 30), (hx, hy), (tx2 + 3, ty2 - 3), 2)


# ---------------------------------------------------------------------------
# Pumpkin projectile (Headless Horseman)
# ---------------------------------------------------------------------------

class Pumpkin:
    RADIUS         = 14
    SPEED_X        = 10
    LAUNCH_VY      = -13.0
    EXPLODE_RADIUS = 80
    EXPLODE_DMG    = 30
    EXPLODE_DUR    = 24

    def __init__(self, x, y, facing, owner):
        self.x             = float(x)
        self.y             = float(y)
        self.vx            = self.SPEED_X * facing
        self.vy            = self.LAUNCH_VY
        self.owner         = owner
        self.exploding     = False
        self.explode_timer = 0
        self.damaged       = False
        self.alive         = True

    def update(self):
        if not self.exploding:
            self.vy += GRAVITY
            self.x  += self.vx
            self.y  += self.vy
            if self.x - self.RADIUS < 0:
                self.x  = float(self.RADIUS)
                self.vx =  abs(self.vx) * 0.65
            elif self.x + self.RADIUS > WIDTH:
                self.x  = float(WIDTH - self.RADIUS)
                self.vx = -abs(self.vx) * 0.65
            if self.y + self.RADIUS >= GROUND_Y:
                self.y = float(GROUND_Y - self.RADIUS)
                self._explode()
        else:
            self.explode_timer -= 1
            if self.explode_timer <= 0:
                self.alive = False

    def _explode(self):
        self.exploding     = True
        self.explode_timer = self.EXPLODE_DUR

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 22

    def draw(self, surface):
        if not self.exploding:
            cx, cy = int(self.x), int(self.y)
            r = self.RADIUS
            pygame.draw.circle(surface, (215, 118, 0), (cx, cy), r)
            for ridge in range(-1, 2):
                pygame.draw.arc(surface, (188, 92, 0),
                                (cx + ridge*int(r*.35) - int(r*.22), cy - r, int(r*.44), r*2),
                                math.radians(55), math.radians(125), 1)
            eye_r = max(2, int(r * .22))
            for eye_off in [-int(r*.32), int(r*.32)]:
                pygame.draw.polygon(surface, BLACK, [
                    (cx + eye_off,           cy - int(r*.18)),
                    (cx + eye_off - eye_r,   cy + eye_r // 2),
                    (cx + eye_off + eye_r,   cy + eye_r // 2)])
            mouth_pts = [(cx - int(r*.42) + i*int(r*.21),
                          cy + int(r*.35) + (int(r*.14) if i % 2 == 0 else 0))
                         for i in range(5)]
            pygame.draw.lines(surface, BLACK, False, mouth_pts, max(1, 2))
            pygame.draw.line(surface, (45, 95, 28), (cx, cy - r), (cx, cy - r - 6), 2)
        else:
            prog = 1.0 - self.explode_timer / self.EXPLODE_DUR
            r_ex = int(self.EXPLODE_RADIUS * prog)
            w    = max(1, int(8 * (1 - prog)))
            cx, cy = int(self.x), int(self.y)
            pygame.draw.circle(surface, (220, 120, 0), (cx, cy), r_ex, w)
            if r_ex > 12:
                pygame.draw.circle(surface, (255, 55, 0), (cx, cy), max(1, r_ex - 12), max(1, w - 2))
            # Pumpkin chunk particles
            for angle in range(0, 360, 60):
                a  = math.radians(angle)
                px = cx + int(math.cos(a) * r_ex * .7)
                py = cy + int(math.sin(a) * r_ex * .7)
                pygame.draw.circle(surface, (200, 100, 0), (px, py), max(2, int(4 * (1 - prog))))


# ---------------------------------------------------------------------------
# Jungle snake NPC
# ---------------------------------------------------------------------------

class JungleSnake:
    SPEED        = 2.5
    MAX_HP       = 20
    BITE_DMG     = 3
    BITE_COOLDOWN = 120   # 2 seconds at 60 fps
    BITE_RANGE   = 45

    def __init__(self):
        self.x       = float(random.choice([80, WIDTH - 80]))
        self.y       = float(GROUND_Y)
        self.facing  = 1
        self.bite_cd = 0
        self.hp      = self.MAX_HP
        self.alive   = True
        self.t       = 0

    def update(self, p1, p2):
        if not self.alive:
            return
        self.t += 1
        if self.bite_cd > 0:
            self.bite_cd -= 1

        # Chase closest living player
        d1 = abs(self.x - p1.x) if p1.hp > 0 else 99999
        d2 = abs(self.x - p2.x) if p2.hp > 0 else 99999
        target = p1 if d1 <= d2 else p2

        dx = target.x - self.x
        self.facing = 1 if dx > 0 else -1
        if abs(dx) > self.BITE_RANGE - 5:
            self.x += self.facing * self.SPEED
        self.x = max(30.0, min(float(WIDTH - 30), self.x))

        # Bite when in range
        if (abs(self.x - target.x) < self.BITE_RANGE and
                abs(self.y - target.y) < 70 and self.bite_cd == 0):
            target.hp = max(0, target.hp - self.BITE_DMG)
            target.flash_timer = 6
            self.bite_cd = self.BITE_COOLDOWN

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y) - 8
        # Body segments
        for i in range(7):
            t = i / 6
            bx = cx - self.facing * int(t * 38)
            by = cy + int(math.sin(self.t * 0.14 + t * math.pi) * 5)
            r  = max(3, 9 - i)
            col = (20, 140, 25) if i % 2 == 0 else (35, 170, 35)
            pygame.draw.circle(surface, col, (bx, by), r)
        # Head
        hx = cx + self.facing * 9
        pygame.draw.circle(surface, (10, 160, 20), (hx, cy), 9)
        # Eye
        ex = hx + self.facing * 5
        pygame.draw.circle(surface, (255, 210, 0), (ex, cy - 3), 3)
        pygame.draw.circle(surface, BLACK, (ex + self.facing, cy - 3), 1)
        # Tongue (flickers)
        if self.t % 18 < 11:
            tip = hx + self.facing * 18
            pygame.draw.line(surface, (220, 30, 30), (hx + self.facing * 9, cy), (tip - 2, cy - 3), 2)
            pygame.draw.line(surface, (220, 30, 30), (hx + self.facing * 9, cy), (tip + 2, cy + 3), 2)
        # HP bar
        bw   = 32
        bx_l = cx - bw // 2
        by_t = cy - 22
        pygame.draw.rect(surface, (160, 0, 0),   (bx_l, by_t, bw, 4))
        pygame.draw.rect(surface, (60, 220, 60),  (bx_l, by_t, int(bw * self.hp / self.MAX_HP), 4))


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
    """Returns ('1p', difficulty), '2p', 'survival_1p', or 'survival_2p'."""
    selected = 0   # 0=1P, 1=2P, 2=SURVIVAL
    difficulty_idx = 1
    difficulties = ['easy', 'medium', 'hard', 'super_hard', 'super_super_hard', 'mega_hard']
    diff_colors  = [GREEN, YELLOW, RED, PURPLE, CYAN, ORANGE]
    scroll_offset = 0
    VISIBLE = 3
    survival_players = 0   # 0=1P survival, 1=2P survival
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
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % 3
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % 3
                if selected == 0:   # 1P: difficulty picker
                    if event.key in (pygame.K_UP, pygame.K_w):
                        difficulty_idx = (difficulty_idx - 1) % len(difficulties)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        difficulty_idx = (difficulty_idx + 1) % len(difficulties)
                    if difficulty_idx < scroll_offset:
                        scroll_offset = difficulty_idx
                    elif difficulty_idx >= scroll_offset + VISIBLE:
                        scroll_offset = difficulty_idx - VISIBLE + 1
                if selected == 2:   # Survival: toggle 1P/2P
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                        survival_players = 1 - survival_players
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected == 0:
                        return ('1p', difficulties[difficulty_idx])
                    elif selected == 1:
                        return '2p'
                    else:
                        return 'survival_2p' if survival_players else 'survival_1p'

        screen.fill(DARK)
        title = font_large.render("STICKMAN FIGHTER", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        card_w, card_h = 170, 240
        cards = [
            (WIDTH//2 - 285, "1 PLAYER",  "vs CPU",    BLUE),
            (WIDTH//2 -  85, "2 PLAYERS", "local",     ORANGE),
            (WIDTH//2 + 115, "SURVIVAL",  "endless",   GREEN),
        ]
        for ci, (cx, top, sub, col) in enumerate(cards):
            border = WHITE if ci == selected else GRAY
            pygame.draw.rect(screen, (50,50,50), (cx, 140, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, border,     (cx, 140, card_w, card_h), 3, border_radius=12)
            lbl = font_medium.render(top, True, col)
            screen.blit(lbl, (cx + card_w//2 - lbl.get_width()//2, 150))
            sl = font_small.render(sub, True, GRAY)
            screen.blit(sl, (cx + card_w//2 - sl.get_width()//2, 190))
            draw_stickman(screen, cx + card_w//2 - 25, 140 + card_h - 30, BLUE, 1, 'walk', preview_t)
            draw_stickman(screen, cx + card_w//2 + 25, 140 + card_h - 30, RED, -1, 'idle', 0.0)
            if ci == selected:
                sel_txt = font_tiny.render("ENTER / SPACE to select", True, WHITE)
                screen.blit(sel_txt, (cx + card_w//2 - sel_txt.get_width()//2, 390))

        # Difficulty picker (1P mode)
        if selected == 0:
            diff_lbl = font_small.render("Difficulty:", True, WHITE)
            screen.blit(diff_lbl, (WIDTH//2 - 285, 400))
            list_x, list_y, row_h = WIDTH//2 - 275, 428, 30
            if scroll_offset > 0:
                screen.blit(font_small.render("▲", True, GRAY), (list_x, list_y - 22))
            for row, di in enumerate(range(scroll_offset, scroll_offset + VISIBLE)):
                if di >= len(difficulties): break
                dname, dcol = difficulties[di], diff_colors[di]
                marker = "► " if di == difficulty_idx else "  "
                dt = font_small.render(f"{marker}{dname.replace('_', ' ').capitalize()}", True,
                                       dcol if di == difficulty_idx else GRAY)
                screen.blit(dt, (list_x, list_y + row * row_h))
            if scroll_offset + VISIBLE < len(difficulties):
                screen.blit(font_small.render("▼", True, GRAY), (list_x, list_y + VISIBLE * row_h + 2))
            screen.blit(font_tiny.render("↑/↓ or W/S to scroll", True, GRAY),
                        (list_x, list_y + VISIBLE * row_h + 22))

        # Survival 1P/2P toggle
        if selected == 2:
            opts = ["1 PLAYER", "2 PLAYERS"]
            for oi, opt in enumerate(opts):
                col = WHITE if oi == survival_players else GRAY
                ot = font_small.render(("► " if oi == survival_players else "  ") + opt, True, col)
                screen.blit(ot, (WIDTH//2 + 125, 405 + oi * 30))
            screen.blit(font_tiny.render("W/S to switch", True, GRAY), (WIDTH//2 + 125, 468))

        nav = font_tiny.render("◄ ► to switch mode", True, GRAY)
        screen.blit(nav, (WIDTH//2 - nav.get_width()//2, HEIGHT - 24))
        pygame.display.flip()


# ---------------------------------------------------------------------------
# Computer bug NPC
# ---------------------------------------------------------------------------

class ComputerBug:
    SPEED        = 3.8
    MAX_HP       = 15
    BITE_DMG     = 4
    BITE_COOLDOWN = 90   # 1.5 s
    BITE_RANGE   = 42

    def __init__(self):
        self.x         = float(random.choice([80, WIDTH - 80]))
        self.y         = float(GROUND_Y)
        self.vx        = random.choice([-1, 1]) * self.SPEED
        self.hp        = self.MAX_HP
        self.bite_timer = 0
        self.leg_t     = 0.0
        self.alive     = True

    def update(self, target):
        if not self.alive:
            return
        self.leg_t += 0.2
        if target:
            self.vx = self.SPEED if target.x > self.x else -self.SPEED
        self.x += self.vx
        if self.x < 30:          self.x = 30;          self.vx =  abs(self.vx)
        if self.x > WIDTH - 30:  self.x = WIDTH - 30;  self.vx = -abs(self.vx)
        if self.bite_timer > 0:
            self.bite_timer -= 1
        if (target and self.bite_timer == 0
                and abs(target.x - self.x) < self.BITE_RANGE
                and abs(target.y - self.y) < 60):
            target.hp = max(0, target.hp - self.BITE_DMG)
            target.flash_timer = 8
            self.bite_timer = self.BITE_COOLDOWN

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y) - 9
        facing_x = 1 if self.vx >= 0 else -1
        # Abdomen (rear)
        pygame.draw.ellipse(surface, (0, 180, 40),  (cx - 14, cy - 5, 20, 12))
        pygame.draw.ellipse(surface, (0, 220, 60),  (cx - 14, cy - 5, 20, 12), 1)
        # Thorax
        pygame.draw.ellipse(surface, (0, 160, 35),  (cx - 6, cy - 6, 15, 13))
        # Head
        pygame.draw.circle(surface, (0, 200, 50),   (cx + facing_x * 12, cy), 6)
        # Eyes (glowing red — bugs have red eyes)
        pygame.draw.circle(surface, (255, 30, 30),  (cx + facing_x * 14, cy - 2), 2)
        pygame.draw.circle(surface, (255, 30, 30),  (cx + facing_x * 14, cy + 2), 2)
        # 6 legs with walk animation
        for i in range(3):
            wave = int(math.sin(self.leg_t + i * 1.1) * 6)
            ly = cy - 3 + i * 4
            pygame.draw.line(surface, (0, 140, 30),
                             (cx - 3, ly), (cx - 16, ly + wave + 7), 1)
            pygame.draw.line(surface, (0, 140, 30),
                             (cx + 3, ly), (cx + 16, ly - wave + 7), 1)
        # Antennae
        hx = cx + facing_x * 17
        pygame.draw.line(surface, (0, 180, 40), (hx, cy - 4),
                         (hx + facing_x * 8,  cy - 13), 1)
        pygame.draw.line(surface, (0, 180, 40), (hx, cy - 4),
                         (hx + facing_x * 10, cy - 11), 1)
        # HP bar
        bw = 26
        bxl = cx - bw // 2
        byt = cy - 22
        pygame.draw.rect(surface, (40, 40, 40),  (bxl, byt, bw, 3))
        pygame.draw.rect(surface, (0, 220, 60),
                         (bxl, byt, int(bw * self.hp / self.MAX_HP), 3))


# ---------------------------------------------------------------------------
# Mouse platform (Computer stage)
# ---------------------------------------------------------------------------

class MousePlatform:
    W        = 115
    H        = 16    # surface height (same as Platform.H)
    SPEED    = 1.6

    def __init__(self, x, y, travel=380):
        self.x       = float(x)
        self.y       = float(y)
        self.w       = self.W
        self.start_x = float(x)
        self.travel  = travel
        self.vx      = self.SPEED

    def update(self):
        self.x += self.vx
        if self.x > self.start_x + self.travel:
            self.x  = self.start_x + self.travel
            self.vx = -self.SPEED
        elif self.x < self.start_x:
            self.x  = self.start_x
            self.vx =  self.SPEED

    def draw(self, surface, _stage_idx=0):
        rx, ry = int(self.x), int(self.y)
        # Draw as a large cursor arrow pointer (NW-pointing)
        # Tip at top-left; flat base at ry (platform surface)
        H = 52  # cursor height
        tx, ty = rx + 8, ry - H   # tip position
        # Classic cursor polygon: tip → left-edge down → inner notch → handle bottom → handle top → upper-right
        pts = [
            (tx,          ty),          # tip
            (tx,          ry - 6),      # left edge bottom
            (tx + 18,     ry - 22),     # inner notch
            (tx + 24,     ry),          # handle bottom-left (platform surface)
            (tx + 38,     ry),          # handle bottom-right
            (tx + 32,     ry - 26),     # inner notch right
            (tx + H - 4,  ty),          # upper-right
        ]
        pts = [(int(x), int(y)) for x, y in pts]
        pygame.draw.polygon(surface, (248, 248, 248), pts)
        pygame.draw.polygon(surface, (10, 10, 10), pts, 2)


# ---------------------------------------------------------------------------
# Character select screen
# ---------------------------------------------------------------------------

def character_select(vs_ai=False):
    """Returns (p1_idx, p2_idx). P2 is random if vs_ai."""
    n     = len(CHARACTERS)
    COLS  = 7
    ROWS  = (n + COLS - 1) // COLS

    # Grid occupies left ~60% of screen
    GX, GY   = 8,  68
    GW, GH   = 540, HEIGHT - GY - 28
    CW       = GW // COLS
    CH       = GH // ROWS

    # Detail panel on the right
    PX       = GX + GW + 10
    PW       = WIDTH - PX - 8
    PY, PH   = GY, GH

    def move(idx, dr, dc):
        r, c = divmod(idx, COLS)
        if dc:
            c = (c + dc) % COLS
            ni = r * COLS + c
            return min(ni, n - 1)
        else:
            r = (r + dr) % ROWS
            ni = r * COLS + c
            return min(ni, n - 1)

    p1_idx, p2_idx = 0, 1
    p1_ready = False
    p2_ready = vs_ai
    preview_t = 0.0
    flash_t   = 0   # for ready flash

    while True:
        clock.tick(FPS)
        preview_t = (preview_t + 0.02) % 1.0
        flash_t   = (flash_t + 1) % 40

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return None, None
                # P1 navigation (WASD or arrows while P1 not ready)
                if not p1_ready:
                    if event.key in (pygame.K_a, pygame.K_LEFT):  p1_idx = move(p1_idx, 0, -1)
                    if event.key in (pygame.K_d, pygame.K_RIGHT): p1_idx = move(p1_idx, 0,  1)
                    if event.key in (pygame.K_w, pygame.K_UP):    p1_idx = move(p1_idx, -1, 0)
                    if event.key in (pygame.K_s, pygame.K_DOWN):  p1_idx = move(p1_idx,  1, 0)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
                        p1_ready = True
                        if vs_ai:
                            p2_idx = random.randint(0, n - 1)
                # P2 navigation (arrows only, after P1 locked in)
                elif not vs_ai and not p2_ready:
                    if event.key == pygame.K_LEFT:  p2_idx = move(p2_idx, 0, -1)
                    if event.key == pygame.K_RIGHT: p2_idx = move(p2_idx, 0,  1)
                    if event.key == pygame.K_UP:    p2_idx = move(p2_idx, -1, 0)
                    if event.key == pygame.K_DOWN:  p2_idx = move(p2_idx,  1, 0)
                    if event.key in (pygame.K_RETURN, pygame.K_k):
                        p2_ready = True

        if p1_ready and p2_ready:
            return p1_idx, p2_idx

        # Whose detail to show: the active picker
        detail_idx = p2_idx if (p1_ready and not p2_ready) else p1_idx
        detail_ch  = CHARACTERS[detail_idx]
        active_col = ORANGE if (p1_ready and not p2_ready) else BLUE

        # ── Background ──────────────────────────────────────────────────────
        screen.fill((18, 18, 28))

        # Title bar
        pygame.draw.rect(screen, (30, 30, 48), (0, 0, WIDTH, GY - 2))
        title = font_medium.render("SELECT YOUR FIGHTER", True, YELLOW)
        screen.blit(title, (GX, 10))
        if not vs_ai:
            phase = "P1 choosing" if not p1_ready else "P2 choosing"
            phase_col = BLUE if not p1_ready else ORANGE
            ps = font_small.render(phase, True, phase_col)
            screen.blit(ps, (WIDTH - ps.get_width() - 10, 12))

        # ── Character grid ───────────────────────────────────────────────────
        for i, ch in enumerate(CHARACTERS):
            r, c  = divmod(i, COLS)
            cx    = GX + c * CW
            cy    = GY + r * CH
            color = ch["color"]

            # Tinted background from character color
            bg_col = (max(10, color[0]//5), max(10, color[1]//5), max(10, color[2]//5))
            pygame.draw.rect(screen, bg_col, (cx+2, cy+2, CW-4, CH-4), border_radius=6)

            # Selection highlights
            is_p1 = (i == p1_idx)
            is_p2 = (i == p2_idx) and not vs_ai

            if is_p1 and is_p2:
                bord, bw = (180, 100, 255), 3
            elif is_p1:
                bord, bw = BLUE,   3
            elif is_p2:
                bord, bw = ORANGE, 3
            else:
                bord, bw = (55, 55, 70), 1
            pygame.draw.rect(screen, bord, (cx+2, cy+2, CW-4, CH-4), bw, border_radius=6)

            # Character name (truncate if needed)
            name_str = ch["name"] if len(ch["name"]) <= 10 else ch["name"][:9] + "."
            nm = font_tiny.render(name_str, True, color if (is_p1 or is_p2) else (160, 160, 160))
            screen.blit(nm, (cx + CW//2 - nm.get_width()//2, cy + CH//2 - 6))

            # Ready badge
            if is_p1 and p1_ready:
                pygame.draw.circle(screen, GREEN, (cx + CW - 8, cy + 8), 5)
            if is_p2 and p2_ready:
                pygame.draw.circle(screen, GREEN, (cx + 8, cy + 8), 5)

            # Player cursor dot(s)
            if is_p1 and not p1_ready:
                pygame.draw.circle(screen, BLUE, (cx + CW - 8, cy + 8), 4)
            if is_p2 and not p2_ready:
                pygame.draw.circle(screen, ORANGE, (cx + 8, cy + 8), 4)

        # Grid border
        pygame.draw.rect(screen, (60, 60, 90), (GX, GY, GW, GH), 1, border_radius=4)

        # ── Detail panel ─────────────────────────────────────────────────────
        pygame.draw.rect(screen, (25, 25, 40),    (PX, PY, PW, PH), border_radius=10)
        pygame.draw.rect(screen, active_col,      (PX, PY, PW, PH), 2, border_radius=10)

        # Large animated stickman
        sm_y = PY + 155
        draw_stickman(screen, PX + PW//2, sm_y, detail_ch["color"], 1, 'walk', preview_t, scale=1.15,
                      char_name=detail_ch["name"])

        # Character name
        nm_big = font_medium.render(detail_ch["name"], True, detail_ch["color"])
        screen.blit(nm_big, (PX + PW//2 - nm_big.get_width()//2, PY + 8))

        # Description (word-wrap)
        words, line, desc_lines = detail_ch["desc"].split(), "", []
        for w in words:
            test = (line + " " + w).strip()
            if font_tiny.size(test)[0] > PW - 16:
                desc_lines.append(line); line = w
            else:
                line = test
        if line: desc_lines.append(line)
        for li, dl in enumerate(desc_lines):
            ds = font_tiny.render(dl, True, YELLOW)
            screen.blit(ds, (PX + PW//2 - ds.get_width()//2, PY + 34 + li * 15))

        # Stat bars
        bar_x  = PX + 10
        bar_y  = PY + 172
        bar_bw = PW - 20
        bar_h  = 14
        bar_gap = 23
        for si, (lbl, val, mx, col) in enumerate([
            ("HP",    detail_ch["max_hp"],              400, (60,  210,  80)),
            ("SPD",   detail_ch["speed"],                10, (80,  170, 255)),
            ("PUNCH", detail_ch["punch_dmg"],            30, (255, 120,  50)),
            ("KICK",  detail_ch["kick_dmg"],             30, (255,  60, 180)),
            ("BLOCK", detail_ch.get("block", 5),         10, (200, 200,  60)),
        ]):
            by  = bar_y + si * bar_gap
            lbs = font_tiny.render(lbl, True, (180, 180, 180))
            screen.blit(lbs, (bar_x, by))
            bx2 = bar_x + 48
            bw2 = bar_bw - 48
            pygame.draw.rect(screen, (50, 50, 65), (bx2, by, bw2, bar_h), border_radius=3)
            fw  = int(bw2 * min(1.0, val / mx))
            if fw > 0:
                pygame.draw.rect(screen, col, (bx2, by, fw, bar_h), border_radius=3)
            pygame.draw.rect(screen, (90, 90, 110), (bx2, by, bw2, bar_h), 1, border_radius=3)
            vs2 = font_tiny.render(str(val), True, WHITE)
            screen.blit(vs2, (bx2 + bw2 + 5, by))

        # Badges row
        badge_y = bar_y + 5 * bar_gap + 6
        badges  = []
        if detail_ch.get("double_jump"):    badges.append(("2x JUMP",      CYAN))
        if detail_ch.get("giant"):          badges.append(("GIANT",         GREEN))
        if detail_ch.get("tiny"):           badges.append(("TINY",          (220, 200, 180)))
        if detail_ch.get("phase"):          badges.append(("PHASES WALLS",  (200, 200, 255)))
        if detail_ch.get("vampire"):        badges.append(("VAMPIRE",       (200, 0, 80)))
        if detail_ch.get("anti_gravity"):   badges.append(("ANTI-GRAVITY",  (180, 220, 255)))
        if detail_ch.get("wall_cling"):     badges.append(("WALL CLING",    ORANGE))
        if detail_ch.get("regen"):          badges.append(("REGEN",         (120, 255, 120)))
        if detail_ch.get("fire_punch"):     badges.append(("FIRE PUNCH",    (255, 100, 20)))
        if detail_ch.get("freeze_kick"):    badges.append(("FREEZE KICK",   (120, 200, 255)))
        if detail_ch.get("shock_punch"):    badges.append(("SHOCK PUNCH",   YELLOW))
        if detail_ch.get("magnet"):         badges.append(("MAGNET",        PURPLE))
        if detail_ch.get("teleport_kick"):  badges.append(("TELEPORT KICK", (220, 80, 255)))
        if detail_ch.get("random_stats"):   badges.append(("RANDOM STATS",  GRAY))
        if detail_ch.get("boomerang_kick"): badges.append(("BOOMERANG",     (200, 130, 50)))
        if detail_ch.get("shoot_kick"):     badges.append(("SHOOTS BALLS",  (60, 200, 80)))
        if detail_ch.get("bazooka_kick"):   badges.append(("BAZOOKA",       (220, 60, 60)))
        if detail_ch.get("bounce_kick"):    badges.append(("BOUNCE BALL",   (255, 80, 200)))
        if detail_ch.get("size_kick"):      badges.append(("SIZE SHIFT",    (80, 200, 220)))
        if detail_ch.get("grapple_kick"):   badges.append(("SNAKE HOOK",    (40, 200, 60)))
        if detail_ch.get("pumpkin_kick"):   badges.append(("PUMPKIN BOMB",  (215, 118, 0)))
        if detail_ch.get("contact_dmg"):    badges.append(("POISON TOUCH",  (100, 220, 60)))
        bx_off = PX + 8
        for btxt, bcol in badges:
            bs = font_tiny.render(btxt, True, bcol)
            if bx_off + bs.get_width() + 10 > PX + PW - 4:
                bx_off  = PX + 8
                badge_y += 18
            pygame.draw.rect(screen, (40, 40, 60), (bx_off - 2, badge_y - 1, bs.get_width() + 8, 16), border_radius=3)
            screen.blit(bs, (bx_off + 2, badge_y))
            bx_off += bs.get_width() + 14

        # Controls hint at bottom of panel
        if not p1_ready:
            hint = "WASD / Arrows  move       F / ENTER  confirm"
            hcol = BLUE
        elif not vs_ai and not p2_ready:
            hint = "Arrows  move       K / ENTER  confirm"
            hcol = ORANGE
        else:
            hint, hcol = "", WHITE
        if hint:
            hs = font_tiny.render(hint, True, hcol)
            screen.blit(hs, (PX + PW//2 - hs.get_width()//2, PY + PH - 18))

        # Ready flash on panel border
        if p1_ready and p2_ready:
            if flash_t < 20:
                pygame.draw.rect(screen, GREEN, (PX, PY, PW, PH), 3, border_radius=10)

        esc = font_tiny.render("ESC — back to menu", True, GRAY)
        screen.blit(esc, (GX + 4, HEIGHT - 22))

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Fight loop
# ---------------------------------------------------------------------------

def run_fight(p1_idx, p2_idx, vs_ai=False, ai_difficulty='medium', stage_idx=0):
    global GRAVITY
    _stage_name = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = GRAVITY
    if _stage_name == "Space":
        GRAVITY = 0.13   # floaty anti-gravity

    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g, duck=pygame.K_s, block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l, duck=pygame.K_DOWN, block=pygame.K_o)

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
    balls        = []   # active Projectile objects
    orbs         = []   # active Orb objects (bazooka)
    bounce_balls = []   # active BouncingBall objects (Pinball)
    hooks        = []   # active SnakeHook objects (Hooker)
    pumpkins     = []   # active Pumpkin objects (Headless Horseman)
    spawn_timer  = 300   # first spawn after 5 seconds
    is_jungle    = stage_data["name"] == "Jungle"
    is_computer  = stage_data["name"] == "Computer"
    jungle_snakes      = []
    snake_spawn_timer  = 180   # first snake after 3 seconds
    computer_bugs      = []
    bug_spawn_timer    = 150
    if is_computer:
        platforms.append(MousePlatform(80, GROUND_Y - 62, travel=720))

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        GRAVITY = _orig_gravity; return 'rematch'
                    if event.key == pygame.K_c:
                        GRAVITY = _orig_gravity; return 'select'
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        GRAVITY = _orig_gravity
                        pygame.quit(); sys.exit()
                else:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        GRAVITY = _orig_gravity; return 'select'

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

            # Boomerang collision
            for thrower, victim in [(p1, p2), (p2, p1)]:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    if math.hypot(bx - victim.x, by - (victim.y - 60)) < 48:
                        victim.hp = max(0, victim.hp - 8)
                        victim.flash_timer = 6
                        thrower.boomerang_hit_cd = 30   # 0.5s between hits

            keys = pygame.key.get_pressed()
            p1.update(keys, p2, platforms)
            p2.update(keys, p1, platforms)

            # Spawn balls from shoot_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing * 30,
                                            shooter.y - 60, shooter.facing, shooter))

            # Update balls and check collisions
            for b in balls:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8
                        b.alive = False
            balls = [b for b in balls if b.alive]

            # Spawn orbs from bazooka_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing * 30,
                                    shooter.y - 60, shooter.facing, shooter))

            # Update orbs and apply explosion damage
            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    victim = p2 if o.owner is p1 else p1
                    if math.hypot(o.x - victim.x, o.y - (victim.y - 60)) < o.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - o.EXPLODE_DMG)
                        victim.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            # Spawn bouncing balls from bounce_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing * 30,
                                                     shooter.y - 60, shooter.facing, shooter))

            # Update bouncing balls and check collisions
            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    victim = p2 if bb.owner is p1 else p1
                    if bb.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8
                        bb.hit_cd = BouncingBall.HIT_CD
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            # Spawn snake hooks from grapple_kick (Hooker)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_hook:
                    shooter.pending_hook = False
                    hooks.append(SnakeHook(
                        shooter.x + shooter.facing * 20, shooter.y - 60,
                        victim.x, victim.y - 60, shooter))

            # Update snake hooks and pull on hit
            for h in hooks:
                h.update()
                if h.alive:
                    victim = p2 if h.owner is p1 else p1
                    if h.collides(victim):
                        pull_dir = 1 if h.owner.x > victim.x else -1
                        victim.knockback = pull_dir * 22
                        victim.hp = max(0, victim.hp - 6)
                        victim.flash_timer = 8
                        h.alive = False
            hooks = [h for h in hooks if h.alive]

            # Pumpkins (Headless Horseman)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(
                        shooter.x + shooter.facing * 24, shooter.y - 80,
                        shooter.facing, shooter))
            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    victim = p2 if pk.owner is p1 else p1
                    if math.hypot(pk.x - victim.x, pk.y - (victim.y - 60)) < pk.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - pk.EXPLODE_DMG)
                        victim.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    victim = p2 if pk.owner is p1 else p1
                    if pk.collides(victim):
                        pk._explode()
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Ink Brush clones
            for shooter, foe in [(p1, p2), (p2, p1)]:
                if shooter.pending_ink_clone:
                    shooter.pending_ink_clone = False
                    cf = AIFighter(shooter.x + shooter.facing * 55, shooter.char, -shooter.facing, 'medium')
                    cf.hp = max(1, shooter.hp)
                    cf.color = shooter.color
                    cf.no_attack = True
                    clones.append({'fighter': cf, 'timer': FPS * 8, 'target': foe, 'ink': True})

            # Pencil drawn platforms + Eraser
            for fighter in (p1, p2):
                if fighter.pending_draw_platform:
                    fighter.pending_draw_platform = False
                    platforms.append(DrawnPlatform(fighter.x - 60, fighter.y, w=120))
                if fighter.pending_erase:
                    fighter.pending_erase = False
                    fighter.flash_timer = 8
                    platforms = [p for p in platforms
                                 if not (isinstance(p, DrawnPlatform)
                                         and abs((p.x + p.w / 2) - fighter.x) < 220)]
            # Update DrawnPlatforms and remove expired ones
            for p in platforms:
                if isinstance(p, DrawnPlatform):
                    p.update()
            platforms = [p for p in platforms if not (isinstance(p, DrawnPlatform) and not p.alive)]

            # Jungle snakes
            if is_jungle:
                snake_spawn_timer -= 1
                if snake_spawn_timer <= 0 and len(jungle_snakes) < 4:
                    jungle_snakes.append(JungleSnake())
                    snake_spawn_timer = random.randint(300, 480)
                for sn in jungle_snakes:
                    sn.update(p1, p2)
                jungle_snakes = [sn for sn in jungle_snakes if sn.alive]

            # Computer bugs
            if is_computer:
                bug_spawn_timer -= 1
                if bug_spawn_timer <= 0 and len(computer_bugs) < 5:
                    computer_bugs.append(ComputerBug())
                    bug_spawn_timer = random.randint(200, 360)
                for b in computer_bugs:
                    target = min([p1, p2], key=lambda p: abs(p.x - b.x))
                    b.update(target)
                computer_bugs = [b for b in computer_bugs if b.alive]

            timer -= 1
            if timer <= 0 or p1.hp <= 0 or p2.hp <= 0:
                game_over = True
                winner = p1 if p1.hp >= p2.hp else p2

            # Spawn powerups
            spawn_timer -= 1
            if spawn_timer <= 0 and len(powerups) < 3:
                powerups.append(Powerup())
                spawn_timer = random.randint(480, 720)   # 8-12 seconds

            # Magician attraction: pull all powerups slowly toward Magician fighters
            for f in (p1, p2):
                if f.char.get("magnet"):
                    for pu in powerups:
                        if not pu.picked_up:
                            dx = f.x - pu.x
                            dy = (f.y - 60) - pu.y
                            dist = math.hypot(dx, dy) or 1
                            speed = min(2.5, 300 / dist)   # faster when closer
                            pu.x += (dx / dist) * speed
                            pu.y += (dy / dist) * speed

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
        for b in balls:
            b.draw(screen)
        for o in orbs:
            o.draw(screen)
        for bb in bounce_balls:
            bb.draw(screen)
        for h in hooks:
            h.draw(screen)
        for pk in pumpkins:
            pk.draw(screen)
        for sn in jungle_snakes:
            sn.draw(screen)
        for b in computer_bugs:
            b.draw(screen)
        # Draw magnet beams from powerups to any Magician fighter
        for f in (p1, p2):
            if f.char.get("magnet"):
                for pu in powerups:
                    if not pu.picked_up:
                        pygame.draw.line(screen, (140, 60, 220),
                                         (int(pu.x), int(pu.y)),
                                         (int(f.x), int(f.y - 60)), 1)
        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen)
        clone_draws = [(cd, cd['fighter'].draw(screen)) for cd in clones]

        if not game_over:
            if p1.attacking and not p1.attack_hit:
                p1.check_hit(p1_hit, p2)
            if p2.attacking and not p2.attack_hit:
                p2.check_hit(p2_hit, p1)
            # Fighter attacks hit jungle snakes
            for attacker, hit_pos in [(p1, p1_hit), (p2, p2_hit)]:
                if attacker.attacking and hit_pos:
                    for sn in jungle_snakes:
                        if math.hypot(hit_pos[0] - sn.x, hit_pos[1] - (sn.y - 8)) < 44:
                            dmg = (attacker.char["punch_dmg"] if attacker.action == 'punch'
                                   else attacker.char["kick_dmg"])
                            sn.take_damage(dmg)
            # Fighter attacks hit computer bugs
            if is_computer:
                for attacker, hit_pos in [(p1, p1_hit), (p2, p2_hit)]:
                    if attacker.attacking and hit_pos:
                        for b in computer_bugs:
                            if math.hypot(hit_pos[0]-b.x, hit_pos[1]-(b.y-8)) < 40:
                                dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                       else attacker.char["kick_dmg"])
                                b.take_damage(dmg)
            for cd, cf_hit in clone_draws:
                cf = cd['fighter']
                # clone attacks its target (ink clones can't attack)
                if not cd.get('ink') and cf.attacking and not cf.attack_hit:
                    cf.check_hit(cf_hit, cd['target'])
                # opponent can hit the clone
                if cd['target'] is p2:
                    if p2.attacking and not p2.attack_hit:
                        p2.check_hit(p2_hit, cf)
                else:
                    if p1.attacking and not p1.attack_hit:
                        p1.check_hit(p1_hit, cf)
            # draw clone timer above each clone (ink clones get no label)
            for cd in clones:
                if cd.get('ink'):
                    continue
                cf = cd['fighter']
                secs = cd['timer'] // FPS
                tag = font_tiny.render(f"2x [{secs}s]", True, (255, 80, 200))
                screen.blit(tag, (int(cf.x) - tag.get_width()//2,
                                  int(cf.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        # Draw AI tag above CPU fighter
        if vs_ai:
            diff_col = {
                'easy': GREEN, 'medium': YELLOW, 'hard': RED,
                'super_hard': PURPLE, 'super_super_hard': CYAN, 'mega_hard': ORANGE
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
            hint  = font_tiny.render("WASD + F punch  G kick  S duck  R block", True, (140, 140, 140))
        else:
            hint  = font_tiny.render(
                "P1: WASD F punch G kick S duck R block        P2: Arrows K punch L kick ↓ duck O block",
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
# Survival mode
# ---------------------------------------------------------------------------

def run_survival(p1_idx, p2_idx=None, two_player=False, stage_idx=0):
    global GRAVITY
    _stage_name   = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = GRAVITY
    if _stage_name == "Space":
        GRAVITY = 0.13

    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g, duck=pygame.K_s, block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l, duck=pygame.K_DOWN, block=pygame.K_o)

    p1      = Fighter(250, CHARACTERS[p1_idx],  1, P1_CTRL)
    p2      = Fighter(650, CHARACTERS[p2_idx], -1, P2_CTRL) if two_player else None
    players = [p1, p2] if two_player else [p1]

    stage_data  = STAGES[stage_idx % len(STAGES)]
    platforms   = [Platform(*p) for p in stage_data["platforms"]]
    springs     = [Spring(*s)   for s in stage_data["springs"]]
    is_jungle   = stage_data["name"] == "Jungle"
    is_computer = stage_data["name"] == "Computer"
    if is_computer:
        platforms.append(MousePlatform(80, GROUND_Y - 62, travel=720))

    enemies           = []
    death_pops        = []   # [{x,y,color,t}] death burst particles
    balls             = []   # Projectile (shoot_kick)
    orbs              = []   # Orb (bazooka_kick)
    bounce_balls      = []   # BouncingBall (bounce_kick)
    hooks             = []   # SnakeHook (grapple_kick)
    pumpkins          = []   # Pumpkin (pumpkin_kick)
    ink_clones        = []   # Ink Brush clones
    en_balls          = []
    en_orbs           = []
    en_bounce_balls   = []
    en_pumpkins       = []
    powerups          = []
    jungle_snakes     = []
    computer_bugs     = []
    bug_spawn_timer   = 150
    survival_timer    = 0
    enemies_killed    = 0
    enemy_spawn_timer = 180
    snake_spawn_timer = 180
    powerup_timer     = 480
    game_over         = False

    def wave_info():
        s = survival_timer // FPS
        if   s <  30: return 1, 'easy'
        elif s <  60: return 2, 'easy'
        elif s <  90: return 2, 'medium'
        elif s < 120: return 3, 'medium'
        elif s < 180: return 3, 'hard'
        elif s < 240: return 4, 'hard'
        else:         return 4, 'super_hard'

    def _draw_survival_hud():
        # HP bars for players
        bw = 240
        pygame.draw.rect(screen, (60,60,60), (10, 10, bw, 20), border_radius=4)
        fw = int(bw * max(0, p1.hp / p1.max_hp))
        pygame.draw.rect(screen, p1.char["color"], (10, 10, fw, 20), border_radius=4)
        pygame.draw.rect(screen, WHITE, (10, 10, bw, 20), 2, border_radius=4)
        ht = font_tiny.render(f"P1 {p1.char['name']}  {max(0,p1.hp)}/{p1.max_hp}", True, WHITE)
        screen.blit(ht, (14, 13))
        if two_player:
            pygame.draw.rect(screen, (60,60,60), (WIDTH-bw-10, 10, bw, 20), border_radius=4)
            fw2 = int(bw * max(0, p2.hp / p2.max_hp))
            pygame.draw.rect(screen, p2.char["color"], (WIDTH-bw-10+bw-fw2, 10, fw2, 20), border_radius=4)
            pygame.draw.rect(screen, WHITE, (WIDTH-bw-10, 10, bw, 20), 2, border_radius=4)
            ht2 = font_tiny.render(f"{max(0,p2.hp)}/{p2.max_hp}  P2 {p2.char['name']}", True, WHITE)
            screen.blit(ht2, (WIDTH-bw-10 + bw - ht2.get_width() - 4, 13))
        # Timer (counting up)
        elapsed = survival_timer // FPS
        mins, secs = divmod(elapsed, 60)
        t_surf = font_medium.render(f"{mins}:{secs:02d}", True, YELLOW)
        screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 6))
        # Kills
        k_surf = font_tiny.render(f"Kills: {enemies_killed}", True, (200, 200, 200))
        screen.blit(k_surf, (WIDTH//2 - k_surf.get_width()//2, 38))
        # Wave
        max_en, diff = wave_info()
        w_surf = font_tiny.render(f"Wave difficulty: {diff.replace('_',' ')}  |  Max enemies: {max_en}", True, GRAY)
        screen.blit(w_surf, (WIDTH//2 - w_surf.get_width()//2, HEIGHT - 22))

    def _draw_game_over():
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))
        go = font_large.render("GAME OVER", True, RED)
        screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//3 - 40))
        elapsed = survival_timer // FPS
        mins, secs = divmod(elapsed, 60)
        ts = font_medium.render(f"Survived: {mins}:{secs:02d}", True, WHITE)
        screen.blit(ts, (WIDTH//2 - ts.get_width()//2, HEIGHT//3 + 40))
        ks = font_medium.render(f"Kills: {enemies_killed}", True, YELLOW)
        screen.blit(ks, (WIDTH//2 - ks.get_width()//2, HEIGHT//3 + 90))
        hint = font_small.render("R — restart     C — menu     Q — quit", True, (200,200,200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT*2//3 + 30))

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        GRAVITY = _orig_gravity; return 'rematch'
                    if event.key == pygame.K_c:
                        GRAVITY = _orig_gravity; return 'select'
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        GRAVITY = _orig_gravity; pygame.quit(); sys.exit()
                else:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        GRAVITY = _orig_gravity; return 'select'

        if not game_over:
            survival_timer += 1
            max_en, diff = wave_info()

            # Platforms & springs
            for plat in platforms:
                plat.update()
            for sp in springs:
                sp.update()
                sp.trigger(p1)
                if two_player: sp.trigger(p2)
                for en in enemies: sp.trigger(en)

            # Spawn enemies
            enemy_spawn_timer -= 1
            if enemy_spawn_timer <= 0 and len(enemies) < max_en:
                ci    = random.randint(0, len(CHARACTERS) - 1)
                sx    = float(random.choice([60, WIDTH - 60]))
                en    = AIFighter(sx, CHARACTERS[ci], -1 if sx > WIDTH // 2 else 1, diff)
                en.hp = en.char["max_hp"]
                enemies.append(en)
                interval          = max(60, 300 - survival_timer // (2 * FPS))
                enemy_spawn_timer = random.randint(max(30, interval // 2), interval)

            # Update enemies — each targets nearest living player
            living = [p for p in players if p.hp > 0]
            for en in enemies:
                if living:
                    target = min(living, key=lambda p: abs(p.x - en.x))
                    en.update(None, target, platforms)
                    if en.pending_ball:
                        en.pending_ball = False
                        en_balls.append(Projectile(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_orb and en.bazooka_cooldown == 0:
                        en.pending_orb = False
                        en_orbs.append(Orb(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_bounce:
                        en.pending_bounce = False
                        en_bounce_balls.append(BouncingBall(en.x + en.facing*30, en.y-60, en.facing, en))

            # Mark newly dead players and freeze them
            for p in players:
                if p.hp <= 0 and p.action != 'dead':
                    p.action     = 'dead'
                    p.action_t   = 0
                    p.flash_timer = 0
                    p.vx = 0
                    p.vy = 0

            # Update players (skip dead ones)
            keys     = pygame.key.get_pressed()
            other_p1 = p2 if two_player else (enemies[0] if enemies else p1)
            if p1.hp > 0:
                p1.update(keys, other_p1, platforms)
            if two_player and p2.hp > 0:
                p2.update(keys, p1, platforms)

            # Spawn player projectiles
            for shooter in players:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing*30, shooter.y-60,
                                            shooter.facing, shooter))
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing*30, shooter.y-60,
                                    shooter.facing, shooter))
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing*30, shooter.y-60,
                                                     shooter.facing, shooter))
                if shooter.pending_hook and enemies:
                    shooter.pending_hook = False
                    tgt = min(enemies, key=lambda e: abs(e.x - shooter.x))
                    hooks.append(SnakeHook(shooter.x + shooter.facing*20, shooter.y-60,
                                           tgt.x, tgt.y-60, shooter))
                else:
                    shooter.pending_hook = False

            # Boomerang damage: player boomerangs hit enemies, enemy boomerangs hit players
            for thrower in players:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    for en in enemies:
                        if math.hypot(bx - en.x, by - (en.y - 60)) < 48:
                            en.hp = max(0, en.hp - 8)
                            en.flash_timer = 6
                            thrower.boomerang_hit_cd = 30
                            break
            for en in enemies:
                if en.boomerang_timer > 0 and en.boomerang_hit_cd == 0:
                    bx = en.x + math.cos(en.boomerang_angle) * 85
                    by = (en.y - 60) + math.sin(en.boomerang_angle) * 55
                    for p in living:
                        if math.hypot(bx - p.x, by - (p.y - 60)) < 48:
                            p.hp = max(0, p.hp - 8)
                            p.flash_timer = 6
                            en.boomerang_hit_cd = 30
                            break

            # Player balls → enemies
            for b in balls:
                b.update()
                if b.alive:
                    for en in enemies:
                        if b.collides(en):
                            en.hp = max(0, en.hp - 10); en.flash_timer = 8
                            b.alive = False; break
            balls = [b for b in balls if b.alive]

            # Player orbs → enemies
            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    for en in enemies:
                        if math.hypot(o.x - en.x, o.y - (en.y - 60)) < o.EXPLODE_RADIUS:
                            en.hp = max(0, en.hp - o.EXPLODE_DMG); en.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            # Player bouncing balls → enemies
            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    for en in enemies:
                        if bb.collides(en):
                            en.hp = max(0, en.hp - 10); en.flash_timer = 8
                            bb.hit_cd = BouncingBall.HIT_CD; break
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            # Player hooks → enemies
            for h in hooks:
                h.update()
                if h.alive:
                    for en in enemies:
                        if h.collides(en):
                            pull = 1 if h.owner.x > en.x else -1
                            en.knockback = pull * 22
                            en.hp = max(0, en.hp - 6); en.flash_timer = 8
                            h.alive = False; break
            hooks = [h for h in hooks if h.alive]

            # Enemy balls → players
            for b in en_balls:
                b.update()
                if b.alive:
                    for p in living:
                        if b.collides(p):
                            p.hp = max(0, p.hp - 10); p.flash_timer = 8
                            b.alive = False; break
            en_balls = [b for b in en_balls if b.alive]

            # Enemy orbs → players
            for o in en_orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    for p in living:
                        if math.hypot(o.x - p.x, o.y - (p.y - 60)) < o.EXPLODE_RADIUS:
                            p.hp = max(0, p.hp - o.EXPLODE_DMG); p.flash_timer = 14
            en_orbs = [o for o in en_orbs if o.alive]

            # Enemy bouncing balls → players
            for bb in en_bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    for p in living:
                        if bb.collides(p):
                            p.hp = max(0, p.hp - 10); p.flash_timer = 8
                            bb.hit_cd = BouncingBall.HIT_CD; break
            en_bounce_balls = [bb for bb in en_bounce_balls if bb.alive]

            # Player pumpkins → enemies
            for shooter in players:
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(
                        shooter.x + shooter.facing * 24, shooter.y - 80,
                        shooter.facing, shooter))
            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    for en in enemies:
                        if math.hypot(pk.x - en.x, pk.y - (en.y - 60)) < pk.EXPLODE_RADIUS:
                            en.hp = max(0, en.hp - pk.EXPLODE_DMG); en.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    for en in enemies:
                        if pk.collides(en):
                            pk._explode(); break
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Enemy pumpkins → players
            for en in enemies:
                if en.pending_pumpkin:
                    en.pending_pumpkin = False
                    en_pumpkins.append(Pumpkin(
                        en.x + en.facing * 24, en.y - 80, en.facing, en))
            for pk in en_pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    for p in living:
                        if math.hypot(pk.x - p.x, pk.y - (p.y - 60)) < pk.EXPLODE_RADIUS:
                            p.hp = max(0, p.hp - pk.EXPLODE_DMG); p.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    for p in living:
                        if pk.collides(p):
                            pk._explode(); break
            en_pumpkins = [pk for pk in en_pumpkins if pk.alive]

            # Ink Brush clones (survival)
            for shooter in players:
                if shooter.pending_ink_clone:
                    shooter.pending_ink_clone = False
                    # target nearest enemy
                    tgt = min(enemies, key=lambda e: abs(e.x - shooter.x)) if enemies else None
                    if tgt:
                        cf = AIFighter(shooter.x + shooter.facing * 55, shooter.char, -shooter.facing, 'medium')
                        cf.hp = max(1, shooter.hp)
                        cf.color = shooter.color
                        cf.no_attack = True
                        ink_clones.append({'fighter': cf, 'timer': FPS * 100, 'target': tgt})
            new_ink = []
            for ic in ink_clones:
                ic['timer'] -= 1
                if ic['timer'] > 0 and ic['fighter'].hp > 0:
                    ic['fighter'].update(None, ic['target'], platforms)
                    new_ink.append(ic)
            ink_clones = new_ink

            # Pencil drawn platforms + Eraser (survival)
            for fighter in players:
                if fighter.pending_draw_platform:
                    fighter.pending_draw_platform = False
                    platforms.append(DrawnPlatform(fighter.x - 60, fighter.y, w=120))
                if fighter.pending_erase:
                    fighter.pending_erase = False
                    fighter.flash_timer = 8
                    platforms = [p for p in platforms
                                 if not (isinstance(p, DrawnPlatform)
                                         and abs((p.x + p.w / 2) - fighter.x) < 220)]
            for p in platforms:
                if isinstance(p, DrawnPlatform):
                    p.update()
            platforms = [p for p in platforms if not (isinstance(p, DrawnPlatform) and not p.alive)]

            # Death pops: spawn burst when enemy hp hits 0, then remove enemy
            for en in enemies:
                if en.hp <= 0:
                    death_pops.append({'x': en.x, 'y': en.y - 60,
                                       'color': en.char["color"], 't': 22})
            for dp in death_pops:
                dp['t'] -= 1
            death_pops = [dp for dp in death_pops if dp['t'] > 0]

            # Count kills, remove dead enemies
            before         = len(enemies)
            enemies        = [en for en in enemies if en.hp > 0]
            enemies_killed += before - len(enemies)

            # Jungle snakes
            if is_jungle:
                snake_spawn_timer -= 1
                if snake_spawn_timer <= 0 and len(jungle_snakes) < 4:
                    jungle_snakes.append(JungleSnake())
                    snake_spawn_timer = random.randint(300, 480)
                for sn in jungle_snakes:
                    all_targets = players + enemies
                    living_targets = [t for t in all_targets if t.hp > 0]
                    if living_targets:
                        closest = min(living_targets, key=lambda t: abs(t.x - sn.x))
                        sn.update(closest, closest)
                jungle_snakes = [sn for sn in jungle_snakes if sn.alive]

            if is_computer:
                bug_spawn_timer -= 1
                if bug_spawn_timer <= 0 and len(computer_bugs) < 5:
                    computer_bugs.append(ComputerBug())
                    bug_spawn_timer = random.randint(200, 360)
                for b in computer_bugs:
                    all_targets = [p for p in players if p.hp > 0] + enemies
                    target = min(all_targets, key=lambda t: abs(t.x - b.x)) if all_targets else None
                    b.update(target)
                computer_bugs = [b for b in computer_bugs if b.alive]

            # Powerups (no clone type in survival)
            _survival_pool = [p for p in POWERUPS if p['type'] != 'clone']
            powerup_timer -= 1
            if powerup_timer <= 0 and len(powerups) < 3:
                pu_new = Powerup.__new__(Powerup)
                pu_new.spec = random.choice(_survival_pool)
                pu_new.name = pu_new.spec['name']
                pu_new.color = pu_new.spec['color']
                pu_new.x = float(random.randint(80, WIDTH - 80))
                pu_new.y = float(GROUND_Y - 14)
                pu_new.age = 0
                pu_new.picked_up = False
                powerups.append(pu_new)
                powerup_timer = random.randint(480, 720)
            for pu in powerups:
                pu.update()
                for p in players:
                    if p.hp > 0 and not pu.picked_up and pu.collides(p):
                        p.apply_powerup(pu.spec)
                        pu.picked_up = True; break
                if not pu.picked_up:
                    for en in enemies:
                        if pu.collides(en):
                            en.apply_powerup(pu.spec)
                            pu.picked_up = True; break
            powerups = [pu for pu in powerups if not pu.picked_up]

            # Game over when all players dead
            if all(p.hp <= 0 for p in players):
                game_over = True

        # --- Draw ---
        draw_bg(screen, stage_idx)
        for plat in platforms:     plat.draw(screen, stage_idx)
        for sp   in springs:       sp.draw(screen)
        for pu   in powerups:      pu.draw(screen)
        for b    in balls:         b.draw(screen)
        for b    in en_balls:      b.draw(screen)
        for o    in orbs:          o.draw(screen)
        for o    in en_orbs:       o.draw(screen)
        for bb   in bounce_balls:  bb.draw(screen)
        for bb   in en_bounce_balls: bb.draw(screen)
        for h    in hooks:         h.draw(screen)
        for pk   in pumpkins:      pk.draw(screen)
        for pk   in en_pumpkins:   pk.draw(screen)
        for sn   in jungle_snakes: sn.draw(screen)
        for b    in computer_bugs: b.draw(screen)
        for ic   in ink_clones:    ic['fighter'].draw(screen)

        # Death burst particles
        for dp in death_pops:
            prog  = 1.0 - dp['t'] / 22
            r     = int(4 + prog * 28)
            col   = dp['color']
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                px  = int(dp['x'] + math.cos(rad) * r * 1.4)
                py  = int(dp['y'] + math.sin(rad) * r)
                cr  = max(1, int(6 * (1.0 - prog)))
                pygame.draw.circle(screen, col, (px, py), cr)
            pygame.draw.circle(screen, WHITE, (int(dp['x']), int(dp['y'])), max(1, int(10 * (1.0 - prog))))

        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen) if two_player else None
        en_hits = [(en, en.draw(screen)) for en in enemies]

        if not game_over:
            # Player attacks hit enemies
            for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                if attacker.attacking and not attacker.attack_hit and hit_pos:
                    for en in enemies:
                        attacker.check_hit(hit_pos, en)
            # Enemy attacks hit players — 2P players can't hurt each other
            for en, en_hit in en_hits:
                if en.attacking and not en.attack_hit and en_hit:
                    for p in players:
                        en.check_hit(en_hit, p)
            # Fighter attacks on jungle snakes
            for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                if attacker.attacking and hit_pos:
                    for sn in jungle_snakes:
                        if math.hypot(hit_pos[0]-sn.x, hit_pos[1]-(sn.y-8)) < 44:
                            dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                   else attacker.char["kick_dmg"])
                            sn.take_damage(dmg)
            # Fighter attacks on computer bugs
            if is_computer:
                for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                    if attacker.attacking and hit_pos:
                        for b in computer_bugs:
                            if math.hypot(hit_pos[0]-b.x, hit_pos[1]-(b.y-8)) < 40:
                                dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                       else attacker.char["kick_dmg"])
                                b.take_damage(dmg)

        # Enemy name tags
        for en in enemies:
            tag = font_tiny.render(en.char["name"], True, en.char["color"])
            screen.blit(tag, (int(en.x) - tag.get_width()//2,
                               int(en.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        _draw_survival_hud()
        draw_active_powerups(screen, p1, 'left')
        if two_player:
            draw_active_powerups(screen, p2, 'right')
        if game_over:
            _draw_game_over()

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    while True:
        mode = mode_select()

        # --- Survival path ---
        if mode in ('survival_1p', 'survival_2p'):
            two_player = (mode == 'survival_2p')
            p1_idx, p2_idx = character_select(vs_ai=not two_player)
            if p1_idx is None:
                continue
            s_idx = stage_select()
            while True:
                result = run_survival(p1_idx, p2_idx if two_player else None,
                                      two_player=two_player, stage_idx=s_idx)
                if result == 'rematch':
                    continue
                break
            continue

        # --- Normal fight path ---
        if mode == '2p':
            vs_ai, difficulty = False, 'medium'
        else:
            vs_ai, difficulty = True, mode[1]

        p1_idx, p2_idx = character_select(vs_ai=vs_ai)
        if p1_idx is None:
            continue

        s_idx = stage_select()
        while True:
            result = run_fight(p1_idx, p2_idx, vs_ai=vs_ai, ai_difficulty=difficulty, stage_idx=s_idx)
            if result == 'rematch':
                continue
            break

if __name__ == "__main__":
    main()
