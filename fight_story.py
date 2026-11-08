"""Story Mode — the attack on Wombrock Town, one map at a time.

Wombrocks have been coming over the ridge into Tombstone, so Tombstone sent
two people to ask you to go east and hit them at home. A map is a yard with
things in it, drawn on paper and read off here: platforms, enemies, coffin
guarders, moving ones, portals, springs and a door you open with E.

This module owns the data and the screens. It never starts a fight itself;
fight_game does that, because run_fight lives there and importing it back
would close a loop.
"""

import math

import pygame

from constants import *
from constants import dev_today
from fight_data import CHARACTERS, STAGES
from fight_drawing import draw_stickman

# ── Maps ────────────────────────────────────────────────────────────────────
# A map is drawn on paper at 1920x1080 with the ground line at y=940, so the
# numbers below are read straight off the drawing and squashed onto the real
# screen here. That way a map can be checked against its picture.
MAP_W, MAP_H, MAP_GROUND = 1920, 1080, 940


def mx(v):
    return int(v * WIDTH / float(MAP_W))


def my(v):
    return int(v * GROUND_Y / float(MAP_GROUND))


# The legend the maps are drawn in:
#   red    enemies            green  coffin guarders
#   yellow moving enemies     blue   portals
#   pink   springs            black  platforms
#   white  background         brown  a door, opened with E
MAPS = [
    {
        "name": "The yard at Tombstone",
        "start": (90, 940),
        "platforms": [            # (x, y, width) — the top face of each
            (290, 125, 440),      # the long roof the coffin sits over
            (1050, 130, 240),     # the biter's ledge
            (900, 290, 90),       # the upright of the middle step
            (790, 440, 200),      # and its foot
            (1110, 285, 120),     # the tall pillar
            (640, 575, 120),      # the lower step, upright
            (465, 715, 295),      # and its foot
            (1740, 470, 80),      # the climb to the top right
            (1800, 400, 80),
            (1860, 330, 60),
        ],
        "walls": [                # drawn as solid blocks under their platform
            (1110, 285, 120, MAP_GROUND - 285),
            (900, 290, 90, 150),
            (640, 575, 120, 140),
        ],
        "coffin": (370, 40, 310, 90),
        "guards": [(305, 125), (715, 125)],
        "biters": [(1150, 130), (1850, 330), (1315, MAP_GROUND)],
        "floaters": [             # (x1, y1, x2, y2) — the line it runs
            (60, 320, 850, 320),
            (1300, 120, 1690, 120),
            (1500, 700, 1880, 500),
        ],
        "portals": [((525, 600), (1370, 405))],
        "springs": [              # (x, y, dx, dy) — the shove it gives
            (925, 290, 0, -19),
            (1075, 530, 13, -9),
            (870, 930, 11, -15),
        ],
        "door": (1437, MAP_GROUND),
        "stones": [(360, 935), (710, 580), (1135, 940), (1725, 935)],
        "slabs": [(1580, 355, 160, 135)],
    },
]


class Biter:
    """A red one. Walks the ledge it was put on and bites what it reaches."""
    R, HP, DMG = 18, 3, 7

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.home = float(x)
        self.hp = self.HP
        self.face = -1
        self.hurt = 0

    def update(self, px, py):
        if abs(px - self.x) < 190 and abs(py - self.y) < 70:
            self.face = 1 if px > self.x else -1
            self.x += self.face * 1.6
        elif abs(self.x - self.home) > 2:
            self.face = 1 if self.home > self.x else -1
            self.x += self.face * 0.9
        self.x = max(20.0, min(float(WIDTH - 20), self.x))
        if self.hurt:
            self.hurt -= 1

    def rect(self):
        return pygame.Rect(int(self.x) - self.R, int(self.y) - self.R * 2,
                           self.R * 2, self.R * 2)

    def draw(self, surface):
        _c = (255, 230, 230) if self.hurt else (214, 54, 40)
        _x, _y = int(self.x), int(self.y)
        pygame.draw.polygon(surface, _c, [
            (_x - self.R, _y), (_x - self.R, _y - self.R),
            (_x, _y - self.R * 2), (_x + self.R, _y - self.R),
            (_x + self.R, _y)])
        for _i in range(4):       # the jagged mouth off the map
            _tx = _x - self.R + 4 + _i * (self.R * 2 - 8) // 4
            pygame.draw.polygon(surface, (250, 250, 250), [
                (_tx, _y - self.R + 2), (_tx + 5, _y - self.R + 2),
                (_tx + 2, _y - 3)])
        for _sg in (-1, 1):
            pygame.draw.circle(surface, (24, 20, 20),
                               (_x + _sg * 6, _y - self.R - 7), 3)
        for _lg in (-1, 1):
            pygame.draw.line(surface, _c, (_x + _lg * 8, _y),
                             (_x + _lg * 11, _y + 7), 3)


