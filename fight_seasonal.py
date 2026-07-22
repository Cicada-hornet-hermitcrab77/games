import datetime
import pygame
import math
from constants import *

# ---------------------------------------------------------------------------
# Seasonal event definitions
# ---------------------------------------------------------------------------

SEASONAL_EVENTS = [
    {"name": "New Dynasties",        "start": (1,  1),  "end": (1,  7),  "deco": "new_dynasties"},
    {"name": "Hearts and Harmonies", "start": (2, 14),  "end": (2, 20),  "deco": "hearts"},
    {"name": "Emerald Echoes",       "start": (3, 17),  "end": (3, 23),  "deco": "emerald",
     "special_mode": "the_casino", "special_mode_label": "The Casino"},
    {"name": "April Rain",           "start": (3, 28),  "end": (4,  4),  "deco": "easter"},
    {"name": "Bound to the Ground",  "start": (4, 22),  "end": (4, 28),  "deco": "earth",
     "special_mode": "giants_among_us", "special_mode_label": "Giants Among Us"},
    {"name": "Legacy of Valor",      "start": (5, 25),  "end": (5, 25),  "deco": "memorial"},
    {"name": "Summer Solstice",      "start": (6, 21),  "end": (6, 27),  "deco": "summer",
     "special_mode": "floor_is_lava", "special_mode_label": "Floor is Lava"},
    {"name": "Red White and Boom",   "start": (7,  4),  "end": (7, 10),  "deco": "july4"},
    {"name": "Novel Beginnings",     "start": (8, 10),  "end": (8, 16),  "deco": "school"},
    {"name": "Project Yellowstone",  "start": (8, 25),  "end": (8, 25),  "deco": "mountain"},
    {"name": "Echoes of the Undying","start": (10,31),  "end": (11, 6),  "deco": "halloween"},
    {"name": "Feasterween",          "start": (11,26),  "end": (12, 2),  "deco": "thanksgiving"},
    {"name": "Aura of Menorah",      "start": (12, 4),  "end": (12,12),  "deco": "hanukkah",
     "special_mode": "chaos_aura", "special_mode_label": "Chaos Aura"},
    {"name": "Yuletide Gatherings",  "start": (12,25),  "end": (12,31),  "deco": "christmas"},
]

# Characters sold in the seasonal shop, each tied to a specific event.
SEASONAL_SHOP_CHARS = [
    # ── New Dynasties ────────────────────────────────────────────────────────
    {"name": "Nian",           "event": "New Dynasties",        "cost": 300},
    {"name": "Bomb",           "event": "New Dynasties",        "cost":  50},
    {"name": "Nuke",           "event": "New Dynasties",        "cost":  80},
    {"name": "Trailblazer",    "event": "New Dynasties",        "cost": 100},
    # ── Hearts and Harmonies ─────────────────────────────────────────────────
    {"name": "Smoochie",       "event": "Hearts and Harmonies", "cost": 330},
    {"name": "Harpy",          "event": "Hearts and Harmonies", "cost":  50},
    {"name": "Angel",          "event": "Hearts and Harmonies", "cost":  75},
    # ── Emerald Echoes ───────────────────────────────────────────────────────
    {"name": "Clover",         "event": "Emerald Echoes",        "cost": 270},
    {"name": "Lucky",          "event": "Emerald Echoes",        "cost": 150},
    {"name": "Rainbow Man",    "event": "Emerald Echoes",        "cost":  80},
    # ── Other events (placeholder — add chars as needed) ─────────────────────
    # ── April Rain ───────────────────────────────────────────────────────────
    {"name": "Baddit",         "event": "April Rain",            "cost": 230},
    {"name": "Eggshell",       "event": "April Rain",            "cost":  70},
    {"name": "Eartha",         "event": "Bound to the Ground",  "cost": 270},
    {"name": "Tombstone",      "event": "Legacy of Valor",      "cost": 1000},
    {"name": "Solara",         "event": "Summer Solstice",      "cost": 270},
    {"name": "Stickman of Liberty", "event": "Red White and Boom", "cost": 280},
    {"name": "Veteran",             "event": "Red White and Boom", "cost":  80},
    {"name": "Gunner",              "event": "Red White and Boom", "cost":  50},
    {"name": "Bazooka Man",         "event": "Red White and Boom", "cost":  70},
    {"name": "Bookzworm",      "event": "Novel Beginnings",     "cost": 320},
    {"name": "Scrollmaster",   "event": "Novel Beginnings",     "cost": 120},
    {"name": "Yellowstone",    "event": "Project Yellowstone",  "cost": 290},
    {"name": "Jack O' Slash",  "event": "Echoes of the Undying", "cost": 330},
    {"name": "Ghost",          "event": "Echoes of the Undying", "cost":  50},
    {"name": "Headless Horseman", "event": "Echoes of the Undying", "cost": 75},
    {"name": "Demon",          "event": "Echoes of the Undying", "cost":  90},
    {"name": "Reaper",         "event": "Echoes of the Undying", "cost":  85},
    {"name": "Vampire",        "event": "Echoes of the Undying", "cost":  60},
    {"name": "Cornucopia",     "event": "Feasterween",          "cost": 350},
    {"name": "Chef",           "event": "Feasterween",          "cost": 100},
    {"name": "Scarecrow",      "event": "Feasterween",          "cost":  60},
    {"name": "Nun-Gimel-Hei-Shin", "event": "Aura of Menorah",   "cost": 290},
    {"name": "Saint Nix",          "event": "Yuletide Gatherings", "cost": 305},
    {"name": "Wendigo",            "event": "Yuletide Gatherings", "cost": 100},
    {"name": "Cryogenisist",       "event": "Yuletide Gatherings", "cost":  50},
]


