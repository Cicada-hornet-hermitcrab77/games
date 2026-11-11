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
from fight_data import CHARACTERS, STAGES, POWERUPS
from fight_drawing import draw_stickman

# ── Maps ────────────────────────────────────────────────────────────────────
# A map is drawn on paper at 1920x1080 with the ground line at y=940, so the
# numbers below are read straight off the drawing and squashed onto the real
# screen here. That way a map can be checked against its picture.
MAP_W, MAP_H, MAP_GROUND = 1920, 1080, 940

# The same squash the maps get, applied to whoever is walking them.
FIGHTER_SCALE = round(WIDTH / float(MAP_W), 3)


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
        "skellamorguards": [(305, 125), (715, 125)],
        "wombrocks": [(1850, 330), (1315, MAP_GROUND)],
        "boss": (1150, 130),
        "cylhosts": [             # (x1, y1, x2, y2) — the line it runs
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
        "house": (1390, 500, 430, MAP_GROUND - 500),
        "door": (1437, MAP_GROUND),
        "stones": [(360, 935), (710, 580), (1135, 940), (1725, 935)],
        "slabs": [(1580, 355, 160, 135)],
    },

    # ── Second map: the Wacdonalds store, out on the road east ─────────────
    {
        "name": "The Wacdonalds store",
        "start": (110, 940),
        "platforms": [
            (560, 560, 190),      # the ledge on the way over
            (770, 470,  80),      # the top of the spire
            (960, 700, 160),
            (980, 300, 240),      # the block the sign stands on
            (1100, 555, 440),     # the store roof
            (1480, 700, 150),
        ],
        "walls": [
            (795, 470, 36, MAP_GROUND - 470),      # the spire itself
            (1050, 560, 18, MAP_GROUND - 560),     # the store, left wall
            (1600, 560, 18, MAP_GROUND - 560),     # and right
        ],
        "store": (1050, 560, 570, MAP_GROUND - 560),
        "sign": (1000, 95, 210, 205),
        "movers": [               # (x1, y1, x2, y2, width)
            (1240, 330, 1240, 480, 90),
            (1400, 520, 1700, 520, 110),
            (1760, 560, 1760, 710, 90),
        ],
        "powerspots": [(880, 700), (1375, 940), (1555, 700)],
        "wombrocks": [(800, 470), (1340, 555), (1150, 940)],
        "cylhosts": [
            (520, 120, 790, 340),
            (1260, 175, 1890, 175),
        ],
        "saddled": [(1150, 400, 1880, 400)],
        "boss": (1105, 300),      # the sign comes down off its block
        "door": (1355, MAP_GROUND),
        "door_barred": "DON'T ENTER",
        "stones": [(730, 940)],
        "slabs": [],
    },
]