class Guarder:
    """A green one. Stands at the coffin and does not leave it."""
    R, HP, DMG = 15, 4, 6

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.hp = self.HP
        self.hurt = 0
        self.t = 0.0

    def update(self, px, py):
        self.t += 0.05
        if self.hurt:
            self.hurt -= 1

    def rect(self):
        return pygame.Rect(int(self.x) - self.R, int(self.y) - 46,
                           self.R * 2, 46)

    def draw(self, surface):
        _c = (235, 255, 235) if self.hurt else (46, 196, 62)
        _x, _y = int(self.x), int(self.y)
        _sw = int(math.sin(self.t) * 3)
        pygame.draw.circle(surface, _c, (_x + _sw, _y - 38), 9)
        pygame.draw.line(surface, _c, (_x + _sw, _y - 30), (_x, _y - 14), 3)
        for _sg in (-1, 1):       # arms out, holding the ground
            pygame.draw.line(surface, _c, (_x + _sw, _y - 27),
                             (_x + _sg * 11 + _sw, _y - 34), 3)
            pygame.draw.line(surface, _c, (_x, _y - 14),
                             (_x + _sg * 9, _y), 3)
        for _sg in (-1, 1):
            pygame.draw.circle(surface, (16, 70, 22),
                               (_x + _sw + _sg * 3, _y - 40), 2)


class Floater:
    """A yellow one. Runs its line, there and back, and never lands."""
    R, HP, DMG = 16, 2, 8

    def __init__(self, x1, y1, x2, y2):
        self.a, self.b = (float(x1), float(y1)), (float(x2), float(y2))
        self.p = 0.0
        self.dir = 1
        self.hp = self.HP
        self.hurt = 0

    def update(self, px, py):
        _len = max(1.0, math.hypot(self.b[0] - self.a[0], self.b[1] - self.a[1]))
        self.p += self.dir * (1.5 / _len)
        if self.p >= 1.0:
            self.p, self.dir = 1.0, -1
        if self.p <= 0.0:
            self.p, self.dir = 0.0, 1
        if self.hurt:
            self.hurt -= 1

    @property
    def x(self):
        return self.a[0] + (self.b[0] - self.a[0]) * self.p

    @property
    def y(self):
        return self.a[1] + (self.b[1] - self.a[1]) * self.p

    def rect(self):
        return pygame.Rect(int(self.x) - self.R, int(self.y) - self.R,
                           self.R * 2, self.R * 2)

    def draw(self, surface):
        _c = (255, 255, 230) if self.hurt else (238, 214, 44)
        _x, _y = int(self.x), int(self.y)
        pygame.draw.line(surface, (90, 84, 40), (int(self.a[0]), int(self.a[1])),
                         (int(self.b[0]), int(self.b[1])), 1)
        pygame.draw.polygon(surface, _c, [
            (_x, _y - self.R), (_x + self.R, _y),
            (_x, _y + self.R + 6), (_x - self.R, _y)])
        pygame.draw.ellipse(surface, (40, 36, 16),
                            (_x - 7, _y - 5, 14, 9))
        pygame.draw.circle(surface, _c, (_x, _y - 1), 2)