def get_active_event():
    """Return the currently active seasonal event dict, or None."""
    today = datetime.date.today()
    t = today.month * 100 + today.day
    for ev in SEASONAL_EVENTS:
        sm, sd = ev["start"]
        em, ed = ev["end"]
        s = sm * 100 + sd
        e = em * 100 + ed
        if s <= e:
            if s <= t <= e:
                return ev
        else:  # year-wrap (none of our events do this, but handle it anyway)
            if t >= s or t <= e:
                return ev
    return None


# ---------------------------------------------------------------------------
# Decoration drawing — called each frame on all UI screens during an event
# ---------------------------------------------------------------------------

def draw_seasonal_decos(screen):
    ev = get_active_event()
    if ev is None:
        return
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    deco = ev["deco"]
    if   deco == "new_dynasties": _deco_new_dynasties(surf)
    elif deco == "hearts":        _deco_hearts(surf)
    elif deco == "emerald":       _deco_emerald(surf)
    elif deco == "easter":        _deco_easter(surf)
    elif deco == "earth":         _deco_earth(surf)
    elif deco == "memorial":      _deco_memorial(surf)
    elif deco == "summer":        _deco_summer(surf)
    elif deco == "july4":         _deco_july4(surf)
    elif deco == "school":        _deco_school(surf)
    elif deco == "mountain":      _deco_mountain(surf)
    elif deco == "halloween":     _deco_halloween(surf)
    elif deco == "thanksgiving":  _deco_thanksgiving(surf)
    elif deco == "hanukkah":      _deco_hanukkah(surf)
    elif deco == "christmas":     _deco_christmas(surf)
    screen.blit(surf, (0, 0))


# ── helpers ─────────────────────────────────────────────────────────────────

def _draw_star(surf, cx, cy, r, color):
    pts = []
    for j in range(5):
        outer = -math.pi / 2 + j * 2 * math.pi / 5
        pts.append((cx + r * math.cos(outer), cy + r * math.sin(outer)))
        inner = outer + math.pi / 5
        pts.append((cx + r * 0.4 * math.cos(inner), cy + r * 0.4 * math.sin(inner)))
    pygame.draw.polygon(surf, color, pts)


