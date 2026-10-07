"""
Achievements — badges you earn for doing things, some of them worth coins.

Each entry is one row in ACHIEVEMENTS: an id that is stored in the save file,
the name and line of text the player reads, the coin reward, the badge art to
draw, and a check that looks at the ordinary stats dict. Nothing here tracks
anything of its own; every condition is read off the stats the game already
keeps, so adding an achievement is one row and (if it needs new art) one badge
function.

    check_achievements(stats, unlocked, userdata) -> [newly earned entries]

awards any that have come true, pays out their coins, and records them in
stats["achievements"]. Call it after anything that could earn one.
"""
import math
import time

import pygame

from constants import WHITE


# ---------------------------------------------------------------------------
# Badge art — each draws itself inside a box of side 2*r centred on (cx, cy)
# ---------------------------------------------------------------------------

def _badge_crown(surf, cx, cy, r):
    gold, deep, jewel = (255, 206, 70), (176, 132, 20), (220, 60, 90)
    base_y = cy + int(r * 0.52)
    pts = [(cx - r, base_y), (cx - r, cy - int(r * 0.45))]
    for i, up in enumerate((0.95, 0.55, 0.95)):          # three spikes
        x0 = cx - r + int(r * 2 * (i / 3.0))
        pts.append((x0 + int(r * 0.33), cy - int(r * up)))
        pts.append((x0 + int(r * 0.66), cy - int(r * 0.35)))
    pts += [(cx + r, cy - int(r * 0.45)), (cx + r, base_y)]
    pygame.draw.polygon(surf, gold, pts)
    pygame.draw.polygon(surf, deep, pts, max(1, r // 10))
    pygame.draw.rect(surf, deep, (cx - r, base_y - int(r * 0.12), r * 2, int(r * 0.34)),
                     border_radius=max(1, r // 6))
    pygame.draw.rect(surf, gold, (cx - r, base_y - int(r * 0.12), r * 2, int(r * 0.34)),
                     max(1, r // 12), border_radius=max(1, r // 6))
    for i, dx in enumerate((-0.55, 0.0, 0.55)):          # jewels along the band
        pygame.draw.circle(surf, jewel, (cx + int(r * dx), base_y + int(r * 0.05)),
                           max(2, r // 7))


def _badge_lhat(surf, cx, cy, r):
    """A dunce-ish triangle hat with an L on it."""
    cloth, shade = (120, 110, 190), (72, 64, 128)
    tip  = (cx, cy - int(r * 0.95))
    left = (cx - int(r * 0.78), cy + int(r * 0.7))
    right = (cx + int(r * 0.78), cy + int(r * 0.7))
    pygame.draw.polygon(surf, cloth, [tip, left, right])
    pygame.draw.polygon(surf, shade, [tip, left, right], max(1, r // 10))
    pygame.draw.rect(surf, shade, (cx - int(r * 0.9), cy + int(r * 0.62),
                                   int(r * 1.8), int(r * 0.26)),
                     border_radius=max(1, r // 8))
    # the L
    lw = max(2, r // 7)
    lx, ly = cx - int(r * 0.16), cy - int(r * 0.22)
    pygame.draw.line(surf, WHITE, (lx, ly), (lx, ly + int(r * 0.6)), lw)
    pygame.draw.line(surf, WHITE, (lx, ly + int(r * 0.6)),
                     (lx + int(r * 0.42), ly + int(r * 0.6)), lw)


def _badge_saintnix(surf, cx, cy, r):
    """Saint Nix: red hat with a white trim and bobble, over a bearded face."""
    skin, beard = (242, 214, 196), (248, 248, 252)
    red, trim   = (196, 48, 46), (240, 240, 245)
    pygame.draw.circle(surf, skin, (cx, cy + int(r * 0.12)), int(r * 0.62))
    pygame.draw.circle(surf, beard, (cx, cy + int(r * 0.42)), int(r * 0.55))
    pygame.draw.rect(surf, skin, (cx - int(r * 0.42), cy - int(r * 0.22),
                                  int(r * 0.84), int(r * 0.5)))
    for dx in (-0.22, 0.22):                              # eyes
        pygame.draw.circle(surf, (40, 36, 34), (cx + int(r * dx), cy - int(r * 0.02)),
                           max(1, r // 10))
    pygame.draw.circle(surf, (214, 120, 110), (cx, cy + int(r * 0.2)), max(1, r // 8))
    pygame.draw.polygon(surf, red, [(cx - int(r * 0.7), cy - int(r * 0.22)),
                                    (cx + int(r * 0.7), cy - int(r * 0.22)),
                                    (cx + int(r * 0.78), cy - int(r * 0.95))])
    pygame.draw.rect(surf, trim, (cx - int(r * 0.74), cy - int(r * 0.34),
                                  int(r * 1.5), int(r * 0.26)),
                     border_radius=max(1, r // 8))
    pygame.draw.circle(surf, trim, (cx + int(r * 0.8), cy - int(r * 0.97)), max(2, r // 5))


def _badge_friends(surf, cx, cy, r):
    """Two stickmen, side by side."""
    for dx, col in ((-0.42, (90, 150, 240)), (0.42, (235, 90, 90))):
        x  = cx + int(r * dx)
        hy = cy - int(r * 0.42)
        hr = max(2, int(r * 0.2))
        w  = max(1, r // 9)
        pygame.draw.circle(surf, col, (x, hy), hr)
        pygame.draw.line(surf, col, (x, hy + hr), (x, cy + int(r * 0.32)), w)
        pygame.draw.line(surf, col, (x, cy + int(r * 0.32)),
                         (x - int(r * 0.26), cy + int(r * 0.78)), w)
        pygame.draw.line(surf, col, (x, cy + int(r * 0.32)),
                         (x + int(r * 0.26), cy + int(r * 0.78)), w)
        # outer arm out, inner arm toward the other one
        pygame.draw.line(surf, col, (x, cy - int(r * 0.08)),
                         (x - int(r * 0.42) * (1 if dx < 0 else -1), cy - int(r * 0.3)), w)
    # the two inner arms meet in the middle
    pygame.draw.line(surf, (235, 215, 120),
                     (cx - int(r * 0.42), cy - int(r * 0.08)),
                     (cx + int(r * 0.42), cy - int(r * 0.08)), max(1, r // 9))


def _badge_burning_number(surf, cx, cy, r, text, heat=0):
    """A number standing in a fire. The longer the streak, the hotter it burns:
    orange, then white-hot, then blue-white with embers coming off it."""
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    outer, inner = [(236, 108, 24), (255, 206, 70)][0], (255, 206, 70)
    if heat >= 1:
        outer, inner = (255, 150, 30), (255, 246, 190)
    if heat >= 2:
        outer, inner = (120, 190, 255), (240, 250, 255)
    spread = 0.33 + 0.05 * heat
    for i in range(7):                                    # the body of the fire
        a = -_m.pi / 2 + (i - 3) * spread
        h = r * (0.75 + 0.3 * heat * 0.4 + 0.3 * abs(_m.sin(t * 4 + i)))
        pygame.draw.polygon(surf, outer, [
            (cx - int(r * 0.5) + i * int(r * 0.17), cy + int(r * 0.55)),
            (cx - int(r * 0.26) + i * int(r * 0.17), cy + int(r * 0.55)),
            (cx + int(_m.cos(a) * h * 0.55), cy + int(_m.sin(a) * h) - int(r * 0.1))])
    for i in range(5):                                    # the hot core
        a = -_m.pi / 2 + (i - 2) * 0.36
        h = r * (0.45 + 0.25 * abs(_m.sin(t * 5 + i * 1.7)))
        pygame.draw.polygon(surf, inner, [
            (cx - int(r * 0.34) + i * int(r * 0.17), cy + int(r * 0.52)),
            (cx - int(r * 0.16) + i * int(r * 0.17), cy + int(r * 0.52)),
            (cx + int(_m.cos(a) * h * 0.5), cy + int(_m.sin(a) * h))])
    for e in range(heat * 3):                             # embers off the top
        _f = (t * 0.9 + e * 0.27) % 1.0
        pygame.draw.circle(surf, inner,
                           (cx + int(_m.sin(t * 3 + e * 2) * r * 0.6),
                            cy - int(r * (0.7 + _f * 0.7))),
                           max(1, int(r * 0.09 * (1.0 - _f))))
    _f2 = pygame.font.SysFont("Arial", max(11, int(r * (1.5 if len(text) < 2 else 1.1))), bold=True)
    for off, col in (((1, 2), (40, 28, 20)), ((0, 0), (255, 252, 244))):
        _t2 = _f2.render(text, True, col)
        surf.blit(_t2, (cx - _t2.get_width() // 2 + off[0], cy - _t2.get_height() // 2 + off[1]))


def _badge_burning_six(surf, cx, cy, r):
    _badge_burning_number(surf, cx, cy, r, "6", heat=0)


def _badge_burning_twelve(surf, cx, cy, r):
    _badge_burning_number(surf, cx, cy, r, "12", heat=1)


def _badge_burning_twentyfour(surf, cx, cy, r):
    _badge_burning_number(surf, cx, cy, r, "24", heat=2)


def _badge_double_o(surf, cx, cy, r):
    """007, with the zeros drawn as elements."""
    _f = pygame.font.SysFont("Arial", max(12, int(r * 1.1)), bold=True)
    for dx, (fill, ring) in ((-0.62, ((60, 130, 220), (150, 205, 255))),
                             (-0.02, ((230, 90, 30), (255, 190, 90)))):
        ox = cx + int(r * dx)
        pygame.draw.circle(surf, fill, (ox, cy), int(r * 0.3))
        pygame.draw.circle(surf, ring, (ox, cy), int(r * 0.3), max(1, r // 12))
        pygame.draw.circle(surf, ring, (ox - int(r * 0.1), cy - int(r * 0.11)),
                           max(1, r // 9))
    _seven = _f.render("7", True, (236, 236, 244))
    surf.blit(_seven, (cx + int(r * 0.28), cy - _seven.get_height() // 2))
    pygame.draw.line(surf, (120, 200, 120), (cx - int(r * 0.9), cy + int(r * 0.52)),
                     (cx + int(r * 0.86), cy + int(r * 0.52)), max(1, r // 10))


def _badge_podium(surf, cx, cy, r):
    """A stickman standing on the top step of a podium."""
    gold, silver, bronze = (236, 190, 70), (190, 192, 200), (198, 132, 76)
    base = cy + int(r * 0.78)
    steps = ((-0.66, 0.40, silver), (0.66, 0.26, bronze), (0.0, 0.62, gold))
    for dx, h, col in steps:
        w = int(r * 0.42)
        x = cx + int(r * dx) - w
        top = base - int(r * h)
        pygame.draw.rect(surf, col, (x, top, w * 2, base - top))
        pygame.draw.rect(surf, (60, 52, 30), (x, top, w * 2, base - top), max(1, r // 14))
    # the winner on the top step
    hy = base - int(r * 0.62) - int(r * 0.34)
    w  = max(1, r // 10)
    pygame.draw.circle(surf, (250, 250, 255), (cx, hy), max(2, int(r * 0.17)))
    pygame.draw.line(surf, (250, 250, 255), (cx, hy + int(r * 0.17)),
                     (cx, hy + int(r * 0.5)), w)
    pygame.draw.line(surf, (250, 250, 255), (cx, hy + int(r * 0.24)),
                     (cx - int(r * 0.26), hy + int(r * 0.08)), w)
    pygame.draw.line(surf, (250, 250, 255), (cx, hy + int(r * 0.24)),
                     (cx + int(r * 0.26), hy + int(r * 0.08)), w)
    pygame.draw.line(surf, (250, 250, 255), (cx, hy + int(r * 0.5)),
                     (cx - int(r * 0.2), hy + int(r * 0.78)), w)
    pygame.draw.line(surf, (250, 250, 255), (cx, hy + int(r * 0.5)),
                     (cx + int(r * 0.2), hy + int(r * 0.78)), w)


def _badge_poison(surf, cx, cy, r):
    """A poison bottle: green glass, skull label, fumes."""
    glass, dark = (96, 196, 96), (40, 104, 48)
    pygame.draw.rect(surf, (120, 96, 60), (cx - int(r * 0.18), cy - int(r * 0.86),
                                           int(r * 0.36), int(r * 0.26)),
                     border_radius=max(1, r // 12))      # cork
    pygame.draw.rect(surf, glass, (cx - int(r * 0.2), cy - int(r * 0.66),
                                   int(r * 0.4), int(r * 0.3)))   # neck
    pygame.draw.ellipse(surf, glass, (cx - int(r * 0.62), cy - int(r * 0.42),
                                      int(r * 1.24), int(r * 1.2)))
    pygame.draw.ellipse(surf, dark, (cx - int(r * 0.62), cy - int(r * 0.42),
                                     int(r * 1.24), int(r * 1.2)), max(1, r // 12))
    # skull on the label
    sy = cy + int(r * 0.18)
    pygame.draw.circle(surf, (240, 244, 240), (cx, sy), int(r * 0.3))
    pygame.draw.rect(surf, (240, 244, 240), (cx - int(r * 0.16), sy + int(r * 0.2),
                                             int(r * 0.32), int(r * 0.16)))
    for dx in (-0.13, 0.13):
        pygame.draw.circle(surf, dark, (cx + int(r * dx), sy - int(r * 0.04)),
                           max(1, int(r * 0.09)))
    # fumes
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    for i in range(3):
        _f = (t * 0.7 + i * 0.33) % 1.0
        pygame.draw.circle(surf, (150, 220, 150),
                           (cx + int(_m.sin(t * 2 + i * 2) * r * 0.3),
                            cy - int(r * (0.9 + _f * 0.5))),
                           max(1, int(r * 0.13 * (1.0 - _f))))


def _badge_heal(surf, cx, cy, r):
    """The poison bottle's opposite: bright glass, a cross, sparkles rising."""
    glass, dark = (248, 150, 180), (168, 60, 100)
    pygame.draw.rect(surf, (230, 220, 210), (cx - int(r * 0.18), cy - int(r * 0.86),
                                             int(r * 0.36), int(r * 0.26)),
                     border_radius=max(1, r // 12))      # cork
    pygame.draw.rect(surf, glass, (cx - int(r * 0.2), cy - int(r * 0.66),
                                   int(r * 0.4), int(r * 0.3)))
    pygame.draw.ellipse(surf, glass, (cx - int(r * 0.62), cy - int(r * 0.42),
                                      int(r * 1.24), int(r * 1.2)))
    pygame.draw.ellipse(surf, dark, (cx - int(r * 0.62), cy - int(r * 0.42),
                                     int(r * 1.24), int(r * 1.2)), max(1, r // 12))
    # a healing cross where the skull would be
    cw = max(2, int(r * 0.16))
    pygame.draw.rect(surf, (255, 255, 255),
                     (cx - cw // 2, cy - int(r * 0.08), cw, int(r * 0.64)))
    pygame.draw.rect(surf, (255, 255, 255),
                     (cx - int(r * 0.26), cy + int(r * 0.16), int(r * 0.52), cw))
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    for i in range(3):                                    # sparkles, not fumes
        _f = (t * 0.7 + i * 0.33) % 1.0
        _sx = cx + int(_m.sin(t * 2 + i * 2) * r * 0.32)
        _sy = cy - int(r * (0.9 + _f * 0.5))
        _ss = max(1, int(r * 0.14 * (1.0 - _f)))
        pygame.draw.line(surf, (255, 240, 250), (_sx - _ss, _sy), (_sx + _ss, _sy), 1)
        pygame.draw.line(surf, (255, 240, 250), (_sx, _sy - _ss), (_sx, _sy + _ss), 1)


def _badge_cipher(surf, cx, cy, r):
    """A cipher disc: an outer ring of letters turning against an inner one."""
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    pygame.draw.circle(surf, (58, 54, 76), (cx, cy), r)
    pygame.draw.circle(surf, (138, 128, 190), (cx, cy), r, max(1, r // 12))
    pygame.draw.circle(surf, (38, 36, 54), (cx, cy), int(r * 0.6))
    pygame.draw.circle(surf, (138, 128, 190), (cx, cy), int(r * 0.6), max(1, r // 16))
    _f = pygame.font.SysFont("Arial", max(7, int(r * 0.34)), bold=True)
    for i, ch in enumerate("ABCDEFGH"):                  # outer ring, turning
        a = t * 0.5 + i * (_m.tau / 8)
        _g = _f.render(ch, True, (222, 216, 255))
        surf.blit(_g, (cx + int(_m.cos(a) * r * 0.79) - _g.get_width() // 2,
                       cy + int(_m.sin(a) * r * 0.79) - _g.get_height() // 2))
    for i, ch in enumerate("?#*%"):                      # inner ring, the other way
        a = -t * 0.8 + i * (_m.tau / 4)
        _g = _f.render(ch, True, (255, 206, 70))
        surf.blit(_g, (cx + int(_m.cos(a) * r * 0.36) - _g.get_width() // 2,
                       cy + int(_m.sin(a) * r * 0.36) - _g.get_height() // 2))
    pygame.draw.circle(surf, (255, 206, 70), (cx, cy), max(1, r // 10))


def _badge_eye_i(surf, cx, cy, r):
    """The secret character I: a lumpy dark body, holes, and the roaming eye."""
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    body, edge = (35, 30, 45), (18, 14, 26)
    lumps = ((0.0, -1.0), (0.58, -0.6), (0.92, 0.0), (0.66, 0.58),
             (0.0, 0.88), (-0.66, 0.58), (-0.92, 0.0), (-0.58, -0.6))
    pts = [(cx + int(dx * r * 0.86), cy + int(dy * r * 0.86)) for dx, dy in lumps]
    pygame.draw.polygon(surf, body, pts)
    pygame.draw.polygon(surf, edge, pts, max(1, r // 12))
    for hx, hy, hr in ((-0.38, -0.24, 0.26), (0.34, 0.1, 0.3), (0.0, 0.5, 0.2)):
        pygame.draw.circle(surf, (8, 6, 12),
                           (cx + int(hx * r), cy + int(hy * r)), max(2, int(r * hr)))
    a = t * 1.3                                           # the eye, orbiting
    ex = cx + int(_m.cos(a) * r * 0.62)
    ey = cy + int(_m.sin(a) * r * 0.42)
    pygame.draw.circle(surf, (238, 238, 246), (ex, ey), max(3, int(r * 0.26)))
    pygame.draw.circle(surf, (190, 40, 40), (ex, ey), max(2, int(r * 0.16)))
    pygame.draw.circle(surf, (10, 8, 14), (ex, ey), max(1, int(r * 0.08)))


def _badge_matrix(surf, cx, cy, r):
    """A stickman bent over backwards while a shot streaks past his nose."""
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    man = (220, 240, 225)
    w = max(1, r // 9)
    hipx, hipy = cx - int(r * 0.1), cy + int(r * 0.42)
    chestx, chesty = cx + int(r * 0.22), cy + int(r * 0.02)
    headx, heady = cx + int(r * 0.52), cy - int(r * 0.2)
    pygame.draw.line(surf, man, (hipx, hipy), (chestx, chesty), w)      # leaning torso
    pygame.draw.circle(surf, man, (headx, heady), max(2, int(r * 0.17)))
    pygame.draw.line(surf, man, (chestx, chesty),
                     (chestx - int(r * 0.42), chesty - int(r * 0.3)), w)
    pygame.draw.line(surf, man, (chestx, chesty),
                     (chestx - int(r * 0.1), chesty + int(r * 0.46)), w)
    pygame.draw.line(surf, man, (hipx, hipy), (hipx - int(r * 0.3), cy + int(r * 0.85)), w)
    pygame.draw.line(surf, man, (hipx, hipy), (hipx + int(r * 0.26), cy + int(r * 0.86)), w)
    # the shot going over him, with a trail
    bx = cx - int(r * 0.9) + int(((t * 1.6) % 1.0) * r * 1.8)
    by = cy - int(r * 0.52)
    for i in range(4):
        pygame.draw.circle(surf, (120, 255, 150),
                           (bx - i * int(r * 0.16), by), max(1, int(r * (0.13 - i * 0.03))))
    # falling green code
    for i in range(3):
        _cx2 = cx - int(r * 0.78) + i * int(r * 0.7)
        _cy2 = cy - r + int(((t * 0.8 + i * 0.3) % 1.0) * r * 2)
        pygame.draw.line(surf, (60, 200, 90), (_cx2, _cy2), (_cx2, _cy2 + int(r * 0.2)), 1)


def _badge_outnumbered(surf, cx, cy, r):
    """One stickman holding off three."""
    def _man(x, y, h, col, lean=0):
        w = max(1, r // 11)
        hr = max(2, int(h * 0.19))
        pygame.draw.circle(surf, col, (x + lean, y - h), hr)
        pygame.draw.line(surf, col, (x + lean, y - h + hr), (x, y - int(h * 0.38)), w)
        pygame.draw.line(surf, col, (x, y - int(h * 0.38)), (x - int(h * 0.2), y), w)
        pygame.draw.line(surf, col, (x, y - int(h * 0.38)), (x + int(h * 0.2), y), w)
        pygame.draw.line(surf, col, (x + lean // 2, y - int(h * 0.66)),
                         (x - int(h * 0.3), y - int(h * 0.74)), w)
        pygame.draw.line(surf, col, (x + lean // 2, y - int(h * 0.66)),
                         (x + int(h * 0.3), y - int(h * 0.74)), w)
    base = cy + int(r * 0.74)
    for i, dx in enumerate((0.26, 0.62, 0.95)):           # the three closing in
        _man(cx + int(r * dx), base, int(r * (1.0 - i * 0.06)), (226, 86, 86), lean=-2)
    _man(cx - int(r * 0.62), base, int(r * 1.05), (120, 190, 250), lean=2)
    pygame.draw.line(surf, (70, 70, 84), (cx - r, base + 2), (cx + r, base + 2),
                     max(1, r // 14))


def _badge_blast_jump(surf, cx, cy, r):
    """A stickman in mid-air over a blast that just missed him."""
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    base = cy + int(r * 0.78)
    puff = 0.85 + 0.15 * _m.sin(t * 6)
    for rad, col in ((0.62, (255, 236, 150)), (0.46, (255, 170, 50)), (0.3, (255, 96, 30))):
        pygame.draw.circle(surf, col, (cx + int(r * 0.3), base - int(r * 0.1)),
                           max(2, int(r * rad * puff)))
    for i in range(7):                                    # debris flying out
        a = -_m.pi + i * (_m.pi / 6)
        d = r * (0.7 + 0.2 * _m.sin(t * 5 + i))
        pygame.draw.circle(surf, (250, 210, 120),
                           (cx + int(r * 0.3 + _m.cos(a) * d),
                            base - int(r * 0.1) + int(_m.sin(a) * d * 0.5)),
                           max(1, r // 14))
    man, w = (235, 245, 255), max(1, r // 10)
    hx, hy = cx - int(r * 0.42), cy - int(r * 0.52)       # tucked up, legs high
    pygame.draw.circle(surf, man, (hx, hy), max(2, int(r * 0.17)))
    pygame.draw.line(surf, man, (hx, hy + int(r * 0.17)), (hx + int(r * 0.2), cy), w)
    pygame.draw.line(surf, man, (hx + int(r * 0.2), cy), (hx + int(r * 0.5), cy - int(r * 0.14)), w)
    pygame.draw.line(surf, man, (hx + int(r * 0.2), cy), (hx + int(r * 0.44), cy + int(r * 0.2)), w)
    pygame.draw.line(surf, man, (hx, hy + int(r * 0.3)), (hx - int(r * 0.34), hy + int(r * 0.1)), w)
    pygame.draw.line(surf, man, (hx, hy + int(r * 0.3)), (hx + int(r * 0.16), hy - int(r * 0.2)), w)


def _badge_velcroraptor(surf, cx, cy, r):
    """A raptor stitched out of velcro: loops on the body, hooks down the back."""
    import math as _m
    hide, dark = (196, 162, 96), (130, 100, 54)
    base = cy + int(r * 0.66)
    # tail, body, neck, head
    pygame.draw.polygon(surf, hide, [
        (cx - int(r * 0.98), base - int(r * 0.06)),
        (cx - int(r * 0.3), base - int(r * 0.46)),
        (cx + int(r * 0.2), base - int(r * 0.5)),
        (cx + int(r * 0.26), base - int(r * 0.08))])
    pygame.draw.ellipse(surf, hide, (cx - int(r * 0.42), base - int(r * 0.72),
                                     int(r * 0.86), int(r * 0.66)))
    pygame.draw.polygon(surf, hide, [
        (cx + int(r * 0.1), base - int(r * 0.66)),
        (cx + int(r * 0.42), base - int(r * 1.04)),
        (cx + int(r * 0.6), base - int(r * 0.86)),
        (cx + int(r * 0.3), base - int(r * 0.52))])
    pygame.draw.ellipse(surf, hide, (cx + int(r * 0.36), base - int(r * 1.12),
                                     int(r * 0.62), int(r * 0.34)))
    pygame.draw.circle(surf, (40, 34, 28), (cx + int(r * 0.58), base - int(r * 1.0)),
                       max(1, r // 12))
    for i in range(4):                                    # teeth
        pygame.draw.polygon(surf, (250, 250, 245), [
            (cx + int(r * (0.48 + i * 0.1)), base - int(r * 0.86)),
            (cx + int(r * (0.53 + i * 0.1)), base - int(r * 0.86)),
            (cx + int(r * (0.5 + i * 0.1)), base - int(r * 0.76))])
    # legs with the big claw
    for dx in (-0.1, 0.16):
        pygame.draw.line(surf, dark, (cx + int(r * dx), base - int(r * 0.2)),
                         (cx + int(r * dx) - int(r * 0.08), base), max(2, r // 9))
        pygame.draw.line(surf, dark, (cx + int(r * dx) - int(r * 0.08), base),
                         (cx + int(r * dx) + int(r * 0.2), base), max(2, r // 11))
    # velcro: loops across the body, hooks along the spine
    for i in range(6):
        lx = cx - int(r * 0.36) + i * int(r * 0.14)
        pygame.draw.circle(surf, dark, (lx, base - int(r * 0.42)), max(1, r // 13), 1)
    for i in range(5):
        hx = cx - int(r * 0.3) + i * int(r * 0.13)
        hy = base - int(r * 0.74) - int(_m.sin(i) * r * 0.04)
        pygame.draw.line(surf, dark, (hx, hy), (hx + int(r * 0.06), hy - int(r * 0.12)), 1)
        pygame.draw.line(surf, dark, (hx + int(r * 0.06), hy - int(r * 0.12)),
                         (hx + int(r * 0.13), hy - int(r * 0.06)), 1)


def _badge_eye(surf, cx, cy, r):
    """An eye, looking around and blinking — you have seen this before."""
    import math as _m
    t = pygame.time.get_ticks() / 1000.0
    blink = (t % 3.4) > 3.25                              # a slow blink
    w = int(r * 0.98)
    h = int(r * (0.1 if blink else 0.58))
    pygame.draw.ellipse(surf, (244, 246, 250), (cx - w, cy - h, w * 2, h * 2))
    pygame.draw.ellipse(surf, (40, 44, 60), (cx - w, cy - h, w * 2, h * 2), max(1, r // 12))
    if not blink:
        px = cx + int(_m.sin(t * 0.9) * r * 0.34)         # the gaze wanders
        pygame.draw.circle(surf, (86, 150, 210), (px, cy), int(r * 0.34))
        pygame.draw.circle(surf, (24, 28, 40), (px, cy), int(r * 0.17))
        pygame.draw.circle(surf, (250, 252, 255), (px - int(r * 0.12), cy - int(r * 0.12)),
                           max(1, int(r * 0.08)))
        # a second, ghosted outline — the same eye, a moment ago
        _gs = pygame.Surface((r * 3, r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(_gs, (150, 200, 255, 70),
                            (0, 0, int(w * 1.9), int(h * 1.9)), max(1, r // 14))
        surf.blit(_gs, (cx - w + int(r * 0.18), cy - h - int(r * 0.12)))


def _badge_nutshell(surf, cx, cy, r):
    """A walnut cracked open with a tiny fighter standing inside it."""
    shell, dark = (176, 128, 72), (116, 80, 42)
    pygame.draw.ellipse(surf, shell, (cx - r, cy - int(r * 0.2), r * 2, int(r * 1.1)))
    pygame.draw.ellipse(surf, dark, (cx - r, cy - int(r * 0.2), r * 2, int(r * 1.1)),
                        max(1, r // 12))
    for i in range(4):                                    # shell grain
        pygame.draw.arc(surf, dark, (cx - r + i * int(r * 0.2), cy - int(r * 0.12),
                                     int(r * 1.2), int(r * 0.9)),
                        math.radians(200), math.radians(340), 1)
    pygame.draw.ellipse(surf, (206, 158, 96), (cx - r, cy - int(r * 0.72), r * 2, int(r * 0.6)))
    pygame.draw.ellipse(surf, dark, (cx - r, cy - int(r * 0.72), r * 2, int(r * 0.6)),
                        max(1, r // 12))                  # the lifted lid
    w = max(1, r // 12)
    hx, hy = cx, cy - int(r * 0.02)
    pygame.draw.circle(surf, (245, 245, 250), (hx, hy - int(r * 0.2)), max(2, int(r * 0.13)))
    pygame.draw.line(surf, (245, 245, 250), (hx, hy - int(r * 0.08)), (hx, hy + int(r * 0.3)), w)
    pygame.draw.line(surf, (245, 245, 250), (hx, hy + int(r * 0.04)),
                     (hx - int(r * 0.26), hy - int(r * 0.08)), w)
    pygame.draw.line(surf, (245, 245, 250), (hx, hy + int(r * 0.04)),
                     (hx + int(r * 0.26), hy - int(r * 0.08)), w)


def _badge_speed_demon(surf, cx, cy, r):
    """A horned head tearing along inside its own slipstream."""
    t = pygame.time.get_ticks() / 1000.0
    for i in range(4):                                    # speed lines
        _y = cy - int(r * 0.5) + i * int(r * 0.34)
        _len = int(r * (0.7 + 0.25 * math.sin(t * 7 + i)))
        pygame.draw.line(surf, (150, 210, 255),
                         (cx - r, _y), (cx - r + _len, _y), max(1, r // 10))
    head = (206, 70, 70)
    pygame.draw.circle(surf, head, (cx + int(r * 0.22), cy), int(r * 0.52))
    for sx in (-1, 1):                                    # horns
        pygame.draw.polygon(surf, (240, 160, 120), [
            (cx + int(r * 0.22) + sx * int(r * 0.3), cy - int(r * 0.36)),
            (cx + int(r * 0.22) + sx * int(r * 0.52), cy - int(r * 0.86)),
            (cx + int(r * 0.22) + sx * int(r * 0.46), cy - int(r * 0.3))])
    for sx in (-1, 1):                                    # eyes
        pygame.draw.circle(surf, (255, 232, 120),
                           (cx + int(r * 0.22) + sx * int(r * 0.2), cy - int(r * 0.06)),
                           max(1, int(r * 0.11)))
    pygame.draw.arc(surf, (40, 20, 20),
                    (cx - int(r * 0.06), cy + int(r * 0.1), int(r * 0.56), int(r * 0.4)),
                    math.radians(200), math.radians(340), max(1, r // 12))


def _badge_fire_mole(surf, cx, cy, r):
    """Fire in the hole: a mole coming up out of a burning burrow."""
    t = pygame.time.get_ticks() / 1000.0
    ground = cy + int(r * 0.44)
    pygame.draw.ellipse(surf, (104, 74, 48), (cx - r, ground - int(r * 0.2),
                                              r * 2, int(r * 0.6)))        # mound
    pygame.draw.ellipse(surf, (34, 24, 18), (cx - int(r * 0.52), ground - int(r * 0.18),
                                             int(r * 1.04), int(r * 0.4)))  # hole
    for i in range(6):                                    # flames out of the hole
        a = -math.pi / 2 + (i - 2.5) * 0.3
        h = r * (0.5 + 0.25 * abs(math.sin(t * 6 + i)))
        pygame.draw.polygon(surf, (255, 150, 40) if i % 2 else (236, 94, 24), [
            (cx - int(r * 0.4) + i * int(r * 0.16), ground - int(r * 0.04)),
            (cx - int(r * 0.24) + i * int(r * 0.16), ground - int(r * 0.04)),
            (cx + int(math.cos(a) * h * 0.5), ground - int(r * 0.1) - int(h))])
    mole = (86, 66, 86)
    pygame.draw.ellipse(surf, mole, (cx - int(r * 0.34), ground - int(r * 0.62),
                                     int(r * 0.68), int(r * 0.56)))
    pygame.draw.circle(surf, (226, 150, 160), (cx, ground - int(r * 0.4)), max(1, int(r * 0.1)))
    for sx in (-1, 1):
        pygame.draw.circle(surf, (24, 20, 24),
                           (cx + sx * int(r * 0.14), ground - int(r * 0.5)), max(1, int(r * 0.05)))
        pygame.draw.ellipse(surf, (200, 180, 200),                       # digging claws
                            (cx + sx * int(r * 0.34) - int(r * 0.1), ground - int(r * 0.3),
                             int(r * 0.2), int(r * 0.16)))


def _badge_map(surf, cx, cy, r):
    """An old map with a route across it and a figure walking the route."""
    paper, edge = (226, 206, 160), (164, 140, 96)
    pygame.draw.polygon(surf, paper, [
        (cx - r, cy - int(r * 0.66)), (cx + r, cy - int(r * 0.78)),
        (cx + r, cy + int(r * 0.74)), (cx - r, cy + int(r * 0.62))])
    pygame.draw.polygon(surf, edge, [
        (cx - r, cy - int(r * 0.66)), (cx + r, cy - int(r * 0.78)),
        (cx + r, cy + int(r * 0.74)), (cx - r, cy + int(r * 0.62))], max(1, r // 14))
    for fx in (-0.34, 0.3):                               # fold creases
        pygame.draw.line(surf, edge, (cx + int(r * fx), cy - int(r * 0.72)),
                         (cx + int(r * fx), cy + int(r * 0.68)), 1)
    # a dashed route wandering across
    pts = [(-0.78, 0.4), (-0.4, 0.1), (-0.05, 0.28), (0.3, -0.12), (0.72, -0.34)]
    for i in range(len(pts) - 1):
        x1 = cx + int(r * pts[i][0]);     y1 = cy + int(r * pts[i][1])
        x2 = cx + int(r * pts[i + 1][0]); y2 = cy + int(r * pts[i + 1][1])
        pygame.draw.line(surf, (190, 70, 60), (x1, y1), (x2, y2), max(1, r // 16))
    pygame.draw.line(surf, (190, 70, 60),                 # the X at the end
                     (cx + int(r * 0.64), cy - int(r * 0.44)),
                     (cx + int(r * 0.8), cy - int(r * 0.24)), max(1, r // 14))
    pygame.draw.line(surf, (190, 70, 60),
                     (cx + int(r * 0.8), cy - int(r * 0.44)),
                     (cx + int(r * 0.64), cy - int(r * 0.24)), max(1, r // 14))
    # the walker, standing on the map
    w = max(1, r // 12)
    hx, hy = cx - int(r * 0.1), cy - int(r * 0.1)
    pygame.draw.circle(surf, (60, 70, 110), (hx, hy - int(r * 0.22)), max(2, int(r * 0.13)))
    pygame.draw.line(surf, (60, 70, 110), (hx, hy - int(r * 0.1)), (hx, hy + int(r * 0.16)), w)
    pygame.draw.line(surf, (60, 70, 110), (hx, hy + int(r * 0.16)),
                     (hx - int(r * 0.16), hy + int(r * 0.42)), w)
    pygame.draw.line(surf, (60, 70, 110), (hx, hy + int(r * 0.16)),
                     (hx + int(r * 0.16), hy + int(r * 0.42)), w)
    pygame.draw.line(surf, (60, 70, 110), (hx, hy + int(r * 0.02)),
                     (hx + int(r * 0.22), hy - int(r * 0.14)), w)


def _badge_unscratched(surf, cx, cy, r):
    """A shield without a mark on it, catching the light."""
    t = pygame.time.get_ticks() / 1000.0
    body = [(cx, cy - int(r * 0.92)), (cx + int(r * 0.76), cy - int(r * 0.54)),
            (cx + int(r * 0.66), cy + int(r * 0.42)), (cx, cy + int(r * 0.94)),
            (cx - int(r * 0.66), cy + int(r * 0.42)), (cx - int(r * 0.76), cy - int(r * 0.54))]
    pygame.draw.polygon(surf, (120, 186, 236), body)
    pygame.draw.polygon(surf, (236, 248, 255), body, max(2, r // 10))
    pygame.draw.polygon(surf, (196, 228, 250), [
        (cx, cy - int(r * 0.7)), (cx + int(r * 0.46), cy - int(r * 0.4)),
        (cx, cy + int(r * 0.1))])
    gleam = (t * 1.4) % 2.4                               # a shine sweeping over
    if gleam < 0.8:
        gx = cx - int(r * 0.7) + int(gleam / 0.8 * r * 1.4)
        pygame.draw.line(surf, (255, 255, 255), (gx, cy - int(r * 0.7)),
                         (gx - int(r * 0.2), cy + int(r * 0.6)), max(1, r // 9))


def _badge_last_leg(surf, cx, cy, r):
    """One sliver of health left, and still standing."""
    t = pygame.time.get_ticks() / 1000.0
    bw, bh = int(r * 1.6), int(r * 0.3)
    bx, by = cx - bw // 2, cy + int(r * 0.42)
    pygame.draw.rect(surf, (54, 48, 54), (bx, by, bw, bh), border_radius=max(1, r // 10))
    _pulse = 0.6 + 0.4 * abs(math.sin(t * 5))
    pygame.draw.rect(surf, (int(220 * _pulse) + 30, 40, 44),
                     (bx + 2, by + 2, max(3, int(bw * 0.09)), bh - 4),
                     border_radius=max(1, r // 12))
    pygame.draw.rect(surf, (210, 210, 220), (bx, by, bw, bh), max(1, r // 14),
                     border_radius=max(1, r // 10))
    man, w = (236, 236, 244), max(1, r // 10)             # down on one knee
    hx, hy = cx - int(r * 0.16), cy - int(r * 0.5)
    pygame.draw.circle(surf, man, (hx, hy), max(2, int(r * 0.17)))
    pygame.draw.line(surf, man, (hx, hy + int(r * 0.16)), (hx + int(r * 0.1), cy + int(r * 0.1)), w)
    pygame.draw.line(surf, man, (hx + int(r * 0.1), cy + int(r * 0.1)),
                     (hx - int(r * 0.3), cy + int(r * 0.3)), w)
    pygame.draw.line(surf, man, (hx + int(r * 0.1), cy + int(r * 0.1)),
                     (hx + int(r * 0.44), cy + int(r * 0.3)), w)
    pygame.draw.line(surf, man, (hx + int(r * 0.04), cy - int(r * 0.2)),
                     (hx - int(r * 0.36), cy - int(r * 0.34)), w)


def _badge_mega_mind(surf, cx, cy, r):
    """The hardest opponent in the game, beaten: a crowned machine head."""
    t = pygame.time.get_ticks() / 1000.0
    pygame.draw.rect(surf, (92, 100, 120), (cx - int(r * 0.6), cy - int(r * 0.34),
                                            int(r * 1.2), int(r * 1.0)),
                     border_radius=max(2, r // 6))
    pygame.draw.rect(surf, (40, 46, 60), (cx - int(r * 0.6), cy - int(r * 0.34),
                                          int(r * 1.2), int(r * 1.0)),
                     max(1, r // 12), border_radius=max(2, r // 6))
    for sx in (-1, 1):
        pygame.draw.rect(surf, (255, 90 + int(60 * abs(math.sin(t * 3))), 60),
                         (cx + sx * int(r * 0.34) - int(r * 0.14), cy - int(r * 0.08),
                          int(r * 0.28), int(r * 0.16)))
    for i in range(4):
        pygame.draw.line(surf, (30, 34, 44),
                         (cx - int(r * 0.3) + i * int(r * 0.2), cy + int(r * 0.34)),
                         (cx - int(r * 0.3) + i * int(r * 0.2), cy + int(r * 0.56)),
                         max(1, r // 14))
    pygame.draw.polygon(surf, (255, 206, 70), [                   # crown on top
        (cx - int(r * 0.52), cy - int(r * 0.36)), (cx - int(r * 0.52), cy - int(r * 0.76)),
        (cx - int(r * 0.2), cy - int(r * 0.52)), (cx, cy - int(r * 0.92)),
        (cx + int(r * 0.2), cy - int(r * 0.52)), (cx + int(r * 0.52), cy - int(r * 0.76)),
        (cx + int(r * 0.52), cy - int(r * 0.36))])


def _badge_tally(surf, cx, cy, r):
    """A hundred kills, kept in five-bar gates on the wall."""
    chalk = (236, 238, 242)
    w = max(1, r // 12)
    for row in range(2):
        for grp in range(3):
            gx = cx - int(r * 0.78) + grp * int(r * 0.58)
            gy = cy - int(r * 0.34) + row * int(r * 0.62)
            for i in range(4):
                pygame.draw.line(surf, chalk, (gx + i * int(r * 0.1), gy),
                                 (gx + i * int(r * 0.1), gy + int(r * 0.4)), w)
            pygame.draw.line(surf, (236, 120, 110), (gx - int(r * 0.06), gy + int(r * 0.4)),
                             (gx + int(r * 0.38), gy), w)
    pygame.draw.circle(surf, (236, 238, 242), (cx + int(r * 0.62), cy + int(r * 0.66)),
                       max(2, int(r * 0.2)))
    for sx in (-1, 1):
        pygame.draw.circle(surf, (30, 30, 38),
                           (cx + int(r * 0.62) + sx * int(r * 0.08), cy + int(r * 0.62)),
                           max(1, int(r * 0.06)))


def _badge_online_fist(surf, cx, cy, r):
    """A fist over a globe: a win against somebody real."""
    pygame.draw.circle(surf, (56, 128, 186), (cx, cy + int(r * 0.12)), int(r * 0.76))
    pygame.draw.circle(surf, (190, 226, 246), (cx, cy + int(r * 0.12)), int(r * 0.76),
                       max(1, r // 14))
    for i in (-0.4, 0.0, 0.4):                            # latitudes
        _h = int(r * 0.76 * math.cos(i * 1.6))
        pygame.draw.ellipse(surf, (130, 190, 226),
                            (cx - _h, cy + int(r * 0.12) + int(i * r * 0.7) - int(r * 0.08),
                             _h * 2, int(r * 0.16)), 1)
    pygame.draw.ellipse(surf, (130, 190, 226),
                        (cx - int(r * 0.3), cy - int(r * 0.64), int(r * 0.6), int(r * 1.52)), 1)
    pygame.draw.circle(surf, (240, 212, 180), (cx + int(r * 0.34), cy - int(r * 0.42)),
                       int(r * 0.32))
    pygame.draw.circle(surf, (170, 130, 96), (cx + int(r * 0.34), cy - int(r * 0.42)),
                       int(r * 0.32), max(1, r // 16))
    for i in range(3):
        pygame.draw.line(surf, (170, 130, 96),
                         (cx + int(r * 0.16), cy - int(r * 0.54) + i * int(r * 0.12)),
                         (cx + int(r * 0.5), cy - int(r * 0.54) + i * int(r * 0.12)), 1)


def _badge_elements_ring(surf, cx, cy, r):
    """All six elements held at once, turning in a ring."""
    t = pygame.time.get_ticks() / 1000.0
    cols = ((60, 130, 220), (120, 100, 80), (70, 160, 70),
            (210, 230, 240), (230, 210, 40), (230, 90, 30))
    for i, col in enumerate(cols):
        a = t * 0.6 + i * (math.tau / 6)
        ox = cx + int(math.cos(a) * r * 0.62)
        oy = cy + int(math.sin(a) * r * 0.62)
        pygame.draw.circle(surf, col, (ox, oy), max(2, int(r * 0.22)))
        pygame.draw.circle(surf, (250, 250, 255), (ox - int(r * 0.07), oy - int(r * 0.08)),
                           max(1, int(r * 0.07)))
    pygame.draw.circle(surf, (245, 240, 255), (cx, cy), max(2, int(r * 0.16)))


def _badge_roster(surf, cx, cy, r):
    """A deck of fighters, fanned out."""
    for i, dx in enumerate((-0.5, -0.17, 0.16)):
        x = cx + int(r * dx)
        col = ((86, 150, 240), (226, 96, 96), (150, 220, 140))[i]
        pygame.draw.rect(surf, (36, 36, 48), (x - int(r * 0.26), cy - int(r * 0.6),
                                              int(r * 0.52), int(r * 1.2)),
                         border_radius=max(1, r // 10))
        pygame.draw.rect(surf, col, (x - int(r * 0.26), cy - int(r * 0.6),
                                     int(r * 0.52), int(r * 1.2)),
                         max(1, r // 16), border_radius=max(1, r // 10))
        pygame.draw.circle(surf, col, (x, cy - int(r * 0.26)), max(2, int(r * 0.13)))
        pygame.draw.line(surf, col, (x, cy - int(r * 0.14)), (x, cy + int(r * 0.2)),
                         max(1, r // 16))
        pygame.draw.line(surf, col, (x, cy + int(r * 0.2)),
                         (x - int(r * 0.14), cy + int(r * 0.46)), max(1, r // 16))
        pygame.draw.line(surf, col, (x, cy + int(r * 0.2)),
                         (x + int(r * 0.14), cy + int(r * 0.46)), max(1, r // 16))
    _f = pygame.font.SysFont("Arial", max(9, int(r * 0.44)), bold=True)
    _t2 = _f.render("100", True, (255, 206, 70))
    surf.blit(_t2, (cx + int(r * 0.3), cy + int(r * 0.2)))


def _badge_modes(surf, cx, cy, r):
    """A wheel of every way to play."""
    t = pygame.time.get_ticks() / 1000.0
    cols = ((90, 150, 240), (240, 150, 60), (110, 210, 120),
            (80, 220, 220), (255, 206, 70), (200, 140, 255))
    for i, col in enumerate(cols):
        a0 = t * 0.4 + i * (math.tau / 6)
        pygame.draw.arc(surf, col, (cx - r + 2, cy - r + 2, r * 2 - 4, r * 2 - 4),
                        a0, a0 + 0.78, max(2, r // 6))
    pygame.draw.circle(surf, (238, 238, 246), (cx, cy), max(2, int(r * 0.22)))
    pygame.draw.circle(surf, (40, 40, 52), (cx, cy), max(1, int(r * 0.1)))


def _badge_lottery(surf, cx, cy, r):
    """A scratch card with every number come up."""
    t = pygame.time.get_ticks() / 1000.0
    paper, ink = (248, 242, 224), (60, 56, 70)
    pygame.draw.rect(surf, paper, (cx - r, cy - int(r * 0.66), r * 2, int(r * 1.32)),
                     border_radius=max(1, r // 10))
    pygame.draw.rect(surf, ink, (cx - r, cy - int(r * 0.66), r * 2, int(r * 1.32)),
                     max(1, r // 14), border_radius=max(1, r // 10))
    for i in range(7):                                    # the perforated edge
        pygame.draw.circle(surf, (24, 24, 32),
                           (cx - r, cy - int(r * 0.6) + i * int(r * 0.2)), max(1, r // 16))
    _f = pygame.font.SysFont("Arial", max(7, int(r * 0.3)), bold=True)
    _tt = _f.render("LUCKY", True, (196, 60, 70))
    surf.blit(_tt, (cx - _tt.get_width() // 2, cy - int(r * 0.58)))
    cols = ((60, 130, 220), (120, 100, 80), (70, 160, 70),
            (210, 230, 240), (230, 210, 40), (230, 90, 30))
    for i, col in enumerate(cols):                        # six scratched panels
        px = cx - int(r * 0.74) + (i % 3) * int(r * 0.74)
        py = cy - int(r * 0.1) + (i // 3) * int(r * 0.44)
        pygame.draw.rect(surf, col, (px - int(r * 0.26), py - int(r * 0.16),
                                     int(r * 0.52), int(r * 0.34)),
                         border_radius=max(1, r // 16))
        pygame.draw.rect(surf, ink, (px - int(r * 0.26), py - int(r * 0.16),
                                     int(r * 0.52), int(r * 0.34)),
                         1, border_radius=max(1, r // 16))
    for i in range(4):                                    # winning sparkle
        a = t * 2 + i * (math.tau / 4)
        _sx = cx + int(math.cos(a) * r * 0.9)
        _sy = cy + int(math.sin(a) * r * 0.78)
        pygame.draw.line(surf, (255, 230, 120), (_sx - 2, _sy), (_sx + 2, _sy), 1)
        pygame.draw.line(surf, (255, 230, 120), (_sx, _sy - 2), (_sx, _sy + 2), 1)


def _badge_serpentoduko(surf, cx, cy, r):
    """A snake curled over a sudoku grid, filling it in."""
    grid, line = (242, 242, 236), (70, 70, 86)
    g = int(r * 1.1)
    gx, gy = cx - g // 2 + int(r * 0.1), cy - int(r * 0.1)
    pygame.draw.rect(surf, grid, (gx, gy, g, g))
    for i in range(1, 3):
        pygame.draw.line(surf, line, (gx + i * g // 3, gy), (gx + i * g // 3, gy + g), 1)
        pygame.draw.line(surf, line, (gx, gy + i * g // 3), (gx + g, gy + i * g // 3), 1)
    pygame.draw.rect(surf, line, (gx, gy, g, g), max(1, r // 16))
    _f = pygame.font.SysFont("Arial", max(6, int(r * 0.26)), bold=True)
    for (ci, cj, ch) in ((0, 0, "5"), (1, 1, "3"), (2, 2, "7"), (2, 0, "1"), (0, 2, "9")):
        _t2 = _f.render(ch, True, (60, 90, 150))
        surf.blit(_t2, (gx + ci * g // 3 + g // 6 - _t2.get_width() // 2,
                        gy + cj * g // 3 + g // 6 - _t2.get_height() // 2))
    body, belly = (70, 170, 80), (160, 220, 140)
    pts = [(cx - int(r * 0.92), cy + int(r * 0.58)), (cx - int(r * 0.48), cy + int(r * 0.96)),
           (cx + int(r * 0.24), cy + int(r * 0.88)), (cx + int(r * 0.78), cy + int(r * 0.98))]
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, body, pts[i], pts[i + 1], max(3, r // 5))
    pygame.draw.circle(surf, body, (cx - int(r * 0.86), cy - int(r * 0.52)), max(3, int(r * 0.26)))
    pygame.draw.circle(surf, belly, (cx - int(r * 0.92), cy - int(r * 0.58)), max(1, int(r * 0.1)))
    pygame.draw.line(surf, body, (cx - int(r * 0.86), cy - int(r * 0.3)),
                     (cx - int(r * 0.92), cy + int(r * 0.44)), max(2, r // 7))
    pygame.draw.circle(surf, (20, 20, 24), (cx - int(r * 0.78), cy - int(r * 0.58)),
                       max(1, int(r * 0.06)))
    pygame.draw.line(surf, (210, 60, 60), (cx - int(r * 0.62), cy - int(r * 0.46)),
                     (cx - int(r * 0.4), cy - int(r * 0.4)), 1)   # tongue, pointing at a square


BADGES = {
    "crown":    _badge_crown,
    "lhat":     _badge_lhat,
    "saintnix": _badge_saintnix,
    "friends":  _badge_friends,
    "six_fire":    _badge_burning_six,
    "twelve_fire": _badge_burning_twelve,
    "tfour_fire":  _badge_burning_twentyfour,
    "double_o": _badge_double_o,
    "podium":   _badge_podium,
    "poison":   _badge_poison,
    "heal":     _badge_heal,
    "cipher":   _badge_cipher,
    "eye_i":    _badge_eye_i,
    "matrix":   _badge_matrix,
    "outnumbered": _badge_outnumbered,
    "blast_jump":  _badge_blast_jump,
    "velcroraptor": _badge_velcroraptor,
    "eye":          _badge_eye,
    "nutshell":     _badge_nutshell,
    "speed_demon":  _badge_speed_demon,
    "fire_mole":    _badge_fire_mole,
    "map":          _badge_map,
    "unscratched":  _badge_unscratched,
    "last_leg":     _badge_last_leg,
    "mega_mind":    _badge_mega_mind,
    "tally":        _badge_tally,
    "online_fist":  _badge_online_fist,
    "elements":     _badge_elements_ring,
    "roster":       _badge_roster,
    "modes":        _badge_modes,
    "lottery":      _badge_lottery,
    "serpentoduko": _badge_serpentoduko,
}


def draw_badge(surface, kind, cx, cy, r, locked=False):
    """Draw one badge. Locked ones show as a grey silhouette with a question mark."""
    if locked:
        pygame.draw.circle(surface, (46, 46, 56), (cx, cy), r)
        pygame.draw.circle(surface, (72, 72, 86), (cx, cy), r, max(1, r // 12))
        _f = pygame.font.SysFont("Arial", max(10, int(r * 1.1)), bold=True)
        _q = _f.render("?", True, (96, 96, 112))
        surface.blit(_q, (cx - _q.get_width() // 2, cy - _q.get_height() // 2))
        return
    fn = BADGES.get(kind)
    if fn:
        fn(surface, cx, cy, r)


# ---------------------------------------------------------------------------
# The achievements themselves
# ---------------------------------------------------------------------------

TOP_SECONDS = 3600          # an hour at number one


def note_leaderboard(stats, entries, my_code):
    """Call whenever a leaderboard arrives.

    Records when the player was first seen holding first place, and forgets it
    the moment somebody else is on top. The achievement then only has to ask
    how long ago that was — which means the clock keeps running while the game
    is shut, exactly as it would on the real leaderboard.
    """
    if not entries or not my_code:
        return
    on_top = (entries[0].get("code") == my_code)
    if on_top:
        stats.setdefault("top_since", time.time())
    else:
        stats.pop("top_since", None)


def _all_stages_played(stats):
    """Every stage the player can actually pick — mode-only arenas excepted."""
    try:
        from fight_data import STAGES
    except Exception:
        return False
    want = {st["name"] for st in STAGES if not st.get("special_mode_only")}
    return want and want <= set(stats.get("stages_played", []))


ALL_MODES = ("1p", "2p", "survival", "online", "shop", "fuser")


def _all_fused(stats):
    """Every fuser recipe landed, with no failure anywhere in the run."""
    try:
        from fight_data import FUSER_RECIPES
    except Exception:
        return False
    want = {r["name"] for r in FUSER_RECIPES.values()}
    return bool(want) and want <= set(stats.get("fuse_run", []))


def _all_elements_reward():
    try:
        from fight_data import FUSER_ELEMENTS
        return [(name, 1) for name, _c, _col in FUSER_ELEMENTS]
    except Exception:
        return []


def _has_all_elements(stats):
    """Every element in the bag at once, not one at a time."""
    try:
        from fight_data import FUSER_ELEMENTS
    except Exception:
        return False
    bag = stats.get("fuser_elements") or {}
    return all(bag.get(name, 0) > 0 for name, _c, _col in FUSER_ELEMENTS)


def _daily_streak(stats):
    """Consecutive days played, counted off the same list the unlocks use."""
    try:
        from fight_game import _count_daily_streak
        return _count_daily_streak(stats.get("daily_play_dates", []))
    except Exception:
        return 0


ACHIEVEMENTS = [
    {
        "id": "winner",
        "name": "Winner!",
        "desc": "Win your first match",
        "reward": 5,
        "badge": "crown",
        "check": lambda s, u, d: s.get("wins_total", 0) >= 1,
    },
    {
        "id": "lose_your_hat",
        "name": "Lose your hat",
        "desc": "Lose your first match",
        "reward": 0,
        "badge": "lhat",
        "check": lambda s, u, d: s.get("losses", 0) >= 1,
    },
    {
        "id": "friends_or_foes",
        "name": "Friends or foes?",
        "desc": "Friend someone",
        "reward": 10,
        "badge": "friends",
        "check": lambda s, u, d: bool((d or {}).get("friends")),
    },
    {
        "id": "six_day_streak",
        "name": "6 day streak",
        "desc": "Play 6 days in a row",
        "reward": 6,
        "badge": "six_fire",
        "check": lambda s, u, d: _daily_streak(s) >= 6,
    },
    {
        "id": "twelve_day_streak",
        "name": "12 day streak",
        "desc": "Play 12 days in a row",
        "reward": 12,
        "badge": "twelve_fire",
        "check": lambda s, u, d: _daily_streak(s) >= 12,
    },
    {
        "id": "twentyfour_day_streak",
        "name": "24 day streak",
        "desc": "Play 24 days in a row",
        "reward": 24,
        "badge": "tfour_fire",
        "check": lambda s, u, d: _daily_streak(s) >= 24,
    },
    {
        "id": "tippity_top",
        "name": "The tippity top",
        "desc": "Top the leaderboard for an hour",
        "reward": 30,
        "badge": "podium",
        "check": lambda s, u, d: (s.get("top_since") is not None
                                  and time.time() - s["top_since"] >= TOP_SECONDS),
    },
    {
        "id": "pick_your_poison",
        "name": "Pick your poison",
        "desc": "Collect a Poison or Killer powerup",
        "reward": -1,
        "badge": "poison",
        "check": lambda s, u, d: bool(s.get("poison_picked")),
    },
    {
        "id": "painpain_go_away",
        "name": "Painpain go away",
        "desc": "Collect a Heal or MegaHeal powerup",
        "reward": 1,
        "badge": "heal",
        "check": lambda s, u, d: bool(s.get("heal_picked")),
    },
    {
        "id": "cipher_it_out",
        "name": "Cipher it out",
        "desc": "Unlock a secret character",
        "reward": 20,
        "badge": "cipher",
        "check": lambda s, u, d: s.get("secret_chars_unlocked", 0) >= 1,
    },
    {
        "id": "i_cant_believe_it",
        "name": '"I" can\'t believe it',
        "desc": "Win 15 in a row without going back to the menu",
        "reward": 10,
        "badge": "eye_i",
        "check": lambda s, u, d: s.get("best_session_win_streak", 0) >= 15,
    },
    {
        "id": "still_in_the_matrix",
        "name": "Do we still live in the matrix?",
        "desc": "Block a projectile",
        "reward": 10,
        "badge": "matrix",
        "check": lambda s, u, d: bool(s.get("proj_blocked")),
    },
    {
        "id": "survive_the_vibe",
        "name": "Survive the vibe",
        "desc": "Last more than 2 minutes in survival",
        "reward": 10,
        "badge": "outnumbered",
        "check": lambda s, u, d: s.get("survival_best_seconds", 0) > 120,
    },
    {
        "id": "rpg_settles_ties",
        "name": "Use RPG to settle ties",
        "desc": "Slip out of a bazooka blast by a hair",
        "reward": 20,
        "badge": "blast_jump",
        "check": lambda s, u, d: bool(s.get("bazooka_dodged")),
    },
    {
        "id": "velcroraptor",
        "name": "Velcroraptor",
        "desc": "Win 10 matches",
        "reward": 10,
        "badge": "velcroraptor",
        "check": lambda s, u, d: s.get("wins_total", 0) >= 10,
    },
    {
        "id": "deja_vu",
        "name": "Deja vu",
        "desc": "Win the same fighter vs opponent on the same stage twice",
        "reward": 30,
        "badge": "eye",
        "check": lambda s, u, d: any(v >= 2 for v in (s.get("win_combos") or {}).values()),
    },
    {
        "id": "in_a_nutshell",
        "name": "In a nutshell",
        "desc": "Win a match in under 20 seconds",
        "reward": 0,
        "element": ("rock", 2),
        "badge": "nutshell",
        "check": lambda s, u, d: (s.get("fastest_win_seconds") is not None
                                  and s["fastest_win_seconds"] < 20),
    },
    {
        "id": "speed_demon",
        "name": "Speed demon",
        "desc": "Win a match in under 10 seconds",
        "reward": 0,
        "element": ("air", 3),
        "badge": "speed_demon",
        "check": lambda s, u, d: (s.get("fastest_win_seconds") is not None
                                  and s["fastest_win_seconds"] < 10),
    },
    {
        "id": "fire_in_the_mole",
        "name": "Fire in the mole",
        "desc": "Win a match in under 5 seconds",
        "reward": 0,
        "element": ("fire", 4),
        "badge": "fire_mole",
        "check": lambda s, u, d: (s.get("fastest_win_seconds") is not None
                                  and s["fastest_win_seconds"] < 5),
    },
    {
        "id": "map_the_flap",
        "name": "Map the flap",
        "desc": "Play every stage at least once",
        "reward": 10,
        "badge": "map",
        "check": lambda s, u, d: _all_stages_played(s),
    },
    {
        "id": "not_a_scratch",
        "name": "Not a scratch",
        "desc": "Win a match without taking a hit",
        "reward": 15,
        "badge": "unscratched",
        "check": lambda s, u, d: s.get("perfect_wins", 0) >= 1,
    },
    {
        "id": "last_leg",
        "name": "Last leg",
        "desc": "Win a match on your last sliver of health",
        "reward": 15,
        "badge": "last_leg",
        "check": lambda s, u, d: s.get("clutch_wins", 0) >= 1,
    },
    {
        "id": "mega_mind",
        "name": "Mega mind",
        "desc": "Beat the mega hard CPU",
        "reward": 20,
        "badge": "mega_mind",
        "check": lambda s, u, d: s.get("wins_mega_hard", 0) >= 1,
    },
    {
        "id": "hundred_club",
        "name": "Hundred club",
        "desc": "Put down 100 enemies in survival",
        "reward": 20,
        "badge": "tally",
        "check": lambda s, u, d: s.get("survival_kills", 0) >= 100,
    },
    {
        "id": "net_profit",
        "name": "Net profit",
        "desc": "Win a match against a real person online",
        "reward": 15,
        "badge": "online_fist",
        "check": lambda s, u, d: s.get("online_wins", 0) >= 1,
    },
    {
        "id": "elementary",
        "name": "Elementary",
        "desc": "Hold all six elements at once",
        "reward": 25,
        "badge": "elements",
        "check": lambda s, u, d: _has_all_elements(s),
    },
    {
        "id": "full_house",
        "name": "Full house",
        "desc": "Own 100 fighters",
        "reward": 25,
        "badge": "roster",
        "check": lambda s, u, d: len(u or ()) >= 100,
    },
    {
        "id": "something_for_everyone",
        "name": "Something for everyone",
        "desc": "Try every mode in the game",
        "reward": 15,
        "badge": "modes",
        "check": lambda s, u, d: set(ALL_MODES) <= set(s.get("modes_played", [])),
    },
    {
        "id": "fuse_the_lottery_ticket",
        "name": "Fuse the lottery ticket",
        "desc": "Fuse every character in a row with no failed fuse",
        "reward": 0,
        "elements": _all_elements_reward(),
        "badge": "lottery",
        "check": lambda s, u, d: _all_fused(s),
    },
    {
        "id": "serpentoduko",
        "name": "Serpentoduko",
        "desc": "Type serpentoduko as a snake without being hit",
        "reward": 10,
        "badge": "serpentoduko",
        "check": lambda s, u, d: bool(s.get("serpentoduko")),
    },
    {
        "id": "double_o_element",
        "name": "Double O Element",
        "desc": "Fuse your first character",
        "reward": 0,
        "element": ("water", 1),
        "badge": "double_o",
        "check": lambda s, u, d: s.get("fuses_done", 0) >= 1,
    },
    {
        "id": "noobs_first_holiday",
        "name": "Noob's first holiday",
        "desc": "Get your first seasonal character",
        "reward": 20,
        "badge": "saintnix",
        "check": lambda s, u, d: bool(s.get("seasonal_purchased")) or bool(s.get("fuser_purchased")),
    },
]

def reward_text(a):
    """How the payout reads on a badge: coins, elements, or nothing."""
    bits = []
    _r = a.get("reward")
    if _r:
        bits.append(f"+${_r}" if _r > 0 else f"-${abs(_r)}")
    if a.get("element"):
        _n, _q = a["element"]
        bits.append(f"+{_q} {_n}")
    if a.get("elements"):
        bits.append("+" + " +".join(f"{_q} {_n}" for _n, _q in a["elements"])
                    if len(a["elements"]) <= 2 else "+every element")
    return "   ".join(bits)


BY_ID = {a["id"]: a for a in ACHIEVEMENTS}


def earned(stats):
    """The ids the player already holds."""
    return set(stats.get("achievements", []))


def check_achievements(stats, unlocked=(), userdata=None):
    """Award anything newly true. Returns the entries just earned, in order.

    `userdata` is the online save (friends, username); conditions that live
    there rather than in stats read it from the third argument."""
    have = earned(stats)
    newly = []
    for a in ACHIEVEMENTS:
        if a["id"] in have:
            continue
        try:
            if not a["check"](stats, unlocked, userdata):
                continue
        except Exception:
            continue          # a broken condition must never break a match
        have.add(a["id"])
        newly.append(a)
        if a["reward"]:
            stats["seasonal_coins"] = max(0, stats.get("seasonal_coins", 0) + a["reward"])
        _els = a.get("elements") or ([a["element"]] if a.get("element") else [])
        if _els:
            _bag = stats.setdefault("fuser_elements", {})
            for _name, _qty in _els:
                _bag[_name] = _bag.get(_name, 0) + _qty
    if newly:
        stats["achievements"] = [a["id"] for a in ACHIEVEMENTS if a["id"] in have]
    return newly
