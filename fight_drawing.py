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
    al = int(ARM_LEN * s)

    def ln(p1, p2, w=2):
        pygame.draw.line(surface, col, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), max(1, int(w * s)))

    if char_name == "Brawler":
        # Red headband across forehead
        band_y = hy + int(hd * 0.2)
        pygame.draw.line(surface, (210, 0, 0), (hx - hd, band_y), (hx + hd, band_y), max(2, int(4*s)))
        # Headband knot trailing to side
        pygame.draw.line(surface, (210, 0, 0), (hx + hd - int(2*s), band_y),
                         (hx + hd + int(6*s), band_y - int(4*s)), max(2, int(3*s)))
        pygame.draw.line(surface, (210, 0, 0), (hx + hd + int(6*s), band_y - int(4*s)),
                         (hx + hd + int(10*s), band_y + int(6*s)), max(1, int(2*s)))
        # Wrapped wrist tape on both hands
        for _tx, _ty in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.rect(surface, (220, 210, 200),
                             (_tx - int(5*s), _ty - int(5*s), int(10*s), int(10*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (190, 180, 170),
                             (_tx - int(5*s), _ty - int(5*s), int(10*s), int(10*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
            # Tape cross-wrap lines
            pygame.draw.line(surface, (180, 160, 140),
                             (_tx - int(4*s), _ty - int(3*s)), (_tx + int(4*s), _ty + int(3*s)), max(1, int(s)))
        # Tank-top V-neck collar marks
        pygame.draw.line(surface, (200, 200, 200), (sx, sy + int(2*s)),
                         (sx - int(7*s), sy + int(12*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (200, 200, 200), (sx, sy + int(2*s)),
                         (sx + int(7*s), sy + int(12*s)), max(1, int(2*s)))
        # Angry scar line on cheek
        pygame.draw.line(surface, (180, 60, 60),
                         (hx + facing*int(hd*0.3), hy + int(hd*0.1)),
                         (hx + facing*int(hd*0.55), hy + int(hd*0.4)), max(1, int(2*s)))

    elif char_name == "Ninja":
        # Dark shinobi suit on torso
        pygame.draw.rect(surface, (20, 20, 20),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (40, 40, 40),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Diagonal wrap sash on torso
        pygame.draw.line(surface, (60, 60, 60),
                         (sx + int(facing*8*s), sy + int(2*s)),
                         (sx - int(facing*8*s), wy - int(4*s)), max(2, int(3*s)))
        # Shuriken (throwing star) on belt
        for _shi2 in range(4):
            _sha2 = math.radians(_shi2 * 45)
            pygame.draw.line(surface, (140, 145, 160),
                             (wx, wy), (wx + int(math.cos(_sha2)*7*s), wy + int(math.sin(_sha2)*7*s)),
                             max(1, int(2*s)))
        pygame.draw.circle(surface, (120, 125, 140), (wx, wy), max(3, int(4*s)))
        # Dark mask over lower face
        mask_y = hy + int(hd * 0.05)
        pygame.draw.rect(surface, (25, 25, 25), (hx - hd + 3, mask_y, hd*2 - 6, int(hd * 0.85)))
        # White headband
        band_y = hy - int(hd * 0.25)
        pygame.draw.line(surface, WHITE, (hx - hd, band_y), (hx + hd, band_y), max(2, int(3*s)))
        # Headband knot tails
        pygame.draw.line(surface, WHITE, (hx + hd - int(2*s), band_y),
                         (hx + hd + int(8*s), band_y - int(6*s)), max(1, int(2*s)))
        pygame.draw.line(surface, WHITE, (hx + hd + int(6*s), band_y - int(6*s)),
                         (hx + hd + int(10*s), band_y + int(4*s)), max(1, int(s)))
        # Katana on back (sheathed diagonal line)
        pygame.draw.line(surface, (160, 165, 180),
                         (sx - int(6*s), sy - int(4*s)),
                         (sx - int(14*s), sy + int(bl*0.85)), max(2, int(3*s)))

    elif char_name == "Boxer":
        # Big green boxing gloves at both hands
        for gx, gy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (0, 180, 0), (gx, gy), max(6, int(10*s)))
            pygame.draw.circle(surface, (0, 120, 0), (gx, gy), max(6, int(10*s)), max(1, int(2*s)))
            # Glove highlight
            pygame.draw.circle(surface, (80, 230, 80),
                               (gx - max(2,int(2*s)), gy - max(2,int(2*s))), max(2, int(3*s)))
            # Glove knuckle ridge
            pygame.draw.line(surface, (0, 90, 0),
                             (gx - max(3,int(5*s)), gy), (gx + max(3,int(5*s)), gy), max(1, int(s)))
        # White wrist tape bands
        for gx2, gy2 in [(lhx, lhy), (rhx, rhy)]:
            _wx3 = (gx2 + sx) // 2
            _wy7 = (gy2 + sy) // 2
            pygame.draw.rect(surface, (220, 220, 220),
                             (_wx3 - int(4*s), _wy7 - int(3*s), int(8*s), int(6*s)),
                             border_radius=max(1, int(2*s)))
        # Boxing shorts on torso
        pygame.draw.rect(surface, (0, 100, 180),
                         (sx - int(9*s), sy + bl//2, int(18*s), bl//2), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (0, 70, 140),
                         (sx - int(9*s), sy + bl//2, int(18*s), bl//2), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Side stripe on shorts
        pygame.draw.line(surface, (255, 255, 255),
                         (sx - int(7*s), sy + bl//2 + int(2*s)),
                         (sx - int(7*s), wy - int(2*s)), max(2, int(2*s)))
        # Bald head with ear guards
        for _eg in (-1, 1):
            pygame.draw.circle(surface, (200, 60, 0),
                               (hx + _eg*int(hd*0.9), hy), max(3, int(5*s)))
            pygame.draw.circle(surface, (160, 40, 0),
                               (hx + _eg*int(hd*0.9), hy), max(3, int(5*s)), max(1, int(s)))
        # Bruised eyebrow
        pygame.draw.line(surface, (120, 40, 80),
                         (hx - int(hd*0.55), hy - int(hd*0.4)),
                         (hx - int(hd*0.1), hy - int(hd*0.25)), max(2, int(3*s)))

    elif char_name == "Phantom":
        # Purple eye-mask over upper face
        pygame.draw.ellipse(surface, (90, 0, 180), (hx - hd + 2, hy - hd + 2, hd*2 - 4, int(hd * 0.9)))
        pygame.draw.ellipse(surface, (160, 60, 255), (hx - hd + 2, hy - hd + 2, hd*2 - 4, int(hd * 0.9)), 2)
        # Eye holes (white) in the mask
        for _eox in (-int(hd*0.4), int(hd*0.4)):
            pygame.draw.ellipse(surface, (220, 200, 255),
                                (hx + _eox - int(hd*0.2), hy - int(hd*0.55),
                                 int(hd*0.4), int(hd*0.3)))
        # Shadow cape from shoulders
        cape_pts = [
            (sx - int(hd*0.55), sy + int(4*s)),
            (sx - int(hd*2.2), wy + int(20*s)),
            (sx - int(hd*1.0), wy + int(10*s)),
            (sx + int(hd*1.0), wy + int(10*s)),
            (sx + int(hd*2.2), wy + int(20*s)),
            (sx + int(hd*0.55), sy + int(4*s)),
        ]
        pygame.draw.polygon(surface, (55, 0, 120), cape_pts)
        pygame.draw.polygon(surface, (100, 30, 200), cape_pts, max(1, int(2*s)))
        # Phantom chest emblem (stylized P shape)
        pygame.draw.circle(surface, (130, 40, 240), (sx, sy + int(bl*0.3)), max(4, int(6*s)), max(1, int(2*s)))
        # Tie/cravat
        pygame.draw.polygon(surface, (200, 180, 0), [
            (sx - int(4*s), sy + int(4*s)),
            (sx + int(4*s), sy + int(4*s)),
            (sx, sy + int(18*s))
        ])

    elif char_name == "Ares":
        # Bronze breastplate on torso
        pygame.draw.rect(surface, (160, 82, 10),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (210, 120, 30),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Breastplate ridge lines (armor segments)
        for _ari in range(3):
            _ary = sy + int(bl * (0.25 + _ari * 0.25))
            pygame.draw.line(surface, (220, 140, 50),
                             (sx - int(9*s), _ary), (sx + int(9*s), _ary), max(1, int(2*s)))
        # Center line divide on breastplate
        pygame.draw.line(surface, (220, 140, 50),
                         (sx, sy + int(4*s)), (sx, sy + int(bl * 0.85)), max(1, int(s)))
        # Bronze pauldrons (shoulder guards)
        for _pside in (-1, 1):
            pygame.draw.ellipse(surface, (160, 82, 10),
                                (sx + _pside * int(4*s), sy - int(10*s), int(14*s), int(10*s)))
            pygame.draw.ellipse(surface, (210, 120, 30),
                                (sx + _pside * int(4*s), sy - int(10*s), int(14*s), int(10*s)),
                                max(1, int(s)))
        # Red tunic/skirt lines below waist
        for _ti in range(5):
            _tx = sx - int(8*s) + _ti * int(4*s)
            pygame.draw.line(surface, (180, 20, 20),
                             (_tx, wy), (_tx + int(2*s), wy + int(12*s)), max(1, int(2*s)))
        # Sandal straps on feet area
        for _fside in (-1, 1):
            _fx = wx + _fside * int(6*s)
            _fy = wy + int(bl * 0.5)
            pygame.draw.line(surface, (140, 70, 10),
                             (_fx - int(4*s), _fy), (_fx + int(4*s), _fy), max(1, int(2*s)))
            pygame.draw.line(surface, (140, 70, 10),
                             (_fx - int(3*s), _fy + int(5*s)), (_fx + int(3*s), _fy + int(5*s)),
                             max(1, int(s)))
        # Spear in right hand
        pygame.draw.line(surface, (160, 120, 40),
                         (rhx, rhy - int(8*s)), (rhx + facing * int(4*s), rhy - int(40*s)),
                         max(2, int(3*s)))
        pygame.draw.polygon(surface, (190, 190, 210), [
            (rhx + facing * int(4*s), rhy - int(40*s)),
            (rhx + facing * int(10*s), rhy - int(50*s)),
            (rhx - facing * int(2*s), rhy - int(44*s)),
        ])
        # Greek war helmet + red horsehair crest
        pts = [(hx - hd, hy), (hx - int(hd*.8), hy - int(hd*1.3)),
               (hx, hy - int(hd*1.6)), (hx + int(hd*.8), hy - int(hd*1.3)),
               (hx + hd, hy)]
        pygame.draw.polygon(surface, (190, 95, 0), pts)
        pygame.draw.polygon(surface, (255, 140, 0), pts, 2)
        # Helmet cheek guards
        for _hgside in (-1, 1):
            pygame.draw.rect(surface, (160, 82, 10),
                             (hx + _hgside * int(hd * 0.7), hy - int(hd * 0.3),
                              int(hd * 0.35), int(hd * 0.7)), border_radius=max(1, int(2*s)))
        # Red horsehair crest
        pygame.draw.line(surface, RED, (hx, hy - int(hd*1.6)), (hx, hy - int(hd*2.3)), max(2, int(4*s)))
        for _ci in range(4):
            _coff = (_ci - 1.5) * int(hd * 0.2)
            pygame.draw.line(surface, (180, 10, 10),
                             (hx + int(_coff), hy - int(hd * 1.9)),
                             (hx + int(_coff) + int(facing * 3 * s), hy - int(hd * 2.25)),
                             max(1, int(2*s)))

    elif char_name == "Zephyr":
        # Flight goggles with blue lenses
        gy = hy - int(hd * 0.1)
        for gx_off in [-int(hd*.38), int(hd*.38)]:
            pygame.draw.circle(surface, (0, 70, 180), (hx + gx_off, gy), int(hd*.33))
            pygame.draw.circle(surface, CYAN, (hx + gx_off, gy), int(hd*.33), max(1, int(2*s)))
            # Lens highlight
            pygame.draw.circle(surface, (180, 240, 255),
                               (hx + gx_off - max(1,int(2*s)), gy - max(1,int(2*s))), max(1, int(2*s)))
        pygame.draw.line(surface, (80, 140, 255), (hx - int(hd*.72), gy), (hx + int(hd*.72), gy), max(1, int(2*s)))
        # Aviator jacket with fur collar
        pygame.draw.rect(surface, (100, 70, 30),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (70, 45, 15),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Fur collar trim
        for _fci in range(5):
            pygame.draw.circle(surface, (230, 220, 200),
                               (sx - int(8*s) + _fci * int(4*s), sy + int(3*s)), max(3, int(4*s)))
        # Wind streamlines on back
        for _wli in range(3):
            pygame.draw.line(surface, (160, 200, 255),
                             (sx - facing*int((6+_wli*6)*s), sy + int(bl*0.25*(_wli+1))),
                             (sx - facing*int((14+_wli*6)*s), sy + int(bl*0.25*(_wli+1)) - int(4*s)),
                             max(1, int(s)))
        # Flight helmet cap over head
        pygame.draw.ellipse(surface, (90, 60, 25),
                            (hx - int(hd*1.1), hy - hd - int(hd*0.65), int(hd*2.2), int(hd*0.8)))
        pygame.draw.ellipse(surface, (70, 45, 15),
                            (hx - int(hd*1.1), hy - hd - int(hd*0.65), int(hd*2.2), int(hd*0.8)),
                            max(1, int(2*s)))

    elif char_name == "Titan":
        # Titanic body — thick stone-gray armor on torso
        pygame.draw.rect(surface, (90, 100, 120),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (130, 140, 160),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Armor ridge lines
        for _ari in range(3):
            _ary = sy + int(bl * (0.2 + _ari * 0.28))
            pygame.draw.line(surface, (150, 160, 180),
                             (sx - int(10*s), _ary), (sx + int(10*s), _ary), max(1, int(2*s)))
        # Massive spiked shoulder plates
        for _tside in (-1, 1):
            pygame.draw.rect(surface, (80, 90, 110),
                             (sx + _tside*int(3*s), sy - int(8*s), int(16*s), int(12*s)),
                             border_radius=max(2, int(3*s)))
            # Shoulder spike
            pygame.draw.polygon(surface, (110, 120, 140), [
                (sx + _tside*int(10*s), sy - int(8*s)),
                (sx + _tside*int(15*s), sy - int(22*s)),
                (sx + _tside*int(18*s), sy - int(8*s)),
            ])
        # Huge stone fists
        for _tfx, _tfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (90, 100, 120), (_tfx, _tfy), max(6, int(12*s)))
            pygame.draw.circle(surface, (130, 140, 160), (_tfx, _tfy), max(6, int(12*s)), max(1, int(2*s)))
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
        # Crown gem highlights
        for _cgi2, _cgx in enumerate([hx - int(hd*0.5), hx, hx + int(hd*0.5)]):
            pygame.draw.circle(surface, (255, 0, 0) if _cgi2 == 1 else (0, 200, 255),
                               (_cgx, ct + int(hd*0.84)), max(2, int(3*s)))

    elif char_name == "Dancing Man":
        # Black tuxedo jacket on torso
        pygame.draw.rect(surface, (15, 15, 20),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (50, 50, 60),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # White dress shirt (front triangle)
        pygame.draw.polygon(surface, (230, 230, 230), [
            (sx - int(3*s), sy + int(3*s)),
            (sx + int(3*s), sy + int(3*s)),
            (sx + int(5*s), sy + int(bl * 0.6)),
            (sx - int(5*s), sy + int(bl * 0.6)),
        ])
        # Shirt buttons
        for _bi in range(3):
            _by2 = sy + int(bl * (0.15 + _bi * 0.18))
            pygame.draw.circle(surface, (180, 180, 190), (sx, _by2), max(1, int(2*s)))
        # Bowtie at collar
        _bty = sy + int(4*s)
        pygame.draw.polygon(surface, (180, 20, 20), [
            (sx - int(6*s), _bty - int(3*s)),
            (sx, _bty),
            (sx - int(6*s), _bty + int(3*s)),
        ])
        pygame.draw.polygon(surface, (180, 20, 20), [
            (sx + int(6*s), _bty - int(3*s)),
            (sx, _bty),
            (sx + int(6*s), _bty + int(3*s)),
        ])
        pygame.draw.circle(surface, (200, 30, 30), (sx, _bty), max(2, int(3*s)))
        # White gloves on both hands
        for _gwx, _gwy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (240, 240, 240), (_gwx, _gwy), max(4, int(7*s)))
            pygame.draw.circle(surface, (200, 200, 200), (_gwx, _gwy), max(4, int(7*s)), max(1, int(s)))
        # Cane in right hand (thin black line with gold top)
        pygame.draw.line(surface, (30, 30, 30),
                         (rhx, rhy + int(4*s)), (rhx + facing * int(6*s), rhy + int(35*s)),
                         max(2, int(3*s)))
        pygame.draw.circle(surface, (200, 170, 0),
                           (rhx, rhy + int(4*s)), max(3, int(5*s)))
        # Spats (white rectangular covering over feet)
        for _spside in (-1, 1):
            _spx = wx + _spside * int(5*s)
            pygame.draw.rect(surface, (230, 230, 230),
                             (_spx - int(5*s), wy + int(bl * 0.55), int(10*s), int(8*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (180, 180, 180),
                             (_spx - int(5*s), wy + int(bl * 0.55), int(10*s), int(8*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Top hat (drawn last so it sits on top)
        brim_y = hy - hd
        hw = int(hd * 1.5)
        hh = int(hd * 1.2)
        pygame.draw.rect(surface, (20, 20, 20), (hx - int(hw*.6), brim_y - hh, int(hw*1.2), hh))
        pygame.draw.line(surface, (20, 20, 20), (hx - hw, brim_y), (hx + hw, brim_y), max(3, int(5*s)))
        pygame.draw.rect(surface, (60, 60, 60), (hx - int(hw*.6), brim_y - hh, int(hw*1.2), hh), 2)
        # Hat band
        pygame.draw.rect(surface, (180, 20, 20),
                         (hx - int(hw*.6), brim_y - int(4*s), int(hw*1.2), max(2, int(4*s))))

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
        # Bone-white face with dark eye sockets
        pygame.draw.circle(surface, (235, 230, 215), (hx, hy), hd)
        # Eye sockets
        ey = hy - int(hd * .2)
        for ex_off in [-int(hd*.4), int(hd*.4)]:
            pygame.draw.circle(surface, (15, 15, 15), (hx + ex_off, ey), int(hd*.3))
            pygame.draw.circle(surface, (40, 35, 30), (hx + ex_off, ey), int(hd*.3), max(1, int(s)))
        # Nasal cavity (inverted V)
        pygame.draw.line(surface, (30, 25, 20),
                         (hx, hy + int(hd*0.1)), (hx - int(hd*0.15), hy + int(hd*0.28)), max(1, int(s)))
        pygame.draw.line(surface, (30, 25, 20),
                         (hx, hy + int(hd*0.1)), (hx + int(hd*0.15), hy + int(hd*0.28)), max(1, int(s)))
        # Teeth (vertical lines)
        ty = hy + int(hd * .48)
        pygame.draw.line(surface, (30, 25, 20), (hx - int(hd*0.5), ty - int(hd*0.1)),
                         (hx + int(hd*0.5), ty - int(hd*0.1)), max(1, int(s)))
        for i in range(-2, 3):
            tx = hx + i * int(hd * .25)
            pygame.draw.line(surface, (20, 18, 15), (tx, ty - int(hd*.1)), (tx, ty + int(hd*.22)), max(2, int(3*s)))
        # Rib cage lines on torso
        for _ri in range(3):
            _ry = sy + int(bl * (0.2 + _ri * 0.25))
            pygame.draw.arc(surface, (220, 215, 200),
                            (sx - int(9*s), _ry - int(4*s), int(18*s), int(8*s)),
                            math.radians(0), math.radians(180), max(1, int(2*s)))
        # Spine line down torso center
        pygame.draw.line(surface, (200, 195, 180),
                         (sx, sy + int(2*s)), (sx, wy - int(2*s)), max(1, int(s)))
        # Bony knee joints (circles on upper leg)
        pygame.draw.circle(surface, (225, 220, 205), (wx - int(8*s), wy + int(bl*0.4)), max(3, int(4*s)), max(1, int(s)))
        pygame.draw.circle(surface, (225, 220, 205), (wx + int(8*s), wy + int(bl*0.4)), max(3, int(4*s)), max(1, int(s)))

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
        # Yellow construction hard hat (filled dome + brim)
        pygame.draw.ellipse(surface, (220, 200, 0), (hx - hd, hy - int(hd*1.85), hd*2, int(hd*1.4)))
        pygame.draw.ellipse(surface, (180, 160, 0), (hx - hd, hy - int(hd*1.85), hd*2, int(hd*1.4)), max(1, int(2*s)))
        # Highlight on hat dome
        pygame.draw.line(surface, (255, 240, 60), (hx - int(hd*0.4), hy - int(hd*1.7)),
                         (hx + int(hd*0.2), hy - int(hd*1.5)), max(1, int(2*s)))
        # Wide brim
        pygame.draw.line(surface, (180, 160, 0), (hx - int(hd*1.35), hy - int(hd*.5)), (hx + int(hd*1.35), hy - int(hd*.5)), max(3, int(5*s)))
        # Chin strap
        pygame.draw.arc(surface, (160, 140, 0),
                        (hx - int(hd*0.9), hy - int(hd*0.5), int(hd*1.8), int(hd*1.2)),
                        math.radians(0), math.radians(180), max(1, int(2*s)))
        # Orange hi-vis vest stripes on torso
        for _vi in range(2):
            _vy = sy + int(bl * (0.25 + _vi * 0.45))
            pygame.draw.line(surface, (255, 140, 0),
                             (sx - int(9*s), _vy), (sx + int(9*s), _vy), max(2, int(3*s)))
        # Tool belt at waist
        pygame.draw.rect(surface, (100, 70, 20),
                         (wx - int(hd*1.0), wy - int(3*s), int(hd*2.0), max(4, int(6*s))))
        pygame.draw.rect(surface, (80, 55, 15),
                         (wx - int(hd*1.0), wy - int(3*s), int(hd*2.0), max(4, int(6*s))), 1)
        # Belt buckle
        pygame.draw.rect(surface, (180, 160, 0),
                         (wx - int(4*s), wy - int(3*s), int(8*s), max(4, int(6*s))))

    elif char_name == "Rogue":
        # Tan hood
        pygame.draw.polygon(surface, (145, 115, 28), [
            (hx - int(hd*1.25), hy + int(hd*.3)), (hx, hy - int(hd*2.05)),
            (hx + int(hd*1.25), hy + int(hd*.3))])
        pygame.draw.polygon(surface, (200, 160, 50), [
            (hx - int(hd*1.25), hy + int(hd*.3)), (hx, hy - int(hd*2.05)),
            (hx + int(hd*1.25), hy + int(hd*.3))], 2)
        # Glinting eyes beneath hood shadow
        for ex_off in [-int(hd*.3), int(hd*.3)]:
            pygame.draw.circle(surface, (180, 140, 20), (hx + ex_off, hy), int(hd*.18))
            pygame.draw.circle(surface, (70, 55, 10), (hx + ex_off, hy), int(hd*.15))
        # Dark cloak body covering torso
        cloak_pts = [
            (sx - int(hd*0.6), sy), (sx - int(hd*1.4), wy + int(10*s)),
            (sx - int(hd*0.6), wy), (sx + int(hd*0.6), wy),
            (sx + int(hd*1.4), wy + int(10*s)), (sx + int(hd*0.6), sy),
        ]
        pygame.draw.polygon(surface, (120, 90, 20), cloak_pts)
        pygame.draw.polygon(surface, (175, 135, 40), cloak_pts, max(1, int(2*s)))
        # Dagger in forward hand (short blade)
        dagger_tip = (rhx + facing*int(18*s), rhy - int(12*s))
        pygame.draw.line(surface, (180, 185, 200), (rhx, rhy), dagger_tip, max(2, int(3*s)))
        pygame.draw.line(surface, (80, 55, 15), (rhx - facing*int(5*s), rhy + int(4*s)),
                         (rhx, rhy), max(3, int(4*s)))
        # Crossguard on dagger
        pygame.draw.line(surface, (150, 120, 30),
                         (rhx - int(5*s), rhy - int(3*s)),
                         (rhx + int(5*s), rhy - int(3*s)), max(1, int(2*s)))

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
        # Lorica segmentata (segmented chest armor)
        for _seg in range(3):
            _sy2 = sy + int(bl * (0.1 + _seg * 0.28))
            pygame.draw.rect(surface, (175, 50, 50),
                             (sx - int(10*s), _sy2, int(20*s), int(bl*0.22)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (220, 80, 80),
                             (sx - int(10*s), _sy2, int(20*s), int(bl*0.22)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Short gladius sword in right hand
        gladius_tip = (rhx + facing*int(32*s), rhy - int(8*s))
        pygame.draw.line(surface, (190, 195, 210), (rhx, rhy), gladius_tip, max(2, int(3*s)))
        pygame.draw.line(surface, (240, 245, 255), (rhx, rhy), gladius_tip, max(1, int(s)))
        pygame.draw.line(surface, (120, 80, 25),  # handle
                         (rhx - facing*int(6*s), rhy + int(3*s)),
                         (rhx, rhy), max(3, int(5*s)))
        # Crossguard
        pygame.draw.line(surface, (150, 105, 40),
                         (rhx - int(7*s), rhy - int(4*s)),
                         (rhx + int(7*s), rhy - int(4*s)), max(2, int(3*s)))
        # Square shield (scutum) in left hand
        shld_pts = [
            (lhx - facing*int(18*s), lhy - int(20*s)),
            (lhx + facing*int(4*s),  lhy - int(20*s)),
            (lhx + facing*int(4*s),  lhy + int(20*s)),
            (lhx - facing*int(18*s), lhy + int(20*s)),
        ]
        pygame.draw.polygon(surface, (100, 30, 30), shld_pts)
        pygame.draw.polygon(surface, (160, 50, 50), shld_pts, max(1, int(2*s)))
        # Shield boss (center circle)
        pygame.draw.circle(surface, (180, 140, 20),
                           (lhx - facing*int(7*s), lhy), max(4, int(6*s)))
        pygame.draw.circle(surface, (220, 180, 40),
                           (lhx - facing*int(7*s), lhy), max(4, int(6*s)), max(1, int(s)))

    elif char_name == "Oni":
        # Red demon horns
        for hd_off, curve in [(-int(hd*.7), -1), (int(hd*.7), 1)]:
            pygame.draw.polygon(surface, (200, 15, 15), [
                (hx + hd_off, hy - hd),
                (hx + hd_off + curve * int(hd*.35), hy - int(hd*2.05)),
                (hx + hd_off + curve * int(hd*.12), hy - int(hd*1.5))])
            pygame.draw.polygon(surface, (240, 60, 60), [
                (hx + hd_off, hy - hd),
                (hx + hd_off + curve * int(hd*.35), hy - int(hd*2.05)),
                (hx + hd_off + curve * int(hd*.12), hy - int(hd*1.5))], max(1, int(s)))
        # Angry V-shaped brows
        brow_y = hy - int(hd * .35)
        pygame.draw.line(surface, (80, 0, 0), (hx - int(hd*.62), brow_y - int(hd*.25)), (hx - int(hd*.1), brow_y), max(3, int(4*s)))
        pygame.draw.line(surface, (80, 0, 0), (hx + int(hd*.1), brow_y), (hx + int(hd*.62), brow_y - int(hd*.25)), max(3, int(4*s)))
        # Fanged mouth
        for _fx in (-int(hd*0.3), int(hd*0.3)):
            pygame.draw.polygon(surface, (245, 240, 230), [
                (hx + _fx - int(hd*0.12), hy + int(hd*0.45)),
                (hx + _fx + int(hd*0.12), hy + int(hd*0.45)),
                (hx + _fx, hy + int(hd*0.72))
            ])
        # Loincloth / tiger stripe cloth on torso
        pygame.draw.rect(surface, (40, 20, 5),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=max(1, int(2*s)))
        # Tiger stripes
        for _oi2 in range(3):
            pygame.draw.line(surface, (80, 50, 10),
                             (sx - int(8*s), sy + int(bl*(0.2 + _oi2*0.25))),
                             (sx + int(8*s), sy + int(bl*(0.2 + _oi2*0.25)) - int(4*s)),
                             max(2, int(3*s)))
        # War club / kanabo in right hand
        club_tip = (rhx + facing*int(8*s), rhy - int(38*s))
        pygame.draw.line(surface, (60, 35, 10), (rhx, rhy), club_tip, max(3, int(5*s)))
        # Spikes on the club
        for _csi in range(3):
            _cst = _csi / 3.0
            _csx = int(rhx + facing*int(8*s) + (club_tip[0] - rhx - facing*int(8*s))*_cst)
            _csy = int(rhy + (club_tip[1] - rhy)*_cst)
            pygame.draw.circle(surface, (180, 120, 20), (_csx, _csy), max(2, int(3*s)))
        # Red war paint on face cheeks
        for _rw in (-1, 1):
            pygame.draw.line(surface, (200, 20, 20),
                             (hx + _rw*int(hd*0.5), hy - int(hd*0.2)),
                             (hx + _rw*int(hd*0.7), hy + int(hd*0.15)), max(2, int(3*s)))

    elif char_name == "Cecalia":
        # Tentacles hanging from waist (waving)
        t_ce = pygame.time.get_ticks()
        for i in range(4):
            tx = wx + int((i - 1.5) * 18 * s)
            _tc = (20 + i*20, 180 + i*10, 180 + i*10)
            for seg in range(4):
                y1 = wy + seg * int(16*s)
                y2 = wy + (seg+1) * int(16*s)
                wave = int(math.sin(seg * 1.5 + i + t_ce * 0.004) * 8 * s)
                pygame.draw.line(surface, _tc, (tx + wave, y1), (tx - wave, y2), max(2, int(4*s)))
            # Sucker rings on tentacle tip
            pygame.draw.circle(surface, (10, 150, 150),
                               (tx, wy + int(62*s)), max(2, int(3*s)), max(1, int(s)))
        # Flowing ocean-blue robe on upper torso
        pygame.draw.rect(surface, (10, 100, 140),
                         (sx - int(10*s), sy, int(20*s), bl//2), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (20, 160, 180),
                         (sx - int(10*s), sy, int(20*s), bl//2), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Scale pattern on robe
        for _scr in range(3):
            for _scc in range(2):
                pygame.draw.arc(surface, (10, 130, 160),
                                (sx - int(9*s) + _scc*int(9*s), sy + int(bl*0.1*_scr), int(10*s), int(8*s)),
                                math.radians(0), math.radians(180), max(1, int(s)))
        # Tentacle hair on head (small waving tendrils)
        for _hi3 in range(5):
            _tha = math.radians(-100 + _hi3 * 50)
            _thbx = hx + int(math.cos(_tha) * hd * 0.85)
            _thby = hy + int(math.sin(_tha) * hd * 0.85)
            _thtx = _thbx + int(math.cos(_tha) * hd * 0.7) + int(math.sin(t_ce * 0.005 + _hi3) * 4 * s)
            _thty = _thby + int(math.sin(_tha) * hd * 0.7)
            pygame.draw.line(surface, (30, 200, 200), (_thbx, _thby), (_thtx, _thty), max(2, int(3*s)))
        # Deep-sea glowing eyes
        for _eox in (-int(hd*0.35), int(hd*0.35)):
            pygame.draw.circle(surface, (0, 220, 220), (hx + _eox, hy - int(hd*0.1)), max(3, int(4*s)))
            pygame.draw.circle(surface, (180, 255, 255), (hx + _eox, hy - int(hd*0.1)), max(1, int(2*s)))

    elif char_name == "Acrobat":
        # Colorful top hat
        brim_y = hy - hd
        hw, hh = int(hd * 1.4), int(hd * 1.1)
        pygame.draw.rect(surface, (190, 70, 190), (hx - int(hw*.55), brim_y - hh, int(hw*1.1), hh))
        pygame.draw.rect(surface, (140, 40, 140), (hx - int(hw*.55), brim_y - hh, int(hw*1.1), hh), max(1, int(2*s)))
        pygame.draw.line(surface, (210, 90, 210), (hx - hw, brim_y), (hx + hw, brim_y), max(3, int(5*s)))
        # White hat band
        pygame.draw.rect(surface, WHITE, (hx - int(hw*.55), brim_y - int(hh*.72), int(hw*1.1), int(hd*.28)))
        # Hat pompom
        pygame.draw.circle(surface, (255, 200, 0), (hx, brim_y - hh), max(3, int(4*s)))
        # Acrobatic leotard on torso (diamond pattern)
        pygame.draw.rect(surface, (200, 60, 200),
                         (sx - int(7*s), sy, int(14*s), bl), border_radius=max(1, int(2*s)))
        # Diamond patterns on leotard
        for _di2 in range(3):
            _dy2 = sy + int(bl * (0.2 + _di2 * 0.3))
            pygame.draw.polygon(surface, (255, 220, 0), [
                (sx, _dy2 - int(5*s)), (sx + int(5*s), _dy2),
                (sx, _dy2 + int(5*s)), (sx - int(5*s), _dy2)
            ])
        # Wrist ribbons on hands
        for _wx2, _wy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (255, 180, 255), (_wx2, _wy2), max(3, int(5*s)))
            pygame.draw.line(surface, (200, 120, 200),
                             (_wx2, _wy2), (_wx2 + facing*int(8*s), _wy2 - int(8*s)), max(1, int(2*s)))

    elif char_name == "Shapeshifter":
        # Shifting body — different limb textures suggest morphing
        t_ss = pygame.time.get_ticks()
        # Dashed purple glow ring
        for angle in range(0, 360, 30):
            a1, a2 = math.radians(angle), math.radians(angle + 20)
            r = (hd + int(5*s))
            p1 = (hx + int(math.cos(a1)*r), hy + int(math.sin(a1)*r))
            p2 = (hx + int(math.cos(a2)*r), hy + int(math.sin(a2)*r))
            pygame.draw.line(surface, (175, 75, 255), p1, p2, max(2, int(3*s)))
        # Inner shifting ring (different phase)
        for angle in range(15, 360, 30):
            a1, a2 = math.radians(angle), math.radians(angle + 20)
            r2 = (hd + int(9*s))
            p1 = (hx + int(math.cos(a1)*r2), hy + int(math.sin(a1)*r2))
            p2 = (hx + int(math.cos(a2)*r2), hy + int(math.sin(a2)*r2))
            pygame.draw.line(surface, (220, 140, 255), p1, p2, max(1, int(2*s)))
        # Morphing face features (shifting eye shapes)
        morph_phase = math.sin(t_ss * 0.004)
        for _eox in (-int(hd*0.38), int(hd*0.38)):
            _er2 = max(2, int((3 + 2 * abs(morph_phase)) * s))
            pygame.draw.ellipse(surface, (200, 100, 255),
                                (hx + _eox - _er2, hy - int(hd*0.1) - _er2, _er2*2, int(_er2 * (1 + morph_phase))))
        # Fluid body silhouette (wavy outline on torso)
        for _wv in range(4):
            _wy3 = sy + int(bl * (0.1 + _wv * 0.25))
            _wave2 = int(math.sin(t_ss * 0.006 + _wv) * 3 * s)
            pygame.draw.line(surface, (140, 60, 220),
                             (sx - int(8*s) + _wave2, _wy3),
                             (sx + int(8*s) + _wave2, _wy3), max(1, int(s)))
        # Color-shifting hands
        _hue = int(t_ss * 0.5) % 360
        _hcol = (max(0, 180 - abs(_hue % 360 - 180)), max(0, 180 - abs((_hue + 120) % 360 - 180)), max(0, 180 - abs((_hue + 240) % 360 - 180)))
        for _hhx, _hhy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, _hcol, (_hhx, _hhy), max(4, int(6*s)))

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
        # Spring torso coil lines (compress/stretch effect)
        for _sci2 in range(4):
            _scy = sy + int(bl * (0.15 + _sci2 * 0.23))
            _swi = int(math.sin(_sci2 * 0.8) * 3 * s)
            pygame.draw.line(surface, (255, 140, 140),
                             (sx - int(7*s) + _swi, _scy),
                             (sx + int(7*s) + _swi, _scy), max(1, int(2*s)))
        # Big spring coil on right hand (spring fist)
        for _hci in range(3):
            _hca = math.radians(_hci * 120)
            _hcr = max(4, int(6*s))
            pygame.draw.circle(surface, (255, 100, 100),
                               (rhx + int(math.cos(_hca)*_hcr), rhy + int(math.sin(_hca)*_hcr)),
                               max(2, int(3*s)))
        # Bouncy "boing" eyes
        for _eox in (-int(hd*0.38), int(hd*0.38)):
            pygame.draw.circle(surface, (255, 60, 60), (hx + _eox, hy - int(hd*0.1)), max(3, int(4*s)))
            pygame.draw.circle(surface, (255, 200, 200), (hx + _eox, hy - int(hd*0.1)), max(1, int(2*s)))

    elif char_name == "Harpy":
        # Large feathered wings from shoulders
        for side in [-1, 1]:
            wing_pts = [
                (sx, sy),
                (sx + side*int(52*s), sy - int(18*s)),
                (sx + side*int(62*s), sy + int(22*s)),
                (sx + side*int(36*s), sy + int(36*s)),
                (sx + side*int(15*s), sy + int(20*s))]
            pygame.draw.polygon(surface, (115, 0, 115), wing_pts)
            pygame.draw.polygon(surface, (175, 0, 175), wing_pts, 2)
            # Wing feather detail lines
            for _wfi in range(3):
                _wfp1 = (sx + side*int((12 + _wfi*14)*s), sy + int((_wfi*8)*s))
                _wfp2 = (sx + side*int((38 + _wfi*8)*s), sy + int((5 + _wfi*10)*s))
                pygame.draw.line(surface, (80, 0, 80), _wfp1, _wfp2, max(1, int(s)))
        # Feathered torso
        for _fti in range(3):
            _ftcol = (130, 20, 130) if _fti % 2 == 0 else (160, 40, 160)
            pygame.draw.ellipse(surface, _ftcol,
                                (sx - int(8*s), sy + int(bl*0.2*_fti), int(16*s), int(bl*0.25)))
        # Eagle-like beak on face
        beak_x = hx + facing * int(hd)
        pygame.draw.polygon(surface, (200, 160, 20), [
            (beak_x, hy - int(hd*0.2)),
            (beak_x + facing*int(10*s), hy + int(hd*0.05)),
            (beak_x, hy + int(hd*0.2)),
        ])
        # Taloned feet at hands
        for _tfx, _tfy in [(lhx, lhy), (rhx, rhy)]:
            for _tci in range(3):
                _tca = math.radians(-30 + _tci * 30)
                pygame.draw.line(surface, (150, 100, 20),
                                 (_tfx, _tfy),
                                 (_tfx + int(math.cos(_tca)*8*s), _tfy + int(math.sin(_tca)*6*s)),
                                 max(1, int(2*s)))

    elif char_name == "Scarecrow":
        # Straw hat (filled triangle with base)
        hat_y = hy - hd
        hw = int(hd * 2.0)
        pygame.draw.polygon(surface, (75, 50, 8), [
            (hx, hat_y - int(hd * 1.0)), (hx - hw, hat_y), (hx + hw, hat_y)])
        pygame.draw.polygon(surface, (110, 80, 20), [
            (hx, hat_y - int(hd * 1.0)), (hx - hw, hat_y), (hx + hw, hat_y)], max(1, int(2*s)))
        # Hat band
        pygame.draw.line(surface, (50, 30, 5),
                         (hx - int(hd*0.85), hat_y - int(hd*0.4)),
                         (hx + int(hd*0.85), hat_y - int(hd*0.4)), max(2, int(3*s)))
        # Straw tufts sticking out from under hat
        for _st in range(5):
            _stx = hx - int(hd*0.8) + _st * int(hd*0.4)
            pygame.draw.line(surface, (190, 155, 40),
                             (_stx, hat_y + int(2*s)),
                             (_stx + int((_st-2)*3*s), hat_y + int(10*s)),
                             max(1, int(2*s)))
        # X eyes (stitched)
        for ex_off in [-int(hd*.38), int(hd*.38)]:
            ex, ey = hx + ex_off, hy - int(hd*.2)
            r = int(hd * .25)
            pygame.draw.line(surface, (40, 10, 5), (ex-r, ey-r), (ex+r, ey+r), max(2, int(3*s)))
            pygame.draw.line(surface, (40, 10, 5), (ex+r, ey-r), (ex-r, ey+r), max(2, int(3*s)))
        # Stitched mouth
        for _mi in range(4):
            _mx = hx - int(hd*0.4) + _mi * int(hd*0.28)
            pygame.draw.circle(surface, (40, 10, 5), (_mx, hy + int(hd*0.45)), max(1, int(2*s)))
        # Patched burlap shirt on torso
        pygame.draw.rect(surface, (160, 130, 50),
                         (sx - int(8*s), sy, int(16*s), bl),
                         max(1, int(2*s)), border_radius=max(1, int(2*s)))
        # Patch rectangle on chest
        pygame.draw.rect(surface, (120, 90, 30),
                         (sx - int(5*s), sy + int(bl*0.3), int(10*s), int(8*s)))
        # Straw sticking out from cuffs / collar
        for _ci in range(3):
            pygame.draw.line(surface, (190, 155, 40),
                             (sx - int(8*s), sy + int(3*s) + int(_ci*5*s)),
                             (sx - int(14*s), sy + int(6*s) + int(_ci*5*s)),
                             max(1, int(s)))

    elif char_name == "Cactus":
        # Green body fill (cactus torso)
        pygame.draw.rect(surface, (20, 130, 40),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (15, 100, 30),
                         (sx - int(8*s), sy, int(16*s), bl), max(1, int(2*s)), border_radius=max(3, int(5*s)))
        # Vertical ribs on cactus body
        pygame.draw.line(surface, (15, 100, 30),
                         (sx - int(3*s), sy + int(2*s)), (sx - int(3*s), wy - int(2*s)), max(1, int(s)))
        pygame.draw.line(surface, (15, 100, 30),
                         (sx + int(3*s), sy + int(2*s)), (sx + int(3*s), wy - int(2*s)), max(1, int(s)))
        # Body spines
        for _bsi in range(5):
            for _side2 in (-1, 1):
                _spy = sy + int(bl * (0.15 + _bsi * 0.18))
                pygame.draw.line(surface, (20, 140, 40),
                                 (sx + _side2*int(8*s), _spy),
                                 (sx + _side2*int(14*s), _spy - int(4*s)),
                                 max(1, int(2*s)))
        # Head spines
        for i in range(8):
            angle = math.radians(-120 + i * 35)
            spine_x = hx + int(math.cos(angle) * hd)
            spine_y = hy + int(math.sin(angle) * hd)
            tip_x = hx + int(math.cos(angle) * (hd + int(13*s)))
            tip_y = hy + int(math.sin(angle) * (hd + int(13*s)))
            pygame.draw.line(surface, (20, 140, 40), (spine_x, spine_y), (tip_x, tip_y), max(2, int(3*s)))
        # Flower on top of head
        for _fli in range(5):
            _fla = math.radians(90 + _fli * 72)
            pygame.draw.circle(surface, (255, 80, 200),
                               (hx + int(math.cos(_fla)*int(5*s)), hy - hd - int(4*s) + int(math.sin(_fla)*int(5*s))),
                               max(3, int(4*s)))
        pygame.draw.circle(surface, (255, 220, 0), (hx, hy - hd - int(4*s)), max(3, int(4*s)))

    elif char_name == "Medic":
        # White nurse/medic hat with red cross
        brim_y = hy - hd
        hw, hh = int(hd * 1.1), int(hd * 1.1)
        pygame.draw.rect(surface, WHITE, (hx - hw, brim_y - hh, hw*2, hh), border_radius=3)
        pygame.draw.rect(surface, (200, 200, 200), (hx - hw, brim_y - hh, hw*2, hh), max(1, int(2*s)), border_radius=3)
        pygame.draw.line(surface, WHITE, (hx - int(hw*1.3), brim_y), (hx + int(hw*1.3), brim_y), max(3, int(5*s)))
        cs = int(hd * .35)
        pygame.draw.line(surface, RED, (hx, brim_y - hh + int(hd*.18)), (hx, brim_y - int(hd*.2)), max(3, int(4*s)))
        pygame.draw.line(surface, RED, (hx - cs, brim_y - hh//2 - int(hd*.08)), (hx + cs, brim_y - hh//2 - int(hd*.08)), max(3, int(4*s)))
        # White coat lapels on torso
        for _lf in (-1, 1):
            pygame.draw.line(surface, (240, 240, 240),
                             (sx, sy + int(4*s)),
                             (sx + _lf*int(8*s), wy - int(4*s)), max(1, int(2*s)))
        # Red cross on chest
        _cx, _cy = sx, sy + int(bl * 0.38)
        pygame.draw.line(surface, RED, (_cx, _cy - int(6*s)), (_cx, _cy + int(6*s)), max(2, int(3*s)))
        pygame.draw.line(surface, RED, (_cx - int(6*s), _cy), (_cx + int(6*s), _cy), max(2, int(3*s)))
        # Medical bag/stethoscope hint at left hand
        pygame.draw.circle(surface, (200, 200, 200), (lhx, lhy), max(4, int(6*s)), max(1, int(2*s)))
        pygame.draw.line(surface, RED, (lhx - int(3*s), lhy), (lhx + int(3*s), lhy), max(1, int(2*s)))
        pygame.draw.line(surface, RED, (lhx, lhy - int(3*s)), (lhx, lhy + int(3*s)), max(1, int(2*s)))

    elif char_name == "Arsonist":
        # Flames on head
        for i in range(5):
            fx = hx + int((i - 2) * hd * .33)
            fh = int(hd * (.58 + (i % 2) * .5))
            fc = (255, 50, 0) if i % 2 == 0 else YELLOW
            pygame.draw.ellipse(surface, fc, (fx - int(hd*.17), hy - hd - fh, int(hd*.34), fh))
        # Burn-marked face: charred cheeks
        pygame.draw.circle(surface, (80, 40, 10), (hx - int(hd*0.5), hy + int(hd*0.15)), max(3, int(4*s)))
        pygame.draw.circle(surface, (80, 40, 10), (hx + int(hd*0.5), hy + int(hd*0.15)), max(3, int(4*s)))
        # Molotov bottle in forward hand
        bottle_base = (rhx + facing*int(4*s), rhy)
        bottle_tip = (rhx + facing*int(4*s), rhy - int(16*s))
        pygame.draw.rect(surface, (180, 130, 60),
                         (bottle_base[0] - int(4*s), bottle_tip[1],
                          int(8*s), int(16*s)), border_radius=max(2, int(3*s)))
        # Rag fuse on top
        pygame.draw.line(surface, (200, 120, 20),
                         bottle_tip, (bottle_tip[0] + facing*int(4*s), bottle_tip[1] - int(6*s)),
                         max(1, int(2*s)))
        pygame.draw.circle(surface, (255, 180, 0), (bottle_tip[0] + facing*int(4*s), bottle_tip[1] - int(6*s)),
                           max(2, int(3*s)))
        # Fire-resistant vest hint (charred dark patches on torso)
        pygame.draw.rect(surface, (50, 30, 10),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(2*s)), border_radius=max(1, int(2*s)))
        # Scorch marks on torso
        for _sci in range(3):
            pygame.draw.circle(surface, (60, 35, 5),
                               (sx + int((_sci-1)*6*s), sy + int(bl * (0.2 + _sci*0.3))),
                               max(3, int(4*s)))

    elif char_name == "Cryogenisist":
        # Ice spike crown
        for i in range(5):
            angle = math.radians(-90 + (i - 2) * 32)
            bx = hx + int(math.cos(angle) * hd * .85)
            by = hy + int(math.sin(angle) * hd * .85)
            tx = hx + int(math.cos(angle) * (hd + int(17*s)))
            ty = hy + int(math.sin(angle) * (hd + int(17*s)))
            pygame.draw.line(surface, (175, 225, 255), (bx, by), (tx, ty), max(2, int(4*s)))
            # Frost sparkle at spike tips
            pygame.draw.circle(surface, (220, 245, 255), (tx, ty), max(1, int(2*s)))
        # Frost-blue face with icy cheek crystals
        for _side in (-1, 1):
            pygame.draw.polygon(surface, (200, 235, 255), [
                (hx + _side*int(hd*0.55), hy - int(hd*0.2)),
                (hx + _side*int(hd*0.8), hy),
                (hx + _side*int(hd*0.55), hy + int(hd*0.2)),
            ])
        # Cryo armor on torso (icy blue plates)
        pygame.draw.rect(surface, (130, 195, 235),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (180, 230, 255),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Ice crack lines on armor
        pygame.draw.lines(surface, (220, 245, 255), False, [
            (sx - int(4*s), sy + int(bl*0.15)),
            (sx + int(2*s), sy + int(bl*0.4)),
            (sx - int(3*s), sy + int(bl*0.65)),
        ], max(1, int(s)))
        # Frost gloves on hands
        for _fx, _fy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (160, 220, 255), (_fx, _fy), max(4, int(7*s)))
            pygame.draw.circle(surface, (200, 240, 255), (_fx, _fy), max(4, int(7*s)), max(1, int(2*s)))

    elif char_name == "Magician":
        # Tall magician's top hat (filled)
        brim_y = hy - hd
        hw, hh = int(hd * 1.1), int(hd * 2.0)
        pygame.draw.polygon(surface, (95, 0, 195), [
            (hx, brim_y - hh), (hx - hw, brim_y), (hx + hw, brim_y)])
        pygame.draw.polygon(surface, (130, 30, 240), [
            (hx, brim_y - hh), (hx - hw, brim_y), (hx + hw, brim_y)], max(1, int(2*s)))
        # Hat brim
        pygame.draw.line(surface, (95, 0, 195), (hx - int(hw*1.4), brim_y), (hx + int(hw*1.4), brim_y), max(3, int(5*s)))
        # Hat band with sparkle
        pygame.draw.line(surface, (180, 120, 255),
                         (hx - int(hw*0.95), brim_y - int(hh*0.12)),
                         (hx + int(hw*0.95), brim_y - int(hh*0.12)), max(2, int(3*s)))
        # Star on hat
        pygame.draw.circle(surface, YELLOW, (hx, brim_y - int(hh*.55)), int(hd*.25))
        pygame.draw.circle(surface, (255, 255, 200), (hx, brim_y - int(hh*.55)), int(hd*.15))
        # Magic wand in forward hand
        wand_base = (rhx, rhy)
        wand_tip = (rhx + facing*int(22*s), rhy - int(12*s))
        pygame.draw.line(surface, (25, 20, 20), wand_base, wand_tip, max(2, int(3*s)))
        pygame.draw.circle(surface, WHITE, wand_tip, max(3, int(4*s)))
        # Magical sparkle dots around wand tip
        for _wsi in range(4):
            _wsa = math.radians(_wsi * 90 + pygame.time.get_ticks() * 0.3)
            pygame.draw.circle(surface, (220, 180, 255),
                               (wand_tip[0] + int(math.cos(_wsa)*5*s), wand_tip[1] + int(math.sin(_wsa)*5*s)),
                               max(1, int(2*s)))
        # Tuxedo vest on torso
        pygame.draw.rect(surface, (20, 15, 40),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=max(1, int(2*s)))
        # White shirt front
        pygame.draw.polygon(surface, (240, 240, 250), [
            (sx - int(4*s), sy + int(4*s)), (sx + int(4*s), sy + int(4*s)),
            (sx + int(3*s), sy + int(bl*0.6)), (sx - int(3*s), sy + int(bl*0.6))
        ])

    elif char_name == "Charger":
        # Large lightning bolt on chest (filled polygon)
        mid_x = sx + int(facing * 2 * s)
        mid_y = (sy + wy) // 2
        bolt_pts = [
            (mid_x + int(7*s), sy + int(4*s)),
            (mid_x - int(4*s), mid_y),
            (mid_x + int(4*s), mid_y),
            (mid_x - int(7*s), wy - int(4*s)),
        ]
        pygame.draw.lines(surface, YELLOW, False, bolt_pts, max(3, int(4*s)))
        pygame.draw.lines(surface, (255, 240, 120), False, bolt_pts, max(1, int(2*s)))
        # Electric arc shoulder pads
        for _side in (-1, 1):
            _sx2 = sx + _side * int(8*s)
            for _ai in range(3):
                _aa = math.radians(90 + _side * (30 + _ai * 20))
                pygame.draw.line(surface, (200, 230, 255),
                                 (_sx2, sy),
                                 (_sx2 + int(math.cos(_aa)*10*s), sy + int(math.sin(_aa)*8*s)),
                                 max(1, int(s)))
        # Sparks at fists
        for _fx, _fy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (255, 230, 60), (_fx, _fy), max(4, int(6*s)))
            pygame.draw.circle(surface, (255, 255, 180), (_fx, _fy), max(2, int(3*s)))
        # Speed visor line across eyes
        pygame.draw.rect(surface, (255, 240, 0),
                         (hx - int(hd*0.8), hy - int(hd*0.15), int(hd*1.6), int(hd*0.3)),
                         max(1, int(2*s)))

    elif char_name == "Psychopath":
        # Knife blade and handle
        pygame.draw.line(surface, (195, 195, 215), (rhx, rhy), (rhx + facing*int(22*s), rhy - int(10*s)), max(2, int(3*s)))
        # Blood-red edge on blade back
        pygame.draw.line(surface, (180, 20, 20),
                         (rhx, rhy - int(2*s)),
                         (rhx + facing*int(22*s), rhy - int(12*s)), max(1, int(s)))
        # Handle with wrapping
        pygame.draw.line(surface, (60, 30, 10), (rhx, rhy), (rhx - facing*int(8*s), rhy + int(5*s)), max(3, int(5*s)))
        for _wi in range(3):
            _wx = rhx - facing*int((2 + _wi*2)*s)
            _wy2 = rhy + int(_wi*2*s)
            pygame.draw.line(surface, (90, 55, 20),
                             (_wx - int(2*s), _wy2), (_wx + int(2*s), _wy2), max(1, int(s)))
        # Deranged X eyes
        for _exoff in (-int(hd*0.38), int(hd*0.38)):
            _ex, _ey = hx + _exoff, hy - int(hd*0.1)
            _er = max(2, int(4*s))
            pygame.draw.line(surface, (180, 0, 0), (_ex-_er, _ey-_er), (_ex+_er, _ey+_er), max(1, int(2*s)))
            pygame.draw.line(surface, (180, 0, 0), (_ex+_er, _ey-_er), (_ex-_er, _ey+_er), max(1, int(2*s)))
        # Messy hair spikes
        for _hi2 in range(4):
            _ha2 = math.radians(120 - _hi2 * 40)
            pygame.draw.line(surface, (40, 20, 0),
                             (hx + int(math.cos(_ha2)*hd*0.85), hy - int(math.sin(_ha2)*hd*0.85)),
                             (hx + int(math.cos(_ha2)*hd*1.4), hy - int(math.sin(_ha2)*hd*1.4)),
                             max(1, int(2*s)))
        # Blood splatters on torso
        for _bi in range(3):
            pygame.draw.circle(surface, (160, 0, 0),
                               (sx + int((_bi - 1)*8*s), sy + int(bl * (0.2 + _bi*0.3))),
                               max(2, int(3*s)))

    elif char_name == "Ran-Doom":
        # Dice on head: draw dots (five-face showing)
        die_size = int(hd * .9)
        die_x = hx - die_size // 2
        die_y = hy - hd - die_size - int(4*s)
        pygame.draw.rect(surface, (230, 225, 215), (die_x, die_y, die_size, die_size), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 60, 60), (die_x, die_y, die_size, die_size), max(1, int(2*s)), border_radius=max(2, int(3*s)))
        for dx, dy in [(die_size//4, die_size//4), (die_size*3//4, die_size//4),
                       (die_size//2, die_size//2),
                       (die_size//4, die_size*3//4), (die_size*3//4, die_size*3//4)]:
            pygame.draw.circle(surface, (20, 20, 20), (die_x + dx, die_y + dy), max(2, int(3*s)))
        # Second small die floating at shoulder
        _d2s = int(die_size * 0.6)
        _d2x = hx + hd + int(3*s)
        _d2y = hy - int(hd*0.5)
        pygame.draw.rect(surface, (255, 200, 60), (_d2x, _d2y, _d2s, _d2s), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (180, 120, 0), (_d2x, _d2y, _d2s, _d2s), max(1, int(s)), border_radius=max(1, int(2*s)))
        pygame.draw.circle(surface, (100, 50, 0), (_d2x + _d2s//2, _d2y + _d2s//2), max(2, int(3*s)))
        # Chaotic question marks orbiting body
        t_rd = pygame.time.get_ticks()
        for _qi in range(3):
            _qa = math.radians(_qi * 120 + t_rd * 0.15)
            _qx = hx + int(math.cos(_qa) * hd * 2.0)
            _qy = wy - int(hd) + int(math.sin(_qa) * int(hd * 0.8))
            _qf2 = _get_font(max(8, int(11*s)))
            _qt3 = _qf2.render("?", True, (255, 60, 60) if _qi == 0 else (60, 200, 255) if _qi == 1 else (255, 200, 0))
            surface.blit(_qt3, (_qx - _qt3.get_width()//2, _qy - _qt3.get_height()//2))
        # Jester-like collar (random colors)
        for _ci2 in range(4):
            _cx4 = sx - int(6*s) + _ci2 * int(4*s)
            _cc = [(255,60,0),(0,180,255),(255,200,0),(180,0,255)][_ci2]
            pygame.draw.circle(surface, _cc, (_cx4, sy + int(3*s)), max(3, int(4*s)))

    elif char_name == "Outbacker":
        # Wide Australian bush hat (full shape)
        brim_y = hy - hd
        hw, hh = int(hd * 1.8), int(hd * .9)
        # Hat crown
        pygame.draw.ellipse(surface, (155, 95, 25), (hx - int(hw*.6), brim_y - hh, int(hw*1.2), hh))
        pygame.draw.ellipse(surface, (115, 65, 10), (hx - int(hw*.6), brim_y - hh, int(hw*1.2), hh), max(1, int(2*s)))
        # Chin-side brim (upturned on one side, drooping on other)
        pygame.draw.arc(surface, (130, 75, 15), (hx - hw, brim_y - int(hd*.4), hw*2, int(hd*.6)),
                        math.radians(200), math.radians(340), max(3, int(5*s)))
        # Hat band
        pygame.draw.line(surface, (90, 50, 5),
                         (hx - int(hw*0.58), brim_y - int(3*s)),
                         (hx + int(hw*0.58), brim_y - int(3*s)), max(2, int(3*s)))
        # Hat tooth-cord (cork) dangling from brim
        pygame.draw.line(surface, (130, 100, 50),
                         (hx + int(hw*0.5), brim_y),
                         (hx + int(hw*0.5) + int(4*s), brim_y + int(8*s)), max(1, int(s)))
        pygame.draw.circle(surface, (200, 170, 100), (hx + int(hw*0.5) + int(4*s), brim_y + int(8*s)), max(2, int(3*s)))
        # Sunburned tan face: redder cheeks
        pygame.draw.circle(surface, (210, 140, 80), (hx + facing*int(hd*0.5), hy + int(hd*0.25)),
                           max(2, int(4*s)))
        # Flannel plaid shirt hint on torso
        for _fi in range(3):
            _fy = sy + int(bl * (0.2 + _fi * 0.3))
            pygame.draw.line(surface, (180, 80, 40),
                             (sx - int(8*s), _fy), (sx + int(8*s), _fy), max(1, int(2*s)))
        # Boomerang on belt
        pygame.draw.arc(surface, (200, 120, 40),
                        (wx + facing*int(3*s), wy - int(8*s), int(16*s), int(10*s)),
                        0, math.pi, max(2, int(3*s)))

    elif char_name == "Gunner":
        # Pistol at forward hand — detailed
        gx1, gy1 = rhx, rhy
        bx = gx1 + facing * int(22*s)
        pygame.draw.rect(surface, (45, 45, 45),
                         (min(gx1, bx) - 2, gy1 - int(4*s), int(26*s), int(8*s)),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (70, 70, 70),
                         (min(gx1, bx) - 2, gy1 - int(4*s), int(26*s), int(8*s)),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Grip
        pygame.draw.rect(surface, (65, 45, 25),
                         (gx1 - facing*int(4*s), gy1, int(8*s), int(12*s)),
                         border_radius=max(1, int(2*s)))
        # Barrel tip with muzzle flash hint
        pygame.draw.circle(surface, (80, 80, 80), (bx, gy1), max(2, int(3*s)))
        # Holster on thigh area
        _hx2 = wx + facing*int(8*s)
        pygame.draw.rect(surface, (55, 35, 15),
                         (_hx2 - int(4*s), wy, int(8*s), int(12*s)),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (75, 50, 25),
                         (_hx2 - int(4*s), wy, int(8*s), int(12*s)),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Tactical vest outline on torso
        pygame.draw.rect(surface, (55, 55, 65),
                         (sx - int(9*s), sy, int(18*s), bl),
                         max(1, int(2*s)), border_radius=max(1, int(2*s)))
        # Vest pocket straps
        pygame.draw.line(surface, (40, 40, 50),
                         (sx - int(8*s), sy + int(bl*0.3)), (sx + int(8*s), sy + int(bl*0.3)),
                         max(1, int(s)))
        # Tactical cap / beret on head
        pygame.draw.ellipse(surface, (40, 40, 50),
                            (hx - int(hd*1.1), hy - hd - int(hd*0.45), int(hd*2.2), int(hd*0.55)))
        pygame.draw.circle(surface, (40, 40, 50), (hx + facing*int(hd*0.2), hy - hd - int(hd*0.35)),
                           int(hd*0.45))

    elif char_name == "Bazooka Man":
        # Bazooka tube on shoulder — wide thick barrel
        baz_x1 = sx - facing * int(5*s)
        baz_x2 = baz_x1 + facing * int(60*s)
        baz_y = sy + int(5*s)
        pygame.draw.line(surface, (60, 65, 60), (baz_x1, baz_y), (baz_x2, baz_y), max(6, int(10*s)))
        pygame.draw.line(surface, (90, 95, 90), (baz_x1, baz_y - max(2,int(3*s))), (baz_x2, baz_y - max(2,int(3*s))), max(1, int(2*s)))
        # Muzzle ring at tip
        pygame.draw.circle(surface, (40, 40, 40), (baz_x2, baz_y), max(5, int(7*s)))
        pygame.draw.circle(surface, (80, 80, 80), (baz_x2, baz_y), max(5, int(7*s)), max(1, int(2*s)))
        # Exhaust vent at rear
        pygame.draw.circle(surface, (50, 50, 50), (baz_x1, baz_y), max(4, int(6*s)))
        pygame.draw.circle(surface, (120, 100, 60), (baz_x1, baz_y), max(4, int(6*s)), max(1, int(2*s)))
        # Grip / trigger guard below tube
        pygame.draw.line(surface, (70, 50, 20), (baz_x1 + facing*int(14*s), baz_y),
                         (baz_x1 + facing*int(14*s), baz_y + int(12*s)), max(3, int(5*s)))
        pygame.draw.arc(surface, (70, 50, 20),
                        (baz_x1 + facing*int(9*s), baz_y + int(8*s), int(10*s), int(8*s)),
                        math.radians(0), math.radians(180), max(2, int(2*s)))
        # Military helmet on head
        pygame.draw.ellipse(surface, (55, 75, 45),
                            (hx - int(hd*1.15), hy - hd - int(hd*0.8), int(hd*2.3), int(hd*1.0)))
        pygame.draw.ellipse(surface, (40, 55, 30),
                            (hx - int(hd*1.15), hy - hd - int(hd*0.8), int(hd*2.3), int(hd*1.0)),
                            max(1, int(2*s)))
        # Helmet brim
        pygame.draw.line(surface, (40, 55, 30),
                         (hx - int(hd*1.2), hy - int(hd*0.25)),
                         (hx + int(hd*1.2), hy - int(hd*0.25)), max(2, int(3*s)))
        # Combat vest lines
        pygame.draw.rect(surface, (55, 70, 45),
                         (sx - int(8*s), sy + int(4*s), int(16*s), int(bl*0.65)),
                         max(1, int(2*s)), border_radius=max(1, int(2*s)))

    elif char_name == "Pinball":
        # Shiny metallic sphere on chest
        mid_y = (sy + wy) // 2
        pygame.draw.circle(surface, (220, 60, 180), (sx, mid_y), max(8, int(hd * .44)))
        pygame.draw.circle(surface, (255, 130, 220), (sx, mid_y), max(8, int(hd * .44)), max(1, int(2*s)))
        # Shine highlight on the ball
        pygame.draw.circle(surface, (255, 240, 255),
                           (sx - max(2, int(3*s)), mid_y - max(2, int(3*s))),
                           max(2, int(3*s)))
        # Bounce trail dots orbiting the ball
        for _pi in range(4):
            _pa = math.radians(_pi * 90 + pygame.time.get_ticks() * 0.25)
            _pr2 = max(7, int(hd * .55))
            pygame.draw.circle(surface, (255, 180, 240),
                               (sx + int(math.cos(_pa)*_pr2), mid_y + int(math.sin(_pa)*_pr2)),
                               max(1, int(2*s)))
        # Flipper arms: bright pink horizontal bars at shoulder height
        pygame.draw.rect(surface, (255, 60, 180),
                         (sx - int(hd*1.2), sy - int(2*s), int(hd*2.4), max(3, int(5*s))),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (255, 180, 230),
                         (sx - int(hd*1.2), sy - int(2*s), int(hd*2.4), max(3, int(5*s))),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Stars on head
        for _bsi in range(3):
            _bsa = math.radians(-60 + _bsi * 60)
            _bsx = hx + int(math.cos(_bsa) * hd * 1.2)
            _bsy = hy - int(math.sin(_bsa) * hd * 0.8)
            pygame.draw.circle(surface, (255, 220, 80), (_bsx, _bsy), max(2, int(3*s)))

    elif char_name == "Giant":
        # Royal cloak on torso (oversized to suggest bulk)
        pygame.draw.rect(surface, (120, 20, 20),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (160, 40, 40),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Ermine trim at collar
        pygame.draw.line(surface, (240, 240, 240),
                         (sx - int(11*s), sy + int(2*s)), (sx + int(11*s), sy + int(2*s)), max(2, int(3*s)))
        # Gem jewels on cloak
        for _gi2 in range(3):
            pygame.draw.circle(surface, (200, 0, 200),
                               (sx + int((_gi2-1)*6*s), sy + int(bl*0.4)), max(3, int(4*s)))
            pygame.draw.circle(surface, (255, 100, 255),
                               (sx + int((_gi2-1)*6*s), sy + int(bl*0.4)), max(1, int(2*s)))
        # Oversized meaty fists
        for _gfx, _gfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (200, 150, 100), (_gfx, _gfy), max(6, int(11*s)))
            pygame.draw.circle(surface, (170, 120, 80), (_gfx, _gfy), max(6, int(11*s)), max(1, int(2*s)))
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
        # Crown jewels
        for _cji, _cjx in enumerate([hx - int(hd*0.5), hx, hx + int(hd*0.5)]):
            _cjcol = [(255,0,0),(0,200,255),(0,255,0)][_cji]
            pygame.draw.circle(surface, _cjcol, (_cjx, ct + int(hd*0.85)), max(2, int(3*s)))

    elif char_name == "Morph":
        # Double-ended resize arrows on chest
        mid_y = (sy + wy) // 2
        arr = int(20 * s)
        pygame.draw.line(surface, CYAN, (sx - arr, mid_y), (sx + arr, mid_y), max(2, int(3*s)))
        for dx in [-arr, arr]:
            sign = 1 if dx > 0 else -1
            pygame.draw.line(surface, CYAN, (sx + dx, mid_y), (sx + dx - sign*int(6*s), mid_y - int(5*s)), max(2, int(3*s)))
            pygame.draw.line(surface, CYAN, (sx + dx, mid_y), (sx + dx - sign*int(6*s), mid_y + int(5*s)), max(2, int(3*s)))
        # Morph aura — shimmering outline around head (cyan rings)
        for _mr in [hd + int(3*s), hd + int(7*s)]:
            pygame.draw.circle(surface, (0, 200, 220), (hx, hy), _mr, max(1, int(s)))
        # Size indicator marks up/down on torso
        pygame.draw.line(surface, (0, 240, 240),
                         (sx, sy + int(4*s)), (sx, mid_y - int(4*s)), max(1, int(s)))
        pygame.draw.line(surface, (0, 240, 240),
                         (sx, mid_y + int(4*s)), (sx, wy - int(4*s)), max(1, int(s)))
        # Geometric eye shapes
        for _eox in (-int(hd*0.35), int(hd*0.35)):
            pygame.draw.ellipse(surface, (0, 255, 240),
                                (hx + _eox - int(4*s), hy - int(4*s), int(8*s), int(8*s)),
                                max(1, int(2*s)))

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
        # Rope looped from hip to hand
        pygame.draw.line(surface, (130, 92, 42), (sx + facing*int(4*s), wy - int(4*s)), (rhx, rhy), max(2, int(3*s)))
        # Hook at forward hand — curved with point
        pygame.draw.arc(surface, (175, 175, 195),
                        (rhx + facing*int(2*s), rhy - int(10*s), int(16*s), int(16*s)),
                        math.radians(0), math.radians(270), max(2, int(4*s)))
        # Hook tip
        pygame.draw.line(surface, (175, 175, 195),
                         (rhx + facing*int(2*s), rhy + int(5*s)),
                         (rhx + facing*int(8*s), rhy + int(8*s)), max(2, int(3*s)))
        # Rope coil on hip
        for _ri in range(3):
            pygame.draw.circle(surface, (110 + _ri*10, 75 + _ri*5, 30 + _ri*4),
                               (sx + facing*int(4*s), wy - int(4*s) + int(_ri*3*s)),
                               max(2, int((5 - _ri)*s)), max(1, int(s)))
        # Captain's cap (short brimmed hat)
        pygame.draw.rect(surface, (30, 30, 80),
                         (hx - int(hd*0.8), hy - hd - int(hd*0.6), int(hd*1.6), int(hd*0.6)))
        pygame.draw.line(surface, (30, 30, 80),
                         (hx - int(hd*1.1), hy - hd - int(2*s)),
                         (hx + int(hd*1.1), hy - hd - int(2*s)), max(3, int(4*s)))
        # Anchor tattoo hint on arm
        _ax2, _ay2 = (rhx + sx) // 2, (rhy + sy) // 2
        pygame.draw.circle(surface, (60, 80, 140), (_ax2, _ay2), max(3, int(4*s)), max(1, int(s)))

    elif char_name == "Mouse":
        # Round mouse ears on top of head
        for ex_off in [-int(hd*.72), int(hd*.72)]:
            pygame.draw.circle(surface, col, (hx + ex_off, hy - int(hd*1.02)), int(hd*.56))
            pygame.draw.circle(surface, (225, 165, 155), (hx + ex_off, hy - int(hd*1.02)), int(hd*.3))
        # Whiskers on face
        for _ws in range(3):
            _wy4 = hy + int(hd*0.25) + _ws*int(hd*0.18)
            # Left whiskers
            pygame.draw.line(surface, (180, 160, 150),
                             (hx - int(hd*0.15), _wy4),
                             (hx - int(hd*1.0), _wy4 - int((_ws-1)*3*s)), max(1, int(s)))
            # Right whiskers
            pygame.draw.line(surface, (180, 160, 150),
                             (hx + int(hd*0.15), _wy4),
                             (hx + int(hd*1.0), _wy4 - int((_ws-1)*3*s)), max(1, int(s)))
        # Pink nose on face
        pygame.draw.circle(surface, (255, 160, 160), (hx, hy + int(hd*0.22)), max(2, int(3*s)))
        # Beady eyes
        for _eox in (-int(hd*0.35), int(hd*0.35)):
            pygame.draw.circle(surface, (20, 10, 30), (hx + _eox, hy - int(hd*0.15)), max(2, int(3*s)))
            pygame.draw.circle(surface, (80, 40, 80), (hx + _eox, hy - int(hd*0.15)), max(1, int(s)))
        # Cheese wedge on chest (yellow triangle)
        pygame.draw.polygon(surface, (240, 210, 30), [
            (sx - int(8*s), sy + int(bl*0.55)),
            (sx + int(8*s), sy + int(bl*0.55)),
            (sx, sy + int(bl*0.2))
        ])
        pygame.draw.polygon(surface, (200, 165, 0), [
            (sx - int(8*s), sy + int(bl*0.55)),
            (sx + int(8*s), sy + int(bl*0.55)),
            (sx, sy + int(bl*0.2))
        ], max(1, int(s)))
        # Cheese holes
        for _chx, _chy in [(sx - int(3*s), sy + int(bl*0.42)), (sx + int(3*s), sy + int(bl*0.38))]:
            pygame.draw.circle(surface, (180, 145, 0), (_chx, _chy), max(1, int(2*s)))
        # Curly tail from waist
        for _ti3 in range(4):
            _ta = math.radians(90 + _ti3 * 60)
            _tr = int((3 + _ti3 * 3) * s)
            pygame.draw.circle(surface, (200, 160, 150),
                               (wx - facing*int(6*s) + int(math.cos(_ta)*_tr),
                                wy + int(4*s) + int(math.sin(_ta)*_tr)),
                               max(1, int(2*s)))

    elif char_name == "Sumo":
        # Topknot with tied paper cord
        pygame.draw.ellipse(surface, (35, 20, 5), (hx - int(hd*.38), hy - int(hd*1.55), int(hd*.76), int(hd*.65)))
        pygame.draw.ellipse(surface, (65, 40, 15), (hx - int(hd*.38), hy - int(hd*1.55), int(hd*.76), int(hd*.65)), max(1, int(s)))
        # Cord tying the topknot
        pygame.draw.line(surface, (240, 220, 180),
                         (hx - int(hd*0.22), hy - int(hd*1.2)),
                         (hx + int(hd*0.22), hy - int(hd*1.2)), max(1, int(2*s)))
        # Mawashi belt at waist (thick, detailed)
        bh = max(5, int(10*s))
        pygame.draw.rect(surface, (195, 148, 48), (wx - int(hd*.95), wy - bh//2, int(hd*1.9), bh),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (175, 118, 18), (wx - int(hd*.95), wy - bh//2, int(hd*1.9), bh),
                         2, border_radius=max(1, int(2*s)))
        # Belt center knot (thick front fold)
        pygame.draw.rect(surface, (210, 165, 60),
                         (wx - int(hd*0.28), wy - bh//2 - int(2*s), int(hd*0.56), bh + int(4*s)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (175, 118, 18),
                         (wx - int(hd*0.28), wy - bh//2 - int(2*s), int(hd*0.56), bh + int(4*s)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Big round body shading (sumo roundness hint)
        pygame.draw.ellipse(surface, col,
                            (sx - int(13*s), sy - int(2*s), int(26*s), bl + int(4*s)))
        # Chubby cheek marks
        for _side in (-1, 1):
            pygame.draw.circle(surface, (220, 160, 120),
                               (hx + _side * int(hd * 0.55), hy + int(hd * 0.25)), max(3, int(4*s)))
        # Determined eyebrows
        for _eox in (-int(hd*0.5), int(hd*0.5)):
            _sign = 1 if _eox < 0 else -1
            pygame.draw.line(surface, (30, 20, 5),
                             (hx + _eox - _sign*int(4*s), hy - int(hd*0.45)),
                             (hx + _eox + _sign*int(2*s), hy - int(hd*0.28)),
                             max(2, int(3*s)))

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
        # Aerodynamic speed helmet
        pygame.draw.ellipse(surface, (30, 30, 50),
                            (hx - int(hd*1.1), hy - hd - int(hd*0.7), int(hd*2.2), int(hd*0.9)))
        pygame.draw.ellipse(surface, (20, 20, 40),
                            (hx - int(hd*1.1), hy - hd - int(hd*0.7), int(hd*2.2), int(hd*0.9)),
                            max(1, int(2*s)))
        # Visor across head
        pygame.draw.ellipse(surface, (40, 40, 60),
                            (hx - hd - int(2*s), hy - int(6*s), int(hd*2 + 4*s), int(10*s)))
        pygame.draw.ellipse(surface, (100, 200, 255),
                            (hx - hd, hy - int(5*s), hd*2, int(8*s)), max(1, int(2*s)))
        # Lightning bolt on chest (filled)
        bolt = [(sx + facing*int(3*s), sy + int(6*s)),
                (sx - facing*int(2*s), sy + int(20*s)),
                (sx + facing*int(6*s), sy + int(20*s)),
                (sx - facing*int(3*s), sy + int(36*s))]
        pygame.draw.lines(surface, (255, 230, 0), False, bolt, max(2, int(3*s)))
        # Speed suit on torso (sleek form-fitting)
        pygame.draw.rect(surface, (20, 25, 50),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (40, 50, 90),
                         (sx - int(8*s), sy, int(16*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Speed stripes on suit sides
        for _ssside in (-1, 1):
            pygame.draw.line(surface, (80, 130, 255),
                             (sx + _ssside*int(7*s), sy + int(2*s)),
                             (sx + _ssside*int(7*s), wy - int(2*s)), max(1, int(2*s)))
        # Speed blur streaks trailing behind
        for _ssi in range(4):
            pygame.draw.line(surface, (100, 200, 255),
                             (sx - facing*int((5 + _ssi*6)*s), sy + int(bl*0.2*(_ssi+1))),
                             (sx - facing*int((12 + _ssi*6)*s), sy + int(bl*0.2*(_ssi+1)) - int(3*s)),
                             max(1, int(s)))

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
        # Wings behind torso (filled polygons, drawn first)
        for side in (-1, 1):
            wing_pts = [
                (sx, sy + int(8*s)),
                (sx + side*int(55*s), sy - int(15*s)),
                (sx + side*int(65*s), sy + int(20*s)),
                (sx + side*int(40*s), sy + int(40*s)),
                (sx + side*int(15*s), sy + int(22*s)),
            ]
            pygame.draw.polygon(surface, (250, 248, 240), wing_pts)
            pygame.draw.polygon(surface, (220, 215, 200), wing_pts, max(1, int(2*s)))
        # White robe on torso
        pygame.draw.rect(surface, (250, 250, 245),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (220, 215, 205),
                         (sx - int(8*s), sy, int(16*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Gold belt sash
        pygame.draw.rect(surface, (230, 200, 20),
                         (sx - int(9*s), wy - int(4*s), int(18*s), int(7*s)))
        pygame.draw.rect(surface, (190, 160, 0),
                         (sx - int(9*s), wy - int(4*s), int(18*s), int(7*s)), max(1, int(s)))
        # Wing arc details (feather layers)
        for side in (-1, 1):
            wx1 = sx + side * int(hd*0.5)
            wy1 = sy + int(6*s)
            pygame.draw.arc(surface, (255, 250, 230),
                            (wx1 + side*int(4*s) - int(30*s), wy1 - int(30*s), int(36*s), int(44*s)),
                            math.radians(200 if side == 1 else -20),
                            math.radians(340 if side == 1 else 160),
                            max(2, int(4*s)))
        # Golden halo
        pygame.draw.ellipse(surface, (255, 240, 100),
                            (hx - int(hd*1.1), hy - hd - int(18*s), int(hd*2.2), int(10*s)), max(3, int(4*s)))
        pygame.draw.ellipse(surface, (255, 255, 160),
                            (hx - int(hd*1.1), hy - hd - int(18*s), int(hd*2.2), int(10*s)), max(1, int(2*s)))
        # Peaceful expression: smile
        pygame.draw.arc(surface, (200, 160, 140),
                        (hx - int(hd*0.45), hy + int(hd*0.15), int(hd*0.9), int(hd*0.55)),
                        math.radians(0), math.radians(180), max(1, int(2*s)))

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
        hip_x = wx + int(facing * int(8*s))
        hip_y = wy
        for i in range(4):
            r_loop = max(2, int((10 - i * 2) * s))
            _wpc = (110 + i * 10, 60 + i * 5, 15 + i * 3)
            pygame.draw.circle(surface, _wpc, (hip_x, hip_y + int(i * 2 * s)), r_loop, max(1, int(2 * s)))
        # Short dangling tip
        tip_x = hip_x + int(facing * 8 * s)
        tip_y = hip_y + int(12 * s)
        pygame.draw.line(surface, (140, 80, 25),
                         (hip_x, hip_y + int(6 * s)), (tip_x, tip_y), max(1, int(2 * s)))
        # Uncoiled whip crack in forward hand (S-curve)
        for _wi2 in range(5):
            _wt1 = _wi2 / 5.0
            _wt2 = (_wi2 + 1) / 5.0
            _wx3 = rhx + int(facing * _wt1 * 45 * s)
            _wy5 = rhy + int(math.sin(_wt1 * math.pi * 2) * 8 * s)
            _wx4 = rhx + int(facing * _wt2 * 45 * s)
            _wy6 = rhy + int(math.sin(_wt2 * math.pi * 2) * 8 * s)
            pygame.draw.line(surface, (120 + _wi2*10, 65, 15),
                             (_wx3, _wy5), (_wx4, _wy6), max(1, int((3 - _wi2//2)*s)))
        # Leather duster coat on torso
        pygame.draw.rect(surface, (70, 40, 15),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (100, 60, 25),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Wide-brim cowboy hat
        _cbrim = hy - hd
        pygame.draw.ellipse(surface, (55, 35, 10),
                            (hx - int(hd*1.6), _cbrim - int(2*s), int(hd*3.2), int(hd*0.5)))
        pygame.draw.rect(surface, (55, 35, 10),
                         (hx - int(hd*0.85), _cbrim - int(hd*0.9), int(hd*1.7), int(hd*0.9)))
        pygame.draw.rect(surface, (80, 55, 20),
                         (hx - int(hd*0.85), _cbrim - int(hd*0.9), int(hd*1.7), int(hd*0.9)), max(1, int(s)))

    elif char_name == "Laser Eyes":
        # Pulsing laser eyes
        t = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(t * 0.008)
        r1 = max(3, int((5 + 3 * pulse) * s))
        for eye_ox in (-int(hd * 0.38), int(hd * 0.38)):
            ex, ey = hx + eye_ox, hy - int(hd * 0.1)
            pygame.draw.circle(surface, (255, int(40 + 40 * pulse), 0), (ex, ey), r1)
            pygame.draw.circle(surface, (255, 220, 80), (ex, ey), max(1, r1 - 2))
            # Laser beams shooting forward
            pygame.draw.line(surface, (255, int(60 + 60*pulse), 0),
                             (ex, ey),
                             (ex + facing*int(hd*2.5), ey), max(1, int(2*s)))
        # Tactical visor frame around eyes
        pygame.draw.rect(surface, (60, 60, 80),
                         (hx - int(hd*0.9), hy - int(hd*0.35), int(hd*1.8), int(hd*0.5)),
                         max(1, int(2*s)), border_radius=max(1, int(2*s)))
        # Tech-armor shoulder pads
        for _side in (-1, 1):
            pygame.draw.rect(surface, (50, 55, 70),
                             (sx + _side*int(3*s), sy - int(4*s), int(12*s), int(8*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (80, 85, 110),
                             (sx + _side*int(3*s), sy - int(4*s), int(12*s), int(8*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Red chest emblem (eye symbol)
        pygame.draw.ellipse(surface, (220, 40, 0),
                            (sx - int(6*s), sy + int(bl*0.35) - int(3*s), int(12*s), int(6*s)))
        pygame.draw.ellipse(surface, (255, 160, 0),
                            (sx - int(6*s), sy + int(bl*0.35) - int(3*s), int(12*s), int(6*s)),
                            max(1, int(s)))
        pygame.draw.circle(surface, (255, 60, 0),
                           (sx, sy + int(bl*0.35)), max(2, int(3*s)))

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
        # Sumo-style big belly body
        pygame.draw.ellipse(surface, col,
                            (sx - int(14*s), sy - int(2*s), int(28*s), bl + int(6*s)))
        # Mawashi belt
        bh_o = max(5, int(9*s))
        pygame.draw.rect(surface, (30, 60, 220), (wx - int(hd*.9), wy - bh_o//2, int(hd*1.8), bh_o))
        pygame.draw.rect(surface, (60, 100, 255), (wx - int(hd*.9), wy - bh_o//2, int(hd*1.8), bh_o), max(1, int(s)))
        # Belt buckle
        pygame.draw.rect(surface, (150, 200, 255),
                         (wx - int(4*s), wy - bh_o//2, int(8*s), bh_o), border_radius=max(1, int(s)))
        # Spiked hair + lightning bolt on head
        pygame.draw.line(surface, (30, 80, 255), (hx, hy - hd), (hx, hy - int(hd * 1.9)), max(3, int(4 * s)))
        pygame.draw.line(surface, (30, 80, 255), (hx - int(hd * 0.4), hy - int(hd * 1.5)),
                         (hx + int(hd * 0.4), hy - int(hd * 1.5)), max(2, int(3 * s)))
        # Lightning bolt on chest (filled)
        bolt = [(sx + int(facing * 4 * s), sy + int(4 * s)),
                (sx - int(facing * 4 * s), sy + int(14 * s)),
                (sx + int(facing * 2 * s), sy + int(14 * s)),
                (sx - int(facing * 4 * s), sy + int(24 * s))]
        pygame.draw.lines(surface, (100, 160, 255), False, bolt, max(2, int(3 * s)))
        # War paint / intimidation lines on cheeks
        for _side in (-1, 1):
            pygame.draw.line(surface, (30, 60, 200),
                             (hx + _side*int(hd*0.55), hy - int(hd*0.2)),
                             (hx + _side*int(hd*0.75), hy + int(hd*0.3)), max(2, int(3*s)))

    elif char_name == "The Creator":
        # Construction hard hat (yellow)
        hat_w = int(hd * 2.2)
        hat_h = int(hd * 0.65)
        pygame.draw.ellipse(surface, (240, 200, 20),
                            (hx - hat_w // 2, hy - hd - hat_h + int(3 * s), hat_w, hat_h))
        pygame.draw.ellipse(surface, (180, 140, 10),
                            (hx - hat_w // 2, hy - hd - hat_h + int(3 * s), hat_w, hat_h), max(1, int(2*s)))
        pygame.draw.rect(surface, (240, 200, 20),
                         (hx - int(hat_w * 0.55), hy - hd - int(4 * s), int(hat_w * 1.1), int(5 * s)))
        pygame.draw.rect(surface, (180, 140, 10),
                         (hx - int(hat_w * 0.55), hy - hd - int(4 * s), int(hat_w * 1.1), int(5 * s)), 1)
        # Hi-vis vest on torso
        pygame.draw.rect(surface, (255, 150, 0),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (200, 110, 0),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Reflective strips on vest
        for _rsi2 in range(2):
            _rsy = sy + int(bl * (0.3 + _rsi2 * 0.4))
            pygame.draw.line(surface, (230, 230, 180),
                             (sx - int(8*s), _rsy), (sx + int(8*s), _rsy), max(2, int(3*s)))
        # Blueprint / plan roll on left hand
        pygame.draw.rect(surface, (180, 200, 220),
                         (lhx - int(4*s), lhy - int(10*s), int(8*s), int(14*s)),
                         border_radius=max(1, int(2*s)))
        pygame.draw.line(surface, (100, 140, 180),
                         (lhx - int(3*s), lhy - int(8*s)), (lhx + int(3*s), lhy - int(3*s)),
                         max(1, int(s)))
        # Block held in forward hand (building block)
        bsz = max(6, int(12 * s))
        pygame.draw.rect(surface, (180, 120, 50), (rhx - bsz // 2, rhy - bsz // 2, bsz, bsz),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (220, 160, 80), (rhx - bsz // 2, rhy - bsz // 2, bsz, bsz),
                         1, border_radius=max(1, int(2*s)))
        # Block grid line
        pygame.draw.line(surface, (150, 95, 35),
                         (rhx, rhy - bsz//2), (rhx, rhy + bsz//2), max(1, int(s)))
        pygame.draw.line(surface, (150, 95, 35),
                         (rhx - bsz//2, rhy), (rhx + bsz//2, rhy), max(1, int(s)))

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
        # Cap button on top
        pygame.draw.circle(surface, (120, 120, 100), (hx, hy - hd - int(hd * 0.55)), max(2, int(3 * s)))
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
        # Blue overalls on torso (full panel)
        pygame.draw.rect(surface, (70, 90, 180),
                         (sx - int(8 * s), sy + int(2 * s), int(16 * s), bl - int(2 * s)),
                         border_radius=max(1, int(2 * s)))
        # Overalls pocket on chest
        pygame.draw.rect(surface, (50, 70, 150),
                         (sx - int(5 * s), sy + int(6 * s), int(10 * s), int(8 * s)),
                         max(1, int(s)), border_radius=max(1, int(s)))
        # Shoulder strap marks
        pygame.draw.line(surface, (50, 70, 150),
                         (sx - int(4 * s), sy + int(2 * s)),
                         (sx - int(6 * s), sy - int(8 * s)), max(1, int(2 * s)))
        pygame.draw.line(surface, (50, 70, 150),
                         (sx + int(4 * s), sy + int(2 * s)),
                         (sx + int(6 * s), sy - int(8 * s)), max(1, int(2 * s)))
        # Spray bottle on belt
        pygame.draw.rect(surface, (100, 160, 220),
                         (wx + facing * int(4 * s), wy - int(8 * s), int(6 * s), int(10 * s)),
                         border_radius=max(1, int(2 * s)))
        pygame.draw.line(surface, (80, 130, 190),
                         (wx + facing * int(7 * s), wy - int(8 * s)),
                         (wx + facing * int(12 * s), wy - int(12 * s)), max(1, int(s)))

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
        # Green scale pattern on torso
        for _sci in range(3):
            for _scj in range(2):
                _scx = sx - int(6*s) + _scj * int(10*s) + (_sci % 2) * int(5*s)
                _scy = sy + int(bl * (0.12 + _sci * 0.28))
                pygame.draw.ellipse(surface, (30, 120, 30),
                                    (_scx - int(5*s), _scy - int(3*s), int(10*s), int(7*s)))
                pygame.draw.ellipse(surface, (60, 160, 50),
                                    (_scx - int(5*s), _scy - int(3*s), int(10*s), int(7*s)),
                                    max(1, int(s)))
        # Belly scales (lighter stripe down center)
        for _bsi in range(5):
            _bsy = sy + int(bl * (0.08 + _bsi * 0.18))
            pygame.draw.ellipse(surface, (180, 220, 140),
                                (sx - int(4*s), _bsy, int(8*s), int(5*s)))
        # Forked tongue
        _tx = hx + facing * hd
        pygame.draw.line(surface, (220, 50, 50),
                         (_tx, hy + int(3*s)),
                         (_tx + facing*int(10*s), hy + int(3*s)), max(2, int(2*s)))
        pygame.draw.line(surface, (220, 50, 50),
                         (_tx + facing*int(10*s), hy + int(3*s)),
                         (_tx + facing*int(14*s), hy - int(3*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (220, 50, 50),
                         (_tx + facing*int(10*s), hy + int(3*s)),
                         (_tx + facing*int(14*s), hy + int(8*s)), max(1, int(2*s)))
        # Slit pupils
        for _eox in (-1, 1):
            pygame.draw.ellipse(surface, (20, 80, 10),
                                (hx + _eox*int(hd*0.3) - int(5*s), hy - int(hd*0.2),
                                 int(10*s), int(8*s)))
            pygame.draw.ellipse(surface, (10, 30, 5),
                                (hx + _eox*int(hd*0.3) - int(2*s), hy - int(hd*0.15),
                                 int(4*s), int(7*s)))
            pygame.draw.circle(surface, (220, 220, 60),
                               (hx + _eox*int(hd*0.3) - int(3*s), hy - int(hd*0.25)),
                               max(1, int(s)))
        # Scale hood markings on head
        for _shi in range(3):
            _sha = math.pi * (0.3 + _shi * 0.2)
            pygame.draw.line(surface, (40, 140, 40),
                             (hx + int(math.cos(_sha) * hd * 0.7),
                              hy - int(math.sin(_sha) * hd * 0.7)),
                             (hx + int(math.cos(_sha) * hd),
                              hy - int(math.sin(_sha) * hd)), max(1, int(2*s)))
        # Fang marks on chin
        for _fi2 in (-1, 1):
            pygame.draw.line(surface, (220, 220, 220),
                             (hx + _fi2*int(hd*0.2), hy + int(hd*0.5)),
                             (hx + _fi2*int(hd*0.2), hy + int(hd*0.75)), max(1, int(2*s)))

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
        # Protective bee suit on torso
        pygame.draw.rect(surface, (240, 235, 200),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 195, 160),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Bee stripes on suit
        for _bsi2 in range(3):
            _bsy = sy + int(bl * (0.2 + _bsi2 * 0.28))
            pygame.draw.line(surface, (20, 20, 0),
                             (sx - int(8*s), _bsy), (sx + int(8*s), _bsy), max(2, int(3*s)))
        # Protective veil mesh around head
        pygame.draw.circle(surface, (200, 190, 160), (hx, hy), int(hd*1.25), max(2, int(3*s)))
        pygame.draw.circle(surface, (180, 170, 140), (hx, hy), int(hd*1.25), max(1, int(s)))
        # Beehive hat (hexagonal dome tiers)
        hat_r = int(hd * 1.1)
        for tier in range(3):
            rr = max(3, hat_r - tier * int(4 * s))
            yy = hy - int(hd*1.25) - int(tier * 9 * s)
            pygame.draw.circle(surface, (220, 170, 0), (hx, yy), rr)
            pygame.draw.circle(surface, (160, 120, 0), (hx, yy), rr, max(1, int(s)))
        # Top knob
        pygame.draw.circle(surface, (200, 150, 0), (hx, hy - int(hd*1.25) - int(26 * s)), max(2, int(3 * s)))
        # Smoker tool in right hand
        pygame.draw.rect(surface, (80, 60, 30),
                         (rhx, rhy - int(8*s), int(facing*16*s), int(8*s)), border_radius=max(1, int(2*s)))
        pygame.draw.line(surface, (60, 45, 20),
                         (rhx + facing*int(16*s), rhy - int(8*s)),
                         (rhx + facing*int(22*s), rhy - int(14*s)), max(2, int(3*s)))
        # Smoke puff
        t_bk = pygame.time.get_ticks()
        if (t_bk // 300) % 2 == 0:
            pygame.draw.circle(surface, (200, 200, 180),
                               (rhx + facing*int(22*s), rhy - int(16*s)), max(3, int(4*s)))

    elif char_name == "Plague Doctor":
        # Dark robes on torso
        pygame.draw.rect(surface, (20, 22, 18),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (40, 45, 35),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Leather strap across chest
        pygame.draw.line(surface, (50, 38, 18),
                         (sx + int(facing*7*s), sy + int(3*s)),
                         (sx - int(facing*7*s), wy - int(5*s)), max(2, int(3*s)))
        # Medical pouch at belt
        pygame.draw.rect(surface, (80, 60, 20),
                         (wx + facing*int(4*s), wy - int(6*s), int(10*s), int(10*s)),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (60, 45, 15),
                         (wx + facing*int(4*s), wy - int(6*s), int(10*s), int(10*s)),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Long beak mask
        beak_len = int(hd * 1.6)
        beak_tip = (hx + int(facing * beak_len), hy + int(4 * s))
        beak_top = (hx + int(facing * int(hd * 0.3)), hy - int(hd * 0.3))
        beak_bot = (hx + int(facing * int(hd * 0.3)), hy + int(hd * 0.5))
        pygame.draw.polygon(surface, (80, 100, 80), [beak_top, beak_tip, beak_bot])
        pygame.draw.polygon(surface, (40, 60, 40),  [beak_top, beak_tip, beak_bot], max(1, int(s)))
        # Dark mask over whole face
        pygame.draw.ellipse(surface, (20, 25, 18), (hx - hd + int(2*s), hy - hd + int(2*s), hd*2 - int(4*s), hd*2 - int(4*s)))
        # Goggle eyes on mask (round glass lenses)
        for _goe in (-1, 1):
            pygame.draw.circle(surface, (15, 30, 15),
                               (hx + _goe*int(hd*0.35), hy - int(hd*0.15)),
                               max(4, int(6*s)))
            pygame.draw.circle(surface, (0, 100, 0),
                               (hx + _goe*int(hd*0.35), hy - int(hd*0.15)),
                               max(4, int(6*s)), max(1, int(2*s)))
        # Dark hat brim
        pygame.draw.ellipse(surface, (20, 20, 20),
                            (hx - int(hd * 1.2), hy - hd - int(4 * s),
                             int(hd * 2.4), int(8 * s)))
        pygame.draw.rect(surface, (20, 20, 20),
                         (hx - int(hd * 0.7), hy - hd - int(18 * s),
                          int(hd * 1.4), int(18 * s)))
        pygame.draw.rect(surface, (40, 40, 35),
                         (hx - int(hd * 0.7), hy - hd - int(18 * s),
                          int(hd * 1.4), int(18 * s)), max(1, int(s)))

    elif char_name == "Necromancer":
        # Dark robe on torso
        pygame.draw.rect(surface, (20, 5, 35),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 20, 100),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Skull emblem on chest
        pygame.draw.circle(surface, (180, 170, 200), (sx, sy + int(bl*0.3)), max(5, int(7*s)))
        for _skex in (-int(2*s), int(2*s)):
            pygame.draw.circle(surface, (30, 10, 50), (sx + _skex, sy + int(bl*0.3) - int(2*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (30, 10, 50),
                         (sx - int(3*s), sy + int(bl*0.3) + int(3*s)),
                         (sx + int(3*s), sy + int(bl*0.3) + int(3*s)), max(1, int(s)))
        # Dark hood
        hood_pts = [
            (hx - int(hd * 1.1), hy + int(hd * 0.3)),
            (hx,                  hy - hd - int(20 * s)),
            (hx + int(hd * 1.1), hy + int(hd * 0.3)),
        ]
        pygame.draw.polygon(surface, (30, 10, 50), hood_pts)
        pygame.draw.polygon(surface, (80, 40, 120), hood_pts, max(1, int(s)))
        # Glowing purple eyes in the dark hood
        for side in (-1, 1):
            ex2 = hx + side * int(hd * 0.35)
            pygame.draw.circle(surface, (160, 0, 255), (ex2, hy - int(2 * s)), max(3, int(4 * s)))
            pygame.draw.circle(surface, (220, 100, 255), (ex2, hy - int(2 * s)), max(1, int(2 * s)))
        # Necromancer staff in right hand
        _nstip = (rhx + facing*int(5*s), rhy - int(42*s))
        pygame.draw.line(surface, (50, 30, 70), (rhx, rhy), _nstip, max(2, int(3*s)))
        pygame.draw.circle(surface, (120, 0, 200), _nstip, max(4, int(6*s)))
        pygame.draw.circle(surface, (200, 80, 255), _nstip, max(2, int(3*s)))
        # Rising soul wisps from ground
        t_nc = pygame.time.get_ticks()
        for _ni in range(3):
            _na = (t_nc * 0.005 + _ni * 2.1) % (2 * math.pi)
            pygame.draw.circle(surface, (100, 0, 180),
                               (wx + int((_ni - 1) * 10 * s), wy + int(bl * 0.6 * (1 - (_na / (2 * math.pi))))),
                               max(2, int(3 * s)))

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
        # Metal gauntlet on the punch fist (right hand)
        gx, gy = int(rhx), int(rhy)
        gr = max(5, int(10 * s))
        pygame.draw.circle(surface, (180, 190, 200), (gx, gy), gr)
        pygame.draw.circle(surface, (100, 110, 130), (gx, gy), gr, max(1, int(2 * s)))
        # Knuckle ridges
        for ki in range(3):
            kx = gx + int((ki - 1) * 4 * s)
            pygame.draw.circle(surface, (220, 220, 240), (kx, gy - max(1, int(3 * s))), max(1, int(2 * s)))
        # Metal bracer on the arm above the fist
        _bx1 = (gx + sx) // 2
        _by1 = (gy + sy) // 2
        pygame.draw.rect(surface, (160, 170, 185),
                         (_bx1 - int(5*s), _by1 - int(4*s), int(10*s), int(8*s)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (100, 110, 130),
                         (_bx1 - int(5*s), _by1 - int(4*s), int(10*s), int(8*s)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Metal shoulder pad on right side
        pygame.draw.rect(surface, (150, 160, 175),
                         (sx + facing*int(3*s), sy - int(5*s), int(14*s), int(9*s)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (100, 110, 130),
                         (sx + facing*int(3*s), sy - int(5*s), int(14*s), int(9*s)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Battle helmet — heavy steel dome
        pygame.draw.rect(surface, (140, 148, 165),
                         (hx - hd, hy - hd, hd*2, int(hd*1.6)),
                         border_radius=max(3, int(4*s)))
        pygame.draw.rect(surface, (80, 88, 105),
                         (hx - hd, hy - hd, hd*2, int(hd*1.6)),
                         max(1, int(2*s)), border_radius=max(3, int(4*s)))
        # T-visor slit
        pygame.draw.rect(surface, (20, 20, 30),
                         (hx - int(hd*0.6), hy - int(3*s), int(hd*1.2), int(5*s)))

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
        # Ray gun body (teal sci-fi pistol)
        gun_x = rhx
        gun_y = rhy
        gun_w = int(28 * s)
        gun_h = int(10 * s)
        pygame.draw.rect(surface, (30, 160, 130),
                         (gun_x, gun_y - gun_h // 2, facing * gun_w, gun_h),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 220, 180),
                         (gun_x, gun_y - gun_h // 2, facing * gun_w, gun_h),
                         max(1, int(2*s)), border_radius=max(2, int(3*s)))
        # Barrel tip with glowing ring
        gun_tip = gun_x + facing * gun_w
        pygame.draw.circle(surface, (120, 255, 210), (gun_tip, gun_y), max(3, int(5 * s)))
        pygame.draw.circle(surface, (255, 255, 255), (gun_tip, gun_y), max(1, int(2 * s)))
        # Grip handle
        pygame.draw.rect(surface, (20, 120, 100),
                         (gun_x + facing*int(8*s), gun_y + gun_h//2, int(7*s), int(9*s)),
                         border_radius=max(1, int(2*s)))
        # Shrink beam pulse effect (tiny circles in beam path)
        t = pygame.time.get_ticks()
        for _bi in range(3):
            _bphase = (t // 100 + _bi * 2) % 6
            _bx = gun_tip + facing * int((_bphase * 4) * s)
            pygame.draw.circle(surface, (60, 220, 180), (_bx, gun_y), max(1, int(2*s)))
        # Lab goggles on head
        _gy3 = hy - int(hd * 0.1)
        for _gxo3 in (-int(hd*.38), int(hd*.38)):
            pygame.draw.circle(surface, (20, 100, 90), (hx + _gxo3, _gy3), int(hd*.32))
            pygame.draw.circle(surface, (60, 200, 170), (hx + _gxo3, _gy3), int(hd*.32), max(1, int(2*s)))
        pygame.draw.line(surface, (40, 160, 130),
                         (hx - int(hd*.06), _gy3), (hx + int(hd*.06), _gy3), max(1, int(s)))
        # Size-down arrows on chest
        for _ai2, _ay2 in enumerate([sy + int(bl*0.25), sy + int(bl*0.55)]):
            _aw = int(5 * s) - _ai2 * int(2 * s)
            pygame.draw.polygon(surface, (80, 220, 180), [
                (sx - _aw, _ay2), (sx, _ay2 + int(5*s)), (sx + _aw, _ay2)])
        pygame.draw.line(surface, (80, 220, 180), (sx, sy + int(bl*0.2)), (sx, sy + int(bl*0.6)),
                         max(1, int(s)))

    elif char_name == "Levitator":
        # Upward-pointing glowing hands
        for hpos in [(lhx, lhy), (rhx, rhy)]:
            glow_r = max(5, int(8 * s))
            gsurf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (180, 140, 255, 100), (glow_r + 2, glow_r + 2), glow_r)
            surface.blit(gsurf, (int(hpos[0]) - glow_r - 2, int(hpos[1]) - glow_r - 2))
            pygame.draw.circle(surface, (220, 180, 255), (int(hpos[0]), int(hpos[1])),
                               max(3, int(5 * s)))
        # Levitation aura ring around body
        t_lv = pygame.time.get_ticks()
        _aura_r = int(hd * 1.5)
        for _li in range(6):
            _la = math.radians(_li * 60 + t_lv * 0.1)
            pygame.draw.circle(surface, (160, 120, 255),
                               (hx + int(math.cos(_la) * _aura_r), wy - int(hd * 0.5) + int(math.sin(_la) * int(_aura_r * 0.5))),
                               max(2, int(3 * s)))
        # Mystical robe on torso
        pygame.draw.rect(surface, (80, 40, 160),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (120, 70, 210),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Robe star pattern
        for _rsi in range(3):
            pygame.draw.circle(surface, (200, 160, 255),
                               (sx + int((_rsi - 1) * 5 * s), sy + int(bl * (0.3 + _rsi * 0.2))),
                               max(2, int(3 * s)))
        # Floating halo above head
        pygame.draw.ellipse(surface, (200, 160, 255),
                            (hx - int(hd*1.1), hy - hd - int(12*s), int(hd*2.2), int(8*s)),
                            max(2, int(3*s)))

    elif char_name == "Stalker":
        # Dark tactical suit on torso
        pygame.draw.rect(surface, (15, 20, 15),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (35, 45, 35),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Utility pockets on vest
        for _up in range(2):
            _upx = sx - int(6*s) + _up*int(9*s)
            pygame.draw.rect(surface, (25, 35, 25),
                             (_upx, sy + int(bl*0.2), int(6*s), int(6*s)))
        # Dark hood pulled low
        hood_pts = [
            (hx - int(hd * 1.05), hy + int(hd * 0.2)),
            (hx,                   hy - hd - int(14 * s)),
            (hx + int(hd * 1.05), hy + int(hd * 0.2)),
        ]
        pygame.draw.polygon(surface, (20, 30, 20), hood_pts)
        pygame.draw.polygon(surface, (40, 60, 40), hood_pts, max(1, int(s)))
        # Glowing red eyes beneath hood
        for side in (-1, 1):
            pygame.draw.circle(surface, (200, 20, 20),
                               (hx + side * int(hd * 0.38), hy), max(3, int(4 * s)))
            pygame.draw.circle(surface, (255, 80, 80),
                               (hx + side * int(hd * 0.38), hy), max(1, int(2 * s)))
        # Night-vision goggle silhouettes above eyes
        for _nside in (-1, 1):
            pygame.draw.circle(surface, (10, 15, 10),
                               (hx + _nside*int(hd*0.38), hy - int(hd*0.08)),
                               max(4, int(6*s)), max(1, int(2*s)))
        # Throwing knife at left hand
        knife_tip2 = (lhx - facing*int(18*s), lhy - int(8*s))
        pygame.draw.line(surface, (170, 175, 190), (lhx, lhy), knife_tip2, max(1, int(2*s)))
        # Belt with shuriken shape at waist
        pygame.draw.rect(surface, (25, 30, 25),
                         (wx - int(10*s), wy - int(3*s), int(20*s), max(4, int(6*s))))
        for _shi in range(4):
            _sha = math.radians(_shi * 45)
            pygame.draw.line(surface, (80, 80, 80),
                             (wx, wy), (wx + int(math.cos(_sha)*5*s), wy + int(math.sin(_sha)*5*s)),
                             max(1, int(s)))

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
        # Gold divine helmet with forward crest
        pygame.draw.ellipse(surface, (200, 160, 10),
                            (hx - int(hd*1.15), hy - hd - int(hd*0.85), int(hd*2.3), int(hd*1.0)))
        pygame.draw.ellipse(surface, (240, 200, 20),
                            (hx - int(hd*1.15), hy - hd - int(hd*0.85), int(hd*2.3), int(hd*1.0)),
                            max(1, int(2*s)))
        # Visor slit on helmet
        pygame.draw.rect(surface, (40, 30, 0),
                         (hx - int(hd*0.65), hy - int(3*s), int(hd*1.3), int(5*s)))
        # God-armor chest plate
        pygame.draw.rect(surface, (190, 155, 10),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (230, 190, 30),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Lightning bolt emblem on chest
        _tcx = sx
        pygame.draw.lines(surface, (255, 255, 100), False, [
            (_tcx + int(5*s), sy + int(4*s)),
            (_tcx - int(3*s), sy + int(bl*0.45)),
            (_tcx + int(3*s), sy + int(bl*0.45)),
            (_tcx - int(5*s), sy + int(bl*0.9)),
        ], max(2, int(3*s)))
        # Thunderbolts at fists
        for _tfx, _tfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (255, 220, 0), (_tfx, _tfy), max(4, int(6*s)))
            pygame.draw.circle(surface, (255, 255, 180), (_tfx, _tfy), max(2, int(3*s)))

    elif char_name == "Glass Cannon":
        # Translucent glass/crystal chest armor
        _gcsurf = pygame.Surface((int(22*s)+1, int(bl)+1), pygame.SRCALPHA)
        pygame.draw.rect(_gcsurf, (180, 220, 255, 60),
                         (0, 0, int(22*s), int(bl)), border_radius=max(2, int(4*s)))
        pygame.draw.rect(_gcsurf, (220, 240, 255, 120),
                         (0, 0, int(22*s), int(bl)), max(1, int(s)), border_radius=max(2, int(4*s)))
        surface.blit(_gcsurf, (sx - int(11*s), sy))
        # Glass shatter cracks on chest
        for _gci, (_gcx1, _gcy1, _gcx2, _gcy2) in enumerate([
            (-5, 5, 3, 18), (2, 3, -4, 20), (-1, 12, 7, 28), (4, 20, -6, 32)]):
            pygame.draw.line(surface, (200, 230, 255),
                             (sx + int(_gcx1*s), sy + int(_gcy1*s)),
                             (sx + int(_gcx2*s), sy + int(_gcy2*s)), max(1, int(s)))
        # Crystal facet highlights
        for _fhx2, _fhy2 in [(-7, 6), (5, 14), (-3, 26), (7, 34)]:
            pygame.draw.circle(surface, (240, 250, 255),
                               (sx + int(_fhx2*s), sy + int(_fhy2*s)), max(1, int(2*s)))
        # Cannon barrel on shoulder — extended and detailed
        c_x = sx + int(facing * int(8 * s))
        c_y = sy - int(6 * s)
        c_len = int(34 * s)
        # Barrel body
        pygame.draw.rect(surface, (160, 180, 200),
                         (c_x, c_y - max(4, int(6*s)),
                          int(facing * c_len), max(8, int(12*s))),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 220, 240),
                         (c_x, c_y - max(4, int(6*s)),
                          int(facing * c_len), max(8, int(12*s))),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Barrel ring reinforcements
        for _bri in range(3):
            _brx = c_x + int(facing * c_len * (0.2 + _bri * 0.25))
            pygame.draw.line(surface, (140, 160, 180),
                             (_brx, c_y - max(4, int(6*s))),
                             (_brx, c_y + max(4, int(6*s))), max(1, int(2*s)))
        # Muzzle flash ring at tip
        pygame.draw.circle(surface, (120, 140, 165),
                           (c_x + int(facing * c_len), c_y), max(5, int(8*s)))
        pygame.draw.circle(surface, (200, 220, 240),
                           (c_x + int(facing * c_len), c_y), max(5, int(8*s)), max(1, int(2*s)))
        # Targeting monocle on eye
        _mox = hx + facing * int(hd * 0.35)
        _moy = hy - int(hd * 0.1)
        pygame.draw.circle(surface, (180, 220, 255), (_mox, _moy), max(4, int(6*s)), max(1, int(2*s)))
        pygame.draw.circle(surface, (220, 240, 255), (_mox, _moy), max(2, int(3*s)))
        pygame.draw.line(surface, (160, 180, 200),
                         (_mox + max(3, int(5*s)), _moy + max(3, int(5*s))),
                         (_mox + max(6, int(9*s)), _moy + max(6, int(9*s))), max(1, int(2*s)))
        # Ammo belt across torso
        for _abi in range(6):
            _abx = sx - int(9*s) + _abi * int(4*s)
            _aby = sy + int(bl * 0.65)
            pygame.draw.rect(surface, (140, 120, 60),
                             (_abx, _aby, max(2, int(3*s)), max(5, int(8*s))),
                             border_radius=max(1, int(s)))
            pygame.draw.rect(surface, (200, 180, 80),
                             (_abx, _aby, max(2, int(3*s)), max(5, int(8*s))),
                             max(1, int(s)), border_radius=max(1, int(s)))

    elif char_name == "Teleporter":
        # Swirling portal ring around body
        t = pygame.time.get_ticks()
        for pi in range(8):
            pa = math.radians(pi * 45 + t * 0.18)
            px2 = hx + int(math.cos(pa) * hd * 1.8)
            py2 = wy + int(math.sin(pa) * int(hd * 1.2))
            pygame.draw.circle(surface, (0, 200, 220), (px2, py2), max(2, int(3 * s)))

    elif char_name == "Sticker":
        # Glue dripping from fists — thick amber drops
        for hpos in [(lhx, lhy), (rhx, rhy)]:
            drop_y = int(hpos[1]) + max(5, int(8 * s))
            pygame.draw.line(surface, (200, 170, 30),
                             (int(hpos[0]), int(hpos[1])),
                             (int(hpos[0]), drop_y), max(2, int(3 * s)))
            pygame.draw.circle(surface, (230, 200, 40), (int(hpos[0]), drop_y), max(3, int(5 * s)))
            pygame.draw.circle(surface, (255, 230, 100),
                               (int(hpos[0]) - max(1, int(1 * s)), drop_y - max(1, int(1 * s))),
                               max(1, int(2 * s)))
        # Sticky glue splat blob on torso
        _gx, _gy = sx, sy + int(bl * 0.4)
        for _gi in range(6):
            _ga = _gi * 1.047
            _grx = _gx + int(math.cos(_ga) * max(5, int(8 * s)))
            _gry = _gy + int(math.sin(_ga) * max(4, int(6 * s)))
            pygame.draw.circle(surface, (200, 170, 30), (_grx, _gry), max(2, int(3 * s)))
        pygame.draw.circle(surface, (230, 200, 40), (_gx, _gy), max(5, int(7 * s)))
        # Goggles with amber lenses
        _gy2 = hy - int(hd * 0.1)
        for _gxo in (-int(hd * .38), int(hd * .38)):
            pygame.draw.circle(surface, (200, 160, 20), (hx + _gxo, _gy2), int(hd * .3))
            pygame.draw.circle(surface, (240, 200, 60), (hx + _gxo, _gy2), int(hd * .3), max(1, int(2 * s)))
        pygame.draw.line(surface, (160, 130, 20),
                         (hx - int(hd * .08), _gy2), (hx + int(hd * .08), _gy2), max(1, int(s)))
        # Sticky belt at waist
        pygame.draw.rect(surface, (180, 150, 20),
                         (wx - int(hd * 0.9), wy - int(3 * s), int(hd * 1.8), max(4, int(6 * s))),
                         max(1, int(2 * s)))

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
        # Soft pyjama robe on torso
        pygame.draw.rect(surface, (170, 170, 210),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (130, 130, 180),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Pyjama stripes
        for _psi in range(3):
            _psy = sy + int(bl * (0.2 + _psi * 0.28))
            pygame.draw.line(surface, (200, 200, 240),
                             (sx - int(7*s), _psy), (sx + int(7*s), _psy), max(1, int(2*s)))
        # Droopy sleep cap
        brim_y = hy - hd
        tip_x  = hx + int(facing * hd * 0.55)
        tip_y  = hy - int(hd * 2.4)
        pygame.draw.polygon(surface, (200, 200, 230),
                            [(hx - hd, brim_y), (hx + hd, brim_y), (tip_x, tip_y)])
        pygame.draw.ellipse(surface, (220, 210, 240),
                            (hx - hd - int(2*s), brim_y - int(4*s), hd*2 + int(4*s), int(8*s)))
        pygame.draw.circle(surface, (240, 200, 255), (tip_x, tip_y), max(3, int(5*s)))
        # Sand bag / pillow strapped on back
        pygame.draw.rect(surface, (200, 180, 120),
                         (sx - facing*int(14*s) - int(5*s), sy + int(4*s), int(10*s), int(bl*0.5)),
                         border_radius=max(2, int(3*s)))
        # Floating Zs with size variation
        tt = pygame.time.get_ticks()
        for zi, (zo, zsize) in enumerate(((0, 14), (-12, 10), (-22, 8))):
            if (tt // 500 + zi) % 2 == 0:
                zf = _get_font(max(zsize, int(zsize*s)))
                zs = zf.render("Z", True, (160, 160, 255))
                surface.blit(zs, (hx + int(hd * 1.2), hy - hd - int((8 + abs(zo)) * s)))

    elif char_name == "Reaper":
        # Dark tattered robe on torso
        pygame.draw.rect(surface, (15, 15, 20),
                         (sx - int(11*s), sy, int(22*s), bl + int(4*s)), border_radius=max(2, int(3*s)))
        # Tattered hem at bottom
        for _ti in range(5):
            _tx = sx - int(10*s) + _ti * int(5*s)
            pygame.draw.polygon(surface, (15, 15, 20), [
                (_tx, wy), (_tx + int(3*s), wy + int(8*s)), (_tx + int(5*s), wy)
            ])
        # Dark hood over head — wide and shadowed
        pygame.draw.polygon(surface, (15, 15, 20),
                            [(hx - hd - int(6*s), hy + int(4*s)),
                             (hx + hd + int(6*s), hy + int(4*s)),
                             (hx + int(hd*0.8), hy - hd - int(10*s)),
                             (hx - int(hd*0.8), hy - hd - int(10*s))])
        pygame.draw.polygon(surface, (50, 50, 60),
                            [(hx - hd - int(6*s), hy + int(4*s)),
                             (hx + hd + int(6*s), hy + int(4*s)),
                             (hx + int(hd*0.8), hy - hd - int(10*s)),
                             (hx - int(hd*0.8), hy - hd - int(10*s))], max(1, int(2*s)))
        # Glowing eyes inside hood
        for _rex in [hx - int(hd*0.28), hx + int(hd*0.28)]:
            pygame.draw.circle(surface, (160, 200, 255), (_rex, hy - int(hd*0.1)), max(2, int(3*s)))
        # Long scythe handle
        spx = rhx + int(facing * int(6*s))
        _spy = rhy
        _shaft_tip = (spx - int(facing * int(6*s)), _spy - int(hd*3.2))
        pygame.draw.line(surface, (70, 45, 20), (spx, _spy), _shaft_tip, max(2, int(4*s)))
        pygame.draw.line(surface, (110, 80, 40), (spx, _spy), _shaft_tip, max(1, int(2*s)))
        # Scythe blade as large crescent arc
        blade_cx, blade_cy = _shaft_tip
        br = int(hd * 1.3)
        blade_start = math.radians(60 if facing > 0 else 300)
        blade_end   = math.radians(200 if facing > 0 else 480)
        pygame.draw.arc(surface, (190, 200, 220),
                        (blade_cx - br, blade_cy - br, br*2, br*2),
                        blade_start, blade_end, max(2, int(3*s)))
        # Blade inner shine
        pygame.draw.arc(surface, (230, 240, 255),
                        (blade_cx - int(br*0.7), blade_cy - int(br*0.7), int(br*1.4), int(br*1.4)),
                        blade_start, blade_end, max(1, int(s)))

    elif char_name == "Chainsaw Man":
        # Grimy work jacket on torso
        pygame.draw.rect(surface, (50, 40, 30),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (80, 65, 45),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Oil splatter marks on torso
        for _ox, _oy in [(-int(5*s), int(10*s)), (int(6*s), int(22*s)), (-int(3*s), int(32*s))]:
            pygame.draw.circle(surface, (20, 15, 10), (sx+_ox, sy+_oy), max(2, int(3*s)))
        # Goggles pushed up on forehead
        pygame.draw.ellipse(surface, (30, 25, 20),
                            (hx - int(hd*0.9), hy - hd - int(hd*0.5), int(hd*1.8), int(hd*0.4)))
        for _gxo in (-int(hd*.38), int(hd*.38)):
            pygame.draw.circle(surface, (50, 45, 35), (hx+_gxo, hy - hd - int(hd*0.32)), max(3, int(5*s)))
            pygame.draw.circle(surface, (70, 65, 50), (hx+_gxo, hy - hd - int(hd*0.32)), max(3, int(5*s)), max(1, int(s)))
        # Orange chainsaw body + blade
        cx2, cy2 = int(rhx + int(facing * int(4*s))), int(rhy)
        blen = int(32*s); bhalf = max(4, int(6*s))
        # Engine block
        pygame.draw.rect(surface, (180, 50, 20),
                         (cx2, cy2 - bhalf - int(3*s),
                          int(facing * int(blen * 0.35)), bhalf*2 + int(6*s)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (220, 80, 40),
                         (cx2, cy2 - bhalf - int(3*s),
                          int(facing * int(blen * 0.35)), bhalf*2 + int(6*s)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Guide bar
        pygame.draw.rect(surface, (80, 80, 90),
                         (cx2 + int(facing * int(blen * 0.3)), cy2 - bhalf,
                          int(facing * int(blen * 0.65)), bhalf*2))
        pygame.draw.rect(surface, (120, 120, 130),
                         (cx2 + int(facing * int(blen * 0.3)), cy2 - bhalf,
                          int(facing * int(blen * 0.65)), bhalf*2), max(1, int(s)))
        # Animated chain teeth
        tt2 = pygame.time.get_ticks()
        for ti in range(6):
            tooth_offset = (ti + tt2 // 60 % 6) * blen // 6
            tooth_x = cx2 + int(facing * tooth_offset)
            pygame.draw.circle(surface, (200, 200, 80), (tooth_x, cy2 - bhalf), max(2, int(3*s)))
            pygame.draw.circle(surface, (200, 200, 80), (tooth_x, cy2 + bhalf), max(2, int(2*s)))

    elif char_name == "Crusher":
        # Massive armored torso — dark purple plating
        pygame.draw.rect(surface, (70, 35, 110),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (110, 60, 160),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(2*s)), border_radius=max(2, int(4*s)))
        # Chest ridge line
        pygame.draw.line(surface, (140, 80, 200),
                         (sx, sy + int(4*s)), (sx, wy - int(2*s)), max(1, int(2*s)))
        # Shoulder spikes
        for _side in (-1, 1):
            _spx = sx + _side * int(12*s)
            pygame.draw.polygon(surface, (100, 50, 160), [
                (_spx, sy - int(4*s)),
                (_spx + _side*int(6*s), sy - int(14*s)),
                (_spx + _side*int(2*s), sy + int(2*s)),
            ])
        # Cracked visor slit on head
        pygame.draw.rect(surface, (70, 35, 110),
                         (hx - int(hd*1.0), hy - hd - int(hd*0.3), int(hd*2.0), int(hd*1.6)),
                         border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (110, 60, 160),
                         (hx - int(hd*1.0), hy - hd - int(hd*0.3), int(hd*2.0), int(hd*1.6)),
                         max(1, int(2*s)), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (30, 15, 50),
                         (hx - int(hd*0.7), hy - int(hd*0.2), int(hd*1.4), int(hd*0.4)))
        # Big spiked knuckles on both fists
        for fhx2, fhy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (100, 50, 160), (fhx2, fhy2), max(6, int(10*s)))
            for si in range(4):
                sa = math.radians(si * 90)
                pygame.draw.circle(surface, (180, 100, 220),
                                   (fhx2 + int(math.cos(sa) * max(6, int(10*s))),
                                    fhy2 + int(math.sin(sa) * max(6, int(10*s)))),
                                   max(2, int(3*s)))

    elif char_name == "Storm Witch":
        # Dark storm robes on torso
        pygame.draw.rect(surface, (30, 15, 60),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (70, 40, 120),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Lightning bolt emblem on chest
        _lpts = [(sx + int(3*s), sy + int(6*s)),
                 (sx - int(2*s), sy + int(16*s)),
                 (sx + int(4*s), sy + int(16*s)),
                 (sx - int(3*s), sy + int(28*s))]
        pygame.draw.lines(surface, (180, 100, 255), False, _lpts, max(2, int(3*s)))
        # Storm cloud aura — dark wisps on both sides
        t_sw = pygame.time.get_ticks()
        for _wi in range(4):
            _wa = math.radians(_wi * 90 + t_sw * 0.12)
            _wrx = wx + int(math.cos(_wa) * int(hd*1.3))
            _wry = sy + int(bl*0.4) + int(math.sin(_wa) * int(6*s))
            pygame.draw.circle(surface, (90, 50, 140), (_wrx, _wry), max(3, int(4*s)))
        # Tall pointed witch hat
        brim_y2 = hy - hd
        pygame.draw.polygon(surface, (40, 20, 80),
                            [(hx - int(hd*1.4), brim_y2), (hx + int(hd*1.4), brim_y2),
                             (hx, hy - int(hd*3.0))])
        pygame.draw.ellipse(surface, (60, 30, 110),
                            (hx - int(hd*1.4) - int(2*s), brim_y2 - int(4*s),
                             int(hd*2.8) + int(4*s), int(8*s)))
        pygame.draw.line(surface, (160, 80, 220),
                         (hx - int(hd*1.2), brim_y2 + int(2*s)),
                         (hx + int(hd*1.2), brim_y2 + int(2*s)),
                         max(1, int(2*s)))
        # Stars on hat
        for _sdx, _sdy in [(facing*int(4*s), -int(hd*1.4)), (-facing*int(5*s), -int(hd*2.0))]:
            pygame.draw.circle(surface, (180, 100, 255), (hx+_sdx, hy - hd + _sdy), max(2, int(3*s)))
        # Storm staff in left hand
        _sspt = (lhx - int(facing*4*s), lhy - int(hd*2.2))
        pygame.draw.line(surface, (70, 40, 110), (lhx, lhy), _sspt, max(2, int(3*s)))
        pygame.draw.circle(surface, (150, 80, 220), _sspt, max(3, int(5*s)))

    elif char_name == "Blood Baron":
        # Black noble coat on torso
        pygame.draw.rect(surface, (15, 10, 15),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (50, 30, 50),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Coat lapels
        pygame.draw.polygon(surface, (30, 10, 30), [
            (sx, sy + int(4*s)), (sx - int(7*s), sy + int(bl*0.5)), (sx - int(4*s), sy)
        ])
        pygame.draw.polygon(surface, (30, 10, 30), [
            (sx, sy + int(4*s)), (sx + int(7*s), sy + int(bl*0.5)), (sx + int(4*s), sy)
        ])
        # Blood-red cravat on chest
        pygame.draw.polygon(surface, (180, 0, 30), [
            (sx - int(4*s), sy + int(2*s)), (sx + int(4*s), sy + int(2*s)),
            (sx + int(3*s), sy + int(12*s)), (sx, sy + int(16*s)), (sx - int(3*s), sy + int(12*s))
        ])
        # Red vampire collar at neck
        pygame.draw.polygon(surface, (150, 0, 30),
                            [(sx - int(hd*1.1), sy - int(6*s)), (sx + int(hd*1.1), sy - int(6*s)),
                             (sx + int(hd*0.7), sy + int(8*s)), (sx - int(hd*0.7), sy + int(8*s))])
        pygame.draw.polygon(surface, (200, 20, 50),
                            [(sx - int(hd*1.1), sy - int(6*s)), (sx + int(hd*1.1), sy - int(6*s)),
                             (sx + int(hd*0.7), sy + int(8*s)), (sx - int(hd*0.7), sy + int(8*s))],
                            max(1, int(2*s)))
        # Fangs below head
        for fx2 in (hx - int(hd*0.3), hx + int(hd*0.3)):
            pygame.draw.polygon(surface, (255, 230, 230),
                                [(fx2 - int(3*s), hy + int(hd*0.9)),
                                 (fx2 + int(3*s), hy + int(hd*0.9)),
                                 (fx2, hy + int(hd*1.5))])
        # Glowing red eyes
        for _bex in [hx - int(hd*0.35), hx + int(hd*0.35)]:
            pygame.draw.circle(surface, (220, 20, 40), (_bex, hy - int(hd*0.1)), max(2, int(3*s)))
            pygame.draw.circle(surface, (255, 80, 80), (_bex, hy - int(hd*0.1)), max(1, int(2*s)))

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
        # Yellow lightning bolt on chest (large filled polygon)
        bx1 = sx + int(facing * int(2*s))
        pts_bolt = [(bx1, sy - int(8*s)), (bx1 - int(facing*int(5*s)), sy + int(2*s)),
                    (bx1 + int(facing*int(2*s)), sy + int(2*s)), (bx1 - int(facing*int(3*s)), sy + int(12*s))]
        if len(pts_bolt) >= 3:
            pygame.draw.polygon(surface, (255, 220, 0), pts_bolt)
            pygame.draw.polygon(surface, (200, 160, 0), pts_bolt, 1)
        # Red speedster helmet with white lightning wing
        pygame.draw.circle(surface, (200, 30, 30), (hx, hy), int(hd * 1.05))
        pygame.draw.circle(surface, (160, 10, 10), (hx, hy), int(hd * 1.05), max(1, int(2*s)))
        # White wing marking on helmet
        wing_tip = (hx + facing * int(hd * 1.35), hy - int(hd * 0.2))
        pygame.draw.polygon(surface, WHITE, [
            (hx + facing * int(hd * 0.7), hy - int(hd * 0.4)),
            wing_tip,
            (hx + facing * int(hd * 0.7), hy + int(hd * 0.1)),
        ])
        # Speed streaks trailing behind
        for _si in range(3):
            pygame.draw.line(surface, (255, 240, 80),
                             (sx - facing * int((8 + _si * 8) * s), sy + int(bl * 0.3 * (_si + 0.5))),
                             (sx - facing * int((16 + _si * 8) * s), sy + int(bl * 0.3 * (_si + 0.5)) - int(2*s)),
                             max(1, int(2 * s)))
        # Redraw head circle to show helmet color over stickman head
        pygame.draw.circle(surface, col, (hx, hy), hd)

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
        # Red apple held in left hand (Newton's)
        ax2, ay2 = lhx, lhy - max(4, int(6*s))
        pygame.draw.circle(surface, (220, 40, 40), (ax2, ay2), max(5, int(8*s)))
        pygame.draw.circle(surface, (255, 80, 80), (ax2, ay2), max(5, int(8*s)), max(1, int(s)))
        # Shine on apple
        pygame.draw.circle(surface, (255, 180, 180),
                           (ax2 - max(1, int(2*s)), ay2 - max(2, int(3*s))), max(2, int(3*s)))
        # Stem and leaf
        pygame.draw.line(surface, (60, 120, 20), (ax2, ay2 - max(4, int(6*s))),
                         (ax2 + int(3*s), ay2 - max(7, int(11*s))), max(1, int(2*s)))
        pygame.draw.ellipse(surface, (60, 180, 30),
                            (ax2, ay2 - max(7, int(11*s)), int(7*s), int(5*s)))
        # Gravity pull aura — concentric downward arcs from head
        for _gi in range(3):
            _gr = int(hd * (0.9 + _gi * 0.5))
            pygame.draw.arc(surface, (80, 80, 200),
                            (hx - _gr, hy - _gr, _gr * 2, _gr * 2),
                            math.radians(200), math.radians(340), max(1, int(s)))
        # Newton wig — wavy white lines on head
        for _wi in range(4):
            _wa = math.radians(130 + _wi * 25)
            _wx2 = hx + int(math.cos(_wa) * hd)
            _wy2 = hy + int(math.sin(_wa) * hd)
            pygame.draw.line(surface, (240, 240, 240),
                             (_wx2, _wy2), (_wx2 - facing*int(4*s), _wy2 + int(5*s)),
                             max(1, int(2*s)))
        # "F" (force) label on chest
        _ff = _get_font(max(8, int(12*s)))
        _ft = _ff.render("F", True, (120, 120, 240))
        surface.blit(_ft, (sx - _ft.get_width()//2, sy + int(bl*0.3) - _ft.get_height()//2))

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
        # Vein marks on forehead
        for vx2 in (-int(hd*0.4), int(hd*0.2)):
            pygame.draw.line(surface, (200, 0, 0),
                             (hx + vx2, hy - int(hd*0.1)), (hx + vx2, hy - int(hd*0.5)),
                             max(1, int(s)))
        # Tank-top with torn edge on torso
        pygame.draw.rect(surface, (80, 60, 150),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (60, 40, 120),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Torn bottom edge marks
        for _ti2 in range(3):
            pygame.draw.line(surface, (60, 40, 120),
                             (sx - int(6*s) + _ti2*int(6*s), wy - int(2*s)),
                             (sx - int(4*s) + _ti2*int(6*s), wy + int(4*s)),
                             max(1, int(s)))
        # Huge fist knuckle marks on both hands
        for _fx2, _fy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (200, 160, 100), (_fx2, _fy2), max(5, int(8*s)))
            for _ki in range(3):
                _kx = _fx2 + int((_ki - 1) * 4 * s)
                pygame.draw.line(surface, (140, 90, 50),
                                 (_kx, _fy2 - max(3, int(4*s))), (_kx, _fy2 + max(1, int(2*s))),
                                 max(1, int(s)))
        # Scar on cheek
        pygame.draw.line(surface, (160, 60, 60),
                         (hx + facing*int(hd*0.25), hy + int(hd*0.05)),
                         (hx + facing*int(hd*0.55), hy + int(hd*0.38)), max(1, int(2*s)))

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
        # Playing card suit — big diamond on chest
        pts_dia = [(sx, sy - int(10*s)), (sx + int(7*s), sy),
                   (sx, sy + int(10*s)), (sx - int(7*s), sy)]
        pygame.draw.polygon(surface, (220, 40, 40), pts_dia)
        pygame.draw.polygon(surface, (255, 80, 80), pts_dia, 1)
        # Card suit symbols on belt area
        for _wi, _wcs in enumerate([(wx - int(8*s), wy, '♠'), (wx + int(8*s), wy, '♥')]):
            pygame.draw.circle(surface, (240, 240, 240), (_wcs[0], _wcs[1]), max(4, int(6*s)))
            pygame.draw.circle(surface, (180, 180, 180), (_wcs[0], _wcs[1]), max(4, int(6*s)), 1)
        # Joker-style ruffled collar at neck
        for _ci in range(4):
            _cx3 = sx - int(6*s) + _ci * int(4*s)
            _ccol = [(200, 0, 0), (0, 0, 200), (200, 0, 0), (0, 0, 200)][_ci]
            pygame.draw.circle(surface, _ccol, (_cx3, sy + int(4*s)), max(3, int(4*s)))
        # Jester-style two-tone hat
        jhat_y = hy - hd
        pygame.draw.polygon(surface, (180, 0, 180), [
            (hx - int(hd*0.8), jhat_y), (hx, jhat_y - int(hd*1.2)),
            (hx - int(hd*0.2), jhat_y)])
        pygame.draw.polygon(surface, (200, 160, 0), [
            (hx + int(hd*0.8), jhat_y), (hx, jhat_y - int(hd*1.2)),
            (hx + int(hd*0.2), jhat_y)])
        pygame.draw.circle(surface, (255, 220, 0), (hx, jhat_y - int(hd*1.2)), max(3, int(4*s)))

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
        # Chitin exoskeleton armor — segmented dark orange carapace on torso
        pygame.draw.rect(surface, (100, 45, 5),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(4*s)))
        # Carapace segment plates
        for _cseg in range(4):
            _csegy = sy + int(bl * (_cseg * 0.24))
            _csegw = int((20 - _cseg * 2) * s)
            pygame.draw.rect(surface, (140, 65, 12),
                             (sx - _csegw//2, _csegy, _csegw, int(bl*0.22)),
                             border_radius=max(1, int(3*s)))
            pygame.draw.rect(surface, (180, 95, 25),
                             (sx - _csegw//2, _csegy, _csegw, int(bl*0.22)),
                             max(1, int(s)), border_radius=max(1, int(3*s)))
        # Center ridge down carapace
        pygame.draw.line(surface, (80, 35, 3),
                         (sx, sy + int(2*s)), (sx, sy + int(bl*0.9)), max(1, int(2*s)))
        # Pauldron shoulder armor
        for _sdir in [-1, 1]:
            pygame.draw.ellipse(surface, (120, 55, 10),
                                (sx + _sdir*int(8*s), sy - int(6*s), int(14*s), int(10*s)))
            pygame.draw.ellipse(surface, (165, 80, 20),
                                (sx + _sdir*int(8*s), sy - int(6*s), int(14*s), int(10*s)),
                                max(1, int(s)))
        # Stinger tail arcing over body (thicker, segmented)
        tail_pts = [
            (wx, wy),
            (wx + facing * int(8*s), wy - int(20*s)),
            (wx + facing * int(20*s), wy - int(40*s)),
            (wx + facing * int(24*s), wy - int(58*s)),
            (wx + facing * int(18*s), wy - int(74*s)),
        ]
        pygame.draw.lines(surface, (100, 42, 4), False, tail_pts, max(4, int(6*s)))
        pygame.draw.lines(surface, (150, 70, 12), False, tail_pts, max(2, int(3*s)))
        # Tail segment rings
        for _tsi in range(len(tail_pts)-1):
            _tsx = (tail_pts[_tsi][0] + tail_pts[_tsi+1][0]) // 2
            _tsy = (tail_pts[_tsi][1] + tail_pts[_tsi+1][1]) // 2
            pygame.draw.circle(surface, (90, 38, 3), (_tsx, _tsy), max(4, int(5*s)), max(1, int(2*s)))
        # Stinger tip (barbed)
        stx, sty = tail_pts[-1]
        pygame.draw.polygon(surface, (200, 80, 10), [
            (stx, sty - int(10*s)),
            (stx - int(5*s), sty + int(5*s)),
            (stx + int(5*s), sty + int(5*s)),
        ])
        pygame.draw.polygon(surface, (240, 120, 30), [
            (stx, sty - int(10*s)),
            (stx - int(5*s), sty + int(5*s)),
            (stx + int(5*s), sty + int(5*s)),
        ], max(1, int(s)))
        # Venom drop at stinger
        pygame.draw.circle(surface, (120, 200, 40), (stx, sty - int(10*s)), max(2, int(3*s)))
        # Large pincer claws at hands
        for (hndx, hndy) in [(lhx, lhy), (rhx, rhy)]:
            # Claw base
            pygame.draw.circle(surface, (120, 52, 8), (hndx, hndy), max(6, int(8*s)))
            pygame.draw.circle(surface, (175, 80, 18), (hndx, hndy), max(6, int(8*s)), max(1, int(2*s)))
            # Upper claw arm
            pygame.draw.line(surface, (140, 60, 10),
                             (hndx, hndy),
                             (hndx + facing*int(10*s), hndy - int(8*s)), max(3, int(4*s)))
            pygame.draw.line(surface, (180, 90, 20),
                             (hndx, hndy),
                             (hndx + facing*int(10*s), hndy - int(8*s)), max(1, int(2*s)))
            # Lower claw arm
            pygame.draw.line(surface, (140, 60, 10),
                             (hndx, hndy),
                             (hndx + facing*int(10*s), hndy + int(6*s)), max(3, int(4*s)))
            pygame.draw.line(surface, (180, 90, 20),
                             (hndx, hndy),
                             (hndx + facing*int(10*s), hndy + int(6*s)), max(1, int(2*s)))
            # Claw tips
            for _ctt, _ctdy in [(-8, -10), (6, 8)]:
                pygame.draw.polygon(surface, (200, 100, 20), [
                    (hndx + facing*int(10*s), hndy + int(_ctt*s)),
                    (hndx + facing*int(14*s), hndy + int((_ctt-3)*s)),
                    (hndx + facing*int(14*s), hndy + int((_ctt+4)*s)),
                ])
        # Eight eye cluster on head
        for _eyi in range(4):
            _eya = math.pi * (0.15 + _eyi * 0.23)
            _eyrad = hd * 0.65
            for _eyoff in [-1, 1]:
                _eyox = int(math.cos(_eya) * _eyrad * _eyoff)
                pygame.draw.circle(surface, (220, 120, 10),
                                   (hx + _eyox, hy - int(hd*0.15)),
                                   max(2, int(3*s)))

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
        # Brown druidic robe on torso
        pygame.draw.rect(surface, (80, 60, 25),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (110, 85, 40),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Vine pattern on robe
        for _vi2 in range(3):
            _viy = sy + int(bl * (0.2 + _vi2 * 0.28))
            pygame.draw.arc(surface, (50, 140, 40),
                            (sx - int(7*s), _viy - int(4*s), int(14*s), int(10*s)),
                            math.radians(0), math.radians(180), max(1, int(s)))
        # Leaf crown on head
        for li in range(5):
            la = math.radians(-80 + li * 40)
            lx = hx + int(math.cos(la) * hd)
            ly = hy - hd + int(math.sin(la) * hd)
            pygame.draw.ellipse(surface, (30, 160, 50),
                                (lx - int(5*s), ly - int(8*s), int(10*s), int(16*s)))
            pygame.draw.ellipse(surface, (20, 120, 35),
                                (lx - int(5*s), ly - int(8*s), int(10*s), int(16*s)), max(1, int(s)))
        # Wooden staff in leading hand (with gnarled top)
        staff_x = rhx + facing * int(4*s)
        pygame.draw.line(surface, (100, 65, 20), (staff_x, rhy - int(45*s)), (staff_x, rhy + int(25*s)), max(2, int(3*s)))
        # Gnarled branch at top
        pygame.draw.line(surface, (80, 50, 15),
                         (staff_x, rhy - int(45*s)),
                         (staff_x + facing*int(8*s), rhy - int(52*s)), max(2, int(3*s)))
        # Glowing nature orb
        pygame.draw.circle(surface, (60, 200, 80), (staff_x, rhy - int(45*s)), max(4, int(6*s)))
        pygame.draw.circle(surface, (180, 255, 180), (staff_x, rhy - int(45*s)), max(2, int(3*s)))
        # Bark-brown belt
        pygame.draw.rect(surface, (90, 55, 20),
                         (wx - int(hd*0.9), wy - int(3*s), int(hd*1.8), max(4, int(6*s))),
                         border_radius=max(1, int(2*s)))

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
        # "42" stamped on the chest — large, glowing
        _f42 = _get_font(max(14, int(22*s)))
        _lbl = _f42.render("42", True, (0, 255, 255))
        surface.blit(_lbl, (wx - _lbl.get_width()//2, wy - _lbl.get_height()//2 - int(bl*0.3)))
        # Galaxy swirl around the body (orbiting stars)
        _t42 = pygame.time.get_ticks()
        for _gi in range(8):
            _ga = math.radians(_gi * 45 + _t42 * 0.08)
            _gr = int(hd * 1.6) + int((_gi % 3) * 4 * s)
            _gcol = [(0,255,255),(100,200,255),(200,150,255),(100,255,200)][_gi % 4]
            pygame.draw.circle(surface, _gcol,
                               (hx + int(math.cos(_ga)*_gr), wy - int(hd) + int(math.sin(_ga)*int(_gr*0.6))),
                               max(1, int(3*s)))
        # Bathrobe/dressing gown pattern on torso
        pygame.draw.rect(surface, (30, 50, 80),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (60, 100, 140),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(1, int(2*s)))
        # Gown lapels
        pygame.draw.polygon(surface, (100, 150, 200), [
            (sx, sy + int(4*s)), (sx - int(7*s), sy + int(bl*0.55)), (sx - int(4*s), sy)
        ])
        pygame.draw.polygon(surface, (100, 150, 200), [
            (sx, sy + int(4*s)), (sx + int(7*s), sy + int(bl*0.55)), (sx + int(4*s), sy)
        ])
        # Towel/question-mark on head
        pygame.draw.ellipse(surface, (200, 180, 150),
                            (hx - int(hd*1.1), hy - hd - int(hd*0.5), int(hd*2.2), int(hd*0.6)))
        # "?" above head (where's my towel?)
        _qf2 = _get_font(max(8, int(12*s)))
        _qt2 = _qf2.render("?", True, (0, 255, 180))
        surface.blit(_qt2, (hx - _qt2.get_width()//2, hy - hd - int(hd*0.5) - _qt2.get_height()))

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
        # Tectonic earth-stone body armor
        pygame.draw.rect(surface, (90, 60, 28),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(4*s)))
        # Tectonic plate slab segments (offset, shifted)
        for _tpi in range(3):
            _tpshift = int((_tpi % 2 * 2 - 1) * 4 * s)
            _tpy = sy + int(bl * (_tpi * 0.32))
            _tph = int(bl * 0.3)
            pygame.draw.rect(surface, (115, 80, 38),
                             (sx - int(10*s) + _tpshift, _tpy, int(20*s), _tph),
                             border_radius=max(1, int(3*s)))
            pygame.draw.rect(surface, (145, 105, 55),
                             (sx - int(10*s) + _tpshift, _tpy, int(20*s), _tph),
                             max(1, int(s)), border_radius=max(1, int(3*s)))
        # Fault crack network on torso
        crack_pts = [(sx, sy + int(bl*0.08)), (sx - int(5*s), sy + int(bl*0.32)),
                     (sx + int(4*s), sy + int(bl*0.55)), (sx - int(3*s), sy + int(bl*0.8))]
        for i in range(len(crack_pts) - 1):
            pygame.draw.line(surface, (55, 35, 10), crack_pts[i], crack_pts[i+1], max(2, int(3*s)))
            pygame.draw.line(surface, (200, 140, 40), crack_pts[i], crack_pts[i+1], max(1, int(s)))
        # Side crack branches
        for _bci, _bcpt in enumerate(crack_pts[1:3]):
            pygame.draw.line(surface, (55, 35, 10),
                             _bcpt,
                             (_bcpt[0] + int((_bci*2-1)*8*s), _bcpt[1] + int(5*s)), max(1, int(s)))
        # Lava glow in cracks
        _glowsurf = pygame.Surface((int(24*s)+1, int(bl)+1), pygame.SRCALPHA)
        for _glowi in range(len(crack_pts)-1):
            _gx1 = crack_pts[_glowi][0] - (sx - int(11*s))
            _gy1 = crack_pts[_glowi][1] - sy
            _gx2 = crack_pts[_glowi+1][0] - (sx - int(11*s))
            _gy2 = crack_pts[_glowi+1][1] - sy
            pygame.draw.line(_glowsurf, (255, 120, 0, 100),
                             (_gx1, _gy1), (_gx2, _gy2), max(3, int(4*s)))
        surface.blit(_glowsurf, (sx - int(11*s), sy))
        # Massive rocky shoulder chunks
        for side in (-1, 1):
            rx = sx + side * int(10*s)
            pygame.draw.polygon(surface, (105, 72, 35), [
                (rx - int(6*s), sy + int(2*s)),
                (rx + int(6*s), sy + int(2*s)),
                (rx + int(4*s), sy - int(14*s)),
                (rx + int(1*s), sy - int(18*s)),
                (rx - int(4*s), sy - int(12*s)),
            ])
            pygame.draw.polygon(surface, (140, 100, 50), [
                (rx - int(6*s), sy + int(2*s)),
                (rx + int(6*s), sy + int(2*s)),
                (rx + int(4*s), sy - int(14*s)),
                (rx + int(1*s), sy - int(18*s)),
                (rx - int(4*s), sy - int(12*s)),
            ], max(1, int(s)))
            # Rock surface cracks on shoulder
            pygame.draw.line(surface, (55, 35, 10),
                             (rx - int(2*s), sy - int(4*s)),
                             (rx + int(4*s), sy - int(10*s)), max(1, int(s)))
        # Stone fists with rubble
        for _sfx2, _sfy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (100, 68, 30), (_sfx2, _sfy2), max(6, int(9*s)))
            pygame.draw.circle(surface, (140, 98, 48), (_sfx2, _sfy2), max(6, int(9*s)), max(1, int(2*s)))
            # Pebble chips around fist
            for _pbi in range(4):
                _pba = _pbi * math.pi * 0.5 + 0.3
                pygame.draw.circle(surface, (85, 58, 22),
                                   (_sfx2 + int(math.cos(_pba)*9*s), _sfy2 + int(math.sin(_pba)*9*s)),
                                   max(2, int(3*s)))
        # Heavy stone brow ridge
        pygame.draw.line(surface, (85, 58, 22),
                         (hx - hd, hy - int(hd*0.18)), (hx + hd, hy - int(hd*0.18)),
                         max(3, int(4*s)))
        pygame.draw.line(surface, (120, 85, 42),
                         (hx - hd, hy - int(hd*0.18)), (hx + hd, hy - int(hd*0.18)),
                         max(1, int(2*s)))
        # Ground fissure radiating from feet
        for _gfi in range(5):
            _gfa = math.pi * (0.05 + _gfi * 0.22)
            pygame.draw.line(surface, (80, 50, 15),
                             (wx, wy + int(4*s)),
                             (wx + int(math.cos(_gfa)*18*s), wy + int(4*s) + int(math.sin(_gfa)*10*s)),
                             max(1, int(s)))

    elif char_name == "Buckler":
        # Chain mail shirt on torso
        for _cmi in range(4):
            for _cmj in range(3):
                _cmx = sx - int(8*s) + _cmj*int(6*s) + (_cmi%2)*int(3*s)
                _cmy = sy + int(bl*(0.08 + _cmi*0.23))
                pygame.draw.ellipse(surface, (80, 100, 80),
                                    (_cmx - int(3*s), _cmy - int(2*s), int(6*s), int(4*s)),
                                    max(1, int(s)))
        # Green-painted chest plate over mail
        pygame.draw.rect(surface, (40, 110, 55),
                         (sx - int(8*s), sy + int(bl*0.08), int(16*s), int(bl*0.55)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (65, 150, 80),
                         (sx - int(8*s), sy + int(bl*0.08), int(16*s), int(bl*0.55)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Heraldic cross on chest plate
        pygame.draw.line(surface, (80, 170, 100),
                         (sx, sy + int(bl*0.12)), (sx, sy + int(bl*0.6)), max(2, int(2*s)))
        pygame.draw.line(surface, (80, 170, 100),
                         (sx - int(7*s), sy + int(bl*0.32)), (sx + int(7*s), sy + int(bl*0.32)),
                         max(2, int(2*s)))
        # Pauldron shoulder guard
        for _bgdir in [-1, 1]:
            pygame.draw.ellipse(surface, (45, 115, 58),
                                (sx + _bgdir*int(7*s), sy - int(5*s), int(12*s), int(9*s)))
            pygame.draw.ellipse(surface, (70, 155, 85),
                                (sx + _bgdir*int(7*s), sy - int(5*s), int(12*s), int(9*s)),
                                max(1, int(s)))
        # Right-hand sword (simple)
        pygame.draw.line(surface, (180, 185, 195),
                         (rhx, rhy), (rhx + facing*int(3*s), rhy - int(24*s)), max(2, int(3*s)))
        pygame.draw.line(surface, (220, 225, 235),
                         (rhx, rhy), (rhx + facing*int(3*s), rhy - int(24*s)), max(1, int(s)))
        # Cross-guard
        pygame.draw.line(surface, (160, 130, 50),
                         (rhx - int(6*s), rhy - int(6*s)),
                         (rhx + int(6*s), rhy - int(6*s)), max(2, int(3*s)))
        # Grip
        pygame.draw.line(surface, (100, 70, 30),
                         (rhx, rhy), (rhx, rhy + int(8*s)), max(2, int(3*s)))
        # Large kite shield on left arm — fully decorated
        shld_r = max(10, int(15*s))
        pygame.draw.ellipse(surface, (40, 110, 55),
                            (lhx - shld_r, lhy - int(shld_r*1.4), shld_r*2, int(shld_r*2.8)))
        pygame.draw.ellipse(surface, (65, 150, 80),
                            (lhx - shld_r, lhy - int(shld_r*1.4), shld_r*2, int(shld_r*2.8)),
                            max(2, int(3*s)))
        # Shield cross heraldry
        pygame.draw.line(surface, (90, 170, 105),
                         (lhx, lhy - int(shld_r*1.2)), (lhx, lhy + int(shld_r*1.2)), max(2, int(2*s)))
        pygame.draw.line(surface, (90, 170, 105),
                         (lhx - int(shld_r*0.7), lhy), (lhx + int(shld_r*0.7), lhy), max(2, int(2*s)))
        # Shield boss (center boss knob)
        pygame.draw.circle(surface, (160, 130, 50), (lhx, lhy), max(3, int(5*s)))
        pygame.draw.circle(surface, (200, 170, 80), (lhx, lhy), max(3, int(5*s)), max(1, int(s)))
        # Full nasal helmet with cheek guards
        pygame.draw.rect(surface, (50, 125, 68),
                         (hx - hd, hy - hd, hd*2, hd + int(4*s)), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (75, 160, 92),
                         (hx - hd, hy - hd, hd*2, hd + int(4*s)), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Nasal guard
        pygame.draw.line(surface, (38, 100, 52),
                         (hx, hy - hd), (hx, hy + int(2*s)), max(3, int(4*s)))
        # Cheek guards
        for _cgdir in [-1, 1]:
            pygame.draw.rect(surface, (45, 112, 60),
                             (hx + _cgdir*int(hd*0.7), hy - int(hd*0.4),
                              int(hd*0.4), int(hd*0.7)), border_radius=max(1, int(2*s)))
        # Helmet plume
        pygame.draw.line(surface, (200, 30, 30),
                         (hx, hy - hd),
                         (hx + facing*int(4*s), hy - hd - int(12*s)), max(2, int(3*s)))
        pygame.draw.line(surface, (240, 60, 60),
                         (hx, hy - hd),
                         (hx + facing*int(4*s), hy - hd - int(12*s)), max(1, int(s)))

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
        # Ghost afterimage silhouettes behind (2 faded copies offset back)
        _pssurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for _psi2, _psoff in enumerate([facing*int(18*s), facing*int(32*s)]):
            _psa = 35 - _psi2*15
            pygame.draw.circle(_pssurf, (40, 40, 180, _psa), (hx - _psoff, hy), hd)
            pygame.draw.line(_pssurf, (40, 40, 180, _psa),
                             (sx - _psoff, sy), (wx - _psoff, wy), max(2, int(3*s)))
            pygame.draw.line(_pssurf, (40, 40, 180, _psa),
                             (sx - _psoff, sy + int(bl*0.15)), (lhx - _psoff, lhy), max(2, int(2*s)))
            pygame.draw.line(_pssurf, (40, 40, 180, _psa),
                             (sx - _psoff, sy + int(bl*0.15)), (rhx - _psoff, rhy), max(2, int(2*s)))
        surface.blit(_pssurf, (0, 0))
        # Dark blue cloak — flowing with layered depth
        cloak_pts = [
            (hx - hd - int(3*s), hy + int(hd*0.5)),
            (hx - int(10*s), wy + int(bl*0.42)),
            (wx, wy + int(bl*0.6)),
            (hx + int(10*s), wy + int(bl*0.42)),
            (hx + hd + int(3*s), hy + int(hd*0.5)),
        ]
        pygame.draw.polygon(surface, (12, 12, 80), cloak_pts)
        pygame.draw.polygon(surface, (50, 50, 160), cloak_pts, max(2, int(3*s)))
        # Inner cloak sheen
        _inner_pts = [
            (hx - int(hd*0.5), hy + int(hd*0.5)),
            (hx - int(5*s), wy + int(bl*0.35)),
            (wx, wy + int(bl*0.5)),
            (hx + int(5*s), wy + int(bl*0.35)),
            (hx + int(hd*0.5), hy + int(hd*0.5)),
        ]
        pygame.draw.polygon(surface, (20, 20, 100), _inner_pts)
        # Ragged cloak hem (torn wisps)
        for _cwi in range(5):
            _cwx = wx - int(8*s) + _cwi * int(4*s)
            _cwlen = int((6 + _cwi % 3 * 4) * s)
            pygame.draw.line(surface, (40, 40, 140),
                             (_cwx, wy + int(bl*0.55)),
                             (_cwx + int((_cwi-2)*2*s), wy + int(bl*0.55) + _cwlen), max(1, int(s)))
        # Shadow wisps floating around body
        for _swi in range(4):
            _swa = math.pi * (0.2 + _swi * 0.5)
            _swx = sx + int(math.cos(_swa) * 16 * s)
            _swy = sy + int(bl*0.4) + int(math.sin(_swa) * 12 * s)
            pygame.draw.circle(surface, (30, 30, 120), (_swx, _swy), max(3, int(4*s)))
        # Dark hood pulled up
        pygame.draw.ellipse(surface, (15, 15, 90),
                            (hx - int(hd*1.2), hy - hd - int(6*s), int(hd*2.4), int(hd*1.5)))
        pygame.draw.ellipse(surface, (50, 50, 150),
                            (hx - int(hd*1.2), hy - hd - int(6*s), int(hd*2.4), int(hd*1.5)),
                            max(1, int(2*s)))
        # Face shadow (deep darkness with only eyes visible)
        pygame.draw.ellipse(surface, (5, 5, 40),
                            (hx - int(hd*0.8), hy - int(hd*0.7), int(hd*1.6), int(hd*1.3)))
        # Glowing blue eyes piercing through darkness
        for _eox in (-1, 1):
            pygame.draw.circle(surface, (60, 60, 220), (hx + _eox*int(hd*0.32), hy - int(hd*0.1)),
                               max(3, int(5*s)))
            pygame.draw.circle(surface, (140, 140, 255), (hx + _eox*int(hd*0.32), hy - int(hd*0.1)),
                               max(2, int(3*s)))
            pygame.draw.circle(surface, (220, 220, 255), (hx + _eox*int(hd*0.32), hy - int(hd*0.1)),
                               max(1, int(2*s)))
        # Spectral blade in right hand
        _sbx = rhx + facing*int(5*s)
        _sby = rhy
        pygame.draw.line(surface, (40, 40, 160),
                         (_sbx, _sby), (_sbx + facing*int(4*s), _sby - int(26*s)), max(3, int(4*s)))
        pygame.draw.line(surface, (100, 100, 240),
                         (_sbx, _sby), (_sbx + facing*int(4*s), _sby - int(26*s)), max(2, int(2*s)))
        pygame.draw.line(surface, (200, 200, 255),
                         (_sbx, _sby), (_sbx + facing*int(4*s), _sby - int(26*s)), max(1, int(s)))
        # Blade tip glow
        _btx = _sbx + facing*int(4*s)
        _bty = _sby - int(26*s)
        pygame.draw.circle(surface, (120, 120, 255), (_btx, _bty), max(3, int(4*s)))
        # Trailing shadow on fists
        for _fhx2, _fhy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (25, 25, 100), (_fhx2, _fhy2), max(5, int(7*s)), max(1, int(2*s)))

    elif char_name == "Trap Master":
        # Dark tactical vest on torso
        pygame.draw.rect(surface, (40, 45, 35),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (65, 72, 55),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Tactical vest pockets (3 columns)
        for _vpi in range(3):
            for _vpj in range(2):
                _vpx = sx - int(7*s) + _vpj*int(8*s)
                _vpy = sy + int(bl*(0.1 + _vpi*0.28))
                pygame.draw.rect(surface, (30, 35, 25),
                                 (_vpx, _vpy, int(6*s), int(6*s)), border_radius=max(1, int(s)))
                pygame.draw.rect(surface, (55, 62, 45),
                                 (_vpx, _vpy, int(6*s), int(6*s)), max(1, int(s)), border_radius=max(1, int(s)))
        # Vest cross-strap
        pygame.draw.line(surface, (55, 62, 45),
                         (sx - int(8*s), sy + int(bl*0.05)),
                         (sx + int(8*s), sy + int(bl*0.55)), max(1, int(2*s)))
        # Heavy utility belt on waist
        pygame.draw.rect(surface, (65, 48, 15),
                         (sx - int(12*s), wy - int(4*s), int(24*s), max(5, int(8*s))),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (95, 72, 25),
                         (sx - int(12*s), wy - int(4*s), int(24*s), max(5, int(8*s))),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Belt buckle
        pygame.draw.rect(surface, (160, 140, 60),
                         (sx - int(4*s), wy - int(3*s), int(8*s), max(4, int(6*s))),
                         border_radius=max(1, int(s)))
        # Belt pouches
        for _bpside in (-1, 1):
            _bppx = sx + _bpside * int(8*s)
            pygame.draw.rect(surface, (50, 38, 12),
                             (_bppx - int(3*s), wy - int(6*s), int(7*s), int(10*s)),
                             border_radius=max(1, int(s)))
            pygame.draw.rect(surface, (80, 62, 22),
                             (_bppx - int(3*s), wy - int(6*s), int(7*s), int(10*s)),
                             max(1, int(s)), border_radius=max(1, int(s)))
            # Pouch flap
            pygame.draw.line(surface, (50, 38, 12),
                             (_bppx - int(3*s), wy - int(2*s)), (_bppx + int(4*s), wy - int(2*s)),
                             max(1, int(s)))
        # Bear trap held in left hand
        _btx2, _bty2 = lhx, lhy
        # Trap jaws
        pygame.draw.arc(surface, (120, 120, 130),
                        (_btx2 - int(8*s), _bty2 - int(10*s), int(16*s), int(12*s)),
                        math.pi * 0.1, math.pi * 0.9, max(2, int(3*s)))
        pygame.draw.arc(surface, (120, 120, 130),
                        (_btx2 - int(8*s), _bty2 - int(3*s), int(16*s), int(12*s)),
                        math.pi * 1.1, math.pi * 1.9, max(2, int(3*s)))
        # Trap teeth
        for _tti in range(5):
            _ttx = _btx2 - int(6*s) + _tti * int(3*s)
            pygame.draw.line(surface, (160, 160, 170),
                             (_ttx, _bty2 - int(4*s)), (_ttx, _bty2 - int(8*s)), max(1, int(s)))
        # Trap spring center
        pygame.draw.circle(surface, (100, 100, 110), (_btx2, _bty2 - int(5*s)), max(3, int(4*s)))
        # Wire spool on back (behind torso)
        _wspool_x = sx - facing*int(12*s)
        _wspool_y = sy + int(bl*0.3)
        pygame.draw.circle(surface, (60, 50, 30), (_wspool_x, _wspool_y), max(5, int(7*s)))
        pygame.draw.circle(surface, (90, 78, 45), (_wspool_x, _wspool_y), max(5, int(7*s)), max(1, int(2*s)))
        pygame.draw.circle(surface, (70, 60, 35), (_wspool_x, _wspool_y), max(2, int(3*s)))
        # Wire line from spool to left hand
        pygame.draw.line(surface, (90, 90, 90),
                         (_wspool_x, _wspool_y), (lhx, lhy), max(1, int(s)))
        # Shovel / digging tool in right hand
        pygame.draw.line(surface, (80, 58, 22), (rhx, rhy), (rhx + facing*int(5*s), rhy - int(20*s)),
                         max(2, int(3*s)))
        pygame.draw.ellipse(surface, (65, 48, 18),
                            (rhx + facing*int(2*s) - int(4*s), rhy - int(24*s), int(9*s), int(6*s)))
        pygame.draw.ellipse(surface, (110, 90, 40),
                            (rhx + facing*int(2*s) - int(4*s), rhy - int(24*s), int(9*s), int(6*s)),
                            max(1, int(s)))
        # Hard hat — full dome with brim
        pygame.draw.ellipse(surface, (90, 70, 25),
                            (hx - int(hd*1.2), hy - hd - int(5*s), int(hd*2.4), int(hd*1.3)))
        pygame.draw.ellipse(surface, (120, 95, 38),
                            (hx - int(hd*1.2), hy - hd - int(5*s), int(hd*2.4), int(hd*1.3)),
                            max(1, int(2*s)))
        pygame.draw.ellipse(surface, (85, 65, 22),
                            (hx - int(hd*1.5), hy - hd, int(hd*3), int(6*s)))
        # Headlamp on hat
        pygame.draw.rect(surface, (50, 50, 60),
                         (hx - int(4*s), hy - hd - int(4*s), int(8*s), int(6*s)),
                         border_radius=max(1, int(s)))
        pygame.draw.circle(surface, (220, 220, 180), (hx, hy - hd - int(1*s)), max(2, int(3*s)))

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
        # Desert mirage robes — layered flowing cloth
        pygame.draw.rect(surface, (190, 170, 120),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(4*s)))
        # Sand-coloured inner cloth layers
        for _mli in range(3):
            _mlw = int((18 - _mli*4)*s)
            _mly = sy + int(bl*(0.1 + _mli*0.28))
            pygame.draw.rect(surface, (210, 195, 145),
                             (sx - _mlw//2, _mly, _mlw, int(bl*0.25)),
                             border_radius=max(1, int(3*s)))
        # Heat shimmer wave lines on robes
        t_mg = pygame.time.get_ticks()
        for ri in range(5):
            wave = math.sin(t_mg * 0.004 + ri * 1.1) * int(4*s)
            ry = sy + int(bl * (0.12 + ri * 0.18))
            pygame.draw.line(surface, (160, 220, 235),
                             (sx - int(9*s) + int(wave), ry),
                             (sx + int(9*s) + int(wave), ry),
                             max(1, int(s)))
        # Ghost duplicate — faded offset copy
        _mgsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for _mgi, _mgoff in enumerate([facing*int(14*s), -facing*int(12*s)]):
            _mga = 30 - _mgi*12
            pygame.draw.circle(_mgsurf, (140, 200, 220, _mga), (hx + _mgoff, hy), hd)
            pygame.draw.line(_mgsurf, (140, 200, 220, _mga),
                             (sx + _mgoff, sy), (wx + _mgoff, wy), max(2, int(3*s)))
            pygame.draw.line(_mgsurf, (140, 200, 220, _mga),
                             (sx + _mgoff, sy + int(bl*0.15)), (lhx + _mgoff, lhy), max(1, int(2*s)))
            pygame.draw.line(_mgsurf, (140, 200, 220, _mga),
                             (sx + _mgoff, sy + int(bl*0.15)), (rhx + _mgoff, rhy), max(1, int(2*s)))
        surface.blit(_mgsurf, (0, 0))
        # Desert headwrap / keffiyeh
        pygame.draw.ellipse(surface, (200, 185, 135),
                            (hx - int(hd*1.15), hy - hd - int(2*s), int(hd*2.3), int(hd*1.4)))
        pygame.draw.ellipse(surface, (225, 215, 165),
                            (hx - int(hd*1.15), hy - hd - int(2*s), int(hd*2.3), int(hd*1.4)),
                            max(1, int(2*s)))
        # Headband stripe
        pygame.draw.line(surface, (80, 140, 160),
                         (hx - int(hd*1.0), hy - hd + int(5*s)),
                         (hx + int(hd*1.0), hy - hd + int(5*s)), max(2, int(2*s)))
        # Trailing fabric wrap off head
        pygame.draw.line(surface, (195, 180, 130),
                         (hx - facing*int(hd*0.8), hy + int(hd*0.4)),
                         (hx - facing*int(hd*1.6), hy + int(hd*0.8) + int(bl*0.2)),
                         max(3, int(4*s)))
        # Veil across lower face (shimmering)
        pygame.draw.arc(surface, (120, 190, 215),
                        (hx - hd + int(2*s), hy, hd*2 - int(4*s), hd - int(2*s)),
                        math.radians(0), math.radians(180), max(2, int(3*s)))
        pygame.draw.arc(surface, (170, 230, 245),
                        (hx - hd + int(4*s), hy + int(2*s), hd*2 - int(8*s), hd - int(5*s)),
                        math.radians(0), math.radians(180), max(1, int(s)))
        # Heat shimmer halo around head
        _halosurf = pygame.Surface((hd*5, hd*5), pygame.SRCALPHA)
        pygame.draw.ellipse(_halosurf, (140, 210, 230, 30), (0, 0, hd*5, hd*5))
        surface.blit(_halosurf, (hx - hd*2 - hd//2, hy - hd*2 - hd//2))
        # Glimmering mirage eyes
        for _mex, _mey in [(hx - int(hd*0.3), hy - int(hd*0.1)), (hx + int(hd*0.3), hy - int(hd*0.1))]:
            pygame.draw.circle(surface, (200, 240, 255), (_mex, _mey), max(3, int(4*s)))
            pygame.draw.circle(surface, (100, 200, 230), (_mex, _mey), max(2, int(3*s)))
            pygame.draw.circle(surface, (220, 250, 255), (_mex - int(s), _mey - int(s)), max(1, int(s)))

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

    elif char_name == "Orb Shooter":
        # Sleek blue/silver sci-fi jumpsuit on torso
        pygame.draw.rect(surface, (20, 40, 90),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 100, 180),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Silver center stripe down suit
        pygame.draw.rect(surface, (160, 200, 240),
                         (sx - int(2*s), sy + int(3*s), int(4*s), bl - int(6*s)),
                         border_radius=max(1, int(2*s)))
        # Energy power pack circles on chest
        for _epi, (_epox, _epoy) in enumerate([(-5, 0.2), (5, 0.2), (0, 0.45)]):
            _epcol = (80, 160, 255) if _epi < 2 else (100, 220, 255)
            _epx = sx + int(_epox * s)
            _epy = sy + int(bl * _epoy)
            pygame.draw.circle(surface, _epcol, (_epx, _epy), max(2, int(4*s)))
            pygame.draw.circle(surface, (200, 240, 255), (_epx, _epy), max(1, int(2*s)))
        # Tech panel lines on suit
        for _tpi in range(3):
            _tpy = sy + int(bl * (0.55 + _tpi * 0.14))
            pygame.draw.line(surface, (80, 140, 220),
                             (sx - int(7*s), _tpy), (sx + int(7*s), _tpy), max(1, int(s)))
        # Glowing blue gauntlets on both hands
        for _gx3, _gy3 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.rect(surface, (20, 60, 160),
                             (_gx3 - int(6*s), _gy3 - int(5*s), int(12*s), int(10*s)),
                             border_radius=max(2, int(3*s)))
            pygame.draw.rect(surface, (80, 160, 255),
                             (_gx3 - int(6*s), _gy3 - int(5*s), int(12*s), int(10*s)),
                             max(1, int(s)), border_radius=max(2, int(3*s)))
            # Gauntlet glow dot
            pygame.draw.circle(surface, (180, 230, 255), (_gx3, _gy3), max(2, int(3*s)))
        # Sci-fi visor across eyes
        pygame.draw.ellipse(surface, (60, 140, 255),
                            (hx - int(hd*0.9), hy - int(hd*0.2), int(hd*1.8), int(hd*0.7)))
        pygame.draw.ellipse(surface, (160, 210, 255),
                            (hx - int(hd*0.9), hy - int(hd*0.2), int(hd*1.8), int(hd*0.7)), max(1, int(2*s)))
        # Visor highlight
        pygame.draw.line(surface, (220, 240, 255),
                         (hx - int(hd * 0.7), hy - int(hd * 0.05)),
                         (hx + int(hd * 0.4), hy - int(hd * 0.05)), max(1, int(s)))
        # Charged orb held in right hand
        pygame.draw.circle(surface, (60, 120, 255), (rhx, rhy), max(5, int(7*s)))
        pygame.draw.circle(surface, (140, 200, 255), (rhx, rhy), max(3, int(5*s)), max(1, int(s)))
        pygame.draw.circle(surface, (220, 240, 255), (rhx, rhy), max(1, int(2*s)))

    elif char_name == "<|-\\||>+()":
        # Heavily corrupted glitch body
        # Base broken torso rect layers (RGB channel split)
        for _goff2, _gcol2 in [
            ((-4, -2), (0, 255, 200, 80)),
            ((5,  1), (255, 0, 220, 80)),
            ((0,  4), (180, 0, 255, 80)),
        ]:
            _glsurf = pygame.Surface((int(22*s)+1, int(bl)+1), pygame.SRCALPHA)
            pygame.draw.rect(_glsurf, _gcol2, (int(_goff2[0]*s), int(_goff2[1]*s), int(22*s), int(bl)))
            surface.blit(_glsurf, (sx - int(11*s), sy))
        # Horizontal scan-line tears
        for _sli in range(7):
            _sly = sy + int(bl * (_sli / 7.0))
            _sllen = int((8 + _sli % 3 * 6) * s)
            _slx = sx - int(10*s) + int((_sli*7) % 12 * s)
            pygame.draw.line(surface, [(0,255,200),(255,0,220),(180,0,255),(255,255,0)][_sli%4],
                             (_slx, _sly), (_slx + _sllen, _sly), max(1, int(s)))
        # Scattered random pixel blocks around body
        for _pbi2, (_pbx, _pby, _pbc) in enumerate([
            (-14,  4, (0,255,180)),   ( 14,  8, (255,0,180)),
            (-12, 22, (180,0,255)),   ( 16, 28, (0,255,255)),
            (-10, 36, (255,255,0)),   ( 12, 14, (255,0,100)),
            (-16, 48, (0,180,255)),
        ]):
            pygame.draw.rect(surface, _pbc,
                             (sx + int(_pbx*s), sy + int(_pby*s),
                              max(3, int((3+_pbi2%3*2)*s)), max(2, int((2+_pbi2%2*3)*s))))
        # Corrupted arm outlines (offset ghost arms)
        for _cax, _cay, _cex, _cey in [
            (sx, sy+int(bl*0.15), lhx, lhy), (sx, sy+int(bl*0.15), rhx, rhy)]:
            pygame.draw.line(surface, (0, 240, 200),
                             (_cax - int(3*s), _cay), (_cex - int(3*s), _cey), max(1, int(s)))
            pygame.draw.line(surface, (255, 0, 200),
                             (_cax + int(3*s), _cay), (_cex + int(3*s), _cey), max(1, int(s)))
        # Glitch pixel blocks around head
        for _gi2, (_gox2, _goy2, _gc2) in enumerate([
            (-1, 0,(0,255,180)), (1, 0,(255,0,180)), (0,-1,(180,0,255)),
            (-1,-1,(255,255,0)), (1,-1,(0,200,255)), (0, 1,(255,100,0)),
        ]):
            _bx2 = hx + _gox2 * int(hd*1.2)
            _by2 = hy + _goy2 * int(hd*0.9)
            pygame.draw.rect(surface, _gc2,
                             (_bx2 - int((3+_gi2%2*2)*s), _by2 - int((2+_gi2%3*s)),
                              int((6+_gi2%3*2)*s), int((5+_gi2%2*2)*s)))
        # Large corrupted X eyes
        for _ceox in (-1, 1):
            _cex2 = hx + _ceox * int(hd*0.32)
            _cey2 = hy - int(hd*0.1)
            pygame.draw.line(surface, (255, 0, 100),
                             (_cex2 - int(5*s), _cey2 - int(5*s)),
                             (_cex2 + int(5*s), _cey2 + int(5*s)), max(2, int(2*s)))
            pygame.draw.line(surface, (255, 0, 100),
                             (_cex2 + int(5*s), _cey2 - int(5*s)),
                             (_cex2 - int(5*s), _cey2 + int(5*s)), max(2, int(2*s)))
        # Character name as mangled text on chest
        _gf2 = _get_font(max(6, int(8*s)))
        _gt = _gf2.render("|>+(", True, (0, 255, 180))
        surface.blit(_gt, (sx - _gt.get_width()//2, sy + int(bl*0.5)))

    elif char_name == "Death Defyer":
        # Tattered half-cloak (not a full reaper — defiant survivor)
        for _ci in range(3):
            _cy = sy + int(bl * 0.3 * _ci)
            pygame.draw.line(surface, (180, 200, 230),
                             (sx, _cy),
                             (sx - facing * int((10 + _ci*4)*s), _cy + int(10*s)),
                             max(1, int(2*s)))
        # Glowing halo (half-cracked — survived death)
        pygame.draw.circle(surface, (220, 240, 255),
                           (hx, hy - hd - int(5*s)), int(hd*0.9), max(1, int(2*s)))
        pygame.draw.arc(surface, (255, 255, 200),
                        (hx - int(hd*0.9), hy - hd - int(5*s) - int(hd*0.9),
                         int(hd*1.8), int(hd*1.8)),
                        0, math.pi, max(1, int(2*s)))
        # Skull eye on face
        pygame.draw.circle(surface, (200, 220, 255),
                           (hx - facing*int(hd*0.3), hy), max(2, int(3*s)))

    elif char_name == "Copycat":
        # Patchwork costume stitched from multiple character colors
        _ccols = [(200, 40, 40), (40, 100, 200), (40, 160, 60), (160, 60, 200), (200, 160, 20)]
        for _cci in range(5):
            _ccx = sx - int(10*s) + (_cci % 3) * int(7*s)
            _ccy = sy + int(bl * (0.05 + (_cci // 3) * 0.5))
            pygame.draw.rect(surface, _ccols[_cci],
                             (_ccx, _ccy, int(8*s), int(bl * 0.45)),
                             border_radius=max(1, int(2*s)))
        # Stitching lines between patches
        for _sti in range(4):
            _stx = sx - int(8*s) + _sti * int(5*s)
            for _stdy in range(0, int(bl), max(4, int(6*s))):
                pygame.draw.line(surface, (240, 240, 200),
                                 (_stx, sy + _stdy), (_stx, sy + _stdy + int(3*s)), max(1, int(s)))
        # Ghost copy silhouette offset behind
        _ccsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        _ccoff = facing * int(16*s)
        pygame.draw.circle(_ccsurf, (200, 200, 230, 50), (hx + _ccoff, hy), hd)
        pygame.draw.line(_ccsurf, (200, 200, 230, 50),
                         (sx + _ccoff, sy), (wx + _ccoff, wy), max(2, int(3*s)))
        surface.blit(_ccsurf, (0, 0))
        # Two overlapping translucent faces
        for _ci, _cof in enumerate((-1, 1)):
            _cx = hx + _cof * int(hd * 0.28)
            pygame.draw.circle(surface, (160 + _ci*40, 160 + _ci*40, 180),
                               (_cx, hy), hd, max(2, int(3*s)))
        # Mirror eyes — each eye is a different color
        pygame.draw.circle(surface, (220, 60, 60),
                           (hx - int(hd*0.35), hy - int(hd*0.1)), max(3, int(4*s)))
        pygame.draw.circle(surface, (60, 100, 220),
                           (hx + int(hd*0.35), hy - int(hd*0.1)), max(3, int(4*s)))
        # Mask divider line down face
        pygame.draw.line(surface, (200, 200, 220),
                         (hx, hy - hd + int(2*s)), (hx, hy + int(hd*0.6)), max(1, int(2*s)))
        # Question mark on forehead
        _qf = _get_font(max(8, int(14*s)))
        _qt = _qf.render("?", True, (220, 220, 255))
        surface.blit(_qt, (hx - _qt.get_width()//2, hy - hd - int(3*s)))
        # Morphing hand shapes (one per side)
        for _mhx, _mhy, _mhcol in [(lhx, lhy, (200, 60, 60)), (rhx, rhy, (60, 100, 220))]:
            pygame.draw.circle(surface, _mhcol, (_mhx, _mhy), max(5, int(7*s)))
            pygame.draw.circle(surface, (240, 240, 255), (_mhx, _mhy), max(5, int(7*s)), max(1, int(s)))

    elif char_name == "Windshield Viper":
        # Snake scales on torso
        for _si in range(3):
            _sy2 = sy + int(bl * 0.25 * _si)
            pygame.draw.ellipse(surface, (60, 180, 140),
                                (sx - int(8*s), _sy2 - int(4*s), int(16*s), int(9*s)),
                                max(1, int(s)))
        # Bubble visor on head
        pygame.draw.ellipse(surface, (100, 220, 200),
                            (hx - int(hd*0.85), hy - int(hd*0.35), int(hd*1.7), int(hd*0.75)),
                            max(1, int(2*s)))
        # Forked tongue
        _tx = hx + facing * hd
        pygame.draw.line(surface, (200, 80, 80),
                         (_tx, hy + int(2*s)),
                         (_tx + facing*int(8*s), hy + int(2*s)), max(1, int(s)))
        pygame.draw.line(surface, (200, 80, 80),
                         (_tx + facing*int(8*s), hy + int(2*s)),
                         (_tx + facing*int(12*s), hy - int(3*s)), max(1, int(s)))
        pygame.draw.line(surface, (200, 80, 80),
                         (_tx + facing*int(8*s), hy + int(2*s)),
                         (_tx + facing*int(12*s), hy + int(7*s)), max(1, int(s)))

    elif char_name == "Rainbow Snake":
        # Rainbow bands across body
        _rcols = [(255,60,60),(255,165,0),(255,255,0),(60,200,60),(60,100,255),(160,60,255)]
        for _ri, _rc in enumerate(_rcols):
            _ry = sy + int(bl * _ri / len(_rcols))
            pygame.draw.line(surface, _rc,
                             (sx - int(8*s), _ry), (sx + int(8*s), _ry),
                             max(1, int(3*s)))
        # Rainbow crown of scales on head
        for _ri, _rc in enumerate(_rcols[:4]):
            _angle = math.pi * 0.6 - _ri * math.pi * 0.3
            _rx = hx + int(math.cos(_angle) * hd * 1.05)
            _ry2 = hy - int(math.sin(_angle) * hd * 1.05)
            pygame.draw.circle(surface, _rc, (_rx, _ry2), max(2, int(3*s)))

    elif char_name == "Inland Taipan":
        # Brown/tan banded scales
        for _si in range(4):
            _sy2 = sy + int(bl * 0.22 * _si)
            _bc = (140 - _si*20, 100 - _si*15, 40)
            pygame.draw.ellipse(surface, _bc,
                                (sx - int(9*s), _sy2 - int(3*s), int(18*s), int(8*s)))
        # Menacing narrow eyes
        _ex = hx + facing * int(hd*0.35)
        pygame.draw.line(surface, (255, 50, 0),
                         (_ex - int(5*s), hy - int(2*s)),
                         (_ex + int(5*s), hy - int(2*s)), max(1, int(2*s)))
        # Venom drops from fang (right hand)
        for _vi in range(2):
            pygame.draw.circle(surface, (180, 255, 80),
                               (rhx + _vi*int(4*s), rhy + int(4*s)), max(2, int(2*s)))

    elif char_name == "Black Mamba":
        # Jet-black scales with iridescent sheen
        for _si in range(5):
            _sy2 = sy + int(bl * 0.18 * _si)
            pygame.draw.ellipse(surface, (20 + _si*5, 20 + _si*5, 30 + _si*8),
                                (sx - int(9*s), _sy2 - int(3*s), int(18*s), int(7*s)))
        # Speed streaks off limbs
        for _li, (_lx, _ly) in enumerate([(lhx, lhy), (rhx, rhy)]):
            pygame.draw.line(surface, (40, 40, 80),
                             (_lx, _ly),
                             (_lx - facing*int(12*s), _ly - int(4*s)), max(1, int(2*s)))
        # Black coffin-mouth marking
        pygame.draw.rect(surface, (5, 5, 5),
                         (hx - int(hd*0.4), hy, int(hd*0.8), int(hd*0.5)),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (40, 200, 120),
                         (hx - int(hd*0.4), hy, int(hd*0.8), int(hd*0.5)),
                         max(1, int(s)), border_radius=max(1, int(2*s)))

    elif char_name == "King Cobra":
        # Spread hood around head
        _hood_w = int(hd * 2.4)
        _hood_h = int(hd * 1.8)
        pygame.draw.ellipse(surface, (30, 110, 30),
                            (hx - _hood_w//2, hy - hd - int(_hood_h*0.3), _hood_w, _hood_h))
        pygame.draw.ellipse(surface, (60, 160, 60),
                            (hx - _hood_w//2, hy - hd - int(_hood_h*0.3), _hood_w, _hood_h),
                            max(1, int(2*s)))
        # Hood eye-spots
        for _hi, _hox in enumerate((-1, 1)):
            pygame.draw.circle(surface, (200, 255, 100),
                               (hx + _hox*int(hd*0.6), hy - int(hd*0.3)), max(3, int(4*s)))
            pygame.draw.circle(surface, (20, 20, 20),
                               (hx + _hox*int(hd*0.6), hy - int(hd*0.3)), max(1, int(2*s)))
        # Crown on top
        pygame.draw.polygon(surface, (255, 200, 0), [
            (hx - int(hd*0.5), hy - hd - int(_hood_h*0.3)),
            (hx - int(hd*0.2), hy - hd - int(_hood_h*0.3) - int(10*s)),
            (hx,               hy - hd - int(_hood_h*0.3) - int(6*s)),
            (hx + int(hd*0.2), hy - hd - int(_hood_h*0.3) - int(10*s)),
            (hx + int(hd*0.5), hy - hd - int(_hood_h*0.3)),
        ])

    elif char_name == "Entomologist":
        # White lab coat lapels
        for _lf in (-1, 1):
            pygame.draw.line(surface, (230, 230, 230),
                             (sx, sy + int(bl*0.1)),
                             (sx + _lf*int(9*s), wy - int(4*s)), max(1, int(2*s)))
        # Magnifying glass in right hand
        pygame.draw.circle(surface, (180, 220, 255),
                           (rhx, rhy - int(8*s)), max(5, int(7*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (150, 120, 80),
                         (rhx + int(4*s), rhy - int(4*s)),
                         (rhx + int(10*s), rhy + int(6*s)), max(2, int(3*s)))
        # Bug net on head (circle with mesh)
        pygame.draw.circle(surface, (180, 200, 180),
                           (hx, hy - hd - int(4*s)), int(hd*1.1), max(1, int(2*s)))
        pygame.draw.circle(surface, (200, 230, 200),
                           (hx, hy - hd - int(4*s)), int(hd*1.1) - max(1, int(2*s)),
                           max(1, int(s)))

    elif char_name == "Hacker":
        # Dark hoodie — shadow over top of head
        pygame.draw.ellipse(surface, (30, 20, 50),
                            (hx - int(hd*1.3), hy - hd - int(hd*0.8),
                             int(hd*2.6), int(hd*1.6)))
        # Glowing HUD visor (green scanline)
        pygame.draw.rect(surface, (0, 40, 0),
                         (hx - int(hd*0.8), hy - int(hd*0.2), int(hd*1.6), int(hd*0.5)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (0, 220, 80),
                         (hx - int(hd*0.8), hy - int(hd*0.2), int(hd*1.6), int(hd*0.5)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Scanline
        pygame.draw.line(surface, (0, 255, 100),
                         (hx - int(hd*0.7), hy),
                         (hx + int(hd*0.7), hy), max(1, int(s)))
        # Circuit trace on arm
        pygame.draw.line(surface, (0, 180, 60),
                         (sx, sy + int(bl*0.4)),
                         (sx + facing*int(al*0.5), sy + int(bl*0.4)), max(1, int(s)))

    elif char_name == "8-Bit Wasp":
        # Pixel-style yellow/black stripes
        for _wi in range(4):
            _wy2 = sy + int(bl * 0.22 * _wi)
            _wc = (20, 20, 20) if _wi % 2 == 0 else (255, 200, 0)
            pygame.draw.rect(surface, _wc,
                             (sx - int(9*s), _wy2, int(18*s), int(bl*0.2)))
        # Pixelated wings (rectangles)
        for _wf in (-1, 1):
            pygame.draw.rect(surface, (200, 230, 255),
                             (sx + _wf*int(5*s), sy + int(bl*0.1),
                              int(16*s), int(bl*0.35)), max(1, int(s)))
        # Stinger — pointed tail at waist
        pygame.draw.polygon(surface, (255, 160, 0), [
            (wx, wy),
            (wx - int(4*s), wy + int(10*s)),
            (wx + int(4*s), wy + int(10*s)),
        ])
        # Pixel antennae
        pygame.draw.line(surface, (20, 20, 20),
                         (hx - int(hd*0.3), hy - hd),
                         (hx - int(hd*0.6), hy - hd - int(10*s)), max(1, int(s)))
        pygame.draw.line(surface, (20, 20, 20),
                         (hx + int(hd*0.3), hy - hd),
                         (hx + int(hd*0.6), hy - hd - int(10*s)), max(1, int(s)))

    elif char_name == "Black Widow":
        # Glossy black spider bodysuit
        pygame.draw.rect(surface, (8, 8, 8),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Web pattern on torso (radiating lines from center)
        _wbx, _wby = sx, sy + int(bl*0.4)
        for _wni in range(8):
            _wna = _wni * math.pi / 4
            pygame.draw.line(surface, (35, 35, 35),
                             (_wbx, _wby),
                             (_wbx + int(math.cos(_wna)*12*s), _wby + int(math.sin(_wna)*12*s)),
                             max(1, int(s)))
        # Web concentric arcs
        for _wri in range(2):
            _wr = int((5 + _wri*5)*s)
            pygame.draw.circle(surface, (35, 35, 35), (_wbx, _wby), _wr, max(1, int(s)))
        # Red hourglass on torso
        _hg_cx, _hg_cy = sx, sy + bl//2
        pygame.draw.polygon(surface, (220, 20, 20), [
            (_hg_cx - int(6*s), _hg_cy - int(8*s)),
            (_hg_cx + int(6*s), _hg_cy - int(8*s)),
            (_hg_cx + int(3*s), _hg_cy),
            (_hg_cx + int(6*s), _hg_cy + int(8*s)),
            (_hg_cx - int(6*s), _hg_cy + int(8*s)),
            (_hg_cx - int(3*s), _hg_cy),
        ])
        pygame.draw.polygon(surface, (255, 60, 60), [
            (_hg_cx - int(6*s), _hg_cy - int(8*s)),
            (_hg_cx + int(6*s), _hg_cy - int(8*s)),
            (_hg_cx + int(3*s), _hg_cy),
            (_hg_cx + int(6*s), _hg_cy + int(8*s)),
            (_hg_cx - int(6*s), _hg_cy + int(8*s)),
            (_hg_cx - int(3*s), _hg_cy),
        ], max(1, int(s)))
        # 8 spider legs — 4 per side, jointed
        for _li in range(4):
            _ly = sy + int(bl * (0.15 + _li * 0.22))
            for _lf in (-1, 1):
                _ljx = sx + _lf * int(18*s)
                _ljy = _ly - int(4*s) + _li*int(3*s)
                _ltx = sx + _lf * int(28*s)
                _lty = _ljy + int(8*s)
                pygame.draw.line(surface, (25, 25, 25), (sx, _ly), (_ljx, _ljy), max(2, int(2*s)))
                pygame.draw.line(surface, (25, 25, 25), (_ljx, _ljy), (_ltx, _lty), max(1, int(2*s)))
        # Web silk from both hands
        for _shx, _shy in [(lhx, lhy), (rhx, rhy)]:
            for _swi in range(2):
                _swa = math.pi * (0.2 + _swi * 0.25) * (-facing)
                pygame.draw.line(surface, (200, 200, 220),
                                 (_shx, _shy),
                                 (_shx + int(math.cos(_swa)*14*s), _shy + int(math.sin(_swa)*14*s)),
                                 max(1, int(s)))
        # Compound eye cluster
        for _eox in (-1, 1):
            pygame.draw.circle(surface, (180, 10, 10),
                               (hx + _eox*int(hd*0.4), hy - int(hd*0.15)), max(3, int(5*s)))
            # Multiple lens circles
            for _eli in range(3):
                _ela = _eli * math.pi * 2 / 3
                pygame.draw.circle(surface, (30, 30, 30),
                                   (hx + _eox*int(hd*0.4) + int(math.cos(_ela)*2*s),
                                    hy - int(hd*0.15) + int(math.sin(_ela)*2*s)),
                                   max(1, int(2*s)))
        # Black glossy head sheen
        pygame.draw.circle(surface, (30, 30, 30), (hx - int(hd*0.2), hy - int(hd*0.3)),
                           max(2, int(4*s)))

    elif char_name == "AI":
        # Robotic helmet — square with rounded corners
        pygame.draw.rect(surface, (0, 180, 160),
                         (hx - int(hd*1.05), hy - hd - int(hd*0.4),
                          int(hd*2.1), int(hd*2.0)),
                         border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (0, 220, 200),
                         (hx - int(hd*1.05), hy - hd - int(hd*0.4),
                          int(hd*2.1), int(hd*2.0)),
                         max(1, int(2*s)), border_radius=max(3, int(5*s)))
        # LED eye bar
        pygame.draw.rect(surface, (0, 255, 220),
                         (hx - int(hd*0.7), hy - int(hd*0.15), int(hd*1.4), int(hd*0.35)))
        # Circuit lines on torso
        for _ci in range(3):
            _cy2 = sy + int(bl*0.2 + bl*0.25*_ci)
            pygame.draw.line(surface, (0, 160, 140),
                             (sx - int(8*s), _cy2), (sx + int(8*s), _cy2),
                             max(1, int(s)))
            pygame.draw.line(surface, (0, 160, 140),
                             (sx + int(4*s), _cy2),
                             (sx + int(4*s), _cy2 + int(5*s)), max(1, int(s)))

    elif char_name == "Forcefield":
        # Energy field rings around body
        for _fi, _fr in enumerate([int(hd*1.4), int(hd*1.7)]):
            _alpha = 180 - _fi * 60
            _fsurf = pygame.Surface((_fr*2+4, _fr*2+4), pygame.SRCALPHA)
            pygame.draw.circle(_fsurf, (100, 180, 255, _alpha),
                               (_fr+2, _fr+2), _fr, max(1, int(2*s)))
            surface.blit(_fsurf, (hx - _fr - 2, hy - _fr - 2))
        # Visor with energy glow
        pygame.draw.ellipse(surface, (80, 160, 255),
                            (hx - int(hd*0.9), hy - int(hd*0.2), int(hd*1.8), int(hd*0.65)))
        # Force gauntlet on right hand
        pygame.draw.circle(surface, (100, 180, 255), (rhx, rhy), max(4, int(6*s)), max(1, int(2*s)))

    elif char_name == "Poltergeist":
        # Ghost wisp trailing behind body
        for _pi in range(3):
            _px = sx - facing * int((8 + _pi*6)*s)
            _py = sy + int(bl*0.3*_pi)
            _pr = max(2, int((5 - _pi)*s))
            _psurf = pygame.Surface((_pr*2+2, _pr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(_psurf, (180, 80, 255, 120 - _pi*30),
                               (_pr+1, _pr+1), _pr)
            surface.blit(_psurf, (_px - _pr - 1, _py - _pr - 1))
        # Glowing possession eyes
        for _ei, _eox in enumerate((-1, 1)):
            pygame.draw.circle(surface, (200, 100, 255),
                               (hx + _eox*int(hd*0.4), hy), max(3, int(4*s)))
            pygame.draw.circle(surface, (255, 200, 255),
                               (hx + _eox*int(hd*0.4), hy), max(1, int(2*s)))
        # Floating haze on head
        _phsurf = pygame.Surface((int(hd*2.4), int(hd*1.2)), pygame.SRCALPHA)
        pygame.draw.ellipse(_phsurf, (120, 40, 200, 80),
                            (0, 0, int(hd*2.4), int(hd*1.2)))
        surface.blit(_phsurf, (hx - int(hd*1.2), hy - hd - int(hd*0.6)))

    elif char_name == "Armor":
        # Heavy shoulder plates
        for _af in (-1, 1):
            pygame.draw.rect(surface, (140, 145, 165),
                             (sx + _af*int(3*s), sy - int(6*s), int(14*s), int(10*s)),
                             border_radius=max(2, int(3*s)))
            pygame.draw.rect(surface, (190, 195, 210),
                             (sx + _af*int(3*s), sy - int(6*s), int(14*s), int(10*s)),
                             max(1, int(s)), border_radius=max(2, int(3*s)))
        # Breastplate
        pygame.draw.rect(surface, (130, 135, 155),
                         (sx - int(9*s), sy + int(2*s), int(18*s), int(bl*0.65)),
                         border_radius=max(2, int(4*s)))
        pygame.draw.line(surface, (200, 205, 220),
                         (sx, sy + int(4*s)), (sx, sy + int(bl*0.6)),
                         max(1, int(s)))
        # Full great helm
        _hw = int(hd*2.0); _hh = int(hd*2.2)
        pygame.draw.rect(surface, (130, 135, 155),
                         (hx - _hw//2, hy - hd - int(_hh*0.55), _hw, _hh),
                         border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (80, 80, 80),
                         (hx - int(hd*0.65), hy - int(4*s), int(hd*1.3), int(6*s)))

    elif char_name == "Deflector":
        # Mirror-chrome torso plates
        pygame.draw.rect(surface, (160, 230, 255),
                         (sx - int(9*s), sy, int(18*s), bl),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 245, 255),
                         (sx - int(9*s), sy, int(18*s), bl),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Reflective shine lines
        for _di in range(3):
            _dy = sy + int(bl*0.2 + bl*0.25*_di)
            pygame.draw.line(surface, (255, 255, 255),
                             (sx - int(7*s), _dy), (sx - int(2*s), _dy + int(4*s)),
                             max(1, int(s)))
        # Mirrored visor
        pygame.draw.ellipse(surface, (180, 240, 255),
                            (hx - int(hd*0.9), hy - int(hd*0.25), int(hd*1.8), int(hd*0.7)))
        pygame.draw.line(surface, (255, 255, 255),
                         (hx - int(hd*0.7), hy - int(hd*0.05)),
                         (hx + int(hd*0.7), hy - int(hd*0.05)), max(1, int(s)))

    elif char_name == "Friday the 13th":
        # Hockey mask — white oval with dark eye-slits and forehead stripes
        pygame.draw.ellipse(surface, (230, 230, 230),
                            (hx - hd, hy - hd, hd * 2, int(hd * 2.1)))
        pygame.draw.ellipse(surface, (40, 40, 40),
                            (hx - hd, hy - hd, hd * 2, int(hd * 2.1)), max(1, int(2 * s)))
        # Eye slits
        for _eo in (-1, 1):
            pygame.draw.ellipse(surface, (20, 20, 20),
                                (hx + _eo * int(hd * 0.38) - int(hd * 0.22),
                                 hy - int(hd * 0.15),
                                 int(hd * 0.44), int(hd * 0.22)))
        # Vertical red stripes on forehead
        for _si in range(3):
            _sx = hx + (_si - 1) * int(hd * 0.38)
            pygame.draw.line(surface, (180, 20, 20),
                             (_sx, hy - hd + int(3 * s)),
                             (_sx, hy - int(hd * 0.35)), max(1, int(2 * s)))
        # Machete in right hand
        _mx, _my = int(rh[0]), int(rh[1])
        _blade_tip = (_mx + facing * int(36 * s), _my - int(28 * s))
        pygame.draw.polygon(surface, (180, 180, 190),
                            [(_mx, _my),
                             (_mx + facing * int(10 * s), _my - int(4 * s)),
                             _blade_tip,
                             (_mx + facing * int(26 * s), _my + int(6 * s))])
        pygame.draw.line(surface, (100, 70, 40),
                         (_mx - facing * int(8 * s), _my + int(4 * s)),
                         (_mx, _my), max(2, int(3 * s)))

    elif char_name == "Unhittable":
        # Phase/blur effect — ghosted offset outlines
        for _ui, _uof in enumerate((-1, 1)):
            _ucol = (255, 255, 80, 60 + _ui*40)
            _usurf = pygame.Surface((int(hd*2.4), int(hd*2.4)), pygame.SRCALPHA)
            pygame.draw.circle(_usurf, _ucol,
                               (int(hd*1.2) + _uof*int(4*s), int(hd*1.2)),
                               hd, max(1, int(2*s)))
            surface.blit(_usurf, (hx - int(hd*1.2), hy - int(hd*1.2)))
        # Speed-blur streaks
        for _ui in range(3):
            pygame.draw.line(surface, (220, 220, 60),
                             (sx - facing*int((4+_ui*5)*s), sy + int(bl*0.3*_ui)),
                             (sx - facing*int((10+_ui*5)*s), sy + int(bl*0.3*_ui) - int(3*s)),
                             max(1, int(s)))
        # Glowing yellow eyes
        for _ei, _eox in enumerate((-1, 1)):
            pygame.draw.circle(surface, (255, 255, 0),
                               (hx + _eox*int(hd*0.35), hy), max(2, int(3*s)))

    elif char_name == "Map Man":
        # Khaki explorer shirt on torso
        pygame.draw.rect(surface, (185, 155, 90),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (215, 185, 115),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Cargo pockets on both sides
        for _cpdir in [-1, 1]:
            _cpx = sx + _cpdir * int(4*s)
            _cpy = sy + int(bl * 0.35)
            pygame.draw.rect(surface, (160, 130, 70),
                             (_cpx - int(3*s), _cpy, int(7*s), int(9*s)), border_radius=max(1, int(s)))
            pygame.draw.rect(surface, (200, 170, 100),
                             (_cpx - int(3*s), _cpy, int(7*s), int(9*s)), max(1, int(s)), border_radius=max(1, int(s)))
            # Pocket flap
            pygame.draw.line(surface, (160, 130, 70),
                             (_cpx - int(3*s), _cpy + int(3*s)), (_cpx + int(4*s), _cpy + int(3*s)),
                             max(1, int(s)))
        # Rolled-up map scroll in left hand
        pygame.draw.rect(surface, (220, 195, 140),
                         (lhx - int(3*s), lhy - int(10*s), int(6*s), int(18*s)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (180, 150, 90),
                         (lhx - int(3*s), lhy - int(10*s), int(6*s), int(18*s)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Map lines on the scroll
        for _mli in range(3):
            pygame.draw.line(surface, (150, 110, 60),
                             (lhx - int(2*s), lhy - int(7*s) + _mli*int(5*s)),
                             (lhx + int(2*s), lhy - int(7*s) + _mli*int(5*s)), max(1, int(s)))
        # Magnifying glass in right hand
        pygame.draw.circle(surface, (140, 180, 210), (rhx, rhy), max(5, int(8*s)), max(2, int(3*s)))
        pygame.draw.circle(surface, (180, 210, 235), (rhx, rhy), max(5, int(8*s)), max(1, int(s)))
        # Glass shine
        pygame.draw.circle(surface, (220, 235, 250), (rhx - int(2*s), rhy - int(2*s)), max(1, int(2*s)))
        # Handle
        pygame.draw.line(surface, (120, 80, 40),
                         (rhx + int(4*s), rhy + int(5*s)),
                         (rhx + int(10*s), rhy + int(12*s)), max(2, int(3*s)))
        # Adventure belt with tool pouches at waist
        pygame.draw.rect(surface, (110, 75, 30),
                         (sx - int(10*s), wy - int(3*s), int(20*s), max(4, int(6*s))),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (150, 110, 55),
                         (sx - int(10*s), wy - int(3*s), int(20*s), max(4, int(6*s))),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Belt pouches
        for _bpd in [-1, 1]:
            pygame.draw.rect(surface, (130, 90, 40),
                             (sx + _bpd*int(6*s) - int(3*s), wy - int(5*s), int(6*s), int(8*s)),
                             border_radius=max(1, int(s)))
        # Tan wide-brimmed explorer hat
        brim_w = int(hd * 2.4)
        pygame.draw.ellipse(surface, (155, 115, 55),
                            (hx - brim_w // 2, hy - int(hd * 0.3), brim_w, int(hd * 0.6)))
        pygame.draw.ellipse(surface, (175, 135, 75),
                            (hx - hd + int(2*s), hy - hd, (hd - int(2*s)) * 2, int(hd * 1.15)))
        pygame.draw.ellipse(surface, (200, 165, 95),
                            (hx - hd + int(2*s), hy - hd, (hd - int(2*s)) * 2, int(hd * 1.15)),
                            max(1, int(s)))
        # Hat band
        pygame.draw.line(surface, (90, 60, 20),
                         (hx - int(hd*0.85), hy - hd + int(3*s)),
                         (hx + int(hd*0.85), hy - hd + int(3*s)), max(2, int(2*s)))
        # Compass rose on chest
        _cx, _cy = sx, sy + int(bl * 0.42)
        _cr = max(6, int(8 * s))
        pygame.draw.circle(surface, (220, 200, 140), (_cx, _cy), _cr)
        pygame.draw.circle(surface, (160, 120, 60), (_cx, _cy), _cr, max(1, int(s)))
        for _di, (_dx, _dy, _col) in enumerate([
            (0,-1,(220,40,40)), (0,1,(160,120,60)), (-1,0,(160,120,60)), (1,0,(160,120,60))]):
            pygame.draw.line(surface, _col, (_cx, _cy),
                             (_cx + _dx * _cr, _cy + _dy * _cr), max(1, int(2*s)))
        # N label on compass
        _nf = _get_font(max(6, int(8*s)))
        _nt = _nf.render("N", True, (200, 40, 40))
        surface.blit(_nt, (_cx - _nt.get_width()//2, _cy - _cr - _nt.get_height()))

    elif char_name == "Mega-Unhittable":
        # Intense phase effect — 4 ghosted outlines with wider spread
        for _ui, _uof in enumerate((-3, -1, 1, 3)):
            _alpha = 30 + _ui * 20
            _ucol = (255, 255, 180, _alpha)
            _usurf = pygame.Surface((int(hd*2.6), int(hd*2.6)), pygame.SRCALPHA)
            pygame.draw.circle(_usurf, _ucol,
                               (int(hd*1.3) + _uof*int(5*s), int(hd*1.3)),
                               hd, max(1, int(2*s)))
            surface.blit(_usurf, (hx - int(hd*1.3), hy - int(hd*1.3)))
        # Heavy blur streaks
        for _ui in range(5):
            pygame.draw.line(surface, (255, 255, 180),
                             (sx - facing*int((3+_ui*6)*s), sy + int(bl*0.25*_ui)),
                             (sx - facing*int((12+_ui*6)*s), sy + int(bl*0.25*_ui) - int(3*s)),
                             max(1, int(s)))
        # Bright white-hot eyes
        for _ei, _eox in enumerate((-1, 1)):
            pygame.draw.circle(surface, (255, 255, 255),
                               (hx + _eox*int(hd*0.35), hy), max(3, int(4*s)))
            pygame.draw.circle(surface, (255, 255, 100),
                               (hx + _eox*int(hd*0.35), hy), max(1, int(2*s)))

    elif char_name == "Bard":
        # Medieval tunic with diamond pattern
        pygame.draw.rect(surface, (130, 60, 160),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Diamond harlequin patches
        for _hdi in range(3):
            _hdx = sx - int(8*s) + _hdi * int(7*s)
            _hdy = sy + int(bl * 0.25)
            pygame.draw.polygon(surface, (220, 180, 40), [
                (_hdx, _hdy - int(6*s)),
                (_hdx + int(4*s), _hdy),
                (_hdx, _hdy + int(6*s)),
                (_hdx - int(4*s), _hdy),
            ])
        for _hdi2 in range(2):
            _hdx2 = sx - int(4*s) + _hdi2 * int(8*s)
            _hdy2 = sy + int(bl * 0.62)
            pygame.draw.polygon(surface, (220, 180, 40), [
                (_hdx2, _hdy2 - int(6*s)),
                (_hdx2 + int(4*s), _hdy2),
                (_hdx2, _hdy2 + int(6*s)),
                (_hdx2 - int(4*s), _hdy2),
            ])
        # Tunic outline
        pygame.draw.rect(surface, (160, 90, 195),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Ruffled collar at neck
        for _rfi in range(5):
            _rfa = math.pi * (0.1 + _rfi * 0.2)
            pygame.draw.ellipse(surface, (240, 235, 200),
                                (sx + int(math.cos(_rfa)*hd*0.8) - int(4*s),
                                 sy - int(5*s),
                                 int(8*s), int(6*s)))
        # Jester bells on collar tips
        for _jbi in range(3):
            _jba = math.pi * (0.2 + _jbi * 0.3)
            _jbx = sx + int(math.cos(_jba) * hd * 0.9)
            pygame.draw.circle(surface, (220, 180, 40), (_jbx, sy - int(2*s)), max(2, int(3*s)))
        # Lute / lyre held in left hand
        _ltx, _lty = lhx, lhy
        # Body of lute
        pygame.draw.ellipse(surface, (140, 90, 40),
                            (_ltx - int(7*s), _lty - int(10*s), int(14*s), int(18*s)))
        pygame.draw.ellipse(surface, (180, 130, 70),
                            (_ltx - int(7*s), _lty - int(10*s), int(14*s), int(18*s)),
                            max(1, int(s)))
        # Sound hole
        pygame.draw.circle(surface, (100, 60, 20), (_ltx, _lty), max(2, int(4*s)))
        # Neck of lute
        pygame.draw.line(surface, (140, 90, 40),
                         (_ltx, _lty - int(10*s)),
                         (_ltx - facing*int(6*s), _lty - int(24*s)), max(2, int(3*s)))
        # Strings
        for _stri in range(3):
            pygame.draw.line(surface, (220, 210, 170),
                             (_ltx - int(3*s) + _stri*int(2*s), _lty + int(6*s)),
                             (_ltx - facing*int(5*s) + _stri*int(s), _lty - int(23*s)),
                             max(1, int(s)))
        # Musical notes floating from right hand
        for _noti in range(2):
            _nx = rhx + facing*int((12 + _noti*10)*s)
            _ny = rhy - int((8 + _noti*6)*s)
            pygame.draw.circle(surface, (200, 120, 230), (_nx, _ny), max(3, int(4*s)))
            pygame.draw.line(surface, (200, 120, 230),
                             (_nx + max(2, int(3*s)), _ny),
                             (_nx + max(2, int(3*s)), _ny - int(10*s)), max(1, int(2*s)))
            if _noti == 1:
                pygame.draw.line(surface, (200, 120, 230),
                                 (_nx + max(2, int(3*s)), _ny - int(6*s)),
                                 (_nx + max(6, int(8*s)), _ny - int(4*s)), max(1, int(s)))
        # Jester hat (2-pronged with bells)
        pygame.draw.polygon(surface, (130, 60, 160),
                            [(hx - int(hd*0.7), hy - hd),
                             (hx + int(hd*0.7), hy - hd),
                             (hx + int(hd*0.5), hy - hd - int(hd*0.9)),
                             (hx - int(hd*0.5), hy - hd - int(hd*0.9))])
        pygame.draw.ellipse(surface, (130, 60, 160),
                            (hx - int(hd*0.9), hy - hd - int(hd*0.15), int(hd*1.8), int(hd*0.45)))
        # Left prong
        pygame.draw.polygon(surface, (220, 180, 40), [
            (hx - int(hd*0.45), hy - hd - int(hd*0.85)),
            (hx - int(hd*0.25), hy - hd - int(hd*0.85)),
            (hx - int(hd*0.1), hy - hd - int(hd*1.7)),
        ])
        pygame.draw.circle(surface, (220, 180, 40),
                           (hx - int(hd*0.1), hy - hd - int(hd*1.7)), max(3, int(4*s)))
        # Right prong
        pygame.draw.polygon(surface, (200, 120, 230), [
            (hx + int(hd*0.25), hy - hd - int(hd*0.85)),
            (hx + int(hd*0.55), hy - hd - int(hd*0.85)),
            (hx + int(hd*0.7), hy - hd - int(hd*1.6)),
        ])
        pygame.draw.circle(surface, (200, 120, 230),
                           (hx + int(hd*0.7), hy - hd - int(hd*1.6)), max(3, int(4*s)))
        # Feather tucked into hat band
        pygame.draw.line(surface, (255, 230, 80),
                         (hx + facing*int(hd*0.5), hy - hd - int(hd*0.1)),
                         (hx + facing*int(hd*1.2), hy - hd - int(hd*1.4)), max(2, int(3*s)))
        # Feather barbs
        for _fbi in range(4):
            _fbt = (_fbi + 1) / 5.0
            _fbx = int(hx + facing*int(hd*0.5) + facing*(hd*0.7)*_fbt)
            _fby = int(hy - hd - int(hd*0.1) - int(hd*1.3)*_fbt)
            pygame.draw.line(surface, (240, 200, 60),
                             (_fbx, _fby), (_fbx + int(4*s), _fby - int(3*s)), max(1, int(s)))

    elif char_name == "Butcher":
        # Blood-stained apron
        pygame.draw.rect(surface, (200, 60, 30),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=int(2*s))
        for _bi in range(3):
            pygame.draw.line(surface, (140, 20, 10),
                             (sx - int(5*s), sy + int(bl*0.2*(_bi+1))),
                             (sx + int(5*s), sy + int(bl*0.2*(_bi+1))),
                             max(1, int(s)))
        # Cleaver in hand
        _mx, _my = int(rh[0]), int(rh[1])
        pygame.draw.polygon(surface, (180, 180, 190),
                            [(_mx, _my - int(6*s)),
                             (_mx + facing*int(22*s), _my - int(14*s)),
                             (_mx + facing*int(22*s), _my + int(4*s)),
                             (_mx, _my + int(4*s))])
        pygame.draw.line(surface, (100, 70, 40), (_mx - facing*int(6*s), _my),
                         (_mx, _my), max(2, int(3*s)))

    elif char_name == "Stone Cold":
        # Granite stone armor — solid grey with texture
        pygame.draw.rect(surface, (95, 90, 85),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(4*s)))
        # Stone texture: mottled dark patches
        for _spi in range(6):
            _spx = sx - int(9*s) + (_spi % 3) * int(7*s)
            _spy = sy + int(bl * (0.1 + (_spi // 3) * 0.45))
            pygame.draw.ellipse(surface, (75, 72, 68),
                                (_spx, _spy, int(8*s), int(6*s)))
        pygame.draw.rect(surface, (130, 125, 118),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(2, int(4*s)))
        # Boulder shoulder plates
        for _bsdir in [-1, 1]:
            pygame.draw.ellipse(surface, (90, 85, 80),
                                (sx + _bsdir*int(9*s), sy - int(7*s), int(16*s), int(12*s)))
            pygame.draw.ellipse(surface, (125, 120, 114),
                                (sx + _bsdir*int(9*s), sy - int(7*s), int(16*s), int(12*s)),
                                max(1, int(2*s)))
            # Rock surface crack on shoulder
            pygame.draw.line(surface, (65, 62, 58),
                             (sx + _bsdir*int(12*s), sy - int(3*s)),
                             (sx + _bsdir*int(16*s), sy + int(4*s)), max(1, int(s)))
        # Granite chest slab dividing lines
        for _gcl in range(3):
            _gcly = sy + int(bl * (0.2 + _gcl * 0.25))
            pygame.draw.line(surface, (65, 62, 58),
                             (sx - int(10*s), _gcly), (sx + int(10*s), _gcly), max(1, int(s)))
        pygame.draw.line(surface, (65, 62, 58),
                         (sx, sy + int(4*s)), (sx, sy + int(bl*0.85)), max(1, int(s)))
        # Rivets
        for _ri in range(3):
            _ry = sy + int(bl * (0.18 + 0.3*_ri))
            for _rdx in [-1, 1]:
                pygame.draw.circle(surface, (150, 145, 138), (sx + _rdx*int(8*s), _ry), max(2, int(3*s)))
                pygame.draw.circle(surface, (170, 165, 158), (sx + _rdx*int(8*s), _ry), max(1, int(2*s)), max(1, int(s)))
        # Stone fist knuckle plating
        for _sfx, _sfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (90, 85, 80), (_sfx, _sfy), max(6, int(9*s)))
            pygame.draw.circle(surface, (125, 120, 114), (_sfx, _sfy), max(6, int(9*s)), max(1, int(2*s)))
            # Rough surface bumps
            for _sfi in range(4):
                _sfa = _sfi * math.pi * 0.5
                pygame.draw.circle(surface, (75, 72, 68),
                                   (_sfx + int(math.cos(_sfa)*5*s), _sfy + int(math.sin(_sfa)*5*s)),
                                   max(1, int(2*s)))
        # Stone head — crack network
        pygame.draw.circle(surface, (100, 95, 90), (hx, hy), hd, max(2, int(2*s)))
        for _hcx1, _hcy1, _hcx2, _hcy2 in [
            (0, -10, 4, 0), (-3, -5, 2, 3), (2, -8, -5, 5),
            (0, 2, -4, 8), (3, 1, 6, -4)]:
            pygame.draw.line(surface, (65, 62, 58),
                             (hx + int(_hcx1*s), hy + int(_hcy1*s)),
                             (hx + int(_hcx2*s), hy + int(_hcy2*s)), max(1, int(s)))
        # Stone cold eyes (sunken dark slits)
        for _eox in (-1, 1):
            pygame.draw.ellipse(surface, (45, 42, 38),
                                (hx + _eox*int(hd*0.3) - int(5*s), hy - int(hd*0.2),
                                 int(10*s), int(5*s)))
            pygame.draw.circle(surface, (80, 75, 70),
                               (hx + _eox*int(hd*0.3), hy - int(hd*0.15)), max(1, int(2*s)))

    elif char_name == "Tycoon":
        # Dark pinstripe business suit
        pygame.draw.rect(surface, (20, 30, 50),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Pinstripes
        for _psi in range(4):
            _psx = sx - int(9*s) + _psi * int(6*s)
            pygame.draw.line(surface, (35, 48, 70),
                             (_psx, sy + int(2*s)), (_psx, sy + int(bl - 2*s)), max(1, int(s)))
        # Lapels
        pygame.draw.polygon(surface, (15, 22, 40), [
            (sx, sy + int(4*s)),
            (sx - int(8*s), sy + int(2*s)),
            (sx - int(6*s), sy + int(bl*0.45)),
        ])
        pygame.draw.polygon(surface, (15, 22, 40), [
            (sx, sy + int(4*s)),
            (sx + int(8*s), sy + int(2*s)),
            (sx + int(6*s), sy + int(bl*0.45)),
        ])
        # White shirt and gold tie
        pygame.draw.polygon(surface, (230, 228, 222), [
            (sx - int(4*s), sy + int(3*s)),
            (sx + int(4*s), sy + int(3*s)),
            (sx + int(2*s), sy + int(bl*0.42)),
            (sx - int(2*s), sy + int(bl*0.42)),
        ])
        pygame.draw.polygon(surface, (200, 165, 0), [
            (sx - int(2*s), sy + int(8*s)),
            (sx + int(2*s), sy + int(8*s)),
            (sx + int(3*s), sy + int(bl*0.38)),
            (sx, sy + int(bl*0.44)),
            (sx - int(3*s), sy + int(bl*0.38)),
        ])
        # Gold tie pin
        pygame.draw.line(surface, (240, 200, 20),
                         (sx - int(3*s), sy + int(bl*0.26)),
                         (sx + int(3*s), sy + int(bl*0.26)), max(2, int(2*s)))
        # Suit jacket buttons
        for _jbi in range(2):
            pygame.draw.circle(surface, (40, 55, 80),
                               (sx, sy + int(bl*(0.5 + _jbi*0.16))), max(2, int(3*s)))
            pygame.draw.circle(surface, (70, 90, 120),
                               (sx, sy + int(bl*(0.5 + _jbi*0.16))), max(2, int(3*s)), max(1, int(s)))
        # Gold monocle on one eye
        _mox = hx + facing * int(hd * 0.38)
        _moy = hy - int(hd * 0.1)
        pygame.draw.circle(surface, (200, 165, 0), (_mox, _moy), max(4, int(6*s)), max(2, int(2*s)))
        pygame.draw.line(surface, (180, 145, 0),
                         (_mox + max(3, int(5*s)), _moy + max(3, int(5*s))),
                         (_mox + max(6, int(9*s)), _moy + max(7, int(10*s))), max(1, int(2*s)))
        # Gold pocket watch
        pygame.draw.arc(surface, (200, 165, 0),
                        (sx - int(7*s), sy + int(bl*0.28), int(14*s), int(bl*0.38)),
                        math.pi * 0.9, math.pi * 2.1, max(1, int(2*s)))
        pygame.draw.circle(surface, (200, 165, 0),
                           (sx + facing*int(6*s), sy + int(bl*0.56)), max(4, int(5*s)))
        pygame.draw.circle(surface, (240, 210, 40),
                           (sx + facing*int(6*s), sy + int(bl*0.56)), max(3, int(4*s)))
        pygame.draw.circle(surface, (200, 165, 0),
                           (sx + facing*int(6*s), sy + int(bl*0.56)), max(3, int(4*s)), max(1, int(s)))
        # Pile of gold coins at feet
        for _gci in range(4):
            pygame.draw.ellipse(surface, (200, 165, 0),
                                (wx - int(8*s) + _gci*int(4*s), wy + int(4*s),
                                 int(8*s), int(5*s)))
            pygame.draw.ellipse(surface, (240, 210, 40),
                                (wx - int(8*s) + _gci*int(4*s), wy + int(4*s),
                                 int(8*s), int(5*s)), max(1, int(s)))
        # Gold top hat
        hat_w = int(hd * 1.55)
        pygame.draw.ellipse(surface, (160, 130, 0),
                            (hx - int(hd*1.05), hy - int(hd*0.3), int(hd*2.1), int(hd*0.45)))
        pygame.draw.rect(surface, (180, 150, 0),
                         (hx - hat_w//2, hy - hd - int(hd*1.05), hat_w, int(hd*1.1)))
        pygame.draw.rect(surface, (210, 180, 20),
                         (hx - hat_w//2, hy - hd - int(hd*1.05), hat_w, int(hd*1.1)),
                         max(1, int(s)))
        # Hat band stripe
        pygame.draw.rect(surface, (20, 30, 50),
                         (hx - hat_w//2, hy - hd - int(hd*0.22), hat_w, max(3, int(4*s))))
        # Money bag symbol on chest
        _cx, _cy = sx - facing*int(4*s), sy + int(bl * 0.68)
        pygame.draw.circle(surface, (210, 175, 0), (_cx, _cy), max(5, int(7*s)))
        pygame.draw.circle(surface, (240, 210, 40), (_cx, _cy), max(5, int(7*s)), max(1, int(s)))
        _sf = _get_font(max(6, int(9*s)))
        _st2 = _sf.render("$", True, (100, 80, 0))
        surface.blit(_st2, (_cx - _st2.get_width()//2, _cy - _st2.get_height()//2))

    elif char_name == "Glass Jaw":
        # Boxing robe / upper body wrap (open, hanging off shoulders)
        pygame.draw.polygon(surface, (20, 20, 20), [
            (sx - int(12*s), sy),
            (sx - int(8*s), sy),
            (sx - int(10*s), wy + int(10*s)),
            (sx - int(14*s), wy + int(10*s)),
        ])
        pygame.draw.polygon(surface, (20, 20, 20), [
            (sx + int(12*s), sy),
            (sx + int(8*s), sy),
            (sx + int(10*s), wy + int(10*s)),
            (sx + int(14*s), wy + int(10*s)),
        ])
        pygame.draw.polygon(surface, (180, 30, 30), [
            (sx - int(12*s), sy),
            (sx - int(14*s), wy + int(10*s)),
            (sx - int(12*s), wy + int(10*s)),
            (sx - int(10*s), sy),
        ])
        pygame.draw.polygon(surface, (180, 30, 30), [
            (sx + int(12*s), sy),
            (sx + int(14*s), wy + int(10*s)),
            (sx + int(12*s), wy + int(10*s)),
            (sx + int(10*s), sy),
        ])
        # Black boxing shorts on lower torso
        pygame.draw.rect(surface, (20, 20, 20),
                         (sx - int(9*s), sy + int(bl * 0.55), int(18*s), int(bl * 0.45)),
                         border_radius=max(2, int(2*s)))
        pygame.draw.rect(surface, (60, 60, 60),
                         (sx - int(9*s), sy + int(bl * 0.55), int(18*s), int(bl * 0.45)),
                         max(1, int(s)), border_radius=max(2, int(2*s)))
        # Shorts waistband stripe
        pygame.draw.rect(surface, (180, 30, 30),
                         (sx - int(9*s), sy + int(bl * 0.55), int(18*s), max(2, int(4*s))))
        # Shorts side stripe
        for _side in [-1, 1]:
            pygame.draw.line(surface, (180, 30, 30),
                             (sx + _side * int(8*s), sy + int(bl * 0.6)),
                             (sx + _side * int(8*s), wy + int(6*s)), max(1, int(2*s)))
        # Cracked glass pattern on upper torso
        pygame.draw.rect(surface, (200, 190, 220),
                         (sx - int(8*s), sy, int(16*s), int(bl * 0.55)), max(1, int(s)), border_radius=int(2*s))
        # Elaborate crack pattern
        for _qi, (_qx, _qy, _qex, _qey) in enumerate([
            (-6, 4, 4, 18), (3, 2, -5, 22), (-2, 14, 8, 30),
            (0, 8, -7, 20), (4, 16, 0, 28), (-4, 22, 6, 34)]):
            pygame.draw.line(surface, (120, 80, 140),
                             (sx + int(_qx*s), sy + int(_qy*s)),
                             (sx + int(_qex*s), sy + int(_qey*s)), max(1, int(s)))
        # Crack branching splinters
        pygame.draw.line(surface, (150, 100, 170),
                         (sx - int(2*s), sy + int(14*s)),
                         (sx - int(8*s), sy + int(20*s)), max(1, int(s)))
        pygame.draw.line(surface, (150, 100, 170),
                         (sx + int(3*s), sy + int(18*s)),
                         (sx + int(8*s), sy + int(12*s)), max(1, int(s)))
        # Shattered glass glint on torso
        pygame.draw.circle(surface, (240, 230, 255), (sx - int(3*s), sy + int(10*s)), max(1, int(2*s)))
        pygame.draw.circle(surface, (240, 230, 255), (sx + int(5*s), sy + int(24*s)), max(1, int(2*s)))
        # Tape wraps on wrists above boxing gloves — wider and more layers
        for _twx, _twy in [(lhx, lhy), (rhx, rhy)]:
            for _tbi in range(5):
                _tw = int(8*s)
                pygame.draw.line(surface, (240, 220, 190),
                                 (_twx - _tw//2, _twy - int((4 + _tbi * 3)*s)),
                                 (_twx + _tw//2, _twy - int((4 + _tbi * 3)*s)),
                                 max(1, int(2*s)))
            # Diagonal tape cross
            pygame.draw.line(surface, (220, 200, 170),
                             (_twx - int(4*s), _twy - int(15*s)),
                             (_twx + int(4*s), _twy - int(5*s)), max(1, int(s)))
        # Large padded boxing gloves on both hands
        for _bgx, _bgy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.ellipse(surface, (180, 20, 20),
                                (_bgx - int(9*s), _bgy - int(8*s), int(18*s), int(14*s)))
            pygame.draw.ellipse(surface, (220, 60, 60),
                                (_bgx - int(9*s), _bgy - int(8*s), int(18*s), int(14*s)),
                                max(1, int(2*s)))
            # Glove seam line
            pygame.draw.line(surface, (140, 10, 10),
                             (_bgx - int(3*s), _bgy - int(7*s)),
                             (_bgx - int(3*s), _bgy + int(5*s)), max(1, int(s)))
            # Glove laces
            for _lace in range(3):
                pygame.draw.line(surface, (200, 40, 40),
                                 (_bgx - int(3*s), _bgy - int(6*s) + _lace*int(4*s)),
                                 (_bgx + int(3*s), _bgy - int(6*s) + _lace*int(4*s)),
                                 max(1, int(s)))
        # Headgear — padded helmet with chin strap
        pygame.draw.ellipse(surface, (180, 20, 20),
                            (hx - int(hd*1.15), hy - hd - int(2*s), int(hd*2.3), int(hd*1.4)))
        pygame.draw.ellipse(surface, (220, 60, 60),
                            (hx - int(hd*1.15), hy - hd - int(2*s), int(hd*2.3), int(hd*1.4)),
                            max(1, int(2*s)))
        # Face opening gap
        pygame.draw.ellipse(surface, col,
                            (hx - int(hd*0.75), hy - int(hd*0.8), int(hd*1.5), int(hd*1.3)))
        # Chin strap
        pygame.draw.arc(surface, (140, 10, 10),
                        (hx - int(hd*0.7), hy - int(hd*0.4), int(hd*1.4), int(hd*0.8)),
                        math.pi * 1.1, math.pi * 1.9, max(2, int(3*s)))
        # Chin guard / mouthguard on lower face
        pygame.draw.rect(surface, (240, 200, 60),
                         (hx - int(hd * 0.55), hy + int(hd * 0.2), int(hd * 1.1), int(hd * 0.4)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 160, 20),
                         (hx - int(hd * 0.55), hy + int(hd * 0.2), int(hd * 1.1), int(hd * 0.4)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Black eye bruise marking
        pygame.draw.ellipse(surface, (30, 10, 40),
                            (hx - facing*int(hd*0.6) - int(5*s), hy - int(5*s), int(10*s), int(6*s)))

    elif char_name == "Sniper":
        # Ghillie suit — layered dark green tattered camouflage
        pygame.draw.rect(surface, (35, 55, 25),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(8*s)),
                         border_radius=max(2, int(4*s)))
        # Ghillie foliage strips (ragged leaf shapes)
        for _gli in range(9):
            _glx = sx - int(10*s) + (_gli % 3) * int(7*s) + int((_gli % 2)*3*s)
            _gly = sy + int(bl * (0.05 + (_gli // 3) * 0.33))
            pygame.draw.polygon(surface, [
                (30, 65, 20), (45, 80, 30), (25, 75, 15)][_gli % 3], [
                (_glx, _gly),
                (_glx - int(4*s), _gly + int(8*s)),
                (_glx, _gly + int(6*s)),
                (_glx + int(4*s), _gly + int(8*s)),
            ])
        # Camo patches (dark splotches)
        for _cpi in range(5):
            _cpx = sx - int(8*s) + (_cpi * 4) % 16 * int(s)
            _cpy = sy + int(bl * (0.1 + _cpi * 0.17))
            pygame.draw.ellipse(surface, (20, 40, 12),
                                (_cpx, _cpy, int((5 + _cpi%3*3)*s), int((4+_cpi%2*3)*s)))
        # Sniper rifle — long barrel with scope
        _rb = rhx
        _ry2 = rhy
        _rtip = _rb + facing * int(50*s)
        # Rifle stock/body
        pygame.draw.rect(surface, (60, 40, 20),
                         (min(_rb, _rtip) if facing>0 else _rtip,
                          _ry2 - int(3*s), int(50*s), max(5, int(7*s))),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (90, 65, 35),
                         (min(_rb, _rtip) if facing>0 else _rtip,
                          _ry2 - int(3*s), int(50*s), max(5, int(7*s))),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Barrel (thin, extends further)
        pygame.draw.line(surface, (140, 140, 150),
                         (_rb + facing*int(20*s), _ry2),
                         (_rtip + facing*int(10*s), _ry2), max(2, int(3*s)))
        # Muzzle
        pygame.draw.line(surface, (180, 180, 190),
                         (_rtip + facing*int(10*s), _ry2 - int(2*s)),
                         (_rtip + facing*int(10*s), _ry2 + int(2*s)), max(2, int(3*s)))
        # Scope on top of rifle
        _scpx = _rb + facing*int(18*s)
        _scpy = _ry2 - int(8*s)
        pygame.draw.rect(surface, (50, 50, 60),
                         (_scpx - int(s), _scpy - int(3*s), int(18*s), max(5, int(7*s))),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (80, 80, 95),
                         (_scpx - int(s), _scpy - int(3*s), int(18*s), max(5, int(7*s))),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Scope lens
        pygame.draw.circle(surface, (100, 180, 200),
                           (_scpx + int(8*s), _scpy), max(3, int(4*s)))
        pygame.draw.circle(surface, (160, 220, 240),
                           (_scpx + int(8*s), _scpy), max(3, int(4*s)), max(1, int(s)))
        # Bipod legs at barrel end
        pygame.draw.line(surface, (80, 80, 90),
                         (_rb + facing*int(40*s), _ry2 + int(3*s)),
                         (_rb + facing*int(38*s), _ry2 + int(12*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (80, 80, 90),
                         (_rb + facing*int(44*s), _ry2 + int(3*s)),
                         (_rb + facing*int(46*s), _ry2 + int(12*s)), max(1, int(2*s)))
        # Ghillie hood on head
        pygame.draw.ellipse(surface, (30, 55, 20),
                            (hx - int(hd*1.2), hy - hd - int(4*s), int(hd*2.4), int(hd*1.5)))
        pygame.draw.ellipse(surface, (45, 75, 30),
                            (hx - int(hd*1.2), hy - hd - int(4*s), int(hd*2.4), int(hd*1.5)),
                            max(1, int(2*s)))
        # Hanging hood strips
        for _hsi in range(5):
            _hsx = hx - int(hd*0.8) + _hsi * int(hd*0.4)
            pygame.draw.line(surface, (25, 50, 15),
                             (_hsx, hy + int(hd*0.5)),
                             (_hsx + int((_hsi-2)*2*s), hy + int(hd*0.5) + int((6+_hsi%3*3)*s)),
                             max(1, int(s)))
        # Face paint camo — dark stripes across eyes
        pygame.draw.line(surface, (20, 35, 10),
                         (hx - hd, hy - int(hd*0.2)),
                         (hx + hd, hy - int(hd*0.2)), max(2, int(3*s)))
        # Crosshair eye glint (scope eye)
        _ex = hx + facing * int(hd*0.35)
        pygame.draw.circle(surface, (180, 200, 220), (_ex, hy - int(hd*0.1)), max(2, int(3*s)))
        pygame.draw.line(surface, (140, 180, 200),
                         (_ex - int(4*s), hy - int(hd*0.1)),
                         (_ex + int(4*s), hy - int(hd*0.1)), max(1, int(s)))
        pygame.draw.line(surface, (140, 180, 200),
                         (_ex, hy - int(hd*0.1) - int(4*s)),
                         (_ex, hy - int(hd*0.1) + int(4*s)), max(1, int(s)))

    elif char_name == "Life Drain":
        # Dark crimson aura wisps
        for _wi in range(4):
            _wa = _wi * 1.57
            _wx = hx + int(math.cos(_wa) * hd * 1.6)
            _wy = hy + int(math.sin(_wa) * hd * 1.2)
            _wsurf = pygame.Surface((int(hd*0.9), int(hd*0.9)), pygame.SRCALPHA)
            pygame.draw.circle(_wsurf, (180, 10, 60, 80), (int(hd*0.45), int(hd*0.45)), int(hd*0.4))
            surface.blit(_wsurf, (_wx - int(hd*0.45), _wy - int(hd*0.45)))
        # Red eyes
        for _ei, _eox in enumerate((-1, 1)):
            pygame.draw.circle(surface, (220, 20, 60),
                               (hx + _eox*int(hd*0.35), hy), max(2, int(3*s)))

    elif char_name == "Lancer":
        # Lance held forward
        _lx, _ly = int(rh[0]), int(rh[1])
        pygame.draw.line(surface, (160, 120, 50),
                         (_lx - facing*int(8*s), _ly),
                         (_lx + facing*int(52*s), _ly - int(4*s)),
                         max(2, int(3*s)))
        # Lance tip
        pygame.draw.polygon(surface, (180, 180, 200),
                            [(_lx + facing*int(52*s), _ly - int(4*s)),
                             (_lx + facing*int(64*s), _ly - int(2*s)),
                             (_lx + facing*int(52*s), _ly + int(6*s))])
        # Armored visor
        pygame.draw.ellipse(surface, (150, 140, 160),
                            (hx - int(hd*0.85), hy - int(hd*0.2), int(hd*1.7), int(hd*0.5)))
        pygame.draw.line(surface, (200, 195, 210),
                         (hx - int(hd*0.6), hy + int(hd*0.05)),
                         (hx + int(hd*0.6), hy + int(hd*0.05)), max(1, int(s)))

    elif char_name == "Absorber":
        # Teal glowing absorption rings
        for _ai in range(2):
            _ar = int(hd * (1.3 + _ai * 0.5))
            _asurf = pygame.Surface((_ar*2+4, _ar*2+4), pygame.SRCALPHA)
            pygame.draw.circle(_asurf, (60, 200, 160, 40 - _ai*15), (_ar+2, _ar+2), _ar, max(1, int(2*s)))
            surface.blit(_asurf, (hx - _ar - 2, hy - _ar - 2))
        # Glowing teal eyes
        for _ei, _eox in enumerate((-1, 1)):
            pygame.draw.circle(surface, (80, 220, 180),
                               (hx + _eox*int(hd*0.35), hy), max(2, int(3*s)))

    elif char_name == "Hexer":
        # Purple hexed aura — star-like sparks
        for _hi in range(6):
            _ha = _hi * 1.047
            _hx2 = hx + int(math.cos(_ha) * hd * 1.5)
            _hy2 = hy + int(math.sin(_ha) * hd * 1.5)
            pygame.draw.circle(surface, (140, 60, 220), (_hx2, _hy2), max(2, int(3*s)))
        # Witch hat
        hat_pts = [
            (hx, hy - hd - int(hd*1.3)),
            (hx - int(hd*0.6), hy - hd),
            (hx + int(hd*0.6), hy - hd),
        ]
        pygame.draw.polygon(surface, (60, 20, 100), hat_pts)
        pygame.draw.ellipse(surface, (80, 30, 120),
                            (hx - int(hd*0.9), hy - hd - int(hd*0.15), int(hd*1.8), int(hd*0.3)))

    elif char_name == "Gambler":
        # Black pinstripe casino suit on torso
        pygame.draw.rect(surface, (20, 20, 20),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Pinstripes
        for _psi in range(4):
            _psx = sx - int(8*s) + _psi * int(6*s)
            pygame.draw.line(surface, (40, 40, 40),
                             (_psx, sy + int(2*s)), (_psx, sy + int(bl - 2*s)), max(1, int(s)))
        # White dress shirt triangle
        pygame.draw.polygon(surface, (230, 230, 230), [
            (sx, sy + int(3*s)),
            (sx - int(6*s), sy + int(3*s)),
            (sx, sy + int(bl * 0.5)),
        ])
        pygame.draw.polygon(surface, (230, 230, 230), [
            (sx, sy + int(3*s)),
            (sx + int(6*s), sy + int(3*s)),
            (sx, sy + int(bl * 0.5)),
        ])
        # Red bow tie
        pygame.draw.polygon(surface, (200, 20, 20), [
            (sx - int(6*s), sy + int(3*s)),
            (sx, sy + int(6*s)),
            (sx - int(6*s), sy + int(9*s)),
        ])
        pygame.draw.polygon(surface, (200, 20, 20), [
            (sx + int(6*s), sy + int(3*s)),
            (sx, sy + int(6*s)),
            (sx + int(6*s), sy + int(9*s)),
        ])
        pygame.draw.circle(surface, (160, 10, 10), (sx, sy + int(6*s)), max(2, int(3*s)))
        # Gold pocket watch chain
        pygame.draw.arc(surface, (200, 170, 40),
                        (sx - int(8*s), sy + int(bl*0.3), int(16*s), int(bl*0.4)),
                        math.pi * 0.8, math.pi * 2.2, max(1, int(2*s)))
        pygame.draw.circle(surface, (200, 170, 40),
                           (sx + facing*int(7*s), sy + int(bl*0.62)), max(3, int(4*s)))
        pygame.draw.circle(surface, (240, 210, 80),
                           (sx + facing*int(7*s), sy + int(bl*0.62)), max(2, int(3*s)),
                           max(1, int(s)))
        # Playing card fan held in right hand
        for _cfi in range(4):
            _cfa = math.pi * (0.3 + _cfi * 0.12) * facing
            _cfex = rhx + int(math.cos(_cfa) * 16 * s)
            _cfey = rhy - int(math.sin(abs(_cfa)) * 16 * s)
            _cfc = [(240, 240, 240), (220, 20, 20), (240, 240, 240), (20, 20, 20)][_cfi]
            pygame.draw.line(surface, _cfc, (rhx, rhy), (_cfex, _cfey), max(2, int(3*s)))
            pygame.draw.rect(surface, _cfc,
                             (_cfex - int(3*s), _cfey - int(4*s), int(6*s), int(8*s)),
                             border_radius=max(1, int(s)))
        # Diamond suit on chest
        _cx, _cy = sx, sy + int(bl * 0.42)
        pygame.draw.polygon(surface, (220, 20, 20),
                            [(_cx, _cy - int(6*s)), (_cx + int(5*s), _cy),
                             (_cx, _cy + int(6*s)), (_cx - int(5*s), _cy)])
        # Lucky star hat — top hat
        pygame.draw.rect(surface, (20, 20, 20),
                         (hx - int(hd*0.75), hy - hd - int(16*s), int(hd*1.5), int(16*s)))
        pygame.draw.rect(surface, (40, 40, 40),
                         (hx - int(hd*0.75), hy - hd - int(16*s), int(hd*1.5), int(16*s)),
                         max(1, int(s)))
        pygame.draw.ellipse(surface, (20, 20, 20),
                            (hx - int(hd*1.1), hy - hd - int(4*s), int(hd*2.2), int(8*s)))
        # Hat band with red stripe
        pygame.draw.rect(surface, (180, 20, 20),
                         (hx - int(hd*0.75), hy - hd - int(5*s), int(hd*1.5), max(2, int(3*s))))
        # Gold dice on hat brim
        pygame.draw.rect(surface, (200, 170, 40),
                         (hx + int(hd*0.4), hy - hd - int(4*s), max(4, int(7*s)), max(4, int(7*s))),
                         border_radius=max(1, int(s)))
        for _dpx, _dpy in [(-1, -1), (2, 2)]:
            pygame.draw.circle(surface, (20, 20, 20),
                               (hx + int(hd*0.4) + int((3+_dpx)*s),
                                hy - hd + int((2+_dpy)*s)), max(1, int(s)))

    elif char_name == "Counter":
        # Silver reflective armor on torso
        pygame.draw.rect(surface, (160, 165, 175),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Mirror-polish highlight panels
        pygame.draw.polygon(surface, (210, 220, 230), [
            (sx - int(9*s), sy + int(2*s)),
            (sx + int(4*s), sy + int(2*s)),
            (sx + int(2*s), sy + int(bl*0.45)),
            (sx - int(9*s), sy + int(bl*0.45)),
        ])
        pygame.draw.polygon(surface, (190, 200, 215), [
            (sx + int(5*s), sy + int(2*s)),
            (sx + int(9*s), sy + int(2*s)),
            (sx + int(9*s), sy + int(bl*0.45)),
            (sx + int(3*s), sy + int(bl*0.45)),
        ])
        # Armor outline
        pygame.draw.rect(surface, (200, 210, 220),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Center dividing ridge
        pygame.draw.line(surface, (230, 240, 250),
                         (sx, sy + int(2*s)), (sx, sy + int(bl*0.9)), max(1, int(2*s)))
        # Shoulder guards
        for _sgdir in [-1, 1]:
            pygame.draw.ellipse(surface, (180, 190, 200),
                                (sx + _sgdir*int(8*s), sy - int(5*s), int(12*s)*_sgdir if _sgdir>0 else int(12*s), int(10*s)))
            pygame.draw.ellipse(surface, (220, 230, 240),
                                (sx + _sgdir*int(8*s), sy - int(5*s), int(12*s)*_sgdir if _sgdir>0 else int(12*s), int(10*s)),
                                max(1, int(s)))
        # Reactive counter visor on helmet
        pygame.draw.ellipse(surface, (160, 165, 175),
                            (hx - int(hd*1.1), hy - hd, int(hd*2.2), int(hd*1.6)))
        pygame.draw.ellipse(surface, (200, 210, 220),
                            (hx - int(hd*1.1), hy - hd, int(hd*2.2), int(hd*1.6)),
                            max(1, int(2*s)))
        # Visor slit (orange tinted)
        pygame.draw.ellipse(surface, (200, 120, 30),
                            (hx - int(hd*0.8), hy - int(hd*0.5), int(hd*1.6), int(hd*0.5)))
        pygame.draw.ellipse(surface, (255, 180, 60),
                            (hx - int(hd*0.8), hy - int(hd*0.5), int(hd*1.6), int(hd*0.5)),
                            max(1, int(s)))
        # Forearm deflectors
        for _dfx, _dfy, _dex, _dey in [(sx, sy+int(bl*0.15), lhx, lhy),
                                         (sx, sy+int(bl*0.15), rhx, rhy)]:
            _dmx = (_dfx + _dex) // 2
            _dmy = (_dfy + _dey) // 2
            pygame.draw.rect(surface, (190, 200, 210),
                             (_dmx - int(6*s), _dmy - int(3*s), int(12*s), int(6*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (230, 240, 250),
                             (_dmx - int(6*s), _dmy - int(3*s), int(12*s), int(6*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Mirrored shield emblem on chest
        _cx, _cy = sx, sy + int(bl * 0.55)
        pygame.draw.polygon(surface, (200, 120, 60),
                            [(_cx, _cy - int(8*s)), (_cx + int(7*s), _cy - int(3*s)),
                             (_cx + int(7*s), _cy + int(5*s)), (_cx, _cy + int(9*s)),
                             (_cx - int(7*s), _cy + int(5*s)), (_cx - int(7*s), _cy - int(3*s))])
        # Return arrow
        pygame.draw.line(surface, (255, 200, 140),
                         (_cx + facing*int(4*s), _cy - int(3*s)),
                         (_cx - facing*int(4*s), _cy + int(3*s)), max(2, int(2*s)))
        pygame.draw.line(surface, (255, 200, 140),
                         (_cx - facing*int(4*s), _cy + int(3*s)),
                         (_cx - facing*int(2*s), _cy - int(s)),  max(2, int(2*s)))
        pygame.draw.line(surface, (255, 200, 140),
                         (_cx - facing*int(4*s), _cy + int(3*s)),
                         (_cx - facing*int(6*s), _cy + int(s)),  max(2, int(2*s)))

    elif char_name == "Blazer":
        # Flame particles around torso
        for _fi, (_fox, _foy) in enumerate([(-10, 10), (10, 5), (-6, 30), (8, 35), (0, 20)]):
            _fsurf = pygame.Surface((int(hd*0.7), int(hd*0.9)), pygame.SRCALPHA)
            pygame.draw.ellipse(_fsurf, (220, 90 + _fi*10, 20, 120),
                                (0, 0, int(hd*0.7), int(hd*0.9)))
            surface.blit(_fsurf, (sx + int(_fox*s) - int(hd*0.35), sy + int(_foy*s) - int(hd*0.45)))
        # Fire on fists
        for _fhx, _fhy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (255, 140, 0), (_fhx, _fhy), max(4, int(7*s)))
            pygame.draw.circle(surface, (255, 60, 0), (_fhx, _fhy), max(2, int(4*s)))
        # Ember glow on head
        _esurf = pygame.Surface((hd*4, hd*4), pygame.SRCALPHA)
        pygame.draw.circle(_esurf, (220, 90, 20, 50), (hd*2, hd*2), hd*2)
        surface.blit(_esurf, (hx - hd*2, hy - hd*2))

    elif char_name == "Colossus":
        # Thick shoulder guards
        for _sx2, _sdx in [(sx - int(10*s), -1), (sx + int(10*s), 1)]:
            pygame.draw.rect(surface, (80, 110, 55),
                             (_sx2 + _sdx*int(2*s), sy - int(4*s), int(14*s), int(10*s)),
                             border_radius=int(2*s))
            pygame.draw.rect(surface, (60, 85, 40),
                             (_sx2 + _sdx*int(2*s), sy - int(4*s), int(14*s), int(10*s)),
                             max(1, int(s)), border_radius=int(2*s))
        # Armor plate on chest
        pygame.draw.rect(surface, (90, 120, 65),
                         (sx - int(9*s), sy + int(4*s), int(18*s), int(bl*0.65)),
                         border_radius=int(3*s))
        pygame.draw.rect(surface, (60, 85, 40),
                         (sx - int(9*s), sy + int(4*s), int(18*s), int(bl*0.65)),
                         max(1, int(s)), border_radius=int(3*s))
        # Huge fists
        for _fhx, _fhy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (80, 110, 55), (_fhx, _fhy), max(6, int(10*s)))
            pygame.draw.circle(surface, (50, 80, 35), (_fhx, _fhy), max(6, int(10*s)), max(1, int(2*s)))

    elif char_name == "Stomper":
        # Construction overalls on torso + legs
        pygame.draw.rect(surface, (240, 160, 20),
                         (sx - int(9*s), sy, int(18*s), bl + int(4*s)), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 130, 10),
                         (sx - int(9*s), sy, int(18*s), bl + int(4*s)), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Overall bib straps
        for _strap in [-1, 1]:
            pygame.draw.rect(surface, (220, 140, 15),
                             (sx + _strap*int(5*s) - int(2*s), sy - int(8*s), int(5*s), int(12*s)))
        # Bib chest pocket
        pygame.draw.rect(surface, (200, 130, 10),
                         (sx - int(5*s), sy + int(4*s), int(10*s), int(9*s)),
                         border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (230, 150, 20),
                         (sx - int(5*s), sy + int(4*s), int(10*s), int(9*s)),
                         max(1, int(s)), border_radius=max(1, int(s)))
        # Safety reflective strips on overalls
        for _rfsi in range(2):
            _rfsy = sy + int(bl * (0.45 + _rfsi * 0.32))
            pygame.draw.rect(surface, (240, 240, 60),
                             (sx - int(9*s), _rfsy, int(18*s), max(2, int(3*s))))
        # Hard hat on head
        pygame.draw.ellipse(surface, (240, 160, 20),
                            (hx - int(hd*1.3), hy - hd - int(8*s), int(hd*2.6), int(hd*1.4)))
        pygame.draw.ellipse(surface, (200, 130, 10),
                            (hx - int(hd*1.3), hy - hd - int(8*s), int(hd*2.6), int(hd*1.4)),
                            max(1, int(2*s)))
        # Hat brim
        pygame.draw.ellipse(surface, (220, 140, 15),
                            (hx - int(hd*1.5), hy - hd - int(2*s), int(hd*3), int(8*s)))
        # Safety sticker on hat
        pygame.draw.circle(surface, (200, 20, 20),
                           (hx + facing*int(hd*0.5), hy - hd - int(3*s)), max(3, int(5*s)))
        pygame.draw.line(surface, (240, 240, 240),
                         (hx + facing*int(hd*0.5) - int(3*s), hy - hd - int(3*s)),
                         (hx + facing*int(hd*0.5) + int(3*s), hy - hd - int(3*s)), max(1, int(s)))
        pygame.draw.line(surface, (240, 240, 240),
                         (hx + facing*int(hd*0.5), hy - hd - int(6*s)),
                         (hx + facing*int(hd*0.5), hy - hd), max(1, int(s)))
        # Knee pads
        for _kpx, _kpy in [(lhx, lhy - int(8*s)), (rhx, rhy - int(8*s))]:
            pygame.draw.ellipse(surface, (60, 40, 20),
                                (_kpx - int(8*s), _kpy - int(5*s), int(16*s), int(12*s)))
            pygame.draw.ellipse(surface, (100, 70, 30),
                                (_kpx - int(8*s), _kpy - int(5*s), int(16*s), int(12*s)),
                                max(1, int(2*s)))
        # Big chunky boots on feet
        for _bx, _by in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.rect(surface, (30, 20, 10),
                             (_bx - int(11*s), _by - int(5*s), int(22*s), int(15*s)),
                             border_radius=int(3*s))
            pygame.draw.rect(surface, (80, 55, 25),
                             (_bx - int(11*s), _by - int(5*s), int(22*s), int(15*s)),
                             max(1, int(2*s)), border_radius=int(3*s))
            # Boot toe cap
            pygame.draw.ellipse(surface, (120, 120, 140),
                                (_bx + facing*int(4*s), _by - int(4*s), int(10*s), int(9*s)))
            # Boot laces
            for _bli in range(3):
                pygame.draw.line(surface, (180, 160, 120),
                                 (_bx - int(3*s), _by - int(4*s) + _bli*int(3*s)),
                                 (_bx + int(3*s), _by - int(4*s) + _bli*int(3*s)), max(1, int(s)))
        # Shockwave impact cracks at feet
        for _ix, _iy in [(lhx, lhy + int(10*s)), (rhx, rhy + int(10*s))]:
            for _ia in range(6):
                _iang = _ia * math.pi / 3
                _ir2 = int((5 + _ia % 3 * 3) * s)
                pygame.draw.line(surface, (80, 100, 220),
                                 (_ix, _iy),
                                 (_ix + int(math.cos(_iang) * _ir2),
                                  _iy + int(math.sin(_iang) * _ir2)), max(1, int(s)))

    elif char_name == "Porcupine":
        # Green fur body vest
        pygame.draw.rect(surface, (30, 90, 25),
                         (sx - int(9*s), sy + int(4*s), int(18*s), int(bl * 0.85)),
                         border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (60, 140, 45),
                         (sx - int(9*s), sy + int(4*s), int(18*s), int(bl * 0.85)),
                         max(1, int(s)), border_radius=max(2, int(4*s)))
        # Quill row on back (behind torso)
        for _qi in range(8):
            _qa = math.pi * 0.15 + _qi * math.pi * 0.1
            _qbx = sx - facing * int(8*s)
            _qby = sy + int(bl * (_qi / 9.0))
            _qtx = _qbx - facing * int((10 + (_qi % 3) * 5) * s)
            _qty = _qby - int(4*s)
            pygame.draw.line(surface, (60, 140, 45), (_qbx, _qby), (_qtx, _qty), max(1, int(2*s)))
            pygame.draw.circle(surface, (120, 200, 80), (_qtx, _qty), max(1, int(2*s)))
        # Spike triangles on torso
        for _pi in range(6):
            _px = sx + int((_pi % 3 - 1) * 8 * s)
            _py = sy + int((_pi // 3 * 0.5 + 0.15) * bl)
            pygame.draw.polygon(surface, (80, 180, 55),
                                [(_px, _py - int(11*s)),
                                 (_px - int(4*s), _py + int(3*s)),
                                 (_px + int(4*s), _py + int(3*s))])
        # Wrist quill bands
        for _wx2, _wy2 in [(lhx, lhy), (rhx, rhy)]:
            for _wqi in range(4):
                _wqa = _wqi * math.pi * 0.5
                pygame.draw.line(surface, (60, 140, 45),
                                 (_wx2, _wy2),
                                 (_wx2 + int(math.cos(_wqa)*8*s), _wy2 + int(math.sin(_wqa)*8*s)),
                                 max(1, int(s)))
        # Crown of long head spikes
        for _hi2 in range(7):
            _ha = math.pi * (_hi2 / 6.0)
            _hspx = hx + int(math.cos(_ha) * hd)
            _hspy = hy - int(math.sin(_ha) * hd)
            _spike_len = int((8 + (_hi2 % 3) * 4) * s)
            pygame.draw.line(surface, (60, 140, 45),
                             (_hspx, _hspy),
                             (_hspx + int(math.cos(_ha)*_spike_len), _hspy - int(math.sin(_ha)*_spike_len)),
                             max(1, int(2*s)))
            pygame.draw.circle(surface, (120, 200, 80),
                               (_hspx + int(math.cos(_ha)*_spike_len),
                                _hspy - int(math.sin(_ha)*_spike_len)), max(1, int(2*s)))
        # Beady black eyes
        for _eox in (-1, 1):
            pygame.draw.circle(surface, (10, 40, 10),
                               (hx + _eox*int(hd*0.38), hy - int(hd*0.1)), max(2, int(3*s)))
            pygame.draw.circle(surface, (200, 240, 180),
                               (hx + _eox*int(hd*0.38) - int(s), hy - int(hd*0.15)), max(1, int(s)))

    elif char_name == "Anchor":
        # Navy blue sailor jacket on torso
        pygame.draw.rect(surface, (20, 30, 80),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 80, 160),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # White sailor collar (V shape)
        pygame.draw.polygon(surface, (220, 225, 240), [
            (sx - int(10*s), sy + int(3*s)),
            (sx + int(10*s), sy + int(3*s)),
            (sx, sy + int(bl * 0.45)),
        ])
        pygame.draw.polygon(surface, (20, 30, 80), [
            (sx - int(5*s), sy + int(3*s)),
            (sx + int(5*s), sy + int(3*s)),
            (sx, sy + int(bl * 0.38)),
        ])
        # Three gold jacket buttons
        for _bi in range(3):
            pygame.draw.circle(surface, (200, 170, 40),
                               (sx, sy + int(bl * (0.5 + _bi * 0.18))), max(2, int(3*s)))
        # Captain hat on head
        pygame.draw.rect(surface, (20, 30, 80),
                         (hx - int(hd*1.1), hy - hd - int(10*s), int(hd*2.2), int(10*s)))
        pygame.draw.rect(surface, (60, 80, 160),
                         (hx - int(hd*1.1), hy - hd - int(10*s), int(hd*2.2), int(10*s)),
                         max(1, int(s)))
        pygame.draw.ellipse(surface, (20, 30, 80),
                            (hx - int(hd*1.3), hy - hd - int(4*s), int(hd*2.6), int(8*s)))
        pygame.draw.line(surface, (200, 170, 40),
                         (hx - int(hd*0.8), hy - hd - int(5*s)),
                         (hx + int(hd*0.8), hy - hd - int(5*s)), max(2, int(2*s)))
        # Anchor symbol on chest
        _cx, _cy = sx, sy + int(bl * 0.48)
        pygame.draw.circle(surface, (180, 190, 220), (_cx, _cy - int(7*s)), max(3, int(5*s)), max(2, int(2*s)))
        pygame.draw.line(surface, (180, 190, 220),
                         (_cx, _cy - int(2*s)), (_cx, _cy + int(12*s)), max(2, int(2*s)))
        pygame.draw.line(surface, (180, 190, 220),
                         (_cx - int(6*s), _cy + int(5*s)), (_cx + int(6*s), _cy + int(5*s)), max(2, int(2*s)))
        pygame.draw.line(surface, (180, 190, 220),
                         (_cx - int(6*s), _cy + int(12*s)), (_cx + int(6*s), _cy + int(12*s)), max(2, int(2*s)))
        # Heavy chain belt at waist
        for _chi in range(7):
            _chx = wx - int(14*s) + _chi * int(5*s)
            pygame.draw.ellipse(surface, (100, 110, 160),
                                (_chx, wy - int(4*s), int(6*s), int(5*s)), max(1, int(2*s)))
            pygame.draw.ellipse(surface, (160, 170, 220),
                                (_chx + int(s), wy - int(3*s), int(4*s), int(3*s)), max(1, int(s)))
        # Rope coils on forearms
        for _rfx, _rfy, _rsx, _rsy in [(lhx, lhy, sx, sy), (rhx, rhy, sx, sy)]:
            _rmx = (_rfx + _rsx) // 2
            _rmy = (_rfy + _rsy) // 2
            for _ri in range(3):
                _rt = _ri / 2.0
                _rrx = int(_rfx + (_rmx - _rfx) * _rt)
                _rry = int(_rfy + (_rmy - _rfy) * _rt)
                pygame.draw.circle(surface, (160, 130, 80), (_rrx, _rry), max(2, int(4*s)), max(1, int(s)))

    elif char_name == "Sleeper":
        # Nightcap (drooping pointed hat)
        cap_pts = [
            (hx - int(hd*0.8), hy - hd),
            (hx + int(hd*0.5), hy - hd),
            (hx + int(hd*1.4), hy - int(hd*1.8)),
        ]
        pygame.draw.polygon(surface, (80, 50, 140), cap_pts)
        pygame.draw.circle(surface, (200, 160, 255),
                           (hx + int(hd*1.4), hy - int(hd*1.8)), max(3, int(4*s)))
        # Sleepy half-closed eyes
        for _eox in (-1, 1):
            _ex = hx + _eox * int(hd*0.35)
            pygame.draw.line(surface, (200, 160, 255),
                             (_ex - int(3*s), hy - int(2*s)),
                             (_ex + int(3*s), hy - int(2*s)), max(1, int(2*s)))
        # Zzz floating above head
        for _zi, (_zox, _zoy) in enumerate([(8, -6), (14, -12), (20, -18)]):
            pygame.draw.circle(surface, (170, 130, 220),
                               (hx + facing*int(_zox*s), hy - hd - int(_zoy*s)),
                               max(2, int((2 + _zi)*s)))

    elif char_name == "Rager":
        # Red glow around whole body
        _rsurf = pygame.Surface((hd*6, hd*6), pygame.SRCALPHA)
        pygame.draw.circle(_rsurf, (200, 40, 20, 45), (hd*3, hd*3), hd*3)
        surface.blit(_rsurf, (sx - hd*3, sy - hd*2))
        # Clenched teeth line
        pygame.draw.line(surface, (240, 240, 240),
                         (hx - int(hd*0.4), hy + int(hd*0.35)),
                         (hx + int(hd*0.4), hy + int(hd*0.35)), max(2, int(3*s)))
        for _ti in range(4):
            _tx = hx - int(hd*0.35) + _ti * int(hd*0.22)
            pygame.draw.line(surface, (200, 40, 20),
                             (_tx, hy + int(hd*0.35)), (_tx, hy + int(hd*0.55)), max(1, int(s)))
        # Steam lines off head
        for _sti, _stox in enumerate([-int(hd*0.6), 0, int(hd*0.6)]):
            pygame.draw.line(surface, (230, 80, 60),
                             (hx + _stox, hy - hd - int(2*s)),
                             (hx + _stox + int((_sti-1)*3*s), hy - hd - int(14*s)),
                             max(1, int(2*s)))

    elif char_name == "Twin":
        # Ghost twin silhouette behind character
        _toff = facing * int(22*s)
        _tsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Ghost head
        pygame.draw.circle(_tsurf, (80, 180, 200, 55), (hx + _toff, hy), hd)
        # Ghost body
        pygame.draw.line(_tsurf, (80, 180, 200, 55),
                         (sx + _toff, sy), (wx + _toff, wy), max(3, int(4*s)))
        # Ghost arms
        pygame.draw.line(_tsurf, (80, 180, 200, 55),
                         (sx + _toff, sy + int(bl*0.15)), (lhx + _toff, lhy), max(2, int(3*s)))
        pygame.draw.line(_tsurf, (80, 180, 200, 55),
                         (sx + _toff, sy + int(bl*0.15)), (rhx + _toff, rhy), max(2, int(3*s)))
        # Ghost legs
        pygame.draw.line(_tsurf, (80, 180, 200, 55),
                         (wx + _toff, wy), (lhx + _toff, lhy + int(al*0.8)), max(2, int(3*s)))
        pygame.draw.line(_tsurf, (80, 180, 200, 55),
                         (wx + _toff, wy), (rhx + _toff, rhy + int(al*0.8)), max(2, int(3*s)))
        surface.blit(_tsurf, (0, 0))
        # Split-color costume: left half blue, right half teal
        _half_pts_l = [
            (sx, sy), (sx - int(10*s), sy), (sx - int(10*s), wy), (sx, wy)
        ]
        _half_pts_r = [
            (sx, sy), (sx + int(10*s), sy), (sx + int(10*s), wy), (sx, wy)
        ]
        pygame.draw.polygon(surface, (40, 90, 160), _half_pts_l)
        pygame.draw.polygon(surface, (20, 160, 170), _half_pts_r)
        pygame.draw.rect(surface, (180, 220, 240),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Yin-yang split line down center of body
        pygame.draw.line(surface, (200, 230, 240),
                         (sx, sy + int(3*s)), (sx, wy - int(3*s)), max(1, int(2*s)))
        # Dual-circle emblem at chest center
        pygame.draw.circle(surface, (40, 90, 160),
                           (sx - int(4*s), sy + int(bl*0.35)), max(3, int(5*s)))
        pygame.draw.circle(surface, (20, 160, 170),
                           (sx + int(4*s), sy + int(bl*0.35)), max(3, int(5*s)))
        pygame.draw.circle(surface, (200, 230, 240),
                           (sx - int(4*s), sy + int(bl*0.35)), max(3, int(5*s)), max(1, int(s)))
        pygame.draw.circle(surface, (200, 230, 240),
                           (sx + int(4*s), sy + int(bl*0.35)), max(3, int(5*s)), max(1, int(s)))
        # Cyan ring outline on head
        pygame.draw.circle(surface, (80, 200, 220), (hx, hy), hd, max(2, int(3*s)))
        pygame.draw.circle(surface, (40, 90, 160), (hx - int(hd*0.3), hy), hd // 2, max(1, int(s)))
        pygame.draw.circle(surface, (20, 160, 170), (hx + int(hd*0.3), hy), hd // 2, max(1, int(s)))

    elif char_name == "Sapper":
        # Dark tattered cloak on torso
        pygame.draw.rect(surface, (35, 20, 8),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(8*s)),
                         border_radius=max(2, int(4*s)))
        # Ragged cloak hem (tattered bottom edge)
        for _ti in range(5):
            _tx = sx - int(10*s) + _ti * int(5*s)
            _th = int((4 + (_ti % 3) * 3) * s)
            pygame.draw.polygon(surface, (35, 20, 8), [
                (_tx - int(2*s), wy + int(6*s)),
                (_tx + int(2*s), wy + int(6*s)),
                (_tx, wy + int(6*s) + _th),
            ])
        # Dark energy drain aura (faint)
        _dasurf = pygame.Surface((hd*8, hd*8), pygame.SRCALPHA)
        pygame.draw.circle(_dasurf, (80, 30, 5, 35), (hd*4, hd*4), hd*4)
        surface.blit(_dasurf, (sx - hd*4, sy - hd*2))
        # Siphon tendrils from hands
        for _hpx, _hpy in [(lhx, lhy), (rhx, rhy)]:
            for _ti2 in range(3):
                _tang = math.pi * (0.3 + _ti2 * 0.2)
                _tex = _hpx + int(math.cos(_tang) * 12 * s)
                _tey = _hpy - int(math.sin(_tang) * 12 * s)
                pygame.draw.line(surface, (100, 50, 10),
                                 (_hpx, _hpy), (_tex, _tey), max(1, int(s)))
                pygame.draw.circle(surface, (140, 70, 15), (_tex, _tey), max(1, int(2*s)))
        # Collar and hood rim
        pygame.draw.ellipse(surface, (50, 30, 10),
                            (sx - int(10*s), sy - int(4*s), int(20*s), int(10*s)))
        pygame.draw.ellipse(surface, (70, 45, 20),
                            (sx - int(10*s), sy - int(4*s), int(20*s), int(10*s)),
                            max(1, int(s)))
        # Drain arrows on arms (pointing inward toward body)
        for _ax, _ay, _adir in [(lhx, lhy, 1), (rhx, rhy, -1)]:
            _amx = (_ax + sx) // 2
            _amy = (_ay + sy) // 2
            pygame.draw.line(surface, (140, 70, 20),
                             (_ax, _ay), (_amx, _amy), max(2, int(3*s)))
            pygame.draw.polygon(surface, (160, 90, 25),
                                [(_amx + _adir*int(6*s), _amy),
                                 (_amx - _adir*int(4*s), _amy - int(5*s)),
                                 (_amx - _adir*int(4*s), _amy + int(5*s))])
        # Sunken dark eye sockets
        for _eox in (-1, 1):
            pygame.draw.ellipse(surface, (30, 15, 5),
                                (hx + _eox*int(hd*0.25) - int(5*s), hy,
                                 int(10*s), int(7*s)))
            pygame.draw.circle(surface, (160, 80, 10),
                               (hx + _eox*int(hd*0.3), hy + int(2*s)), max(1, int(2*s)))
        # Gaunt hollow face outline
        pygame.draw.circle(surface, (80, 50, 15), (hx, hy), hd, max(2, int(2*s)))
        # Sunken cheekbone lines
        for _eox in (-1, 1):
            pygame.draw.line(surface, (60, 35, 10),
                             (hx + _eox*int(hd*0.2), hy + int(hd*0.3)),
                             (hx + _eox*int(hd*0.6), hy + int(hd*0.5)), max(1, int(s)))

    elif char_name == "Mimic":
        # Shifting patchwork body (color-morphing panels)
        _patch_cols = [(180, 80, 80), (80, 80, 180), (80, 160, 80), (160, 140, 40), (130, 60, 160)]
        for _mi in range(5):
            _mpx = sx - int(10*s) + (_mi % 3) * int(7*s)
            _mpy = sy + int(bl * (0.1 + (_mi // 3) * 0.5))
            pygame.draw.rect(surface, _patch_cols[_mi],
                             (_mpx, _mpy, int(8*s), int(bl * 0.38)),
                             border_radius=max(1, int(2*s)))
        # Body outline pulsing dashes
        for _di in range(12):
            _da = _di * (math.pi * 2 / 12)
            _drx = sx + int(math.cos(_da) * 12 * s)
            _dry = sy + int(bl * 0.5) + int(math.sin(_da) * int(bl * 0.55))
            pygame.draw.circle(surface, (200, 200, 210), (_drx, _dry), max(2, int(3*s)))
        # Dashed ring around head
        for _di in range(10):
            _da = _di * (math.pi * 2 / 10)
            _drx = hx + int(math.cos(_da) * hd * 1.4)
            _dry = hy + int(math.sin(_da) * hd * 1.4)
            pygame.draw.circle(surface, (190, 190, 200), (_drx, _dry), max(1, int(2*s)))
        # Morphing arm traces (ghost outlines of different positions)
        for _mac, _max2, _may in [((140, 80, 80), lhx - int(8*s), lhy - int(6*s)),
                                   ((80, 80, 180), rhx + int(8*s), rhy - int(6*s))]:
            pygame.draw.line(surface, _mac,
                             (sx, sy + int(bl * 0.15)), (_max2, _may), max(1, int(2*s)))
            pygame.draw.circle(surface, _mac, (_max2, _may), max(2, int(4*s)), max(1, int(s)))
        # Question mark on chest
        _cx, _cy = sx, sy + int(bl * 0.35)
        pygame.draw.arc(surface, (220, 220, 230),
                        (_cx - int(7*s), _cy - int(9*s), int(14*s), int(12*s)),
                        math.pi * 0.1, math.pi * 1.1, max(2, int(3*s)))
        pygame.draw.line(surface, (220, 220, 230),
                         (_cx, _cy + int(2*s)), (_cx, _cy + int(6*s)), max(2, int(2*s)))
        pygame.draw.circle(surface, (220, 220, 230), (_cx, _cy + int(9*s)), max(2, int(3*s)))
        # Kaleidoscope eyes
        for _eox in (-1, 1):
            for _eri in range(3):
                _erc = [(200, 80, 80), (80, 200, 80), (80, 80, 200)][_eri]
                pygame.draw.circle(surface, _erc,
                                   (hx + _eox*int(hd*0.38), hy - int(hd*0.1)),
                                   max(1, int((3 - _eri) * s)))

    elif char_name == "Boomerang":
        # Tan outback shirt on torso
        pygame.draw.rect(surface, (190, 150, 90),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (220, 185, 120),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Chest pocket
        pygame.draw.rect(surface, (170, 130, 70),
                         (sx + facing*int(2*s), sy + int(bl*0.18), int(8*s), int(8*s)),
                         border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (220, 185, 120),
                         (sx + facing*int(2*s), sy + int(bl*0.18), int(8*s), int(8*s)),
                         max(1, int(s)), border_radius=max(1, int(s)))
        # Aboriginal-style body paint stripes (ochre + white)
        for _bpi in range(3):
            _bpy = sy + int(bl * (0.3 + _bpi * 0.22))
            pygame.draw.line(surface, (230, 100, 20),
                             (sx - int(8*s), _bpy), (sx + int(8*s), _bpy), max(2, int(2*s)))
        # Ochre headband with dot pattern
        pygame.draw.rect(surface, (200, 100, 20),
                         (hx - hd, hy - int(hd*0.1), hd*2, max(4, int(5*s))))
        for _dpi in range(5):
            pygame.draw.circle(surface, (240, 200, 80),
                               (hx - hd + int(hd*0.4*_dpi), hy + int(hd*0.15)),
                               max(1, int(2*s)))
        # Boomerang weapon held in right hand (larger, wood grain)
        pygame.draw.arc(surface, (160, 90, 25),
                        (rhx - int(17*s), rhy - int(13*s), int(34*s), int(24*s)),
                        0, math.pi, max(3, int(4*s)))
        pygame.draw.arc(surface, (210, 145, 60),
                        (rhx - int(13*s), rhy - int(10*s), int(26*s), int(18*s)),
                        0, math.pi, max(2, int(3*s)))
        pygame.draw.arc(surface, (240, 200, 110),
                        (rhx - int(10*s), rhy - int(7*s), int(20*s), int(14*s)),
                        0, math.pi, max(1, int(s)))
        # Second smaller boomerang tucked on back/left side
        pygame.draw.arc(surface, (160, 90, 25),
                        (lhx - int(12*s), lhy - int(9*s), int(24*s), int(17*s)),
                        math.pi, math.pi * 2, max(2, int(3*s)))
        pygame.draw.arc(surface, (210, 145, 60),
                        (lhx - int(9*s), lhy - int(7*s), int(18*s), int(13*s)),
                        math.pi, math.pi * 2, max(1, int(2*s)))
        # Wrist bands (leather)
        for _wbx, _wby in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (140, 80, 30), (_wbx, _wby), max(4, int(6*s)), max(2, int(3*s)))
        # Upper arm band on throwing arm
        _bmx = (rhx + sx) // 2
        _bmy = (rhy + sy) // 2
        pygame.draw.circle(surface, (200, 100, 20), (_bmx, _bmy), max(4, int(6*s)), max(2, int(3*s)))
        pygame.draw.circle(surface, (240, 160, 60), (_bmx, _bmy), max(2, int(3*s)))

    elif char_name == "Parry":
        # Plate armor chest piece on torso
        pygame.draw.rect(surface, (140, 150, 170),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (190, 200, 220),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Chest ridge lines on plate armor
        for _pri in range(4):
            _pry = sy + int(bl * (0.15 + _pri * 0.22))
            pygame.draw.line(surface, (200, 210, 230),
                             (sx - int(9*s), _pry), (sx + int(9*s), _pry), max(1, int(s)))
        # Chest center ridge
        pygame.draw.line(surface, (200, 210, 230),
                         (sx, sy + int(4*s)), (sx, sy + int(bl * 0.9)), max(1, int(s)))
        # Blue pauldron on left shoulder
        pygame.draw.ellipse(surface, (40, 80, 160),
                            (sx - int(18*s), sy - int(10*s), int(16*s), int(12*s)))
        pygame.draw.ellipse(surface, (80, 130, 210),
                            (sx - int(18*s), sy - int(10*s), int(16*s), int(12*s)),
                            max(1, int(s)))
        # Full-face helmet (rounded rect over head)
        pygame.draw.rect(surface, (130, 140, 160),
                         (hx - hd, hy - hd, hd * 2, hd * 2 - int(2*s)),
                         border_radius=max(3, int(hd // 2)))
        pygame.draw.rect(surface, (180, 190, 210),
                         (hx - hd, hy - hd, hd * 2, hd * 2 - int(2*s)),
                         max(1, int(2*s)), border_radius=max(3, int(hd // 2)))
        # Helmet crest ridge on top
        pygame.draw.rect(surface, (100, 120, 150),
                         (hx - int(3*s), hy - hd - int(4*s), int(6*s), int(6*s)),
                         border_radius=max(1, int(2*s)))
        # Visor slit
        pygame.draw.rect(surface, (60, 120, 200),
                         (hx - int(hd * 0.7), hy - int(4*s), int(hd * 1.4), max(3, int(5*s))),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (130, 180, 255),
                         (hx - int(hd * 0.7), hy - int(4*s), int(hd * 1.4), max(3, int(5*s))),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Sword in right hand with crossguard
        _swx, _swy = rhx, rhy
        pygame.draw.line(surface, (190, 190, 210),
                         (_swx, _swy + int(6*s)),
                         (_swx + facing * int(6*s), _swy - int(36*s)),
                         max(2, int(3*s)))
        # Crossguard
        pygame.draw.line(surface, (170, 140, 60),
                         (_swx - int(8*s), _swy - int(8*s)),
                         (_swx + int(8*s), _swy - int(8*s)),
                         max(2, int(3*s)))
        # Sword tip
        pygame.draw.polygon(surface, (220, 220, 240), [
            (_swx + facing * int(6*s), _swy - int(36*s)),
            (_swx + facing * int(10*s), _swy - int(46*s)),
            (_swx - facing * int(2*s), _swy - int(40*s)),
        ])
        # Blue buckler shield on left hand
        pygame.draw.circle(surface, (60, 120, 200), (lhx, lhy), max(5, int(9*s)))
        pygame.draw.circle(surface, (100, 160, 240), (lhx, lhy), max(5, int(9*s)), max(1, int(2*s)))
        pygame.draw.circle(surface, (200, 220, 255), (lhx, lhy), max(2, int(3*s)))

    elif char_name == "Healer":
        # Green cross on chest
        _hcx, _hcy = sx, sy + int(bl * 0.35)
        pygame.draw.line(surface, (60, 200, 80),
                         (_hcx, _hcy - int(8*s)), (_hcx, _hcy + int(8*s)), max(2, int(3*s)))
        pygame.draw.line(surface, (60, 200, 80),
                         (_hcx - int(8*s), _hcy), (_hcx + int(8*s), _hcy), max(2, int(3*s)))
        # Small halo above head
        pygame.draw.arc(surface, (100, 230, 120),
                        (hx - hd, hy - hd - int(6*s), hd * 2, int(8*s)),
                        0, math.pi, max(2, int(2*s)))

    elif char_name == "Iron Wall":
        # Full iron armor chest plate with rivets
        pygame.draw.rect(surface, (70, 75, 90),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (120, 125, 145),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Armor segment lines on chest
        for _iri in range(3):
            _iry = sy + int(bl * (0.25 + _iri * 0.25))
            pygame.draw.line(surface, (130, 135, 155),
                             (sx - int(10*s), _iry), (sx + int(10*s), _iry), max(1, int(2*s)))
        # Rivets (dots) on chest plate
        for _rvx, _rvy in [(-8, 0.1), (8, 0.1), (-8, 0.5), (8, 0.5), (-8, 0.85), (8, 0.85)]:
            pygame.draw.circle(surface, (150, 155, 175),
                               (sx + int(_rvx * s), sy + int(bl * _rvy)), max(1, int(2*s)))
        # Arm guards on both forearms
        for _agx, _agy in [(lhx, lhy), (rhx, rhy)]:
            _amid_x = (_agx + sx) // 2
            _amid_y = (_agy + sy) // 2
            pygame.draw.rect(surface, (80, 85, 100),
                             (_amid_x - int(5*s), _amid_y - int(4*s), int(10*s), int(8*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (130, 135, 155),
                             (_amid_x - int(5*s), _amid_y - int(4*s), int(10*s), int(8*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Shoulder plates
        for _spside in (-1, 1):
            pygame.draw.ellipse(surface, (65, 70, 85),
                                (sx + _spside * int(4*s), sy - int(12*s), int(14*s), int(12*s)))
            pygame.draw.ellipse(surface, (120, 125, 145),
                                (sx + _spside * int(4*s), sy - int(12*s), int(14*s), int(12*s)),
                                max(1, int(s)))
        # Knee guards
        for _kgside in (-1, 1):
            _kgx = wx + _kgside * int(6*s)
            _kgy = wy + int(bl * 0.4)
            pygame.draw.rect(surface, (75, 80, 95),
                             (_kgx - int(5*s), _kgy - int(4*s), int(10*s), int(8*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (125, 130, 150),
                             (_kgx - int(5*s), _kgy - int(4*s), int(10*s), int(8*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Heavy iron boots
        for _bside in (-1, 1):
            _bfx = wx + _bside * int(6*s)
            _bfy = wy + int(bl * 0.65)
            pygame.draw.rect(surface, (60, 65, 80),
                             (_bfx - int(6*s), _bfy, int(12*s), int(10*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (110, 115, 135),
                             (_bfx - int(6*s), _bfy, int(12*s), int(10*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Full-face iron helmet (keep existing)
        pygame.draw.rect(surface, (80, 80, 100),
                         (hx - hd, hy - hd // 2, hd * 2, hd + 2))
        pygame.draw.rect(surface, (120, 125, 145),
                         (hx - hd, hy - hd // 2, hd * 2, hd + 2), max(1, int(s)))
        # Helmet top dome
        pygame.draw.ellipse(surface, (75, 80, 95),
                            (hx - hd, hy - hd - int(4*s), hd * 2, int(hd * 1.0)))
        pygame.draw.ellipse(surface, (120, 125, 145),
                            (hx - hd, hy - hd - int(4*s), hd * 2, int(hd * 1.0)),
                            max(1, int(s)))
        # Horizontal visor slit (keep existing)
        pygame.draw.rect(surface, (160, 180, 200),
                         (hx - hd + 2, hy - int(4*s), hd * 2 - 4, max(3, int(4*s))))
        pygame.draw.rect(surface, (200, 220, 240),
                         (hx - hd + 2, hy - int(4*s), hd * 2 - 4, max(3, int(4*s))),
                         max(1, int(s)))

    elif char_name == "Pierce":
        # Jousting knight armor on torso
        pygame.draw.rect(surface, (150, 155, 165),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (190, 200, 215),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Armor ridge and plate lines
        for _pli in range(4):
            _ply = sy + int(bl * (0.12 + _pli * 0.22))
            pygame.draw.line(surface, (200, 210, 225),
                             (sx - int(9*s), _ply), (sx + int(9*s), _ply), max(1, int(s)))
        pygame.draw.line(surface, (200, 210, 225),
                         (sx, sy + int(3*s)), (sx, sy + int(bl*0.9)), max(1, int(2*s)))
        # Pointed shoulder pauldrons
        for _pdir in [-1, 1]:
            pygame.draw.polygon(surface, (160, 165, 180), [
                (sx + _pdir*int(9*s), sy - int(2*s)),
                (sx + _pdir*int(18*s), sy + int(3*s)),
                (sx + _pdir*int(16*s), sy + int(12*s)),
                (sx + _pdir*int(9*s), sy + int(10*s)),
            ])
            pygame.draw.polygon(surface, (200, 210, 225), [
                (sx + _pdir*int(9*s), sy - int(2*s)),
                (sx + _pdir*int(18*s), sy + int(3*s)),
                (sx + _pdir*int(16*s), sy + int(12*s)),
                (sx + _pdir*int(9*s), sy + int(10*s)),
            ], max(1, int(s)))
        # Full visor helmet
        pygame.draw.ellipse(surface, (155, 160, 170),
                            (hx - int(hd*1.15), hy - hd - int(3*s), int(hd*2.3), int(hd*1.8)))
        pygame.draw.ellipse(surface, (200, 210, 225),
                            (hx - int(hd*1.15), hy - hd - int(3*s), int(hd*2.3), int(hd*1.8)),
                            max(1, int(2*s)))
        # Visor slit
        pygame.draw.rect(surface, (30, 30, 40),
                         (hx - int(hd*0.75), hy - int(hd*0.45), int(hd*1.5), max(3, int(4*s))),
                         border_radius=max(1, int(s)))
        # Helmet crest plume
        for _plm in range(3):
            _plmx = hx + int((_plm - 1) * hd * 0.3)
            pygame.draw.line(surface, (200, 30, 30),
                             (_plmx, hy - hd - int(2*s)),
                             (_plmx + int((_plm-1)*2*s), hy - hd - int((10+_plm*3)*s)),
                             max(2, int(3*s)))
        # Lance with wrapped grip and pennant
        _tip_x = rhx + facing * int(36*s)
        # Lance shaft (tapered)
        pygame.draw.line(surface, (120, 80, 40), (rhx, rhy), (_tip_x, rhy), max(4, int(5*s)))
        pygame.draw.line(surface, (160, 110, 60), (rhx, rhy), (_tip_x, rhy), max(2, int(3*s)))
        # Grip wrapping
        for _gwi in range(5):
            _gwx = rhx + facing * int(_gwi * 5 * s)
            pygame.draw.line(surface, (80, 55, 20),
                             (_gwx, rhy - int(4*s)), (_gwx + facing*int(3*s), rhy + int(4*s)),
                             max(1, int(2*s)))
        # Guard ring at grip
        pygame.draw.circle(surface, (180, 180, 200),
                           (rhx + facing*int(8*s), rhy), max(4, int(6*s)))
        pygame.draw.circle(surface, (210, 220, 230),
                           (rhx + facing*int(8*s), rhy), max(4, int(6*s)), max(1, int(s)))
        # Pennant flag on lance
        _pfx = rhx + facing * int(20*s)
        pygame.draw.polygon(surface, (200, 30, 30), [
            (_pfx, rhy - int(4*s)),
            (_pfx + facing*int(12*s), rhy - int(2*s)),
            (_pfx, rhy + int(3*s)),
        ])
        # Arrow head tip
        pygame.draw.polygon(surface, (220, 225, 240), [
            (_tip_x + facing * int(10*s), rhy),
            (_tip_x - facing * int(3*s), rhy - int(6*s)),
            (_tip_x - facing * int(3*s), rhy + int(6*s)),
        ])
        # Silver eye glint
        pygame.draw.circle(surface, (220, 220, 240), (hx + facing * int(hd * 0.35), hy - int(2*s)),
                           max(2, int(3*s)))

    elif char_name == "Rage Stack":
        # Battle-worn torn vest
        pygame.draw.rect(surface, (60, 20, 10),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Torn vest edges (jagged rips)
        for _tri in range(4):
            _trx = sx - int(8*s) + _tri * int(5*s)
            _try2 = sy + int(bl * (0.7 + (_tri % 2)*0.1))
            pygame.draw.polygon(surface, (40, 12, 5), [
                (_trx, _try2),
                (_trx + int(2*s), _try2 + int(8*s)),
                (_trx + int(5*s), _try2 + int(4*s)),
                (_trx + int(5*s), _try2),
            ])
        # Tally marks on vest (stacking counter)
        for _tmi in range(4):
            _tmx = sx - int(6*s) + _tmi * int(4*s)
            pygame.draw.line(surface, (200, 40, 20),
                             (_tmx, sy + int(6*s)), (_tmx, sy + int(14*s)), max(1, int(2*s)))
        # Diagonal cross through 4 tallies
        pygame.draw.line(surface, (220, 60, 30),
                         (sx - int(8*s), sy + int(14*s)),
                         (sx + int(8*s), sy + int(6*s)), max(1, int(2*s)))
        # Rage veins on both arms
        for _rvx, _rvy, _rex, _rey in [(sx, sy+int(bl*0.15), lhx, lhy),
                                         (sx, sy+int(bl*0.15), rhx, rhy)]:
            for _vi in range(3):
                _vt1 = 0.2 + _vi * 0.25
                _vt2 = _vt1 + 0.15
                _vx1 = int(_rvx + (_rex - _rvx) * _vt1) + int((_vi-1)*3*s)
                _vy1 = int(_rvy + (_rey - _rvy) * _vt1)
                _vx2 = int(_rvx + (_rex - _rvx) * _vt2) - int((_vi-1)*2*s)
                _vy2 = int(_rvy + (_rey - _rvy) * _vt2)
                pygame.draw.line(surface, (180, 30, 10), (_vx1, _vy1), (_vx2, _vy2), max(1, int(s)))
        # Rage aura glow
        _rsurf = pygame.Surface((hd*8, hd*8), pygame.SRCALPHA)
        pygame.draw.ellipse(_rsurf, (200, 30, 10, 40), (0, 0, hd*8, hd*8))
        surface.blit(_rsurf, (sx - hd*4, sy - hd*2))
        # Jagged flames on fists
        for _fx, _fy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (200, 40, 20), (_fx, _fy), max(5, int(8*s)))
            for _fi in range(6):
                _fa = _fi * 1.047
                _flen = int((7 + _fi % 3 * 3) * s)
                pygame.draw.line(surface, (255, 120, 20),
                                 (_fx, _fy),
                                 (_fx + int(math.cos(_fa) * _flen),
                                  _fy + int(math.sin(_fa) * _flen)), max(1, int(2*s)))
        # Sweat drops on face
        for _sdi, _sdox in enumerate([-1, 1]):
            pygame.draw.circle(surface, (100, 180, 220),
                               (hx + _sdox*int(hd*0.7), hy - int(hd*0.4) + _sdi*int(4*s)),
                               max(1, int(2*s)))
        # Wide red headband with knot
        band_y = hy + int(hd * 0.15)
        pygame.draw.rect(surface, (180, 15, 15),
                         (hx - hd, band_y - int(3*s), hd*2, max(4, int(6*s))))
        pygame.draw.rect(surface, (220, 30, 30),
                         (hx - hd, band_y - int(3*s), hd*2, max(4, int(6*s))),
                         max(1, int(s)))
        # Knot knot at side
        _kx = hx + facing * hd
        pygame.draw.polygon(surface, (200, 20, 20), [
            (_kx - int(2*s), band_y - int(5*s)),
            (_kx + int(2*s), band_y - int(5*s)),
            (_kx + int(4*s), band_y),
            (_kx + int(2*s), band_y + int(5*s)),
            (_kx - int(2*s), band_y + int(5*s)),
            (_kx - int(4*s), band_y),
        ])

    elif char_name == "Phoenix":
        # Full fiery wings spreading from back (drawn first/behind)
        _wingsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        _wbase_x, _wbase_y = sx, sy + int(bl * 0.2)
        for _wi, _wside in enumerate([-1, 1]):
            _wcols = [(230, 80, 10, 80), (240, 140, 20, 60), (255, 200, 60, 40)]
            for _wli, _wcol in enumerate(_wcols):
                _wspan = int((28 - _wli * 5) * s)
                _wpts = [
                    (_wbase_x, _wbase_y),
                    (_wbase_x + _wside * _wspan, _wbase_y - int(20*s) - _wli*int(5*s)),
                    (_wbase_x + _wside * int((_wspan * 1.3)), _wbase_y + int(10*s)),
                    (_wbase_x + _wside * int((_wspan * 0.8)), _wbase_y + int(bl * 0.7)),
                    (_wbase_x, _wbase_y + int(bl * 0.5)),
                ]
                pygame.draw.polygon(_wingsurf, _wcol, _wpts)
        # Wing feather tips
        for _wside2 in [-1, 1]:
            for _fti in range(5):
                _fta = math.pi * (0.1 + _fti * 0.15)
                _ftx = _wbase_x + _wside2 * int(math.cos(_fta) * 30 * s)
                _fty = _wbase_y - int(math.sin(_fta) * 25 * s)
                pygame.draw.line(_wingsurf, (255, 220, 80, 150),
                                 (_wbase_x, _wbase_y), (_ftx, _fty), max(1, int(2*s)))
        surface.blit(_wingsurf, (0, 0))
        # Flame body suit on torso
        pygame.draw.rect(surface, (180, 60, 10),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (230, 110, 20),
                         (sx - int(9*s), sy, int(18*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Flame lick patterns on torso
        for _fli in range(4):
            _flx = sx - int(8*s) + _fli * int(5*s)
            _flb = wy - int(2*s)
            _fltop = _flb - int((8 + (_fli % 2) * 6) * s)
            pygame.draw.polygon(surface, (255, 180, 40), [
                (_flx - int(3*s), _flb),
                (_flx + int(3*s), _flb),
                (_flx + int(s), _fltop),
                (_flx - int(s), _fltop),
            ])
        # Feather-scale armor lines on arms
        for _asx, _asy, _aex, _aey in [(sx, sy+int(bl*0.15), lhx, lhy),
                                         (sx, sy+int(bl*0.15), rhx, rhy)]:
            for _fsi in range(4):
                _ft = _fsi / 3.0
                _fsx = int(_asx + (_aex - _asx) * _ft)
                _fsy = int(_asy + (_aey - _asy) * _ft)
                pygame.draw.ellipse(surface, (220, 100, 20),
                                    (_fsx - int(4*s), _fsy - int(2*s), int(8*s), int(5*s)))
                pygame.draw.ellipse(surface, (255, 160, 40),
                                    (_fsx - int(4*s), _fsy - int(2*s), int(8*s), int(5*s)),
                                    max(1, int(s)))
        # Glowing ember aura around whole body
        _esurf = pygame.Surface((hd*10, hd*10), pygame.SRCALPHA)
        pygame.draw.ellipse(_esurf, (230, 80, 10, 30), (0, 0, hd*10, hd*10))
        surface.blit(_esurf, (sx - hd*5, sy - hd*2))
        # Large flame crown crest on head
        for _pi in range(5):
            _poff = (_pi - 2) * int(hd * 0.4)
            _ph = int((10 - abs(_pi - 2) * 3) * s) + hd
            _pcol = (255, 180, 40) if _pi % 2 == 0 else (230, 80, 10)
            pygame.draw.line(surface, _pcol,
                             (hx + _poff, hy - hd), (hx + _poff, hy - _ph),
                             max(2, int(3*s)))
            pygame.draw.circle(surface, (255, 230, 100), (hx + _poff, hy - _ph),
                               max(2, int(4*s)))
        # Ember tail below body
        for _emi in range(5):
            _emx = wx + int((_emi - 2) * 4 * s)
            pygame.draw.line(surface, (255, 140, 20),
                             (_emx, wy), (_emx + int((_emi-2)*2*s), wy + int((8 + _emi*3)*s)),
                             max(1, int(2*s)))
            pygame.draw.circle(surface, (255, 200, 60),
                               (_emx + int((_emi-2)*2*s), wy + int((8 + _emi*3)*s)),
                               max(1, int(2*s)))

    elif char_name == "Chain Fighter":
        # Studded leather vest on torso
        pygame.draw.rect(surface, (60, 35, 15),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (90, 60, 30),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Vest studs
        for _vsi in range(3):
            for _vsj in range(2):
                _vsx = sx - int(6*s) + _vsj * int(12*s)
                _vsy = sy + int(bl * (0.15 + _vsi * 0.28))
                pygame.draw.circle(surface, (140, 120, 60), (_vsx, _vsy), max(1, int(2*s)))
        # Heavy chain belt at waist
        for _cbi in range(6):
            _cbx = sx - int(12*s) + _cbi * int(5*s)
            _cby = wy - int(4*s)
            pygame.draw.ellipse(surface, (80, 80, 80),
                                (_cbx - int(3*s), _cby - int(2*s), int(6*s), int(4*s)), max(1, int(s)))
        # Spiked collar around neck
        _ncy = sy - int(4*s)
        pygame.draw.rect(surface, (50, 30, 10),
                         (sx - int(7*s), _ncy, int(14*s), int(5*s)), border_radius=max(1, int(2*s)))
        for _spki in range(5):
            _spkx = sx - int(6*s) + _spki * int(3*s)
            pygame.draw.polygon(surface, (120, 110, 60), [
                (_spkx - int(2*s), _ncy),
                (_spkx + int(2*s), _ncy),
                (_spkx, _ncy - int(5*s)),
            ])
        # Chain links along left arm (wrist toward elbow)
        _lax, _lay = lhx, lhy
        _lelbx = (_lax + sx) // 2
        _lelby = (_lay + sy) // 2
        for _cli in range(5):
            _ct = _cli / 4.0
            _clx = int(_lax + (_lelbx - _lax) * _ct)
            _cly = int(_lay + (_lelby - _lay) * _ct)
            pygame.draw.ellipse(surface, (80, 160, 160),
                                (_clx - int(4*s), _cly - int(2*s), int(8*s), int(5*s)),
                                max(1, int(2*s)))
        # Chain links along right arm
        _rax, _ray = rhx, rhy
        _relbx = (_rax + sx) // 2
        _relby = (_ray + sy) // 2
        for _cli in range(5):
            _ct = _cli / 4.0
            _clx = int(_rax + (_relbx - _rax) * _ct)
            _cly = int(_ray + (_relby - _ray) * _ct)
            pygame.draw.ellipse(surface, (80, 160, 160),
                                (_clx - int(4*s), _cly - int(2*s), int(8*s), int(5*s)),
                                max(1, int(2*s)))
        # Chain wrist links on both hands
        for _cx2, _cy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (60, 160, 160), (_cx2, _cy2), max(4, int(7*s)), max(1, int(2*s)))
            pygame.draw.circle(surface, (100, 200, 200), (_cx2, _cy2), max(2, int(4*s)), max(1, int(2*s)))
        # Ball-and-chain weapon hanging from right hand
        _bcy = rhy + int(16*s)
        pygame.draw.line(surface, (90, 90, 100),
                         (rhx, rhy + int(7*s)), (rhx + int(facing * 3 * s), _bcy),
                         max(1, int(2*s)))
        pygame.draw.circle(surface, (60, 60, 70), (rhx + int(facing * 3 * s), _bcy), max(4, int(8*s)))
        pygame.draw.circle(surface, (100, 100, 115), (rhx + int(facing * 3 * s), _bcy),
                           max(4, int(8*s)), max(1, int(s)))
        # Spikes on ball
        for _bsi in range(6):
            _bsa = _bsi * 1.047
            pygame.draw.line(surface, (80, 80, 95),
                             (rhx + int(facing * 3 * s) + int(math.cos(_bsa) * 7 * s),
                              _bcy + int(math.sin(_bsa) * 7 * s)),
                             (rhx + int(facing * 3 * s) + int(math.cos(_bsa) * 11 * s),
                              _bcy + int(math.sin(_bsa) * 11 * s)),
                             max(1, int(2*s)))

    elif char_name == "Breaker":
        # Demolition worker body armor (dark charcoal)
        pygame.draw.rect(surface, (45, 40, 50),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 70, 90),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Blast impact cracks on chest armor
        for _bci, (_bcx1, _bcy1, _bcx2, _bcy2) in enumerate([
            (0, 6, -7, 20), (2, 4, 8, 22), (-3, 15, 5, 30), (0, 22, -8, 35)]):
            pygame.draw.line(surface, (130, 110, 160),
                             (sx + int(_bcx1*s), sy + int(_bcy1*s)),
                             (sx + int(_bcx2*s), sy + int(_bcy2*s)), max(1, int(s)))
        # Wrecking ball emblem (circle with cracks)
        _wbex, _wbey = sx, sy + int(bl * 0.48)
        pygame.draw.circle(surface, (90, 70, 110), (_wbex, _wbey), max(7, int(10*s)))
        pygame.draw.circle(surface, (130, 110, 160), (_wbex, _wbey), max(7, int(10*s)), max(1, int(2*s)))
        for _wbci in range(4):
            _wba = _wbci * math.pi * 0.5
            pygame.draw.line(surface, (160, 140, 190),
                             (_wbex, _wbey),
                             (_wbex + int(math.cos(_wba)*8*s), _wbey + int(math.sin(_wba)*8*s)),
                             max(1, int(s)))
        # Wrecking ball chain from right hand
        _wbcx, _wbcy = rhx + facing*int(8*s), rhy + int(20*s)
        for _wci in range(4):
            _wct = _wci / 3.0
            _wcx = int(rhx + (_wbcx - rhx) * _wct)
            _wcy = int(rhy + (_wbcy - rhy) * _wct)
            pygame.draw.ellipse(surface, (100, 80, 120),
                                (_wcx - int(4*s), _wcy - int(2*s), int(8*s), int(5*s)), max(1, int(2*s)))
        # Wrecking ball
        pygame.draw.circle(surface, (70, 55, 85), (_wbcx, _wbcy), max(6, int(10*s)))
        pygame.draw.circle(surface, (110, 90, 130), (_wbcx, _wbcy), max(6, int(10*s)), max(1, int(2*s)))
        # Ball spike bumps
        for _wbsi in range(4):
            _wbsa = _wbsi * math.pi * 0.5
            pygame.draw.circle(surface, (140, 120, 160),
                               (_wbcx + int(math.cos(_wbsa)*8*s),
                                _wbcy + int(math.sin(_wbsa)*8*s)), max(2, int(3*s)))
        # Heavy purple gauntlets (expanded)
        for _gx, _gy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.rect(surface, (80, 60, 130),
                             (_gx - int(8*s), _gy - int(6*s), int(16*s), int(12*s)),
                             border_radius=max(2, int(3*s)))
            pygame.draw.rect(surface, (130, 100, 190),
                             (_gx - int(8*s), _gy - int(6*s), int(16*s), int(12*s)),
                             max(1, int(2*s)), border_radius=max(2, int(3*s)))
            # Knuckle plates
            for _kpi in range(3):
                _kpx2 = _gx - int(4*s) + _kpi * int(4*s)
                pygame.draw.rect(surface, (100, 80, 160),
                                 (_kpx2, _gy - int(6*s), int(4*s), int(5*s)),
                                 border_radius=max(1, int(s)))
                pygame.draw.rect(surface, (160, 130, 210),
                                 (_kpx2, _gy - int(6*s), int(4*s), int(5*s)),
                                 max(1, int(s)), border_radius=max(1, int(s)))
        # Cracked forehead line with splinter
        pygame.draw.line(surface, (130, 110, 160),
                         (hx - int(5*s), hy - int(hd * 0.55)),
                         (hx + int(3*s), hy + int(hd * 0.35)), max(2, int(2*s)))
        pygame.draw.line(surface, (100, 80, 140),
                         (hx, hy - int(hd * 0.1)),
                         (hx - int(6*s), hy + int(hd * 0.15)), max(1, int(s)))
        # Demolition hard hat (cracked)
        pygame.draw.ellipse(surface, (80, 70, 90),
                            (hx - int(hd*1.2), hy - hd - int(6*s), int(hd*2.4), int(hd*1.3)))
        pygame.draw.ellipse(surface, (120, 100, 140),
                            (hx - int(hd*1.2), hy - hd - int(6*s), int(hd*2.4), int(hd*1.3)),
                            max(1, int(2*s)))
        pygame.draw.line(surface, (160, 130, 190),
                         (hx - int(hd*0.3), hy - hd - int(5*s)),
                         (hx + int(hd*0.5), hy - int(hd*0.1)), max(1, int(s)))

    elif char_name == "Titan Grip":
        # Massive iron-muscle torso (dark steel + flex lines)
        pygame.draw.rect(surface, (55, 45, 75),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (100, 80, 140),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(2*s)), border_radius=max(3, int(5*s)))
        # Muscle definition lines on chest
        pygame.draw.line(surface, (80, 60, 110),
                         (sx, sy + int(4*s)), (sx, sy + int(bl*0.6)), max(1, int(2*s)))
        for _mdi in range(3):
            _mdy = sy + int(bl * (0.2 + _mdi * 0.18))
            pygame.draw.arc(surface, (80, 60, 110),
                            (sx - int(8*s), _mdy, int(8*s), int(8*s)),
                            math.pi * 0.5, math.pi * 1.5, max(1, int(s)))
            pygame.draw.arc(surface, (80, 60, 110),
                            (sx, _mdy, int(8*s), int(8*s)),
                            math.pi * 1.5, math.pi * 2.5, max(1, int(s)))
        # Iron grip emblem on chest
        _ige_x, _ige_y = sx, sy + int(bl * 0.55)
        pygame.draw.circle(surface, (70, 55, 100), (_ige_x, _ige_y), max(7, int(11*s)))
        pygame.draw.circle(surface, (120, 95, 160), (_ige_x, _ige_y), max(7, int(11*s)), max(1, int(2*s)))
        # Fist silhouette inside emblem
        pygame.draw.rect(surface, (140, 110, 180),
                         (_ige_x - int(4*s), _ige_y - int(5*s), int(8*s), int(8*s)),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (160, 130, 200),
                         (_ige_x - int(4*s), _ige_y - int(5*s), int(8*s), int(8*s)),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Forearm vein lines
        for _fax, _fay, _fex, _fey in [(sx, sy+int(bl*0.15), lhx, lhy),
                                         (sx, sy+int(bl*0.15), rhx, rhy)]:
            for _vni in range(3):
                _vnt = 0.3 + _vni * 0.2
                _vnx = int(_fax + (_fex - _fax) * _vnt) + int((_vni-1)*3*s)
                _vny = int(_fay + (_fey - _fay) * _vnt)
                _vnx2 = int(_fax + (_fex - _fax) * (_vnt + 0.15)) - int((_vni-1)*2*s)
                _vny2 = int(_fay + (_fey - _fay) * (_vnt + 0.15))
                pygame.draw.line(surface, (130, 100, 170), (_vnx, _vny), (_vnx2, _vny2), max(1, int(s)))
        # Thick arm bands (iron bracers)
        for _abx, _aby in [(lhx, lhy), (rhx, rhy)]:
            _abmx = (_abx + sx) // 2
            _abmy = (_aby + sy) // 2
            pygame.draw.rect(surface, (60, 45, 85),
                             (_abmx - int(7*s), _abmy - int(4*s), int(14*s), int(8*s)),
                             border_radius=max(2, int(3*s)))
            pygame.draw.rect(surface, (110, 85, 150),
                             (_abmx - int(7*s), _abmy - int(4*s), int(14*s), int(8*s)),
                             max(1, int(2*s)), border_radius=max(2, int(3*s)))
            # Rivet dots on bracer
            for _rv in range(4):
                pygame.draw.circle(surface, (140, 115, 180),
                                   (_abmx - int(5*s) + _rv*int(3*s), _abmy), max(1, int(2*s)))
        # Large claw grip hands
        for _gx2, _gy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (70, 50, 100), (_gx2, _gy2), max(7, int(12*s)))
            pygame.draw.circle(surface, (120, 90, 160), (_gx2, _gy2), max(7, int(12*s)), max(1, int(2*s)))
            # Knuckle ridges
            for _kri in range(4):
                _kra = math.pi * (0.1 + _kri * 0.2)
                pygame.draw.circle(surface, (150, 120, 190),
                                   (_gx2 + int(math.cos(_kra) * 8 * s * (-facing)),
                                    _gy2 - int(math.sin(abs(_kra)) * 6 * s)),
                                   max(2, int(3*s)))
            # Claw lines (longer and sharper)
            for _ci2 in range(4):
                _ca = (_ci2 - 1.5) * 0.35
                _clen = int((11 + _ci2 % 2 * 3) * s)
                pygame.draw.line(surface, (170, 140, 210),
                                 (_gx2, _gy2),
                                 (_gx2 + int(math.cos(_ca) * _clen * (-facing)),
                                  _gy2 - int(abs(math.sin(_ca)) * _clen)),
                                 max(2, int(2*s)))

    elif char_name == "Overload":
        # Glowing rainbow aura dots around entire body
        for _oi in range(12):
            _oa = _oi * 0.524
            _orx = hx + int(math.cos(_oa) * (hd + int(8*s)))
            _ory = hy + int(math.sin(_oa) * (hd + int(8*s)))
            _ocol = [(255,60,60),(255,160,0),(255,255,0),(60,255,60),(0,200,255),(180,0,255)][_oi % 6]
            pygame.draw.circle(surface, _ocol, (_orx, _ory), max(2, int(4*s)))
        # Crown
        for _ki in range(5):
            _kx = hx - hd + _ki * (hd // 2)
            pygame.draw.line(surface, (255, 220, 0),
                             (_kx, hy - hd), (_kx, hy - hd - int((5 - abs(_ki - 2)) * 4 * s)),
                             max(1, int(2*s)))

    elif char_name == "Glitch":
        # Corrupted torso segments — broken/offset rect layers in different colors
        for _goff, _gcol in [
            ((-3, -2), (0, 240, 255)),   # cyan shifted left
            ((4, 1), (255, 0, 200)),      # magenta shifted right
            ((0, 3), (60, 255, 60)),      # green shifted down
        ]:
            pygame.draw.rect(surface, _gcol,
                             (sx - int(9*s) + int(_goff[0]*s),
                              sy + int(_goff[1]*s),
                              int(18*s), bl),
                             max(1, int(2*s)), border_radius=max(1, int(2*s)))
        # Main torso base (slightly opaque dark)
        pygame.draw.rect(surface, (20, 20, 30),
                         (sx - int(8*s), sy + int(2*s), int(16*s), bl - int(4*s)),
                         border_radius=max(1, int(2*s)))
        # Scan lines across body
        for _sli in range(6):
            _sly = sy + int(bl * (_sli / 6.0))
            _slcol = [(0, 220, 255), (255, 0, 180), (80, 255, 80)][_sli % 3]
            pygame.draw.line(surface, _slcol,
                             (sx - int(9*s), _sly), (sx + int(9*s), _sly), max(1, int(s)))
        # Corrupted arm outline rectangles
        for _arx, _ary in [(lhx, lhy), (rhx, rhy)]:
            _amid_x = (_arx + sx) // 2
            _amid_y = (_ary + sy) // 2
            for _agoff, _agcol in [((-2, 0), (0, 240, 255)), ((2, 0), (255, 0, 200))]:
                pygame.draw.rect(surface, _agcol,
                                 (_amid_x - int(4*s) + int(_agoff[0]*s),
                                  _amid_y - int(3*s) + int(_agoff[1]*s),
                                  int(8*s), int(6*s)),
                                 max(1, int(s)))
        # Glitch pixel clusters at different body parts
        _glitch_spots = [
            (sx - int(12*s), sy + int(bl * 0.2)),
            (sx + int(10*s), sy + int(bl * 0.5)),
            (wx - int(8*s), wy - int(4*s)),
            (sx + int(14*s), sy + int(bl * 0.3)),
        ]
        _glitch_colors = [(60, 255, 60), (255, 60, 255), (60, 200, 255), (255, 200, 0)]
        for _gpi, (_gpx, _gpy) in enumerate(_glitch_spots):
            for _pj in range(3):
                _grx = _gpx + random.randint(-int(4*s), int(4*s))
                _gry = _gpy + random.randint(-int(4*s), int(4*s))
                pygame.draw.rect(surface, _glitch_colors[_gpi],
                                 (_grx, _gry, max(2, int(3*s)), max(2, int(3*s))))
        # Glitchy pixel scatter around head
        for _gli in range(8):
            _glx = hx + random.randint(-hd - 6, hd + 6)
            _gly = hy + random.randint(-hd - 6, hd + 6)
            _glc = [(60,255,60),(255,60,255),(60,200,255),(255,200,0)][_gli % 4]
            pygame.draw.rect(surface, _glc, (_glx, _gly, max(2, int(4*s)), max(2, int(4*s))))
        # Glitch bar across face
        pygame.draw.rect(surface, (60, 255, 120),
                         (hx - hd, hy - int(3*s), hd * 2, max(2, int(4*s))))
        # Secondary offset glitch bar
        pygame.draw.rect(surface, (255, 0, 180),
                         (hx - hd + int(3*s), hy + int(2*s), hd * 2 - int(4*s), max(1, int(2*s))))

    elif char_name == "Nick of Time":
        # Hourglass on chest
        _ncx, _ncy = sx, sy + int(bl * 0.3)
        pygame.draw.polygon(surface, (60, 200, 255), [
            (_ncx - int(7*s), _ncy - int(8*s)),
            (_ncx + int(7*s), _ncy - int(8*s)),
            (_ncx, _ncy),
        ])
        pygame.draw.polygon(surface, (60, 200, 255), [
            (_ncx - int(7*s), _ncy + int(8*s)),
            (_ncx + int(7*s), _ncy + int(8*s)),
            (_ncx, _ncy),
        ])
        pygame.draw.rect(surface, (100, 220, 255),
                         (_ncx - int(7*s), _ncy - int(9*s), int(14*s), max(2, int(3*s))))
        pygame.draw.rect(surface, (100, 220, 255),
                         (_ncx - int(7*s), _ncy + int(6*s), int(14*s), max(2, int(3*s))))
        # Clock hand on head
        pygame.draw.circle(surface, (60, 200, 255), (hx, hy), hd, max(1, int(2*s)))
        pygame.draw.line(surface, (200, 240, 255),
                         (hx, hy), (hx + facing * int(hd * 0.8), hy - int(hd * 0.5)),
                         max(1, int(2*s)))

    elif char_name == "Buffer":
        # Green plus signs on chest (stat-up symbol)
        _bx, _by = sx, sy
        for _boff in [(-int(6*s), 0), (int(6*s), 0)]:
            _cx2 = _bx + _boff[0]
            pygame.draw.line(surface, (180, 255, 180),
                             (_cx2 - int(4*s), _by), (_cx2 + int(4*s), _by), max(2, int(3*s)))
            pygame.draw.line(surface, (180, 255, 180),
                             (_cx2, _by - int(4*s)), (_cx2, _by + int(4*s)), max(2, int(3*s)))
        # Upward arrow on head
        pygame.draw.polygon(surface, (100, 240, 100), [
            (hx, hy - hd - int(7*s)),
            (hx - int(5*s), hy - hd),
            (hx + int(5*s), hy - hd),
        ])

    elif char_name == "Cursed":
        # Purple skull on chest
        _cx2, _cy2 = sx, sy - int(bl * 0.1)
        pygame.draw.circle(surface, (140, 0, 140), (_cx2, _cy2), max(5, int(8*s)))
        pygame.draw.circle(surface, (60, 0, 60),   (_cx2, _cy2), max(3, int(5*s)))
        # Eye sockets
        for _ex in [_cx2 - int(3*s), _cx2 + int(3*s)]:
            pygame.draw.circle(surface, (0, 0, 0), (_ex, _cy2 - int(2*s)), max(1, int(2*s)))
        # Dark cracked halo above head
        pygame.draw.arc(surface, (100, 0, 100),
                        (hx - hd - int(3*s), hy - hd * 2 - int(4*s), (hd + int(3*s)) * 2, hd + int(4*s)),
                        0, math.pi, max(2, int(3*s)))
        # Jagged crack lines on chest
        pygame.draw.lines(surface, (200, 0, 200), False, [
            (sx - int(5*s), sy - int(8*s)),
            (sx - int(2*s), sy - int(2*s)),
            (sx + int(4*s), sy + int(5*s)),
        ], max(1, int(2*s)))


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

    elif s == 23:  # Portal World
        # Deep void background gradient (dark purple → black)
        for _gy in range(0, HEIGHT, 3):
            _t = _gy / HEIGHT
            _r = int(10 + _t * 8)
            _g = int(5  + _t * 5)
            _b = int(30 + _t * 20)
            pygame.draw.line(surface, (_r, _g, _b), (0, _gy), (WIDTH, _gy))
        # Swirling portal aura rings scattered in background
        _portal_bg = [
            ((80, 100, 220),  110, 220),   # blue
            ((220, 120,  20), 450,  60),   # orange
            ((20,  200,  80), 170, 350),   # green
            ((180,  40, 220), 240, 110),   # purple
            ((220,  40,  40), 290, GROUND_Y-280),  # red
        ]
        for _pc, _px2, _py2 in _portal_bg:
            for _pr in range(28, 6, -7):
                _alpha = max(20, 60 - _pr * 2)
                _psurf = pygame.Surface((_pr*2+2, _pr*2+2), pygame.SRCALPHA)
                pygame.draw.circle(_psurf, (_pc[0], _pc[1], _pc[2], _alpha), (_pr+1, _pr+1), _pr, 2)
                surface.blit(_psurf, (_px2 - _pr - 1, _py2 - _pr - 1))
        # Stars / floating particles
        for _sx, _sy in [(50,40),(130,90),(220,25),(350,70),(470,15),(590,50),(720,30),(840,80),
                          (90,150),(320,130),(600,110),(800,160),(160,260),(500,240),(750,280)]:
            pygame.draw.circle(surface, (160, 140, 200), (_sx, _sy), 1)
        # Floating platform glow (subtle teal glow under each platform)
        for _fpx, _fpy, _fpw in [(80,GROUND_Y-110,130),(690,GROUND_Y-110,130),(380,GROUND_Y-200,140),
                                   (190,GROUND_Y-310,100),(610,GROUND_Y-310,100),(370,GROUND_Y-380,120)]:
            _gsurf = pygame.Surface((_fpw+20, 12), pygame.SRCALPHA)
            for _gi in range(6):
                pygame.draw.rect(_gsurf, (80, 220, 200, 18 - _gi * 3), (0, _gi, _fpw+20, 2))
            surface.blit(_gsurf, (_fpx - 10, _fpy + 10))
        # Void ground
        pygame.draw.rect(surface, (18, 10, 35), (0, GROUND_Y+2, WIDTH, HEIGHT-GROUND_Y-2))
        pygame.draw.line(surface, (80, 40, 160), (0, GROUND_Y+2), (WIDTH, GROUND_Y+2), 3)
        # Ground energy pulses (horizontal glow lines)
        for _gl in range(3):
            _glsurf = pygame.Surface((WIDTH, 4), pygame.SRCALPHA)
            pygame.draw.line(_glsurf, (120, 60, 200, 60 - _gl * 18), (0, 0), (WIDTH, 0), 2)
            surface.blit(_glsurf, (0, GROUND_Y + 4 + _gl * 5))


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