def _draw_heart(surf, cx, cy, r, color):
    pygame.draw.circle(surf, color, (cx - r // 2, cy), r // 2)
    pygame.draw.circle(surf, color, (cx + r // 2, cy), r // 2)
    pts = [(cx - r, cy), (cx + r, cy), (cx, cy + r + r // 3)]
    pygame.draw.polygon(surf, color, pts)


def _draw_snowflake(surf, cx, cy, r, color):
    for j in range(6):
        angle = j * math.pi / 3
        x2 = int(cx + r * math.cos(angle))
        y2 = int(cy + r * math.sin(angle))
        pygame.draw.line(surf, color, (cx, cy), (x2, y2), 1)
        for cross_sign in (-1, 1):
            perp = angle + cross_sign * math.pi / 3
            xm = cx + (r * 0.55) * math.cos(angle)
            ym = cy + (r * 0.55) * math.sin(angle)
            xc = xm + (r * 0.25) * math.cos(perp)
            yc = ym + (r * 0.25) * math.sin(perp)
            pygame.draw.line(surf, color, (int(xm), int(ym)), (int(xc), int(yc)), 1)


# ── per-event drawing ────────────────────────────────────────────────────────

def _deco_new_dynasties(surf):
    # Red lanterns hanging from the top + gold coins in corners
    A = 210
    for x in [50, 160, 290, 450, 610, 750, 860]:
        pygame.draw.line(surf, (180, 30, 30, A), (x, 0), (x, 14), 2)
        body = pygame.Rect(x - 11, 13, 22, 30)
        pygame.draw.ellipse(surf, (220, 30, 30, A), body)
        pygame.draw.ellipse(surf, (255, 60, 60, A), body, 1)
        pygame.draw.line(surf, (255, 200, 0, A), (x - 9, 15), (x + 9, 15), 2)
        pygame.draw.line(surf, (255, 200, 0, A), (x - 9, 41), (x + 9, 41), 2)
        pygame.draw.line(surf, (255, 200, 0, A), (x, 43), (x, 52), 2)
    for cx, cy in [(12, HEIGHT - 12), (WIDTH - 12, HEIGHT - 12)]:
        pygame.draw.circle(surf, (255, 200, 0, A), (cx, cy), 9)
        pygame.draw.circle(surf, (200, 150, 0, A), (cx, cy), 9, 2)


def _deco_hearts(surf):
    A = 200
    positions = [30, 110, 220, 350, 460, 580, 700, 810, 875,
                 15, WIDTH - 15]
    for i, x in enumerate(positions):
        y = 18 if i < 9 else HEIGHT - 18
        _draw_heart(surf, x, y, 10, (255, 140, 180, A))


def _deco_emerald(surf):
    A = 200
    for x in [45, 145, 280, 430, 580, 720, 855]:
        c = (40, 190, 80, A)
        pygame.draw.circle(surf, c, (x, 12), 7)
        pygame.draw.circle(surf, c, (x - 7, 19), 7)
        pygame.draw.circle(surf, c, (x + 7, 19), 7)
        pygame.draw.line(surf, (30, 140, 50, A), (x, 24), (x, 36), 2)


def _deco_easter(surf):
    A = 220
    cols = [(255, 100, 100, A), (100, 180, 255, A), (255, 220, 50, A),
            (160, 100, 255, A), (80, 210, 120, A), (255, 150, 60, A)]
    for i, x in enumerate([40, 130, 230, 350, 470, 590, 710, 830]):
        col = cols[i % len(cols)]
        pygame.draw.ellipse(surf, col, (x - 9, 4, 18, 26))
        pygame.draw.line(surf, tuple(max(0, c - 80) for c in col[:3]) + (A,),
                         (x - 8, 17), (x + 8, 17), 2)


def _deco_earth(surf):
    A = 200
    for x in [30, 120, 250, 400, 550, 690, 830, 875]:
        pygame.draw.ellipse(surf, (50, 190, 70, A), (x - 9, 5, 18, 12))
        pygame.draw.line(surf, (80, 130, 50, A), (x, 14), (x, 24), 2)


def _deco_memorial(surf):
    A = 200
    star_cols = [(200, 30, 30, A), (30, 60, 200, A)]
    for i, x in enumerate([35, 135, 270, 440, 610, 760, 865]):
        _draw_star(surf, x, 16, 10, star_cols[i % 2])


def _deco_summer(surf):
    A = 210
    # Large sun in top-right corner with 12 rays
    sun_x, sun_y, sun_r = WIDTH - 44, 44, 26
    pygame.draw.circle(surf, (255, 230, 30, A), (sun_x, sun_y), sun_r)
    pygame.draw.circle(surf, (255, 245, 120, A), (sun_x, sun_y), sun_r - 8)
    for j in range(12):
        angle = j * math.pi / 6
        x1 = int(sun_x + (sun_r + 4) * math.cos(angle))
        y1 = int(sun_y + (sun_r + 4) * math.sin(angle))
        ray_len = 22 if j % 2 == 0 else 14
        x2 = int(sun_x + (sun_r + 4 + ray_len) * math.cos(angle))
        y2 = int(sun_y + (sun_r + 4 + ray_len) * math.sin(angle))
        lw = 3 if j % 2 == 0 else 2
        pygame.draw.line(surf, (255, 210, 0, A), (x1, y1), (x2, y2), lw)
    # Heat shimmer wavy lines in middle of screen
    mid_y = HEIGHT // 2
    for row in range(4):
        wy = mid_y - 30 + row * 18
        alpha_w = max(40, 110 - row * 20)
        pts = []
        x = 80
        while x <= WIDTH - 80:
            pts.append((x, wy + int(5 * math.sin(x * 0.06 + row * 1.2))))
            x += 8
        if len(pts) >= 2:
            pygame.draw.lines(surf, (255, 180, 60, alpha_w), False, pts, 1)
    # Small flame shapes along bottom edge
    for fx in range(20, WIDTH, 38):
        fh = 14 + int(7 * math.sin(fx * 0.07))
        flame_pts = [
            (fx, HEIGHT),
            (fx - 6, HEIGHT - fh // 2),
            (fx - 3, HEIGHT - fh),
            (fx,     HEIGHT - fh - 5),
            (fx + 3, HEIGHT - fh),
            (fx + 6, HEIGHT - fh // 2),
            (fx, HEIGHT),
        ]
        pygame.draw.polygon(surf, (255, 90, 10, 180), flame_pts)
        inner_pts = [
            (fx, HEIGHT),
            (fx - 3, HEIGHT - fh // 2 - 2),
            (fx,     HEIGHT - fh + 2),
            (fx + 3, HEIGHT - fh // 2 - 2),
            (fx, HEIGHT),
        ]
        pygame.draw.polygon(surf, (255, 210, 60, 160), inner_pts)


def _deco_july4(surf):
    A = 200
    for cx, cy, col in [(35, 28, (220, 40, 40, A)), (WIDTH - 35, 28, (40, 80, 220, A)),
                        (35, HEIGHT - 28, (40, 80, 220, A)), (WIDTH - 35, HEIGHT - 28, (220, 40, 40, A))]:
        for j in range(8):
            angle = j * math.pi / 4
            pygame.draw.line(surf, col, (cx, cy),
                             (int(cx + 18 * math.cos(angle)), int(cy + 18 * math.sin(angle))), 2)
        pygame.draw.circle(surf, (255, 255, 255, A), (cx, cy), 4)
    for x in [200, 380, 560, 720]:
        _draw_star(surf, x, 14, 8, (255, 255, 255, A))


def _deco_school(surf):
    A = 200
    book_cols = [(200, 60, 60, A), (60, 100, 200, A), (60, 180, 80, A)]
    for i, x in enumerate([35, 135, 255, 390, 530, 670, 820]):
        if i % 2 == 0:
            col = book_cols[(i // 2) % 3]
            pygame.draw.rect(surf, col, (x - 9, 5, 18, 26))
            pygame.draw.rect(surf, (255, 255, 255, A), (x - 9, 5, 18, 26), 1)
            pygame.draw.line(surf, (255, 255, 255, A), (x - 5, 5), (x - 5, 31), 1)
        else:
            pygame.draw.rect(surf, (255, 220, 50, A), (x - 3, 7, 6, 20))
            pygame.draw.polygon(surf, (255, 200, 160, A),
                                [(x - 3, 27), (x + 3, 27), (x, 36)])
            pygame.draw.rect(surf, (220, 180, 180, A), (x - 3, 4, 6, 5))


def _deco_mountain(surf):
    A = 190
    mountain_pts = [
        (0, HEIGHT), (90, HEIGHT - 55), (200, HEIGHT - 35),
        (310, HEIGHT - 85), (440, HEIGHT - 45),
        (570, HEIGHT - 75), (680, HEIGHT - 35),
        (800, HEIGHT - 65), (WIDTH, HEIGHT - 25), (WIDTH, HEIGHT),
    ]
    pygame.draw.polygon(surf, (65, 85, 75, A), mountain_pts)
    for mx, my in [(90, HEIGHT - 55), (310, HEIGHT - 85), (570, HEIGHT - 75), (800, HEIGHT - 65)]:
        pygame.draw.polygon(surf, (215, 225, 235, A),
                            [(mx - 12, my + 10), (mx, my), (mx + 12, my + 10)])
    for gx in [WIDTH // 2 - 6, WIDTH // 2, WIDTH // 2 + 6]:
        for gy in range(5, 30, 6):
            r = max(2, 7 - gy // 5)
            pygame.draw.circle(surf, (190, 220, 255, max(0, 180 - gy * 5)), (gx, gy), r)


def _deco_halloween(surf):
    A = 200
    # Spider web top-left corner
    for r in [20, 38, 56]:
        for j in range(6):
            angle = j * math.pi / 10
            x2 = int(r * math.cos(angle))
            y2 = int(r * math.sin(angle))
            pygame.draw.line(surf, (100, 100, 100, 150), (0, 0), (x2, y2), 1)
        for j in range(6):
            a1, a2 = j * math.pi / 10, (j + 1) * math.pi / 10
            pygame.draw.line(surf, (100, 100, 100, 130),
                             (int(r * math.cos(a1)), int(r * math.sin(a1))),
                             (int(r * math.cos(a2)), int(r * math.sin(a2))), 1)
    for x in [180, 380, 580, 780]:
        pygame.draw.circle(surf, (200, 100, 20, A), (x, 17), 13)
        pygame.draw.circle(surf, (0, 0, 0, A), (x - 4, 13), 3)
        pygame.draw.circle(surf, (0, 0, 0, A), (x + 4, 13), 3)
        pygame.draw.line(surf, (0, 0, 0, A), (x - 5, 22), (x - 2, 25), 2)
        pygame.draw.line(surf, (0, 0, 0, A), (x - 2, 25), (x + 2, 25), 2)
        pygame.draw.line(surf, (0, 0, 0, A), (x + 2, 25), (x + 5, 22), 2)


def _deco_thanksgiving(surf):
    A = 200
    leaf_cols = [(200, 100, 30, A), (180, 60, 20, A), (220, 160, 40, A)]
    for i, x in enumerate([30, 120, 240, 380, 530, 670, 820]):
        col = leaf_cols[i % 3]
        pygame.draw.ellipse(surf, col, (x - 10, 7, 20, 13))
        pygame.draw.line(surf, (100, 70, 30, A), (x, 14), (x + 5, 23), 2)
    tx, ty = WIDTH - 32, 24
    pygame.draw.ellipse(surf, (120, 80, 40, A), (tx - 13, ty - 9, 26, 20))
    pygame.draw.circle(surf, (130, 90, 50, A), (tx + 7, ty - 11), 7)
    fan_cols = [(200, 100, 30, A), (180, 60, 20, A), (220, 160, 40, A), (160, 80, 20, A)]
    for j in range(5):
        angle = math.pi * 0.7 + j * math.pi * 0.12
        pygame.draw.line(surf, fan_cols[j % 4], (tx - 12, ty - 2),
                         (int(tx - 12 + 20 * math.cos(angle)), int(ty - 2 + 20 * math.sin(angle))), 3)


def _deco_hanukkah(surf):
    A = 200
    mx, my = WIDTH // 2, 4
    pygame.draw.rect(surf, (200, 180, 60, A), (mx - 22, my + 32, 44, 5))
    pygame.draw.line(surf, (200, 180, 60, A), (mx, my + 32), (mx, my + 8), 3)
    pygame.draw.circle(surf, (255, 230, 60, A), (mx, my + 6), 5)
    for side in (-1, 1):
        for j in range(1, 5):
            bx = mx + side * j * 10
            pygame.draw.line(surf, (200, 180, 60, A), (mx + side * j * 10, my + 32), (bx, my + 15), 2)
            pygame.draw.circle(surf, (255, 230, 60, A), (bx, my + 13), 4)
    for cx, cy in [(18, 20), (WIDTH - 18, 20)]:
        r = 12
        pts1 = [(cx, cy - r), (cx - r * 0.866, cy + r * 0.5), (cx + r * 0.866, cy + r * 0.5)]
        pygame.draw.polygon(surf, (50, 110, 220, A), pts1, 2)
        pts2 = [(cx, cy + r), (cx - r * 0.866, cy - r * 0.5), (cx + r * 0.866, cy - r * 0.5)]
        pygame.draw.polygon(surf, (50, 110, 220, A), pts2, 2)


def _deco_christmas(surf):
    A = 200
    tree_col = (30, 140, 50, A)
    for tx in [28, 145, WIDTH - 28]:
        pygame.draw.rect(surf, (100, 70, 40, A), (tx - 3, 34, 6, 8))
        pygame.draw.polygon(surf, tree_col, [(tx, 4), (tx - 17, 32), (tx + 17, 32)])
        pygame.draw.polygon(surf, (20, 110, 40, A), [(tx, 10), (tx - 13, 30), (tx + 13, 30)])
        _draw_star(surf, tx, 4, 5, (255, 220, 0, A))
        for ox, oy, oc in [(tx - 7, 24, (220, 40, 40, A)),
                           (tx + 7, 24, (40, 80, 220, A)),
                           (tx, 29, (255, 215, 0, A))]:
            pygame.draw.circle(surf, oc, (ox, oy), 3)
    for sx, sy in [(250, 11), (400, 7), (540, 13), (680, 9), (820, 12)]:
        _draw_snowflake(surf, sx, sy, 10, (200, 230, 255, A))