# ── The story ───────────────────────────────────────────────────────────────
# One entry per map, in order. Each carries what is said before you go in
# and what is said once the door is open.
MAPS[0].update({
    "act": "The ask",
    "before": [
        "Wombrocks have been coming over the ridge into Tombstone for the "
        "best part of a year, and nobody in Tombstone fights.",
        "So Tombstone sent two people to ask you about it: a tombstone "
        "called Tombstone, and a black and white lunatic.",
        "They were not asking you to defend anything. They want you to go "
        "east and hit the Wombrocks at home.",
        "First you have to get out of the yard, and the yard is already "
        "full of them.",
    ],
    "after": [
        "The door gives. Past it is the road east, and the road east ends "
        "at Wombrock Town.",
    ],
})

# Who the story puts you in on each map. Tombstone sent two people to ask
# you: a tombstone called Tombstone, and a black and white lunatic, who is
# Legacy Jawke — the old sketch of him, hat and all.
_CAST = ["Legacy Jawke"]


def player_for(idx):
    return _CAST[idx % len(_CAST)]


# What finishing the whole thing is worth.
STORY_REWARD = "He-Who-Shall-Not-Be-Named"


def is_open_today():
    """Story Mode runs on Sundays. Six days a week the chain is back on it
    and Tombstone is behind it, which is where he would rather be anyway."""
    return dev_today().weekday() == 6


def progress(stats):
    """How many chapters are done. Chapters only unlock in order."""
    return int((stats or {}).get("story_progress", 0))


def is_done(stats):
    return progress(stats) >= len(MAPS)


def mark_done(stats, idx):
    """Record a chapter cleared. Returns True if that finished the story."""
    if idx + 1 > progress(stats):
        stats["story_progress"] = idx + 1
    if is_done(stats):
        stats["story_done"] = True
        return True
    return False


# ── Screens ─────────────────────────────────────────────────────────────────
_PAPER   = (232, 226, 210)
_INK     = (38, 34, 32)
_FADED   = (120, 112, 104)
_ACCENT  = (196, 110,  96)


def _wrap(text, font, width):
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if font.size(trial)[0] <= width or not line:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def _char(name):
    return next((c for c in CHARACTERS if c["name"] == name), None)


def _stage_idx(name):
    for i, s in enumerate(STAGES):
        if s["name"] == name:
            return i
    return 0