class MovingPlatform:
    """Orange on the map: a slab that runs between two points, there and
    back, and carries whatever is standing on it."""
    H = 14

    def __init__(self, x1, y1, x2, y2, w, speed=1.6):
        self.a, self.b = (float(x1), float(y1)), (float(x2), float(y2))
        self.w = w
        self.speed = speed
        self.p = 0.0
        self.dir = 1
        self.x, self.y = self.a
        self.dx = self.dy = 0.0

    def update(self):
        _len = max(1.0, math.hypot(self.b[0] - self.a[0], self.b[1] - self.a[1]))
        self.p += self.dir * (self.speed / _len)
        if self.p >= 1.0:
            self.p, self.dir = 1.0, -1
        if self.p <= 0.0:
            self.p, self.dir = 0.0, 1
        _nx = self.a[0] + (self.b[0] - self.a[0]) * self.p
        _ny = self.a[1] + (self.b[1] - self.a[1]) * self.p
        self.dx, self.dy = _nx - self.x, _ny - self.y
        self.x, self.y = _nx, _ny

    def carries(self, px, py):
        """True when somebody is standing on the top of it."""
        return (self.x - 6 <= px <= self.x + self.w + 6
                and -4 <= py - self.y <= 14)

    def draw(self, surface):
        _x, _y = int(self.x), int(self.y)
        pygame.draw.line(surface, (120, 78, 36), (int(self.a[0]) + self.w // 2,
                                                  int(self.a[1]) + 6),
                         (int(self.b[0]) + self.w // 2, int(self.b[1]) + 6), 1)
        pygame.draw.rect(surface, (226, 128, 44), (_x, _y, self.w, self.H),
                         border_radius=3)
        pygame.draw.rect(surface, (250, 178, 96), (_x, _y, self.w, 4),
                         border_radius=2)
        pygame.draw.rect(surface, (138, 70, 20), (_x, _y, self.w, self.H), 2,
                         border_radius=3)


class PowerSpot:
    """Gold on the map: a patch of ground that keeps putting a power-up out.
    Take it and another turns up after a while."""
    EVERY = 420

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.timer = 90
        self.spec = None

    def update(self, px, py, taker):
        if self.spec is None:
            self.timer -= 1
            if self.timer <= 0:
                self.spec = POWERUPS[(int(self.x) + self.timer) % len(POWERUPS)]
                self.timer = self.EVERY
            return
        if abs(px - self.x) < 26 and abs(py - 24 - self.y) < 40:
            taker(self.spec)
            self.spec = None
            self.timer = self.EVERY

    def draw(self, surface):
        _x, _y = int(self.x), int(self.y)
        _t = pygame.time.get_ticks() / 1000.0
        pygame.draw.rect(surface, (214, 176, 54), (_x - 20, _y - 5, 40, 6),
                         border_radius=2)
        pygame.draw.rect(surface, (150, 118, 28), (_x - 20, _y - 5, 40, 6), 1,
                         border_radius=2)
        for _k in range(4):          # the sparks it throws while it charges
            _sp = ((_t * 0.8 + _k * 0.25) % 1.0)
            pygame.draw.circle(surface, (242, 212, 120),
                               (_x - 15 + _k * 10, _y - 8 - int(_sp * 18)),
                               max(1, 3 - int(_sp * 3)))
        if self.spec is None:
            return
        _bob = int(math.sin(_t * 3.0) * 4)
        pygame.draw.circle(surface, self.spec.get("color", (240, 200, 90)),
                           (_x, _y - 26 + _bob), 11)
        pygame.draw.circle(surface, (250, 250, 250), (_x, _y - 26 + _bob), 11, 2)
        _lbl = font_tiny.render(self.spec["name"][:9], True, (236, 230, 220))
        surface.blit(_lbl, (_x - _lbl.get_width() // 2, _y - 54 + _bob))


class Wombrock:
    """A Wombrock: a headstone that grew a mouth and got up. It comes after
    you from wherever it is standing, and it never stops — it is only slow.
    This is the thing that has been coming over the ridge into Tombstone."""
    R, HP, DMG, SPEED = 18, 80, 10, 6.0
    RANGE, REACH = 250, 100      # how far it notices you, how far it leans

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.home = float(x)
        self.hp = self.HP
        self.face = -1
        self.hurt = 0
        self.awake = False

    def update(self, px, py):
        self.awake = (abs(px - self.x) < self.RANGE
                      and abs(py - self.y) < self.REACH)
        if self.awake and abs(px - self.x) > 3:
            self.face = 1 if px > self.x else -1
            self.x += self.face * self.SPEED
        self.x = max(20.0, min(float(WIDTH - 20), self.x))
        if self.hurt:
            self.hurt -= 1

    def rect(self):
        return pygame.Rect(int(self.x) - self.R, int(self.y) - self.R * 2,
                           self.R * 2, self.R * 2)

    def hp_bar(self, surface, top):
        if self.hp >= self.HP:
            return
        _w = 34
        _x = int(self.x) - _w // 2
        pygame.draw.rect(surface, (36, 32, 34), (_x, top, _w, 5))
        pygame.draw.rect(surface, (214, 70, 54),
                         (_x, top, int(_w * max(0, self.hp) / self.HP), 5))
        pygame.draw.rect(surface, (120, 112, 108), (_x, top, _w, 5), 1)

    def draw(self, surface):
        _c = (255, 230, 230) if self.hurt else (168, 150, 152)
        _dk = (255, 240, 240) if self.hurt else (104, 92, 98)
        _vein = (255, 200, 190) if self.hurt else (206, 48, 36)
        _x, _y = int(self.x), int(self.y)
        _h = self.R * 2 + 6
        # the stone: square shoulders, arched top, exactly like the ones it
        # is standing among — except this one opened
        pygame.draw.rect(surface, _c, (_x - self.R, _y - _h + self.R,
                                       self.R * 2, _h - self.R))
        pygame.draw.circle(surface, _c, (_x, _y - _h + self.R), self.R)
        pygame.draw.rect(surface, _dk, (_x - self.R, _y - _h + self.R,
                                        self.R * 2, _h - self.R), 2)
        pygame.draw.arc(surface, _dk, (_x - self.R, _y - _h, self.R * 2,
                                       self.R * 2), 0.0, 3.1416, 2)
        for _k in range(3):        # the cracks it opened along
            _cy = _y - _h + self.R + 6 + _k * 7
            pygame.draw.line(surface, _vein, (_x - self.R + 2, _cy),
                             (_x - 2 + (_k % 2) * 8, _cy + 4), 2)
        pygame.draw.ellipse(surface, (74, 112, 60),   # moss along the foot
                            (_x - self.R, _y - 8, self.R * 2, 9))
        # the mouth, across the face of it, chewing
        _gape = 5 + int(abs(math.sin(self.x * 0.09)) * 4)
        _my0 = _y - self.R - 2
        pygame.draw.rect(surface, (118, 22, 20),
                         (_x - self.R + 3, _my0 - _gape // 2,
                          self.R * 2 - 6, _gape))
        pygame.draw.rect(surface, (210, 70, 46),
                         (_x - self.R + 3, _my0 - _gape // 2,
                          self.R * 2 - 6, max(1, _gape // 3)))
        for _i in range(5):
            _tx = _x - self.R + 4 + _i * (self.R * 2 - 8) // 5
            _tw = max(2, (self.R * 2 - 8) // 6)
            pygame.draw.polygon(surface, (248, 246, 240), [
                (_tx, _my0 - _gape // 2), (_tx + _tw, _my0 - _gape // 2),
                (_tx + _tw // 2, _my0 - _gape // 2 + _gape - 1)])
            pygame.draw.polygon(surface, (248, 246, 240), [
                (_tx, _my0 + _gape // 2), (_tx + _tw, _my0 + _gape // 2),
                (_tx + _tw // 2, _my0 + _gape // 2 - _gape + 1)])
        for _sg in (-1, 1):       # eyes up where the name would be
            pygame.draw.circle(surface, (252, 236, 150),
                               (_x + _sg * 7, _y - _h + self.R - 2), 4)
            pygame.draw.circle(surface, (210, 70, 20),
                               (_x + _sg * 7 + self.face * 2,
                                _y - _h + self.R - 2), 2)
        for _lg in (-1, 1):       # the little legs it walks on
            pygame.draw.line(surface, _dk, (_x + _lg * 8, _y),
                             (_x + _lg * 11, _y + 7), 3)


class Skellamorguard:
    """A skeleton that came up out of the ground by the coffin, and that is
    where it stays — it guards, it does not hunt. There is a great deal of
    it to get through."""
    R, HP, DMG, SPEED = 15, 210, 10, 0.0
    RANGE, REACH = 90, 70        # it only ever notices what is on top of it
    BONE, DARK = (238, 234, 218), (168, 160, 138)

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.hp = self.HP
        self.hurt = 0
        self.awake = False
        self.t = 0.0

    def update(self, px, py):
        self.t += 0.06
        self.awake = (abs(px - self.x) < self.RANGE
                      and abs(py - self.y) < self.REACH)
        self.face = 1 if px > self.x else -1   # it watches you; it does not follow
        if self.hurt:
            self.hurt -= 1

    def rect(self):
        return pygame.Rect(int(self.x) - self.R, int(self.y) - 52,
                           self.R * 2, 52)

    def hp_bar(self, surface, top):
        """Only once it has been hit — an untouched yard is not a HUD."""
        if self.hp >= self.HP:
            return
        _w = 34
        _x = int(self.x) - _w // 2
        pygame.draw.rect(surface, (36, 32, 34), (_x, top, _w, 5))
        pygame.draw.rect(surface, (214, 70, 54),
                         (_x, top, int(_w * max(0, self.hp) / self.HP), 5))
        pygame.draw.rect(surface, (120, 112, 108), (_x, top, _w, 5), 1)

    def draw(self, surface):
        _b = (255, 120, 120) if self.hurt else self.BONE
        _d = (210, 90, 90) if self.hurt else self.DARK
        _x, _y = int(self.x), int(self.y)
        _sw = int(math.sin(self.t) * 2)
        _f = getattr(self, "face", 1)
        # legs
        for _sg in (-1, 1):
            pygame.draw.line(surface, _b, (_x + _sg * 3, _y - 22),
                             (_x + _sg * 7, _y - 10), 3)
            pygame.draw.line(surface, _b, (_x + _sg * 7, _y - 10),
                             (_x + _sg * 8, _y), 3)
            pygame.draw.circle(surface, _d, (_x + _sg * 7, _y - 10), 2)
        # spine and ribs
        pygame.draw.line(surface, _b, (_x + _sw, _y - 42), (_x, _y - 22), 3)
        for _k in range(4):
            _ry = _y - 40 + _k * 5
            pygame.draw.arc(surface, _b, (_x - 9 + _sw, _ry - 4, 18, 10),
                            3.34, 6.08, 2)
        # arms, held out over the ground it is guarding
        for _sg in (-1, 1):
            pygame.draw.line(surface, _b, (_x + _sw, _y - 39),
                             (_x + _sg * 12 + _sw, _y - 33), 3)
            pygame.draw.line(surface, _b, (_x + _sg * 12 + _sw, _y - 33),
                             (_x + _sg * 15 + _sw, _y - 42 + (_sg * _sw)), 3)
            for _fg in range(3):   # finger bones
                pygame.draw.line(surface, _b,
                                 (_x + _sg * 15 + _sw, _y - 42 + (_sg * _sw)),
                                 (_x + _sg * (16 + _fg * 2) + _sw,
                                  _y - 48 + _fg), 1)
        # the skull
        _sx, _sy = _x + _sw, _y - 50
        pygame.draw.circle(surface, _b, (_sx, _sy), 9)
        pygame.draw.rect(surface, _b, (_sx - 6, _sy + 5, 12, 7),
                         border_radius=2)
        for _sg in (-1, 1):
            pygame.draw.circle(surface, (24, 22, 26),
                               (_sx + _sg * 4 + _f, _sy - 1), 3)
            pygame.draw.circle(surface, (120, 220, 140),
                               (_sx + _sg * 4 + _f, _sy - 1), 1)
        pygame.draw.polygon(surface, (24, 22, 26), [
            (_sx - 1, _sy + 3), (_sx + 1, _sy + 3), (_sx, _sy + 6)])
        for _k in range(3):        # teeth
            pygame.draw.line(surface, _d, (_sx - 4 + _k * 4, _sy + 6),
                             (_sx - 4 + _k * 4, _sy + 11), 1)


class Wolf:
    """The one on top. Wolf-shaped, red, and the only thing in the yard that
    comes looking for you. The door does not open while it is up."""
    W, H, HP, DMG, SPEED = 34, 26, 100, 14, 8.0
    RANGE, REACH = 340, 170      # it ranges further than anything else here
    GONE_EVERY, GONE_FOR = 240, 90     # vanishes every 4s, for a second and a half

    def __init__(self, x, y, plats=()):
        self.x, self.y = float(x), float(y)
        self.hp = self.HP
        self.face = -1
        self.hurt = 0
        self.vy = 0.0
        self.lunge = 0
        self.cool = 90
        self.t = 0.0
        self.age = 0
        self.awake = False
        self.asleep = True      # it is having a lie down until you start it
        self.plats = list(plats)

    def wake(self):
        """Hit it once and it is up, and it does not go back down."""
        self.asleep = False
        self.age = 0            # the vanishing clock starts when it does

    @property
    def unseen(self):
        """Completely gone — not faded, not a shimmer. Still biting."""
        if self.asleep:
            return False        # you can always see a sleeping one
        return (self.age % self.GONE_EVERY) >= (self.GONE_EVERY - self.GONE_FOR)

    def _floor_under(self):
        """The nearest thing it can stand on at or below where it is."""
        best = float(GROUND_Y)
        for pl in self.plats:
            if pl.x - 8 <= self.x <= pl.x + pl.w + 8 and pl.y >= self.y - 6:
                best = min(best, float(pl.y))
        return best

    def update(self, px, py):
        self.t += 0.1
        if self.asleep:
            # Nothing. Not a step, not a bite. Wake it yourself.
            self.awake = False
            self.vy += 0.5
            self.y = min(self.y + self.vy, self._floor_under())
            if self.y >= self._floor_under():
                self.y, self.vy = self._floor_under(), 0.0
            return
        self.age += 1
        self.awake = (abs(px - self.x) < self.RANGE
                      and abs(py - self.y) < self.REACH)
        self.face = 1 if px > self.x else -1
        if self.cool:
            self.cool -= 1
        if self.lunge:
            self.lunge -= 1
            self.x += self.face * (self.SPEED * 1.8)
        elif self.awake and not self.cool and abs(px - self.x) < 260:
            self.lunge, self.cool = 22, 130
            self.vy = -8.5
        elif self.awake:
            self.x += self.face * (self.SPEED * 0.42)
        self.vy += 0.5
        self.y += self.vy
        _fl = self._floor_under()
        if self.y >= _fl and self.vy >= 0:
            self.y, self.vy = _fl, 0.0
        self.x = max(24.0, min(float(WIDTH - 24), self.x))
        if self.hurt:
            self.hurt -= 1

    def rect(self):
        return pygame.Rect(int(self.x) - self.W, int(self.y) - self.H - 12,
                           self.W * 2, self.H + 12)

    def draw(self, surface):
        if self.unseen:
            return                      # you will know where it is soon enough
        if self.asleep:
            self._draw_asleep(surface)
            return
        _c = (255, 226, 226) if self.hurt else (198, 56, 40)
        _dk = (255, 240, 240) if self.hurt else (116, 24, 22)
        _lt = (255, 246, 246) if self.hurt else (238, 128, 72)
        _x, _y = int(self.x), int(self.y)
        _f = self.face
        _gait = int(math.sin(self.t * 1.6) * 3)
        for _lg, _ph in ((-20, 0.0), (-8, 1.6), (10, 0.8), (22, 2.4)):
            _sw = int(math.sin(self.t * 1.6 + _ph) * 4)
            pygame.draw.line(surface, _dk, (_x + _lg, _y - 12),
                             (_x + _lg + _sw, _y), 5)
        pygame.draw.ellipse(surface, _c, (_x - 30, _y - 32, 60, 24))
        pygame.draw.ellipse(surface, _lt, (_x - 24, _y - 29, 40, 9))
        pygame.draw.ellipse(surface, _dk, (_x - 30, _y - 32, 60, 24), 2)
        for _k in range(5):          # the ridge down its back
            pygame.draw.polygon(surface, (252, 176, 60), [
                (_x - 22 + _k * 11, _y - 31),
                (_x - 16 + _k * 11, _y - 42),
                (_x - 10 + _k * 11, _y - 31)])
            pygame.draw.polygon(surface, _dk, [
                (_x - 22 + _k * 11, _y - 31),
                (_x - 16 + _k * 11, _y - 42),
                (_x - 10 + _k * 11, _y - 31)], 1)
        pygame.draw.line(surface, _c, (_x - _f * 28, _y - 26),
                         (_x - _f * 44, _y - 38 + _gait), 6)   # the tail
        _hx = _x + _f * 30
        _hy = _y - 38
        pygame.draw.polygon(surface, _c, [
            (_hx - _f * 12, _hy - 10), (_hx + _f * 20, _hy - 4),
            (_hx + _f * 18, _hy + 12), (_hx - _f * 12, _hy + 14)])
        for _sg in (-1, 1):          # ears up
            pygame.draw.polygon(surface, _c, [
                (_hx - _f * 8, _hy - 8), (_hx - _f * 2 + _sg * 2, _hy - 24),
                (_hx + _f * 4, _hy - 8)])
        _gape = 4 + int(abs(math.sin(self.t * 1.1)) * 7)
        pygame.draw.polygon(surface, (22, 12, 14), [
            (_hx + _f * 2, _hy + 4), (_hx + _f * 21, _hy - 1 - _gape // 2),
            (_hx + _f * 21, _hy + 7 + _gape // 2)])
        for _k in range(4):
            _tx = _hx + _f * (6 + _k * 4)
            pygame.draw.polygon(surface, (248, 246, 240), [
                (_tx, _hy + 1), (_tx + _f * 3, _hy + 1),
                (_tx + _f * 1, _hy + 1 + _gape // 2 + 2)])
        pygame.draw.circle(surface, (252, 220, 90), (_hx + _f * 6, _hy - 4), 4)
        pygame.draw.circle(surface, (22, 12, 14), (_hx + _f * 7, _hy - 4), 2)
        # how much of it is left, over its head
        _bw = 54
        pygame.draw.rect(surface, (40, 36, 36), (_x - _bw // 2, _y - 58, _bw, 6))
        pygame.draw.rect(surface, (214, 54, 40),
                         (_x - _bw // 2, _y - 58,
                          int(_bw * max(0, self.hp) / self.HP), 6))
        pygame.draw.rect(surface, (120, 112, 108), (_x - _bw // 2, _y - 58, _bw, 6), 1)


    def _draw_asleep(self, surface):
        """Curled up on the ledge, which is the only time you get a free
        shot at it."""
        _c = (255, 226, 226) if self.hurt else (168, 50, 38)
        _dk = (255, 240, 240) if self.hurt else (104, 22, 20)
        _x, _y = int(self.x), int(self.y)
        _br = int(math.sin(self.t * 0.5) * 2)
        pygame.draw.ellipse(surface, _c, (_x - 34, _y - 24 - _br, 68, 24 + _br))
        pygame.draw.ellipse(surface, _dk, (_x - 34, _y - 24 - _br, 68, 24 + _br), 2)
        for _k in range(4):              # the ridge, flat while it sleeps
            pygame.draw.polygon(surface, (182, 128, 48), [
                (_x - 20 + _k * 12, _y - 23 - _br),
                (_x - 15 + _k * 12, _y - 30 - _br),
                (_x - 10 + _k * 12, _y - 23 - _br)])
        pygame.draw.ellipse(surface, _c, (_x + 14, _y - 20, 26, 16))   # the head
        pygame.draw.ellipse(surface, _dk, (_x + 14, _y - 20, 26, 16), 2)
        pygame.draw.line(surface, _dk, (_x + 22, _y - 13), (_x + 32, _y - 13), 2)
        for _sg in (-1, 1):              # ears folded back
            pygame.draw.polygon(surface, _c, [
                (_x + 16, _y - 18), (_x + 10, _y - 26 + _sg), (_x + 21, _y - 19)])
        pygame.draw.arc(surface, _c, (_x - 46, _y - 22, 26, 20), 0.6, 2.6, 5)
        for _k in range(3):              # three Zs, drifting
            _zp = (self.t * 0.35 + _k * 0.33) % 1.0
            _zx = _x + 24 + int(_zp * 16)
            _zy = _y - 26 - int(_zp * 26)
            _zs = 4 + _k
            pygame.draw.lines(surface, (236, 230, 240), False, [
                (_zx, _zy), (_zx + _zs, _zy),
                (_zx, _zy + _zs), (_zx + _zs, _zy + _zs)], 2)


class Wacdubbletomatsplusletusgost:
    """The sign off the top of the store, and the full name is on the menu
    board: Wac, dubble, tomats, plus letus, gost. Everything on it is in
    there, including the gost, which is the part that is alive. Hit the
    burger and you are hitting it; it is holding on from in between the
    patties."""
    W, H, HP, DMG, SPEED = 42, 58, 160, 13, 5.0
    RANGE, REACH = 400, 220

    def __init__(self, x, y, plats=()):
        self.x, self.y = float(x), float(y)
        self.hp = self.HP
        self.face = -1
        self.hurt = 0
        self.vy = 0.0
        self.t = 0.0
        self.hop = 0
        self.awake = False
        self.asleep = True
        self.plats = list(plats)

    def wake(self):
        self.asleep = False

    def _floor_under(self):
        best = float(GROUND_Y)
        for pl in self.plats:
            if pl.x - 10 <= self.x <= pl.x + pl.w + 10 and pl.y >= self.y - 6:
                best = min(best, float(pl.y))
        return best

    def update(self, px, py):
        self.t += 0.1
        if self.asleep:
            self.awake = False
            return
        self.awake = (abs(px - self.x) < self.RANGE
                      and abs(py - self.y) < self.REACH)
        self.face = 1 if px > self.x else -1
        if self.awake:
            if self.hop:
                self.hop -= 1
            elif self.vy == 0.0:
                self.vy, self.hop = -9.5, 40      # it does not run, it bounces
            self.x += self.face * self.SPEED * (0.9 if self.vy else 0.3)
        self.vy += 0.5
        self.y += self.vy
        _fl = self._floor_under()
        if self.y >= _fl and self.vy >= 0:
            self.y, self.vy = _fl, 0.0
        self.x = max(30.0, min(float(WIDTH - 30), self.x))
        if self.hurt:
            self.hurt -= 1

    def rect(self):
        return pygame.Rect(int(self.x) - self.W, int(self.y) - self.H,
                           self.W * 2, self.H)

    def draw(self, surface):
        _x, _y = int(self.x), int(self.y)
        _f = 1.0 if not self.hurt else 1.6
        _bun = (236, 176, 86) if not self.hurt else (255, 235, 220)
        _top = _y - self.H
        pygame.draw.rect(surface, (196, 140, 60), (_x - 40, _y - 10, 80, 10),
                         border_radius=4)          # the bottom bun
        pygame.draw.rect(surface, (142, 74, 44), (_x - 42, _y - 18, 84, 9),
                         border_radius=3)          # dubble — patty one
        for _tm in (-22, 0, 22):                   # tomats
            pygame.draw.ellipse(surface, (206, 48, 44),
                                (_x + _tm - 15, _y - 25, 30, 9))
            pygame.draw.ellipse(surface, (236, 110, 96),
                                (_x + _tm - 9, _y - 23, 18, 5))
        pygame.draw.rect(surface, (142, 74, 44), (_x - 42, _y - 33, 84, 9),
                         border_radius=3)          # patty two
        pygame.draw.polygon(surface, (96, 168, 72), [   # plus letus
            (_x - 44, _y - 33), (_x - 30, _y - 41), (_x - 12, _y - 33),
            (_x + 8, _y - 41), (_x + 26, _y - 33), (_x + 44, _y - 39),
            (_x + 42, _y - 31), (_x - 42, _y - 31)])
        pygame.draw.ellipse(surface, (238, 196, 72), (_x - 36, _y - 45, 72, 14))
        pygame.draw.ellipse(surface, _bun, (_x - 40, _top, 80, 44))   # top bun
        pygame.draw.ellipse(surface, (176, 120, 46), (_x - 40, _top, 80, 44), 2)
        for _sx2, _sy2 in ((-18, 10), (4, 6), (20, 16), (-6, 20)):
            pygame.draw.circle(surface, (252, 242, 212),
                               (_x + _sx2, _top + _sy2), 3)
        # ── the one actually doing it ─────────────────────────────────
        # A ghost, wedged in between the bun and the patty, with its arms
        # out through the sides of the burger.
        _gy5 = _y - 34
        _wob = int(math.sin(self.t * (0.6 if self.asleep else 2.1)) * 3)
        _gsurf = pygame.Surface((110, 70), pygame.SRCALPHA)
        _alpha = 120 if self.asleep else 215
        _gc = (226, 238, 250, _alpha)
        pygame.draw.ellipse(_gsurf, _gc, (40 + _wob, 4, 30, 32))
        pygame.draw.polygon(_gsurf, _gc, [            # the ragged hem
            (40 + _wob, 26), (70 + _wob, 26), (70 + _wob, 48),
            (63 + _wob, 39), (55 + _wob, 50), (47 + _wob, 39),
            (40 + _wob, 48)])
        for _sg in (-1, 1):                           # arms out of the sides
            pygame.draw.line(_gsurf, _gc, (55 + _wob, 22),
                             (55 + _sg * 48 + _wob, 30 + _sg * 4), 6)
        surface.blit(_gsurf, (_x - 55, _gy5 - 14))
        if self.asleep:
            pygame.draw.arc(surface, (40, 54, 74),
                            (_x - 12 + _wob, _gy5 - 2, 11, 8), 3.4, 6.0, 2)
            pygame.draw.arc(surface, (40, 54, 74),
                            (_x + 2 + _wob, _gy5 - 2, 11, 8), 3.4, 6.0, 2)
            for _k in range(3):
                _zp = (self.t * 0.3 + _k * 0.33) % 1.0
                pygame.draw.lines(surface, (236, 230, 240), False, [
                    (_x + 34 + int(_zp * 14), _top - int(_zp * 22)),
                    (_x + 39 + int(_zp * 14), _top - int(_zp * 22)),
                    (_x + 34 + int(_zp * 14), _top + 5 - int(_zp * 22)),
                    (_x + 39 + int(_zp * 14), _top + 5 - int(_zp * 22))], 2)
        else:
            for _sg in (-1, 1):                       # wide, and not blinking
                pygame.draw.ellipse(surface, (18, 24, 38),
                                    (_x - 11 + _wob + (0 if _sg < 0 else 13),
                                     _gy5 - 3, 9, 12))
                pygame.draw.circle(surface, (142, 222, 255),
                                   (_x - 7 + _wob + (0 if _sg < 0 else 13)
                                    + self.face * 2, _gy5 + 2), 3)
            _gape = 5 + int(abs(math.sin(self.t * 1.2)) * 9)
            pygame.draw.ellipse(surface, (18, 24, 38),
                                (_x - 6 + _wob, _gy5 + 13, 12, _gape))
        _nm5 = font_tiny.render("WACDUBBLETOMATSPLUSLETUSGOST", True,
                                (206, 198, 190))
        surface.blit(_nm5, (_x - _nm5.get_width() // 2, _top - 28))
        _bw = 80
        pygame.draw.rect(surface, (40, 36, 36), (_x - _bw // 2, _top - 14, _bw, 7))
        pygame.draw.rect(surface, (226, 86, 54),
                         (_x - _bw // 2, _top - 14,
                          int(_bw * max(0, self.hp) / self.HP), 7))
        pygame.draw.rect(surface, (120, 112, 108), (_x - _bw // 2, _top - 14, _bw, 7), 1)


class Cylhost:
    """Strung on a wire, running it end to end for ever. It does not care
    where you are — it is your job to not be on the wire. You cannot kill
    one. Hitting it only tells you that."""
    R, DMG, SPEED = 16, 5, 8.0
    HP = float("inf")
    RANGE, REACH = 70, 60        # it runs its wire; you have to be on it

    def __init__(self, x1, y1, x2, y2, saddle=False):
        self.a, self.b = (float(x1), float(y1)), (float(x2), float(y2))
        self.p = 0.0
        self.dir = 1
        self.hp = self.HP
        self.hurt = 0
        self.awake = False
        self.saddle = saddle      # a saddled one is a ride, not a hazard
        self.ridden = False

    def __repr__(self):
        return f"<Cylhost {self.a}->{self.b}>"

    def update(self, px, py):
        _len = max(1.0, math.hypot(self.b[0] - self.a[0], self.b[1] - self.a[1]))
        self.awake = (abs(px - self.x) < self.RANGE
                      and abs(py - self.y) < self.REACH
                      and not (self.saddle and self.ridden))
        self.p += self.dir * (self.SPEED / _len)
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

    def hp_bar(self, surface, top):
        return          # there is no bar to draw for something endless

    def draw(self, surface):
        _c = (255, 255, 230) if self.hurt else (246, 206, 48)
        _x, _y = int(self.x), int(self.y)
        _glow = pygame.Surface((self.R * 5, self.R * 5), pygame.SRCALPHA)
        pygame.draw.circle(_glow, (246, 206, 48, 46),
                           (self.R * 2 + 2, self.R * 2 + 2), self.R * 2)
        surface.blit(_glow, (_x - self.R * 2 - 2, _y - self.R * 2 - 2))
        pygame.draw.line(surface, (90, 84, 40), (int(self.a[0]), int(self.a[1])),
                         (int(self.b[0]), int(self.b[1])), 1)
        pygame.draw.polygon(surface, _c, [
            (_x, _y - self.R), (_x + self.R, _y),
            (_x, _y + self.R + 6), (_x - self.R, _y)])
        pygame.draw.polygon(surface, (255, 238, 150), [
            (_x, _y - self.R), (_x + self.R // 2, _y - self.R // 3),
            (_x, _y), (_x - self.R // 2, _y - self.R // 3)])
        pygame.draw.ellipse(surface, (248, 250, 252), (_x - 8, _y - 6, 16, 11))
        pygame.draw.circle(surface, (40, 110, 180), (_x + 1, _y - 1), 4)
        pygame.draw.circle(surface, (12, 14, 20), (_x + 1, _y - 1), 2)
        if self.saddle:           # the thing that makes it a ride
            pygame.draw.rect(surface, (142, 138, 150),
                             (_x - 13, _y - self.R - 6, 26, 8),
                             border_radius=2)
            for _k in range(3):
                pygame.draw.rect(surface, (206, 204, 214),
                                 (_x - 10 + _k * 8, _y - self.R - 11, 5, 6))
            pygame.draw.rect(surface, (96, 92, 104),
                             (_x - 13, _y - self.R - 6, 26, 8), 1,
                             border_radius=2)


# ── The story ───────────────────────────────────────────────────────────────
# One entry per map, in order. Each carries what is said before you go in
# and what is said once the door is open.
MAPS[1].update({
    "act": "The road east",
    "boss_class": "Wacdubbletomatsplusletusgost",
    "boss_name": "Wacdubbletomatsplusletusgost",
    "before": [
        "The road east has one building on it and the building is a "
        "Wacdonalds. Nobody has ever established who it is for.",
        "The front door has DON'T ENTER across it in somebody's handwriting, "
        "which is the clearest sign yet that you are going the right way.",
        "The sign on the roof is a burger four feet across and the menu "
        "board gives its whole name: the Wacdubbletomatsplusletusgost. Wac, "
        "dubble, tomats, plus letus, gost. Every word of that is in there.",
        "The gost is the part that is alive, and it is asleep between the "
        "patties with its arms out through the sides. It will not be asleep "
        "for long.",
    ],
    "after": [
        "The burger comes apart — two patties, three tomats and the letus "
        "— and the gost goes out of the back of the store without looking "
        "at you. It was the last word on the menu board and it was the only "
        "one that mattered.",
        "There is a saddled Cylhost going east along a wire over the store, "
        "and a Cylhost going east is the fastest thing on this road.",
    ],
})

MAPS[0].update({
    "act": "The ask",
    "boss_class": "Wolf",
    "boss_name": "wolf",
    "before": [
        "Wombrocks have been coming over the ridge into Tombstone for the "
        "best part of a year, and nobody in Tombstone fights.",
        "So Tombstone sent two people to ask you about it: a tombstone "
        "called Tombstone, and a black and white lunatic. You are the one "
        "they asked, and you brought the gun.",
        "They were not asking you to defend anything. They want you to go "
        "east and hit the Wombrocks at home.",
        "First you have to get out of the yard, and the yard is already "
        "full of them.",
    ],
    "after": [
        "The wolf is down, and the yard is yours.",
        "The house on the right has a door in it, and the door opens. What "
        "is behind it is not the end of anything — it is the way further "
        "in, and that is for next time.",
    ],
})

# Who the story puts you in on each map. Tombstone sent two people to ask
# YOU — a tombstone called Tombstone, and a black and white lunatic, who is
# Legacy Jawke. You are the one they asked, and you walk the first yard as
# the Gunner, because the Wombrocks do not let you close.
_CAST = ["Gunner", "Gunner"]


def player_for(idx):
    return _CAST[idx % len(_CAST)]


# What finishing the whole thing is worth, in coins. Tombstone came to ask
# you for a favour; he is good for it.
STORY_REWARD = 250


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
    for _a, _b in m.get("skellamorguards", ()):
        pygame.draw.circle(surface, (46, 196, 62), (_tx(_a), _ty(_b) - 3), 2)
    for _a, _b in m.get("wombrocks", ()):
        pygame.draw.circle(surface, (214, 54, 40), (_tx(_a), _ty(_b) - 3), 2)
    for _a, _b, _c, _d in m.get("cylhosts", ()):
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
            _counts = [("enemies", len(ch.get("wombrocks", ()))),
                       ("skellamorguards", len(ch.get("skellamorguards", ()))),
                       ("cylhosts", len(ch.get("cylhosts", ()))),
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
