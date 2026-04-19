import pygame
import math
import random
from constants import *
from fight_data import STAGES, STAGE_MATCHUPS, POWERUPS

_font_cache = {}  # size → Font, avoids recreating fonts every frame

def _get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]

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
    bl = max(1, wy - sy)

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
        hull_top    = wy + int(4  * s)
        hull_bot    = wy + int(LEG_LEN * s) + int(6 * s)
        hull_h      = hull_bot - hull_top
        hull_w      = int(110 * s)
        hull_x      = wx - hull_w // 2
        tank_col    = (45, 90, 45)
        tank_dark   = (25, 55, 25)
        tank_mid    = (60, 115, 60)
        # --- Tracks (drawn first, behind hull) ---
        track_h = int(18 * s)
        track_w = hull_w + int(14 * s)
        track_x = wx - track_w // 2
        track_y = hull_bot - track_h
        pygame.draw.rect(surface, (25, 25, 25), (track_x, track_y, track_w, track_h), border_radius=int(8*s))
        pygame.draw.rect(surface, (50, 50, 50), (track_x, track_y, track_w, track_h), 2, border_radius=int(8*s))
        # Track wheel circles
        for wx2 in range(track_x + int(10*s), track_x + track_w - int(8*s), int(18*s)):
            pygame.draw.circle(surface, (70, 70, 70), (wx2, track_y + track_h//2), max(3, int(7*s)))
            pygame.draw.circle(surface, (30, 30, 30), (wx2, track_y + track_h//2), max(2, int(4*s)))
        # --- Hull body ---
        pygame.draw.rect(surface, tank_col,  (hull_x, hull_top, hull_w, hull_h), border_radius=int(3*s))
        pygame.draw.rect(surface, tank_dark, (hull_x, hull_top, hull_w, hull_h), 2, border_radius=int(3*s))
        # Hull panel lines
        pygame.draw.line(surface, tank_dark, (hull_x + int(8*s), hull_top), (hull_x + int(8*s), hull_bot - track_h), 1)
        pygame.draw.line(surface, tank_dark, (hull_x + hull_w - int(8*s), hull_top), (hull_x + hull_w - int(8*s), hull_bot - track_h), 1)
        # --- Turret (covers waist, stickman sits on top) ---
        t_w = int(62 * s); t_h = int(22 * s)
        t_x = wx - t_w // 2; t_y = hull_top - t_h + int(2*s)
        pygame.draw.rect(surface, tank_mid,  (t_x, t_y, t_w, t_h), border_radius=int(5*s))
        pygame.draw.rect(surface, tank_dark, (t_x, t_y, t_w, t_h), 2, border_radius=int(5*s))
        # Hatch ring around the stickman's waist
        pygame.draw.circle(surface, tank_dark, (wx, hull_top), int(14*s), 2)
        # --- Barrel ---
        barrel_base = (wx + facing * int(t_w//2 - 4), t_y + t_h//2)
        barrel_tip  = (barrel_base[0] + facing * int(52*s), barrel_base[1])
        pygame.draw.line(surface, tank_dark, barrel_base, barrel_tip, max(4, int(7*s)))
        pygame.draw.line(surface, tank_mid,  barrel_base, barrel_tip, max(2, int(4*s)))
        pygame.draw.circle(surface, tank_dark, barrel_tip, max(3, int(5*s)))
        # --- Helmet on stickman's head ---
        pygame.draw.circle(surface, tank_col, (hx, hy - int(hd*.1)), int(hd * 1.1))
        pygame.draw.circle(surface, tank_dark, (hx, hy - int(hd*.1)), int(hd * 1.1), 2)
        pygame.draw.line(surface, tank_dark, (hx - int(hd*.7), hy + int(hd*.15)), (hx + int(hd*.7), hy + int(hd*.15)), max(2, int(3*s)))

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

    elif char_name == "Viking":
        # Horned helmet
        helm_w = int(hd * 2.2)
        helm_h = int(hd * 1.1)
        pygame.draw.ellipse(surface, (100, 80, 50), (hx - helm_w//2, hy - hd - helm_h + int(4*s), helm_w, helm_h))
        pygame.draw.rect(surface, (100, 80, 50), (hx - int(hd*0.7), hy - int(4*s), int(hd*1.4), int(8*s)))  # cheek guard
        for side in (-1, 1):
            hox = hx + side * helm_w//2
            hoy = hy - hd - helm_h//2
            pygame.draw.line(surface, (220, 220, 220), (hox, hoy), (hox + side*int(14*s), hoy - int(20*s)), max(2, int(3*s)))
            pygame.draw.ellipse(surface, (220, 220, 220), (hox + side*int(10*s) - int(4*s), hoy - int(26*s), int(8*s), int(12*s)))
        # Axe in right hand
        ax_tip = (rhx + facing*int(36*s), rhy - int(6*s))
        pygame.draw.line(surface, (140, 100, 60), (rhx, rhy), ax_tip, max(2, int(4*s)))  # handle
        blade_cx = ax_tip[0] + facing*int(4*s)
        blade_cy = ax_tip[1]
        pts = [(blade_cx, blade_cy - int(22*s)),
               (blade_cx + facing*int(20*s), blade_cy - int(14*s)),
               (blade_cx + facing*int(18*s), blade_cy + int(8*s)),
               (blade_cx, blade_cy + int(14*s))]
        pygame.draw.polygon(surface, (180, 185, 195), pts)
        pygame.draw.polygon(surface, (220, 225, 240), pts, max(1, int(2*s)))

    elif char_name == "Wizard":
        # Tall pointy hat
        hat_base_w = int(hd * 2.4)
        pygame.draw.polygon(surface, (70, 30, 160),
                            [(hx - hat_base_w//2, hy - hd),
                             (hx + hat_base_w//2, hy - hd),
                             (hx + facing*int(4*s), hy - hd - int(52*s))])
        pygame.draw.ellipse(surface, (90, 40, 190),
                            (hx - hat_base_w//2 - int(4*s), hy - hd - int(7*s), hat_base_w + int(8*s), int(12*s)))
        # Stars on hat
        for sdx, sdy in [(facing*int(3*s), -int(30*s)), (-facing*int(5*s), -int(18*s))]:
            pygame.draw.circle(surface, (255, 230, 80), (hx + sdx, hy - hd + sdy), max(2, int(3*s)))
        # Magic staff in right hand
        staff_tip = (rhx + facing*int(6*s), rhy - int(40*s))
        pygame.draw.line(surface, (120, 90, 50), (rhx, rhy), staff_tip, max(2, int(3*s)))
        pygame.draw.circle(surface, (180, 80, 255), staff_tip, max(3, int(6*s)))
        pygame.draw.circle(surface, (220, 160, 255), staff_tip, max(2, int(4*s)))

    elif char_name == "Wrestler":
        # Singlet straps
        pygame.draw.line(surface, (200, 50, 50), (sx - int(4*s), sy), (sx - int(8*s), wy), max(2, int(3*s)))
        pygame.draw.line(surface, (200, 50, 50), (sx + int(4*s), sy), (sx + int(8*s), wy), max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 50, 50), (sx - int(10*s), wy, int(20*s), int(10*s)))
        # Headband
        pygame.draw.arc(surface, (255, 80, 80),
                        (hx - hd, hy - hd - int(8*s), hd*2, int(12*s)), 0, math.pi, max(2, int(4*s)))
        # Wrist bands
        pygame.draw.rect(surface, (255, 80, 80), (lhx - int(5*s), lhy - int(4*s), int(10*s), int(7*s)), border_radius=2)
        pygame.draw.rect(surface, (255, 80, 80), (rhx - int(5*s), rhy - int(4*s), int(10*s), int(7*s)), border_radius=2)

    elif char_name == "Clown":
        # Big clown hat
        hat_bw = int(hd * 2.6)
        pygame.draw.polygon(surface, (255, 80, 200),
                            [(hx - hat_bw//2, hy - hd),
                             (hx + hat_bw//2, hy - hd),
                             (hx, hy - hd - int(46*s))])
        pygame.draw.ellipse(surface, (255, 120, 220),
                            (hx - hat_bw//2 - int(3*s), hy - hd - int(6*s), hat_bw + int(6*s), int(11*s)))
        pygame.draw.circle(surface, (255, 255, 80), (hx, hy - hd - int(46*s)), max(3, int(5*s)))  # pompom
        # Red nose
        pygame.draw.circle(surface, (255, 40, 40), (hx, hy + int(2*s)), max(3, int(6*s)))
        # Colorful collar
        for i, cx2 in enumerate(range(sx - int(18*s), sx + int(20*s), int(9*s))):
            c = [(255,80,80),(255,200,0),(80,200,255),(200,80,255)][i % 4]
            pygame.draw.circle(surface, c, (cx2, sy + int(8*s)), max(3, int(5*s)))
        # Big shoes
        for fx, fy in [(lhx, lhy), (rhx, rhy)]:
            pass  # shoes would be on feet coords - skip for simplicity

    elif char_name == "Speedster":
        # Aerodynamic visor
        pygame.draw.ellipse(surface, (40, 40, 60),
                            (hx - hd - int(2*s), hy - int(6*s), int(hd*2 + 4*s), int(10*s)))
        pygame.draw.ellipse(surface, (100, 200, 255),
                            (hx - hd, hy - int(5*s), hd*2, int(8*s)), max(1, int(2*s)))
        # Lightning bolt on chest
        bolt = [(sx + facing*int(3*s), sy + int(6*s)),
                (sx - facing*int(2*s), sy + int(20*s)),
                (sx + facing*int(6*s), sy + int(20*s)),
                (sx - facing*int(3*s), sy + int(36*s))]
        pygame.draw.lines(surface, (255, 230, 0), False, bolt, max(2, int(3*s)))

    elif char_name == "Knight":
        # Full great helm
        helm_w = int(hd * 2.1)
        helm_h = int(hd * 2.2)
        pygame.draw.rect(surface, (130, 135, 150),
                         (hx - helm_w//2, hy - hd - int(helm_h*0.6), helm_w, helm_h),
                         border_radius=max(3, int(5*s)))
        # Visor slit
        pygame.draw.rect(surface, (20, 20, 30),
                         (hx - int(hd*0.7), hy - int(4*s), int(hd*1.4), int(7*s)))
        # Plume
        pygame.draw.line(surface, (180, 20, 20),
                         (hx + facing*int(3*s), hy - hd - int(helm_h*0.55)),
                         (hx + facing*int(8*s), hy - hd - int(helm_h*0.55) - int(22*s)),
                         max(2, int(3*s)))
        # Sword in right hand (big)
        blade_base = (rhx, rhy - int(4*s))
        blade_tip  = (rhx + facing*int(50*s), rhy - int(28*s))
        pygame.draw.line(surface, (200, 210, 220), blade_base, blade_tip, max(2, int(4*s)))
        pygame.draw.line(surface, (240, 245, 255), blade_base, blade_tip, max(1, int(2*s)))  # shine
        # Cross guard
        gx, gy = rhx + facing*int(10*s), rhy - int(8*s)
        pygame.draw.line(surface, (160, 130, 60), (gx - int(10*s), gy), (gx + int(10*s), gy), max(2, int(3*s)))

    elif char_name == "Lava Man":
        # Glowing lava cracks on body
        for ly, lx1, lx2 in [(sy+int(10*s), sx-int(8*s), sx+int(5*s)),
                              (sy+int(25*s), sx+int(3*s), sx-int(6*s)),
                              (sy+int(38*s), sx-int(4*s), sx+int(10*s))]:
            pygame.draw.line(surface, (255, 200, 50), (lx1, ly), (lx2, ly+int(8*s)), max(1,int(2*s)))
        # Horns on head
        for side in (-1, 1):
            hpx = hx + side * int(hd*0.7)
            pygame.draw.polygon(surface, (80, 20, 0),
                [(hpx-side*int(4*s), hy-hd+int(2*s)),
                 (hpx+side*int(4*s), hy-hd+int(2*s)),
                 (hpx+side*int(2*s), hy-hd-int(18*s))])
        # Glowing eyes
        pygame.draw.circle(surface, (255, 180, 0), (hx - int(hd*0.35), hy - int(2*s)), max(2, int(4*s)))
        pygame.draw.circle(surface, (255, 180, 0), (hx + int(hd*0.35), hy - int(2*s)), max(2, int(4*s)))

    elif char_name == "Angel":
        # Halo
        pygame.draw.ellipse(surface, (255, 240, 100),
                            (hx - int(hd*1.1), hy - hd - int(18*s), int(hd*2.2), int(10*s)), max(2, int(3*s)))
        pygame.draw.ellipse(surface, (255, 255, 160),
                            (hx - int(hd*1.1), hy - hd - int(18*s), int(hd*2.2), int(10*s)), max(1, int(2*s)))
        # Wings (two arcs on sides)
        for side in (-1, 1):
            wx1 = sx + side * int(hd*0.5)
            wy1 = sy + int(6*s)
            pygame.draw.arc(surface, (255, 250, 230),
                            (wx1 + side*int(4*s) - int(30*s), wy1 - int(30*s), int(36*s), int(44*s)),
                            math.radians(200 if side == 1 else -20),
                            math.radians(340 if side == 1 else 160),
                            max(2, int(4*s)))
            pygame.draw.arc(surface, (240, 240, 210),
                            (wx1 + side*int(4*s) - int(22*s), wy1 + int(4*s), int(28*s), int(32*s)),
                            math.radians(190 if side == 1 else -10),
                            math.radians(350 if side == 1 else 170),
                            max(1, int(3*s)))

    elif char_name == "Mime":
        # Black and white striped shirt
        for si in range(3):
            sy2m = sy + int((si * 14 + 4) * s)
            pygame.draw.rect(surface, (30, 30, 30),
                             (sx - int(12*s), sy2m, int(24*s), int(6*s)))
        # White face with black outlines
        pygame.draw.circle(surface, (255, 255, 255), (hx, hy), hd)
        pygame.draw.circle(surface, (0, 0, 0), (hx, hy), hd, max(1, int(2*s)))
        # Sad/happy mime smile
        pygame.draw.arc(surface, (0, 0, 0),
                        (hx - int(hd*0.55), hy, int(hd*1.1), int(hd*0.8)),
                        0, math.pi, max(1, int(2*s)))
        # Beret
        pygame.draw.ellipse(surface, (20, 20, 20),
                            (hx - int(hd*1.1), hy - hd - int(10*s), int(hd*2.2), int(12*s)))
        pygame.draw.ellipse(surface, (30, 30, 30),
                            (hx - int(hd*0.7), hy - hd - int(18*s), int(hd*1.4), int(14*s)))

    elif char_name == "Lumberjack":
        # Flannel shirt (red/dark checked)
        for ci in range(3):
            sx2l = sx - int(12*s) + ci * int(8*s)
            for ri in range(4):
                rc = (200, 40, 30) if (ci + ri) % 2 == 0 else (80, 20, 15)
                pygame.draw.rect(surface, rc, (sx2l, sy + int(ri*10*s), int(8*s), int(10*s)))
        # Beard
        pygame.draw.ellipse(surface, (130, 80, 40),
                            (hx - int(hd*0.9), hy + int(4*s), int(hd*1.8), int(hd*1.1)))
        # Axe in right hand
        ax_tip2 = (rhx + facing*int(38*s), rhy - int(4*s))
        pygame.draw.line(surface, (130, 90, 40), (rhx, rhy), ax_tip2, max(2, int(4*s)))
        bx2l = ax_tip2[0] + facing*int(3*s)
        by2l = ax_tip2[1]
        lpts = [(bx2l, by2l - int(24*s)),
                (bx2l + facing*int(22*s), by2l - int(12*s)),
                (bx2l + facing*int(20*s), by2l + int(10*s)),
                (bx2l, by2l + int(16*s))]
        pygame.draw.polygon(surface, (160, 170, 180), lpts)
        pygame.draw.polygon(surface, (200, 210, 220), lpts, max(1, int(2*s)))

    elif char_name == "Bouncer":
        # Black vest
        pygame.draw.rect(surface, (20, 20, 20),
                         (sx - int(14*s), sy, int(28*s), int(36*s)), border_radius=max(2,int(3*s)))
        pygame.draw.line(surface, (50, 50, 50),
                         (sx, sy + int(4*s)), (sx, sy + int(32*s)), max(1, int(2*s)))
        # Big boxing gloves on both hands
        for ghx, ghy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (220, 60, 20), (ghx, ghy), max(5, int(10*s)))
            pygame.draw.circle(surface, (255, 90, 40), (ghx, ghy), max(3, int(7*s)), max(1,int(2*s)))
        # Sunglasses
        for side2, ex2 in [(-1, hx - int(hd*0.55)), (1, hx + int(hd*0.1))]:
            pygame.draw.rect(surface, (10, 10, 10),
                             (ex2 - int(3*s), hy - int(5*s), int(hd*0.7), int(8*s)), border_radius=2)
        pygame.draw.line(surface, (10, 10, 10),
                         (hx - int(hd*0.1), hy - int(2*s)), (hx + int(hd*0.1), hy - int(2*s)),
                         max(1, int(2*s)))

    elif char_name == "Demon":
        # Large curved horns
        for side in (-1, 1):
            hbx = hx + side * int(hd*0.8)
            hby = hy - hd + int(4*s)
            pts2 = [(hbx - side*int(4*s), hby),
                    (hbx + side*int(16*s), hby - int(28*s)),
                    (hbx + side*int(20*s), hby - int(10*s))]
            pygame.draw.polygon(surface, (100, 10, 10), pts2)
            pygame.draw.polygon(surface, (140, 30, 20), pts2, max(1,int(2*s)))
        # Tail
        tpts = [(sx - facing*int(8*s), wy + int(8*s)),
                (sx - facing*int(30*s), wy + int(28*s)),
                (sx - facing*int(36*s), wy + int(18*s)),
                (sx - facing*int(28*s), wy + int(10*s))]
        pygame.draw.lines(surface, (140, 20, 20), False, tpts, max(2, int(3*s)))
        # Arrow-head tail tip
        pygame.draw.polygon(surface, (180, 30, 30),
            [(sx - facing*int(28*s), wy + int(10*s)),
             (sx - facing*int(40*s), wy + int(6*s)),
             (sx - facing*int(34*s), wy + int(20*s))])
        # Glowing red eyes
        for ex3 in [hx - int(hd*0.38), hx + int(hd*0.38)]:
            pygame.draw.circle(surface, (255, 60, 0), (ex3, hy - int(3*s)), max(2, int(5*s)))
            pygame.draw.circle(surface, (255, 150, 0), (ex3, hy - int(3*s)), max(1, int(3*s)))
        # Pitchfork in right hand
        pf_top = (rhx + facing*int(8*s), rhy - int(46*s))
        pygame.draw.line(surface, (160, 130, 60), (rhx, rhy), pf_top, max(2, int(3*s)))
        for pfd in [-1, 0, 1]:
            pygame.draw.line(surface, (200, 180, 80),
                pf_top,
                (pf_top[0] + pfd*int(8*s), pf_top[1] - int(14*s)),
                max(1, int(2*s)))

    elif char_name == "Dark Mage":
        # Dark hooded robe
        pygame.draw.rect(surface, (30, 10, 60),
                         (sx - int(14*s), sy, int(28*s), int(38*s)), border_radius=max(2,int(3*s)))
        # Hood over head
        hood_pts = [(hx - int(hd*1.3), hy - hd + int(6*s)),
                    (hx, hy - hd - int(28*s)),
                    (hx + int(hd*1.3), hy - hd + int(6*s))]
        pygame.draw.polygon(surface, (30, 10, 60), hood_pts)
        # Glowing skull on chest
        pygame.draw.circle(surface, (180, 180, 200),
                           (sx, sy + int(14*s)), max(3, int(6*s)))
        pygame.draw.circle(surface, (220, 220, 240),
                           (sx, sy + int(14*s)), max(2, int(4*s)), max(1,int(1*s)))
        # Dark staff with skull top in right hand
        st_tip = (rhx + facing*int(5*s), rhy - int(44*s))
        pygame.draw.line(surface, (60, 40, 80), (rhx, rhy), st_tip, max(2, int(3*s)))
        pygame.draw.circle(surface, (160, 20, 200), st_tip, max(3, int(6*s)))
        pygame.draw.circle(surface, (200, 80, 255), st_tip, max(2, int(4*s)))
        # Stars orbiting staff tip
        for sai in range(3):
            sa2 = math.radians(pygame.time.get_ticks() * 0.3 + sai * 120)
            sdx2 = int(math.cos(sa2) * int(10*s))
            sdy2 = int(math.sin(sa2) * int(8*s))
            pygame.draw.circle(surface, (180, 100, 255), (st_tip[0]+sdx2, st_tip[1]+sdy2), max(1,int(3*s)))

    elif char_name == "Pirate":
        # Tricorn hat
        hat_bw2 = int(hd * 2.6)
        pygame.draw.polygon(surface, (20, 15, 10),
                            [(hx - hat_bw2//2, hy - hd),
                             (hx + hat_bw2//2, hy - hd),
                             (hx + facing*int(6*s), hy - hd - int(38*s))])
        pygame.draw.ellipse(surface, (30, 22, 15),
                            (hx - hat_bw2//2 - int(4*s), hy - hd - int(6*s),
                             hat_bw2 + int(8*s), int(11*s)))
        pygame.draw.ellipse(surface, (60, 50, 30),
                            (hx - hat_bw2//2 - int(4*s), hy - hd - int(6*s),
                             hat_bw2 + int(8*s), int(11*s)), max(1,int(2*s)))
        # Eyepatch
        pygame.draw.circle(surface, (10, 8, 5),
                           (hx + facing*int(hd*0.4), hy - int(4*s)), max(3, int(6*s)))
        pygame.draw.circle(surface, (30, 25, 15),
                           (hx + facing*int(hd*0.4), hy - int(4*s)), max(3, int(6*s)), max(1,int(2*s)))
        pygame.draw.line(surface, (40, 30, 20),
                         (hx + facing*int(hd*0.4) - int(hd*0.5), hy - int(4*s)),
                         (hx + facing*int(hd*0.4) + int(hd*0.5), hy - int(4*s)), max(1,int(1*s)))
        # Hook on left hand
        pygame.draw.arc(surface, (180, 185, 195),
                        (lhx - int(10*s), lhy - int(10*s), int(14*s), int(14*s)),
                        math.radians(-30), math.radians(200), max(2, int(3*s)))

    elif char_name == "Mr. Crit":
        # Spinning gold star above his head
        t     = pygame.time.get_ticks()
        angle = (t * 0.004) % (2 * math.pi)
        cx    = hx
        cy    = hy - int(hd * 1.6)
        r_out = max(4, int(10 * s))
        r_in  = max(2, int(4  * s))
        pts   = []
        for i in range(10):
            r   = r_out if i % 2 == 0 else r_in
            a   = angle + i * math.pi / 5
            pts.append((int(cx + math.cos(a) * r), int(cy + math.sin(a) * r)))
        if len(pts) >= 3:
            pygame.draw.polygon(surface, (255, 215, 0), pts)
            pygame.draw.polygon(surface, (255, 255, 120), pts, max(1, int(s)))

    elif char_name == "Whipper":
        # Coiled whip looped at the hip
        hip_x = hx + int(facing * hd * 0.55)
        hip_y = hy + int(hd * 1.6)
        for i in range(4):
            r_loop = max(2, int((10 - i * 2) * s))
            col = (110 + i * 10, 60 + i * 5, 15 + i * 3)
            pygame.draw.circle(surface, col, (hip_x, hip_y + int(i * 2 * s)), r_loop, max(1, int(2 * s)))
        # Short dangling tip
        tip_x = hip_x + int(facing * 8 * s)
        tip_y = hip_y + int(12 * s)
        pygame.draw.line(surface, (140, 80, 25),
                         (hip_x, hip_y + int(6 * s)), (tip_x, tip_y), max(1, int(2 * s)))

    elif char_name == "Laser Eyes":
        # Glowing red eyes
        t = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(t * 0.008)
        r1 = max(3, int((5 + 3 * pulse) * s))
        for eye_ox in (-int(hd * 0.38), int(hd * 0.38)):
            ex, ey = hx + eye_ox, hy - int(hd * 0.1)
            pygame.draw.circle(surface, (255, int(40 + 40 * pulse), 0), (ex, ey), r1)
            pygame.draw.circle(surface, (255, 220, 80), (ex, ey), max(1, r1 - 2))

    elif char_name == "Hammerhead":
        # Hard hat
        hat_w = int(hd * 2.0)
        hat_h = int(hd * 0.7)
        pygame.draw.ellipse(surface, (40, 30, 20), (hx - hat_w//2, hy - hd - hat_h + int(2*s), hat_w, hat_h))
        pygame.draw.rect(surface, (40, 30, 20), (hx - int(hat_w*0.6), hy - hd - int(4*s), int(hat_w*1.2), int(5*s)))
        # Gigantic hammer in right hand
        shaft_len = int(90 * s)
        head_w    = int(70 * s)
        head_h    = int(52 * s)
        shaft_w   = max(3, int(8 * s))
        hx2, hy2 = rhx, rhy   # hand position
        tip_x  = hx2 + facing * shaft_len
        tip_y2 = hy2 - int(8 * s)
        # Shaft
        pygame.draw.line(surface, (140, 90, 40), (hx2, hy2), (tip_x, tip_y2), shaft_w)
        pygame.draw.line(surface, (180, 130, 70), (hx2, hy2 - shaft_w//3), (tip_x, tip_y2 - shaft_w//3), max(1, shaft_w//3))  # highlight
        # Hammer head fill
        hd_x = tip_x - head_w//2 + facing * int(10 * s)
        hd_y = tip_y2 - head_h//2
        pygame.draw.rect(surface, (60, 65, 75), (hd_x, hd_y, head_w, head_h), border_radius=max(3, int(6*s)))
        # Face highlight
        pygame.draw.rect(surface, (110, 115, 130), (hd_x + int(4*s), hd_y + int(4*s), head_w - int(8*s), int(16*s)), border_radius=max(2, int(4*s)))
        # Outline
        pygame.draw.rect(surface, (160, 165, 180), (hd_x, hd_y, head_w, head_h), max(1, int(3*s)), border_radius=max(3, int(6*s)))

    elif char_name == "Kitsune":
        # Fox ears — two pointed triangles atop the head
        for ear_side in (-1, 1):
            ear_base_x = hx + ear_side * int(hd * 0.55)
            ear_tip_x  = hx + ear_side * int(hd * 0.9)
            ear_tip_y  = hy - int(hd * 2.1)
            ear_base_y = hy - int(hd * 0.9)
            pygame.draw.polygon(surface, (220, 100, 0),
                                [(ear_base_x, ear_base_y),
                                 (ear_tip_x,  ear_tip_y),
                                 (ear_base_x + ear_side * int(hd * 0.15), ear_tip_y + int(hd * 0.7))])
            pygame.draw.polygon(surface, (255, 180, 80),
                                [(ear_base_x, ear_base_y),
                                 (ear_tip_x,  ear_tip_y),
                                 (ear_base_x + ear_side * int(hd * 0.15), ear_tip_y + int(hd * 0.7))], max(1, int(2*s)))
        # Multiple fox tails (fanned behind)
        for ti in range(3):
            tail_ang = math.radians(90 + (ti - 1) * 30)
            tail_base = (wx - facing * int(hd * 0.5), wy + int(6 * s))
            tail_mid  = (tail_base[0] - facing * int(30 * s),
                         tail_base[1] - int(22 * s) + ti * int(8 * s))
            tail_tip  = (tail_base[0] - facing * int(50 * s),
                         tail_mid[1]  - int(20 * s))
            pygame.draw.line(surface, (235, 120, 20), tail_base, tail_mid, max(3, int(5 * s)))
            pygame.draw.line(surface, (235, 120, 20), tail_mid,  tail_tip, max(2, int(3 * s)))
            pygame.draw.circle(surface, (255, 240, 220), tail_tip, max(2, int(4 * s)))

    elif char_name == "Medusa":
        t = pygame.time.get_ticks()
        # Snake hair — 6 snakes waving from the head
        for si in range(6):
            base_ang = si * 60
            base_x   = hx + int(math.cos(math.radians(base_ang)) * hd)
            base_y   = hy + int(math.sin(math.radians(base_ang)) * hd * 0.6) - int(hd * 0.3)
            wave     = math.sin(t * 0.006 + si * 1.0)
            mid_x    = base_x + int(math.cos(math.radians(base_ang + 20)) * int(14 * s))
            mid_y    = base_y - int(14 * s) + int(wave * 4 * s)
            tip_x    = mid_x + int(math.cos(math.radians(base_ang - 10)) * int(10 * s))
            tip_y    = mid_y - int(10 * s)
            pygame.draw.line(surface, (40, 160, 40),  (base_x, base_y), (mid_x, mid_y), max(2, int(3 * s)))
            pygame.draw.line(surface, (40, 160, 40),  (mid_x, mid_y),   (tip_x, tip_y), max(2, int(2 * s)))
            # Forked tongue
            pygame.draw.line(surface, (220, 30, 30),
                             (tip_x, tip_y),
                             (tip_x + int(facing * 3 * s), tip_y - int(3 * s)), 1)
            pygame.draw.line(surface, (220, 30, 30),
                             (tip_x, tip_y),
                             (tip_x - int(facing * 2 * s), tip_y - int(3 * s)), 1)
        # Glowing green eyes
        pulse = 0.5 + 0.5 * math.sin(t * 0.01)
        er = max(3, int((4 + 3 * pulse) * s))
        for ex_off in (-int(hd * 0.38), int(hd * 0.38)):
            ex, ey = hx + ex_off, hy - int(hd * 0.1)
            pygame.draw.circle(surface, (0, int(160 + 80 * pulse), 0), (ex, ey), er)
            pygame.draw.circle(surface, (180, 255, 130), (ex, ey), max(1, er - 2))

    elif char_name == "Omus":
        # Inverted sumo: small spiked hair + lightning bolt on chest (speed symbol)
        pygame.draw.line(surface, (30, 80, 255), (hx, hy - hd), (hx, hy - int(hd * 1.9)), max(2, int(3 * s)))
        pygame.draw.line(surface, (30, 80, 255), (hx - int(hd * 0.4), hy - int(hd * 1.5)),
                         (hx + int(hd * 0.4), hy - int(hd * 1.5)), max(2, int(3 * s)))
        # Lightning bolt on chest
        bolt = [(sx + int(facing * 4 * s), sy + int(4 * s)),
                (sx - int(facing * 4 * s), sy + int(14 * s)),
                (sx + int(facing * 2 * s), sy + int(14 * s)),
                (sx - int(facing * 4 * s), sy + int(24 * s))]
        pygame.draw.lines(surface, (100, 160, 255), False, bolt, max(1, int(2 * s)))

    elif char_name == "The Creator":
        # Construction hard hat (yellow)
        hat_w = int(hd * 2.2)
        hat_h = int(hd * 0.65)
        pygame.draw.ellipse(surface, (240, 200, 20),
                            (hx - hat_w // 2, hy - hd - hat_h + int(3 * s), hat_w, hat_h))
        pygame.draw.rect(surface, (240, 200, 20),
                         (hx - int(hat_w * 0.55), hy - hd - int(4 * s), int(hat_w * 1.1), int(5 * s)))
        pygame.draw.rect(surface, (180, 140, 10),
                         (hx - int(hat_w * 0.55), hy - hd - int(4 * s), int(hat_w * 1.1), int(5 * s)), 1)
        # Small block held in forward hand
        bsz = max(5, int(10 * s))
        pygame.draw.rect(surface, (180, 120, 50), (rhx - bsz // 2, rhy - bsz // 2, bsz, bsz))
        pygame.draw.rect(surface, (220, 160, 80), (rhx - bsz // 2, rhy - bsz // 2, bsz, bsz), 1)

    elif char_name == "Disorientated":
        t = pygame.time.get_ticks()
        # Spinning dizzy stars above head
        for i in range(4):
            ang = math.radians(t * 0.2 + i * 90)
            sx2 = hx + int(math.cos(ang) * int(hd * 1.3))
            sy2 = hy - int(hd * 1.5) + int(math.sin(ang) * int(hd * 0.5))
            pygame.draw.circle(surface, (255, 220, 50), (sx2, sy2), max(2, int(4 * s)))
            pygame.draw.circle(surface, (255, 100, 200), (sx2, sy2), max(1, int(2 * s)))
        # Googly / spiral eyes
        for ex_off in (-int(hd * 0.38), int(hd * 0.38)):
            ex, ey = hx + ex_off, hy - int(hd * 0.1)
            pygame.draw.circle(surface, (255, 255, 255), (ex, ey), max(3, int(5 * s)))
            spiral_a = math.radians(t * 0.4)
            px2 = ex + int(math.cos(spiral_a) * int(2 * s))
            py2 = ey + int(math.sin(spiral_a) * int(2 * s))
            pygame.draw.circle(surface, (80, 0, 80), (px2, py2), max(1, int(2 * s)))

    elif char_name == "Janitor":
        # Mop bucket cap (grey baseball cap)
        cap_brim = int(hd * 1.6)
        pygame.draw.ellipse(surface, (140, 140, 120),
                            (hx - cap_brim // 2, hy - hd - int(4 * s), cap_brim, int(7 * s)))
        pygame.draw.ellipse(surface, (160, 160, 140),
                            (hx - int(hd * 0.75), hy - hd - int(hd * 0.6),
                             int(hd * 1.5), int(hd * 0.75)))
        # Mop in rear hand (trailing side)
        mp_x = lhx
        mp_y = lhy
        # Handle
        pygame.draw.line(surface, (160, 110, 60),
                         (mp_x, mp_y), (mp_x - facing * int(8 * s), mp_y + int(50 * s)),
                         max(2, int(3 * s)))
        # Mop head (stringy)
        mop_bot = (mp_x - facing * int(8 * s), mp_y + int(50 * s))
        for mi in range(5):
            mop_off = (mi - 2) * int(4 * s)
            pygame.draw.line(surface, (220, 220, 220),
                             mop_bot,
                             (mop_bot[0] + mop_off, mop_bot[1] + int(12 * s)),
                             max(1, int(2 * s)))
        # Blue overalls stripe on chest
        pygame.draw.line(surface, (80, 100, 200),
                         (sx - int(hd * 0.3), sy + int(6 * s)),
                         (sx + int(hd * 0.3), sy + int(6 * s)),
                         max(2, int(4 * s)))

    elif char_name == "Riptide":
        # Water droplet halo around head
        t = pygame.time.get_ticks()
        for di in range(5):
            a    = math.radians(t * 0.15 + di * 72)
            dx2  = hx + int(math.cos(a) * int(hd * 1.6))
            dy2  = hy + int(math.sin(a) * int(hd * 1.2)) - int(hd * 0.3)
            pygame.draw.circle(surface, (0, 160, 220), (dx2, dy2), max(2, int(4 * s)))
            pygame.draw.circle(surface, (180, 240, 255), (dx2, dy2), max(1, int(2 * s)))
        # Wave pattern on chest
        for wi in range(3):
            wx2 = sx - int(hd * 0.5) + wi * int(hd * 0.5)
            wy2 = sy + int(10 * s)
            wy3 = sy + int(18 * s)
            wave_off = int(math.sin(t * 0.01 + wi) * 3 * s)
            pygame.draw.arc(surface, (0, 200, 255),
                            (wx2 - int(5 * s), wy2 + wave_off - int(4 * s),
                             int(10 * s), int(8 * s)),
                            math.radians(0), math.radians(180), max(1, int(2 * s)))

    elif char_name == "Whirlpool":
        t = pygame.time.get_ticks()
        # Spinning swirl rings around the body — speed reflects momentum
        for ri in range(3):
            ring_r   = int((hd * 1.4 + ri * hd * 0.5) * s)
            ring_ang = math.radians(t * (0.3 + ri * 0.15) + ri * 120)
            dot_x    = hx + int(math.cos(ring_ang) * ring_r)
            dot_y    = wy - int(hd) + int(math.sin(ring_ang) * int(ring_r * 0.5))
            pygame.draw.circle(surface, (0, 140 + ri * 30, 200), (dot_x, dot_y),
                               max(2, int((4 - ri) * s)))
        # Water swirl on forehead
        for si in range(4):
            sa = math.radians(t * 0.25 + si * 90)
            sx2 = hx + int(math.cos(sa) * int(hd * 0.6))
            sy2 = hy - int(hd * 0.3) + int(math.sin(sa) * int(hd * 0.4))
            pygame.draw.circle(surface, (0, 180, 240), (sx2, sy2), max(1, int(2 * s)))

    elif char_name == "Shadowfax":
        # Flowing silver mane from head
        t = pygame.time.get_ticks()
        mane_pts = [(hx - facing * int(hd * 0.4), hy - int(hd * 0.8))]
        for mi in range(5):
            wave = math.sin(t * 0.008 + mi * 0.8) * int(6 * s)
            mane_pts.append((hx - facing * int((hd * 0.3 + mi * hd * 0.35) * s),
                             hy - int(hd * 0.8) + mi * int(8 * s) + int(wave)))
        if len(mane_pts) >= 2:
            pygame.draw.lines(surface, (200, 200, 240), False, mane_pts, max(2, int(3 * s)))
            pygame.draw.lines(surface, (255, 255, 255), False, mane_pts[:3], max(1, int(2 * s)))
        # Glowing speed aura (faint rings)
        for ri in range(2):
            ring_r = int(hd * (1.2 + ri * 0.5))
            pygame.draw.circle(surface, (180, 180, 220),
                               (hx, hy), ring_r, max(1, int(s)))

    elif char_name == "ASCII":
        # Keyboard key decorations at body joints
        key_font = font_tiny
        _key_positions = [
            (hx,  hy - int(hd * 0.1), '@'),
            (sx,  sy + int(6 * s),    '#'),
            (wx,  wy,                  '$'),
            (lhx, lhy,                '<'),
            (rhx, rhy,                '>'),
        ]
        for kx, ky, kch in _key_positions:
            kr = max(5, int(8 * s))
            # Key background (white rounded rect)
            pygame.draw.rect(surface, (230, 230, 230),
                             (kx - kr, ky - kr, kr * 2, kr * 2),
                             border_radius=max(1, int(2 * s)))
            pygame.draw.rect(surface, (100, 100, 100),
                             (kx - kr, ky - kr, kr * 2, kr * 2),
                             max(1, int(s)), border_radius=max(1, int(2 * s)))
            # Key character
            txt = key_font.render(kch, True, (20, 20, 20))
            surface.blit(txt, (kx - txt.get_width() // 2, ky - txt.get_height() // 2))
        # Floating random key chars orbiting the body
        t = pygame.time.get_ticks()
        orbit_keys = ['Q','W','E','R','A','S','D','F','Z','X','C','V']
        for oi, ok in enumerate(orbit_keys[:4]):
            oa = math.radians(t * 0.12 + oi * 90)
            ox2 = hx + int(math.cos(oa) * int(hd * 2.2))
            oy2 = wy - int(hd) + int(math.sin(oa) * int(hd * 1.2))
            okr = max(4, int(6 * s))
            pygame.draw.rect(surface, (200, 200, 200),
                             (ox2 - okr, oy2 - okr, okr * 2, okr * 2),
                             border_radius=max(1, int(2 * s)))
            pygame.draw.rect(surface, (80, 80, 80),
                             (ox2 - okr, oy2 - okr, okr * 2, okr * 2),
                             1, border_radius=max(1, int(2 * s)))
            otxt = key_font.render(ok, True, (10, 10, 10))
            surface.blit(otxt, (ox2 - otxt.get_width() // 2, oy2 - otxt.get_height() // 2))

    elif char_name == "Snake":
        pass  # head drawn directly in Fighter.draw() as a block

    elif char_name == "Enraged":
        # Angry red aura flames on head + furrowed brows
        t = pygame.time.get_ticks()
        for fi in range(5):
            fa = math.radians(fi * 72 + t * 0.25)
            fx = hx + int(math.cos(fa) * hd * 1.3)
            fy = hy + int(math.sin(fa) * hd * 1.0) - int(hd * 0.4)
            pygame.draw.circle(surface, (255, 60, 0), (fx, fy), max(2, int(4 * s)))
            pygame.draw.circle(surface, (255, 200, 0), (fx, fy), max(1, int(2 * s)))
        # Angry brows
        for side in (-1, 1):
            bx1 = hx + side * int(hd * 0.6)
            bx2 = hx + side * int(hd * 0.2)
            by1 = hy - int(hd * 0.55)
            by2 = hy - int(hd * 0.7)
            pygame.draw.line(surface, (30, 20, 0), (bx1, by1), (bx2, by2), max(1, int(2 * s)))

    elif char_name == "Beekeeper":
        # Beehive hat (hexagonal dome) + striped collar
        hat_r = int(hd * 1.1)
        for tier in range(3):
            rr = max(3, hat_r - tier * int(4 * s))
            yy = hy - hd - int(tier * 8 * s)
            pygame.draw.circle(surface, (220, 170, 0), (hx, yy), rr)
            pygame.draw.circle(surface, (160, 120, 0), (hx, yy), rr, max(1, int(s)))
        # Top knob
        pygame.draw.circle(surface, (200, 150, 0), (hx, hy - hd - int(20 * s)), max(2, int(3 * s)))
        # Black & yellow collar stripe
        stripe_y = sy + int(6 * s)
        pygame.draw.line(surface, (20, 20, 0), (hx - int(8 * s), stripe_y), (hx + int(8 * s), stripe_y), max(1, int(2 * s)))

    elif char_name == "Plague Doctor":
        # Long beak mask
        beak_len = int(hd * 1.6)
        beak_tip = (hx + int(facing * beak_len), hy + int(4 * s))
        beak_top = (hx + int(facing * int(hd * 0.3)), hy - int(hd * 0.3))
        beak_bot = (hx + int(facing * int(hd * 0.3)), hy + int(hd * 0.5))
        pygame.draw.polygon(surface, (80, 100, 80), [beak_top, beak_tip, beak_bot])
        pygame.draw.polygon(surface, (40, 60, 40),  [beak_top, beak_tip, beak_bot], max(1, int(s)))
        # Dark hat brim
        pygame.draw.ellipse(surface, (20, 20, 20),
                            (hx - int(hd * 1.2), hy - hd - int(4 * s),
                             int(hd * 2.4), int(8 * s)))
        pygame.draw.rect(surface, (20, 20, 20),
                         (hx - int(hd * 0.7), hy - hd - int(18 * s),
                          int(hd * 1.4), int(18 * s)))

    elif char_name == "Necromancer":
        # Dark hood
        hood_pts = [
            (hx - int(hd * 1.1), hy + int(hd * 0.3)),
            (hx,                  hy - hd - int(20 * s)),
            (hx + int(hd * 1.1), hy + int(hd * 0.3)),
        ]
        pygame.draw.polygon(surface, (30, 10, 50), hood_pts)
        pygame.draw.polygon(surface, (80, 40, 120), hood_pts, max(1, int(s)))
        # Glowing eyes in the dark hood
        for side in (-1, 1):
            ex2 = hx + side * int(hd * 0.35)
            pygame.draw.circle(surface, (160, 0, 255), (ex2, hy - int(2 * s)), max(2, int(3 * s)))

    elif char_name == "Joker":
        # Jester hat — two-pointed with bells
        t = pygame.time.get_ticks()
        for side, angle_off in [(-1, math.radians(150 + math.sin(t * 0.003) * 8)),
                                  (1,  math.radians(30  + math.sin(t * 0.003 + 1) * 8))]:
            px = hx + int(math.cos(angle_off) * hd * 1.6)
            py = hy - hd + int(math.sin(angle_off) * hd * 1.6)
            # Point shaft
            pygame.draw.line(surface, (220, 60, 255) if side == -1 else (255, 200, 0),
                             (hx, hy - hd), (px, py), max(2, int(3 * s)))
            # Bell at tip
            pygame.draw.circle(surface, (255, 220, 0), (px, py), max(3, int(5 * s)))
            pygame.draw.circle(surface, (180, 140, 0), (px, py), max(3, int(5 * s)), max(1, int(s)))
        # Collar ruff
        pygame.draw.circle(surface, (255, 60, 200), (hx, hy + hd), max(4, int(7 * s)), max(1, int(2 * s)))

    elif char_name == "Blitzer":
        # Lightning bolt on chest + goggles
        # Goggles (two circles with strap)
        for gside in (-1, 1):
            gx = hx + gside * int(hd * 0.45)
            pygame.draw.circle(surface, (255, 220, 0), (gx, hy), max(3, int(5 * s)))
            pygame.draw.circle(surface, (30, 20, 0),   (gx, hy), max(3, int(5 * s)), max(1, int(s)))
        pygame.draw.line(surface, (255, 200, 0),
                         (hx - int(hd * 0.45), hy), (hx + int(hd * 0.45), hy), max(1, int(s)))
        # Lightning bolt on chest
        bolt = [
            (sx + int(4 * s), sy - int(4 * s)),
            (sx,              sy + int(6 * s)),
            (sx + int(3 * s), sy + int(6 * s)),
            (sx - int(2 * s), sy + int(16 * s)),
            (sx + int(2 * s), sy + int(7 * s)),
            (sx - int(2 * s), sy + int(7 * s)),
        ]
        pygame.draw.polygon(surface, (255, 230, 0), bolt)

    elif char_name == "Vamp Lord":
        # Dramatic vampire cape
        cape_pts = [
            (hx,                     hy + hd),
            (hx - int(hd * 1.6),    wy + int(10 * s)),
            (hx - int(hd * 0.8),    wy - int(5 * s)),
            (hx + int(hd * 0.8),    wy - int(5 * s)),
            (hx + int(hd * 1.6),    wy + int(10 * s)),
        ]
        pygame.draw.polygon(surface, (80, 0, 30), cape_pts)
        pygame.draw.polygon(surface, (140, 0, 60), cape_pts, max(1, int(s)))
        # Fang showing from mouth
        fang_x = hx + int(facing * hd * 0.2)
        fang_y = hy + int(hd * 0.35)
        pygame.draw.polygon(surface, (240, 240, 255),
                            [(fang_x, fang_y),
                             (fang_x - max(1, int(2*s)), fang_y + int(6*s)),
                             (fang_x + max(1, int(2*s)), fang_y + int(6*s))])

    elif char_name == "Iron Fist":
        # Metal gauntlet on the punch fist
        gx, gy = int(rhx), int(rhy)   # right-hand position
        gr = max(5, int(9 * s))
        pygame.draw.circle(surface, (180, 190, 200), (gx, gy), gr)
        pygame.draw.circle(surface, (100, 110, 130), (gx, gy), gr, max(1, int(2 * s)))
        # Knuckle ridges
        for ki in range(3):
            kx = gx + int((ki - 1) * 4 * s)
            pygame.draw.circle(surface, (220, 220, 240), (kx, gy - max(1, int(3 * s))), max(1, int(2 * s)))

    elif char_name == "Toxic":
        # Gas mask with round visor
        mask_r = int(hd * 0.95)
        pygame.draw.circle(surface, (60, 80, 60), (hx, hy), mask_r)
        pygame.draw.circle(surface, (20, 40, 20), (hx, hy), mask_r, max(1, int(2 * s)))
        # Round visor lenses
        for side in (-1, 1):
            lx = hx + side * int(hd * 0.38)
            pygame.draw.circle(surface, (0, 200, 80), (lx, hy - int(hd * 0.1)), max(3, int(5 * s)))
            pygame.draw.circle(surface, (0, 100, 40), (lx, hy - int(hd * 0.1)), max(3, int(5 * s)), max(1, int(s)))
        # Circular filter at bottom
        pygame.draw.circle(surface, (40, 60, 40), (hx, hy + int(hd * 0.5)), max(3, int(5 * s)))
        pygame.draw.circle(surface, (20, 40, 20), (hx, hy + int(hd * 0.5)), max(3, int(5 * s)), max(1, int(s)))
        # Green gas puffs drifting upward
        t2 = pygame.time.get_ticks()
        for gi in range(3):
            ga = (t2 // 200 + gi * 7) % 20
            gpx = hx + (gi - 1) * int(8 * s)
            gpy = hy - hd - int(ga * 2 * s)
            if ga < 12:
                pygame.draw.circle(surface, (60, 220, 60, 120), (gpx, gpy), max(2, int((4 - ga//4) * s)))

    elif char_name == "Kamikaze":
        # Ticking bomb strapped to chest
        bx2, by2 = sx - int(6 * s), sy - int(8 * s)
        bsz2 = max(8, int(14 * s))
        t = pygame.time.get_ticks()
        blink = (t // 300) % 2 == 0
        pygame.draw.rect(surface, (220, 60, 20) if blink else (160, 40, 10),
                         (bx2, by2, bsz2, bsz2), border_radius=3)
        pygame.draw.rect(surface, (255, 200, 0), (bx2, by2, bsz2, bsz2), 1, border_radius=3)
        # Fuse spark
        if blink:
            pygame.draw.circle(surface, (255, 230, 0),
                               (bx2 + bsz2 // 2, by2 - max(2, int(3 * s))), max(2, int(3 * s)))

    elif char_name == "Shrink Ray":
        # Ray gun held out front
        gun_x = hx + int(facing * hd)
        gun_y = hy + int(hd * 0.2)
        gun_w = int(22 * s)
        gun_h = int(9 * s)
        pygame.draw.rect(surface, (60, 220, 180),
                         (gun_x, gun_y - gun_h // 2, int(facing) * gun_w, gun_h),
                         border_radius=3)
        pygame.draw.circle(surface, (120, 255, 210),
                           (gun_x + int(facing * gun_w), gun_y), max(3, int(5 * s)))

    elif char_name == "Levitator":
        # Upward-pointing glowing hands
        for hpos in [(lhx, lhy), (rhx, rhy)]:
            glow_r = max(5, int(8 * s))
            gsurf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (180, 140, 255, 100), (glow_r + 2, glow_r + 2), glow_r)
            surface.blit(gsurf, (int(hpos[0]) - glow_r - 2, int(hpos[1]) - glow_r - 2))
            pygame.draw.circle(surface, (220, 180, 255), (int(hpos[0]), int(hpos[1])),
                               max(3, int(5 * s)))

    elif char_name == "Stalker":
        # Dark hood pulled low, glowing red eyes
        hood_pts = [
            (hx - int(hd * 1.05), hy + int(hd * 0.2)),
            (hx,                   hy - hd - int(14 * s)),
            (hx + int(hd * 1.05), hy + int(hd * 0.2)),
        ]
        pygame.draw.polygon(surface, (20, 30, 20), hood_pts)
        pygame.draw.polygon(surface, (40, 60, 40), hood_pts, max(1, int(s)))
        for side in (-1, 1):
            pygame.draw.circle(surface, (200, 20, 20),
                               (hx + side * int(hd * 0.38), hy), max(2, int(3 * s)))

    elif char_name == "Mirror Man":
        # Shiny mirror shield on blocking arm side
        shx = hx + int(facing * hd * 1.4)
        shy = hy
        sh_r = max(8, int(14 * s))
        pygame.draw.circle(surface, (200, 220, 240), (shx, shy), sh_r)
        pygame.draw.circle(surface, (255, 255, 255), (shx, shy), sh_r, max(1, int(2 * s)))
        # Reflection glint
        pygame.draw.line(surface, (255, 255, 255),
                         (shx - int(4 * s), shy - int(6 * s)),
                         (shx + int(4 * s), shy + int(6 * s)), max(1, int(s)))

    elif char_name == "Pyro":
        # Flamethrower nozzle on the punch arm
        nozzle_x = rhx + int(facing * int(10 * s))
        nozzle_y = rhy
        pygame.draw.rect(surface, (80, 60, 40),
                         (nozzle_x - max(3, int(4 * s)), nozzle_y - max(3, int(4 * s)),
                          max(6, int(8 * s)) + int(facing * max(8, int(14 * s))),
                          max(6, int(8 * s))), border_radius=2)
        t = pygame.time.get_ticks()
        if (t // 150) % 2 == 0:
            pygame.draw.circle(surface, (255, 120, 0),
                               (nozzle_x + int(facing * max(10, int(16 * s))), nozzle_y),
                               max(3, int(5 * s)))

    elif char_name == "Thunder God":
        # Lightning crown of 5 bolts
        t = pygame.time.get_ticks()
        for ci in range(5):
            ca = math.radians(ci * 72 + t * 0.08)
            cx2 = hx + int(math.cos(ca) * hd * 1.4)
            cy2 = hy - hd - int(math.sin(ca) * hd * 0.6) - int(6 * s)
            pygame.draw.line(surface, (255, 240, 0),
                             (hx, hy - hd), (cx2, cy2), max(1, int(2 * s)))
            pygame.draw.circle(surface, (255, 255, 180), (cx2, cy2), max(2, int(3 * s)))

    elif char_name == "Glass Cannon":
        # Cannon barrel on shoulder
        c_x = sx + int(facing * int(8 * s))
        c_y = sy - int(8 * s)
        c_len = int(28 * s)
        pygame.draw.rect(surface, (180, 200, 220),
                         (c_x, c_y - max(3, int(5 * s)),
                          int(facing * c_len), max(6, int(10 * s))),
                         border_radius=2)
        pygame.draw.circle(surface, (140, 160, 180),
                           (c_x + int(facing * c_len), c_y), max(4, int(7 * s)))

    elif char_name == "Teleporter":
        # Swirling portal ring around body
        t = pygame.time.get_ticks()
        for pi in range(8):
            pa = math.radians(pi * 45 + t * 0.18)
            px2 = hx + int(math.cos(pa) * hd * 1.8)
            py2 = wy + int(math.sin(pa) * int(hd * 1.2))
            pygame.draw.circle(surface, (0, 200, 220), (px2, py2), max(2, int(3 * s)))

    elif char_name == "Sticker":
        # Glue dripping from fists
        for hpos in [(lhx, lhy), (rhx, rhy)]:
            drop_y = int(hpos[1]) + max(4, int(6 * s))
            pygame.draw.line(surface, (230, 200, 50),
                             (int(hpos[0]), int(hpos[1])),
                             (int(hpos[0]), drop_y), max(1, int(2 * s)))
            pygame.draw.circle(surface, (255, 220, 60),
                               (int(hpos[0]), drop_y), max(2, int(3 * s)))

    elif char_name == "Shifter":
        # Three spinning icons above the head showing the cycle
        t = pygame.time.get_ticks()
        icons = [("N", (200, 200, 200)), ("W", (200, 120, 20)), ("S", (80, 180, 255))]
        for ii, (ch2, ic) in enumerate(icons):
            ia = math.radians(ii * 120 + t * 0.12)
            ix = hx + int(math.cos(ia) * hd * 1.5)
            iy = hy - hd - int(hd * 0.8) + int(math.sin(ia) * hd * 0.5)
            ir = max(4, int(6 * s))
            pygame.draw.circle(surface, ic, (ix, iy), ir)
            lbl2 = font_tiny.render(ch2, True, (10, 10, 10))
            surface.blit(lbl2, (ix - lbl2.get_width() // 2, iy - lbl2.get_height() // 2))

    elif char_name == "Time Lord":
        # Hourglass held in hand + clock face on chest
        # Hourglass
        hgx, hgy = int(rhx), int(rhy)
        hg_h = int(12 * s)
        hg_w = int(6 * s)
        pygame.draw.polygon(surface, (220, 200, 140),
                            [(hgx - hg_w, hgy - hg_h), (hgx + hg_w, hgy - hg_h),
                             (hgx, hgy), (hgx + hg_w, hgy + hg_h), (hgx - hg_w, hgy + hg_h),
                             (hgx, hgy)])
        pygame.draw.circle(surface, (180, 150, 80), (hgx, hgy), max(2, int(3 * s)))
        # Clock face on chest
        cr = max(5, int(8 * s))
        pygame.draw.circle(surface, (220, 220, 240), (sx, sy), cr)
        pygame.draw.circle(surface, (80, 80, 120),   (sx, sy), cr, max(1, int(s)))
        t3 = pygame.time.get_ticks()
        hand_a = math.radians(t3 * 0.1 % 360)
        pygame.draw.line(surface, (40, 40, 80),
                         (sx, sy),
                         (sx + int(math.cos(hand_a) * (cr - 2)), sy + int(math.sin(hand_a) * (cr - 2))),
                         max(1, int(s)))

    elif char_name == "Sandman":
        # Droopy sleep cap + floating Zs
        brim_y = hy - hd
        tip_x  = hx + int(facing * hd * 0.4)
        tip_y  = hy - int(hd * 2.2)
        pygame.draw.polygon(surface, (200, 200, 230),
                            [(hx - hd, brim_y), (hx + hd, brim_y), (tip_x, tip_y)])
        pygame.draw.circle(surface, (220, 180, 240), (tip_x, tip_y), max(3, int(5*s)))
        tt = pygame.time.get_ticks()
        for zi, zo in enumerate((0, -10, -20)):
            if (tt // 500 + zi) % 2 == 0:
                zs = font_tiny.render("z", True, (160, 160, 255))
                surface.blit(zs, (hx + int(hd * 1.1), hy - hd - int((10 + zo) * s)))

    elif char_name == "Reaper":
        # Dark hood over head
        pygame.draw.polygon(surface, (25, 25, 25),
                            [(hx - hd - int(4*s), hy + int(2*s)),
                             (hx + hd + int(4*s), hy + int(2*s)),
                             (hx + int(hd*0.6), hy - hd - int(6*s)),
                             (hx - int(hd*0.6), hy - hd - int(6*s))])
        # Scythe handle
        spx = hx - int(facing * int(14*s))
        pygame.draw.line(surface, (90, 60, 30),
                         (spx, hy + int(10*s)), (spx - int(facing * int(4*s)), hy - int(hd*2.4)),
                         max(2, int(3*s)))
        # Scythe blade (arc approximated with a few lines)
        blade_cx = spx - int(facing * int(4*s))
        blade_cy = hy - int(hd * 2.4)
        for ba in range(0, 8):
            a1 = math.radians(ba * 22.5 + (0 if facing > 0 else 180))
            a2 = math.radians((ba+1) * 22.5 + (0 if facing > 0 else 180))
            br = int(hd * 0.9)
            pygame.draw.line(surface, (200, 200, 220),
                             (blade_cx + int(math.cos(a1)*br), blade_cy - int(math.sin(a1)*br)),
                             (blade_cx + int(math.cos(a2)*br), blade_cy - int(math.sin(a2)*br)),
                             max(2, int(2*s)))

    elif char_name == "Chainsaw Man":
        # Orange chainsaw on the forward arm
        cx2, cy2 = int(rhx + int(facing * int(4*s))), int(rhy)
        blen = int(20*s); bhalf = max(3, int(5*s))
        pygame.draw.rect(surface, (200, 60, 30),
                         (cx2, cy2 - bhalf, int(facing * blen), bhalf*2), border_radius=2)
        tt2 = pygame.time.get_ticks()
        for ti in range(5):
            tooth_x = cx2 + int(facing * int((ti + tt2//80 % 5) * blen // 5))
            pygame.draw.circle(surface, (255, 120, 0), (tooth_x, cy2 - bhalf), max(2, int(2*s)))

    elif char_name == "Crusher":
        # Big spiked knuckles on both fists
        for fhx2, fhy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (100, 50, 160), (fhx2, fhy2), max(5, int(8*s)))
            for si in range(4):
                sa = math.radians(si * 90)
                pygame.draw.circle(surface, (140, 80, 200),
                                   (fhx2 + int(math.cos(sa) * max(5, int(8*s))),
                                    fhy2 + int(math.sin(sa) * max(5, int(8*s)))),
                                   max(1, int(2*s)))

    elif char_name == "Storm Witch":
        # Tall pointed witch hat
        brim_y2 = hy - hd
        pygame.draw.polygon(surface, (40, 20, 80),
                            [(hx - int(hd*1.4), brim_y2), (hx + int(hd*1.4), brim_y2),
                             (hx, hy - int(hd*3.0))])
        pygame.draw.line(surface, (40, 20, 80),
                         (hx - int(hd*1.4), brim_y2), (hx + int(hd*1.4), brim_y2),
                         max(3, int(5*s)))
        pygame.draw.line(surface, (160, 80, 220),
                         (hx - int(hd*1.2), brim_y2 + int(2*s)),
                         (hx + int(hd*1.2), brim_y2 + int(2*s)),
                         max(1, int(2*s)))

    elif char_name == "Blood Baron":
        # Red vampire collar + fangs
        pygame.draw.polygon(surface, (150, 0, 30),
                            [(sx - int(hd*1.1), sy - int(6*s)), (sx + int(hd*1.1), sy - int(6*s)),
                             (sx + int(hd*0.7), sy + int(8*s)), (sx - int(hd*0.7), sy + int(8*s))])
        # Fangs below head
        for fx2 in (hx - int(hd*0.3), hx + int(hd*0.3)):
            pygame.draw.polygon(surface, (255, 230, 230),
                                [(fx2 - int(3*s), hy + int(hd*0.9)),
                                 (fx2 + int(3*s), hy + int(hd*0.9)),
                                 (fx2, hy + int(hd*1.4))])

    elif char_name == "Drifter":
        # Cool sunglasses
        g_y = hy - int(hd*0.1)
        for gx_off in (-int(hd*.4), int(hd*.4)):
            pygame.draw.ellipse(surface, (10, 10, 10),
                                (hx + gx_off - int(hd*.32), g_y - int(hd*.22),
                                 int(hd*.64), int(hd*.44)))
            pygame.draw.ellipse(surface, (60, 60, 60),
                                (hx + gx_off - int(hd*.32), g_y - int(hd*.22),
                                 int(hd*.64), int(hd*.44)), 1)
        pygame.draw.line(surface, (60, 60, 60),
                         (hx - int(hd*.08), g_y), (hx + int(hd*.08), g_y), max(1, int(s)))

    elif char_name == "Warlock":
        # Dark wizard hat + glowing orb in hand
        brim_y3 = hy - hd
        pygame.draw.polygon(surface, (40, 20, 100),
                            [(hx - int(hd*1.2), brim_y3), (hx + int(hd*1.2), brim_y3),
                             (hx, hy - int(hd*2.8))])
        pygame.draw.line(surface, (40, 20, 100),
                         (hx - int(hd*1.2), brim_y3), (hx + int(hd*1.2), brim_y3),
                         max(3, int(4*s)))
        # Orb at hand
        pygame.draw.circle(surface, (120, 60, 255), (rhx, rhy), max(4, int(7*s)))
        pygame.draw.circle(surface, (200, 160, 255), (rhx, rhy), max(4, int(7*s)), 1)

    elif char_name == "Flash":
        # Yellow lightning bolt on chest
        bx1 = sx + int(facing * int(2*s))
        pts_bolt = [(bx1, sy - int(8*s)), (bx1 - int(facing*int(5*s)), sy + int(2*s)),
                    (bx1 + int(facing*int(2*s)), sy + int(2*s)), (bx1 - int(facing*int(3*s)), sy + int(12*s))]
        if len(pts_bolt) >= 3:
            pygame.draw.polygon(surface, (255, 220, 0), pts_bolt)
            pygame.draw.polygon(surface, (200, 160, 0), pts_bolt, 1)

    elif char_name == "Portal Maker":
        # Glowing portal ring at hand
        tt3 = pygame.time.get_ticks()
        pr = max(6, int(9*s))
        for pi2 in range(12):
            pa2 = math.radians(pi2 * 30 + tt3 * 0.15)
            pcol = ((0, 180, 255) if pi2 % 2 == 0 else (255, 100, 0))
            pygame.draw.circle(surface, pcol,
                               (rhx + int(math.cos(pa2)*pr), rhy + int(math.sin(pa2)*pr)),
                               max(2, int(2*s)))

    elif char_name == "Gravity":
        # Red apple in hand
        ax2, ay2 = lhx, lhy - max(4, int(6*s))
        pygame.draw.circle(surface, (220, 40, 40), (ax2, ay2), max(4, int(7*s)))
        pygame.draw.line(surface, (60, 120, 20), (ax2, ay2 - max(4, int(6*s))),
                         (ax2 + int(3*s), ay2 - max(7, int(11*s))), max(1, int(2*s)))
        pygame.draw.ellipse(surface, (60, 180, 30),
                            (ax2, ay2 - max(7, int(11*s)), int(7*s), int(5*s)))

    elif char_name == "Swapper":
        # Double-sided swap arrows on chest
        for dx2, col2 in ((-int(hd*0.6), (255, 160, 60)), (int(hd*0.6), (60, 160, 255))):
            dir2 = 1 if dx2 > 0 else -1
            ax3, ay3 = sx + dx2, sy
            pts_arr = [(ax3, ay3 - int(4*s)), (ax3 + int(dir2*9*s), ay3 - int(4*s)),
                       (ax3 + int(dir2*9*s), ay3 - int(7*s)),
                       (ax3 + int(dir2*14*s), ay3),
                       (ax3 + int(dir2*9*s), ay3 + int(7*s)),
                       (ax3 + int(dir2*9*s), ay3 + int(4*s)),
                       (ax3, ay3 + int(4*s))]
            pygame.draw.polygon(surface, col2, pts_arr)

    elif char_name == "Bruiser":
        # Red headband + anger veins on forehead
        band_y2 = hy + int(hd * 0.1)
        pygame.draw.line(surface, (200, 0, 0), (hx - hd, band_y2), (hx + hd, band_y2),
                         max(3, int(5*s)))
        pygame.draw.line(surface, (255, 60, 60), (hx - int(hd*0.8), band_y2),
                         (hx + int(hd*0.8), band_y2), max(1, int(2*s)))
        # Vein marks
        for vx2 in (-int(hd*0.4), int(hd*0.2)):
            pygame.draw.line(surface, (200, 0, 0),
                             (hx + vx2, hy - int(hd*0.1)), (hx + vx2, hy - int(hd*0.5)),
                             max(1, int(s)))

    elif char_name == "Grappler":
        # Wrestling championship belt around waist + big padded gloves
        belt_y = wy + int(4*s)
        pygame.draw.rect(surface, (180, 140, 20),
                         (wx - int(hd*1.2), belt_y, int(hd*2.4), max(5, int(8*s))),
                         border_radius=2)
        pygame.draw.rect(surface, (220, 180, 40),
                         (wx - int(hd*0.4), belt_y - int(2*s), int(hd*0.8), max(6, int(10*s))),
                         border_radius=2)
        for ghx, ghy in ((lhx, lhy), (rhx, rhy)):
            pygame.draw.circle(surface, (50, 100, 180), (ghx, ghy), max(6, int(10*s)))
            pygame.draw.circle(surface, (80, 130, 210), (ghx, ghy), max(6, int(10*s)), 2)

    elif char_name == "Trickster":
        # Jester cap: two prongs with bells
        jrim_y = hy - hd
        pygame.draw.rect(surface, (180, 0, 180),
                         (hx - hd, jrim_y - int(4*s), hd*2, int(4*s)))
        for ji, (jdx, jcol) in enumerate(((-hd, (200, 0, 200)), (hd, (255, 200, 0)))):
            pygame.draw.line(surface, jcol,
                             (hx + jdx//2, jrim_y),
                             (hx + jdx + int(facing * ji * int(6*s)), jrim_y - int(hd*1.2)),
                             max(2, int(3*s)))
            pygame.draw.circle(surface, jcol,
                               (hx + jdx + int(facing * ji * int(6*s)), jrim_y - int(hd*1.2)),
                               max(3, int(5*s)))

    elif char_name == "Wildcard":
        # Playing card diamond on chest
        pts_dia = [(sx, sy - int(10*s)), (sx + int(7*s), sy),
                   (sx, sy + int(10*s)), (sx - int(7*s), sy)]
        pygame.draw.polygon(surface, (220, 40, 40), pts_dia)
        pygame.draw.polygon(surface, (255, 80, 80), pts_dia, 1)

    elif char_name == "Ironclad":
        # Iron bucket helmet with visor slit
        helm_y = hy - hd - int(4*s)
        hw2 = hd + int(3*s)
        hh2 = int(hd * 1.6)
        pygame.draw.rect(surface, (130, 140, 160), (hx - hw2, helm_y, hw2*2, hh2), border_radius=int(3*s))
        pygame.draw.rect(surface, (90, 100, 120), (hx - hw2, helm_y, hw2*2, hh2), 2, border_radius=int(3*s))
        # Visor slit
        vis_y = helm_y + int(hh2*0.45)
        pygame.draw.line(surface, (10, 10, 10),
                         (hx - hw2 + int(3*s), vis_y), (hx + hw2 - int(3*s), vis_y),
                         max(2, int(4*s)))
        # Rivets
        for rx2 in (hx - hw2 + int(4*s), hx + hw2 - int(4*s)):
            pygame.draw.circle(surface, (160, 170, 190), (rx2, helm_y + int(5*s)), max(2, int(3*s)))

    elif char_name == "Siphon":
        # Tubes running from each fist toward body center
        for fhx3, fhy3 in ((lhx, lhy), (rhx, rhy)):
            pygame.draw.line(surface, (140, 0, 140), (fhx3, fhy3), (sx, sy), max(1, int(2*s)))
            pygame.draw.circle(surface, (200, 40, 200), (fhx3, fhy3), max(3, int(5*s)))
        # Glowing core at chest
        pygame.draw.circle(surface, (200, 40, 200), (sx, sy), max(4, int(6*s)))
        pygame.draw.circle(surface, (255, 120, 255), (sx, sy), max(4, int(6*s)), 1)

    elif char_name == "Timekeeper":
        # Clock face on head
        cr2 = max(6, int(10*s))
        pygame.draw.circle(surface, (240, 240, 255), (hx, hy - int(hd*0.1)), cr2 + 2)
        pygame.draw.circle(surface, (80, 100, 140), (hx, hy - int(hd*0.1)), cr2 + 2, 2)
        tt4 = pygame.time.get_ticks()
        # Hour hand
        ha = math.radians(tt4 * 0.02 % 360 - 90)
        pygame.draw.line(surface, (30, 30, 60),
                         (hx, hy - int(hd*0.1)),
                         (hx + int(math.cos(ha) * (cr2 - 2)), hy - int(hd*0.1) + int(math.sin(ha) * (cr2 - 2))),
                         max(1, int(s)))
        # Minute hand
        ma = math.radians(tt4 * 0.1 % 360 - 90)
        pygame.draw.line(surface, (80, 80, 160),
                         (hx, hy - int(hd*0.1)),
                         (hx + int(math.cos(ma) * cr2), hy - int(hd*0.1) + int(math.sin(ma) * cr2)),
                         max(1, int(s)))

    elif char_name == "The One":
        # Rotating golden halo above head + orbiting sparks
        tt5 = pygame.time.get_ticks()
        halo_y = hy - hd - int(6*s)
        halo_r = int(hd * 1.1)
        for hi in range(12):
            ha2 = math.radians(hi * 30 + tt5 * 0.12)
            hcol2 = (255, int(200 + 55 * math.sin(ha2)), 0)
            pygame.draw.circle(surface, hcol2,
                               (hx + int(math.cos(ha2)*halo_r), halo_y + int(math.sin(ha2)*int(hd*0.25))),
                               max(2, int(3*s)))
        # White glow around body
        for oi in range(6):
            oa = math.radians(oi * 60 + tt5 * 0.07)
            pygame.draw.circle(surface, (255, 255, 200),
                               (wx + int(math.cos(oa)*int(hd*1.6)), wy + int(math.sin(oa)*int(hd*0.8))),
                               max(2, int(3*s)))

    elif char_name == "Mirror":
        # Oval mirror held in hand with gleam
        mx2, my2 = int(rhx + int(facing * int(8*s))), int(rhy)
        mr = max(7, int(12*s))
        pygame.draw.ellipse(surface, (200, 230, 255), (mx2 - mr, my2 - mr, mr*2, mr))
        pygame.draw.ellipse(surface, (255, 255, 255), (mx2 - mr, my2 - mr, mr*2, mr), 2)
        # Gleam line
        pygame.draw.line(surface, (255, 255, 255),
                         (mx2 - int(4*s), my2 - int(6*s)),
                         (mx2 + int(4*s), my2 + int(2*s)), max(1, int(s)))
        # Handle
        pygame.draw.line(surface, (160, 120, 60),
                         (mx2, my2), (mx2 - int(facing * int(8*s)), my2 + int(8*s)),
                         max(2, int(2*s)))

    elif char_name == "Paradox":
        # Infinity symbol above head
        tt6 = pygame.time.get_ticks()
        inf_y = hy - hd - int(6*s)
        inf_r = max(5, int(8*s))
        col_l = (int(100 + 100*math.sin(tt6*0.004)), 60, 200)
        col_r = (80, 40, int(150 + 100*math.cos(tt6*0.004)))
        pygame.draw.circle(surface, col_l, (hx - inf_r, inf_y), inf_r, max(2, int(2*s)))
        pygame.draw.circle(surface, col_r, (hx + inf_r, inf_y), inf_r, max(2, int(2*s)))
        # Crossing lines
        pygame.draw.line(surface, (120, 80, 255),
                         (hx - inf_r, inf_y), (hx + inf_r, inf_y), max(1, int(s)))

    elif char_name == "Rainbow Man":
        # Rainbow arc above head
        tt7 = pygame.time.get_ticks()
        arc_r = int(hd * 1.8)
        rainbow_cols = [(255,0,0),(255,140,0),(255,255,0),(0,200,0),(0,100,255),(140,0,255)]
        for ri, rc in enumerate(rainbow_cols):
            rr = arc_r - ri * max(2, int(3*s))
            if rr > 2:
                pygame.draw.arc(surface, rc,
                                (hx - rr, hy - hd - rr - int(4*s), rr*2, rr*2),
                                math.radians(0), math.radians(180), max(2, int(3*s)))
        # Rainbow sparkle dots orbiting body
        for si in range(6):
            sa2 = math.radians(si * 60 + tt7 * 0.15)
            sc2 = rainbow_cols[si]
            pygame.draw.circle(surface, sc2,
                               (wx + int(math.cos(sa2)*int(hd*1.4)), wy + int(math.sin(sa2)*int(hd*0.6))),
                               max(2, int(3*s)))

    elif char_name == "Spitting Cobra":
        # Snake eye (vertical slit pupil) on head + forked tongue
        eye_y = hy - int(hd * 0.15)
        # Yellow eye whites
        pygame.draw.ellipse(surface, (220, 200, 0),
                            (hx - int(hd*0.22), eye_y - int(hd*0.28), int(hd*0.44), int(hd*0.55)))
        # Black slit pupil
        pygame.draw.ellipse(surface, (0, 0, 0),
                            (hx - int(hd*0.08), eye_y - int(hd*0.22), int(hd*0.16), int(hd*0.44)))
        # Forked tongue
        tongue_base_x = hx + int(facing * hd)
        tongue_base_y = hy + int(hd * 0.6)
        tongue_tip_x  = tongue_base_x + int(facing * int(12*s))
        pygame.draw.line(surface, (220, 0, 0),
                         (tongue_base_x, tongue_base_y), (tongue_tip_x, tongue_base_y),
                         max(1, int(2*s)))
        # Fork tips
        pygame.draw.line(surface, (220, 0, 0),
                         (tongue_tip_x, tongue_base_y),
                         (tongue_tip_x + int(facing * int(4*s)), tongue_base_y - int(3*s)),
                         max(1, int(s)))
        pygame.draw.line(surface, (220, 0, 0),
                         (tongue_tip_x, tongue_base_y),
                         (tongue_tip_x + int(facing * int(4*s)), tongue_base_y + int(3*s)),
                         max(1, int(s)))

    elif char_name == "Jetpack":
        # Jetpack pack on back + thrust flames
        jp_x = hx - int(facing * int(12*s))
        jp_y = sy - int(4*s)
        jp_w = max(8, int(14*s))
        jp_h = max(14, int(22*s))
        pygame.draw.rect(surface, (140, 60, 200),
                         (jp_x - jp_w//2, jp_y, jp_w, jp_h), border_radius=3)
        pygame.draw.rect(surface, (180, 100, 255),
                         (jp_x - jp_w//2, jp_y, jp_w, jp_h), 2, border_radius=3)
        # Thrust nozzles
        for nox in (jp_x - jp_w//4, jp_x + jp_w//4):
            pygame.draw.rect(surface, (80, 40, 120),
                             (nox - int(3*s), jp_y + jp_h, int(6*s), int(4*s)))
        # Animated flames
        tt8 = pygame.time.get_ticks()
        for nox2 in (jp_x - jp_w//4, jp_x + jp_w//4):
            flame_h = max(6, int((8 + 4 * math.sin(tt8 * 0.02 + nox2)) * s))
            flame_col = (255, int(100 + 100 * ((tt8 // 80) % 2)), 0)
            pygame.draw.polygon(surface, flame_col,
                                [(nox2 - int(4*s), jp_y + jp_h + int(4*s)),
                                 (nox2 + int(4*s), jp_y + jp_h + int(4*s)),
                                 (nox2, jp_y + jp_h + int(4*s) + flame_h)])

    elif char_name == "The Impossible Victor":
        # Crown made of trophies (star + circle)
        trophy_y = hy - hd - int(4*s)
        for ti2, tx2 in enumerate((-int(hd*0.8), 0, int(hd*0.8))):
            tcy = trophy_y - (int(6*s) if ti2 == 1 else 0)
            pygame.draw.circle(surface, (0, 255, 180), (hx + tx2, tcy), max(3, int(5*s)))
            pygame.draw.circle(surface, (255, 255, 255), (hx + tx2, tcy), max(3, int(5*s)), 1)
        pygame.draw.line(surface, (0, 200, 140),
                         (hx - int(hd*0.9), trophy_y), (hx + int(hd*0.9), trophy_y),
                         max(2, int(3*s)))

    elif char_name == "Pacman":
        # Large yellow circle body with animated chomping mouth
        t_pac = pygame.time.get_ticks()
        mouth_angle = abs(math.sin(t_pac * 0.008)) * 35 + 5  # 5–40 degrees, oscillating
        body_r = max(hd + int(6*s), int(22*s))
        # Draw filled yellow body circle
        pygame.draw.circle(surface, (255, 220, 0) if not col == (255, 255, 255) else col,
                           (hx, hy), body_r)
        # Draw mouth wedge cutout (black)
        mouth_start = -mouth_angle if facing == 1 else 180 - mouth_angle
        mouth_end   =  mouth_angle if facing == 1 else 180 + mouth_angle
        pygame.draw.polygon(surface, (0, 0, 0), [
            (hx, hy),
            (hx + int(math.cos(math.radians(mouth_start)) * body_r),
             hy + int(math.sin(math.radians(mouth_start)) * body_r)),
            (hx + int(math.cos(math.radians(mouth_start / 2 + mouth_end / 2)) * body_r),
             hy + int(math.sin(math.radians(mouth_start / 2 + mouth_end / 2)) * body_r)),
            (hx + int(math.cos(math.radians(mouth_end)) * body_r),
             hy + int(math.sin(math.radians(mouth_end)) * body_r)),
        ])
        # Eye
        eye_x = hx + int(facing * int(hd*0.35))
        eye_y = hy - int(hd*0.5)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x, eye_y), max(2, int(3*s)))

    elif char_name == "ChickenBanana":
        # Glitches between a chicken visual and banana visual based on time
        t_cb = pygame.time.get_ticks()
        is_chicken = (t_cb // 500) % 2 == 0   # flips every 500ms
        if is_chicken:
            # Chicken: red comb on top of head, orange beak, white feather tufts
            comb_pts = [(hx - int(hd*0.3), hy - hd),
                        (hx - int(hd*0.1), hy - hd - int(8*s)),
                        (hx + int(hd*0.1), hy - hd),
                        (hx + int(hd*0.3), hy - hd - int(5*s)),
                        (hx + int(hd*0.5), hy - hd)]
            pygame.draw.polygon(surface, (220, 0, 0), comb_pts)
            # Beak
            beak_x = hx + int(facing * hd)
            pygame.draw.polygon(surface, (255, 140, 0), [
                (beak_x, hy - int(hd*0.1)),
                (beak_x + int(facing * int(8*s)), hy),
                (beak_x, hy + int(hd*0.1))])
            # Feather tufts at shoulders
            for side in (-1, 1):
                fx = sx + int(side * int(hd*0.9))
                pygame.draw.circle(surface, (240, 240, 240), (fx, sy), max(3, int(5*s)))
        else:
            # Banana: yellow curved shape arcing from head to waist
            ban_pts = []
            steps = 8
            for bi in range(steps + 1):
                t2 = bi / steps
                bx2 = hx + int(math.sin(t2 * math.pi) * int(hd*1.2) * facing)
                by2 = hy + int((wy - hy) * t2)
                ban_pts.append((bx2, by2))
            if len(ban_pts) >= 2:
                pygame.draw.lines(surface, (255, 220, 0), False, ban_pts, max(4, int(6*s)))
            # Banana tips
            pygame.draw.circle(surface, (200, 160, 0), (hx, hy), max(4, int(6*s)))
            pygame.draw.circle(surface, (200, 160, 0), (ban_pts[-1][0], ban_pts[-1][1]), max(3, int(5*s)))

    elif char_name == "Soul Master":
        # Purple soul aura around head + ink brush trail effect
        t_sm = pygame.time.get_ticks()
        for si2 in range(6):
            sa3 = math.radians(t_sm * 0.15 + si2 * 60)
            sr3 = hd + int(4*s) + int(math.sin(t_sm * 0.008 + si2) * 3*s)
            sc3 = (80 + (si2 * 20) % 100, 0, 160)
            pygame.draw.circle(surface, sc3,
                               (hx + int(math.cos(sa3)*sr3), hy + int(math.sin(sa3)*sr3)),
                               max(2, int(3*s)))
        # Soul wisp floating above head
        wisp_y = hy - hd - int((6 + 4*math.sin(t_sm*0.006))*s)
        pygame.draw.circle(surface, (180, 80, 255), (hx, wisp_y), max(3, int(5*s)))
        pygame.draw.circle(surface, (255, 200, 255), (hx, wisp_y), max(1, int(2*s)))

    elif char_name == "Scorpio":
        # Scorpion stinger tail arcing up from waist
        t_sc = pygame.time.get_ticks()
        tail_pts = [
            (wx, wy),
            (wx + facing * int(8*s), wy - int(18*s)),
            (wx + facing * int(18*s), wy - int(36*s)),
            (wx + facing * int(22*s), wy - int(52*s)),
            (wx + facing * int(18*s), wy - int(66*s)),
        ]
        pygame.draw.lines(surface, (130, 55, 5), False, tail_pts, max(2, int(3*s)))
        # Stinger tip
        stx, sty = tail_pts[-1]
        pygame.draw.polygon(surface, (200, 80, 10), [
            (stx, sty - int(8*s)), (stx - int(4*s), sty + int(4*s)), (stx + int(4*s), sty + int(4*s))
        ])
        # Claws at hands
        for (hndx, hndy) in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (140, 60, 10), (hndx, hndy), max(4, int(6*s)))
            pygame.draw.circle(surface, (200, 90, 20), (hndx, hndy), max(4, int(6*s)), max(1, int(2*s)))
            pygame.draw.line(surface, (140, 60, 10), (hndx, hndy),
                             (hndx + facing * int(6*s), hndy - int(4*s)), max(2, int(3*s)))
            pygame.draw.line(surface, (140, 60, 10), (hndx, hndy),
                             (hndx + facing * int(6*s), hndy + int(4*s)), max(2, int(3*s)))

    elif char_name == "Nuke":
        # Nuclear hazard circle on torso
        nuke_y = wy - int(bl * 0.45)
        nuke_r = max(8, int(11*s))
        pygame.draw.circle(surface, (30, 30, 30), (wx, nuke_y), nuke_r)
        pygame.draw.circle(surface, (240, 200, 0), (wx, nuke_y), nuke_r, max(2, int(3*s)))
        # Three hazard wedges
        for ang_off in (0, 120, 240):
            a1 = math.radians(ang_off + 30)
            a2 = math.radians(ang_off + 90)
            pts = [(wx, nuke_y),
                   (wx + int(math.cos(a1)*nuke_r*0.8), nuke_y + int(math.sin(a1)*nuke_r*0.8)),
                   (wx + int(math.cos(a2)*nuke_r*0.8), nuke_y + int(math.sin(a2)*nuke_r*0.8))]
            pygame.draw.polygon(surface, (240, 200, 0), pts)
        pygame.draw.circle(surface, (30, 30, 30), (wx, nuke_y), max(3, int(4*s)))
        # Fuse/spark on head
        fuse_x = hx + int(hd * 0.6)
        fuse_y = hy - hd
        pygame.draw.line(surface, (200, 160, 60), (fuse_x, fuse_y), (fuse_x + int(4*s), fuse_y - int(10*s)), max(2, int(2*s)))
        t_nk = pygame.time.get_ticks()
        if (t_nk // 120) % 2 == 0:
            pygame.draw.circle(surface, (255, 200, 0), (fuse_x + int(4*s), fuse_y - int(10*s)), max(2, int(3*s)))

    elif char_name == "Druid":
        # Leaf crown on head
        for li in range(5):
            la = math.radians(-80 + li * 40)
            lx = hx + int(math.cos(la) * hd)
            ly = hy - hd + int(math.sin(la) * hd)
            pygame.draw.ellipse(surface, (30, 160, 50),
                                (lx - int(5*s), ly - int(8*s), int(10*s), int(16*s)))
        # Wooden staff in leading hand
        staff_x = rhx + facing * int(4*s)
        pygame.draw.line(surface, (100, 65, 20), (staff_x, rhy - int(30*s)), (staff_x, rhy + int(25*s)), max(2, int(3*s)))
        pygame.draw.circle(surface, (60, 200, 80), (staff_x, rhy - int(30*s)), max(3, int(5*s)))

    elif char_name == "Big Bad Critter Clad":
        # Thick armored shell on torso — ridged carapace
        shell_w = int(24*s); shell_h = int(bl * 0.7)
        pygame.draw.rect(surface, (55, 35, 15), (wx - shell_w//2, sy, shell_w, shell_h), border_radius=max(3, int(4*s)))
        pygame.draw.rect(surface, (90, 60, 30), (wx - shell_w//2, sy, shell_w, shell_h), max(1, int(2*s)), border_radius=max(3, int(4*s)))
        # Ridge lines
        for ri in range(3):
            ry = sy + int((ri + 1) * shell_h // 4)
            pygame.draw.line(surface, (110, 75, 35), (wx - shell_w//2 + int(2*s), ry), (wx + shell_w//2 - int(2*s), ry), max(1, int(2*s)))
        # Horns / spikes on shoulders
        for side in (-1, 1):
            hk_x = sx + side * int(10*s)
            pygame.draw.polygon(surface, (70, 45, 20), [
                (hk_x - int(3*s), sy + int(2*s)),
                (hk_x + int(3*s), sy + int(2*s)),
                (hk_x, sy - int(10*s)),
            ])
        # Heavy brow ridges on head
        pygame.draw.arc(surface, (70, 45, 20), (hx - hd, hy - hd, hd*2, hd),
                        math.radians(0), math.radians(180), max(2, int(3*s)))

    elif char_name == "Dementor":
        # Dark flowing hood/cloak
        t_dm = pygame.time.get_ticks()
        # Hood
        hood_pts = [
            (hx - hd - int(2*s), hy),
            (hx - hd - int(6*s), hy - int(8*s)),
            (hx - int(4*s), hy - hd - int(12*s)),
            (hx + int(4*s), hy - hd - int(12*s)),
            (hx + hd + int(6*s), hy - int(8*s)),
            (hx + hd + int(2*s), hy),
        ]
        pygame.draw.polygon(surface, (15, 5, 30), hood_pts)
        pygame.draw.polygon(surface, (40, 20, 70), hood_pts, max(1, int(2*s)))
        # Wispy cloak trails at waist
        for wi in range(4):
            wt = t_dm * 0.004 + wi * 1.5
            wx2 = wx + int(math.sin(wt) * 6*s) + (wi - 2) * int(5*s)
            wbot = wy + int(bl * 0.5) + int(math.sin(wt + 1) * 4*s)
            pygame.draw.line(surface, (25, 10, 50),
                             (wx2, wy), (wx2, wbot), max(1, int(2*s)))
        # Glowing eyes in hood
        pygame.draw.circle(surface, (120, 0, 200), (hx - int(hd*0.3), hy - int(hd*0.1)), max(2, int(3*s)))
        pygame.draw.circle(surface, (120, 0, 200), (hx + int(hd*0.3), hy - int(hd*0.1)), max(2, int(3*s)))

    elif char_name == "Life the Universe Everything":
        # "42" stamped on the chest
        _f42 = _get_font(max(10, int(18*s)))
        _lbl = _f42.render("42", True, (0, 255, 255))
        surface.blit(_lbl, (wx - _lbl.get_width()//2, wy - _lbl.get_height()//2 - int(bl*0.3)))

    elif char_name == "Shade":
        # Wispy dark energy silhouette — thin dark aura lines
        t_sh = pygame.time.get_ticks()
        for wi in range(5):
            a = math.radians(wi * 72 + t_sh * 0.05)
            ex = hx + int(math.cos(a) * (hd + int(4*s)))
            ey = hy + int(math.sin(a) * (hd + int(4*s)))
            pygame.draw.line(surface, (60, 20, 100), (hx, hy), (ex, ey), max(1, int(2*s)))
        # Dark hood outline
        pygame.draw.circle(surface, (40, 10, 70), (hx, hy), hd + max(2, int(3*s)), max(1, int(2*s)))
        # Glowing purple eyes
        pygame.draw.circle(surface, (180, 0, 255), (hx - int(hd*0.3), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (180, 0, 255), (hx + int(hd*0.3), hy), max(2, int(3*s)))

    elif char_name == "Decay":
        # Rotting shoulder pads — dark brown splotches
        for side in (-1, 1):
            px = sx + side * int(7*s)
            pygame.draw.circle(surface, (50, 35, 10), (px, sy), max(5, int(7*s)))
            pygame.draw.circle(surface, (90, 60, 20), (px, sy), max(3, int(5*s)), max(1, int(2*s)))
        # Decay speckles on torso
        for di in range(5):
            dangle = math.radians(di * 60 + 10)
            dx = wx + int(math.cos(dangle) * int(6*s))
            dy = sy + int(bl * (0.2 + di * 0.14))
            pygame.draw.circle(surface, (60, 40, 10), (dx, dy), max(2, int(3*s)))
        # Cracked skull motif on head
        pygame.draw.arc(surface, (80, 55, 20), (hx - hd, hy - hd, hd*2, hd),
                        math.radians(20), math.radians(160), max(1, int(2*s)))

    elif char_name == "Fault Line":
        # Crack pattern on torso
        crack_pts = [(wx, sy + int(bl*0.1)), (wx - int(5*s), sy + int(bl*0.35)),
                     (wx + int(4*s), sy + int(bl*0.55)), (wx - int(3*s), sy + int(bl*0.8))]
        for i in range(len(crack_pts) - 1):
            pygame.draw.line(surface, (100, 65, 25), crack_pts[i], crack_pts[i+1], max(2, int(3*s)))
        # Rocky shoulder chunks
        for side in (-1, 1):
            rx = sx + side * int(8*s)
            pygame.draw.polygon(surface, (120, 80, 40), [
                (rx - int(4*s), sy),
                (rx + int(4*s), sy),
                (rx + int(2*s), sy - int(9*s)),
                (rx - int(2*s), sy - int(9*s)),
            ])
        # Stone brow ridge
        pygame.draw.line(surface, (100, 70, 35),
                         (hx - hd, hy - int(hd*0.2)), (hx + hd, hy - int(hd*0.2)),
                         max(2, int(3*s)))

    elif char_name == "Buckler":
        # Round shield on left hand
        shld_r = max(8, int(12*s))
        pygame.draw.circle(surface, (50, 130, 70), (lhx, lhy), shld_r)
        pygame.draw.circle(surface, (30, 90, 50),  (lhx, lhy), shld_r, max(2, int(3*s)))
        pygame.draw.line(surface, (30, 90, 50),
                         (lhx - shld_r + int(2*s), lhy), (lhx + shld_r - int(2*s), lhy),
                         max(1, int(2*s)))
        pygame.draw.line(surface, (30, 90, 50),
                         (lhx, lhy - shld_r + int(2*s)), (lhx, lhy + shld_r - int(2*s)),
                         max(1, int(2*s)))
        # Simple nasal helmet
        pygame.draw.rect(surface, (60, 140, 80),
                         (hx - hd, hy - hd, hd*2, hd), border_radius=max(2, int(3*s)))
        pygame.draw.line(surface, (40, 110, 60),
                         (hx, hy - hd), (hx, hy), max(2, int(3*s)))

    elif char_name == "Overdrive":
        # Orange energy rings around body
        t_od = pygame.time.get_ticks()
        for ri in range(3):
            angle_off = t_od * 0.003 + ri * 2.09
            rx = wx + int(math.cos(angle_off) * int(10*s))
            ry = sy + int(bl * 0.5) + int(math.sin(angle_off) * int(5*s))
            pygame.draw.circle(surface, (255, 160, 0), (rx, ry), max(3, int(4*s)))
        # Charge lightning bolt on chest
        bolt = [(wx, sy + int(bl*0.1)), (wx - int(4*s), sy + int(bl*0.45)),
                (wx + int(2*s), sy + int(bl*0.45)), (wx - int(4*s), sy + int(bl*0.85))]
        for i in range(len(bolt) - 1):
            pygame.draw.line(surface, (255, 200, 0), bolt[i], bolt[i+1], max(2, int(3*s)))

    elif char_name == "Revenant":
        # Ghostly purple aura wisps around body
        t_rv = pygame.time.get_ticks()
        for wi in range(4):
            a = math.radians(wi * 90 + t_rv * 0.04)
            rx = wx + int(math.cos(a) * int(12*s))
            ry = sy + int(bl * 0.5) + int(math.sin(a) * int(6*s))
            pygame.draw.circle(surface, (120, 40, 180), (rx, ry), max(3, int(4*s)))
        # Dark hollow eyes
        pygame.draw.circle(surface, (80, 0, 140), (hx - int(hd*0.3), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (80, 0, 140), (hx + int(hd*0.3), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (200, 100, 255), (hx - int(hd*0.3), hy), max(1, int(2*s)))
        pygame.draw.circle(surface, (200, 100, 255), (hx + int(hd*0.3), hy), max(1, int(2*s)))
        # Spectral collar
        pygame.draw.arc(surface, (140, 60, 200), (hx - hd, hy, hd*2, hd//2),
                        math.radians(0), math.radians(180), max(2, int(3*s)))

    elif char_name == "Volt":
        # Electric bolt on chest
        bolt = [(wx, sy + int(bl*0.08)), (wx - int(5*s), sy + int(bl*0.42)),
                (wx + int(3*s), sy + int(bl*0.42)), (wx - int(5*s), sy + int(bl*0.82))]
        for i in range(len(bolt) - 1):
            pygame.draw.line(surface, (220, 255, 40), bolt[i], bolt[i+1], max(2, int(3*s)))
        # Sparks on shoulders
        for side in (-1, 1):
            sx2 = sx + side * int(6*s)
            pygame.draw.circle(surface, (255, 255, 100), (sx2, sy), max(3, int(5*s)))
            pygame.draw.circle(surface, (180, 220, 0), (sx2, sy), max(3, int(5*s)), max(1, int(2*s)))
        # Electrical arcs on head
        pygame.draw.arc(surface, (200, 255, 60), (hx - hd, hy - hd, hd*2, hd),
                        math.radians(20), math.radians(160), max(2, int(3*s)))

    elif char_name == "Phantom Strike":
        # Dark blue cloak
        cloak_pts = [
            (hx - hd - int(3*s), hy + int(hd*0.5)),
            (hx - int(8*s), wy + int(bl*0.4)),
            (wx, wy + int(bl*0.55)),
            (hx + int(8*s), wy + int(bl*0.4)),
            (hx + hd + int(3*s), hy + int(hd*0.5)),
        ]
        pygame.draw.polygon(surface, (20, 20, 100), cloak_pts)
        pygame.draw.polygon(surface, (60, 60, 180), cloak_pts, max(1, int(2*s)))
        # Glowing blue eyes
        pygame.draw.circle(surface, (80, 80, 255), (hx - int(hd*0.3), hy - int(hd*0.1)), max(2, int(3*s)))
        pygame.draw.circle(surface, (80, 80, 255), (hx + int(hd*0.3), hy - int(hd*0.1)), max(2, int(3*s)))
        # Trailing shadow on left hand
        pygame.draw.circle(surface, (30, 30, 120), (lhx, lhy), max(4, int(6*s)), max(1, int(2*s)))

    elif char_name == "Trap Master":
        # Utility belt on waist
        pygame.draw.rect(surface, (80, 60, 20),
                         (wx - int(12*s), wy - int(4*s), int(24*s), int(7*s)))
        # Belt pouches
        for side in (-1, 1):
            px = wx + side * int(7*s)
            pygame.draw.rect(surface, (60, 45, 15),
                             (px - int(3*s), wy - int(4*s), int(6*s), int(7*s)))
        # Shovel/tool in right hand
        pygame.draw.line(surface, (90, 65, 25), (rhx, rhy), (rhx + facing * int(6*s), rhy - int(18*s)),
                         max(2, int(3*s)))
        pygame.draw.ellipse(surface, (70, 50, 20),
                            (rhx + facing * int(3*s) - int(4*s), rhy - int(22*s), int(8*s), int(6*s)))
        # Hardhat
        pygame.draw.arc(surface, (100, 75, 30), (hx - hd, hy - hd, hd*2, hd),
                        math.radians(0), math.radians(180), max(3, int(4*s)))
        pygame.draw.line(surface, (100, 75, 30),
                         (hx - hd - int(3*s), hy), (hx + hd + int(3*s), hy), max(2, int(3*s)))

    elif char_name == "Juggernaut":
        # Massive shoulder armor
        for side in (-1, 1):
            ax = sx + side * int(9*s)
            pygame.draw.rect(surface, (140, 50, 15),
                             (ax - int(7*s), sy - int(10*s), int(14*s), int(18*s)),
                             border_radius=max(2, int(3*s)))
            pygame.draw.rect(surface, (200, 80, 30),
                             (ax - int(7*s), sy - int(10*s), int(14*s), int(18*s)),
                             max(1, int(2*s)), border_radius=max(2, int(3*s)))
        # Thick chest plate
        pygame.draw.rect(surface, (160, 60, 20),
                         (wx - int(12*s), sy, int(24*s), bl),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (210, 90, 40),
                         (wx - int(12*s), sy, int(24*s), bl),
                         max(1, int(2*s)), border_radius=max(2, int(3*s)))
        # Horned visor helmet
        helmet_top = hy - hd - int(6*s)
        pygame.draw.polygon(surface, (150, 55, 15), [
            (hx - hd, hy), (hx - hd, helmet_top), (hx, helmet_top - int(6*s)),
            (hx + hd, helmet_top), (hx + hd, hy),
        ])
        for side in (-1, 1):
            pygame.draw.polygon(surface, (180, 70, 20), [
                (hx + side * hd, helmet_top),
                (hx + side * (hd + int(3*s)), helmet_top - int(12*s)),
                (hx + side * (hd - int(3*s)), helmet_top - int(6*s)),
            ])

    elif char_name == "Mirage":
        # Shimmering heat-haze robes — pale wavy lines
        t_mg = pygame.time.get_ticks()
        for ri in range(4):
            wave = math.sin(t_mg * 0.005 + ri * 1.1) * int(4*s)
            ry = sy + int(bl * (0.15 + ri * 0.23))
            pygame.draw.line(surface, (140, 200, 220),
                             (wx - int(10*s) + int(wave), ry),
                             (wx + int(10*s) + int(wave), ry),
                             max(1, int(2*s)))
        # Veil across lower face
        pygame.draw.arc(surface, (120, 190, 215),
                        (hx - hd + int(2*s), hy, hd*2 - int(4*s), hd - int(2*s)),
                        math.radians(0), math.radians(180), max(1, int(2*s)))
        # Glimmering eyes
        for ex, ey in [(hx - int(hd*0.3), hy - int(hd*0.1)), (hx + int(hd*0.3), hy - int(hd*0.1))]:
            pygame.draw.circle(surface, (200, 240, 255), (ex, ey), max(2, int(3*s)))
            pygame.draw.circle(surface, (100, 200, 230), (ex, ey), max(1, int(2*s)))

    elif char_name == "Hypnotist":
        # Top hat
        hat_w = int(hd * 1.6)
        hat_h = int(hd * 1.2)
        pygame.draw.rect(surface, (30, 10, 60),
                         (hx - hat_w//2, hy - hd - hat_h, hat_w, hat_h))
        pygame.draw.rect(surface, (60, 20, 100),
                         (hx - int(hat_w*0.7), hy - hd - max(2, int(3*s)), int(hat_w*1.4), max(3, int(5*s))))
        # Spiral eye pattern on face
        t_hy = pygame.time.get_ticks()
        for si in range(3):
            sr = max(2, int((si + 1) * 3 * s))
            pygame.draw.circle(surface, (200, 80, 255),
                               (hx, hy + int(hd*0.15)), sr, max(1, int(s)))
        # Swirling monocle hint
        pygame.draw.circle(surface, (220, 100, 255), (hx + int(hd*0.35), hy + int(hd*0.1)),
                           max(3, int(4*s)), max(1, int(2*s)))


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

    # ── ASCII fighter: render body as ASCII art text chars ────────────────────
    if char_name == "ASCII":
        _asc_col = WHITE if flash else col
        _af = pygame.font.SysFont("Courier", max(9, int(13 * s)), bold=True)
        def _achar(ch, cx, cy):
            _t = _af.render(ch, True, _asc_col)
            surface.blit(_t, (int(cx) - _t.get_width()//2, int(cy) - _t.get_height()//2))
        # Head
        _achar("O", head_c[0], head_c[1])
        # Torso
        for _i in range(1, 5):
            _ty = shoulder[1] + (waist[1] - shoulder[1]) * _i / 4
            _achar("|", shoulder[0], _ty)
        # Arms
        if action == 'punch':
            _achar("\\", la[0], la[1]); _achar("|", lh[0], lh[1])
            _achar("-",  ra[0], ra[1]); _achar(">", rh[0], rh[1])
        elif action == 'hurt':
            _achar("<", la[0], la[1]); _achar("*", lh[0], lh[1])
            _achar(">", ra[0], ra[1]); _achar("*", rh[0], rh[1])
        elif action == 'duck':
            _achar("-", la[0], la[1]); _achar("_", lh[0], lh[1])
            _achar("-", ra[0], ra[1]); _achar("_", rh[0], rh[1])
        else:
            _achar("/",  la[0], la[1]); _achar("|", lh[0], lh[1])
            _achar("\\", ra[0], ra[1]); _achar("|", rh[0], rh[1])
        # Legs
        if action == 'kick':
            _achar("/",  lk[0], lk[1]); _achar("|", lf[0], lf[1])
            _achar("=",  rk[0], rk[1]); _achar(">", rf[0] + facing * 5, rf[1])
        elif action == 'jump':
            _achar("/",  lk[0], lk[1]); _achar("/",  lf[0], lf[1])
            _achar("\\", rk[0], rk[1]); _achar("\\", rf[0], rf[1])
        elif action == 'duck':
            _achar("/",  lk[0], lk[1]); _achar("_", lf[0], lf[1])
            _achar("\\", rk[0], rk[1]); _achar("_", rf[0], rf[1])
        else:
            _achar("/",  lk[0], lk[1]); _achar("|", lf[0], lf[1])
            _achar("\\", rk[0], rk[1]); _achar("|", rf[0], rf[1])
        draw_costume(surface, char_name, head_c, hd, shoulder, waist, lh, rh, facing, s, col)
        if action == 'punch':
            return (int(ra[0] + facing * 10 * s), int(ra[1]))
        if action == 'kick':
            return (int(waist[0] + facing * int(action_t * 80 * s)), int(y - 20 * s))
        return None

    ln(waist, lk); ln(lk, lf)
    ln(waist, rk); ln(rk, rf)
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

    elif s == 10:  # Ice Cave
        surface.fill((40, 60, 100))
        # Background ice wall gradient
        for gy in range(HEIGHT):
            t = gy / HEIGHT
            r = int(40 + t * 30)
            g = int(60 + t * 50)
            b = int(100 + t * 60)
            pygame.draw.line(surface, (r, g, b), (0, gy), (WIDTH, gy))
        # Stalactites from ceiling
        for sx2, sw2, sh2 in [(50,30,80),(140,22,55),(240,28,70),(360,20,50),(460,32,90),
                               (570,24,60),(680,26,75),(790,20,45),(860,30,65)]:
            pygame.draw.polygon(surface, (160, 200, 240),
                [(sx2, 0),(sx2+sw2, 0),(sx2+sw2//2, sh2)])
            pygame.draw.polygon(surface, (200, 230, 255),
                [(sx2+4, 0),(sx2+8, 0),(sx2+6, sh2//2)])
        # Ice crystals on ground
        for cx2, ch2 in [(80,35),(180,25),(320,40),(500,30),(660,38),(800,28)]:
            pygame.draw.polygon(surface, (180, 220, 255),
                [(cx2-10, GROUND_Y+2),(cx2+10, GROUND_Y+2),(cx2, GROUND_Y+2-ch2)])
            pygame.draw.polygon(surface, (220, 240, 255),
                [(cx2-4, GROUND_Y+2),(cx2+4, GROUND_Y+2),(cx2, GROUND_Y+2-ch2//2)])
        # Icy ground
        pygame.draw.rect(surface, (100, 160, 210), (0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (140, 190, 235), (0, GROUND_Y+2, WIDTH, 10))
        pygame.draw.line(surface, (200, 230, 255), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)
        # Shiny reflections on ground
        for rx2 in range(60, WIDTH, 120):
            pygame.draw.line(surface, (220, 245, 255), (rx2, GROUND_Y+4), (rx2+50, GROUND_Y+4), 2)

    elif s == 11:  # Pirate Ship
        # Ocean sky
        surface.fill((80, 130, 190))
        # Clouds
        for cxc, cyc, cwr in [(100,60,80),(280,40,60),(550,70,90),(750,45,70)]:
            pygame.draw.ellipse(surface, (230,230,240),(cxc-cwr//2, cyc, cwr, 30))
            pygame.draw.ellipse(surface, (240,240,250),(cxc-cwr//3, cyc-12, cwr*2//3, 26))
        # Background sea
        pygame.draw.rect(surface, (30, 80, 140), (0, GROUND_Y-60, WIDTH, 62))
        # Waves
        for wx2 in range(0, WIDTH, 70):
            pygame.draw.arc(surface, (60, 120, 180),
                (wx2, GROUND_Y-65, 70, 30), 0, math.pi, 3)
        # Ship hull silhouette in background
        hull_pts = [(50,GROUND_Y+2),(120,GROUND_Y-55),(780,GROUND_Y-55),(850,GROUND_Y+2)]
        pygame.draw.polygon(surface, (60, 35, 10), hull_pts)
        pygame.draw.polygon(surface, (90, 55, 20), hull_pts, 3)
        # Mast
        mx = WIDTH//2
        pygame.draw.line(surface, (80, 50, 15), (mx, GROUND_Y-55), (mx, GROUND_Y-280), 8)
        pygame.draw.line(surface, (80, 50, 15), (mx-2, GROUND_Y-55), (mx-2, GROUND_Y-280), 3)
        # Sail
        sail_pts = [(mx+4, GROUND_Y-260),(mx+4, GROUND_Y-130),(mx+130, GROUND_Y-160),(mx+120, GROUND_Y-240)]
        pygame.draw.polygon(surface, (240, 235, 210), sail_pts)
        pygame.draw.polygon(surface, (200, 195, 170), sail_pts, 2)
        # Crow's nest
        pygame.draw.rect(surface, (80, 50, 15), (mx-20, GROUND_Y-290, 40, 18))
        # Wooden deck
        pygame.draw.rect(surface, (100, 65, 25), (0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        for plank_x in range(0, WIDTH, 40):
            pygame.draw.line(surface, (80, 50, 15), (plank_x, GROUND_Y+2), (plank_x, HEIGHT), 2)
        pygame.draw.line(surface, (140, 90, 35), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)
        # Skull-and-crossbones flag
        pygame.draw.circle(surface, WHITE, (mx, GROUND_Y-265), 9)
        pygame.draw.line(surface, WHITE, (mx-7, GROUND_Y-258), (mx+7, GROUND_Y-274), 2)
        pygame.draw.line(surface, WHITE, (mx+7, GROUND_Y-258), (mx-7, GROUND_Y-274), 2)

    elif s == 12:  # City Rooftop
        surface.fill((8, 8, 25))
        # Stars
        for sx3, sy3 in [(50,30),(120,15),(200,45),(340,20),(480,35),(600,10),(720,40),(840,25),(90,70),(400,55),(650,65)]:
            pygame.draw.circle(surface, (255,255,220),(sx3,sy3), random.randint(1,2))
        # Moon
        pygame.draw.circle(surface, (240,240,200),(760,55),32)
        pygame.draw.circle(surface, (8,8,25),(775,48),26)
        # Building silhouettes
        for bx2, bw2, bh2 in [(0,90,200),(85,70,260),(150,80,180),(230,60,300),(290,100,220),
                                (480,70,250),(550,90,190),(640,80,270),(720,100,210),(820,80,240)]:
            pygame.draw.rect(surface, (20,20,40),(bx2, GROUND_Y-bh2, bw2, bh2))
            # Windows
            for wy2 in range(GROUND_Y-bh2+15, GROUND_Y-20, 25):
                for wx3 in range(bx2+8, bx2+bw2-8, 18):
                    wc = (255,230,100) if random.random()>0.35 else (30,30,50)
                    pygame.draw.rect(surface, wc, (wx3, wy2, 10, 14))
        # Neon signs
        for nx2, ny2, nt, nc in [(160,GROUND_Y-70,"BAR",(255,40,80)),
                                   (480,GROUND_Y-90,"DINER",(80,200,255)),
                                   (700,GROUND_Y-60,"CLUB",(200,80,255))]:
            ns = font_tiny.render(nt, True, nc)
            surface.blit(ns, (nx2, ny2))
            pygame.draw.rect(surface, nc, (nx2-2, ny2-2, ns.get_width()+4, ns.get_height()+4), 1)
        # Rooftop floor (gravel)
        pygame.draw.rect(surface, (55,55,60),(0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (70,70,75),(0, GROUND_Y+2, WIDTH, 8))
        pygame.draw.line(surface, (100,100,110),(0, GROUND_Y+2),(WIDTH, GROUND_Y+2), 3)
        # AC units
        for ax2 in [120, 380, 650, 820]:
            pygame.draw.rect(surface, (70,70,80),(ax2, GROUND_Y-22, 38, 22))
            pygame.draw.rect(surface, (90,90,100),(ax2, GROUND_Y-22, 38, 22), 2)

    elif s == 13:  # Medieval Castle
        surface.fill((30, 25, 20))
        # Stone wall background — grid of blocks
        for gy2 in range(0, GROUND_Y, 36):
            offset = 18 if (gy2 // 36) % 2 == 0 else 0
            for gx2 in range(-offset, WIDTH+36, 72):
                pygame.draw.rect(surface, (55,50,45),(gx2+1, gy2+1, 70, 34), border_radius=2)
                pygame.draw.rect(surface, (65,60,55),(gx2+1, gy2+1, 70, 34), 1, border_radius=2)
        # Battlements at the top
        for bx2 in range(0, WIDTH, 50):
            pygame.draw.rect(surface, (70,65,58),(bx2, 0, 30, 40))
        # Torches
        for tx2 in [140, 380, 620, 820]:
            pygame.draw.rect(surface, (100,60,20),(tx2-3, GROUND_Y-100, 6, 40))
            pygame.draw.circle(surface, (255,160,0),(tx2, GROUND_Y-102), 9)
            pygame.draw.circle(surface, (255,220,80),(tx2, GROUND_Y-104), 5)
            pygame.draw.circle(surface, (255,255,180),(tx2, GROUND_Y-106), 2)
            # Glow
            gsurf = pygame.Surface((60,60), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (255,140,0,40),(30,30),28)
            surface.blit(gsurf,(tx2-30, GROUND_Y-130))
        # Red banners
        for bx2 in [80, 430, 780]:
            pygame.draw.rect(surface, (160,20,20),(bx2-8, 40, 16, 70))
            pygame.draw.polygon(surface, (160,20,20),
                [(bx2-8,110),(bx2+8,110),(bx2, 130)])
        # Stone floor
        pygame.draw.rect(surface, (60,55,50),(0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        for fx2 in range(0, WIDTH, 80):
            pygame.draw.line(surface, (50,45,40),(fx2, GROUND_Y+2),(fx2, HEIGHT), 2)
        pygame.draw.line(surface, (90,82,72),(0, GROUND_Y+2),(WIDTH, GROUND_Y+2), 3)

    elif s == 14:  # Circus
        surface.fill((10, 5, 20))
        # Big top tent stripes (alternating red/white/yellow from top)
        stripe_w = WIDTH // 10
        stripe_cols = [(210,30,30),(240,240,240),(220,180,0),(210,30,30),(240,240,240),
                       (220,180,0),(210,30,30),(240,240,240),(220,180,0),(210,30,30)]
        for i, sc in enumerate(stripe_cols):
            pygame.draw.rect(surface, sc, (i*stripe_w, 0, stripe_w, GROUND_Y+2))
        # Dark overlay for depth
        ov2 = pygame.Surface((WIDTH, GROUND_Y+2), pygame.SRCALPHA)
        ov2.fill((0,0,0,110))
        surface.blit(ov2,(0,0))
        # Tent border outline
        pygame.draw.line(surface,(255,255,200),(0,0),(WIDTH,0),4)
        # Spotlight cones from top corners
        for sp_x in [0, WIDTH]:
            sp_pts = [(sp_x, 0),(sp_x + (300 if sp_x==0 else -300), 0),
                      (WIDTH//2 + (100 if sp_x==0 else -100), GROUND_Y)]
            sp_surf = pygame.Surface((WIDTH, GROUND_Y+2), pygame.SRCALPHA)
            pygame.draw.polygon(sp_surf,(255,255,180,18), sp_pts)
            surface.blit(sp_surf,(0,0))
        # Sparkles
        for px2, py2 in [(80,50),(200,30),(400,20),(600,35),(780,25),(140,80),(660,70)]:
            pygame.draw.line(surface,(255,230,0),(px2-5,py2),(px2+5,py2),2)
            pygame.draw.line(surface,(255,230,0),(px2,py2-5),(px2,py2+5),2)
        # Sawdust ground
        pygame.draw.rect(surface,(180,130,60),(0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface,(200,155,80),(0, GROUND_Y+2, WIDTH, 10))
        pygame.draw.line(surface,(220,175,100),(0, GROUND_Y+2),(WIDTH, GROUND_Y+2),3)

    elif s == 15:  # The Void
        # Deep black abyss
        surface.fill((5, 0, 15))
        # Starfield / void particles
        for vx2, vy2, vr in [
            (60,40,2),(150,80,1),(230,30,2),(380,60,1),(500,45,2),(620,25,1),
            (740,70,2),(830,35,1),(90,120,1),(300,100,2),(470,130,1),(680,110,2),
            (800,90,1),(180,160,2),(420,150,1),(560,170,2),(720,140,1),(50,200,1),
        ]:
            pygame.draw.circle(surface, (180,160,255), (vx2, vy2), vr)
        # Void tendrils drifting up from below
        for tx2, offset in [(80,0),(220,15),(370,5),(530,20),(680,8),(820,12)]:
            for i in range(6):
                ty1 = HEIGHT - i * 55
                ty2 = ty1 - 50
                pygame.draw.line(surface, (40,0,80),
                    (tx2 + int(math.sin(i * 0.7 + offset) * 18), ty1),
                    (tx2 + int(math.sin((i+1) * 0.7 + offset) * 18), ty2), 3)
        # Eerie purple glow at the bottom
        glow = pygame.Surface((WIDTH, 160), pygame.SRCALPHA)
        for gi in range(80):
            alpha = int(80 * (1 - gi / 80))
            pygame.draw.line(glow, (80, 0, 140, alpha), (0, 160-gi), (WIDTH, 160-gi))
        surface.blit(glow, (0, HEIGHT - 160))
        # Floating platform islands have a glowing underside — drawn after platforms in game loop
        # (the background just sets up the void atmosphere)

    elif s == 16:  # Underwater
        # Deep sea gradient
        for gy2 in range(HEIGHT):
            t = gy2 / HEIGHT
            r = int(0  + t * 10)
            g = int(30 + t * 60)
            b = int(80 + t * 80)
            pygame.draw.line(surface, (r, g, b), (0, gy2), (WIDTH, gy2))
        # Light rays from surface
        for lx2 in range(50, WIDTH, 130):
            ray_pts = [(lx2-20,0),(lx2+20,0),(lx2+50, GROUND_Y),(lx2-50, GROUND_Y)]
            rs = pygame.Surface((WIDTH, GROUND_Y+2), pygame.SRCALPHA)
            pygame.draw.polygon(rs,(180,220,255,15), ray_pts)
            surface.blit(rs,(0,0))
        # Bubbles rising (static pattern)
        for bx2, by2, br2 in [(80,300,4),(200,200,3),(330,350,5),(460,150,3),
                               (580,280,4),(700,180,3),(820,320,4),(130,100,2),(650,380,3)]:
            pygame.draw.circle(surface,(160,220,255,0),(bx2,by2),br2,1)
            pygame.draw.circle(surface,(160,220,255),(bx2,by2),br2,1)
        # Coral at ground
        for cx2, cc in [(80,(255,80,80)),(160,(255,120,60)),(280,(220,60,120)),
                         (420,(255,80,80)),(540,(200,80,200)),(660,(255,100,60)),
                         (760,(220,70,120)),(840,(255,80,80))]:
            for branch in range(-2,3):
                bh2 = random.randint(20,50)
                pygame.draw.line(surface, cc,
                    (cx2+branch*8, GROUND_Y+2),
                    (cx2+branch*6, GROUND_Y+2-bh2), 4)
                pygame.draw.circle(surface, cc, (cx2+branch*6, GROUND_Y+2-bh2), 5)
        # Seaweed
        for wx2 in [130, 320, 500, 720, 860]:
            for seg2 in range(8):
                sy2_1 = GROUND_Y + 2 - seg2 * 16
                sy2_2 = sy2_1 - 14
                pygame.draw.line(surface,(40,160,60),
                    (wx2 + int(math.sin(seg2*0.8)*8), sy2_1),
                    (wx2 + int(math.sin((seg2+1)*0.8)*8), sy2_2), 4)
        # Sandy seafloor
        pygame.draw.rect(surface,(140,120,60),(0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface,(160,140,80),(0, GROUND_Y+2, WIDTH, 8))
        pygame.draw.line(surface,(180,160,100),(0, GROUND_Y+2),(WIDTH, GROUND_Y+2), 3)
        # Fish silhouettes in background
        for fx2, fy2, ff in [(200,180,1),(500,120,-1),(750,220,1),(350,300,-1)]:
            pygame.draw.ellipse(surface,(20,80,120),(fx2,fy2,24,12))
            pygame.draw.polygon(surface,(20,80,120),
                [(fx2-ff*12,fy2+6),(fx2-ff*22,fy2+2),(fx2-ff*22,fy2+10)])

    elif s == 17:  # Arctic Tundra
        # Sky gradient: pale blue top to white horizon
        for gy2 in range(HEIGHT):
            t = gy2 / HEIGHT
            r = int(180 + t * 55)
            g = int(210 + t * 35)
            b = int(240 + t * 10)
            pygame.draw.line(surface, (min(r,255), min(g,255), min(b,255)), (0, gy2), (WIDTH, gy2))
        # Distant snow hills
        for hx, hw, hh, hc in [(0,320,90,(230,240,250)),(260,300,75,(220,232,244)),(520,340,85,(235,244,252))]:
            pygame.draw.ellipse(surface, hc, (hx, GROUND_Y-hh+20, hw, hh*2))
        # Snow ground
        pygame.draw.rect(surface, (240, 248, 255), (0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface, (210, 228, 245), (0, GROUND_Y+2, WIDTH, 10))
        pygame.draw.line(surface, (255,255,255), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)
        # Blizzard snowflakes
        for bx2, by2, bs2 in [(40,80,3),(120,200,2),(200,140,4),(310,60,2),(420,180,3),
                               (540,100,4),(650,240,2),(760,70,3),(840,190,2),(110,310,3),
                               (340,280,2),(590,330,3),(720,150,2),(80,380,4),(500,360,3)]:
            pygame.draw.circle(surface, (255,255,255), (bx2, by2), bs2)
            pygame.draw.line(surface,(220,230,255),(bx2-bs2-2,by2),(bx2+bs2+2,by2),1)
            pygame.draw.line(surface,(220,230,255),(bx2,by2-bs2-2),(bx2,by2+bs2+2),1)
        # Ice formations at ground
        for ix in [60,180,320,480,640,800]:
            pts = [(ix,GROUND_Y+2),(ix-14,GROUND_Y-38),(ix,GROUND_Y-22),(ix+14,GROUND_Y-38)]
            pygame.draw.polygon(surface,(180,220,255),pts)
            pygame.draw.polygon(surface,(220,240,255),pts,2)

    elif s == 18:  # Haunted House
        # Dark purple-blue night sky
        for gy2 in range(HEIGHT):
            t = gy2 / HEIGHT
            r = int(20 + t * 25)
            g = int(10 + t * 20)
            b = int(40 + t * 30)
            pygame.draw.line(surface, (r, g, b), (0, gy2), (WIDTH, gy2))
        # Full moon
        pygame.draw.circle(surface, (200, 200, 160), (720, 80), 42)
        pygame.draw.circle(surface, (230, 230, 190), (720, 80), 38)
        # Moon glow
        gsurf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(gsurf, (200,200,150,25),(60,60),60)
        surface.blit(gsurf, (660, 20))
        # Haunted house silhouette
        house_pts = [(50,GROUND_Y+2),(50,GROUND_Y-120),(120,GROUND_Y-120),(120,GROUND_Y-180),
                     (155,GROUND_Y-200),(190,GROUND_Y-180),(190,GROUND_Y-120),(250,GROUND_Y-120),
                     (250,GROUND_Y+2)]
        pygame.draw.polygon(surface,(30,20,40),house_pts)
        # Windows glowing yellow
        for wx2, wy2 in [(80,GROUND_Y-105),(155,GROUND_Y-115),(80,GROUND_Y-60),(210,GROUND_Y-60)]:
            pygame.draw.rect(surface,(180,140,20),(wx2,wy2,22,18),border_radius=2)
            pygame.draw.rect(surface,(220,180,60),(wx2+3,wy2+3,16,12),border_radius=1)
        # Bare trees
        for tx2 in [310, 590, 740]:
            pygame.draw.line(surface,(40,30,30),(tx2,GROUND_Y+2),(tx2,GROUND_Y-90),4)
            for ang2 in [-50,-30,30,50]:
                blen = random.randint(30,50)
                ex2 = tx2 + int(math.cos(math.radians(ang2))*blen)
                ey2 = (GROUND_Y-90) + int(math.sin(math.radians(ang2-90))*blen)
                pygame.draw.line(surface,(40,30,30),(tx2,GROUND_Y-60),(ex2,ey2),2)
        # Stars
        for sx3,sy3 in [(100,40),(200,20),(400,55),(550,30),(650,15),(800,45),(860,25)]:
            pygame.draw.circle(surface,(220,220,200),(sx3,sy3),2)
        # Dark ground
        pygame.draw.rect(surface,(30,25,35),(0,GROUND_Y+2,WIDTH,HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface,(45,35,50),(0,GROUND_Y+2,WIDTH,8))
        pygame.draw.line(surface,(60,50,65),(0,GROUND_Y+2),(WIDTH,GROUND_Y+2),2)
        # Gravestones
        for gx3 in [400,480,560,640]:
            pygame.draw.rect(surface,(60,55,65),(gx3,GROUND_Y-28,20,26),border_radius=5)
            pygame.draw.rect(surface,(80,75,85),(gx3,GROUND_Y-28,20,26),2,border_radius=5)

    elif s == 19:  # Volcano Core
        # Deep red-orange gradient
        for gy2 in range(HEIGHT):
            t = gy2 / HEIGHT
            r = int(80 + t * 80)
            g = int(10 + t * 30)
            b = int(5 + t * 10)
            pygame.draw.line(surface, (min(r,255), min(g,255), min(b,255)), (0, gy2), (WIDTH, gy2))
        # Glowing lava cracks in walls
        for cx3, cy3_list in [(0,[(80,150),(160,260),(220,360)]),
                               (WIDTH,[(70,120),(180,240),(240,380)])]:
            for cy3a, cy3b in cy3_list:
                lx3 = cx3 + (random.randint(10,50) if cx3==0 else -random.randint(10,50))
                pygame.draw.line(surface,(255,120,0),(cx3,cy3a),(lx3,(cy3a+cy3b)//2),3)
                pygame.draw.line(surface,(255,60,0),(lx3,(cy3a+cy3b)//2),(cx3,cy3b),3)
                pygame.draw.line(surface,(255,200,50),(cx3,cy3a),(lx3,(cy3a+cy3b)//2),1)
        # Lava pools at edges
        for lx3, lw3 in [(0,180),(WIDTH-180,180)]:
            pygame.draw.rect(surface,(200,60,0),(lx3,GROUND_Y+2,lw3,HEIGHT-GROUND_Y-2))
            pygame.draw.rect(surface,(255,120,0),(lx3,GROUND_Y+2,lw3,12))
            pygame.draw.line(surface,(255,180,0),(lx3,GROUND_Y+2),(lx3+lw3,GROUND_Y+2),3)
        # Center ground
        pygame.draw.rect(surface,(60,30,10),(180,GROUND_Y+2,WIDTH-360,HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface,(90,50,20),(180,GROUND_Y+2,WIDTH-360,8))
        # Lava drips from ceiling
        for dx3 in [80,200,380,550,700,860]:
            dh3 = random.randint(20,60)
            pygame.draw.line(surface,(200,60,0),(dx3,0),(dx3,dh3),4)
            pygame.draw.circle(surface,(255,120,0),(dx3,dh3),5)
        # Heat shimmer lines
        for hx3 in range(50,WIDTH,80):
            pygame.draw.line(surface,(200,80,0),(hx3,GROUND_Y-100),(hx3+10,GROUND_Y-40),1)

    elif s == 20:  # Sky Island
        # Bright sky gradient
        for gy2 in range(GROUND_Y+2):
            t = gy2 / (GROUND_Y+2)
            r = int(50 + t * 130)
            g = int(130 + t * 100)
            b = int(230 - t * 30)
            pygame.draw.line(surface, (r, g, b), (0, gy2), (WIDTH, gy2))
        pygame.draw.rect(surface,(120,90,60),(0,GROUND_Y+2,WIDTH,HEIGHT-GROUND_Y-2))
        # Sun
        pygame.draw.circle(surface,(255,240,100),(820,60),36)
        pygame.draw.circle(surface,(255,255,160),(820,60),28)
        # Sun rays
        for ra in range(0,360,30):
            rx1 = 820 + int(math.cos(math.radians(ra))*40)
            ry1 =  60 + int(math.sin(math.radians(ra))*40)
            rx2 = 820 + int(math.cos(math.radians(ra))*54)
            ry2 =  60 + int(math.sin(math.radians(ra))*54)
            pygame.draw.line(surface,(255,220,80),(rx1,ry1),(rx2,ry2),2)
        # Clouds (fluffy, below ground level too)
        for cxc, cyc, cw in [(60,GROUND_Y+30,180),(300,GROUND_Y+60,220),(580,GROUND_Y+20,200),(800,GROUND_Y+50,160)]:
            for cdx, cdy, cr in [(0,0,30),(35,-10,24),(-35,-8,22),(60,5,20),(-60,5,18)]:
                pygame.draw.circle(surface,(255,255,255),(cxc+cdx,cyc+cdy),cr)
        # A few background clouds in sky
        for cxc, cyc, cw in [(150,120,160),(500,80,200),(750,140,150)]:
            for cdx, cdy, cr in [(0,0,22),(28,-8,18),(-28,-6,16)]:
                pygame.draw.circle(surface,(230,240,255),(cxc+cdx,cyc+cdy),cr)
        # Floating rock islands (decorative, small)
        for rxc, ryc, rw in [(130,GROUND_Y+5,90),(450,GROUND_Y+15,110),(750,GROUND_Y+5,80)]:
            pygame.draw.ellipse(surface,(100,80,50),(rxc,ryc,rw,22))
            pygame.draw.ellipse(surface,(130,105,70),(rxc,ryc,rw,10))
        # Ground (floating rock)
        pygame.draw.rect(surface,(110,90,55),(0,GROUND_Y+2,WIDTH,HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface,(140,115,70),(0,GROUND_Y+2,WIDTH,10))
        pygame.draw.line(surface,(170,140,90),(0,GROUND_Y+2),(WIDTH,GROUND_Y+2),3)
        # Grass tufts on ground
        for gxt in range(40,WIDTH,60):
            pygame.draw.line(surface,(60,160,40),(gxt,GROUND_Y+2),(gxt-5,GROUND_Y-8),2)
            pygame.draw.line(surface,(60,160,40),(gxt,GROUND_Y+2),(gxt+5,GROUND_Y-10),2)

    elif s == 22:  # Under the Void
        surface.fill((5, 0, 20))
        # Rocky ceiling stalactites
        for rx, rh in [(0,55),(80,70),(170,42),(275,65),(390,50),(505,72),(615,48),(715,62),(820,55)]:
            pygame.draw.polygon(surface, (35, 20, 55), [(rx, 0), (rx+80, 0), (rx+40, rh)])
            pygame.draw.polygon(surface, (55, 35, 80), [(rx, 0), (rx+80, 0), (rx+40, rh)], 2)
        # Void glow bleeding through ceiling
        gsurf = pygame.Surface((WIDTH, 90), pygame.SRCALPHA)
        for gi in range(80):
            a = int(110 * (1 - gi / 80))
            pygame.draw.line(gsurf, (130, 0, 230, a), (0, gi), (WIDTH, gi))
        surface.blit(gsurf, (0, 0))
        # Ceiling death-zone line
        pygame.draw.line(surface, (200, 0, 255), (0, 3), (WIDTH, 3), 3)
        # Totem pole background (centred)
        tp = WIDTH // 2
        pygame.draw.rect(surface, (80, 50, 18), (tp - 17, GROUND_Y - 310, 34, 312))
        pygame.draw.rect(surface, (55, 35, 10), (tp - 17, GROUND_Y - 310, 34, 312), 2)
        for i, (off, fc) in enumerate([
            (310, (185, 65, 28)),
            (230, ( 50, 135, 50)),
            (150, (170, 105, 25)),
            ( 70, ( 95,  55, 175)),
        ]):
            fy = GROUND_Y - off
            pygame.draw.rect(surface, fc, (tp - 21, fy, 42, 56), border_radius=3)
            pygame.draw.rect(surface, (0, 0, 0), (tp - 21, fy, 42, 56), 2, border_radius=3)
            pygame.draw.rect(surface, (255, 255, 200), (tp - 14, fy +  9, 9, 7))
            pygame.draw.rect(surface, (255, 255, 200), (tp +  5, fy +  9, 9, 7))
            pygame.draw.rect(surface, (0,   0,   0),   (tp - 12, fy + 11, 5, 3))
            pygame.draw.rect(surface, (0,   0,   0),   (tp +  7, fy + 11, 5, 3))
            if i % 2 == 0:
                pygame.draw.rect(surface, (0, 0, 0), (tp - 10, fy + 34, 20, 7), border_radius=2)
                for tx in (tp - 9, tp - 3, tp + 3, tp + 8):
                    pygame.draw.rect(surface, (255, 255, 200), (tx, fy + 34, 4, 5))
            else:
                pygame.draw.rect(surface, (0, 0, 0), (tp - 8, fy + 34, 16, 6), border_radius=2)
        pygame.draw.polygon(surface, (185, 65, 28),
                            [(tp, GROUND_Y - 330), (tp - 19, GROUND_Y - 310), (tp + 19, GROUND_Y - 310)])
        # Eerie purple floor glow (void energy seeping from above, collecting below)
        fsurf = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
        for fi in range(50):
            a2 = int(50 * (1 - fi / 50))
            pygame.draw.line(fsurf, (100, 0, 180, a2), (0, 50 - fi), (WIDTH, 50 - fi))
        surface.blit(fsurf, (0, GROUND_Y - 40))
        # Dark rocky ground
        pygame.draw.rect(surface, (25, 15, 45), (0, GROUND_Y + 2, WIDTH, HEIGHT - GROUND_Y - 2))
        pygame.draw.line(surface, (80, 45, 120), (0, GROUND_Y + 2), (WIDTH, GROUND_Y + 2), 3)
        # Rock chunks along ground
        for rx2, rw2, rh2 in [(50,60,18),(200,45,14),(420,70,20),(600,50,16),(780,55,19)]:
            pygame.draw.ellipse(surface, (45, 28, 70), (rx2, GROUND_Y + 2, rw2, rh2))

    elif s == 21:  # Graveyard
        # Dark blue-grey night sky
        for gy2 in range(HEIGHT):
            t = gy2 / HEIGHT
            r = int(15 + t * 20)
            g = int(20 + t * 25)
            b = int(35 + t * 30)
            pygame.draw.line(surface, (r, g, b), (0, gy2), (WIDTH, gy2))
        # Full moon with glow
        pygame.draw.circle(surface,(210,210,180),(180,70),36)
        pygame.draw.circle(surface,(240,240,210),(180,70),30)
        msurf = pygame.Surface((120,120),pygame.SRCALPHA)
        pygame.draw.circle(msurf,(200,200,170,20),(60,60),60)
        surface.blit(msurf,(120,10))
        # Stars
        for sx4,sy4 in [(70,30),(250,18),(400,45),(530,22),(640,38),(780,15),(850,55),(330,10)]:
            pygame.draw.circle(surface,(200,200,180),(sx4,sy4),2)
        # Fog at ground
        fsurf = pygame.Surface((WIDTH,60),pygame.SRCALPHA)
        for fy4 in range(60):
            fa = int((60-fy4)/60 * 40)
            pygame.draw.line(fsurf,(180,190,200,fa),(0,fy4),(WIDTH,fy4))
        surface.blit(fsurf,(0,GROUND_Y-30))
        # Dark ground with grass
        pygame.draw.rect(surface,(25,35,20),(0,GROUND_Y+2,WIDTH,HEIGHT-GROUND_Y-2))
        pygame.draw.rect(surface,(35,50,28),(0,GROUND_Y+2,WIDTH,8))
        pygame.draw.line(surface,(50,70,38),(0,GROUND_Y+2),(WIDTH,GROUND_Y+2),2)
        # Tombstones
        for gxt2 in [100,220,380,530,680,820]:
            gh = random.randint(32,48)
            pygame.draw.rect(surface,(55,55,60),(gxt2-10,GROUND_Y+2-gh,20,gh),border_radius=5)
            pygame.draw.rect(surface,(70,70,78),(gxt2-10,GROUND_Y+2-gh,20,gh),2,border_radius=5)
            if gxt2 % 2 == 0:
                pygame.draw.line(surface,(80,80,90),(gxt2,GROUND_Y+2-gh+8),(gxt2,GROUND_Y+2-gh+gh//2),1)
                pygame.draw.line(surface,(80,80,90),(gxt2-6,GROUND_Y+2-gh+gh//3),(gxt2+6,GROUND_Y+2-gh+gh//3),1)
        # Bare trees
        for tx4 in [50, 450, 870]:
            pygame.draw.line(surface,(40,38,35),(tx4,GROUND_Y+2),(tx4,GROUND_Y-100),4)
            for ang4 in [-45,-20,20,45]:
                bl4 = 35+random.randint(0,20)
                ex4 = tx4 + int(math.cos(math.radians(ang4))*bl4)
                ey4 = (GROUND_Y-80) + int(math.sin(math.radians(ang4-90))*bl4)
                pygame.draw.line(surface,(40,38,35),(tx4,GROUND_Y-80),(ex4,ey4),2)


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

    def _char_display_name(ch):
        n = ch["name"]
        if n == "ChickenBanana":
            t_cb2 = pygame.time.get_ticks()
            return "Chicken" if (t_cb2 // 500) % 2 == 0 else "Banana"
        return n
    p1_name = f"P1 — {_char_display_name(p1.char)}"
    bar(20, 40, p1.hp, p1.max_hp, p1.char["color"], p1_name)
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
    hint = font_small.render("R — rematch     C — char select     ESC — quit", True, (200,200,200))
    surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT*2//3 + 20))

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