def narration(lines, title, subtitle, cont="press any key"):
    """A page of story. Returns False if the player quit out of it."""
    shown, hold = 0, 0
    full = "\n".join(lines)
    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN,
                           pygame.FINGERDOWN):
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return False
                if shown < len(full):
                    shown = len(full)        # a key skips the typing
                else:
                    return True
        if shown < len(full):
            shown = min(len(full), shown + 2)
        else:
            hold += 1

        screen.fill((20, 18, 24))
        pygame.draw.rect(screen, (28, 25, 32), (60, 50, WIDTH - 120, HEIGHT - 150))
        pygame.draw.rect(screen, (84, 74, 70), (60, 50, WIDTH - 120, HEIGHT - 150), 2)
        _t = font_medium.render(title, True, _ACCENT)
        screen.blit(_t, (90, 74))
        _s = font_small.render(subtitle, True, _FADED)
        screen.blit(_s, (90, 108))
        pygame.draw.line(screen, (84, 74, 70), (90, 134), (WIDTH - 90, 134), 1)

        _typed = full[:shown].split("\n")
        y = 152
        for para in _typed:
            for ln in _wrap(para, font_small, WIDTH - 200):
                screen.blit(font_small.render(ln, True, (214, 208, 198)), (90, y))
                y += 22
            y += 10
        if shown >= len(full) and (hold // 24) % 2 == 0:
            _c = font_tiny.render(cont, True, (150, 144, 136))
            screen.blit(_c, (WIDTH // 2 - _c.get_width() // 2, HEIGHT - 76))
        pygame.display.flip()


def draw_map_thumb(surface, m, rect):
    """The map at a glance, in the colours it was drawn in."""
    rx, ry, rw, rh = rect
    pygame.draw.rect(surface, (20, 18, 24), rect)
    pygame.draw.rect(surface, (70, 64, 62), rect, 1)
    def _tx(v):
        return rx + int(v * rw / float(MAP_W))
    def _ty(v):
        return ry + int(v * rh / float(MAP_H))
    pygame.draw.line(surface, (92, 86, 74), (rx, _ty(MAP_GROUND)),
                     (rx + rw, _ty(MAP_GROUND)), 1)
    for _a, _b, _c in m.get("platforms", ()):
        pygame.draw.rect(surface, (120, 112, 102),
                         (_tx(_a), _ty(_b), max(2, _tx(_c) - rx), 2))
    for _a, _b in m.get("stones", ()):
        pygame.draw.circle(surface, (150, 148, 156), (_tx(_a), _ty(_b) - 3), 2)
    if m.get("coffin"):
        _cf = m["coffin"]
        pygame.draw.rect(surface, (60, 190, 210),
                         (_tx(_cf[0]), _ty(_cf[1]),
                          max(3, _tx(_cf[2]) - rx), max(2, _ty(_cf[3]) - ry)), 1)
    for _a, _b in m.get("guards", ()):
        pygame.draw.circle(surface, (46, 196, 62), (_tx(_a), _ty(_b) - 3), 2)
    for _a, _b in m.get("biters", ()):
        pygame.draw.circle(surface, (214, 54, 40), (_tx(_a), _ty(_b) - 3), 2)
    for _a, _b, _c, _d in m.get("floaters", ()):
        pygame.draw.line(surface, (160, 146, 40),
                         (_tx(_a), _ty(_b)), (_tx(_c), _ty(_d)), 1)
        pygame.draw.circle(surface, (238, 214, 44), (_tx(_a), _ty(_b)), 2)
    for _p1, _p2 in m.get("portals", ()):
        for _pt in (_p1, _p2):
            pygame.draw.circle(surface, (70, 100, 240),
                               (_tx(_pt[0]), _ty(_pt[1])), 3, 1)
    for _a, _b, _c, _d in m.get("springs", ()):
        pygame.draw.circle(surface, (236, 110, 200), (_tx(_a), _ty(_b)), 2)
    pygame.draw.rect(surface, (176, 120, 56),
                     (_tx(m["door"][0]) - 2, _ty(m["door"][1]) - 8, 4, 8))


def chapter_select(stats):
    """Pick a chapter. Returns its index, or None to leave."""
    done = progress(stats)
    sel  = min(done, len(MAPS) - 1)
    scroll = 0
    t = 0.0
    ROWH, VISIBLE = 30, 11
    LIST_X, LIST_W = 40, 320
    while True:
        clock.tick(FPS)
        t += 0.02
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                if ev.key in (pygame.K_DOWN, pygame.K_s):
                    sel = min(len(MAPS) - 1, sel + 1)
                if ev.key in (pygame.K_UP, pygame.K_w):
                    sel = max(0, sel - 1)
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if sel <= done:
                        return sel
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                _mp = ((int(ev.x * WIDTH), int(ev.y * HEIGHT))
                       if ev.type == pygame.FINGERDOWN else ev.pos)
                for _i in range(VISIBLE):
                    _ci = scroll + _i
                    if _ci >= len(MAPS):
                        break
                    if pygame.Rect(LIST_X, 96 + _i * ROWH, LIST_W,
                                   ROWH - 2).collidepoint(_mp):
                        if _ci == sel and _ci <= done:
                            return _ci
                        sel = _ci
                if pygame.Rect(WIDTH - 130, HEIGHT - 52, 100, 32).collidepoint(_mp):
                    return None
        scroll = max(0, min(sel - VISIBLE + 2, len(MAPS) - VISIBLE))
        scroll = max(0, min(scroll, sel))

        screen.fill((20, 18, 24))
        _h = font_medium.render("STORY MODE", True, _ACCENT)
        screen.blit(_h, (40, 30))
        _hs = font_small.render(
            f"the attack on Wombrock Town  ·  {done} of {len(MAPS)} maps open",
            True, _FADED)
        screen.blit(_hs, (40, 62))

        # ── the chapter list ───────────────────────────────────────────────
        _last_act = None
        for _i in range(VISIBLE):
            _ci = scroll + _i
            if _ci >= len(MAPS):
                break
            ch = MAPS[_ci]
            y  = 96 + _i * ROWH
            locked = _ci > done
            if ch["act"] != _last_act:
                pygame.draw.line(screen, (70, 62, 60), (LIST_X, y - 2),
                                 (LIST_X + LIST_W, y - 2), 1)
            _last_act = ch["act"]
            if _ci == sel:
                pygame.draw.rect(screen, (44, 38, 46),
                                 (LIST_X, y, LIST_W, ROWH - 2), border_radius=4)
                pygame.draw.rect(screen, _ACCENT if not locked else (90, 82, 80),
                                 (LIST_X, y, LIST_W, ROWH - 2), 1, border_radius=4)
            _num = font_tiny.render(f"{_ci + 1:2d}", True, (110, 104, 100))
            screen.blit(_num, (LIST_X + 8, y + 9))
            _col = (96, 90, 88) if locked else (
                (150, 200, 150) if _ci < done else (235, 230, 222))
            _nm = ch["name"] if not locked else "— locked —"
            screen.blit(font_small.render(_nm, True, _col), (LIST_X + 32, y + 5))
            if _ci < done:
                pygame.draw.circle(screen, (110, 200, 120),
                                   (LIST_X + LIST_W - 16, y + 14), 4)

        # ── the map itself ────────────────────────────────────────────────
        ch = MAPS[sel]
        locked = sel > done
        PX, PW = LIST_X + LIST_W + 30, WIDTH - (LIST_X + LIST_W + 30) - 40
        pygame.draw.rect(screen, (28, 25, 32), (PX, 96, PW, HEIGHT - 170))
        pygame.draw.rect(screen, (84, 74, 70), (PX, 96, PW, HEIGHT - 170), 2)
        screen.blit(font_tiny.render(ch["act"].upper(), True, _ACCENT),
                    (PX + 14, 108))
        screen.blit(font_medium.render(
            ch["name"] if not locked else "???", True,
            (235, 230, 222) if not locked else (110, 104, 100)), (PX + 14, 124))
        if locked:
            for _k, _ln in enumerate(_wrap(
                    "Open the door on the map before it. The road east only "
                    "goes one way.", font_small, PW - 28)):
                screen.blit(font_small.render(_ln, True, _FADED),
                            (PX + 14, 170 + _k * 22))
        else:
            _counts = [("enemies", len(ch.get("biters", ()))),
                       ("coffin guarders", len(ch.get("guards", ()))),
                       ("moving", len(ch.get("floaters", ()))),
                       ("portals", len(ch.get("portals", ()))),
                       ("springs", len(ch.get("springs", ())))]
            _y9 = 164
            for _lbl9, _n9 in _counts:
                if not _n9:
                    continue
                screen.blit(font_small.render(_lbl9, True, _FADED), (PX + 14, _y9))
                _nv = font_small.render(str(_n9), True, (226, 220, 212))
                screen.blit(_nv, (PX + PW - 20 - _nv.get_width(), _y9))
                _y9 += 22
            _thumb = pygame.Rect(PX + 14, _y9 + 12, PW - 28, 118)
            draw_map_thumb(screen, ch, _thumb)
            _state = ("open — walk it again" if sel < done
                      else "press ENTER to go in")
            _s2 = font_small.render(_state, True,
                                    (150, 200, 150) if sel < done else _ACCENT)
            screen.blit(_s2, (PX + PW // 2 - _s2.get_width() // 2, HEIGHT - 110))

        if is_done(stats):
            _fin = font_tiny.render(
                f"Story complete — {STORY_REWARD} is yours", True, (255, 200, 90))
            screen.blit(_fin, (40, HEIGHT - 44))
        _b = pygame.Rect(WIDTH - 130, HEIGHT - 52, 100, 32)
        pygame.draw.rect(screen, (40, 36, 44), _b, border_radius=5)
        pygame.draw.rect(screen, (120, 112, 108), _b, 1, border_radius=5)
        _bt = font_small.render("BACK", True, (220, 214, 206))
        screen.blit(_bt, (_b.centerx - _bt.get_width() // 2, _b.y + 6))
        screen.blit(font_tiny.render("up/down picks  ·  enter plays  ·  esc leaves",
                                     True, (110, 104, 100)), (40, HEIGHT - 24))
        pygame.display.flip()
