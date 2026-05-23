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
        t = pygame.time.get_ticks()
        # Ethereal aura — faint glowing halo behind body
        _aura_alpha = int(60 + 30 * math.sin(t * 0.003))
        for _ar in range(3, 0, -1):
            _ac = (170 + _ar*15, 170 + _ar*15, 230 + _ar*5)
            pygame.draw.circle(surface, _ac, (hx, hy), hd + int(_ar * 5 * s), max(1, int(2*s)))
        # Sheet draped from shoulders
        sheet_pts = [
            (sx - int(hd*1.25), sy + int(5*s)), (sx - int(hd*1.45), wy + int(28*s)),
            (sx - int(hd*.8), wy + int(18*s)), (sx, wy + int(33*s)),
            (sx + int(hd*.8), wy + int(18*s)), (sx + int(hd*1.45), wy + int(28*s)),
            (sx + int(hd*1.25), sy + int(5*s))]
        pygame.draw.polygon(surface, (185, 185, 220), sheet_pts)
        pygame.draw.polygon(surface, (215, 215, 255), sheet_pts, max(1, int(2*s)))
        # Hollow black eye holes
        for _ex in (sx - int(hd*0.35), sx + int(hd*0.35)):
            _ey = sy + int(bl*0.22)
            pygame.draw.ellipse(surface, (20, 15, 35),
                                (_ex - int(hd*.28), _ey - int(hd*.18), int(hd*.56), int(hd*.38)))
            # Pale inner pupil flicker
            if (t // 300) % 3 != 0:
                pygame.draw.ellipse(surface, (200, 200, 240),
                                    (_ex - int(hd*.1), _ey - int(hd*.08), int(hd*.2), int(hd*.16)))
        # Wispy squiggly bottom fringe on sheet
        _fy = wy + int(28*s)
        for _fi in range(-1, 2):
            _fx = sx + _fi * int(hd*0.8)
            _wave = int(5 * s * math.sin(t * 0.004 + _fi * 1.5))
            pygame.draw.circle(surface, (185, 185, 220), (_fx, _fy + _wave), max(3, int(5*s)))
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
        pygame.draw.polygon(surface, (115, 0, 38), cape_pts, max(1, int(2*s)))
        # Formal dark suit vest on torso
        pygame.draw.rect(surface, (20, 10, 25),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        # White shirt collar and tie
        pygame.draw.polygon(surface, (230, 225, 235), [
            (sx - int(5*s), sy + int(2*s)), (sx + int(5*s), sy + int(2*s)),
            (sx + int(2*s), sy + int(bl*0.35)), (sx - int(2*s), sy + int(bl*0.35))])
        # Blood red tie
        pygame.draw.polygon(surface, (160, 0, 20), [
            (sx - int(2*s), sy + int(bl*0.35)), (sx + int(2*s), sy + int(bl*0.35)),
            (sx + int(3*s), sy + int(bl*0.6)), (sx, sy + int(bl*0.72)),
            (sx - int(3*s), sy + int(bl*0.6))])
        # Pale hands
        for _vhx, _vhy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (200, 180, 190), (_vhx, _vhy), max(4, int(6*s)))
        # Fangs
        for fx_off in [-int(hd*.3), int(hd*.3)]:
            pygame.draw.polygon(surface, WHITE, [
                (hx + fx_off - int(hd*.12), hy + int(hd*.42)),
                (hx + fx_off + int(hd*.12), hy + int(hd*.42)),
                (hx + fx_off, hy + int(hd*.72))])
        # Redraw head
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Astronaut":
        # White space-suit torso
        pygame.draw.rect(surface, (220, 225, 235),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (180, 185, 200),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(s)),
                         border_radius=max(3, int(5*s)))
        # Chest life-support panel — orange rectangle with status lights
        pygame.draw.rect(surface, (200, 120, 30),
                         (sx - int(7*s), sy + int(bl*0.2), int(14*s), int(bl*0.35)),
                         border_radius=max(1, int(2*s)))
        for _li, _lc in enumerate([(80, 255, 80), (255, 80, 80), (255, 220, 0)]):
            pygame.draw.circle(surface, _lc,
                               (sx - int(4*s) + _li*int(4*s), sy + int(bl*0.27)),
                               max(1, int(2*s)))
        # Shoulder rings (suit joints)
        for _srx in (sx - int(11*s), sx + int(11*s)):
            pygame.draw.circle(surface, (160, 165, 180), (_srx, sy + int(4*s)),
                               max(3, int(5*s)), max(1, int(2*s)))
        # Bulky gloves
        for _gx, _gy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (200, 205, 215), (_gx, _gy), max(5, int(8*s)))
            pygame.draw.circle(surface, (160, 165, 180), (_gx, _gy), max(5, int(8*s)),
                               max(1, int(s)))
        # Oxygen tank on back (behind torso)
        _tkx = sx - facing*int(13*s)
        pygame.draw.rect(surface, (180, 185, 200),
                         (_tkx - int(4*s), sy + int(bl*0.1), int(8*s), int(bl*0.75)),
                         border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (140, 145, 160),
                         (_tkx - int(4*s), sy + int(bl*0.1), int(8*s), int(bl*0.75)),
                         max(1, int(s)), border_radius=max(2, int(4*s)))
        # Space helmet (dome around head)
        pygame.draw.circle(surface, (175, 195, 235), (hx, hy), int(hd * 1.38))
        pygame.draw.circle(surface, (95, 135, 195), (hx, hy), int(hd * 1.38), max(3, int(4*s)))
        # Visor
        pygame.draw.ellipse(surface, (55, 115, 195), (hx - int(hd*.88), hy - int(hd*.72), int(hd*1.76), int(hd*1.18)))
        pygame.draw.ellipse(surface, (100, 160, 230), (hx - int(hd*.88), hy - int(hd*.72), int(hd*1.76), int(hd*1.18)), 2)
        # Visor shine streak
        pygame.draw.line(surface, (180, 220, 255),
                         (hx - int(hd*.6), hy - int(hd*.55)),
                         (hx - int(hd*.2), hy - int(hd*.6)), max(1, int(s)))
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
        t = pygame.time.get_ticks()
        # Dark basalt rock body with glowing interior
        pygame.draw.rect(surface, (50, 25, 10),
                         (sx - int(12*s), sy - int(2*s), int(24*s), bl + int(4*s)),
                         border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (30, 12, 5),
                         (sx - int(12*s), sy - int(2*s), int(24*s), bl + int(4*s)),
                         max(1, int(s)), border_radius=max(3, int(5*s)))
        # Thick glowing lava crack network
        _lava_cracks = [
            [(sx-int(10*s), sy+int(8*s)), (sx-int(4*s), sy+int(16*s)), (sx+int(6*s), sy+int(12*s))],
            [(sx+int(8*s), sy+int(10*s)), (sx+int(2*s), sy+int(22*s)), (sx+int(9*s), sy+int(30*s))],
            [(sx-int(8*s), sy+int(26*s)), (sx+int(4*s), sy+int(34*s)), (sx-int(2*s), sy+int(42*s))],
            [(sx-int(5*s), sy+int(14*s)), (sx+int(3*s), sy+int(28*s)), (sx-int(4*s), sy+int(38*s))],
        ]
        for _lc in _lava_cracks:
            # Deep orange core
            pygame.draw.lines(surface, (255, 120, 0), False, _lc, max(2, int(3*s)))
            # Bright yellow-white center
            pygame.draw.lines(surface, (255, 240, 100), False, _lc, max(1, int(s)))
        # Lava drip fists — molten rock with glow
        for _lfx, _lfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (100, 40, 0), (_lfx, _lfy), max(6, int(9*s)))
            pygame.draw.circle(surface, (255, 100, 0), (_lfx, _lfy), max(4, int(7*s)), max(2, int(3*s)))
            pygame.draw.circle(surface, (255, 220, 60), (_lfx, _lfy), max(2, int(3*s)))
            # Lava drip below fist
            pygame.draw.ellipse(surface, (220, 80, 0),
                                (_lfx - int(3*s), _lfy + int(5*s), int(6*s), int(9*s)))
        # Volcanic smoke puffs drifting upward
        for _vsi in range(3):
            _vst = (t * 0.001 + _vsi * 0.9) % 2.0
            _vsy = hy - hd - int(_vst * 20 * s)
            _vsx = hx + int((_vsi - 1) * 8 * s)
            _vsa = max(0, int(70 - _vst * 50))
            if _vsa > 0:
                _vsc = (60 + _vsi*10, 40 + _vsi*8, 30)
                pygame.draw.circle(surface, _vsc, (_vsx, _vsy), max(2, int((4 - _vsi) * s)))
        # Horns on head
        for side in (-1, 1):
            hpx = hx + side * int(hd*0.7)
            pygame.draw.polygon(surface, (40, 10, 0),
                [(hpx-side*int(4*s), hy-hd+int(2*s)),
                 (hpx+side*int(4*s), hy-hd+int(2*s)),
                 (hpx+side*int(2*s), hy-hd-int(20*s))])
            # Lava glow inside horn
            pygame.draw.polygon(surface, (200, 60, 0),
                [(hpx-side*int(2*s), hy-hd+int(4*s)),
                 (hpx+side*int(2*s), hy-hd+int(4*s)),
                 (hpx+side*int(1*s), hy-hd-int(12*s))])
        # Rocky head — dark basalt with glow
        pygame.draw.circle(surface, (55, 28, 10), (hx, hy), int(hd*1.08))
        pygame.draw.circle(surface, (35, 15, 5), (hx, hy), int(hd*1.08), max(1, int(2*s)))
        pygame.draw.circle(surface, col, (hx, hy), hd)
        # Glowing molten eyes
        for _lex in (hx - int(hd*0.35), hx + int(hd*0.35)):
            pygame.draw.circle(surface, (255, 100, 0), (_lex, hy - int(hd*0.1)), max(3, int(5*s)))
            pygame.draw.circle(surface, (255, 240, 80), (_lex, hy - int(hd*0.1)), max(1, int(3*s)))

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
        t = pygame.time.get_ticks()
        # Sharp red power suit on torso
        pygame.draw.rect(surface, (160, 20, 20),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Gold power-up trim lines
        pygame.draw.rect(surface, (220, 180, 0),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # "CRIT" exclamation mark on chest
        _cf = _get_font(max(9, int(14*s)))
        _ct = _cf.render("!", True, (255, 220, 0))
        surface.blit(_ct, (sx - _ct.get_width()//2, sy + int(bl*0.25) - _ct.get_height()//2))
        # Gold star-shaped knuckledusters on hands
        for _chx, _chy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (220, 180, 0), (_chx, _chy), max(4, int(6*s)))
            pygame.draw.circle(surface, (255, 230, 60), (_chx, _chy), max(4, int(6*s)), max(1, int(s)))
        # Spinning gold star above head
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
        # Big sumo belly — wide ellipse
        pygame.draw.ellipse(surface, col,
                            (sx - int(15*s), sy - int(4*s), int(30*s), bl + int(8*s)))
        pygame.draw.ellipse(surface, (min(255,col[0]+30), min(255,col[1]+30), min(255,col[2]+30)),
                            (sx - int(15*s), sy - int(4*s), int(30*s), bl + int(8*s)),
                            max(1, int(s)))
        # Belly button
        pygame.draw.circle(surface, (max(0,col[0]-30), max(0,col[1]-30), max(0,col[2]-30)),
                           (sx, (sy+wy)//2 + int(4*s)), max(2, int(3*s)))
        # Mawashi belt (thick, decorative)
        bh_o = max(7, int(12*s))
        pygame.draw.rect(surface, (20, 40, 180),
                         (wx - int(hd*1.1), wy - bh_o//2, int(hd*2.2), bh_o),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (50, 80, 230),
                         (wx - int(hd*1.1), wy - bh_o//2, int(hd*2.2), bh_o),
                         max(1, int(s)), border_radius=max(1, int(2*s)))
        # Belt hanging tassels
        for _bti in range(3):
            _btx = wx - int(6*s) + _bti * int(6*s)
            pygame.draw.line(surface, (60, 100, 255),
                             (_btx, wy + bh_o//2), (_btx, wy + bh_o//2 + int(8*s)),
                             max(1, int(2*s)))
            pygame.draw.circle(surface, (100, 150, 255),
                               (_btx, wy + bh_o//2 + int(8*s)), max(2, int(3*s)))
        # Belt buckle jewel
        pygame.draw.rect(surface, (180, 220, 255),
                         (wx - int(5*s), wy - bh_o//2, int(10*s), bh_o),
                         border_radius=max(1, int(2*s)))
        pygame.draw.circle(surface, (80, 160, 255), (wx, wy), max(2, int(3*s)))
        # Filled lightning bolt on chest
        bolt = [(sx + int(facing * 5 * s), sy + int(5 * s)),
                (sx - int(facing * 5 * s), sy + int(17 * s)),
                (sx + int(facing * 3 * s), sy + int(17 * s)),
                (sx - int(facing * 5 * s), sy + int(30 * s)),
                (sx + int(facing * 3 * s), sy + int(19 * s)),
                (sx - int(facing * 3 * s), sy + int(19 * s))]
        pygame.draw.polygon(surface, (80, 160, 255), bolt)
        pygame.draw.polygon(surface, (150, 210, 255), bolt, max(1, int(s)))
        # Topknot hair (dome + knot bun)
        pygame.draw.circle(surface, (30, 20, 10), (hx, hy - hd + int(2*s)), int(hd*0.7))
        pygame.draw.ellipse(surface, (20, 10, 5),
                            (hx - int(hd*0.3), hy - int(hd*1.85), int(hd*0.6), int(hd*0.55)))
        # Thick war paint slashes on cheeks
        for _side in (-1, 1):
            pygame.draw.line(surface, (20, 40, 200),
                             (hx + _side*int(hd*0.42), hy - int(hd*0.28)),
                             (hx + _side*int(hd*0.72), hy + int(hd*0.38)), max(2, int(4*s)))
            # Second diagonal slash
            pygame.draw.line(surface, (20, 40, 200),
                             (hx + _side*int(hd*0.55), hy - int(hd*0.38)),
                             (hx + _side*int(hd*0.82), hy + int(hd*0.22)), max(1, int(2*s)))

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
        t = pygame.time.get_ticks()
        key_font = font_tiny
        # Dark terminal green-on-black bodysuit
        pygame.draw.rect(surface, (10, 20, 12),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (20, 60, 25),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Scrolling code text lines on torso
        _code_lines = ["> RUN", "0x1A3", "NULL", "{}[];"]
        _scroll = (t // 400) % len(_code_lines)
        _ascii_f = _get_font(max(7, int(8*s)))
        for _ali in range(3):
            _alt = _code_lines[(_scroll + _ali) % len(_code_lines)]
            _alsurf = _ascii_f.render(_alt, True, (0, 200, 50))
            surface.blit(_alsurf, (sx - _alsurf.get_width()//2,
                                   sy + int(bl*(0.2 + _ali*0.28)) - _alsurf.get_height()//2))
        # Terminal monitor helmet — dark rectangle with green screen
        pygame.draw.rect(surface, (15, 15, 15),
                         (hx - int(hd*1.1), hy - hd - int(2*s), int(hd*2.2), int(hd*1.85)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (30, 80, 35),
                         (hx - int(hd*1.1), hy - hd - int(2*s), int(hd*2.2), int(hd*1.85)),
                         max(1, int(2*s)), border_radius=max(2, int(3*s)))
        # Green CRT screen face
        pygame.draw.rect(surface, (5, 40, 10),
                         (hx - int(hd*.85), hy - hd + int(2*s), int(hd*1.7), int(hd*1.45)),
                         border_radius=max(1, int(2*s)))
        # Blinking cursor on face
        if (t // 500) % 2 == 0:
            pygame.draw.rect(surface, (0, 220, 50),
                             (hx - int(2*s), hy - int(hd*0.1), int(8*s), max(3, int(5*s))))
        # "@" symbol on screen face
        _at_f = _get_font(max(9, int(13*s)))
        _at_t = _at_f.render("@", True, (0, 200, 50))
        surface.blit(_at_t, (hx - _at_t.get_width()//2, hy - _at_t.get_height()//2 - int(2*s)))
        # Keyboard key decorations at body joints
        _key_positions = [
            (sx,  sy + int(6 * s),    '#'),
            (wx,  wy,                  '$'),
            (lhx, lhy,                '<'),
            (rhx, rhy,                '>'),
        ]
        for kx, ky, kch in _key_positions:
            kr = max(5, int(8 * s))
            pygame.draw.rect(surface, (200, 200, 200),
                             (kx - kr, ky - kr, kr * 2, kr * 2),
                             border_radius=max(1, int(2 * s)))
            pygame.draw.rect(surface, (80, 80, 80),
                             (kx - kr, ky - kr, kr * 2, kr * 2),
                             max(1, int(s)), border_radius=max(1, int(2 * s)))
            txt = key_font.render(kch, True, (20, 20, 20))
            surface.blit(txt, (kx - txt.get_width() // 2, ky - txt.get_height() // 2))

    elif char_name == "Snake":
        # Draw classic snake-game blocks along the body (like actual gameplay look)
        bsz = max(10, int(16 * s))
        # Snake body path: head → shoulder → waist → feet, then a curving tail
        _snake_pts = [
            (hx, hy),
            (hx, hy + hd + int(4*s)),
            (sx, sy + int(bl * 0.3)),
            (sx, sy + int(bl * 0.6)),
            (wx, wy),
            (wx + facing * int(10*s), wy + int(12*s)),
            (wx + facing * int(18*s), wy + int(20*s)),
            (wx + facing * int(22*s), wy + int(30*s)),
            (wx + facing * int(18*s), wy + int(40*s)),
        ]
        for _sbi, _sbpt in enumerate(_snake_pts):
            _g = min(230, 80 + _sbi * 18)
            pygame.draw.rect(surface, (10, _g, 20),
                             (_sbpt[0] - bsz//2, _sbpt[1] - bsz//2, bsz, bsz))
            pygame.draw.rect(surface, (40, min(255, _g + 60), 40),
                             (_sbpt[0] - bsz//2, _sbpt[1] - bsz//2, bsz, bsz), max(1, int(2*s)))
        # Forked tongue from head block
        _tx = hx + facing * (bsz // 2)
        pygame.draw.line(surface, (220, 50, 50),
                         (_tx, hy), (_tx + facing*int(8*s), hy), max(1, int(2*s)))
        pygame.draw.line(surface, (220, 50, 50),
                         (_tx + facing*int(8*s), hy),
                         (_tx + facing*int(12*s), hy - int(3*s)), max(1, int(s)))
        pygame.draw.line(surface, (220, 50, 50),
                         (_tx + facing*int(8*s), hy),
                         (_tx + facing*int(12*s), hy + int(3*s)), max(1, int(s)))
        # Eye dot on head block
        pygame.draw.circle(surface, (220, 220, 60),
                           (hx + facing*int(4*s), hy - int(3*s)), max(2, int(3*s)))

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
        t = pygame.time.get_ticks()
        # Joker playing-card suit: black and red diamond-pattern body
        pygame.draw.rect(surface, (10, 10, 10),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (40, 40, 40),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Red diamond playing card symbol on chest
        _jdpts = [(sx, sy + int(bl*0.05)), (sx + int(8*s), sy + int(bl*0.28)),
                  (sx, sy + int(bl*0.5)), (sx - int(8*s), sy + int(bl*0.28))]
        pygame.draw.polygon(surface, (200, 20, 20), _jdpts)
        # Purple glove on hand
        for _jhx, _jhy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (160, 20, 180), (_jhx, _jhy), max(4, int(6*s)))
        # Jester hat — two-pointed with animated wobbling bells
        for side, angle_off in [(-1, math.radians(150 + math.sin(t * 0.003) * 8)),
                                  (1,  math.radians(30  + math.sin(t * 0.003 + 1) * 8))]:
            px = hx + int(math.cos(angle_off) * hd * 1.6)
            py = hy - hd + int(math.sin(angle_off) * hd * 1.6)
            pygame.draw.line(surface, (220, 60, 255) if side == -1 else (255, 200, 0),
                             (hx, hy - hd), (px, py), max(2, int(3 * s)))
            pygame.draw.circle(surface, (255, 220, 0), (px, py), max(3, int(5 * s)))
            pygame.draw.circle(surface, (180, 140, 0), (px, py), max(3, int(5 * s)), max(1, int(s)))
        # Wide painted grin on face
        pygame.draw.arc(surface, (200, 20, 20),
                        (hx - int(hd*.65), hy - int(hd*.05), int(hd*1.3), int(hd*.75)),
                        math.radians(200), math.radians(340), max(2, int(3*s)))
        # Collar ruff (multi-petal)
        for _jri in range(6):
            _jra = math.radians(_jri * 60)
            _jrx = hx + int(math.cos(_jra) * hd * 0.85)
            _jry = hy + hd + int(math.sin(_jra) * hd * 0.5)
            _jrc = (220, 60, 255) if _jri % 2 == 0 else (255, 200, 0)
            pygame.draw.circle(surface, _jrc, (_jrx, _jry), max(3, int(5*s)))

    elif char_name == "Blitzer":
        t = pygame.time.get_ticks()
        # Yellow electro-suit body
        pygame.draw.rect(surface, (180, 130, 10),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (230, 190, 30),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Animated electricity arcing on arms
        if (t // 150) % 2 == 0:
            for _blex, _bley in [(lhx, lhy), (rhx, rhy)]:
                pygame.draw.line(surface, (255, 240, 80),
                                 (_blex, _bley),
                                 (_blex + facing*int(6*s), _bley - int(8*s)), max(1, int(2*s)))
                pygame.draw.circle(surface, (255, 240, 80), (_blex, _bley), max(3, int(5*s)))
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
        # Charge meter bar on torso side
        pygame.draw.rect(surface, (40, 30, 0),
                         (sx + int(8*s), sy + int(bl*0.25), int(4*s), int(bl*0.5)))
        _blcharge = 0.5 + 0.5 * math.sin(t * 0.004)
        pygame.draw.rect(surface, (255, 220, 0),
                         (sx + int(8*s), sy + int(bl*0.25) + int(bl*0.5*(1-_blcharge)),
                          int(4*s), int(bl*0.5*_blcharge)))

    elif char_name == "Vamp Lord":
        # Dramatic vampire cape
        cape_pts = [
            (hx,                     hy + hd),
            (hx - int(hd * 1.6),    wy + int(10 * s)),
            (hx - int(hd * 0.8),    wy - int(5 * s)),
            (hx + int(hd * 0.8),    wy - int(5 * s)),
            (hx + int(hd * 1.6),    wy + int(10 * s)),
        ]
        pygame.draw.polygon(surface, (60, 0, 20), cape_pts)
        pygame.draw.polygon(surface, (130, 0, 50), cape_pts, max(1, int(s)))
        # Aristocratic black suit vest on torso
        pygame.draw.rect(surface, (15, 10, 20),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # White ruffled shirt collar / cravat
        pygame.draw.polygon(surface, (240, 235, 250), [
            (sx - int(6*s), sy + int(2*s)),
            (sx + int(6*s), sy + int(2*s)),
            (sx + int(3*s), sy + int(bl*0.4)),
            (sx - int(3*s), sy + int(bl*0.4)),
        ])
        # Gold medallion chain
        pygame.draw.circle(surface, (200, 165, 10), (sx, sy + int(bl*0.55)), max(3, int(5*s)))
        pygame.draw.circle(surface, (240, 215, 60), (sx, sy + int(bl*0.55)), max(3, int(5*s)), max(1, int(s)))
        # Glowing crimson eyes
        for _vex in (hx - int(hd*0.35), hx + int(hd*0.35)):
            pygame.draw.circle(surface, (220, 0, 40), (_vex, hy - int(hd*0.15)), max(2, int(3*s)))
            pygame.draw.circle(surface, (255, 60, 60), (_vex, hy - int(hd*0.15)), max(1, int(2*s)))
        # Count's tall top-hat
        pygame.draw.rect(surface, (10, 5, 20),
                         (hx - int(hd*0.75), hy - hd - int(20*s), int(hd*1.5), int(20*s)))
        pygame.draw.rect(surface, (40, 20, 50),
                         (hx - int(hd*0.75), hy - hd - int(20*s), int(hd*1.5), int(20*s)),
                         max(1, int(s)))
        pygame.draw.rect(surface, (20, 10, 30),
                         (hx - hd - int(2*s), hy - hd - int(2*s), hd*2 + int(4*s), max(3, int(4*s))))
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
        t = pygame.time.get_ticks()
        blink = (t // 300) % 2 == 0
        # Explosive-vest / flak jacket on torso
        pygame.draw.rect(surface, (60, 50, 30),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 70, 40),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Strapped bombs across chest
        for _kbi in range(3):
            _kbx = sx - int(7*s) + _kbi * int(7*s)
            _kby = sy + int(bl*0.15)
            _kbc = (220, 60, 20) if blink and _kbi == 1 else (160, 40, 10)
            pygame.draw.rect(surface, _kbc, (_kbx - int(3*s), _kby, int(6*s), int(8*s)), border_radius=1)
            pygame.draw.rect(surface, (255, 200, 0), (_kbx - int(3*s), _kby, int(6*s), int(8*s)), 1, border_radius=1)
        # Strap across chest
        pygame.draw.line(surface, (100, 80, 40),
                         (sx - int(10*s), sy + int(bl*0.19)), (sx + int(10*s), sy + int(bl*0.19)),
                         max(2, int(3*s)))
        # Ticking bomb strapped to chest (main bomb)
        bx2, by2 = sx - int(6 * s), sy + int(bl*0.35)
        bsz2 = max(8, int(14 * s))
        pygame.draw.rect(surface, (220, 60, 20) if blink else (160, 40, 10),
                         (bx2, by2, bsz2, bsz2), border_radius=3)
        pygame.draw.rect(surface, (255, 200, 0), (bx2, by2, bsz2, bsz2), 1, border_radius=3)
        # Countdown digits on bomb
        _kdf = _get_font(max(6, int(8*s)))
        _kdt = _kdf.render("3!" if blink else "3", True, (255, 220, 0))
        surface.blit(_kdt, (bx2 + bsz2//2 - _kdt.get_width()//2, by2 + bsz2//2 - _kdt.get_height()//2))
        # Fuse wire going up
        pygame.draw.line(surface, (120, 100, 30),
                         (bx2 + bsz2//2, by2), (bx2 + bsz2//2 + int(4*s), by2 - int(10*s)),
                         max(1, int(s)))
        # Fuse spark
        if blink:
            pygame.draw.circle(surface, (255, 230, 0),
                               (bx2 + bsz2//2 + int(4*s), by2 - int(10*s)), max(2, int(3 * s)))
            pygame.draw.circle(surface, (255, 100, 0),
                               (bx2 + bsz2//2 + int(4*s), by2 - int(10*s)), max(1, int(2 * s)))
        # Headband / bandana
        pygame.draw.arc(surface, (180, 40, 10),
                        (hx - hd, hy - hd - int(6*s), hd*2, int(10*s)), 0, math.pi, max(2, int(4*s)))

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
        # Full-body mirrored silver suit
        pygame.draw.rect(surface, (200, 210, 225),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Reflection glints cascading down torso
        for _mri in range(4):
            _mry = sy + int(bl * (_mri * 0.25 + 0.05))
            _mrx = sx + int((_mri % 2 - 0.5) * 12 * s)
            pygame.draw.line(surface, (255, 255, 255),
                             (_mrx - int(4*s), _mry), (_mrx + int(6*s), _mry + int(3*s)),
                             max(1, int(s)))
        pygame.draw.rect(surface, (160, 175, 195),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Mirrored silver helmet
        pygame.draw.circle(surface, (200, 215, 230), (hx, hy), int(hd*1.1))
        pygame.draw.circle(surface, (160, 180, 200), (hx, hy), int(hd*1.1), max(1, int(2*s)))
        # Silver visor reflection band
        pygame.draw.ellipse(surface, (230, 240, 250),
                            (hx - int(hd*.8), hy - int(hd*.32), int(hd*1.6), int(hd*.6)))
        pygame.draw.ellipse(surface, (200, 215, 230),
                            (hx - int(hd*.8), hy - int(hd*.32), int(hd*1.6), int(hd*.6)),
                            max(1, int(s)))
        # Mirrored hands
        for _mhx, _mhy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (200, 215, 230), (_mhx, _mhy), max(4, int(6*s)))
            pygame.draw.circle(surface, (255, 255, 255), (_mhx, _mhy), max(2, int(3*s)))
        # Shiny round shield on blocking arm side
        shx = hx + int(facing * hd * 1.4)
        shy = hy
        sh_r = max(8, int(14 * s))
        pygame.draw.circle(surface, (210, 225, 240), (shx, shy), sh_r)
        pygame.draw.circle(surface, (255, 255, 255), (shx, shy), sh_r, max(1, int(2 * s)))
        # Multiple glint streaks on shield
        for _sgi, _sga in enumerate([(-0.8, -0.6), (0.2, 0.4), (-0.3, 0.5)]):
            pygame.draw.line(surface, (255, 255, 255),
                             (shx + int(_sga[0]*sh_r), shy + int(_sga[0]*sh_r*0.5)),
                             (shx + int(_sga[1]*sh_r), shy + int(_sga[1]*sh_r*0.5)),
                             max(1, int(s)))

    elif char_name == "Pyro":
        t = pygame.time.get_ticks()
        # Fire-resistant orange suit
        pygame.draw.rect(surface, (200, 90, 20),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (140, 60, 10),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Reflective safety stripes on suit
        for _psi2 in range(2):
            _psy2 = sy + int(bl * (0.3 + _psi2 * 0.45))
            pygame.draw.line(surface, (240, 200, 0),
                             (sx - int(9*s), _psy2), (sx + int(9*s), _psy2), max(2, int(3*s)))
        # Fuel tank on back
        _ptx = sx - facing*int(13*s)
        pygame.draw.rect(surface, (80, 60, 40),
                         (_ptx - int(4*s), sy + int(4*s), int(8*s), int(bl*0.7)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (100, 80, 50),
                         (_ptx - int(4*s), sy + int(4*s), int(8*s), int(bl*0.7)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Fuel hose from tank to arm
        pygame.draw.line(surface, (60, 50, 30),
                         (_ptx, sy + int(bl*0.3)), (rhx, rhy), max(2, int(3*s)))
        # Protective mask/visor on head
        pygame.draw.ellipse(surface, (80, 60, 40),
                            (hx - int(hd*.9), hy - int(hd*.5), int(hd*1.8), int(hd*1.0)))
        pygame.draw.ellipse(surface, (255, 160, 0),
                            (hx - int(hd*.7), hy - int(hd*.4), int(hd*1.4), int(hd*.8)))
        pygame.draw.ellipse(surface, (180, 100, 0),
                            (hx - int(hd*.7), hy - int(hd*.4), int(hd*1.4), int(hd*.8)),
                            max(1, int(s)))
        # Flamethrower nozzle on punch arm
        nozzle_x = rhx + int(facing * int(10 * s))
        nozzle_y = rhy
        pygame.draw.rect(surface, (80, 60, 40),
                         (nozzle_x - max(3, int(4 * s)), nozzle_y - max(3, int(4 * s)),
                          max(6, int(8 * s)) + int(facing * max(8, int(14 * s))),
                          max(6, int(8 * s))), border_radius=2)
        # Animated flame at nozzle
        if (t // 150) % 2 == 0:
            pygame.draw.circle(surface, (255, 80, 0),
                               (nozzle_x + int(facing * max(14, int(20 * s))), nozzle_y),
                               max(4, int(7 * s)))
            pygame.draw.circle(surface, (255, 200, 0),
                               (nozzle_x + int(facing * max(10, int(16 * s))), nozzle_y),
                               max(2, int(4 * s)))

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
        t = pygame.time.get_ticks()
        # Sci-fi bodysuit — dark teal panels
        pygame.draw.rect(surface, (10, 50, 60),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Panel seam lines on torso
        pygame.draw.line(surface, (0, 180, 200),
                         (sx - int(10*s), sy + int(bl*0.35)), (sx + int(10*s), sy + int(bl*0.35)),
                         max(1, int(s)))
        pygame.draw.line(surface, (0, 180, 200),
                         (sx - int(10*s), sy + int(bl*0.68)), (sx + int(10*s), sy + int(bl*0.68)),
                         max(1, int(s)))
        # Glowing cyan core disc on chest
        pygame.draw.circle(surface, (0, 200, 220), (sx, sy + int(bl*0.25)), max(4, int(6*s)))
        pygame.draw.circle(surface, (150, 255, 255), (sx, sy + int(bl*0.25)), max(2, int(3*s)))
        # Holographic visor over eyes
        pygame.draw.ellipse(surface, (0, 180, 200),
                            (hx - int(hd*.85), hy - int(hd*.28), int(hd*1.7), int(hd*.52)))
        pygame.draw.ellipse(surface, (100, 240, 255),
                            (hx - int(hd*.85), hy - int(hd*.28), int(hd*1.7), int(hd*.52)),
                            max(1, int(s)))
        # Visor inner scan-line shimmer
        pygame.draw.line(surface, (180, 255, 255),
                         (hx - int(hd*.55), hy - int(hd*.18)),
                         (hx + int(hd*.3), hy - int(hd*.18)), max(1, int(s)))
        # Energy-charged hands (glowing rings)
        for _hpos in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (0, 220, 240), _hpos, max(4, int(6*s)), max(1, int(2*s)))
            pygame.draw.circle(surface, (200, 255, 255), _hpos, max(2, int(3*s)))
        # Swirling portal ring around body
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
        t = pygame.time.get_ticks()
        _phase = (t // 1200) % 3
        _phase_frac = ((t % 1200) / 1200.0)  # 0→1 within current phase
        # Phase colours: Normal / Warrior / Speeder
        _body_tints = [(200, 200, 200), (200, 80, 20), (60, 160, 255)]
        _phase_names = ["N", "W", "S"]
        _bt = _body_tints[_phase]
        # Ghost-trail echo of previous phase (semi-transparent offset)
        _prev = (_phase - 1) % 3
        _pt = _body_tints[_prev]
        _ghost_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        _ghost_alpha = max(0, int(80 * (1 - _phase_frac)))
        pygame.draw.rect(_ghost_surf, (_pt[0], _pt[1], _pt[2], _ghost_alpha),
                         (sx - facing*int(8*s) - int(10*s), sy, int(20*s), bl),
                         border_radius=max(2, int(3*s)))
        surface.blit(_ghost_surf, (0, 0))
        # Main phase body
        pygame.draw.rect(surface, _bt,
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (min(255,_bt[0]+50), min(255,_bt[1]+50), min(255,_bt[2]+50)),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Phase-specific chest accessory
        if _phase == 0:
            # Normal: gear cog outline
            for _cgi3 in range(8):
                _cga = math.radians(_cgi3 * 45)
                _cgx = sx + int(math.cos(_cga) * int(8*s))
                _cgy = sy + int(bl*0.35) + int(math.sin(_cga) * int(8*s))
                pygame.draw.circle(surface, (160, 160, 160), (_cgx, _cgy), max(2, int(3*s)))
            pygame.draw.circle(surface, (180, 180, 180), (sx, sy + int(bl*0.35)), max(3, int(5*s)))
        elif _phase == 1:
            # Warrior: crossed sword lines on chest
            pygame.draw.line(surface, (240, 180, 60),
                             (sx - int(7*s), sy + int(bl*0.1)),
                             (sx + int(7*s), sy + int(bl*0.55)), max(2, int(3*s)))
            pygame.draw.line(surface, (240, 180, 60),
                             (sx + int(7*s), sy + int(bl*0.1)),
                             (sx - int(7*s), sy + int(bl*0.55)), max(2, int(3*s)))
        else:
            # Speeder: horizontal speed lines
            for _sli4 in range(4):
                _sly4 = sy + int(bl*(0.15 + _sli4*0.2))
                _slw = int((10 - _sli4*2)*s)
                pygame.draw.line(surface, (120, 220, 255),
                                 (sx - _slw, _sly4), (sx + _slw, _sly4), max(1, int(s)))
        # Phase symbol label on chest
        _pf = _get_font(max(10, int(16*s)))
        _ps = _pf.render(_phase_names[_phase], True, (20, 20, 20))
        surface.blit(_ps, (sx - _ps.get_width()//2, sy + int(bl*0.65) - _ps.get_height()//2))
        # Energy shimmer on hands
        for _sfhx, _sfhy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, _bt, (_sfhx, _sfhy), max(4, int(6*s)), max(1, int(2*s)))
        # Three spinning phase icons above head
        icons = [("N", (200, 200, 200)), ("W", (200, 80, 20)), ("S", (60, 160, 255))]
        for ii, (ch2, ic) in enumerate(icons):
            ia = math.radians(ii * 120 + t * 0.12)
            ix = hx + int(math.cos(ia) * hd * 1.5)
            iy = hy - hd - int(hd * 0.8) + int(math.sin(ia) * hd * 0.5)
            ir = max(4, int(6 * s))
            _is_active = (ii == _phase)
            pygame.draw.circle(surface, ic, (ix, iy), ir + (int(2*s) if _is_active else 0))
            if _is_active:
                pygame.draw.circle(surface, (255, 255, 255), (ix, iy), ir + int(2*s), max(1, int(s)))
            lbl2 = font_tiny.render(ch2, True, (10, 10, 10) if not _is_active else (255, 255, 255))
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
        # Black leather jacket on torso
        pygame.draw.rect(surface, (15, 15, 15),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Jacket collar V
        pygame.draw.polygon(surface, (25, 25, 25), [
            (sx - int(10*s), sy + int(2*s)),
            (sx + int(10*s), sy + int(2*s)),
            (sx, sy + int(bl*0.42)),
        ])
        pygame.draw.polygon(surface, (35, 35, 35), [
            (sx - int(5*s), sy + int(2*s)),
            (sx + int(5*s), sy + int(2*s)),
            (sx, sy + int(bl*0.34)),
        ])
        # Jacket outline + sheen
        pygame.draw.rect(surface, (40, 40, 40),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Silver zipper down center
        for _zi in range(5):
            _zy = sy + int(bl*(0.12 + _zi*0.16))
            pygame.draw.line(surface, (100, 100, 110),
                             (sx - int(s), _zy), (sx + int(s), _zy), max(1, int(s)))
        # Chest patch / band logo
        pygame.draw.rect(surface, (30, 30, 35),
                         (sx + facing*int(2*s), sy + int(bl*0.22), int(8*s), int(6*s)),
                         border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (55, 55, 65),
                         (sx + facing*int(2*s), sy + int(bl*0.22), int(8*s), int(6*s)),
                         max(1, int(s)), border_radius=max(1, int(s)))
        # Toothpick / cigarette in corner of mouth
        pygame.draw.line(surface, (220, 200, 150),
                         (hx + facing*int(hd*0.35), hy + int(hd*0.35)),
                         (hx + facing*int(hd*0.9), hy + int(hd*0.2)), max(1, int(s)))
        # Slicked-back hair
        pygame.draw.polygon(surface, (20, 18, 14), [
            (hx - int(hd*0.9), hy - hd + int(2*s)),
            (hx + int(hd*0.9), hy - hd + int(2*s)),
            (hx + int(hd*0.7), hy - hd - int(6*s)),
            (hx - int(hd*0.2), hy - hd - int(8*s)),
        ])
        # Cool mirror-lens sunglasses
        g_y = hy - int(hd*0.1)
        for gx_off in (-int(hd*.38), int(hd*.38)):
            pygame.draw.ellipse(surface, (10, 10, 10),
                                (hx + gx_off - int(hd*.32), g_y - int(hd*.22),
                                 int(hd*.64), int(hd*.44)))
            pygame.draw.ellipse(surface, (60, 60, 60),
                                (hx + gx_off - int(hd*.32), g_y - int(hd*.22),
                                 int(hd*.64), int(hd*.44)), max(1, int(s)))
            # Lens shine
            pygame.draw.line(surface, (80, 80, 90),
                             (hx + gx_off - int(hd*.2), g_y - int(hd*.15)),
                             (hx + gx_off, g_y - int(hd*.18)), max(1, int(s)))
        pygame.draw.line(surface, (60, 60, 60),
                         (hx - int(hd*.08), g_y), (hx + int(hd*.08), g_y), max(1, int(s)))
        # Speed-blur smoke trail
        for _dti in range(3):
            pygame.draw.ellipse(surface, (30, 30, 30),
                                (sx - facing*int((14+_dti*8)*s), sy + int(bl*(0.2+_dti*0.25)),
                                 int((10-_dti*2)*s), int((8-_dti*2)*s)))

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
        # Two-tone split bodysuit: left half orange, right half blue
        pygame.draw.polygon(surface, (230, 120, 30), [
            (sx, sy), (sx - int(11*s), sy), (sx - int(11*s), wy), (sx, wy)])
        pygame.draw.polygon(surface, (30, 120, 230), [
            (sx, sy), (sx + int(11*s), sy), (sx + int(11*s), wy), (sx, wy)])
        # Split seam down center
        pygame.draw.line(surface, (240, 240, 240), (sx, sy), (sx, wy), max(1, int(2*s)))
        # Two-tone belt at waist
        pygame.draw.rect(surface, (200, 200, 200),
                         (sx - int(11*s), wy - int(3*s), int(22*s), max(4, int(6*s))))
        # Double-sided swap arrows on chest
        for dx2, col2 in ((-int(hd*0.6), (255, 200, 80)), (int(hd*0.6), (80, 200, 255))):
            dir2 = 1 if dx2 > 0 else -1
            ax3, ay3 = sx + dx2, sy
            pts_arr = [(ax3, ay3 - int(4*s)), (ax3 + int(dir2*9*s), ay3 - int(4*s)),
                       (ax3 + int(dir2*9*s), ay3 - int(7*s)),
                       (ax3 + int(dir2*14*s), ay3),
                       (ax3 + int(dir2*9*s), ay3 + int(7*s)),
                       (ax3 + int(dir2*9*s), ay3 + int(4*s)),
                       (ax3, ay3 + int(4*s))]
            pygame.draw.polygon(surface, col2, pts_arr)
        # Split half-mask on face: left orange, right blue
        pygame.draw.polygon(surface, (230, 120, 30), [
            (hx - int(hd*.9), hy - int(hd*.55)),
            (hx, hy - int(hd*.55)),
            (hx, hy + int(hd*.55)),
            (hx - int(hd*.9), hy + int(hd*.55)),
        ])
        pygame.draw.polygon(surface, (30, 120, 230), [
            (hx + int(hd*.9), hy - int(hd*.55)),
            (hx, hy - int(hd*.55)),
            (hx, hy + int(hd*.55)),
            (hx + int(hd*.9), hy + int(hd*.55)),
        ])
        pygame.draw.line(surface, (240, 240, 240),
                         (hx, hy - int(hd*.6)), (hx, hy + int(hd*.6)), max(1, int(2*s)))
        # Two-tone gloves
        for _gx, _gy, _gc in [(lhx, lhy, (230, 120, 30)), (rhx, rhy, (30, 120, 230))]:
            pygame.draw.circle(surface, _gc, (_gx, _gy), max(4, int(7*s)))

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
        # Wrestling singlet body — dark blue
        pygame.draw.rect(surface, (25, 60, 160),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (40, 90, 200),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Singlet chest stripe
        pygame.draw.polygon(surface, (60, 120, 220), [
            (sx - int(6*s), sy + int(2*s)),
            (sx + int(6*s), sy + int(2*s)),
            (sx + int(9*s), wy - int(2*s)),
            (sx - int(9*s), wy - int(2*s)),
        ])
        # Championship belt around waist
        belt_y = wy + int(4*s)
        pygame.draw.rect(surface, (180, 140, 20),
                         (wx - int(hd*1.2), belt_y, int(hd*2.4), max(5, int(8*s))),
                         border_radius=2)
        pygame.draw.rect(surface, (220, 180, 40),
                         (wx - int(hd*0.4), belt_y - int(2*s), int(hd*0.8), max(6, int(10*s))),
                         border_radius=2)
        # Belt buckle gem
        pygame.draw.circle(surface, (60, 200, 255), (wx, belt_y + int(4*s)), max(2, int(3*s)))
        # Headband
        pygame.draw.arc(surface, (220, 180, 40),
                        (hx - hd, hy - hd - int(7*s), hd*2, int(12*s)), 0, math.pi, max(2, int(4*s)))
        # Big padded gloves
        for ghx, ghy in ((lhx, lhy), (rhx, rhy)):
            pygame.draw.circle(surface, (50, 100, 180), (ghx, ghy), max(6, int(10*s)))
            pygame.draw.circle(surface, (80, 130, 210), (ghx, ghy), max(6, int(10*s)), max(1, int(2*s)))
            pygame.draw.circle(surface, (100, 160, 230), (ghx, ghy), max(3, int(5*s)))
        # Knee pads
        for _kpx in (sx - int(5*s), sx + int(5*s)):
            _kpy = wy + int(bl*0.4)
            pygame.draw.rect(surface, (60, 100, 180),
                             (_kpx - int(4*s), _kpy, int(8*s), max(4, int(7*s))),
                             border_radius=max(1, int(2*s)))

    elif char_name == "Trickster":
        # Jester diamond-pattern suit on torso
        _cell = max(5, int(8*s))
        for _row in range(3):
            for _col2 in range(3):
                _tx = sx - int(10*s) + _col2 * _cell
                _ty = sy + _row * _cell
                _tc = (200, 0, 200) if (_row + _col2) % 2 == 0 else (255, 200, 0)
                pygame.draw.rect(surface, _tc, (_tx, _ty, _cell, min(_cell, bl - _row*_cell)))
        # Ruffled collar at neck
        for _ri in range(5):
            _rx = sx - int(8*s) + _ri * int(4*s)
            _rc = [(200, 0, 200), (255, 200, 0)][_ri % 2]
            pygame.draw.circle(surface, _rc, (_rx, sy + int(3*s)), max(3, int(4*s)))
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
        # Fool's grin — wide smile painted on face
        pygame.draw.arc(surface, (255, 60, 200),
                        (hx - int(hd*.6), hy - int(hd*.1), int(hd*1.2), int(hd*.7)),
                        math.radians(200), math.radians(340), max(1, int(2*s)))
        # Jester shoe curls at feet
        for _shx, _shy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.arc(surface, (180, 0, 180),
                            (_shx - int(5*s), _shy - int(4*s), int(14*s), int(8*s)),
                            0, math.pi, max(2, int(3*s)))
            pygame.draw.circle(surface, (255, 200, 0), (_shx + int(9*s), _shy - int(4*s)),
                               max(2, int(3*s)))

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
        # Iron plate body armor — dark steel torso
        pygame.draw.rect(surface, (100, 110, 130),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (70, 80, 100),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Chest plate horizontal ridge lines
        for _pl in range(3):
            _ply = sy + int(bl * (0.25 + _pl * 0.25))
            pygame.draw.line(surface, (140, 150, 170),
                             (sx - int(10*s), _ply), (sx + int(10*s), _ply), max(1, int(s)))
        # Center vertical seam
        pygame.draw.line(surface, (60, 70, 90),
                         (sx, sy + int(2*s)), (sx, wy - int(2*s)), max(1, int(s)))
        # Shoulder pauldrons (rounded plates over shoulders)
        for _spx in (sx - int(13*s), sx + int(13*s)):
            pygame.draw.ellipse(surface, (120, 130, 150),
                                (_spx - int(6*s), sy - int(2*s), int(12*s), int(8*s)))
            pygame.draw.ellipse(surface, (80, 90, 110),
                                (_spx - int(6*s), sy - int(2*s), int(12*s), int(8*s)),
                                max(1, int(s)))
        # Iron gauntlets on hands
        for _gx, _gy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.rect(surface, (110, 120, 140),
                             (_gx - int(5*s), _gy - int(4*s), int(10*s), int(9*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (70, 80, 100),
                             (_gx - int(5*s), _gy - int(4*s), int(10*s), int(9*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Iron bucket helmet with visor slit
        helm_y = hy - hd - int(4*s)
        hw2 = hd + int(3*s)
        hh2 = int(hd * 1.6)
        pygame.draw.rect(surface, (130, 140, 160), (hx - hw2, helm_y, hw2*2, hh2), border_radius=int(3*s))
        pygame.draw.rect(surface, (90, 100, 120), (hx - hw2, helm_y, hw2*2, hh2), max(1, int(2*s)), border_radius=int(3*s))
        # Visor slit
        vis_y = helm_y + int(hh2*0.45)
        pygame.draw.line(surface, (10, 10, 10),
                         (hx - hw2 + int(3*s), vis_y), (hx + hw2 - int(3*s), vis_y),
                         max(2, int(4*s)))
        # Rivets on helmet
        for rx2 in (hx - hw2 + int(4*s), hx + hw2 - int(4*s)):
            pygame.draw.circle(surface, (160, 170, 190), (rx2, helm_y + int(5*s)), max(2, int(3*s)))

    elif char_name == "Siphon":
        # Dark energy-drain bodysuit
        pygame.draw.rect(surface, (50, 0, 70),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (100, 20, 140),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Drain pulse rings around chest core
        _coresurf = pygame.Surface((hd*6, hd*6), pygame.SRCALPHA)
        for _dri in range(3):
            pygame.draw.circle(_coresurf, (200, 40, 200, 30 + _dri*15),
                               (hd*3, hd*3), hd*3 - _dri*int(4*s))
        surface.blit(_coresurf, (sx - hd*3, sy - hd))
        # Siphon tubes from each fist to chest (thick pulsing)
        for fhx3, fhy3 in ((lhx, lhy), (rhx, rhy)):
            pygame.draw.line(surface, (80, 0, 100), (fhx3, fhy3), (sx, sy + int(bl*0.2)), max(3, int(4*s)))
            pygame.draw.line(surface, (160, 20, 200), (fhx3, fhy3), (sx, sy + int(bl*0.2)), max(1, int(2*s)))
            # Energy orbs along tubes
            for _eoi in range(3):
                _eot = (_eoi + 1) / 4.0
                _eox2 = int(fhx3 + (sx - fhx3) * _eot)
                _eoy2 = int(fhy3 + (sy + int(bl*0.2) - fhy3) * _eot)
                pygame.draw.circle(surface, (220, 60, 255), (_eox2, _eoy2), max(2, int(3*s)))
            # Hand vortex
            pygame.draw.circle(surface, (160, 0, 200), (fhx3, fhy3), max(5, int(7*s)))
            pygame.draw.circle(surface, (220, 80, 255), (fhx3, fhy3), max(5, int(7*s)), max(1, int(2*s)))
            pygame.draw.circle(surface, (255, 160, 255), (fhx3, fhy3), max(2, int(3*s)))
        # Glowing core orb at chest
        pygame.draw.circle(surface, (160, 0, 200), (sx, sy + int(bl*0.2)), max(6, int(9*s)))
        pygame.draw.circle(surface, (220, 60, 255), (sx, sy + int(bl*0.2)), max(6, int(9*s)), max(1, int(2*s)))
        pygame.draw.circle(surface, (255, 160, 255), (sx, sy + int(bl*0.2)), max(3, int(4*s)))
        # Purple glowing eyes
        for _sex in (-1, 1):
            pygame.draw.circle(surface, (200, 40, 200),
                               (hx + _sex*int(hd*0.33), hy - int(hd*0.1)), max(3, int(4*s)))
            pygame.draw.circle(surface, (255, 140, 255),
                               (hx + _sex*int(hd*0.33), hy - int(hd*0.1)), max(1, int(2*s)))

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
        # Silver reflective suit on torso
        pygame.draw.rect(surface, (180, 190, 200),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Mirror-finish highlight panel
        pygame.draw.polygon(surface, (220, 235, 245), [
            (sx - int(9*s), sy + int(2*s)),
            (sx + int(5*s), sy + int(2*s)),
            (sx + int(3*s), sy + int(bl*0.9)),
            (sx - int(9*s), sy + int(bl*0.9)),
        ])
        pygame.draw.rect(surface, (210, 225, 235),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Reflected body ghost on opposite side
        _mrsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        _mroff = -facing * int(20*s)
        pygame.draw.circle(_mrsurf, (200, 225, 245, 50), (hx + _mroff, hy), hd)
        pygame.draw.line(_mrsurf, (200, 225, 245, 50),
                         (sx + _mroff, sy), (wx + _mroff, wy), max(2, int(3*s)))
        surface.blit(_mrsurf, (0, 0))
        # Large ornate mirror held in right hand
        mx2, my2 = int(rhx + int(facing * int(10*s))), int(rhy - int(5*s))
        mr = max(9, int(14*s))
        # Mirror frame (gold)
        pygame.draw.ellipse(surface, (180, 150, 40),
                            (mx2 - mr - int(3*s), my2 - int(mr*1.35) - int(3*s),
                             (mr + int(3*s))*2, int(mr*2.7) + int(6*s)))
        # Mirror surface
        pygame.draw.ellipse(surface, (200, 230, 255),
                            (mx2 - mr, my2 - int(mr*1.35), mr*2, int(mr*2.7)))
        pygame.draw.ellipse(surface, (230, 245, 255),
                            (mx2 - mr, my2 - int(mr*1.35), mr*2, int(mr*2.7)), max(1, int(s)))
        # Gleam lines on mirror surface
        pygame.draw.line(surface, (255, 255, 255),
                         (mx2 - int(5*s), my2 - int(mr*1.1)),
                         (mx2 + int(5*s), my2 - int(mr*0.3)), max(1, int(s)))
        pygame.draw.line(surface, (240, 250, 255),
                         (mx2 - int(3*s), my2 - int(mr*0.5)),
                         (mx2 - int(7*s), my2 + int(mr*0.4)), max(1, int(s)))
        # Frame ornament dots
        for _fdi in range(6):
            _fda = _fdi * math.pi / 3
            pygame.draw.circle(surface, (220, 190, 70),
                               (mx2 + int(math.cos(_fda)*(mr+int(2*s))),
                                my2 + int(math.sin(_fda)*int(mr*1.35+2*s))),
                               max(2, int(3*s)))
        # Handle
        pygame.draw.line(surface, (160, 130, 50),
                         (mx2, my2 + int(mr*1.35)),
                         (mx2 - facing*int(10*s), my2 + int(mr*1.35) + int(10*s)),
                         max(3, int(4*s)))
        pygame.draw.line(surface, (200, 170, 80),
                         (mx2, my2 + int(mr*1.35)),
                         (mx2 - facing*int(10*s), my2 + int(mr*1.35) + int(10*s)),
                         max(1, int(2*s)))
        # Mirror-shard head ornament
        for _mshi in range(3):
            _msha = math.pi * (0.3 + _mshi * 0.2)
            pygame.draw.polygon(surface, (210, 230, 245), [
                (hx + int(math.cos(_msha)*hd), hy - int(math.sin(_msha)*hd)),
                (hx + int(math.cos(_msha)*(hd+int(8*s))), hy - int(math.sin(_msha)*(hd+int(8*s)))),
                (hx + int(math.cos(_msha+0.3)*(hd+int(5*s))), hy - int(math.sin(_msha+0.3)*(hd+int(5*s)))),
            ])

    elif char_name == "Paradox":
        # Split-reality torso — left half normal, right half inverted/dark
        pygame.draw.polygon(surface, (30, 10, 80), [
            (sx, sy), (sx - int(10*s), sy), (sx - int(10*s), wy), (sx, wy)
        ])
        pygame.draw.polygon(surface, (220, 200, 255), [
            (sx, sy), (sx + int(10*s), sy), (sx + int(10*s), wy), (sx, wy)
        ])
        # Dividing rift line down center
        pygame.draw.line(surface, (160, 100, 255),
                         (sx, sy - int(2*s)), (sx, wy + int(4*s)), max(2, int(3*s)))
        pygame.draw.line(surface, (255, 200, 255),
                         (sx, sy - int(2*s)), (sx, wy + int(4*s)), max(1, int(s)))
        # Paradox symbols each side (∞ halves)
        tt6 = pygame.time.get_ticks()
        inf_y = hy - hd - int(8*s)
        inf_r = max(6, int(10*s))
        col_l = (int(100 + 100*math.sin(tt6*0.004)), 60, 200)
        col_r = (200, 80, int(150 + 100*math.cos(tt6*0.004)))
        pygame.draw.circle(surface, col_l, (hx - inf_r, inf_y), inf_r, max(2, int(3*s)))
        pygame.draw.circle(surface, col_r, (hx + inf_r, inf_y), inf_r, max(2, int(3*s)))
        pygame.draw.line(surface, (200, 140, 255),
                         (hx - inf_r, inf_y), (hx + inf_r, inf_y), max(2, int(2*s)))
        # Clock and anti-clock arrows on the ∞ loops
        for _par, _pcol in [(-inf_r, col_l), (inf_r, col_r)]:
            _pat = tt6 * 0.004
            pygame.draw.circle(surface, _pcol,
                               (hx + _par + int(math.cos(_pat)*inf_r*0.7),
                                inf_y + int(math.sin(_pat)*inf_r*0.7)),
                               max(2, int(3*s)))
        # Split face — one side dark, one light
        pygame.draw.ellipse(surface, (15, 5, 40),
                            (hx - hd, hy - hd, hd, hd*2))
        pygame.draw.ellipse(surface, (240, 230, 255),
                            (hx, hy - hd, hd, hd*2))
        # Split eyes
        pygame.draw.circle(surface, (220, 180, 255), (hx - int(hd*0.35), hy - int(hd*0.1)), max(3, int(4*s)))
        pygame.draw.circle(surface, (20, 5, 60), (hx + int(hd*0.35), hy - int(hd*0.1)), max(3, int(4*s)))
        pygame.draw.circle(surface, (255, 255, 255), (hx - int(hd*0.35), hy - int(hd*0.1)), max(1, int(2*s)))
        pygame.draw.circle(surface, (160, 80, 255), (hx + int(hd*0.35), hy - int(hd*0.1)), max(1, int(2*s)))

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

    elif char_name == "Impossible":
        t = pygame.time.get_ticks()
        # Paper-thin cracked armour — reflects 1 HP / 1 dmg theme
        # Hollow body rect (just an outline, barely there)
        pygame.draw.rect(surface, (0, 220, 240),
                         (sx - int(9*s), sy, int(18*s), bl),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Crack lines on torso
        mid_x = sx
        mid_y = (sy + wy) // 2
        for _ci, (_coff, _clen, _cang) in enumerate([
                (0,  int(14*s), math.radians(70)),
                (int(4*s), int(8*s),  math.radians(110)),
                (-int(3*s), int(10*s), math.radians(80)),
        ]):
            _cx0 = mid_x + _coff
            _cy0 = mid_y + _ci * int(5*s) - int(6*s)
            pygame.draw.line(surface, (0, 200, 220),
                             (_cx0, _cy0),
                             (_cx0 + int(math.cos(_cang)*_clen),
                              _cy0 + int(math.sin(_cang)*_clen)),
                             max(1, int(s)))
        # Bandage cross on chest
        bx, by = sx, sy + int(bl * 0.3)
        bw, bh = int(7*s), int(3*s)
        pygame.draw.rect(surface, (220, 220, 220), (bx - bw//2, by - bh//2, bw, bh))
        pygame.draw.rect(surface, (220, 220, 220), (bx - bh//2, by - bw//2, bh, bw))
        # Cracked glass visor — thin cyan ring + lightning bolt crack
        pygame.draw.circle(surface, (0, 220, 240), (hx, hy), hd + max(1, int(2*s)), max(1, int(s)))
        crack_pts = [
            (hx - int(3*s), hy - int(6*s)),
            (hx + int(2*s), hy - int(1*s)),
            (hx - int(1*s), hy + int(4*s)),
        ]
        pygame.draw.lines(surface, (180, 255, 255), False, crack_pts, max(1, int(s)))
        # "×1" badge floating above head — flickers
        if (t // 400) % 2 == 0:
            badge_surf = pygame.Surface((int(22*s), int(12*s)), pygame.SRCALPHA)
            pygame.draw.rect(badge_surf, (200, 0, 0, 200),
                             (0, 0, int(22*s), int(12*s)), border_radius=max(2, int(2*s)))
            badge_surf.blit(
                pygame.font.SysFont(None, max(8, int(11*s))).render("×1", True, (255,255,255)),
                (max(1, int(2*s)), max(0, int(1*s)))
            )
            surface.blit(badge_surf, (hx - int(11*s), hy - hd - int(16*s)))

    elif char_name == "The Impossible Victor":
        t = pygame.time.get_ticks()
        # Glittering golden suit
        pygame.draw.rect(surface, (180, 145, 10),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (230, 195, 50),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Sheen highlight on suit
        pygame.draw.polygon(surface, (255, 230, 100), [
            (sx - int(8*s), sy + int(2*s)), (sx - int(2*s), sy + int(2*s)),
            (sx - int(4*s), wy - int(2*s)), (sx - int(9*s), wy - int(2*s)),
        ])
        # "1st" champion sash
        pygame.draw.polygon(surface, (0, 200, 140), [
            (sx - int(10*s), sy), (sx - int(3*s), sy),
            (sx + int(9*s), wy), (sx + int(2*s), wy),
        ])
        pygame.draw.polygon(surface, (0, 255, 180), [
            (sx - int(10*s), sy), (sx - int(3*s), sy),
            (sx + int(9*s), wy), (sx + int(2*s), wy),
        ], max(1, int(s)))
        # Multiple medals — gold, silver, bronze hanging from chest
        for _mi3, (_mx3, _mc3, _mrc3) in enumerate([
                (sx - int(6*s), (210,180,20), (255,230,80)),
                (sx,            (180,180,185),(230,230,235)),
                (sx + int(6*s), (160,90,30),  (210,140,60))]):
            _my3 = sy + int(bl*0.5) + _mi3*int(0*s)
            pygame.draw.line(surface, (180, 150, 20),
                             (_mx3, sy + int(bl*0.25)), (_mx3, _my3 - int(5*s)), max(1, int(s)))
            pygame.draw.circle(surface, _mc3, (_mx3, _my3), max(4, int(6*s)))
            pygame.draw.circle(surface, _mrc3, (_mx3, _my3), max(4, int(6*s)), max(1, int(s)))
            pygame.draw.circle(surface, (255, 255, 220), (_mx3, _my3), max(1, int(2*s)))
        # Sparkle star particles twinkling around body
        for _spi in range(6):
            _spa = math.radians(_spi * 60 + t * 0.08)
            _spr = max(12, int((18 + (_spi%3)*6)*s))
            _spx = sx + int(math.cos(_spa) * _spr)
            _spy = (sy+wy)//2 + int(math.sin(_spa) * _spr//2)
            if (t//300 + _spi) % 2 == 0:
                pygame.draw.circle(surface, (255, 240, 100), (_spx, _spy), max(2, int(3*s)))
        # Trophy cup crown (actual cup shapes, not just dots)
        trophy_y = hy - hd - int(4*s)
        pygame.draw.rect(surface, (200, 165, 15),
                         (hx - int(hd*0.95), trophy_y, int(hd*1.9), max(3, int(5*s))))
        for ti2, tx2 in enumerate((-int(hd*0.75), 0, int(hd*0.75))):
            _th = int(8*s) if ti2 == 1 else int(5*s)
            _tw = int(7*s) if ti2 == 1 else int(5*s)
            _tcx = hx + tx2
            _tcy = trophy_y - _th
            # Cup body
            pygame.draw.polygon(surface, (0, 220, 160), [
                (_tcx - _tw, _tcy), (_tcx + _tw, _tcy),
                (_tcx + int(_tw*0.6), _tcy - _th), (_tcx - int(_tw*0.6), _tcy - _th),
            ])
            # Cup stem + base
            pygame.draw.rect(surface, (0, 180, 130),
                             (_tcx - int(2*s), _tcy - _th, int(4*s), int(4*s)))
            pygame.draw.rect(surface, (0, 200, 145),
                             (_tcx - _tw + int(s), _tcy - _th - int(2*s), _tw*2 - int(2*s), max(2, int(3*s))))
            pygame.draw.polygon(surface, (0, 255, 180), [
                (_tcx - _tw, _tcy), (_tcx + _tw, _tcy),
                (_tcx + int(_tw*0.6), _tcy - _th), (_tcx - int(_tw*0.6), _tcy - _th),
            ], max(1, int(s)))

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
        # Alternates between full chicken and banana forms every 500ms
        t_cb = pygame.time.get_ticks()
        is_chicken = (t_cb // 500) % 2 == 0
        if is_chicken:
            # Chicken: white feathery body suit
            pygame.draw.rect(surface, (245, 245, 240),
                             (sx - int(10*s), sy, int(20*s), bl), border_radius=max(3, int(5*s)))
            pygame.draw.rect(surface, (255, 255, 255),
                             (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(3, int(5*s)))
            # Feather texture rows
            for _fri in range(4):
                for _fci in range(3):
                    _fcx = sx - int(7*s) + _fci * int(6*s) + (_fri%2)*int(3*s)
                    _fcy = sy + int(bl*(0.1 + _fri*0.22))
                    pygame.draw.ellipse(surface, (230, 230, 225),
                                        (_fcx - int(4*s), _fcy - int(3*s), int(8*s), int(6*s)))
            # Wing spans on arms
            for _wsx, _wsy, _wex, _wey in [(sx, sy+int(bl*0.15), lhx, lhy),
                                             (sx, sy+int(bl*0.15), rhx, rhy)]:
                for _wfi in range(4):
                    _wft = _wfi / 3.0
                    _wfx = int(_wsx + (_wex-_wsx)*_wft)
                    _wfy = int(_wsy + (_wey-_wsy)*_wft)
                    pygame.draw.ellipse(surface, (245, 245, 235),
                                        (_wfx - int(5*s), _wfy - int(3*s), int(10*s), int(6*s)))
            # Large red comb
            comb_pts = [(hx - int(hd*0.4), hy - hd),
                        (hx - int(hd*0.2), hy - hd - int(10*s)),
                        (hx, hy - hd - int(4*s)),
                        (hx + int(hd*0.2), hy - hd - int(12*s)),
                        (hx + int(hd*0.4), hy - hd - int(5*s)),
                        (hx + int(hd*0.6), hy - hd)]
            pygame.draw.polygon(surface, (220, 20, 20), comb_pts)
            pygame.draw.polygon(surface, (255, 60, 60), comb_pts, max(1, int(s)))
            # Wattle (red chin blob)
            pygame.draw.circle(surface, (200, 10, 10),
                               (hx + facing*int(hd*0.4), hy + int(hd*0.4)), max(3, int(5*s)))
            # Large orange beak
            beak_x = hx + int(facing * hd)
            pygame.draw.polygon(surface, (255, 140, 0), [
                (beak_x, hy - int(hd*0.15)),
                (beak_x + int(facing * int(12*s)), hy + int(hd*0.05)),
                (beak_x, hy + int(hd*0.15))])
            pygame.draw.line(surface, (200, 100, 0),
                             (beak_x, hy), (beak_x + facing*int(10*s), hy), max(1, int(s)))
            # Chicken eye
            pygame.draw.circle(surface, (255, 200, 0),
                               (hx + facing*int(hd*0.4), hy - int(hd*0.2)), max(3, int(4*s)))
            pygame.draw.circle(surface, (20, 20, 20),
                               (hx + facing*int(hd*0.4), hy - int(hd*0.2)), max(1, int(2*s)))
            # Fluffy tail feathers
            for _tfi in range(5):
                _tfa = math.pi * (0.6 + _tfi * 0.12) * (-facing)
                pygame.draw.line(surface, (240, 240, 230),
                                 (wx - facing*int(6*s), wy),
                                 (wx - facing*int(6*s) + int(math.cos(_tfa)*12*s),
                                  wy + int(math.sin(abs(_tfa))*12*s)), max(2, int(3*s)))
        else:
            # Banana: yellow curved body + green tips
            pygame.draw.rect(surface, (240, 200, 20),
                             (sx - int(8*s), sy, int(16*s), bl), border_radius=max(3, int(6*s)))
            # Curved banana arc on body
            ban_pts = []
            for bi in range(9):
                t2 = bi / 8.0
                bx2 = sx + int(math.sin(t2 * math.pi) * int(hd*1.4) * facing)
                by2 = sy + int(bl * t2)
                ban_pts.append((bx2, by2))
            if len(ban_pts) >= 2:
                pygame.draw.lines(surface, (255, 230, 0), False, ban_pts, max(5, int(7*s)))
                pygame.draw.lines(surface, (255, 255, 100), False, ban_pts, max(2, int(3*s)))
            # Green banana tips
            pygame.draw.circle(surface, (80, 180, 40), ban_pts[0], max(5, int(7*s)))
            pygame.draw.circle(surface, (80, 180, 40), ban_pts[-1], max(4, int(6*s)))
            # Brown spots on banana
            for _bsi2, (_bspx, _bspy) in enumerate([(sx - int(3*s), sy + int(bl*0.3)),
                                                      (sx + int(4*s), sy + int(bl*0.55))]):
                pygame.draw.ellipse(surface, (160, 120, 10),
                                    (_bspx - int(3*s), _bspy - int(2*s), int(6*s), int(4*s)))
            # Banana label sticker
            pygame.draw.rect(surface, (200, 220, 80),
                             (sx - int(5*s), sy + int(bl*0.42), int(10*s), int(6*s)),
                             border_radius=max(1, int(s)))
            _bf = _get_font(max(5, int(7*s)))
            _bt = _bf.render("🍌", True, (160, 120, 0))
            surface.blit(_bt, (sx - _bt.get_width()//2, sy + int(bl*0.43)))

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
        # White coat body
        pygame.draw.rect(surface, (220, 245, 220),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (160, 210, 160),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Red cross emblem on chest
        _hcx, _hcy = sx, sy + int(bl * 0.38)
        pygame.draw.rect(surface, (220, 40, 40),
                         (_hcx - int(s), _hcy - int(8*s), int(2*s+1), int(16*s)))
        pygame.draw.rect(surface, (220, 40, 40),
                         (_hcx - int(6*s), _hcy - int(s), int(12*s), int(2*s+1)))
        # White coat lapels
        pygame.draw.polygon(surface, (255, 255, 255),
                            [(sx - int(5*s), sy), (sx, sy + int(bl*0.3)), (sx - int(11*s), sy)])
        pygame.draw.polygon(surface, (255, 255, 255),
                            [(sx + int(5*s), sy), (sx, sy + int(bl*0.3)), (sx + int(11*s), sy)])
        # Glowing halo ring
        pygame.draw.circle(surface, (120, 240, 140), (hx, hy - hd), hd + int(5*s), max(2, int(2*s)))

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

    elif char_name == "God":
        # Divine radiance aura — warm golden glow around entire body
        _godsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(_godsurf, (255, 230, 100, 35),
                            (sx - int(hd*3), sy - int(hd*2), int(hd*6), int(hd*6)))
        surface.blit(_godsurf, (0, 0))
        # White/gold divine robes on torso
        pygame.draw.rect(surface, (250, 248, 235),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(3, int(5*s)))
        # Gold trim on robe
        pygame.draw.rect(surface, (220, 185, 40),
                         (sx - int(10*s), sy, int(20*s), bl), max(2, int(3*s)), border_radius=max(3, int(5*s)))
        # Gold cross emblem on chest
        pygame.draw.line(surface, (220, 185, 40),
                         (sx, sy + int(bl*0.12)), (sx, sy + int(bl*0.65)), max(3, int(4*s)))
        pygame.draw.line(surface, (220, 185, 40),
                         (sx - int(7*s), sy + int(bl*0.28)), (sx + int(7*s), sy + int(bl*0.28)),
                         max(3, int(4*s)))
        # Glowing golden halo above head
        _halo_y = hy - hd - int(6*s)
        pygame.draw.ellipse(surface, (220, 185, 40),
                            (hx - int(hd*1.3), _halo_y - int(4*s), int(hd*2.6), int(8*s)),
                            max(2, int(3*s)))
        pygame.draw.ellipse(surface, (255, 240, 120),
                            (hx - int(hd*1.3), _halo_y - int(4*s), int(hd*2.6), int(8*s)),
                            max(1, int(s)))
        # Sun ray spikes from halo
        for _sri in range(8):
            _sra = _sri * math.pi / 4
            _srx = hx + int(math.cos(_sra) * hd * 1.4)
            _sry = _halo_y + int(math.sin(_sra) * int(4*s))
            pygame.draw.line(surface, (255, 220, 80),
                             (_srx, _sry),
                             (_srx + int(math.cos(_sra)*8*s), _sry + int(math.sin(_sra)*4*s)),
                             max(1, int(2*s)))
        # Divine white wings behind body
        _gwsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for _gwside in [-1, 1]:
            _gwpts = [
                (sx, sy + int(bl*0.2)),
                (sx + _gwside*int(32*s), sy - int(10*s)),
                (sx + _gwside*int(38*s), sy + int(bl*0.35)),
                (sx + _gwside*int(28*s), sy + int(bl*0.7)),
                (sx, sy + int(bl*0.5)),
            ]
            pygame.draw.polygon(_gwsurf, (255, 255, 240, 70), _gwpts)
            pygame.draw.polygon(_gwsurf, (255, 240, 180, 120), _gwpts, max(1, int(2*s)))
        surface.blit(_gwsurf, (0, 0))
        # Glowing radiant eyes
        for _gex in (-1, 1):
            pygame.draw.circle(surface, (255, 240, 120),
                               (hx + _gex*int(hd*0.33), hy - int(hd*0.1)), max(3, int(5*s)))
            pygame.draw.circle(surface, (255, 255, 200),
                               (hx + _gex*int(hd*0.33), hy - int(hd*0.1)), max(2, int(3*s)))

    elif char_name == "Nightfall":
        # Deep midnight-blue cloak
        pygame.draw.rect(surface, (10, 5, 40),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(8*s)),
                         border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (30, 15, 80),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(8*s)),
                         max(1, int(s)), border_radius=max(2, int(4*s)))
        # Star pattern on cloak
        for _nsi in range(8):
            _nsx = sx - int(9*s) + (_nsi % 3) * int(7*s) + int((_nsi//3)*3*s)
            _nsy = sy + int(bl*(0.1 + (_nsi//3)*0.38 + (_nsi%3)*0.18))
            pygame.draw.circle(surface, (200, 210, 255), (_nsx, _nsy), max(1, int(2*s)))
            # Star spike
            for _nsa in range(4):
                _nsang = _nsa * math.pi / 2
                pygame.draw.line(surface, (180, 195, 255),
                                 (_nsx, _nsy),
                                 (_nsx + int(math.cos(_nsang)*3*s), _nsy + int(math.sin(_nsang)*3*s)),
                                 max(1, int(s)))
        # Crescent moon emblem on chest
        _nmx, _nmy = sx, sy + int(bl*0.4)
        pygame.draw.circle(surface, (220, 210, 120), (_nmx, _nmy), max(7, int(10*s)))
        pygame.draw.circle(surface, (10, 5, 40), (_nmx + int(4*s), _nmy - int(2*s)), max(6, int(9*s)))
        # Dark hood
        pygame.draw.ellipse(surface, (8, 4, 35),
                            (hx - int(hd*1.2), hy - hd - int(5*s), int(hd*2.4), int(hd*1.4)))
        pygame.draw.ellipse(surface, (25, 12, 70),
                            (hx - int(hd*1.2), hy - hd - int(5*s), int(hd*2.4), int(hd*1.4)),
                            max(1, int(2*s)))
        # Face shadow with glowing moon-silver eyes
        pygame.draw.ellipse(surface, (5, 2, 20),
                            (hx - int(hd*0.8), hy - int(hd*0.7), int(hd*1.6), int(hd*1.2)))
        for _nex in (-1, 1):
            pygame.draw.circle(surface, (180, 200, 255),
                               (hx + _nex*int(hd*0.33), hy - int(hd*0.1)), max(3, int(4*s)))
            pygame.draw.circle(surface, (220, 230, 255),
                               (hx + _nex*int(hd*0.33), hy - int(hd*0.1)), max(1, int(2*s)))
        # Floating dark orbs around body
        _nfsurf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for _noi in range(4):
            _noa = math.pi * (0.25 + _noi * 0.5)
            _nox = sx + int(math.cos(_noa) * 18 * s)
            _noy = sy + int(bl*0.4) + int(math.sin(_noa) * 14 * s)
            pygame.draw.circle(_nfsurf, (20, 10, 60, 100), (_nox, _noy), max(4, int(6*s)))
        surface.blit(_nfsurf, (0, 0))

    elif char_name == "Lucky":
        # Green shamrock/clover suit on torso
        pygame.draw.rect(surface, (30, 130, 50),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 170, 80),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # 4-leaf clover on chest
        _lcx, _lcy = sx, sy + int(bl*0.38)
        for _lcdir in [(-1,-1),(1,-1),(-1,1),(1,1)]:
            pygame.draw.circle(surface, (50, 180, 70),
                               (_lcx + _lcdir[0]*int(5*s), _lcy + _lcdir[1]*int(5*s)),
                               max(4, int(6*s)))
            pygame.draw.circle(surface, (80, 220, 100),
                               (_lcx + _lcdir[0]*int(5*s), _lcy + _lcdir[1]*int(5*s)),
                               max(4, int(6*s)), max(1, int(s)))
        pygame.draw.circle(surface, (30, 130, 50), (_lcx, _lcy), max(3, int(5*s)))
        # Lucky horseshoe on head
        pygame.draw.arc(surface, (200, 165, 40),
                        (hx - int(hd*0.9), hy - hd - int(10*s), int(hd*1.8), int(hd*1.4)),
                        math.pi * 1.1, math.pi * 2.9 - 0.1, max(3, int(5*s)))
        # Horseshoe nail dots
        for _hni, _hna in enumerate([math.pi*1.15, math.pi*1.5, math.pi*1.85]):
            pygame.draw.circle(surface, (220, 190, 60),
                               (hx + int(math.cos(_hna)*int(hd*0.9)),
                                hy - hd - int(4*s) + int(math.sin(_hna)*int(hd*0.7))),
                               max(2, int(3*s)))
        # Leprechaun top hat
        pygame.draw.rect(surface, (25, 110, 45),
                         (hx - int(hd*0.7), hy - hd - int(14*s), int(hd*1.4), int(14*s)))
        pygame.draw.rect(surface, (50, 160, 70),
                         (hx - int(hd*0.7), hy - hd - int(14*s), int(hd*1.4), int(14*s)),
                         max(1, int(s)))
        pygame.draw.ellipse(surface, (25, 110, 45),
                            (hx - int(hd*1.0), hy - hd - int(4*s), int(hd*2.0), int(8*s)))
        # Gold buckle on hat
        pygame.draw.rect(surface, (200, 165, 40),
                         (hx - int(5*s), hy - hd - int(6*s), int(10*s), int(6*s)),
                         border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (240, 210, 60),
                         (hx - int(5*s), hy - hd - int(6*s), int(10*s), int(6*s)),
                         max(1, int(s)), border_radius=max(1, int(s)))
        # Gold coin sparkles around body
        for _gci2, _gca in enumerate([0.5, 1.2, 1.9, 2.6, 3.3, 4.0]):
            _gcx2 = sx + int(math.cos(_gca) * 20 * s)
            _gcy2 = sy + int(bl*0.5) + int(math.sin(_gca) * 14 * s)
            pygame.draw.circle(surface, (220, 185, 40), (_gcx2, _gcy2), max(2, int(4*s)))
            pygame.draw.circle(surface, (255, 230, 80), (_gcx2, _gcy2), max(1, int(2*s)))

    elif char_name == "Great Totem Spirit":
        # Layered totem body paint on torso
        _totem_cols = [(200, 60, 20), (220, 160, 20), (30, 120, 180)]
        for _tbi in range(3):
            _tby = sy + int(bl * (_tbi * 0.33))
            _tbh = int(bl * 0.32)
            pygame.draw.rect(surface, _totem_cols[_tbi],
                             (sx - int(10*s), _tby, int(20*s), _tbh))
            # Totem face/pattern on each band
            _tfcx, _tfcy = sx, _tby + _tbh//2
            for _tfd in [-1, 1]:
                pygame.draw.line(surface, (20, 10, 5),
                                 (_tfcx + _tfd*int(3*s), _tfcy - int(4*s)),
                                 (_tfcx + _tfd*int(6*s), _tfcy + int(4*s)), max(1, int(s)))
            pygame.draw.line(surface, (20, 10, 5),
                             (_tfcx - int(4*s), _tfcy),
                             (_tfcx + int(4*s), _tfcy), max(1, int(s)))
        # Totem mask on head
        pygame.draw.rect(surface, (200, 60, 20),
                         (hx - int(hd*1.1), hy - hd, int(hd*2.2), int(hd*1.8)),
                         border_radius=max(1, int(3*s)))
        pygame.draw.rect(surface, (240, 100, 40),
                         (hx - int(hd*1.1), hy - hd, int(hd*2.2), int(hd*1.8)),
                         max(1, int(2*s)), border_radius=max(1, int(3*s)))
        # Mask eye diamonds
        for _meox in (-1, 1):
            pygame.draw.polygon(surface, (220, 160, 20), [
                (hx + _meox*int(hd*0.45), hy - int(hd*0.4)),
                (hx + _meox*int(hd*0.2), hy - int(hd*0.1)),
                (hx + _meox*int(hd*0.45), hy + int(hd*0.15)),
                (hx + _meox*int(hd*0.7), hy - int(hd*0.1)),
            ])
        # Fanged mouth bar
        pygame.draw.rect(surface, (220, 160, 20),
                         (hx - int(hd*0.6), hy + int(hd*0.25), int(hd*1.2), int(hd*0.35)))
        for _fgi in range(4):
            _fgx = hx - int(hd*0.5) + _fgi * int(hd*0.32)
            pygame.draw.polygon(surface, (240, 235, 220), [
                (_fgx, hy + int(hd*0.25)),
                (_fgx + int(hd*0.12), hy + int(hd*0.25)),
                (_fgx + int(hd*0.06), hy + int(hd*0.55)),
            ])
        # Tall feather headdress
        for _hfi in range(5):
            _hfa = math.pi * (0.15 + _hfi * 0.175)
            _hfl = int((22 + (_hfi%3)*6)*s)
            _hfcols = [(200, 30, 20), (220, 160, 20), (30, 120, 180), (20, 140, 60), (200, 30, 20)]
            pygame.draw.line(surface, _hfcols[_hfi],
                             (hx + int(math.cos(_hfa)*hd), hy - int(math.sin(_hfa)*hd)),
                             (hx + int(math.cos(_hfa)*(_hfl+hd)),
                              hy - int(math.sin(_hfa)*(_hfl+hd))), max(3, int(4*s)))
            pygame.draw.circle(surface, (240, 240, 200),
                               (hx + int(math.cos(_hfa)*(_hfl+hd)),
                                hy - int(math.sin(_hfa)*(_hfl+hd))), max(2, int(3*s)))

    elif char_name == "Prime Time":
        # TV/broadcast blue suit on torso
        pygame.draw.rect(surface, (20, 60, 160),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # White shirt and red tie
        pygame.draw.polygon(surface, (235, 232, 228), [
            (sx - int(5*s), sy + int(3*s)),
            (sx + int(5*s), sy + int(3*s)),
            (sx + int(3*s), sy + int(bl*0.48)),
            (sx - int(3*s), sy + int(bl*0.48)),
        ])
        pygame.draw.polygon(surface, (200, 20, 20), [
            (sx - int(2*s), sy + int(8*s)),
            (sx + int(2*s), sy + int(8*s)),
            (sx + int(3*s), sy + int(bl*0.38)),
            (sx, sy + int(bl*0.44)),
            (sx - int(3*s), sy + int(bl*0.38)),
        ])
        # Suit outline
        pygame.draw.rect(surface, (35, 85, 200),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Lapels
        pygame.draw.polygon(surface, (15, 45, 130), [
            (sx, sy + int(5*s)),
            (sx - int(9*s), sy + int(2*s)),
            (sx - int(7*s), sy + int(bl*0.44)),
        ])
        pygame.draw.polygon(surface, (15, 45, 130), [
            (sx, sy + int(5*s)),
            (sx + int(9*s), sy + int(2*s)),
            (sx + int(7*s), sy + int(bl*0.44)),
        ])
        # Broadcast microphone in right hand
        pygame.draw.line(surface, (80, 80, 90), (rhx, rhy), (rhx, rhy - int(20*s)), max(2, int(3*s)))
        pygame.draw.ellipse(surface, (60, 60, 70),
                            (rhx - int(5*s), rhy - int(28*s), int(10*s), int(14*s)))
        pygame.draw.ellipse(surface, (140, 140, 150),
                            (rhx - int(5*s), rhy - int(28*s), int(10*s), int(14*s)),
                            max(1, int(s)))
        # Mic grid lines
        for _mgi2 in range(3):
            pygame.draw.line(surface, (100, 100, 110),
                             (rhx - int(4*s), rhy - int(25*s) + _mgi2*int(4*s)),
                             (rhx + int(4*s), rhy - int(25*s) + _mgi2*int(4*s)), max(1, int(s)))
        # TV screen / teleprompter by left hand
        pygame.draw.rect(surface, (20, 20, 30),
                         (lhx - int(12*s), lhy - int(10*s), int(20*s), int(14*s)),
                         border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (0, 160, 220),
                         (lhx - int(11*s), lhy - int(9*s), int(18*s), int(11*s)))
        # Screen scanlines
        for _scl in range(3):
            pygame.draw.line(surface, (0, 130, 180),
                             (lhx - int(10*s), lhy - int(7*s) + _scl*int(3*s)),
                             (lhx + int(6*s), lhy - int(7*s) + _scl*int(3*s)), max(1, int(s)))
        # Slick hair on head
        pygame.draw.ellipse(surface, (30, 20, 10),
                            (hx - int(hd*1.05), hy - hd - int(4*s), int(hd*2.1), int(hd*0.8)))
        # Bright studio lights hitting eyes
        for _ptex in (-1, 1):
            pygame.draw.circle(surface, (60, 120, 220),
                               (hx + _ptex*int(hd*0.33), hy - int(hd*0.1)), max(3, int(4*s)))
            pygame.draw.circle(surface, (180, 220, 255),
                               (hx + _ptex*int(hd*0.33), hy - int(hd*0.1)), max(1, int(2*s)))

    elif char_name == "Rage Quitter":
        # Rage-red crumpled body (like something being thrown)
        pygame.draw.rect(surface, (180, 20, 10),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Crumple lines across the suit
        for _rqi, (_rqx1, _rqy1, _rqx2, _rqy2) in enumerate([
            (-8, 5, 3, 18), (4, 2, -5, 20), (-2, 14, 8, 28),
            (0, 9, -7, 22), (5, 16, -1, 30)]):
            pygame.draw.line(surface, (220, 50, 30),
                             (sx + int(_rqx1*s), sy + int(_rqy1*s)),
                             (sx + int(_rqx2*s), sy + int(_rqy2*s)), max(1, int(s)))
        # Controller silhouette thrown (right hand)
        _ctx = rhx + facing*int(14*s)
        _cty = rhy - int(8*s)
        pygame.draw.rect(surface, (30, 30, 35),
                         (_ctx - int(10*s), _cty - int(4*s), int(20*s), int(8*s)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 60, 70),
                         (_ctx - int(10*s), _cty - int(4*s), int(20*s), int(8*s)),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Controller buttons
        for _cbi2, _cbc in [(0,(200,30,30)), (1,(30,30,200)), (2,(30,200,30))]:
            pygame.draw.circle(surface, _cbc,
                               (_ctx + int((5-_cbi2*3)*s), _cty - int(2*s)), max(1, int(2*s)))
        # Cord flying behind
        pygame.draw.line(surface, (50, 50, 60),
                         (_ctx - int(10*s), _cty),
                         (_ctx - int(18*s), _cty + int(6*s)), max(1, int(2*s)))
        # Rage steam bursting from head
        for _rsti in range(5):
            _rsta = math.pi * (0.3 + _rsti * 0.12) - 0.2
            pygame.draw.line(surface, (255, 80, 40),
                             (hx + int(math.cos(_rsta)*hd), hy - int(math.sin(_rsta)*hd)),
                             (hx + int(math.cos(_rsta)*(hd+int((8+_rsti*3)*s))),
                              hy - int(math.sin(_rsta)*(hd+int((8+_rsti*3)*s)))),
                             max(2, int(3*s)))
        # Screaming mouth (wide open)
        pygame.draw.ellipse(surface, (20, 5, 5),
                            (hx - int(hd*0.4), hy + int(hd*0.2), int(hd*0.8), int(hd*0.45)))
        # Angry furrowed brows
        for _rbdir in (-1, 1):
            pygame.draw.line(surface, (80, 10, 5),
                             (hx + _rbdir*int(hd*0.6), hy - int(hd*0.5)),
                             (hx + _rbdir*int(hd*0.15), hy - int(hd*0.65)), max(2, int(3*s)))
        # Rage veins on forehead
        pygame.draw.line(surface, (200, 40, 20),
                         (hx - int(hd*0.15), hy - int(hd*0.6)),
                         (hx + int(hd*0.1), hy - int(hd*0.3)), max(1, int(s)))

    elif char_name == "Void Master":
        # Pure black void body — deep absence of light
        pygame.draw.rect(surface, (5, 0, 15),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(4*s)),
                         border_radius=max(2, int(4*s)))
        # Void edge dissolve — darkened outer border
        pygame.draw.rect(surface, (20, 5, 40),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(4*s)),
                         max(2, int(3*s)), border_radius=max(2, int(4*s)))
        # Stars being consumed (dark orbs at edges)
        for _vsi in range(6):
            _vsa = _vsi * math.pi / 3
            _vsx2 = sx + int(math.cos(_vsa) * 16 * s)
            _vsy2 = sy + int(bl*0.4) + int(math.sin(_vsa) * 14 * s)
            pygame.draw.circle(surface, (15, 5, 35), (_vsx2, _vsy2), max(4, int(6*s)))
            # Faint dying star
            pygame.draw.circle(surface, (80, 40, 120), (_vsx2, _vsy2), max(1, int(2*s)))
        # Purple void tear on chest (rip in reality)
        _vtx, _vty = sx, sy + int(bl*0.4)
        pygame.draw.polygon(surface, (40, 0, 80), [
            (_vtx, _vty - int(12*s)),
            (_vtx + int(4*s), _vty - int(5*s)),
            (_vtx + int(6*s), _vty + int(2*s)),
            (_vtx + int(3*s), _vty + int(10*s)),
            (_vtx - int(3*s), _vty + int(10*s)),
            (_vtx - int(6*s), _vty + int(2*s)),
            (_vtx - int(4*s), _vty - int(5*s)),
        ])
        # Inner void glow (deep purple inner light)
        _voidsurf = pygame.Surface((int(14*s)+1, int(26*s)+1), pygame.SRCALPHA)
        pygame.draw.ellipse(_voidsurf, (120, 0, 200, 120), (0, 0, int(14*s), int(26*s)))
        surface.blit(_voidsurf, (_vtx - int(7*s), _vty - int(13*s)))
        # Void eyes — glowing deep purple
        for _vex in (-1, 1):
            pygame.draw.circle(surface, (60, 0, 120),
                               (hx + _vex*int(hd*0.33), hy - int(hd*0.1)), max(4, int(6*s)))
            pygame.draw.circle(surface, (140, 0, 220),
                               (hx + _vex*int(hd*0.33), hy - int(hd*0.1)), max(2, int(4*s)))
            pygame.draw.circle(surface, (200, 80, 255),
                               (hx + _vex*int(hd*0.33), hy - int(hd*0.1)), max(1, int(2*s)))
        # Void head — dark with no features visible
        pygame.draw.circle(surface, (8, 0, 20), (hx, hy), hd, max(2, int(3*s)))

    elif char_name == "Screentime":
        # Monitor / screen body on torso
        pygame.draw.rect(surface, (30, 30, 40),
                         (sx - int(12*s), sy - int(2*s), int(24*s), bl + int(4*s)),
                         border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (60, 60, 75),
                         (sx - int(12*s), sy - int(2*s), int(24*s), bl + int(4*s)),
                         max(1, int(2*s)), border_radius=max(2, int(4*s)))
        # Screen surface (glowing blue-white)
        pygame.draw.rect(surface, (0, 180, 240),
                         (sx - int(10*s), sy + int(2*s), int(20*s), int(bl*0.75)),
                         border_radius=max(1, int(2*s)))
        # Scanlines on screen
        for _scl2 in range(6):
            _scly = sy + int(2*s) + int(bl*0.75 * _scl2 / 7)
            pygame.draw.line(surface, (0, 150, 200),
                             (sx - int(10*s), _scly), (sx + int(10*s), _scly), max(1, int(s)))
        # Screen content — UI elements
        pygame.draw.rect(surface, (0, 100, 160),
                         (sx - int(8*s), sy + int(4*s), int(16*s), max(3, int(4*s))),
                         border_radius=max(1, int(s)))
        for _uii in range(3):
            pygame.draw.rect(surface, (0, 130, 190),
                             (sx - int(8*s), sy + int(9*s) + _uii*int(5*s), int(10*s), max(2, int(3*s))),
                             border_radius=max(1, int(s)))
        # Progress bar at bottom of screen
        pygame.draw.rect(surface, (0, 80, 120),
                         (sx - int(9*s), sy + int(bl*0.7), int(18*s), max(3, int(4*s))),
                         border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (0, 200, 255),
                         (sx - int(9*s), sy + int(bl*0.7), int(12*s), max(3, int(4*s))),
                         border_radius=max(1, int(s)))
        # Keyboard / stand below screen
        pygame.draw.rect(surface, (40, 40, 50),
                         (sx - int(10*s), wy - int(2*s), int(20*s), max(3, int(5*s))),
                         border_radius=max(1, int(2*s)))
        for _kyi in range(5):
            pygame.draw.rect(surface, (55, 55, 70),
                             (sx - int(8*s) + _kyi*int(4*s), wy - int(s), int(3*s), max(2, int(3*s))),
                             border_radius=max(1, int(s)))
        # Screen-face head (monitor head)
        pygame.draw.rect(surface, (30, 30, 40),
                         (hx - int(hd*1.1), hy - hd - int(2*s), int(hd*2.2), int(hd*1.9)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (60, 60, 75),
                         (hx - int(hd*1.1), hy - hd - int(2*s), int(hd*2.2), int(hd*1.9)),
                         max(1, int(2*s)), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (0, 180, 240),
                         (hx - int(hd*0.9), hy - hd + int(s), int(hd*1.8), int(hd*1.5)),
                         border_radius=max(1, int(2*s)))
        # Face UI: two eye rectangles and mouth bar
        for _heox in (-1, 1):
            pygame.draw.rect(surface, (255, 255, 100),
                             (hx + _heox*int(hd*0.5) - int(4*s), hy - int(hd*0.35),
                              int(8*s), max(4, int(6*s))), border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (255, 100, 100),
                         (hx - int(hd*0.5), hy + int(hd*0.2), int(hd), max(3, int(4*s))),
                         border_radius=max(1, int(s)))

    elif char_name == "777":
        # Golden casino suit on torso
        pygame.draw.rect(surface, (180, 140, 0),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Suit sheen
        pygame.draw.polygon(surface, (220, 185, 30), [
            (sx - int(9*s), sy + int(2*s)),
            (sx + int(4*s), sy + int(2*s)),
            (sx + int(2*s), sy + int(bl*0.9)),
            (sx - int(9*s), sy + int(bl*0.9)),
        ])
        pygame.draw.rect(surface, (240, 210, 60),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # "777" on chest
        _sf2 = _get_font(max(8, int(12*s)))
        _st3 = _sf2.render("777", True, (220, 30, 30))
        surface.blit(_st3, (sx - _st3.get_width()//2, sy + int(bl*0.35)))
        # Spinning slot reel symbols on arms
        for _sar, _sahand, _sasym in [(lhx, lhy, "★"), (rhx, rhy, "♦")]:
            pygame.draw.rect(surface, (200, 160, 0),
                             (_sar - int(8*s), _sahand - int(8*s), int(16*s), int(14*s)),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (240, 210, 60),
                             (_sar - int(8*s), _sahand - int(8*s), int(16*s), int(14*s)),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
            _ssf = _get_font(max(7, int(10*s)))
            _sst = _ssf.render(_sasym, True, (200, 20, 20))
            surface.blit(_sst, (_sar - _sst.get_width()//2, _sahand - _sst.get_height()//2))
        # Gold coin scatter around feet
        for _gc3i in range(5):
            _gc3x = wx - int(12*s) + _gc3i * int(6*s)
            _gc3y = wy + int(4*s) + (_gc3i % 2) * int(4*s)
            pygame.draw.circle(surface, (200, 165, 0), (_gc3x, _gc3y), max(3, int(5*s)))
            pygame.draw.circle(surface, (240, 215, 60), (_gc3x, _gc3y), max(3, int(5*s)), max(1, int(s)))
            pygame.draw.circle(surface, (220, 185, 20), (_gc3x, _gc3y), max(1, int(2*s)))
        # Lucky 7 head crown
        pygame.draw.rect(surface, (180, 140, 0),
                         (hx - int(hd*0.9), hy - hd - int(8*s), int(hd*1.8), int(8*s)))
        for _cwi in range(4):
            _cwx = hx - int(hd*0.8) + _cwi * int(hd*0.5)
            pygame.draw.polygon(surface, (220, 175, 20), [
                (_cwx - int(3*s), hy - hd - int(8*s)),
                (_cwx + int(3*s), hy - hd - int(8*s)),
                (_cwx, hy - hd - int(16*s)),
            ])
        # Red 7 gems on crown
        for _cgi in range(3):
            pygame.draw.circle(surface, (200, 20, 20),
                               (hx - int(hd*0.6) + _cgi*int(hd*0.58), hy - hd - int(6*s)),
                               max(2, int(3*s)))

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

    elif char_name == "Godslayer":
        t = pygame.time.get_ticks()
        # Dark crimson armor — body
        pygame.draw.rect(surface, (80, 5, 20),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (160, 20, 60),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Gold divine runes on armor (cracking / corrupted)
        for _gri, _grp in enumerate([(sx-int(6*s), sy+int(bl*.15)),
                                      (sx+int(2*s), sy+int(bl*.4)),
                                      (sx-int(3*s), sy+int(bl*.65))]):
            pygame.draw.line(surface, (200, 160, 10),
                             _grp, (_grp[0]+int(8*s), _grp[1]+int(4*s)), max(1, int(s)))
            pygame.draw.line(surface, (200, 160, 10),
                             _grp, (_grp[0]-int(4*s), _grp[1]+int(8*s)), max(1, int(s)))
        # Dark wings on back (two jagged polygons)
        for _wsign in (-1, 1):
            _wpts = [
                (sx, sy + int(4*s)),
                (sx + _wsign*int(50*s), sy - int(30*s)),
                (sx + _wsign*int(40*s), sy + int(20*s)),
                (sx + _wsign*int(60*s), sy + int(40*s)),
                (sx + _wsign*int(30*s), sy + int(45*s)),
                (sx + _wsign*int(20*s), wy + int(5*s)),
            ]
            pygame.draw.polygon(surface, (40, 5, 15), _wpts)
            pygame.draw.polygon(surface, (160, 20, 60), _wpts, max(1, int(s)))
        # Pulsing divine aura ring
        _asize = int(hd * 1.4 + 3 * s * math.sin(t * 0.004))
        pygame.draw.circle(surface, (200, 160, 10), (hx, hy), _asize, max(1, int(2*s)))
        # Glowing gold eyes
        for _gex in (hx - int(hd*.35), hx + int(hd*.35)):
            pygame.draw.circle(surface, (220, 180, 0), (_gex, hy - int(hd*.15)), max(2, int(4*s)))
            pygame.draw.circle(surface, (255, 240, 60), (_gex, hy - int(hd*.15)), max(1, int(2*s)))
        # Shoulder pauldrons
        for _spx in (sx - int(13*s), sx + int(13*s)):
            pygame.draw.ellipse(surface, (120, 10, 30),
                                (_spx - int(6*s), sy - int(2*s), int(12*s), int(8*s)))
            pygame.draw.ellipse(surface, (200, 30, 60),
                                (_spx - int(6*s), sy - int(2*s), int(12*s), int(8*s)), max(1, int(s)))

    elif char_name == "Scrollmaster":
        # Ancient scholar robes
        pygame.draw.rect(surface, (140, 115, 55),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (175, 150, 80),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(3, int(5*s)))
        # Robe sash belt
        pygame.draw.rect(surface, (80, 60, 20),
                         (sx - int(11*s), wy - int(4*s), int(22*s), max(4, int(7*s))))
        pygame.draw.rect(surface, (120, 90, 35),
                         (sx - int(11*s), wy - int(4*s), int(22*s), max(4, int(7*s))), max(1, int(s)))
        # Arcane rune marks on robe
        for _sri, (_srx, _sry) in enumerate([(sx-int(5*s), sy+int(bl*.2)),
                                              (sx+int(3*s), sy+int(bl*.55))]):
            pygame.draw.circle(surface, (200, 180, 80), (_srx, _sry), max(2, int(3*s)), max(1, int(s)))
            pygame.draw.line(surface, (200, 180, 80),
                             (_srx - int(4*s), _sry), (_srx + int(4*s), _sry), max(1, int(s)))
            pygame.draw.line(surface, (200, 180, 80),
                             (_srx, _sry - int(4*s)), (_srx, _sry + int(4*s)), max(1, int(s)))
        # Scroll in forward hand (rolled parchment)
        _scx, _scy = rhx + facing*int(6*s), rhy
        pygame.draw.rect(surface, (220, 200, 150),
                         (_scx - int(3*s), _scy - int(10*s), int(6*s), int(20*s)),
                         border_radius=max(2, int(3*s)))
        pygame.draw.ellipse(surface, (200, 175, 120),
                            (_scx - int(4*s), _scy - int(12*s), int(8*s), int(6*s)))
        pygame.draw.ellipse(surface, (200, 175, 120),
                            (_scx - int(4*s), _scy + int(6*s), int(8*s), int(6*s)))
        # Ink lines on scroll
        for _sli in range(3):
            pygame.draw.line(surface, (40, 30, 20),
                             (_scx - int(2*s), _scy - int(5*s) + _sli*int(4*s)),
                             (_scx + int(2*s), _scy - int(5*s) + _sli*int(4*s)), max(1, int(s)))
        # Long pointed hat
        pygame.draw.polygon(surface, (120, 95, 40), [
            (hx - hd, hy - hd),
            (hx + hd, hy - hd),
            (hx + facing*int(hd*0.3), hy - int(hd*3.0)),
        ])
        pygame.draw.polygon(surface, (160, 130, 60), [
            (hx - hd, hy - hd),
            (hx + hd, hy - hd),
            (hx + facing*int(hd*0.3), hy - int(hd*3.0)),
        ], max(1, int(s)))
        # Flowing beard wisps
        for _bwi in range(3):
            pygame.draw.line(surface, (220, 215, 200),
                             (hx - int(hd*0.2) + _bwi*int(hd*0.2), hy + int(hd*0.5)),
                             (hx - int(hd*0.3) + _bwi*int(hd*0.3), hy + int(hd*1.4) + _bwi*int(2*s)),
                             max(1, int(s)))

    elif char_name == "Boulder":
        # Massive stone body — wide rough rectangle
        pygame.draw.rect(surface, (95, 70, 45),
                         (sx - int(16*s), sy - int(4*s), int(32*s), bl + int(8*s)),
                         border_radius=max(4, int(7*s)))
        pygame.draw.rect(surface, (70, 50, 30),
                         (sx - int(16*s), sy - int(4*s), int(32*s), bl + int(8*s)),
                         max(1, int(s)), border_radius=max(4, int(7*s)))
        # Stone crack lines
        pygame.draw.lines(surface, (50, 35, 18), False, [
            (sx - int(8*s), sy + int(4*s)),
            (sx - int(2*s), sy + int(14*s)),
            (sx + int(6*s), sy + int(10*s)),
        ], max(1, int(2*s)))
        pygame.draw.lines(surface, (50, 35, 18), False, [
            (sx + int(5*s), sy + int(25*s)),
            (sx - int(3*s), sy + int(32*s)),
            (sx + int(2*s), sy + int(40*s)),
        ], max(1, int(2*s)))
        # Boulder-sized fists (large round stones)
        for _bfx, _bfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (100, 75, 50), (_bfx, _bfy), max(7, int(11*s)))
            pygame.draw.circle(surface, (70, 52, 32), (_bfx, _bfy), max(7, int(11*s)), max(1, int(2*s)))
            # Knuckle crack marks
            pygame.draw.line(surface, (55, 38, 20),
                             (_bfx - int(4*s), _bfy - int(3*s)),
                             (_bfx + int(4*s), _bfy + int(2*s)), max(1, int(s)))
        # Stone pebble brow ridge on head
        pygame.draw.arc(surface, (80, 60, 35),
                        (hx - hd, hy - hd - int(4*s), hd*2, int(8*s)), 0, math.pi, max(3, int(5*s)))
        # Rocky head bump texture
        pygame.draw.circle(surface, (110, 84, 54), (hx, hy), int(hd*1.05))
        pygame.draw.circle(surface, (80, 60, 35), (hx, hy), int(hd*1.05), max(1, int(2*s)))
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Wisp":
        t = pygame.time.get_ticks()
        # Ethereal light aura pulsing around whole body
        _wpulse = 0.5 + 0.5 * math.sin(t * 0.005)
        for _wr in range(5, 0, -1):
            _wc = (max(0, int(150 + _wr*12)), max(0, int(220 + _wr*6)), 255)
            pygame.draw.circle(surface, _wc, (hx, hy), hd + int(_wr * 5 * s * (0.8 + 0.4*_wpulse)),
                               max(1, int(2*s)))
        # Wispy light trail particles drifting upward
        for _wpi in range(5):
            _wpx = sx + int((_wpi - 2) * 7 * s)
            _wpy = sy - int(_wpi * 8 * s * (0.5 + _wpulse))
            _wpc2 = (180, 240, 255)
            pygame.draw.circle(surface, _wpc2, (_wpx, _wpy), max(1, int((4 - _wpi//2) * s)))
        # Bright luminous core ring on body
        pygame.draw.circle(surface, (220, 245, 255), (sx, (sy+wy)//2), max(6, int(10*s)), max(2, int(3*s)))
        pygame.draw.circle(surface, (255, 255, 255), (sx, (sy+wy)//2), max(3, int(5*s)))
        # Glowing hand orbs
        for _whx, _why in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (180, 240, 255), (_whx, _why), max(4, int(6*s)))
            pygame.draw.circle(surface, (255, 255, 255), (_whx, _why), max(2, int(3*s)))
        # Soft glowing head halo
        pygame.draw.circle(surface, (200, 245, 255), (hx, hy), int(hd*1.15), max(1, int(2*s)))

    elif char_name == "Polar Bear":
        # Thick white fur suit body
        pygame.draw.rect(surface, (225, 235, 250),
                         (sx - int(13*s), sy - int(2*s), int(26*s), bl + int(4*s)),
                         border_radius=max(4, int(8*s)))
        pygame.draw.rect(surface, (190, 205, 225),
                         (sx - int(13*s), sy - int(2*s), int(26*s), bl + int(4*s)),
                         max(1, int(s)), border_radius=max(4, int(8*s)))
        # Fur texture lines on body
        for _fti in range(5):
            _ftx = sx - int(10*s) + _fti * int(5*s)
            pygame.draw.line(surface, (200, 215, 235),
                             (_ftx, sy + int(5*s)), (_ftx + int(3*s), sy + int(15*s)), max(1, int(s)))
        # Bear paw gloves
        for _pbx, _pby in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (210, 225, 245), (_pbx, _pby), max(6, int(9*s)))
            pygame.draw.circle(surface, (180, 195, 215), (_pbx, _pby), max(6, int(9*s)), max(1, int(s)))
            # Claw tips
            for _ci2, _ca in enumerate([math.radians(-30), 0, math.radians(30)]):
                _ctx = _pbx + int(math.cos(_ca) * max(7, int(10*s)))
                _cty = _pby + int(math.sin(_ca) * max(7, int(10*s)))
                pygame.draw.line(surface, (160, 170, 190), (_pbx, _pby), (_ctx, _cty), max(1, int(s)))
        # Bear ear rounds on head
        for _beax in (hx - int(hd*0.75), hx + int(hd*0.75)):
            pygame.draw.circle(surface, (210, 225, 245), (_beax, hy - hd + int(2*s)), max(5, int(8*s)))
            pygame.draw.circle(surface, (180, 140, 130), (_beax, hy - hd + int(2*s)), max(3, int(4*s)))
        # Big black bear nose
        pygame.draw.circle(surface, (15, 10, 10), (hx, hy + int(hd*0.25)), max(3, int(5*s)))
        pygame.draw.circle(surface, (40, 30, 30), (hx, hy + int(hd*0.25)), max(3, int(5*s)), max(1, int(s)))

    elif char_name == "Quaker":
        # Seismic bodysuit — earthy dark browns
        pygame.draw.rect(surface, (80, 55, 25),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (120, 90, 45),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Seismic wave rings emanating from waist
        for _qri in range(3):
            _qrr = int((hd + int(_qri*8*s)) * 1.1)
            pygame.draw.arc(surface, (150, 115, 60),
                            (wx - _qrr, wy - _qrr//2, _qrr*2, _qrr),
                            math.radians(200), math.radians(340), max(1, int(s)))
        # Ground cracks radiating from each foot
        for _qfx in (sx - int(8*s), sx + int(8*s)):
            pygame.draw.lines(surface, (60, 40, 15), False, [
                (_qfx, wy + int(14*s)),
                (_qfx + int(5*s*(-1 if _qfx < sx else 1)), wy + int(24*s)),
                (_qfx + int(9*s*(-1 if _qfx < sx else 1)), wy + int(20*s)),
            ], max(1, int(2*s)))
        # Rocky stone gauntlet fists
        for _qqx, _qqy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (100, 75, 45), (_qqx, _qqy), max(6, int(9*s)))
            pygame.draw.circle(surface, (70, 52, 28), (_qqx, _qqy), max(6, int(9*s)), max(1, int(2*s)))
        # Rough stone helmet
        pygame.draw.circle(surface, (110, 82, 48), (hx, hy), int(hd*1.12))
        pygame.draw.circle(surface, (80, 58, 30), (hx, hy), int(hd*1.12), max(1, int(2*s)))
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Echo":
        t = pygame.time.get_ticks()
        # Teal sound-wave bodysuit
        pygame.draw.rect(surface, (20, 120, 110),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (40, 180, 165),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Sound wave ripple rings on chest
        for _eri in range(3):
            _err = int(hd * (0.55 + _eri * 0.4))
            _eral = max(1, int(s) - (_eri > 1))
            pygame.draw.arc(surface, (80, 220, 200),
                            (sx - _err, sy + int(bl*0.25) - _err//2, _err*2, _err),
                            math.radians(20), math.radians(160), _eral)
        # Speaker grill on chest
        _sgx, _sgy = sx, sy + int(bl*0.55)
        pygame.draw.rect(surface, (15, 90, 80),
                         (_sgx - int(8*s), _sgy - int(5*s), int(16*s), int(10*s)),
                         border_radius=max(1, int(2*s)))
        for _sgi2 in range(4):
            pygame.draw.line(surface, (60, 200, 180),
                             (_sgx - int(6*s), _sgy - int(3*s) + _sgi2*int(2*s)),
                             (_sgx + int(6*s), _sgy - int(3*s) + _sgi2*int(2*s)), max(1, int(s)))
        # Big headphone ear cups
        for _ehead in (-1, 1):
            _ehx = hx + _ehead * int(hd * 1.15)
            pygame.draw.circle(surface, (25, 130, 120), (_ehx, hy), max(5, int(8*s)))
            pygame.draw.circle(surface, (50, 190, 175), (_ehx, hy), max(5, int(8*s)), max(1, int(2*s)))
            pygame.draw.circle(surface, (30, 160, 145), (_ehx, hy), max(3, int(5*s)))
        # Headband connecting ears
        pygame.draw.arc(surface, (30, 140, 130),
                        (hx - int(hd*1.2), hy - hd - int(4*s), int(hd*2.4), int(hd*1.0)),
                        0, math.pi, max(2, int(3*s)))
        # Animated musical note floating up
        _nt = (t // 600) % 3
        _nx = hx + int((_nt - 1) * 12 * s)
        _ny = hy - hd - int(10*s) - int(_nt * 6 * s)
        pygame.draw.circle(surface, (80, 220, 200), (_nx, _ny), max(2, int(3*s)))
        pygame.draw.line(surface, (80, 220, 200),
                         (_nx + int(3*s), _ny), (_nx + int(3*s), _ny - int(8*s)), max(1, int(s)))

    elif char_name == "Phantom Thief":
        # Dramatic dark midnight-blue suit
        pygame.draw.rect(surface, (25, 25, 60),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (50, 50, 100),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # White pocket square / rose at lapel
        pygame.draw.circle(surface, (220, 30, 60),
                           (sx + facing*int(5*s), sy + int(bl*0.18)), max(2, int(4*s)))
        pygame.draw.circle(surface, (255, 80, 100),
                           (sx + facing*int(5*s), sy + int(bl*0.18)), max(2, int(4*s)), max(1, int(s)))
        # Calling card in hand
        _ccx, _ccy = rhx + facing*int(5*s), rhy - int(6*s)
        pygame.draw.rect(surface, (240, 240, 230),
                         (_ccx - int(6*s), _ccy - int(4*s), int(12*s), int(8*s)),
                         border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (100, 100, 90),
                         (_ccx - int(6*s), _ccy - int(4*s), int(12*s), int(8*s)),
                         max(1, int(s)), border_radius=max(1, int(s)))
        # "?" on card
        _pf2 = _get_font(max(7, int(9*s)))
        _pt = _pf2.render("?", True, (50, 50, 90))
        surface.blit(_pt, (_ccx - _pt.get_width()//2, _ccy - _pt.get_height()//2))
        # Phantom half-mask (white, covers upper face)
        pygame.draw.ellipse(surface, (240, 238, 235),
                            (hx + facing*int(hd*.05), hy - int(hd*.6),
                             int(hd*.9), int(hd*.65)))
        pygame.draw.ellipse(surface, (180, 175, 170),
                            (hx + facing*int(hd*.05), hy - int(hd*.6),
                             int(hd*.9), int(hd*.65)), max(1, int(s)))
        # Mask eye hole
        pygame.draw.circle(surface, (0, 0, 0),
                           (hx + facing*int(hd*.4), hy - int(hd*.35)), max(2, int(3*s)))
        # Wide-brim phantom hat
        pygame.draw.polygon(surface, (15, 15, 40), [
            (hx - int(hd*1.2), hy - hd), (hx + int(hd*1.2), hy - hd),
            (hx + int(hd*0.5), hy - int(hd*2.2)), (hx - int(hd*0.5), hy - int(hd*2.2)),
        ])
        pygame.draw.rect(surface, (15, 15, 40),
                         (hx - int(hd*1.3), hy - hd - int(2*s), int(hd*2.6), max(3, int(4*s))))
        pygame.draw.line(surface, (50, 50, 100),
                         (hx - int(hd*1.3), hy - hd - int(2*s)),
                         (hx + int(hd*1.3), hy - hd - int(2*s)), max(1, int(s)))
        # Flowing dramatic cape
        _cape_col = (20, 20, 55)
        pygame.draw.polygon(surface, _cape_col, [
            (sx - int(hd*.5), sy + int(4*s)),
            (sx - int(hd*2.0), wy + int(22*s)),
            (sx - int(hd*1.0), wy + int(10*s)),
            (sx, wy + int(28*s)),
            (sx + int(hd*1.0), wy + int(10*s)),
            (sx + int(hd*2.0), wy + int(22*s)),
            (sx + int(hd*.5), sy + int(4*s)),
        ])
        pygame.draw.polygon(surface, (50, 50, 100), [
            (sx - int(hd*.5), sy + int(4*s)),
            (sx - int(hd*2.0), wy + int(22*s)),
            (sx - int(hd*1.0), wy + int(10*s)),
            (sx, wy + int(28*s)),
            (sx + int(hd*1.0), wy + int(10*s)),
            (sx + int(hd*2.0), wy + int(22*s)),
            (sx + int(hd*.5), sy + int(4*s)),
        ], max(1, int(s)))

    elif char_name == "Cloned":
        t = pygame.time.get_ticks()
        # Ghost/shadow clone trailing slightly behind
        _offset = int(7*s)
        _clone_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.circle(_clone_surf, (80, 200, 150, 80),
                           (hx - facing*_offset, hy), hd)
        pygame.draw.rect(_clone_surf, (60, 160, 120, 60),
                         (sx - facing*_offset - int(10*s), sy, int(20*s), bl),
                         border_radius=max(2, int(3*s)))
        surface.blit(_clone_surf, (0, 0))
        # Main body — teal-green suit
        pygame.draw.rect(surface, (50, 160, 120),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 200, 160),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Digital scanlines glitch effect
        _scan_phase = (t // 80) % 8
        for _sli2 in range(4):
            _sly2 = sy + int(bl * (_sli2 * 0.25 + 0.05))
            if (_sli2 + _scan_phase) % 4 == 0:
                pygame.draw.line(surface, (150, 255, 210),
                                 (sx - int(10*s), _sly2), (sx + int(10*s), _sly2), max(1, int(s)))
        # "×2" clone symbol on chest
        _clf = _get_font(max(9, int(13*s)))
        _clt = _clf.render("x2", True, (200, 255, 220))
        surface.blit(_clt, (sx - _clt.get_width()//2, sy + int(bl*0.35) - _clt.get_height()//2))
        # Glowing green eyes (two pairs = clone effect)
        for _ceox in (hx - int(hd*.35), hx + int(hd*.35)):
            pygame.draw.circle(surface, (80, 255, 160), (_ceox, hy - int(hd*.15)), max(2, int(3*s)))

    elif char_name == "Bomb":
        t = pygame.time.get_ticks()
        _bblink = (t // 400) % 2 == 0
        # Orange explosive suit
        pygame.draw.rect(surface, (170, 60, 15),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (210, 90, 30),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Warning stripes on suit
        for _bsi2 in range(3):
            _bsy2 = sy + int(bl*(0.2 + _bsi2*0.28))
            pygame.draw.line(surface, (255, 200, 0) if _bsi2 % 2 == 0 else (20, 20, 20),
                             (sx - int(9*s), _bsy2), (sx + int(9*s), _bsy2), max(2, int(3*s)))
        # BOOM label on chest
        _bof = _get_font(max(8, int(10*s)))
        _bot = _bof.render("BOOM", True, (255, 220, 0) if _bblink else (200, 160, 0))
        surface.blit(_bot, (sx - _bot.get_width()//2, sy + int(bl*0.55) - _bot.get_height()//2))
        # Round bomb for a head
        pygame.draw.circle(surface, (20, 20, 20), (hx, hy), int(hd*1.1))
        pygame.draw.circle(surface, (40, 40, 40), (hx, hy), int(hd*1.1), max(1, int(2*s)))
        # Fuse rope from top of head
        pygame.draw.line(surface, (120, 100, 30),
                         (hx, hy - int(hd*1.1)), (hx + int(hd*0.6), hy - int(hd*1.8)),
                         max(2, int(3*s)))
        pygame.draw.line(surface, (120, 100, 30),
                         (hx + int(hd*0.6), hy - int(hd*1.8)),
                         (hx + int(hd*0.3), hy - int(hd*2.2)), max(2, int(3*s)))
        # Fuse spark (blinking)
        if _bblink:
            pygame.draw.circle(surface, (255, 220, 0),
                               (hx + int(hd*0.3), hy - int(hd*2.2)), max(3, int(5*s)))
            pygame.draw.circle(surface, (255, 80, 0),
                               (hx + int(hd*0.3), hy - int(hd*2.2)), max(1, int(3*s)))
        # Angry bomb face
        for _bex2 in (hx - int(hd*.35), hx + int(hd*.35)):
            pygame.draw.circle(surface, (255, 60, 0) if _bblink else (180, 40, 0),
                               (_bex2, hy - int(hd*.15)), max(2, int(3*s)))
        pygame.draw.arc(surface, (200, 40, 0),
                        (hx - int(hd*.4), hy + int(hd*.1), int(hd*.8), int(hd*.5)),
                        math.radians(15), math.radians(165), max(1, int(2*s)))

    elif char_name == "Halves":
        # Body split exactly down the middle
        # Left half: dark charcoal
        pygame.draw.polygon(surface, (30, 20, 40), [
            (sx, sy), (sx - int(11*s), sy), (sx - int(11*s), wy), (sx, wy)])
        # Right half: magenta
        pygame.draw.polygon(surface, (200, 60, 200), [
            (sx, sy), (sx + int(11*s), sy), (sx + int(11*s), wy), (sx, wy)])
        # Split seam with glow
        pygame.draw.line(surface, (255, 120, 255), (sx, sy - int(2*s)), (sx, wy + int(2*s)),
                         max(2, int(3*s)))
        # "½" symbol
        _hf = _get_font(max(9, int(14*s)))
        _ht = _hf.render("½", True, (255, 200, 255))
        surface.blit(_ht, (sx - _ht.get_width()//2, sy + int(bl*0.35) - _ht.get_height()//2))
        # Split face: left dark, right magenta
        pygame.draw.polygon(surface, (30, 20, 40), [
            (hx, hy - hd), (hx - int(hd*.9), hy - hd), (hx - int(hd*.9), hy + hd), (hx, hy + hd)])
        pygame.draw.polygon(surface, (200, 60, 200), [
            (hx, hy - hd), (hx + int(hd*.9), hy - hd), (hx + int(hd*.9), hy + hd), (hx, hy + hd)])
        pygame.draw.line(surface, (255, 120, 255),
                         (hx, hy - hd - int(2*s)), (hx, hy + hd + int(2*s)), max(2, int(3*s)))
        # Split hands
        pygame.draw.circle(surface, (30, 20, 40), (lhx, lhy), max(4, int(6*s)))
        pygame.draw.circle(surface, (200, 60, 200), (rhx, rhy), max(4, int(6*s)))

    elif char_name == "Elemental":
        t = pygame.time.get_ticks()
        # Four elemental quadrants on body
        # Fire (top-left): red-orange
        pygame.draw.polygon(surface, (220, 80, 20), [
            (sx - int(10*s), sy), (sx, sy), (sx, sy + int(bl*0.5)), (sx - int(10*s), sy + int(bl*0.5))])
        # Water (top-right): blue
        pygame.draw.polygon(surface, (20, 100, 220), [
            (sx, sy), (sx + int(10*s), sy), (sx + int(10*s), sy + int(bl*0.5)), (sx, sy + int(bl*0.5))])
        # Earth (bottom-left): brown-green
        pygame.draw.polygon(surface, (60, 130, 40), [
            (sx - int(10*s), sy + int(bl*0.5)), (sx, sy + int(bl*0.5)),
            (sx, wy), (sx - int(10*s), wy)])
        # Wind (bottom-right): light grey
        pygame.draw.polygon(surface, (160, 200, 220), [
            (sx, sy + int(bl*0.5)), (sx + int(10*s), sy + int(bl*0.5)),
            (sx + int(10*s), wy), (sx, wy)])
        # Element symbol at each quadrant corner
        _efs = _get_font(max(7, int(9*s)))
        for _esym, _epos in [("F", (sx - int(7*s), sy + int(bl*.15))),
                              ("W", (sx + int(3*s), sy + int(bl*.15))),
                              ("E", (sx - int(7*s), sy + int(bl*.65))),
                              ("A", (sx + int(3*s), sy + int(bl*.65)))]:
            _et = _efs.render(_esym, True, (255, 255, 255))
            surface.blit(_et, (_epos[0], _epos[1] - _et.get_height()//2))
        # Central elemental orb pulsing
        _eorb = int(hd * 0.55 + 2*s*math.sin(t*0.005))
        pygame.draw.circle(surface, (120, 200, 255), (sx, (sy+wy)//2), _eorb)
        pygame.draw.circle(surface, (200, 240, 255), (sx, (sy+wy)//2), _eorb, max(1, int(s)))
        # Elemental aura on head (rotating color)
        _ec_idx = (t // 500) % 4
        _ec = [(220, 80, 20), (20, 100, 220), (60, 130, 40), (160, 200, 220)][_ec_idx]
        pygame.draw.circle(surface, _ec, (hx, hy), int(hd*1.12), max(2, int(3*s)))

    elif char_name == "Chameleon":
        t = pygame.time.get_ticks()
        # Color-cycling body (shifts through hues)
        _hue_t = (t * 0.0005) % 1.0
        _hue_r = int(127 + 127*math.sin(_hue_t * 2 * math.pi))
        _hue_g = int(127 + 127*math.sin(_hue_t * 2 * math.pi + 2.09))
        _hue_b = int(127 + 127*math.sin(_hue_t * 2 * math.pi + 4.19))
        _cham_col = (_hue_r, _hue_g, _hue_b)
        pygame.draw.rect(surface, _cham_col,
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (min(255, _hue_r+40), min(255, _hue_g+40), min(255, _hue_b+40)),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Scale pattern diamond grid on body
        _cscale_col = (max(0, _hue_r-40), max(0, _hue_g-40), max(0, _hue_b-40))
        for _csrow in range(4):
            for _cscol in range(3):
                _csx2 = sx - int(9*s) + _cscol*int(6*s) + (_csrow%2)*int(3*s)
                _csy2 = sy + int(bl*.1) + _csrow*int(bl*.22)
                pygame.draw.rect(surface, _cscale_col,
                                 (_csx2, _csy2, int(5*s), int(5*s)), max(1, int(s)),
                                 border_radius=max(1, int(s)))
        # Curling chameleon tail on back (spiral arc)
        _ctstart = (sx - facing*int(10*s), wy - int(4*s))
        for _cti in range(4):
            _cta = math.radians(-90 - _cti * 80)
            _ctr = max(4, int((12 - _cti*3)*s))
            _ctx2 = _ctstart[0] + int(math.cos(_cta) * _ctr * _cti)
            _cty2 = _ctstart[1] + int(math.sin(_cta) * _ctr * _cti)
            pygame.draw.circle(surface, _cham_col, (_ctx2, _cty2), max(3, int((6-_cti)*s)))

    elif char_name == "Gargoyle":
        # Stone-grey gargoyle body — crouched and wide
        pygame.draw.rect(surface, (90, 85, 100),
                         (sx - int(14*s), sy - int(2*s), int(28*s), bl + int(4*s)),
                         border_radius=max(3, int(6*s)))
        pygame.draw.rect(surface, (60, 55, 75),
                         (sx - int(14*s), sy - int(2*s), int(28*s), bl + int(4*s)),
                         max(1, int(s)), border_radius=max(3, int(6*s)))
        # Stone texture lines
        for _gli in range(4):
            _gly = sy + int(bl*(_gli*.22 + .05))
            pygame.draw.line(surface, (65, 60, 80),
                             (sx - int(12*s), _gly), (sx + int(12*s), _gly), max(1, int(s)))
        # Bat wings spread behind
        for _gws in (-1, 1):
            _gwpts = [
                (sx + _gws*int(5*s), sy + int(6*s)),
                (sx + _gws*int(55*s), sy - int(15*s)),
                (sx + _gws*int(50*s), sy + int(30*s)),
                (sx + _gws*int(30*s), sy + int(50*s)),
                (sx + _gws*int(15*s), sy + int(35*s)),
            ]
            pygame.draw.polygon(surface, (50, 45, 60), _gwpts)
            pygame.draw.polygon(surface, (75, 70, 90), _gwpts, max(1, int(s)))
        # Stone claw fists
        for _gfx, _gfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (90, 85, 100), (_gfx, _gfy), max(5, int(8*s)))
            pygame.draw.circle(surface, (60, 55, 75), (_gfx, _gfy), max(5, int(8*s)), max(1, int(s)))
            # Claw tips
            for _gca in [math.radians(-40), 0, math.radians(40)]:
                _gcx = _gfx + int(math.cos(_gca) * max(6, int(9*s)))
                _gcy = _gfy + int(math.sin(_gca) * max(6, int(9*s)))
                pygame.draw.line(surface, (50, 45, 60), (_gfx, _gfy), (_gcx, _gcy), max(1, int(2*s)))
        # Gargoyle head: horns + glowing red eyes
        pygame.draw.circle(surface, (85, 80, 95), (hx, hy), int(hd*1.1))
        pygame.draw.circle(surface, (60, 55, 75), (hx, hy), int(hd*1.1), max(1, int(2*s)))
        # Horns
        for _ghx2 in (hx - int(hd*.6), hx + int(hd*.6)):
            pygame.draw.polygon(surface, (65, 58, 78), [
                (_ghx2 - int(4*s), hy - hd + int(2*s)),
                (_ghx2 + int(4*s), hy - hd + int(2*s)),
                (_ghx2, hy - int(hd*2.2)),
            ])
        # Glowing red eyes
        for _grex in (hx - int(hd*.35), hx + int(hd*.35)):
            pygame.draw.circle(surface, (200, 20, 20), (_grex, hy - int(hd*.15)), max(2, int(3*s)))
            pygame.draw.circle(surface, (255, 60, 60), (_grex, hy - int(hd*.15)), max(1, int(2*s)))
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Banshee":
        t = pygame.time.get_ticks()
        _bwsurf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        # Pulsing eerie aura around body
        _bpulse = 0.5 + 0.5 * math.sin(t * 0.004)
        for _bari in range(4, 0, -1):
            _bar = hd + int(_bari * 7 * s * (0.7 + 0.3 * _bpulse))
            pygame.draw.circle(_bwsurf, (180, 100, 255, 25 + _bari*8), (hx, hy), _bar)
        # Ghostly swirl blobs around torso
        for _bwi2 in range(4):
            _bwa = math.radians(_bwi2 * 90 + t * 0.1)
            _bwx = sx + int(math.cos(_bwa) * int(9*s))
            _bwy = (sy + wy)//2 + int(math.sin(_bwa) * int(14*s))
            pygame.draw.circle(_bwsurf, (200, 140, 255, 70), (_bwx, _bwy), max(8, int(14*s)))
        # Omnidirectional wail shockwave rings from mouth
        _sw_y = hy + int(hd*0.3)
        _wail_phase = (t // 120) % 5
        for _swi2 in range(6):
            _swa2 = math.radians(180 - _swi2 * 30 + math.sin(t*0.003)*12)
            _swr = max(10 + _swi2*7, int((10+_swi2*7)*s))
            _swx3 = hx + int(math.cos(_swa2) * _swr)
            _swy3 = _sw_y + int(math.sin(_swa2) * _swr // 2)
            _swc = max(0, 200 - _swi2 * 20)
            pygame.draw.line(_bwsurf, (_swc, int(_swc*0.7), 255, 180 - _swi2*25),
                             (hx, _sw_y), (_swx3, _swy3), max(1, int(2*s)))
        # Scream shockwave expanding circle
        _swave_r = int(((t // 60) % 30) * s * 1.5)
        if _swave_r > 2:
            pygame.draw.circle(_bwsurf, (220, 160, 255, max(0, 120 - _swave_r*4)),
                               (hx, _sw_y), _swave_r, max(1, int(s)))
        surface.blit(_bwsurf, (0, 0))
        # Flowing tattered ethereal robe
        _banshee_robe = [
            (sx - int(hd*1.3), sy + int(4*s)), (sx - int(hd*1.8), wy + int(20*s)),
            (sx - int(hd*1.0), wy + int(8*s)), (sx - int(hd*0.4), wy + int(28*s)),
            (sx, wy + int(14*s)), (sx + int(hd*0.4), wy + int(30*s)),
            (sx + int(hd*1.0), wy + int(8*s)), (sx + int(hd*1.8), wy + int(20*s)),
            (sx + int(hd*1.3), sy + int(4*s)),
        ]
        pygame.draw.polygon(surface, (155, 95, 205), _banshee_robe)
        pygame.draw.polygon(surface, (200, 160, 255), _banshee_robe, max(1, int(s)))
        # Torn robe tatter tips at bottom
        for _brti in range(4):
            _brtx = sx - int(hd*0.9) + _brti * int(hd*0.6)
            _brty = wy + int((18 + (_brti%2)*10)*s)
            _wave_off = int(4*s*math.sin(t*0.005 + _brti))
            pygame.draw.lines(surface, (175, 120, 230), False, [
                (_brtx, _brty + _wave_off),
                (_brtx + int(4*s), _brty + int(8*s) + _wave_off),
                (_brtx + int(2*s), _brty + int(14*s) + _wave_off),
            ], max(1, int(s)))
        # Hollow dark screaming mouth
        pygame.draw.ellipse(surface, (8, 4, 18),
                            (hx - int(hd*.35), hy + int(hd*.12), int(hd*.7), int(hd*.55)))
        # Inner mouth purple glow
        pygame.draw.ellipse(surface, (80, 20, 120),
                            (hx - int(hd*.25), hy + int(hd*.18), int(hd*.5), int(hd*.38)))
        # Wild streaming hair in all directions
        for _bhi in range(8):
            _bha = math.radians(90 + _bhi * 22.5 + math.sin(t*0.003+_bhi*0.8)*15)
            _bhl = hd * (1.3 + 0.4 * math.sin(t*0.002 + _bhi))
            _bhx = hx + int(math.cos(_bha) * _bhl)
            _bhy = hy - hd//2 + int(math.sin(_bha) * _bhl * 0.6)
            pygame.draw.line(surface, (235, 230, 255),
                             (hx, hy - hd + int(4*s)), (_bhx, _bhy), max(1, int(2*s)))
        # Glowing hollow eyes
        for _gbex in (hx - int(hd*.35), hx + int(hd*.35)):
            pygame.draw.circle(surface, (160, 80, 240), (_gbex, hy - int(hd*.2)), max(3, int(5*s)))
            pygame.draw.circle(surface, (220, 160, 255), (_gbex, hy - int(hd*.2)), max(2, int(4*s)))
            pygame.draw.circle(surface, (255, 240, 255), (_gbex, hy - int(hd*.2)), max(1, int(2*s)))
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Storm Caller":
        t = pygame.time.get_ticks()
        # Dark stormcloud blue bodysuit
        pygame.draw.rect(surface, (30, 50, 130),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (50, 80, 180),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Swirling storm clouds on torso
        for _sci in range(3):
            _sca = math.radians(_sci * 120 + t * 0.06)
            _scx2 = sx + int(math.cos(_sca) * int(7*s))
            _scy2 = sy + int(bl*0.4) + int(math.sin(_sca) * int(5*s))
            pygame.draw.circle(surface, (80, 100, 180), (_scx2, _scy2), max(4, int(7*s)))
        # Lightning bolt on chest
        _scbolt = [
            (sx + int(3*s), sy + int(bl*0.08)),
            (sx - int(3*s), sy + int(bl*0.38)),
            (sx + int(2*s), sy + int(bl*0.38)),
            (sx - int(4*s), sy + int(bl*0.72)),
            (sx + int(2*s), sy + int(bl*0.44)),
            (sx - int(1*s), sy + int(bl*0.44)),
        ]
        pygame.draw.polygon(surface, (255, 240, 80), _scbolt)
        # Storm cloud crown on head
        for _scci in range(4):
            _sccx = hx - int(hd*0.6) + _scci*int(hd*0.4)
            pygame.draw.circle(surface, (60, 80, 160), (_sccx, hy - hd - int(4*s)),
                               max(4, int(6*s)))
        # Animated lightning arcs from hands
        if (t // 200) % 3 != 0:
            for _slhx, _slhy in [(lhx, lhy), (rhx, rhy)]:
                for _sli3 in range(2):
                    _sltx = _slhx + facing*int((8+_sli3*8)*s)
                    _slty = _slhy - int((_sli3+1)*4*s)
                    pygame.draw.line(surface, (200, 220, 80),
                                     (_slhx, _slhy), (_sltx, _slty), max(1, int(s)))

    elif char_name == "Magnetar":
        t = pygame.time.get_ticks()
        # Deep purple magnetic bodysuit
        pygame.draw.rect(surface, (80, 20, 160),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (130, 50, 220),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Magnetic field lines curving around body
        for _mfi in range(4):
            _mfa = math.radians(_mfi * 90 + t * 0.04)
            _mfr = max(12, int((16 + _mfi*4)*s))
            pygame.draw.arc(surface, (180, 100, 255),
                            (sx - _mfr, (sy+wy)//2 - _mfr//2, _mfr*2, _mfr),
                            _mfa, _mfa + math.radians(160), max(1, int(s)))
        # Horseshoe magnet on chest
        _mhx, _mhy = sx, sy + int(bl*0.3)
        pygame.draw.arc(surface, (220, 30, 30),
                        (_mhx - int(8*s), _mhy - int(8*s), int(16*s), int(16*s)),
                        math.radians(0), math.radians(180), max(2, int(4*s)))
        pygame.draw.rect(surface, (220, 30, 30),
                         (_mhx - int(8*s), _mhy - int(2*s), max(3, int(4*s)), int(8*s)))
        pygame.draw.rect(surface, (50, 80, 220),
                         (_mhx + int(4*s), _mhy - int(2*s), max(3, int(4*s)), int(8*s)))
        # Iron filings orbiting body (animated dots)
        for _ifo in range(8):
            _ifa = math.radians(_ifo * 45 + t * 0.12)
            _ifr = max(14, int(22*s))
            _ifx = sx + int(math.cos(_ifa) * _ifr)
            _ify = (sy+wy)//2 + int(math.sin(_ifa) * _ifr//2)
            pygame.draw.circle(surface, (200, 150, 255), (_ifx, _ify), max(1, int(2*s)))

    elif char_name == "Swamp Thing":
        # Dark swamp-green mossy body
        pygame.draw.rect(surface, (25, 70, 20),
                         (sx - int(12*s), sy - int(2*s), int(24*s), bl + int(4*s)),
                         border_radius=max(3, int(6*s)))
        pygame.draw.rect(surface, (40, 110, 35),
                         (sx - int(12*s), sy - int(2*s), int(24*s), bl + int(4*s)),
                         max(1, int(s)), border_radius=max(3, int(6*s)))
        # Vine tendrils hanging from body
        for _vti in range(5):
            _vtx2 = sx - int(8*s) + _vti * int(4*s)
            pygame.draw.line(surface, (30, 90, 25),
                             (_vtx2, wy), (_vtx2 + int((_vti%3-1)*3*s), wy + int(14*s)),
                             max(1, int(2*s)))
            pygame.draw.circle(surface, (60, 140, 40),
                               (_vtx2 + int((_vti%3-1)*3*s), wy + int(14*s)), max(2, int(3*s)))
        # Moss clumps on shoulders
        for _msx in (sx - int(11*s), sx + int(11*s)):
            pygame.draw.ellipse(surface, (55, 130, 40),
                                (_msx - int(5*s), sy - int(3*s), int(10*s), int(8*s)))
        # Muddy vine-wrapped arms/fists
        for _stfx, _stfy in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (35, 90, 25), (_stfx, _stfy), max(6, int(9*s)))
            pygame.draw.circle(surface, (55, 130, 40), (_stfx, _stfy), max(6, int(9*s)), max(1, int(2*s)))
        # Swamp head: mossy, glowing yellow eyes
        pygame.draw.circle(surface, (30, 80, 25), (hx, hy), int(hd*1.12))
        pygame.draw.circle(surface, (45, 115, 35), (hx, hy), int(hd*1.12), max(1, int(2*s)))
        # Yellow glowing eyes
        for _stey in (hx - int(hd*.35), hx + int(hd*.35)):
            pygame.draw.circle(surface, (180, 200, 20), (_stey, hy - int(hd*.15)), max(2, int(4*s)))
            pygame.draw.circle(surface, (240, 255, 60), (_stey, hy - int(hd*.15)), max(1, int(2*s)))
        pygame.draw.circle(surface, col, (hx, hy), hd)

    elif char_name == "Duelist":
        # Sharp gold fencing outfit — white/cream jacket
        pygame.draw.rect(surface, (240, 235, 210),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 190, 160),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Gold epaulette on shoulder
        for _dep in (sx - int(10*s), sx + int(5*s)):
            pygame.draw.rect(surface, (200, 165, 10),
                             (_dep, sy - int(3*s), int(8*s), max(4, int(6*s))),
                             border_radius=max(1, int(2*s)))
            pygame.draw.rect(surface, (240, 215, 60),
                             (_dep, sy - int(3*s), int(8*s), max(4, int(6*s))),
                             max(1, int(s)), border_radius=max(1, int(2*s)))
        # Rapier sword held in forward hand
        _rwx = rhx + facing*int(6*s)
        _rwy = rhy
        pygame.draw.line(surface, (180, 185, 200),
                         (_rwx, _rwy), (_rwx + facing*int(45*s), _rwy - int(20*s)),
                         max(1, int(2*s)))
        # Blade highlight
        pygame.draw.line(surface, (230, 235, 250),
                         (_rwx + facing*int(4*s), _rwy - int(2*s)),
                         (_rwx + facing*int(38*s), _rwy - int(17*s)), max(1, int(s)))
        # Cross-guard / hilt
        pygame.draw.line(surface, (200, 165, 10),
                         (_rwx - facing*int(5*s), _rwy - int(5*s)),
                         (_rwx + facing*int(5*s), _rwy + int(5*s)),
                         max(2, int(3*s)))
        # Fencing mask on face (wire mesh look)
        pygame.draw.rect(surface, (40, 40, 50),
                         (hx - int(hd*.9), hy - int(hd*.7), int(hd*1.8), int(hd*1.3)),
                         border_radius=max(2, int(3*s)))
        # Mesh lines
        for _dmi in range(3):
            _dmy = hy - int(hd*.5) + _dmi * int(hd*.35)
            pygame.draw.line(surface, (70, 70, 85),
                             (hx - int(hd*.8), _dmy), (hx + int(hd*.8), _dmy), max(1, int(s)))
        for _dmj in range(4):
            _dmx2 = hx - int(hd*.7) + _dmj * int(hd*.45)
            pygame.draw.line(surface, (70, 70, 85),
                             (_dmx2, hy - int(hd*.65)), (_dmx2, hy + int(hd*.55)), max(1, int(s)))

    elif char_name == "Sunderer":
        t = pygame.time.get_ticks()
        # Thick stone-red body armour
        pygame.draw.rect(surface, (130, 30, 15),
                         (sx - int(14*s), sy - int(2*s), int(28*s), bl + int(4*s)),
                         border_radius=max(3, int(4*s)))
        pygame.draw.rect(surface, (200, 60, 30),
                         (sx - int(14*s), sy - int(2*s), int(28*s), bl + int(4*s)),
                         max(1, int(2*s)), border_radius=max(3, int(4*s)))
        # Chest plate rivets
        for _ri2, (_rx2, _ry2) in enumerate([(-8, 0), (8, 0), (-8, int(bl*.5)), (8, int(bl*.5))]):
            pygame.draw.circle(surface, (220, 180, 60),
                               (sx + int(_rx2*s), sy + int(_ry2*s)), max(2, int(3*s)))
        # Massive spiked knuckle dusters on fists
        for _fx2, _fy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (180, 40, 20), (_fx2, _fy2), max(6, int(9*s)))
            pygame.draw.circle(surface, (240, 80, 40), (_fx2, _fy2), max(5, int(8*s)), max(1, int(s)))
            for _si2 in range(6):
                _sa2 = math.radians(_si2 * 60 + t * 0.05)
                _sx3 = _fx2 + int(math.cos(_sa2) * 9 * s)
                _sy3 = _fy2 + int(math.sin(_sa2) * 9 * s)
                pygame.draw.circle(surface, (210, 70, 30), (_sx3, _sy3), max(2, int(3*s)))
        # Neck collar
        pygame.draw.rect(surface, (160, 40, 20),
                         (sx - int(9*s), sy - int(6*s), int(18*s), int(6*s)),
                         border_radius=max(2, int(3*s)))
        # Horned helmet visor strip
        pygame.draw.rect(surface, (200, 55, 30),
                         (hx - hd, hy - int(hd*.3), hd * 2, int(hd*.5)))
        pygame.draw.line(surface, (240, 90, 50),
                         (hx - int(hd*.8), hy), (hx + int(hd*.8), hy), max(1, int(s)))

    elif char_name == "Haunter":
        t = pygame.time.get_ticks()
        # Wispy ghost trails beneath body
        _hasurf = pygame.Surface((int(60*s)+4, int(bl+40)*int(s)+4), pygame.SRCALPHA)
        for _hi in range(4):
            _ha = int(70 - _hi * 18)
            _hr = max(5, int((16 - _hi*3)*s))
            _hcy2 = int((bl * 0.4 + _hi * 10) * s) + 2
            pygame.draw.ellipse(_hasurf, (100, 0, 140, _ha),
                                (int(30*s)-_hr+2, _hcy2, _hr*2, int(_hr*1.4)))
        surface.blit(_hasurf, (sx - int(30*s), sy))
        # Dark robe body
        pygame.draw.polygon(surface, (40, 0, 60), [
            (sx - int(8*s), sy), (sx + int(8*s), sy),
            (sx + int(18*s), wy + int(8*s)), (sx - int(18*s), wy + int(8*s)),
        ])
        pygame.draw.polygon(surface, (80, 10, 110), [
            (sx - int(8*s), sy), (sx + int(8*s), sy),
            (sx + int(18*s), wy + int(8*s)), (sx - int(18*s), wy + int(8*s)),
        ], max(1, int(s)))
        # Toxic wisps floating
        for _ti in range(3):
            _ta = math.radians(_ti * 120 + t * 0.07)
            _tr2 = max(10, int(14*s))
            _tx2 = sx + int(math.cos(_ta) * _tr2)
            _ty2 = (sy + wy) // 2 + int(math.sin(_ta) * _tr2 * 0.5)
            _tsurf2 = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(_tsurf2, (80, 220, 60, 130), (5, 5), 4)
            surface.blit(_tsurf2, (_tx2 - 5, _ty2 - 5))
        # Glowing purple eyes
        pygame.draw.circle(surface, (160, 50, 255), (hx - int(hd*.35), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (220, 140, 255), (hx - int(hd*.35), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (160, 50, 255), (hx + int(hd*.35), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (220, 140, 255), (hx + int(hd*.35), hy), max(2, int(3*s)))

    elif char_name == "Zeus":
        t = pygame.time.get_ticks()
        # Gold-trimmed white toga body
        pygame.draw.rect(surface, (200, 190, 80),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (255, 245, 120),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Diagonal toga sash
        pygame.draw.line(surface, (255, 255, 160),
                         (sx - int(9*s), sy + int(2*s)),
                         (sx + int(9*s), wy - int(4*s)), max(2, int(3*s)))
        # Lightning bolt crown
        _lbpts = [
            (hx - int(8*s), hy - hd - int(4*s)),
            (hx + int(2*s), hy - hd - int(12*s)),
            (hx,            hy - hd - int(6*s)),
            (hx + int(8*s), hy - hd - int(14*s)),
            (hx + int(2*s), hy - hd - int(4*s)),
        ]
        pygame.draw.polygon(surface, (255, 230, 0), _lbpts)
        pygame.draw.polygon(surface, (255, 255, 180), _lbpts, max(1, int(s)))
        # Electric sparks orbiting
        for _ei in range(5):
            _ea = math.radians(_ei * 72 + t * 0.1)
            _er2 = max(14, int(20*s))
            _ex2 = sx + int(math.cos(_ea) * _er2)
            _ey2 = (sy + wy) // 2 + int(math.sin(_ea) * int(_er2 * 0.6))
            _esurf2 = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(_esurf2, (255, 240, 80, 160 if (t//200+_ei)%2==0 else 60), (4,4), 3)
            surface.blit(_esurf2, (_ex2 - 4, _ey2 - 4))
        # Shock lines on fists
        for _fx2, _fy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (255, 240, 60), (_fx2, _fy2), max(4, int(6*s)))
            pygame.draw.circle(surface, (255, 255, 200), (_fx2, _fy2), max(2, int(3*s)))

    elif char_name == "Glacial":
        t = pygame.time.get_ticks()
        # Ice-blue armour body
        pygame.draw.rect(surface, (100, 180, 220),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(4*s)),
                         border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (200, 240, 255),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(4*s)),
                         max(1, int(s)), border_radius=max(3, int(5*s)))
        # Ice crack lines on armour
        for _ii, (_ix, _iy, _il, _ia2) in enumerate([
                (-6, int(bl*.2), 12, 75), (4, int(bl*.5), 10, 100), (-2, int(bl*.7), 8, 60)
        ]):
            pygame.draw.line(surface, (180, 230, 255),
                             (sx + int(_ix*s), sy + int(_iy*s)),
                             (sx + int((_ix + math.cos(math.radians(_ia2))*_il)*s),
                              sy + int((_iy + math.sin(math.radians(_ia2))*_il)*s)),
                             max(1, int(s)))
        # Icicle crown
        for _ici, _icx in enumerate(range(-2, 3)):
            _ich = max(6, int((8 + abs(_icx)*2)*s))
            _icbx = hx + int(_icx * hd * 0.5)
            pygame.draw.polygon(surface, (180, 230, 255), [
                (_icbx - max(2, int(3*s)), hy - hd),
                (_icbx + max(2, int(3*s)), hy - hd),
                (_icbx, hy - hd - _ich),
            ])
            pygame.draw.polygon(surface, (220, 248, 255), [
                (_icbx - max(1, int(2*s)), hy - hd),
                (_icbx, hy - hd),
                (_icbx, hy - hd - _ich + max(1, int(2*s))),
            ])
        # Frost particles drifting down
        for _fpi in range(4):
            _fpa = (t * 0.03 + _fpi * 1.5) % (math.pi * 2)
            _fpx2 = sx + int(math.sin(_fpa) * 12 * s)
            _fpy2 = sy + int((t * 0.02 + _fpi * 12) % (bl + 10) * s)
            pygame.draw.circle(surface, (210, 245, 255), (_fpx2, _fpy2), max(1, int(2*s)))

    elif char_name == "Soul Eater":
        t = pygame.time.get_ticks()
        # Dark blood-crimson robe
        pygame.draw.polygon(surface, (80, 0, 30), [
            (sx - int(8*s), sy), (sx + int(8*s), sy),
            (sx + int(16*s), wy + int(6*s)), (sx - int(16*s), wy + int(6*s)),
        ])
        pygame.draw.polygon(surface, (160, 10, 50), [
            (sx - int(8*s), sy), (sx + int(8*s), sy),
            (sx + int(16*s), wy + int(6*s)), (sx - int(16*s), wy + int(6*s)),
        ], max(1, int(s)))
        # Soul wisps orbiting
        for _swi in range(5):
            _swa = math.radians(_swi * 72 + t * 0.08)
            _swr2 = max(16, int(22*s))
            _swx2 = sx + int(math.cos(_swa) * _swr2)
            _swy2 = (sy + wy) // 2 + int(math.sin(_swa) * _swr2 * 0.5)
            _swsurf = pygame.Surface((12, 12), pygame.SRCALPHA)
            _swalpha = 150 if (t // 250 + _swi) % 2 == 0 else 80
            pygame.draw.circle(_swsurf, (200, 100, 255, _swalpha), (6, 6), 4)
            pygame.draw.circle(_swsurf, (255, 180, 255, _swalpha // 2), (6, 6), 4, 1)
            surface.blit(_swsurf, (_swx2 - 6, _swy2 - 6))
        # Glowing red eyes
        for _sex2, _sey2 in [(hx - int(hd*.35), hy), (hx + int(hd*.35), hy)]:
            pygame.draw.circle(surface, (220, 0, 40), (_sex2, _sey2), max(3, int(4*s)))
            pygame.draw.circle(surface, (255, 100, 100), (_sex2, _sey2), max(1, int(2*s)))
        # Drain tendrils from hands
        for _dx2, _dy2 in [(lhx, lhy), (rhx, rhy)]:
            for _dti in range(3):
                _dta = math.radians(_dti * 120 + t * 0.12)
                pygame.draw.line(surface, (180, 0, 60),
                                 (_dx2, _dy2),
                                 (_dx2 + int(math.cos(_dta) * 8 * s),
                                  _dy2 + int(math.sin(_dta) * 8 * s)),
                                 max(1, int(s)))

    elif char_name == "Frenzy":
        t = pygame.time.get_ticks()
        # Ragged torn orange-red vest
        pygame.draw.rect(surface, (200, 70, 10),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        # Torn edges (zigzag bottom)
        for _fri in range(5):
            _frx2 = sx - int(8*s) + _fri * int(4*s)
            _fry2 = wy + int(((_fri % 2) * 5)*s)
            pygame.draw.line(surface, (160, 50, 5),
                             (_frx2, wy), (_frx2, _fry2), max(1, int(s)))
        # Rage streaks on body
        for _rsi, (_rsx2, _rsy2, _rsl) in enumerate([(-6, int(bl*.2), 10), (3, int(bl*.5), 8)]):
            pygame.draw.line(surface, (255, 140, 0),
                             (sx + int(_rsx2*s), sy + int(_rsy2*s)),
                             (sx + int((_rsx2+_rsl)*s), sy + int(_rsy2*s)),
                             max(1, int(s)))
        # Wild spiky hair
        for _shi in range(7):
            _sha = math.radians(-90 + (_shi - 3) * 22)
            _shr2 = max(8, int((10 + abs(_shi-3)*3)*s))
            pygame.draw.line(surface, (255, 100, 0),
                             (hx, hy - hd),
                             (hx + int(math.cos(_sha) * _shr2),
                              hy - hd + int(math.sin(_sha) * _shr2)),
                             max(1, int(2*s)))
        # Spinning fist sparks (rapid punching feel)
        _fang = math.radians(t * 0.3)
        for _fx2, _fy2 in [(lhx, lhy), (rhx, rhy)]:
            for _fsi in range(3):
                _fspa = _fang + math.radians(_fsi * 120)
                _fsx2 = _fx2 + int(math.cos(_fspa) * 7 * s)
                _fsy2 = _fy2 + int(math.sin(_fspa) * 7 * s)
                pygame.draw.circle(surface, (255, 180, 20), (_fsx2, _fsy2), max(1, int(2*s)))

    elif char_name == "Specter":
        t = pygame.time.get_ticks()
        # Translucent violet ghost body
        _spsurf = pygame.Surface((int(50*s)+4, int(bl+30)*int(max(1,s))+4), pygame.SRCALPHA)
        pygame.draw.polygon(_spsurf, (120, 100, 200, 90), [
            (int(8*s)+2, 2),
            (int(42*s)+2, 2),
            (int(46*s)+2, int((bl+20)*s)+2),
            (int(4*s)+2,  int((bl+20)*s)+2),
        ])
        surface.blit(_spsurf, (sx - int(25*s), sy - int(10*s)))
        # Phase shimmer edges
        for _spi2 in range(3):
            _spa2 = math.radians(_spi2 * 120 + t * 0.06)
            _spx2 = sx + int(math.cos(_spa2) * 14 * s)
            _spy2 = (sy + wy) // 2 + int(math.sin(_spa2) * 8 * s)
            _spsurf2 = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(_spsurf2, (160, 140, 255, 100), (5, 5), 4)
            surface.blit(_spsurf2, (_spx2 - 5, _spy2 - 5))
        # Ghost face — hollow eyes
        pygame.draw.circle(surface, (40, 20, 80), (hx - int(hd*.35), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (40, 20, 80), (hx + int(hd*.35), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (200, 180, 255), (hx - int(hd*.35), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (200, 180, 255), (hx + int(hd*.35), hy), max(2, int(3*s)))
        # Wispy tail trails below waist
        for _wti in range(4):
            _wtx2 = wx + int((_wti - 1.5) * 6 * s)
            _wty2 = wy + int(_wti * 6 * s)
            _wtsurf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(_wtsurf, (140, 120, 220, 80 - _wti * 18), (0, 0, 8, 8))
            surface.blit(_wtsurf, (_wtx2 - 4, _wty2))

    elif char_name == "Demolisher":
        t = pygame.time.get_ticks()
        # Construction orange safety vest
        pygame.draw.rect(surface, (200, 100, 20),
                         (sx - int(11*s), sy - int(2*s), int(22*s), bl + int(4*s)),
                         border_radius=max(2, int(3*s)))
        # Reflective safety stripes
        for _dsi in range(2):
            _dsy2 = sy + int(bl * (0.3 + _dsi * 0.4))
            pygame.draw.line(surface, (255, 230, 0),
                             (sx - int(10*s), _dsy2), (sx + int(10*s), _dsy2),
                             max(2, int(3*s)))
        # Hard hat
        pygame.draw.ellipse(surface, (255, 200, 0),
                            (hx - int(hd*1.2), hy - hd - int(8*s), int(hd*2.4), int(hd + 8*s)))
        pygame.draw.ellipse(surface, (220, 170, 0),
                            (hx - int(hd*1.2), hy - hd - int(8*s), int(hd*2.4), int(hd + 8*s)),
                            max(1, int(s)))
        # Brim of hard hat
        pygame.draw.rect(surface, (200, 160, 0),
                         (hx - int(hd*1.4), hy - int(2*s), int(hd*2.8), int(4*s)),
                         border_radius=max(1, int(2*s)))
        # Ground crack lines below feet (shockwave visual)
        for _gci in range(3):
            _gca = math.radians((_gci - 1) * 30 + 90)
            _gcl = max(10, int((12 + _gci * 4)*s))
            pygame.draw.line(surface, (160, 100, 30),
                             (wx, wy + int(4*s)),
                             (wx + int(math.cos(_gca)*_gcl), wy + int(4*s) + int(math.sin(_gca)*_gcl)),
                             max(1, int(2*s)))
        # Heavy wrecking-ball fists
        for _fx2, _fy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (80, 60, 30), (_fx2, _fy2), max(7, int(10*s)))
            pygame.draw.circle(surface, (130, 100, 50), (_fx2, _fy2), max(6, int(9*s)), max(1, int(s)))
            for _cbi in range(4):
                _cba = math.radians(_cbi * 90 + 45)
                pygame.draw.line(surface, (80, 60, 30),
                                 (_fx2, _fy2),
                                 (_fx2 + int(math.cos(_cba)*9*s), _fy2 + int(math.sin(_cba)*9*s)),
                                 max(1, int(s)))

    elif char_name == "Feedback":
        t = pygame.time.get_ticks()
        # Teal elastic body suit
        pygame.draw.rect(surface, (30, 150, 130),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(3, int(5*s)))
        pygame.draw.rect(surface, (80, 210, 190),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(3, int(5*s)))
        # Absorb rings — concentric pulsing rings on chest
        _phase2 = (t % 1200) / 1200.0
        for _ari2 in range(3):
            _arr2 = max(4, int((6 + _ari2 * 5)*s))
            _ara2 = int(180 * (1 - (_phase2 + _ari2 * 0.33) % 1.0))
            _arsurf2 = pygame.Surface((_arr2*2+2, _arr2*2+2), pygame.SRCALPHA)
            pygame.draw.circle(_arsurf2, (80, 230, 210, _ara2),
                               (_arr2+1, _arr2+1), _arr2, max(1, int(s)))
            surface.blit(_arsurf2, (sx - _arr2 - 1, (sy+wy)//2 - _arr2 - 1))
        # Charge indicator on chest: growing bar
        _charge_w = max(4, int(16*s))
        pygame.draw.rect(surface, (20, 80, 70),
                         (sx - _charge_w//2, sy + int(bl*.35), _charge_w, max(3, int(5*s))),
                         border_radius=max(1, int(2*s)))
        # Elastic spiral pattern on arms
        for _fx2, _fy2 in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (60, 200, 180), (_fx2, _fy2), max(4, int(6*s)))
            pygame.draw.circle(surface, (130, 230, 220), (_fx2, _fy2), max(3, int(5*s)), max(1, int(s)))
        # Helmet visor ring
        pygame.draw.circle(surface, (50, 180, 160), (hx, hy), hd + max(1, int(2*s)), max(1, int(s)))

    elif char_name == "Escalator":
        t = pygame.time.get_ticks()
        # Amber body suit with stair-step patterns
        pygame.draw.rect(surface, (150, 100, 0),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (220, 160, 10),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Staircase / escalator steps on torso
        for _esi in range(4):
            _esx2 = sx - int(8*s) + _esi * int(4*s)
            _esy2 = sy + int(bl * (_esi * 0.2 + 0.1))
            pygame.draw.rect(surface, (255, 200, 30),
                             (_esx2, _esy2, int(5*s), int(3*s)))
        # Growing power indicator — pulsing gold halo
        _gpulse = abs(math.sin(t * 0.003)) * max(3, int(4*s))
        _gsurf2 = pygame.Surface((int((hd+14)*s*2)+4, int((hd+14)*s*2)+4), pygame.SRCALPHA)
        _gr2 = int((hd + int(_gpulse)) * s)
        pygame.draw.circle(_gsurf2, (255, 200, 0, 80),
                           (_gr2+2, _gr2+2), _gr2)
        pygame.draw.circle(_gsurf2, (255, 230, 80, 160),
                           (_gr2+2, _gr2+2), _gr2, max(1, int(s)))
        surface.blit(_gsurf2, (hx - _gr2 - 2, hy - _gr2 - 2))
        # Upward arrow on chest
        _arrowpts = [
            (sx, sy + int(bl*.15)),
            (sx - int(5*s), sy + int(bl*.35)),
            (sx - int(2*s), sy + int(bl*.35)),
            (sx - int(2*s), sy + int(bl*.6)),
            (sx + int(2*s), sy + int(bl*.6)),
            (sx + int(2*s), sy + int(bl*.35)),
            (sx + int(5*s), sy + int(bl*.35)),
        ]
        pygame.draw.polygon(surface, (255, 230, 0), _arrowpts)
        pygame.draw.polygon(surface, (180, 130, 0), _arrowpts, max(1, int(s)))

    elif char_name == "Pacifist":
        t = pygame.time.get_ticks()
        # Pure white flowing robe
        pygame.draw.polygon(surface, (210, 240, 210), [
            (sx - int(6*s), sy), (sx + int(6*s), sy),
            (sx + int(20*s), wy + int(10*s)), (sx - int(20*s), wy + int(10*s)),
        ])
        pygame.draw.polygon(surface, (255, 255, 240), [
            (sx - int(6*s), sy), (sx + int(6*s), sy),
            (sx + int(20*s), wy + int(10*s)), (sx - int(20*s), wy + int(10*s)),
        ], max(1, int(s)))
        # Peace symbol on chest
        _psr2 = max(6, int(9*s))
        pygame.draw.circle(surface, (100, 180, 100), (sx, (sy+wy)//2), _psr2, max(1, int(2*s)))
        pygame.draw.line(surface, (100, 180, 100),
                         (sx, (sy+wy)//2 - _psr2),
                         (sx, (sy+wy)//2 + _psr2), max(1, int(s)))
        pygame.draw.line(surface, (100, 180, 100),
                         (sx, (sy+wy)//2),
                         (sx - int(_psr2*.8), (sy+wy)//2 + int(_psr2*.6)), max(1, int(s)))
        pygame.draw.line(surface, (100, 180, 100),
                         (sx, (sy+wy)//2),
                         (sx + int(_psr2*.8), (sy+wy)//2 + int(_psr2*.6)), max(1, int(s)))
        # Halo above head
        _halo_y = hy - hd - max(5, int(7*s))
        _halo_r = max(hd, int(hd*1.3))
        _hsurf2 = pygame.Surface((_halo_r*2+4, int(8*s)+4), pygame.SRCALPHA)
        pygame.draw.ellipse(_hsurf2, (255, 240, 100, 200),
                            (2, 2, _halo_r*2, max(4, int(6*s))))
        pygame.draw.ellipse(_hsurf2, (255, 255, 180, 100),
                            (2, 2, _halo_r*2, max(4, int(6*s))), max(1, int(2*s)))
        surface.blit(_hsurf2, (hx - _halo_r - 2, _halo_y - int(3*s) - 2))
        # Reflect glow on hands — soft aura showing damage reflect
        for _px2, _py2 in [(lhx, lhy), (rhx, rhy)]:
            _psurf2 = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(_psurf2, (200, 255, 200, 100), (7, 7), 6)
            surface.blit(_psurf2, (_px2 - 7, _py2 - 7))

    elif char_name == "Cyclone":
        t = pygame.time.get_ticks()
        # Storm-blue body with swirling wind bands
        pygame.draw.rect(surface, (60, 120, 185),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (130, 190, 240),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(4*s)))
        # Spinning wind spiral
        _wphase = t * 0.08
        for _wsi in range(8):
            _wsa = math.radians(_wsi * 45) + _wphase
            _wsr2 = max(10, int((8 + _wsi * 2)*s))
            _wsx2 = sx + int(math.cos(_wsa) * _wsr2 * 0.7)
            _wsy2 = (sy + wy) // 2 + int(math.sin(_wsa) * _wsr2 * 0.4)
            _wssurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            _wsa2 = 180 - _wsi * 20
            pygame.draw.circle(_wssurf, (180, 220, 255, max(20, _wsa2)), (3, 3), 2)
            surface.blit(_wssurf, (_wsx2 - 3, _wsy2 - 3))
        # Tornado funnel below feet
        _tfpts = [
            (wx - int(14*s), wy),
            (wx + int(14*s), wy),
            (wx + int(4*s),  wy + int(12*s)),
            (wx - int(4*s),  wy + int(12*s)),
        ]
        _tfsurf = pygame.Surface((int(30*s)+4, int(14*s)+4), pygame.SRCALPHA)
        pygame.draw.polygon(_tfsurf, (140, 200, 240, 100), [
            (2, 2), (int(28*s)+2, 2),
            (int(22*s)+2, int(12*s)+2), (int(8*s)+2, int(12*s)+2)
        ])
        surface.blit(_tfsurf, (wx - int(14*s) - 2, wy - 2))
        # Teleport shimmer on head
        pygame.draw.circle(surface, (100, 170, 230), (hx, hy), hd + max(1, int(2*s)), max(1, int(s)))
        for _tpsi in range(4):
            _tpsa = math.radians(_tpsi * 90 + t * 0.15)
            _tpsx = hx + int(math.cos(_tpsa) * (hd + int(4*s)))
            _tpsy = hy + int(math.sin(_tpsa) * (hd + int(4*s)))
            pygame.draw.circle(surface, (200, 230, 255), (_tpsx, _tpsy), max(1, int(2*s)))

    elif char_name == "Phantom Blade":
        t = pygame.time.get_ticks()
        # Ghostly violet armour with lance-tip ornament
        pygame.draw.rect(surface, (100, 80, 180),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 180, 255),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Translucent ghost shroud
        _pbsurf = pygame.Surface((int(30*s), bl + int(10*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(_pbsurf, (180, 160, 255, 50),
                            (0, 0, int(30*s), bl + int(10*s)))
        surface.blit(_pbsurf, (sx - int(15*s), sy))
        # Lance glow on punching hand
        _lance_x = rhx if facing > 0 else lhx
        _lance_y = rhy if facing > 0 else lhy
        pygame.draw.line(surface, (220, 200, 255),
                         (_lance_x, _lance_y),
                         (_lance_x + int(facing * 18*s), _lance_y - int(5*s)),
                         max(2, int(2*s)))
        pygame.draw.polygon(surface, (255, 240, 255), [
            (_lance_x + int(facing * 18*s), _lance_y - int(5*s)),
            (_lance_x + int(facing * 24*s), _lance_y - int(2*s)),
            (_lance_x + int(facing * 18*s), _lance_y + int(3*s)),
        ])
        # Stealth shimmer particles
        _pbphase = t * 0.09
        for _pbi in range(5):
            _pba = math.radians(_pbi * 72) + _pbphase
            _pbpx = sx + int(math.cos(_pba) * int(14*s))
            _pbpy = (sy + wy)//2 + int(math.sin(_pba) * int(8*s))
            _pbps = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(_pbps, (200, 180, 255, 120), (2, 2), 2)
            surface.blit(_pbps, (_pbpx - 2, _pbpy - 2))
        # Visor stripe on head
        pygame.draw.line(surface, (180, 160, 255), (hx - hd//2, hy), (hx + hd//2, hy), max(1, int(s)))

    elif char_name == "Inferno":
        t = pygame.time.get_ticks()
        # Charred black torso with ember cracks
        pygame.draw.rect(surface, (30, 20, 10),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Lava crack lines
        for _ici, (_icx1, _icy1, _icx2, _icy2) in enumerate([
            (-7, 5, -2, 10), (3, 8, 8, 14), (-5, 15, 2, 22), (4, 3, 9, 9)
        ]):
            pygame.draw.line(surface, (255, 100, 0),
                             (sx + int(_icx1*s), sy + int(_icy1*s)),
                             (sx + int(_icx2*s), sy + int(_icy2*s)),
                             max(1, int(s)))
        # Fire halo above head
        _firehase = t * 0.12
        for _fhi in range(6):
            _fha = math.radians(_fhi * 60) + _firehase
            _fhr = hd + max(2, int(5*s))
            _fhx = hx + int(math.cos(_fha) * _fhr)
            _fhy = hy + int(math.sin(_fha) * _fhr * 0.5) - int(4*s)
            _fhcol = [(255,80,0),(255,140,20),(255,60,0),(255,180,40),(255,100,0),(255,50,0)][_fhi]
            pygame.draw.circle(surface, _fhcol, (_fhx, _fhy), max(2, int(2*s)))
        # Burning fists
        for _hpos in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (255, 120, 0), _hpos, max(3, int(4*s)))
            pygame.draw.circle(surface, (255, 220, 80), _hpos, max(1, int(2*s)))
        # Fire aura ring
        _faring = pygame.Surface((int(50*s), int(40*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(_faring, (255, 60, 0, 30), (0, 0, int(50*s), int(40*s)))
        surface.blit(_faring, (sx - int(25*s), (sy+wy)//2 - int(20*s)))

    elif char_name == "Titan Smash":
        t = pygame.time.get_ticks()
        # Massive dark-iron body
        pygame.draw.rect(surface, (45, 35, 25),
                         (sx - int(16*s), sy, int(32*s), bl), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (90, 70, 50),
                         (sx - int(16*s), sy, int(32*s), bl), max(1, int(2*s)),
                         border_radius=max(2, int(4*s)))
        # Metal plate rivets across chest
        for _rci in range(-12, 14, 6):
            for _rcj in [int(8*s), int(18*s)]:
                pygame.draw.circle(surface, (120, 100, 70), (sx + int(_rci*s), sy + _rcj), max(2, int(2*s)))
        # Giant hammer fists
        for _hfpos, _hfdir in [((lhx, lhy), -1), ((rhx, rhy), 1)]:
            _hfx, _hfy = _hfpos
            # Handle
            pygame.draw.line(surface, (80, 60, 40),
                             (_hfx, _hfy), (_hfx + int(_hfdir * 10*s), _hfy - int(8*s)),
                             max(2, int(3*s)))
            # Hammer head
            pygame.draw.rect(surface, (70, 70, 70),
                             (_hfx + int(_hfdir * 6*s) - int(6*s), _hfy - int(14*s),
                              int(12*s), int(8*s)), border_radius=max(1, int(2*s)))
        # Ground crack indicator
        pygame.draw.ellipse(surface, (60, 40, 20), (wx - int(16*s), wy, int(32*s), int(5*s)))

    elif char_name == "Infiltrator":
        t = pygame.time.get_ticks()
        # Chameleon-shifting body — colour cycles
        _inf_hue = int(t * 0.05) % 360
        _inf_r = int(60 + 40 * math.sin(math.radians(_inf_hue)))
        _inf_g = int(80 + 40 * math.sin(math.radians(_inf_hue + 120)))
        _inf_b = int(60 + 40 * math.sin(math.radians(_inf_hue + 240)))
        _inf_col = (_inf_r, _inf_g, _inf_b)
        pygame.draw.rect(surface, _inf_col,
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Spy utility belt
        pygame.draw.rect(surface, (20, 15, 10),
                         (sx - int(10*s), sy + bl//2, int(20*s), max(2, int(3*s))))
        pygame.draw.circle(surface, (180, 150, 30), (sx, sy + bl//2 + max(1, int(s))), max(2, int(3*s)))
        # Visor + night-vision lenses
        pygame.draw.rect(surface, (10, 10, 10),
                         (hx - hd + max(1, int(s)), hy - max(1, int(2*s)),
                          hd * 2 - max(1, int(2*s)), max(2, int(4*s))),
                         border_radius=max(1, int(s)))
        pygame.draw.circle(surface, (0, 220, 80), (hx - hd//3, hy), max(1, int(2*s)))
        pygame.draw.circle(surface, (0, 220, 80), (hx + hd//3, hy), max(1, int(2*s)))
        # Confuse swirls on fists
        for _cfpos in [(lhx, lhy), (rhx, rhy)]:
            _cfx, _cfy = _cfpos
            pygame.draw.arc(surface, (255, 80, 200),
                            (_cfx - int(4*s), _cfy - int(4*s), int(8*s), int(8*s)),
                            0, math.pi, max(1, int(s)))

    elif char_name == "Executioner":
        t = pygame.time.get_ticks()
        # Midnight-black executioner robe
        pygame.draw.rect(surface, (15, 5, 5),
                         (sx - int(13*s), sy, int(26*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 20, 20),
                         (sx - int(13*s), sy, int(26*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Blood-red X emblem on chest
        _ecx, _ecy = sx, sy + bl//3
        for _edx, _edy in [(-7, -7), (7, -7)]:
            pygame.draw.line(surface, (180, 0, 0),
                             (_ecx + int(_edx*s), _ecy + int(_edy*s)),
                             (_ecx - int(_edx*s), _ecy - int(_edy*s)),
                             max(1, int(2*s)))
        # Hood / cowl around head
        pygame.draw.arc(surface, (15, 5, 5),
                        (hx - hd - max(2, int(3*s)), hy - hd - max(2, int(3*s)),
                         (hd + max(2, int(3*s))) * 2, (hd + max(2, int(3*s))) * 2),
                        0, math.pi * 2, max(2, int(3*s)))
        # Glowing red eyes
        pygame.draw.circle(surface, (255, 0, 0), (hx - hd//3, hy), max(1, int(2*s)))
        pygame.draw.circle(surface, (255, 0, 0), (hx + hd//3, hy), max(1, int(2*s)))
        # Reaper blade (scythe arc) on dominant hand
        _scx = rhx if facing > 0 else lhx
        _scy = rhy if facing > 0 else lhy
        pygame.draw.arc(surface, (60, 60, 60),
                        (_scx + int(facing * 2*s) - int(10*s), _scy - int(14*s),
                         int(20*s), int(20*s)),
                        math.radians(200), math.radians(360), max(2, int(2*s)))
        # Death pulse — red ring that expands when enemy is low
        _dphase = (t % 800) / 800
        _dpsurf = pygame.Surface((int(50*s), int(50*s)), pygame.SRCALPHA)
        _dpalpha = int(140 * (1 - _dphase))
        pygame.draw.circle(_dpsurf, (200, 0, 0, _dpalpha),
                           (int(25*s), int(25*s)), int(_dphase * 22*s), max(1, int(s)))
        surface.blit(_dpsurf, (sx - int(25*s), (sy + wy)//2 - int(25*s)))

    elif char_name == "Coldheart":
        t = pygame.time.get_ticks()
        # Ice-blue armour
        pygame.draw.rect(surface, (100, 160, 210),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 230, 255),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Cracked-ice pattern
        for _icl in [(-6, 6, 0, 16), (3, 4, 8, 18), (-4, 20, 5, 28)]:
            pygame.draw.line(surface, (180, 220, 255),
                             (sx + int(_icl[0]*s), sy + int(_icl[1]*s)),
                             (sx + int(_icl[2]*s), sy + int(_icl[3]*s)),
                             max(1, int(s)))
        # Cold-heart symbol — dark purple heart outline
        _chx, _chy = sx, sy + int(8*s)
        pygame.draw.circle(surface, (120, 0, 80), (_chx - max(2, int(3*s)), _chy - max(1, int(2*s))), max(2, int(3*s)), max(1, int(s)))
        pygame.draw.circle(surface, (120, 0, 80), (_chx + max(2, int(3*s)), _chy - max(1, int(2*s))), max(2, int(3*s)), max(1, int(s)))
        pygame.draw.polygon(surface, (120, 0, 80), [
            (_chx - max(5, int(6*s)), _chy),
            (_chx, _chy + max(5, int(6*s))),
            (_chx + max(5, int(6*s)), _chy),
        ])
        # Drain aura — dark purple seeping tendrils
        _drphase = t * 0.07
        for _dri in range(4):
            _dra = math.radians(_dri * 90) + _drphase
            _drx = sx + int(math.cos(_dra) * int(15*s))
            _dry = (sy + wy)//2 + int(math.sin(_dra) * int(9*s))
            _drsurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(_drsurf, (80, 0, 80, 140), (3, 3), 2)
            surface.blit(_drsurf, (_drx - 3, _dry - 3))
        # Icicle crown
        for _ici in range(-2, 3):
            _icy_tip = hy - hd - max(4, int((8 + abs(_ici) * 3)*s))
            pygame.draw.polygon(surface, (210, 240, 255), [
                (hx + int(_ici * 4*s) - max(1, int(2*s)), hy - hd),
                (hx + int(_ici * 4*s) + max(1, int(2*s)), hy - hd),
                (hx + int(_ici * 4*s), _icy_tip),
            ])

    elif char_name == "Tempest":
        t = pygame.time.get_ticks()
        # Sky-blue body with cloud-puff collar
        pygame.draw.rect(surface, (80, 140, 200),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (180, 220, 255),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(4*s)))
        # Cloud puffs at shoulder
        for _cpi in [-8, -3, 2, 7]:
            pygame.draw.circle(surface, (240, 240, 255),
                               (sx + int(_cpi*s), sy + max(2, int(3*s))),
                               max(2, int(4*s)))
        # Storm bolt on chest
        _sbtpts = [
            (sx + int(facing * 3*s), sy + int(5*s)),
            (sx + int(facing * -1*s), sy + int(12*s)),
            (sx + int(facing * 2*s), sy + int(12*s)),
            (sx + int(facing * -2*s), sy + int(20*s)),
        ]
        pygame.draw.lines(surface, (100, 160, 255), False, _sbtpts, max(1, int(2*s)))
        # Slow-fall feathers — two wing stubs behind arms
        for _fwi, (_fwx, _fwy) in enumerate([(lhx, lhy), (rhx, rhy)]):
            _fwdir = -1 if _fwi == 0 else 1
            pygame.draw.polygon(surface, (200, 225, 255), [
                (_fwx, _fwy),
                (_fwx + int(_fwdir * 8*s), _fwy - int(5*s)),
                (_fwx + int(_fwdir * 10*s), _fwy + int(3*s)),
                (_fwx + int(_fwdir * 4*s), _fwy + int(6*s)),
            ])
        # Teleport flicker dots
        _tphase = t * 0.1
        for _tpi in range(4):
            _tpa = math.radians(_tpi * 90) + _tphase
            _tpx = hx + int(math.cos(_tpa) * (hd + int(4*s)))
            _tpy = hy + int(math.sin(_tpa) * (hd + int(4*s)))
            pygame.draw.circle(surface, (140, 200, 255), (_tpx, _tpy), max(1, int(2*s)))

    elif char_name == "Ancient":
        t = pygame.time.get_ticks()
        # Stone-gold robes with weathered trim
        pygame.draw.polygon(surface, (150, 125, 75), [
            (sx - int(13*s), sy),
            (sx + int(13*s), sy),
            (sx + int(18*s), wy),
            (sx - int(18*s), wy),
        ])
        pygame.draw.polygon(surface, (210, 175, 100), [
            (sx - int(13*s), sy),
            (sx + int(13*s), sy),
            (sx + int(18*s), wy),
            (sx - int(18*s), wy),
        ], max(1, int(s)))
        # Ancient rune marks on robe
        for _ryi in range(3):
            _ry = sy + int((_ryi * 10 + 5)*s)
            pygame.draw.line(surface, (200, 160, 80),
                             (sx - int(6*s), _ry), (sx + int(6*s), _ry), max(1, int(s)))
            pygame.draw.line(surface, (200, 160, 80),
                             (sx, _ry - int(3*s)), (sx, _ry + int(3*s)), max(1, int(s)))
        # Regen aura — soft golden halo
        _asurf = pygame.Surface((int(40*s), int(14*s)), pygame.SRCALPHA)
        _apulse = abs(math.sin(t * 0.002)) * 60
        pygame.draw.ellipse(_asurf, (220, 180, 60, int(40 + _apulse)),
                            (0, 0, int(40*s), int(14*s)))
        surface.blit(_asurf, (hx - int(20*s), hy - hd - int(10*s)))
        # Status-immune glow — white outline
        pygame.draw.circle(surface, (255, 250, 230), (hx, hy), hd, max(1, int(s)))
        # Long beard lines
        for _bli in range(-3, 4):
            _blen = max(6, int((18 - abs(_bli) * 4)*s))
            pygame.draw.line(surface, (220, 200, 150),
                             (hx + int(_bli * 2*s), hy + hd),
                             (hx + int(_bli * 2*s) + int(_bli * s), hy + hd + _blen),
                             max(1, int(s)))

    elif char_name == "Berserk Lord":
        t = pygame.time.get_ticks()
        # Blood-red torn vest
        pygame.draw.rect(surface, (140, 15, 10),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(1, int(2*s)))
        # Torn zigzag edges
        _tear_pts = []
        for _ti in range(7):
            _tx = sx - int(12*s) + int(_ti * 4*s)
            _ty = sy + bl + (0 if _ti % 2 == 0 else int(5*s))
            _tear_pts.append((_tx, _ty))
        if len(_tear_pts) >= 2:
            pygame.draw.lines(surface, (80, 5, 5), False, _tear_pts, max(1, int(2*s)))
        # Rage veins on arms and torso
        _rphase = t * 0.05
        for _rvi in range(4):
            _rva = math.radians(_rvi * 90 + _rphase * 30)
            _rvx = sx + int(math.cos(_rva) * int(9*s))
            _rvy = (sy + wy)//2 + int(math.sin(_rva) * int(6*s))
            pygame.draw.circle(surface, (255, 40, 40), (_rvx, _rvy), max(1, int(s)))
        # Wild spiky hair
        for _shi in range(-3, 4):
            _shang = math.radians(-90 + _shi * 20)
            _shlen = max(8, int((14 - abs(_shi) * 2)*s))
            pygame.draw.line(surface, (40, 10, 10),
                             (hx + int(math.cos(_shang) * hd),
                              hy + int(math.sin(_shang) * hd)),
                             (hx + int(math.cos(_shang) * (hd + _shlen)),
                              hy + int(math.sin(_shang) * (hd + _shlen))),
                             max(1, int(2*s)))
        # Bulging enraged eyes
        pygame.draw.circle(surface, (255, 60, 0), (hx - hd//3, hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (255, 60, 0), (hx + hd//3, hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (255, 255, 255), (hx - hd//3, hy), max(1, int(s)))
        pygame.draw.circle(surface, (255, 255, 255), (hx + hd//3, hy), max(1, int(s)))
        # Regen glow — pulsing green ring
        _rgphase = abs(math.sin(t * 0.003))
        _rgsurf = pygame.Surface((int(30*s), int(30*s)), pygame.SRCALPHA)
        pygame.draw.circle(_rgsurf, (40, 200, 60, int(80 * _rgphase)),
                           (int(15*s), int(15*s)), int(13*s), max(1, int(2*s)))
        surface.blit(_rgsurf, (sx - int(15*s), (sy + wy)//2 - int(15*s)))

    elif char_name == "Shadow Dancer":
        t = pygame.time.get_ticks()
        # Deep shadow-purple leotard
        pygame.draw.rect(surface, (20, 10, 40),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 50, 120),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Speed trails — fading copies of the torso
        for _sti in range(1, 4):
            _stsurf = pygame.Surface((int(22*s), bl), pygame.SRCALPHA)
            pygame.draw.rect(_stsurf, (60, 30, 100, 60 - _sti * 15),
                             (0, 0, int(22*s), bl), border_radius=max(1, int(2*s)))
            surface.blit(_stsurf, (sx - int(11*s) - int(_sti * facing * 5*s), sy))
        # Stealth shimmer particles
        _sdphase = t * 0.09
        for _sdi in range(5):
            _sda = math.radians(_sdi * 72) + _sdphase
            _sdx = sx + int(math.cos(_sda) * int(13*s))
            _sdy = (sy + wy)//2 + int(math.sin(_sda) * int(8*s))
            _sdsurf = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(_sdsurf, (140, 80, 200, 130), (2, 2), 2)
            surface.blit(_sdsurf, (_sdx - 2, _sdy - 2))
        # Blade edge on hands
        for _sdh in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (100, 60, 180), _sdh, max(3, int(4*s)))
        # Mask — black face slash
        pygame.draw.line(surface, (5, 0, 20),
                         (hx - hd//2, hy - max(1, int(2*s))),
                         (hx + hd//2, hy + max(1, int(2*s))),
                         max(2, int(2*s)))

    elif char_name == "Voodoo":
        t = pygame.time.get_ticks()
        # Dark purple hooded robe
        pygame.draw.polygon(surface, (60, 0, 100), [
            (sx - int(12*s), sy),
            (sx + int(12*s), sy),
            (sx + int(16*s), wy),
            (sx - int(16*s), wy),
        ])
        pygame.draw.polygon(surface, (120, 30, 180), [
            (sx - int(12*s), sy),
            (sx + int(12*s), sy),
            (sx + int(16*s), wy),
            (sx - int(16*s), wy),
        ], max(1, int(s)))
        # Voodoo doll icon on chest
        _vdx, _vdy = sx, sy + int(8*s)
        pygame.draw.circle(surface, (200, 160, 100), (_vdx, _vdy), max(3, int(3*s)))
        pygame.draw.line(surface, (200, 160, 100),
                         (_vdx, _vdy + max(3, int(3*s))),
                         (_vdx, _vdy + max(8, int(8*s))), max(1, int(s)))
        pygame.draw.line(surface, (200, 160, 100),
                         (_vdx - max(3, int(3*s)), _vdy + max(4, int(4*s))),
                         (_vdx + max(3, int(3*s)), _vdy + max(4, int(4*s))), max(1, int(s)))
        # Reflect pins — bright needles radiating out
        _vphase = t * 0.06
        for _vpi in range(6):
            _vpa = math.radians(_vpi * 60) + _vphase
            _vplen = max(8, int(12*s))
            _vpx1 = sx + int(math.cos(_vpa) * int(10*s))
            _vpy1 = (sy + wy)//2 + int(math.sin(_vpa) * int(7*s))
            _vpx2 = sx + int(math.cos(_vpa) * (_vplen + int(10*s)))
            _vpy2 = (sy + wy)//2 + int(math.sin(_vpa) * (_vplen//2 + int(7*s)))
            pygame.draw.line(surface, (200, 100, 255), (_vpx1, _vpy1), (_vpx2, _vpy2), max(1, int(s)))
        # Glowing purple eyes under hood
        pygame.draw.circle(surface, (200, 80, 255), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (200, 80, 255), (hx + hd//3, hy), max(2, int(2*s)))
        # Reflect pulse
        _rpsurf = pygame.Surface((int(44*s), int(44*s)), pygame.SRCALPHA)
        _rpphase = (t % 1200) / 1200
        _rpalpha = int(120 * (1 - _rpphase))
        pygame.draw.circle(_rpsurf, (160, 40, 220, _rpalpha),
                           (int(22*s), int(22*s)), int(_rpphase * 20*s), max(1, int(s)))
        surface.blit(_rpsurf, (sx - int(22*s), (sy + wy)//2 - int(22*s)))

    elif char_name == "Magma":
        t = pygame.time.get_ticks()
        # Charred dark-red stone body
        pygame.draw.rect(surface, (80, 25, 10),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (160, 60, 20),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(2*s)),
                         border_radius=max(2, int(4*s)))
        # Lava glowing cracks across the body
        for _lci, (_lx1, _ly1, _lx2, _ly2) in enumerate([
            (-8, 4,  -2, 12), (3,  7,  9,  18), (-5, 16,  4, 26),
            ( 5, 3,  10,  9), (-3, 22, -9, 30),
        ]):
            _lglow = (220 + _lci * 6, 80 - _lci * 10, 0)
            pygame.draw.line(surface, _lglow,
                             (sx + int(_lx1*s), sy + int(_ly1*s)),
                             (sx + int(_lx2*s), sy + int(_ly2*s)),
                             max(1, int(s)))
        # Dripping lava from fists
        for _lhpos in [(lhx, lhy), (rhx, rhy)]:
            _lhx2, _lhy2 = _lhpos
            pygame.draw.circle(surface, (255, 100, 0), _lhpos, max(4, int(4*s)))
            pygame.draw.circle(surface, (255, 210, 50), _lhpos, max(2, int(2*s)))
            # Drip drop
            pygame.draw.ellipse(surface, (255, 80, 0),
                                (_lhx2 - max(1, int(2*s)), _lhy2 + max(3, int(3*s)),
                                 max(2, int(4*s)), max(3, int(5*s))))
        # Magma aura pulsing ring
        _maphase = abs(math.sin(t * 0.003))
        _masurf = pygame.Surface((int(40*s), int(40*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(_masurf, (255, 60, 0, int(50 + 40 * _maphase)),
                            (0, 0, int(40*s), int(40*s)), max(1, int(2*s)))
        surface.blit(_masurf, (sx - int(20*s), (sy + wy)//2 - int(20*s)))
        # Stone-cracked head
        pygame.draw.line(surface, (200, 80, 20),
                         (hx - hd//2, hy - hd//3),
                         (hx, hy + hd//3), max(1, int(s)))
        pygame.draw.circle(surface, (255, 120, 0), (hx, hy), max(2, int(2*s)))

    elif char_name == "Minotaur":
        t = pygame.time.get_ticks()
        # Heavy dark-brown bull hide body
        pygame.draw.rect(surface, (70, 40, 15),
                         (sx - int(16*s), sy, int(32*s), bl), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (120, 75, 30),
                         (sx - int(16*s), sy, int(32*s), bl), max(1, int(2*s)),
                         border_radius=max(2, int(4*s)))
        # Bull horns on head
        for _hdir in [-1, 1]:
            pygame.draw.polygon(surface, (220, 200, 140), [
                (hx + int(_hdir * hd * 0.6), hy - hd//2),
                (hx + int(_hdir * (hd + max(6, int(8*s)))), hy - hd - max(6, int(7*s))),
                (hx + int(_hdir * (hd + max(2, int(3*s)))), hy - hd//3),
            ])
        # Snout — wide dark ellipse below head centre
        pygame.draw.ellipse(surface, (90, 55, 20),
                            (hx - max(5, int(6*s)), hy + max(1, int(2*s)),
                             max(10, int(12*s)), max(5, int(7*s))))
        pygame.draw.circle(surface, (50, 30, 10), (hx - max(2, int(3*s)), hy + max(3, int(4*s))), max(1, int(2*s)))
        pygame.draw.circle(surface, (50, 30, 10), (hx + max(2, int(3*s)), hy + max(3, int(4*s))), max(1, int(2*s)))
        # Hammer fists — large chunky rectangles
        for _mfh, _mfd in [((lhx, lhy), -1), ((rhx, rhy), 1)]:
            _mfx, _mfy = _mfh
            pygame.draw.rect(surface, (60, 35, 10),
                             (_mfx - max(5, int(6*s)), _mfy - max(4, int(5*s)),
                              max(12, int(12*s)), max(10, int(10*s))),
                             border_radius=max(1, int(2*s)))
        # Rage breath — steam puffs from nostrils
        _mbphase = (t % 600) / 600
        for _mbi in range(2):
            _mbsurf = pygame.Surface((16, 16), pygame.SRCALPHA)
            _mbalpha = int(80 * (1 - _mbphase))
            pygame.draw.circle(_mbsurf, (255, 255, 255, _mbalpha), (8, 8), int(4 + _mbphase * 4))
            _mboff = _mbi * max(6, int(6*s)) - max(3, int(3*s))
            surface.blit(_mbsurf, (hx + _mboff - 8, hy + hd - 8 - int(_mbphase * 10*s)))

    elif char_name == "Puppet Master":
        t = pygame.time.get_ticks()
        # Tan puppet-master coat
        pygame.draw.rect(surface, (160, 130, 80),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (210, 180, 110),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Puppet strings hanging from hands
        for _pmh in [(lhx, lhy), (rhx, rhy)]:
            _pmx, _pmy = _pmh
            for _pms in range(3):
                _pmsy = _pmy + max(6, int((6 + _pms * 5)*s))
                pygame.draw.line(surface, (200, 180, 130), (_pmx, _pmy), (_pmx + _pms - 1, _pmsy), max(1, int(s)))
        # Control crossbar above head
        _cbw = max(14, int(18*s))
        pygame.draw.line(surface, (140, 110, 60),
                         (hx - _cbw, hy - hd - max(8, int(8*s))),
                         (hx + _cbw, hy - hd - max(8, int(8*s))),
                         max(2, int(2*s)))
        pygame.draw.line(surface, (140, 110, 60),
                         (hx, hy - hd - max(8, int(8*s))),
                         (hx, hy - hd - max(2, int(2*s))),
                         max(1, int(s)))
        # Monocle eye
        pygame.draw.circle(surface, (200, 180, 100), (hx + hd//3, hy), max(3, int(4*s)), max(1, int(s)))
        # Confuse swirls on hands
        for _pmhp in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.arc(surface, (255, 80, 200),
                            (_pmhp[0] - max(4, int(4*s)), _pmhp[1] - max(4, int(4*s)),
                             max(8, int(8*s)), max(8, int(8*s))),
                            0, math.pi, max(1, int(s)))

    elif char_name == "Clockwork":
        t = pygame.time.get_ticks()
        # Brass clockwork body
        pygame.draw.rect(surface, (140, 110, 40),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 170, 80),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Gear on chest — spinning
        _gcx, _gcy = sx, sy + bl//3
        _gphase = t * 0.003
        _gr = max(7, int(8*s))
        pygame.draw.circle(surface, (180, 150, 60), (_gcx, _gcy), _gr)
        pygame.draw.circle(surface, (100, 80, 30), (_gcx, _gcy), max(3, int(3*s)))
        for _gti in range(8):
            _gta = math.radians(_gti * 45) + _gphase
            _gtx1 = _gcx + int(math.cos(_gta) * _gr)
            _gty1 = _gcy + int(math.sin(_gta) * _gr)
            _gtx2 = _gcx + int(math.cos(_gta) * (_gr + max(3, int(3*s))))
            _gty2 = _gcy + int(math.sin(_gta) * (_gr + max(3, int(3*s))))
            pygame.draw.line(surface, (200, 170, 80), (_gtx1, _gty1), (_gtx2, _gty2), max(2, int(2*s)))
        # Clock-face eyes
        pygame.draw.circle(surface, (230, 210, 140), (hx - hd//3, hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (230, 210, 140), (hx + hd//3, hy), max(3, int(3*s)))
        # Clock hands on each eye
        for _cex, _cey in [(hx - hd//3, hy), (hx + hd//3, hy)]:
            _ceha = math.radians(-90 + t * 0.5)
            pygame.draw.line(surface, (60, 40, 10),
                             (_cex, _cey),
                             (_cex + int(math.cos(_ceha) * max(2, int(2*s))),
                              _cey + int(math.sin(_ceha) * max(2, int(2*s)))),
                             max(1, int(s)))
        # Time-freeze shimmer ring
        _tfsurf = pygame.Surface((int(44*s), int(44*s)), pygame.SRCALPHA)
        _tfphase = abs(math.sin(t * 0.002))
        pygame.draw.circle(_tfsurf, (200, 180, 80, int(60 * _tfphase)),
                           (int(22*s), int(22*s)), int(20*s), max(1, int(2*s)))
        surface.blit(_tfsurf, (sx - int(22*s), (sy + wy)//2 - int(22*s)))

    elif char_name == "Void Walker":
        t = pygame.time.get_ticks()
        # Deep void-purple body — semi-translucent
        _vwsurf = pygame.Surface((int(26*s), bl), pygame.SRCALPHA)
        pygame.draw.rect(_vwsurf, (20, 0, 40, 200),
                         (0, 0, int(26*s), bl), border_radius=max(2, int(3*s)))
        surface.blit(_vwsurf, (sx - int(13*s), sy))
        pygame.draw.rect(surface, (80, 20, 120),
                         (sx - int(13*s), sy, int(26*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Void particles swirling inward
        _vphase = t * 0.07
        for _vwi in range(6):
            _vwa = math.radians(_vwi * 60) + _vphase
            _vwr = max(10, int((16 - (_vphase * 3 % 8))*s))
            _vwx = sx + int(math.cos(_vwa) * _vwr)
            _vwy = (sy + wy)//2 + int(math.sin(_vwa) * _vwr * 0.5)
            _vwps = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(_vwps, (140, 0, 200, 160), (3, 3), 2)
            surface.blit(_vwps, (_vwx - 3, _vwy - 3))
        # Hollow void eyes
        pygame.draw.circle(surface, (0, 0, 0), (hx - hd//3, hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (0, 0, 0), (hx + hd//3, hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (100, 0, 160), (hx - hd//3, hy), max(1, int(s)))
        pygame.draw.circle(surface, (100, 0, 160), (hx + hd//3, hy), max(1, int(s)))
        # Drain tendrils
        _dtphase = t * 0.05
        for _dti in range(3):
            _dta = math.radians(_dti * 120) + _dtphase
            pygame.draw.line(surface, (60, 0, 90),
                             (sx, (sy + wy)//2),
                             (sx + int(math.cos(_dta) * int(18*s)),
                              (sy + wy)//2 + int(math.sin(_dta) * int(10*s))),
                             max(1, int(s)))

    elif char_name == "Lich":
        t = pygame.time.get_ticks()
        # Dark plum robe
        pygame.draw.polygon(surface, (40, 20, 60), [
            (sx - int(12*s), sy),
            (sx + int(12*s), sy),
            (sx + int(18*s), wy),
            (sx - int(18*s), wy),
        ])
        pygame.draw.polygon(surface, (90, 50, 120), [
            (sx - int(12*s), sy),
            (sx + int(12*s), sy),
            (sx + int(18*s), wy),
            (sx - int(18*s), wy),
        ], max(1, int(s)))
        # Skull staff in dominant hand
        _nskx = rhx if facing > 0 else lhx
        _nsky = rhy if facing > 0 else lhy
        pygame.draw.line(surface, (140, 110, 80),
                         (_nskx, _nsky), (_nskx + int(facing * 4*s), _nsky - int(16*s)),
                         max(2, int(2*s)))
        _sktop = (_nskx + int(facing * 4*s), _nsky - int(22*s))
        pygame.draw.circle(surface, (220, 210, 190), _sktop, max(4, int(4*s)))
        pygame.draw.circle(surface, (40, 20, 60), (_sktop[0] - max(1, int(2*s)), _sktop[1]), max(1, int(s)))
        pygame.draw.circle(surface, (40, 20, 60), (_sktop[0] + max(1, int(2*s)), _sktop[1]), max(1, int(s)))
        # Soul wisps floating up
        _swphase = t * 0.06
        for _swi in range(3):
            _swa = math.radians(_swi * 120) + _swphase
            _swx = sx + int(math.cos(_swa) * int(12*s))
            _swy = sy - max(4, int(4*s)) + int(math.sin(_swphase + _swi) * int(4*s))
            _swsurf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(_swsurf, (80, 200, 100, 140), (4, 4), 3)
            surface.blit(_swsurf, (_swx - 4, _swy - 4))
        # Glowing green eyes
        pygame.draw.circle(surface, (60, 230, 80), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (60, 230, 80), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Crimson":
        t = pygame.time.get_ticks()
        # Blood-red bodysuit with speed-trail streaks
        pygame.draw.rect(surface, (160, 10, 20),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (220, 60, 50),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Speed streaks behind body (intensity suggests desperation)
        for _csi in range(1, 5):
            _cssurf = pygame.Surface((int(22*s), bl), pygame.SRCALPHA)
            pygame.draw.rect(_cssurf, (220, 40, 40, 40 - _csi * 8),
                             (0, 0, int(22*s), bl), border_radius=max(1, int(2*s)))
            surface.blit(_cssurf, (sx - int(11*s) - int(facing * _csi * 6*s), sy))
        # Cracked adrenaline veins
        for _cvi, (_cvx1, _cvy1, _cvx2, _cvy2) in enumerate([(-4, 4, -9, 12), (4, 6, 9, 14), (-2, 18, -7, 26)]):
            pygame.draw.line(surface, (255, 80, 80),
                             (sx + int(_cvx1*s), sy + int(_cvy1*s)),
                             (sx + int(_cvx2*s), sy + int(_cvy2*s)), max(1, int(s)))
        # Wild wide eyes
        pygame.draw.circle(surface, (255, 50, 50), (hx - hd//3, hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (255, 50, 50), (hx + hd//3, hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (255, 220, 220), (hx - hd//3, hy), max(1, int(s)))
        pygame.draw.circle(surface, (255, 220, 220), (hx + hd//3, hy), max(1, int(s)))

    elif char_name == "Jester":
        t = pygame.time.get_ticks()
        # Jester motley — pink/yellow alternating diamonds (simplified as half-and-half)
        pygame.draw.rect(surface, (220, 60, 160),
                         (sx - int(11*s), sy, int(11*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (240, 220, 40),
                         (sx, sy, int(11*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 40, 140),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Jester bells on collar
        for _jbx in [sx - max(5, int(6*s)), sx, sx + max(5, int(6*s))]:
            pygame.draw.circle(surface, (255, 220, 50), (_jbx, sy + max(3, int(4*s))), max(3, int(3*s)))
            pygame.draw.circle(surface, (160, 140, 20), (_jbx, sy + max(3, int(4*s)) + max(2, int(2*s))), max(1, int(s)))
        # Jester hat with two points
        pygame.draw.polygon(surface, (220, 60, 160), [
            (hx - hd, hy - hd),
            (hx, hy - hd),
            (hx - max(5, int(7*s)), hy - hd - max(14, int(16*s))),
        ])
        pygame.draw.polygon(surface, (240, 220, 40), [
            (hx, hy - hd),
            (hx + hd, hy - hd),
            (hx + max(5, int(7*s)), hy - hd - max(14, int(16*s))),
        ])
        # Bell at each hat tip
        pygame.draw.circle(surface, (255, 220, 50),
                           (hx - max(5, int(7*s)), hy - hd - max(14, int(16*s))), max(3, int(3*s)))
        pygame.draw.circle(surface, (255, 220, 50),
                           (hx + max(5, int(7*s)), hy - hd - max(14, int(16*s))), max(3, int(3*s)))
        # Chaos swirl around body
        _jphase = t * 0.08
        for _ji in range(6):
            _ja = math.radians(_ji * 60) + _jphase
            _jsurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            _jcols = [(255,80,180),(255,220,40),(80,200,255),(255,120,40),(120,255,80),(200,80,255)]
            pygame.draw.circle(_jsurf, (*_jcols[_ji], 180), (3, 3), 2)
            surface.blit(_jsurf,
                         (sx + int(math.cos(_ja) * int(15*s)) - 3,
                          (sy + wy)//2 + int(math.sin(_ja) * int(9*s)) - 3))

    elif char_name == "Golem":
        t = pygame.time.get_ticks()
        # Rough stone-grey block body
        pygame.draw.rect(surface, (90, 85, 75),
                         (sx - int(15*s), sy, int(30*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (140, 130, 115),
                         (sx - int(15*s), sy, int(30*s), bl), max(2, int(2*s)),
                         border_radius=max(1, int(2*s)))
        # Stone texture cracks
        for _gcl in [(-8, 3, -3, 11), (4, 7, 9, 16), (-6, 18, 1, 27), (5, 1, 10, 6)]:
            pygame.draw.line(surface, (60, 55, 45),
                             (sx + int(_gcl[0]*s), sy + int(_gcl[1]*s)),
                             (sx + int(_gcl[2]*s), sy + int(_gcl[3]*s)), max(1, int(s)))
        # Iron fists — dark heavy rectangles
        for _gfh, _gfd in [((lhx, lhy), -1), ((rhx, rhy), 1)]:
            _gfx, _gfy = _gfh
            pygame.draw.rect(surface, (50, 50, 50),
                             (_gfx - max(5, int(6*s)), _gfy - max(4, int(5*s)),
                              max(12, int(12*s)), max(10, int(10*s))),
                             border_radius=max(1, int(s)))
            pygame.draw.rect(surface, (80, 80, 80),
                             (_gfx - max(5, int(6*s)), _gfy - max(4, int(5*s)),
                              max(12, int(12*s)), max(10, int(10*s))),
                             max(1, int(s)), border_radius=max(1, int(s)))
        # Glowing core on chest
        _gcsurf = pygame.Surface((int(14*s), int(14*s)), pygame.SRCALPHA)
        _gcpulse = abs(math.sin(t * 0.002))
        pygame.draw.circle(_gcsurf, (80, 200, 100, int(100 + 80 * _gcpulse)),
                           (int(7*s), int(7*s)), int(6*s))
        surface.blit(_gcsurf, (sx - int(7*s), sy + bl//2 - int(7*s)))
        # Square rock head
        pygame.draw.rect(surface, (90, 85, 75),
                         (hx - hd, hy - hd, hd * 2, hd * 2))
        pygame.draw.rect(surface, (140, 130, 115),
                         (hx - hd, hy - hd, hd * 2, hd * 2), max(1, int(s)))
        pygame.draw.rect(surface, (50, 50, 50), (hx - hd//2, hy - max(1, int(2*s)), hd, max(3, int(4*s))))

    elif char_name == "Blaze":
        t = pygame.time.get_ticks()
        # Bright orange suit with fire patterns
        pygame.draw.rect(surface, (190, 80, 0),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (255, 140, 20),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Fire streaks on torso
        for _bfi, (_bfx1, _bfy1, _bfx2, _bfy2) in enumerate([
            (-5, 8, -2, 18), (3, 5, 7, 16), (-3, 22, 2, 30)
        ]):
            pygame.draw.line(surface, (255, 60 + _bfi * 20, 0),
                             (sx + int(_bfx1*s), sy + int(_bfy1*s)),
                             (sx + int(_bfx2*s), sy + int(_bfy2*s)), max(1, int(s)))
        # Fire crown
        _bfphase = t * 0.1
        for _bci in range(5):
            _bca = math.radians(-90 + (_bci - 2) * 22) + math.sin(_bfphase + _bci) * 0.2
            _bclen = max(6, int((10 + (_bci % 3) * 4)*s))
            pygame.draw.line(surface, (255, max(0, 140 - _bci * 20), 0),
                             (hx + int(math.cos(_bca) * hd),
                              hy + int(math.sin(_bca) * hd)),
                             (hx + int(math.cos(_bca) * (hd + _bclen)),
                              hy + int(math.sin(_bca) * (hd + _bclen))),
                             max(2, int(2*s)))
        # Fiery eyes
        pygame.draw.circle(surface, (255, 200, 0), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (255, 200, 0), (hx + hd//3, hy), max(2, int(2*s)))
        # Fire aura
        _basurf = pygame.Surface((int(46*s), int(36*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(_basurf, (255, 80, 0, 35), (0, 0, int(46*s), int(36*s)))
        surface.blit(_basurf, (sx - int(23*s), (sy + wy)//2 - int(18*s)))

    elif char_name == "Surge":
        t = pygame.time.get_ticks()
        # Electric teal bodysuit
        pygame.draw.rect(surface, (20, 150, 170),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 220, 240),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Combo counter rings — concentric circles on chest
        _ccx, _ccy = sx, sy + bl//3
        for _ccr in range(1, 4):
            _ccsurf = pygame.Surface((int(_ccr * 14*s), int(_ccr * 14*s)), pygame.SRCALPHA)
            _ccalpha = 100 - _ccr * 25
            pygame.draw.circle(_ccsurf, (80, 240, 255, _ccalpha),
                               (int(_ccr * 7*s), int(_ccr * 7*s)), int(_ccr * 7*s), max(1, int(s)))
            surface.blit(_ccsurf, (_ccx - int(_ccr * 7*s), _ccy - int(_ccr * 7*s)))
        # Lightning bolt on chest
        _slpts = [
            (sx + int(facing * 3*s), sy + int(4*s)),
            (sx + int(facing * -1*s), sy + int(12*s)),
            (sx + int(facing * 2*s), sy + int(12*s)),
            (sx + int(facing * -2*s), sy + int(22*s)),
        ]
        pygame.draw.lines(surface, (60, 230, 255), False, _slpts, max(2, int(2*s)))
        # Spark on each fist
        for _sfh in [(lhx, lhy), (rhx, rhy)]:
            _sfx, _sfy = _sfh
            pygame.draw.circle(surface, (60, 230, 255), _sfh, max(3, int(4*s)))
            for _ssi in range(4):
                _ssa = math.radians(_ssi * 90 + t * 0.2)
                pygame.draw.line(surface, (160, 250, 255),
                                 (_sfx, _sfy),
                                 (_sfx + int(math.cos(_ssa) * max(4, int(5*s))),
                                  _sfy + int(math.sin(_ssa) * max(4, int(5*s)))),
                                 max(1, int(s)))

    elif char_name == "Phantom King":
        t = pygame.time.get_ticks()
        # Near-invisible dark void body (shade mechanic)
        _pksurf = pygame.Surface((int(28*s), bl), pygame.SRCALPHA)
        pygame.draw.rect(_pksurf, (40, 10, 70, 60),
                         (0, 0, int(28*s), bl), border_radius=max(2, int(3*s)))
        surface.blit(_pksurf, (sx - int(14*s), sy))
        pygame.draw.rect(surface, (120, 60, 180),
                         (sx - int(14*s), sy, int(28*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Crown — sharp points
        _pkbase = hy - hd - max(2, int(2*s))
        for _pki, _pkh in enumerate([10, 16, 22, 16, 10]):
            _pkx = hx - hd + int(_pki * hd * 0.5)
            pygame.draw.polygon(surface, (180, 120, 255), [
                (_pkx - max(3, int(3*s)), _pkbase),
                (_pkx + max(3, int(3*s)), _pkbase),
                (_pkx, _pkbase - max(4, int(_pkh * s))),
            ])
        # Phase shimmer particles
        _pkphase = t * 0.08
        for _pkpi in range(7):
            _pkpa = math.radians(_pkpi * 51) + _pkphase
            _pkpsurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(_pkpsurf, (160, 80, 255, 120), (3, 3), 2)
            surface.blit(_pkpsurf,
                         (sx + int(math.cos(_pkpa) * int(16*s)) - 3,
                          (sy + wy)//2 + int(math.sin(_pkpa) * int(9*s)) - 3))
        # Glowing siphon tendrils from hands
        for _pkhpos in [(lhx, lhy), (rhx, rhy)]:
            _pktsurf = pygame.Surface((int(20*s), int(20*s)), pygame.SRCALPHA)
            pygame.draw.circle(_pktsurf, (120, 0, 200, 100),
                               (int(10*s), int(10*s)), int(8*s))
            surface.blit(_pktsurf, (_pkhpos[0] - int(10*s), _pkhpos[1] - int(10*s)))
        # Piercing violet eyes
        pygame.draw.circle(surface, (200, 100, 255), (hx - hd//3, hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (200, 100, 255), (hx + hd//3, hy), max(2, int(3*s)))

    elif char_name == "Abomination":
        t = pygame.time.get_ticks()
        # Massive bloated green-grey body
        pygame.draw.rect(surface, (55, 100, 30),
                         (sx - int(17*s), sy, int(34*s), bl), border_radius=max(2, int(5*s)))
        pygame.draw.rect(surface, (100, 160, 50),
                         (sx - int(17*s), sy, int(34*s), bl), max(1, int(2*s)),
                         border_radius=max(2, int(5*s)))
        # Toxic pustule spots
        for _apspot in [(-8, 6), (6, 10), (-4, 20), (9, 3), (2, 28)]:
            pygame.draw.circle(surface, (140, 200, 60),
                               (sx + int(_apspot[0]*s), sy + int(_apspot[1]*s)),
                               max(3, int(3*s)))
            pygame.draw.circle(surface, (180, 240, 100),
                               (sx + int(_apspot[0]*s), sy + int(_apspot[1]*s)),
                               max(1, int(s)))
        # Toxic aura bubbles
        _aophase = t * 0.06
        for _aoi in range(5):
            _aoa = math.radians(_aoi * 72) + _aophase
            _aosurf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(_aosurf, (120, 220, 40, 120), (5, 5), 4)
            surface.blit(_aosurf,
                         (sx + int(math.cos(_aoa) * int(20*s)) - 5,
                          (sy + wy)//2 + int(math.sin(_aoa) * int(12*s)) - 5))
        # Drooling maw
        pygame.draw.ellipse(surface, (30, 60, 10),
                            (hx - hd//2, hy + max(2, int(3*s)),
                             hd, max(5, int(6*s))))
        # Tiny enraged eyes
        pygame.draw.circle(surface, (255, 60, 0), (hx - hd//3, hy - max(1, int(2*s))), max(2, int(2*s)))
        pygame.draw.circle(surface, (255, 60, 0), (hx + hd//3, hy - max(1, int(2*s))), max(2, int(2*s)))

    elif char_name == "Witch":
        t = pygame.time.get_ticks()
        # Dark purple witch's dress
        pygame.draw.polygon(surface, (70, 20, 110), [
            (sx - int(10*s), sy),
            (sx + int(10*s), sy),
            (sx + int(18*s), wy),
            (sx - int(18*s), wy),
        ])
        pygame.draw.polygon(surface, (130, 60, 180), [
            (sx - int(10*s), sy),
            (sx + int(10*s), sy),
            (sx + int(18*s), wy),
            (sx - int(18*s), wy),
        ], max(1, int(s)))
        # Tall pointed witch hat
        _whbase = hy - hd
        pygame.draw.polygon(surface, (30, 10, 50), [
            (hx - hd - max(2, int(2*s)), _whbase),
            (hx + hd + max(2, int(2*s)), _whbase),
            (hx, _whbase - max(22, int(26*s))),
        ])
        pygame.draw.ellipse(surface, (30, 10, 50),
                            (hx - hd - max(4, int(4*s)), _whbase - max(4, int(4*s)),
                             (hd + max(4, int(4*s))) * 2, max(8, int(8*s))))
        # Stars on hat
        for _wsi, (_wsx, _wsy) in enumerate([(0, -8), (-5, -14), (5, -18)]):
            pygame.draw.circle(surface, (255, 220, 80),
                               (hx + int(_wsx*s), _whbase + int(_wsy*s)), max(2, int(2*s)))
        # Magic orb in hand
        _wmh = rhx if facing > 0 else lhx
        _wmhy = rhy if facing > 0 else lhy
        _wmorb = pygame.Surface((int(12*s), int(12*s)), pygame.SRCALPHA)
        _wmphase = abs(math.sin(t * 0.004))
        pygame.draw.circle(_wmorb, (180, 80, 255, int(160 + 60 * _wmphase)),
                           (int(6*s), int(6*s)), int(5*s))
        surface.blit(_wmorb, (_wmh - int(6*s), _wmhy - int(6*s)))
        # Chaos swirl orbiting body
        _wcphase = t * 0.07
        for _wci in range(4):
            _wca = math.radians(_wci * 90) + _wcphase
            _wcsurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(_wcsurf, (200, 100, 255, 150), (3, 3), 2)
            surface.blit(_wcsurf,
                         (sx + int(math.cos(_wca) * int(15*s)) - 3,
                          (sy + wy)//2 + int(math.sin(_wca) * int(9*s)) - 3))
        # Green glowing eyes
        pygame.draw.circle(surface, (80, 240, 80), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (80, 240, 80), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Giant Killer":
        t = pygame.time.get_ticks()
        # Teal agile armour
        pygame.draw.rect(surface, (40, 130, 160),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 200, 230),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Giant-slayer lance on back
        pygame.draw.line(surface, (160, 180, 200),
                         (sx - int(facing * 10*s), sy + int(3*s)),
                         (sx + int(facing * 18*s), sy + bl - int(3*s)), max(3, int(3*s)))
        pygame.draw.polygon(surface, (200, 220, 240), [
            (sx + int(facing * 18*s), sy + bl - int(3*s)),
            (sx + int(facing * 24*s), sy + bl - int(6*s)),
            (sx + int(facing * 19*s), sy + bl + int(2*s)),
        ])
        # Crit sparks on fists
        for _gkh in [(lhx, lhy), (rhx, rhy)]:
            _gksurf = pygame.Surface((int(14*s), int(14*s)), pygame.SRCALPHA)
            pygame.draw.circle(_gksurf, (255, 215, 0, 160), (int(7*s), int(7*s)), int(6*s))
            surface.blit(_gksurf, (_gkh[0] - int(7*s), _gkh[1] - int(7*s)))
        # Scale indicator on chest
        pygame.draw.line(surface, (80, 200, 230),
                         (sx - int(6*s), sy + int(8*s)), (sx + int(6*s), sy + int(8*s)), max(1, int(s)))
        for _gks in range(3):
            _gkx = sx - int(6*s) + _gks * max(3, int(6*s))
            pygame.draw.line(surface, (80, 200, 230),
                             (_gkx, sy + int(6*s)), (_gkx, sy + int(12*s)), max(1, int(s)))

    elif char_name == "Speed Demon":
        t = pygame.time.get_ticks()
        # Flame-orange speed suit
        pygame.draw.rect(surface, (200, 100, 0),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (255, 160, 20),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Speed stack trails — growing number of streaks
        for _sdi in range(5):
            _sdsurf = pygame.Surface((int(22*s), bl), pygame.SRCALPHA)
            pygame.draw.rect(_sdsurf, (255, 120, 0, 30 - _sdi * 5),
                             (0, 0, int(22*s), bl), border_radius=max(1, int(2*s)))
            surface.blit(_sdsurf, (sx - int(11*s) - int(facing * _sdi * 8*s), sy))
        # Lightning bolt chest mark
        _sdpts = [
            (sx + int(facing * 4*s), sy + int(4*s)),
            (sx + int(facing * 0*s), sy + int(12*s)),
            (sx + int(facing * 3*s), sy + int(12*s)),
            (sx + int(facing * -1*s), sy + int(22*s)),
        ]
        pygame.draw.lines(surface, (255, 240, 60), False, _sdpts, max(2, int(2*s)))
        # Demon horns
        for _sdh in [-1, 1]:
            pygame.draw.polygon(surface, (180, 60, 0), [
                (hx + int(_sdh * hd//2), hy - hd),
                (hx + int(_sdh * (hd + max(3, int(5*s)))), hy - hd - max(8, int(10*s))),
                (hx + int(_sdh * (hd + max(1, int(s)))), hy - hd + max(2, int(2*s))),
            ])
        # Red eyes
        pygame.draw.circle(surface, (255, 30, 0), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (255, 30, 0), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Wild Card":
        t = pygame.time.get_ticks()
        # Playing-card black and red split suit
        pygame.draw.rect(surface, (20, 10, 10),
                         (sx - int(11*s), sy, int(11*s), bl))
        pygame.draw.rect(surface, (180, 20, 20),
                         (sx, sy, int(11*s), bl))
        pygame.draw.rect(surface, (150, 130, 120),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(1, int(2*s)))
        # Card suit symbols on chest
        pygame.draw.circle(surface, (180, 20, 20), (sx - max(4, int(4*s)), sy + int(8*s)), max(2, int(2*s)))
        pygame.draw.circle(surface, (20, 10, 10), (sx + max(4, int(4*s)), sy + int(8*s)), max(2, int(2*s)))
        # Spinning question marks
        _wqphase = t * 0.08
        for _wqi in range(3):
            _wqa = math.radians(_wqi * 120) + _wqphase
            _wqsurf = pygame.Surface((8, 8), pygame.SRCALPHA)
            _wqcols = [(255,30,30),(255,255,255),(255,200,0)]
            pygame.draw.circle(_wqsurf, (*_wqcols[_wqi], 180), (4, 4), 3)
            surface.blit(_wqsurf,
                         (sx + int(math.cos(_wqa) * int(14*s)) - 4,
                          (sy + wy)//2 + int(math.sin(_wqa) * int(8*s)) - 4))
        # Joker hat halved
        pygame.draw.polygon(surface, (20, 10, 10), [
            (hx - hd, hy - hd), (hx, hy - hd),
            (hx - hd//2, hy - hd - max(12, int(14*s))),
        ])
        pygame.draw.polygon(surface, (180, 20, 20), [
            (hx, hy - hd), (hx + hd, hy - hd),
            (hx + hd//2, hy - hd - max(12, int(14*s))),
        ])
        # One red, one black eye
        pygame.draw.circle(surface, (255, 40, 40), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (200, 200, 200), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Ghost Warrior":
        t = pygame.time.get_ticks()
        # Translucent ghost body
        _gwsurf = pygame.Surface((int(26*s), bl + int(14*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(_gwsurf, (180, 200, 240, 100),
                            (0, 0, int(26*s), bl + int(14*s)))
        surface.blit(_gwsurf, (sx - int(13*s), sy))
        pygame.draw.rect(surface, (200, 220, 255),
                         (sx - int(13*s), sy, int(26*s), bl), max(1, int(s)),
                         border_radius=max(3, int(4*s)))
        # Wavy ghost tail
        _gwphase = t * 0.05
        for _gwi in range(4):
            _gwx = sx + int(math.sin(_gwphase + _gwi * 1.2) * int(5*s))
            _gwy = wy + _gwi * max(4, int(4*s))
            _gwtsurf = pygame.Surface((int(16*s), max(5, int(5*s))), pygame.SRCALPHA)
            pygame.draw.ellipse(_gwtsurf, (180, 200, 240, 120 - _gwi * 25),
                                (0, 0, int(16*s), max(5, int(5*s))))
            surface.blit(_gwtsurf, (_gwx - int(8*s), _gwy))
        # Reflect shield shimmer
        _grsurf = pygame.Surface((int(50*s), int(50*s)), pygame.SRCALPHA)
        _grpulse = abs(math.sin(t * 0.002))
        pygame.draw.circle(_grsurf, (200, 220, 255, int(30 * _grpulse)),
                           (int(25*s), int(25*s)), int(23*s), max(1, int(2*s)))
        surface.blit(_grsurf, (sx - int(25*s), (sy + wy)//2 - int(25*s)))
        # Hollow eyes
        pygame.draw.circle(surface, (30, 30, 60), (hx - hd//3, hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (30, 30, 60), (hx + hd//3, hy), max(3, int(3*s)))

    elif char_name == "Suicide King":
        t = pygame.time.get_ticks()
        # Crown and red coat — classic playing card king
        pygame.draw.rect(surface, (140, 15, 25),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 40, 50),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Sword through the head (suicide king motif) — vertical line
        pygame.draw.line(surface, (180, 170, 140),
                         (hx + int(facing * hd//2), hy - hd - max(6, int(6*s))),
                         (hx + int(facing * hd//2), hy + hd + max(4, int(4*s))),
                         max(2, int(2*s)))
        pygame.draw.polygon(surface, (200, 190, 160), [
            (hx + int(facing * hd//2), hy - hd - max(6, int(6*s))),
            (hx + int(facing * hd//2) + max(2, int(2*s)), hy - hd - max(2, int(2*s))),
            (hx + int(facing * hd//2) - max(2, int(2*s)), hy - hd - max(2, int(2*s))),
        ])
        # King crown
        _skcrown = hy - hd - max(2, int(s))
        for _ski, _skh in enumerate([10, 16, 10]):
            _skx = hx + int((_ski - 1) * hd * 0.6)
            pygame.draw.polygon(surface, (220, 180, 40), [
                (_skx - max(3, int(3*s)), _skcrown),
                (_skx + max(3, int(3*s)), _skcrown),
                (_skx, _skcrown - max(4, int(_skh * s))),
            ])
        # Explosion warning glow — pulsing red
        _skgsurf = pygame.Surface((int(40*s), int(40*s)), pygame.SRCALPHA)
        _skpulse = abs(math.sin(t * 0.005))
        pygame.draw.circle(_skgsurf, (255, 40, 0, int(60 * _skpulse)),
                           (int(20*s), int(20*s)), int(18*s), max(1, int(2*s)))
        surface.blit(_skgsurf, (sx - int(20*s), (sy + wy)//2 - int(20*s)))

    elif char_name == "Harbinger":
        t = pygame.time.get_ticks()
        # Dark omen robe
        pygame.draw.polygon(surface, (35, 10, 55), [
            (sx - int(12*s), sy),
            (sx + int(12*s), sy),
            (sx + int(17*s), wy),
            (sx - int(17*s), wy),
        ])
        pygame.draw.polygon(surface, (80, 30, 120), [
            (sx - int(12*s), sy),
            (sx + int(12*s), sy),
            (sx + int(17*s), wy),
            (sx - int(17*s), wy),
        ], max(1, int(s)))
        # Orbiting void orbs that bounce
        _hbphase = t * 0.06
        for _hbi in range(3):
            _hba = math.radians(_hbi * 120) + _hbphase
            _hbr = max(14, int(16*s))
            _hbsurf = pygame.Surface((int(10*s), int(10*s)), pygame.SRCALPHA)
            pygame.draw.circle(_hbsurf, (140, 60, 220, 200), (int(5*s), int(5*s)), int(4*s))
            pygame.draw.circle(_hbsurf, (200, 150, 255, 255), (int(5*s), int(4*s)), max(1, int(s)))
            surface.blit(_hbsurf,
                         (sx + int(math.cos(_hba) * _hbr) - int(5*s),
                          (sy + wy)//2 + int(math.sin(_hba) * _hbr * 0.5) - int(5*s)))
        # Doom sigil on chest
        _hsx, _hsy = sx, sy + bl//3
        pygame.draw.circle(surface, (80, 30, 120), (_hsx, _hsy), max(6, int(7*s)), max(1, int(s)))
        pygame.draw.line(surface, (120, 50, 180), (_hsx, _hsy - max(5, int(5*s))), (_hsx, _hsy + max(5, int(5*s))), max(1, int(s)))
        pygame.draw.line(surface, (120, 50, 180), (_hsx - max(5, int(5*s)), _hsy), (_hsx + max(5, int(5*s)), _hsy), max(1, int(s)))
        # Cowl with glowing eyes
        pygame.draw.arc(surface, (25, 8, 40),
                        (hx - hd - max(2, int(2*s)), hy - hd - max(2, int(2*s)),
                         (hd + max(2, int(2*s))) * 2, (hd + max(2, int(2*s))) * 2),
                        0, math.pi * 2, max(2, int(3*s)))
        pygame.draw.circle(surface, (140, 60, 220), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (140, 60, 220), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Hex Doctor":
        t = pygame.time.get_ticks()
        # Plague doctor coat — dark olive
        pygame.draw.rect(surface, (60, 75, 40),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (100, 130, 70),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Plague doctor beak mask
        pygame.draw.ellipse(surface, (50, 60, 30),
                            (hx - hd, hy - hd, hd * 2, hd * 2 + max(4, int(4*s))))
        pygame.draw.polygon(surface, (50, 60, 30), [
            (hx - max(3, int(3*s)), hy + max(2, int(2*s))),
            (hx + max(3, int(3*s)), hy + max(2, int(2*s))),
            (hx + int(facing * max(3, int(2*s))), hy + max(10, int(12*s))),
        ])
        # Goggles — tinted red-green
        pygame.draw.circle(surface, (100, 60, 10), (hx - hd//3, hy - max(1, int(s))), max(3, int(4*s)))
        pygame.draw.circle(surface, (100, 60, 10), (hx + hd//3, hy - max(1, int(s))), max(3, int(4*s)))
        pygame.draw.circle(surface, (60, 200, 80), (hx - hd//3, hy - max(1, int(s))), max(2, int(2*s)))
        pygame.draw.circle(surface, (60, 200, 80), (hx + hd//3, hy - max(1, int(s))), max(2, int(2*s)))
        # Toxic cloud drifting from body
        _hxphase = t * 0.05
        for _hxi in range(4):
            _hxa = math.radians(_hxi * 90) + _hxphase
            _hxsurf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(_hxsurf, (80, 200, 60, 100), (5, 5), 4)
            surface.blit(_hxsurf,
                         (sx + int(math.cos(_hxa) * int(16*s)) - 5,
                          (sy + wy)//2 + int(math.sin(_hxa) * int(10*s)) - 5))

    elif char_name == "Time Warden":
        t = pygame.time.get_ticks()
        # Blue-white temporal armour
        pygame.draw.rect(surface, (60, 100, 160),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (140, 190, 240),
                         (sx - int(12*s), sy, int(24*s), bl), max(1, int(2*s)),
                         border_radius=max(2, int(3*s)))
        # Hourglass emblem on chest
        _twx, _twy2 = sx, sy + bl//3
        pygame.draw.polygon(surface, (200, 220, 255), [
            (_twx - max(5, int(6*s)), _twy2 - max(5, int(5*s))),
            (_twx + max(5, int(6*s)), _twy2 - max(5, int(5*s))),
            (_twx + max(2, int(2*s)), _twy2),
            (_twx - max(2, int(2*s)), _twy2),
        ])
        pygame.draw.polygon(surface, (200, 220, 255), [
            (_twx - max(2, int(2*s)), _twy2),
            (_twx + max(2, int(2*s)), _twy2),
            (_twx + max(5, int(6*s)), _twy2 + max(5, int(5*s))),
            (_twx - max(5, int(6*s)), _twy2 + max(5, int(5*s))),
        ])
        # Time-freeze clock particles orbiting
        _twphase = t * 0.04
        for _twi in range(6):
            _twa = math.radians(_twi * 60) + _twphase
            _twsurf = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(_twsurf, (160, 210, 255, 160), (2, 2), 2)
            surface.blit(_twsurf,
                         (sx + int(math.cos(_twa) * int(15*s)) - 2,
                          (sy + wy)//2 + int(math.sin(_twa) * int(9*s)) - 2))
        # Temporal helm
        pygame.draw.rect(surface, (60, 100, 160),
                         (hx - hd, hy - hd, hd * 2, hd), border_radius=max(1, int(2*s)))
        pygame.draw.circle(surface, (140, 190, 240), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (140, 190, 240), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Doppelganger":
        t = pygame.time.get_ticks()
        # Silver-grey mirror body
        pygame.draw.rect(surface, (110, 110, 130),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (190, 190, 210),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Mirror sheen — diagonal highlight
        pygame.draw.line(surface, (220, 220, 240),
                         (sx - int(8*s), sy + int(4*s)),
                         (sx + int(4*s), sy + int(20*s)), max(1, int(s)))
        # Copy orbs on hands — mimic glimmer
        for _dgh in [(lhx, lhy), (rhx, rhy)]:
            _dgsurf = pygame.Surface((int(12*s), int(12*s)), pygame.SRCALPHA)
            pygame.draw.circle(_dgsurf, (180, 200, 255, 160), (int(6*s), int(6*s)), int(5*s))
            surface.blit(_dgsurf, (_dgh[0] - int(6*s), _dgh[1] - int(6*s)))
        # Confuse spirals around body
        _dgphase = t * 0.09
        for _dgi in range(5):
            _dga = math.radians(_dgi * 72) + _dgphase
            _dgsurf2 = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(_dgsurf2, (180, 180, 220, 140), (2, 2), 2)
            surface.blit(_dgsurf2,
                         (sx + int(math.cos(_dga) * int(13*s)) - 2,
                          (sy + wy)//2 + int(math.sin(_dga) * int(8*s)) - 2))
        # Featureless reflective face
        pygame.draw.circle(surface, (190, 195, 215), (hx, hy), hd)
        pygame.draw.circle(surface, (150, 155, 175), (hx, hy), hd, max(1, int(s)))

    elif char_name == "Graverobber":
        t = pygame.time.get_ticks()
        # Tattered earth-brown coat
        pygame.draw.rect(surface, (75, 55, 35),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(2*s)))
        pygame.draw.rect(surface, (120, 90, 55),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(2*s)))
        # Stolen goods pouch on belt
        pygame.draw.rect(surface, (55, 40, 20),
                         (sx - int(11*s), sy + bl//2, int(22*s), max(2, int(3*s))))
        for _grp in [-5, 0, 5]:
            pygame.draw.ellipse(surface, (90, 70, 40),
                                (sx + int(_grp*s) - max(3, int(3*s)),
                                 sy + bl//2 - max(2, int(2*s)),
                                 max(6, int(6*s)), max(5, int(5*s))))
        # Shovel in back hand
        _grsh = lhx if facing > 0 else rhx
        _grshy = lhy if facing > 0 else rhy
        pygame.draw.line(surface, (100, 80, 50),
                         (_grsh, _grshy), (_grsh - int(facing * 4*s), _grshy - int(16*s)),
                         max(2, int(2*s)))
        pygame.draw.rect(surface, (80, 70, 55),
                         (_grsh - int(facing * 7*s) - max(2, int(2*s)),
                          _grshy - int(20*s) - max(3, int(3*s)),
                          max(5, int(5*s)), max(5, int(5*s))))
        # Soul wisp floating up (undead)
        _grwsurf = pygame.Surface((8, 8), pygame.SRCALPHA)
        _grwphase = (t // 16) % 20
        pygame.draw.circle(_grwsurf, (80, 200, 100, 140), (4, 4), 3)
        surface.blit(_grwsurf, (sx + max(6, int(6*s)), sy - _grwphase))
        # Wide-brim hat
        pygame.draw.ellipse(surface, (45, 32, 18),
                            (hx - hd - max(4, int(5*s)), hy - hd - max(2, int(2*s)),
                             (hd + max(4, int(5*s))) * 2, max(6, int(6*s))))
        pygame.draw.rect(surface, (45, 32, 18),
                         (hx - hd//2, hy - hd - max(9, int(10*s)),
                          hd, max(9, int(10*s))), border_radius=max(1, int(s)))

    elif char_name == "Brawler King":
        t = pygame.time.get_ticks()
        # Orange fighter's tank top
        pygame.draw.rect(surface, (180, 70, 10),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (240, 120, 30),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # King crown — simple but bold
        _bkcrown = hy - hd - max(1, int(s))
        pygame.draw.rect(surface, (220, 180, 40),
                         (hx - hd, _bkcrown - max(6, int(6*s)), hd * 2, max(6, int(6*s))))
        for _bkci in range(-1, 2):
            pygame.draw.polygon(surface, (220, 180, 40), [
                (hx + int(_bkci * hd * 0.6) - max(2, int(2*s)), _bkcrown - max(6, int(6*s))),
                (hx + int(_bkci * hd * 0.6) + max(2, int(2*s)), _bkcrown - max(6, int(6*s))),
                (hx + int(_bkci * hd * 0.6), _bkcrown - max(11, int(12*s))),
            ])
        # Glowing critted fists
        for _bkfh in [(lhx, lhy), (rhx, rhy)]:
            pygame.draw.circle(surface, (255, 215, 0), _bkfh, max(4, int(5*s)))
            pygame.draw.circle(surface, (255, 255, 200), _bkfh, max(2, int(2*s)))
        # Rage streaks
        _bkphase = t * 0.08
        for _bkri in range(4):
            _bkra = math.radians(_bkri * 90 + _bkphase * 20)
            pygame.draw.line(surface, (255, 80, 0),
                             (sx, (sy + wy)//2),
                             (sx + int(math.cos(_bkra) * int(14*s)),
                              (sy + wy)//2 + int(math.sin(_bkra) * int(9*s))),
                             max(1, int(s)))

    elif char_name == "Marksman":
        t = pygame.time.get_ticks()
        # Khaki sniper coat
        pygame.draw.rect(surface, (140, 110, 60),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (180, 150, 90),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Sniper rifle across the back — long diagonal barrel
        pygame.draw.line(surface, (60, 50, 40),
                         (sx - int(10*s), sy + int(5*s)),
                         (sx + int(16*s), sy + bl - int(5*s)), max(3, int(3*s)))
        pygame.draw.line(surface, (100, 90, 70),
                         (sx - int(10*s), sy + int(5*s)),
                         (sx + int(16*s), sy + bl - int(5*s)), max(1, int(s)))
        # Scope lens glint
        pygame.draw.circle(surface, (100, 180, 220),
                           (sx + int(6*s), sy + bl//2), max(3, int(3*s)))
        pygame.draw.circle(surface, (200, 230, 255),
                           (sx + int(6*s), sy + bl//2 - max(1, int(s))), max(1, int(s)))
        # Ghillie netting spots
        for _gnx, _gny in [(-6, 6), (4, 12), (-3, 20), (7, 4)]:
            pygame.draw.circle(surface, (100, 90, 40),
                               (sx + int(_gnx*s), sy + int(_gny*s)), max(2, int(2*s)))
        # Beret and laser-eye glow
        pygame.draw.ellipse(surface, (80, 65, 30),
                            (hx - hd - max(1, int(s)), hy - hd - max(3, int(3*s)),
                             (hd + max(1, int(s))) * 2, max(7, int(7*s))))
        pygame.draw.circle(surface, (255, 80, 0), (hx + int(facing * hd//2), hy), max(2, int(2*s)))

    elif char_name == "Elder":
        t = pygame.time.get_ticks()
        # Mossy green robes
        pygame.draw.polygon(surface, (60, 100, 50), [
            (sx - int(13*s), sy),
            (sx + int(13*s), sy),
            (sx + int(19*s), wy),
            (sx - int(19*s), wy),
        ])
        pygame.draw.polygon(surface, (100, 160, 80), [
            (sx - int(13*s), sy),
            (sx + int(13*s), sy),
            (sx + int(19*s), wy),
            (sx - int(19*s), wy),
        ], max(1, int(s)))
        # Leaf and vine patterns
        for _eli, (_elx, _ely) in enumerate([(-7, 5), (5, 10), (-3, 20), (7, 15)]):
            pygame.draw.ellipse(surface, (80, 140, 60),
                                (sx + int(_elx*s) - max(3, int(3*s)),
                                 sy + int(_ely*s) - max(2, int(2*s)),
                                 max(6, int(6*s)), max(4, int(4*s))))
        # Still-heal pulse — green ring when standing still
        _elpulse = abs(math.sin(t * 0.002))
        _elsurf = pygame.Surface((int(40*s), int(40*s)), pygame.SRCALPHA)
        pygame.draw.circle(_elsurf, (80, 200, 60, int(60 * _elpulse)),
                           (int(20*s), int(20*s)), int(18*s), max(1, int(2*s)))
        surface.blit(_elsurf, (sx - int(20*s), (sy + wy)//2 - int(20*s)))
        # Long white beard
        for _elb in range(-3, 4):
            _elblen = max(8, int((20 - abs(_elb) * 4)*s))
            pygame.draw.line(surface, (240, 240, 230),
                             (hx + int(_elb * 2*s), hy + hd),
                             (hx + int(_elb * 2*s) + int(_elb * s), hy + hd + _elblen),
                             max(1, int(s)))
        # Glowing green eyes
        pygame.draw.circle(surface, (100, 220, 80), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (100, 220, 80), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Shade Walker":
        t = pygame.time.get_ticks()
        # Deep navy shadow suit
        pygame.draw.rect(surface, (15, 10, 35),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (50, 40, 100),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Wall-cling hook claws on hands
        for _wch in [(lhx, lhy), (rhx, rhy)]:
            _wcx, _wcy = _wch
            for _wci in range(3):
                _wca = math.radians(30 + _wci * 30)
                pygame.draw.line(surface, (160, 140, 180),
                                 (_wcx, _wcy),
                                 (_wcx + int(math.cos(_wca) * max(4, int(5*s))),
                                  _wcy - int(math.sin(_wca) * max(4, int(5*s)))),
                                 max(1, int(s)))
        # Stealth shimmer
        _wsphase = t * 0.09
        for _wsi in range(5):
            _wsa = math.radians(_wsi * 72) + _wsphase
            _wssurf = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(_wssurf, (80, 60, 140, 130), (2, 2), 2)
            surface.blit(_wssurf,
                         (sx + int(math.cos(_wsa) * int(13*s)) - 2,
                          (sy + wy)//2 + int(math.sin(_wsa) * int(8*s)) - 2))
        # Narrow slit-mask eyes
        pygame.draw.line(surface, (100, 80, 200),
                         (hx - hd//2, hy), (hx - max(1, int(2*s)), hy), max(1, int(s)))
        pygame.draw.line(surface, (100, 80, 200),
                         (hx + max(1, int(2*s)), hy), (hx + hd//2, hy), max(1, int(s)))

    elif char_name == "Emperor":
        t = pygame.time.get_ticks()
        # Gold and crimson imperial robe
        pygame.draw.polygon(surface, (160, 20, 20), [
            (sx - int(16*s), sy),
            (sx + int(16*s), sy),
            (sx + int(22*s), wy),
            (sx - int(22*s), wy),
        ])
        pygame.draw.polygon(surface, (220, 180, 40), [
            (sx - int(16*s), sy),
            (sx + int(16*s), sy),
            (sx + int(22*s), wy),
            (sx - int(22*s), wy),
        ], max(2, int(2*s)))
        # Dragon emblem on chest
        _dex, _dey = sx, sy + bl//3
        pygame.draw.circle(surface, (220, 180, 40), (_dex, _dey), max(6, int(7*s)), max(1, int(s)))
        pygame.draw.circle(surface, (255, 220, 80), (_dex, _dey), max(3, int(3*s)))
        # Imperial crown — tall pointed
        _ecbase = hy - hd - max(1, int(s))
        for _eci, _ech in enumerate([14, 22, 16]):
            _ecx = hx + int((_eci - 1) * hd * 0.7)
            pygame.draw.polygon(surface, (220, 180, 40), [
                (_ecx - max(3, int(3*s)), _ecbase),
                (_ecx + max(3, int(3*s)), _ecbase),
                (_ecx, _ecbase - max(5, int(_ech * s))),
            ])
            if _eci == 1:
                pygame.draw.circle(surface, (255, 60, 60), (_ecx, _ecbase - max(5, int(_ech * s))), max(2, int(2*s)))
        # Power glow
        _egsurf = pygame.Surface((int(50*s), int(50*s)), pygame.SRCALPHA)
        _egpulse = abs(math.sin(t * 0.002))
        pygame.draw.circle(_egsurf, (220, 160, 40, int(40 * _egpulse)),
                           (int(25*s), int(25*s)), int(23*s), max(1, int(2*s)))
        surface.blit(_egsurf, (sx - int(25*s), (sy + wy)//2 - int(25*s)))

    elif char_name == "Iron Grappler":
        t = pygame.time.get_ticks()
        # Dark slate grappling suit
        pygame.draw.rect(surface, (60, 50, 90),
                         (sx - int(13*s), sy, int(26*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (100, 80, 140),
                         (sx - int(13*s), sy, int(26*s), bl), max(1, int(2*s)),
                         border_radius=max(2, int(3*s)))
        # Chain links across belt
        for _cli in range(-2, 3):
            pygame.draw.circle(surface, (160, 140, 180),
                               (sx + int(_cli * 5*s), sy + bl//2), max(2, int(3*s)), max(1, int(s)))
        # Hook-gauntlet fists
        for _igh in [(lhx, lhy, -1), (rhx, rhy, 1)]:
            _igx, _igy, _igd = _igh
            pygame.draw.rect(surface, (80, 70, 120),
                             (_igx - max(4, int(5*s)), _igy - max(4, int(5*s)),
                              max(10, int(10*s)), max(10, int(10*s))),
                             border_radius=max(1, int(2*s)))
            # Hook tip
            pygame.draw.arc(surface, (180, 160, 220),
                            (_igx + int(_igd * 2*s) - max(4, int(4*s)),
                             _igy - max(6, int(6*s)),
                             max(8, int(8*s)), max(8, int(8*s))),
                            math.radians(0), math.radians(180), max(2, int(2*s)))
        # Anchor ground indicator
        pygame.draw.ellipse(surface, (50, 40, 80), (wx - int(13*s), wy, int(26*s), int(5*s)))

    elif char_name == "Corsair":
        t = pygame.time.get_ticks()
        # Dark pirate coat
        pygame.draw.rect(surface, (40, 25, 10),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (90, 60, 25),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Belt with skull buckle
        pygame.draw.rect(surface, (20, 15, 5),
                         (sx - int(11*s), sy + bl//2, int(22*s), max(2, int(3*s))))
        pygame.draw.circle(surface, (180, 160, 80), (sx, sy + bl//2 + max(1, int(s))), max(3, int(3*s)))
        pygame.draw.circle(surface, (20, 15, 5), (sx, sy + bl//2 + max(1, int(s))), max(1, int(s)))
        # Hook hand on non-dominant side
        _csh = lhx if facing > 0 else rhx
        _cshy = lhy if facing > 0 else rhy
        pygame.draw.arc(surface, (180, 170, 150),
                        (_csh - max(5, int(5*s)), _cshy - max(5, int(6*s)),
                         max(10, int(10*s)), max(10, int(10*s))),
                        math.radians(0), math.radians(200), max(2, int(2*s)))
        # Pirate hat — tricorn
        pygame.draw.polygon(surface, (20, 15, 5), [
            (hx - hd - max(2, int(2*s)), hy - hd),
            (hx + hd + max(2, int(2*s)), hy - hd),
            (hx + hd - max(2, int(2*s)), hy - hd - max(8, int(10*s))),
            (hx - hd + max(2, int(2*s)), hy - hd - max(8, int(10*s))),
        ])
        pygame.draw.polygon(surface, (80, 60, 20), [
            (hx - hd - max(2, int(2*s)), hy - hd),
            (hx + hd + max(2, int(2*s)), hy - hd),
            (hx + hd - max(2, int(2*s)), hy - hd - max(8, int(10*s))),
            (hx - hd + max(2, int(2*s)), hy - hd - max(8, int(10*s))),
        ], max(1, int(s)))
        # Skull and crossbones badge on hat
        pygame.draw.circle(surface, (240, 230, 210), (hx, hy - hd - max(4, int(5*s))), max(3, int(3*s)))

    elif char_name == "Mech":
        t = pygame.time.get_ticks()
        # Gunmetal body panels
        pygame.draw.rect(surface, (70, 80, 90),
                         (sx - int(13*s), sy, int(26*s), bl), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (120, 135, 150),
                         (sx - int(13*s), sy, int(26*s), bl), max(1, int(2*s)),
                         border_radius=max(1, int(2*s)))
        # Panel seam lines
        pygame.draw.line(surface, (50, 60, 70),
                         (sx - int(13*s), sy + bl//2), (sx + int(13*s), sy + bl//2), max(1, int(s)))
        # Reactor core — pulsing blue
        _mrpulse = abs(math.sin(t * 0.003))
        _mrsurf = pygame.Surface((int(14*s), int(14*s)), pygame.SRCALPHA)
        pygame.draw.circle(_mrsurf, (60, 180, 255, int(120 + 80 * _mrpulse)),
                           (int(7*s), int(7*s)), int(6*s))
        surface.blit(_mrsurf, (sx - int(7*s), sy + bl//2 - int(7*s)))
        # Auto-fire missile launchers on shoulders
        for _mfd in [-1, 1]:
            pygame.draw.rect(surface, (60, 70, 80),
                             (sx + int(_mfd * 10*s) - max(2, int(2*s)),
                              sy - max(4, int(4*s)),
                              max(5, int(5*s)), max(8, int(8*s))),
                             border_radius=max(1, int(s)))
        # Square visor head
        pygame.draw.rect(surface, (60, 70, 80),
                         (hx - hd, hy - hd, hd * 2, hd * 2))
        pygame.draw.rect(surface, (100, 130, 160),
                         (hx - hd + max(1, int(s)), hy - max(3, int(4*s)),
                          hd * 2 - max(2, int(2*s)), max(6, int(7*s))))
        pygame.draw.circle(surface, (60, 200, 255), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (60, 200, 255), (hx + hd//3, hy), max(2, int(2*s)))

    elif char_name == "Vault":
        t = pygame.time.get_ticks()
        # Heavy green doorman suit
        pygame.draw.rect(surface, (40, 130, 50),
                         (sx - int(13*s), sy, int(26*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 180, 90),
                         (sx - int(13*s), sy, int(26*s), bl), max(2, int(2*s)),
                         border_radius=max(2, int(3*s)))
        # Stone-skin texture — grey patches
        for _vsp in [(-6, 4), (5, 8), (-4, 18), (7, 14), (0, 26)]:
            pygame.draw.ellipse(surface, (100, 110, 100),
                                (sx + int(_vsp[0]*s) - max(4, int(4*s)),
                                 sy + int(_vsp[1]*s) - max(2, int(3*s)),
                                 max(8, int(8*s)), max(5, int(5*s))))
        # Bounce-punch fists — spring coils on hands
        for _vfh in [(lhx, lhy), (rhx, rhy)]:
            _vfx, _vfy = _vfh
            for _vfi in range(3):
                _vfy2 = _vfy - max(2, int(2*s)) + _vfi * max(2, int(2*s))
                pygame.draw.arc(surface, (180, 200, 180),
                                (_vfx - max(3, int(4*s)), _vfy2 - max(2, int(2*s)),
                                 max(6, int(8*s)), max(4, int(4*s))),
                                0 if _vfi % 2 == 0 else math.pi,
                                math.pi if _vfi % 2 == 0 else math.pi * 2,
                                max(1, int(s)))
        # Reflect shield shimmer on arms
        _vsurf = pygame.Surface((int(50*s), int(30*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(_vsurf, (100, 220, 120, 40), (0, 0, int(50*s), int(30*s)))
        surface.blit(_vsurf, (sx - int(25*s), sy + int(4*s)))

    elif char_name == "Shaolin":
        t = pygame.time.get_ticks()
        # Saffron monk's robe
        pygame.draw.polygon(surface, (200, 120, 20), [
            (sx - int(11*s), sy),
            (sx + int(11*s), sy),
            (sx + int(15*s), wy),
            (sx - int(15*s), wy),
        ])
        pygame.draw.polygon(surface, (240, 160, 40), [
            (sx - int(11*s), sy),
            (sx + int(11*s), sy),
            (sx + int(15*s), wy),
            (sx - int(15*s), wy),
        ], max(1, int(s)))
        # Waist sash
        pygame.draw.rect(surface, (160, 80, 10),
                         (sx - int(12*s), sy + bl//2 - max(2, int(2*s)),
                          int(24*s), max(4, int(4*s))))
        # Crit aura — golden sparks orbiting
        _shphase = t * 0.1
        for _shi in range(5):
            _sha = math.radians(_shi * 72) + _shphase
            _shsurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(_shsurf, (255, 215, 0, 180), (3, 3), 2)
            surface.blit(_shsurf,
                         (sx + int(math.cos(_sha) * int(16*s)) - 3,
                          (sy + wy)//2 + int(math.sin(_sha) * int(9*s)) - 3))
        # Shaved head + calm eyes
        pygame.draw.circle(surface, (180, 140, 80), (hx, hy), hd)
        pygame.draw.line(surface, (100, 70, 20),
                         (hx - hd//3, hy), (hx - max(1, int(s)), hy), max(1, int(s)))
        pygame.draw.line(surface, (100, 70, 20),
                         (hx + max(1, int(s)), hy), (hx + hd//3, hy), max(1, int(s)))

    elif char_name == "Warlord":
        t = pygame.time.get_ticks()
        # Blood-dark war armour
        pygame.draw.rect(surface, (100, 10, 10),
                         (sx - int(14*s), sy, int(28*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (180, 30, 20),
                         (sx - int(14*s), sy, int(28*s), bl), max(1, int(2*s)),
                         border_radius=max(2, int(3*s)))
        # Spiked shoulder pauldrons
        for _wpd in [-1, 1]:
            _wpx = sx + int(_wpd * 14*s)
            pygame.draw.rect(surface, (80, 8, 8),
                             (_wpx - max(4, int(4*s)), sy - max(3, int(3*s)),
                              max(8, int(8*s)), max(7, int(7*s))),
                             border_radius=max(1, int(s)))
            for _wps in range(3):
                pygame.draw.line(surface, (160, 25, 15),
                                 (_wpx - max(2, int(2*s)) + _wps * max(2, int(2*s)),
                                  sy - max(3, int(3*s))),
                                 (_wpx - max(2, int(2*s)) + _wps * max(2, int(2*s)),
                                  sy - max(7, int(7*s))), max(1, int(s)))
        # Battle-axe silhouette on chest
        _wax, _way = sx, sy + bl//3
        pygame.draw.line(surface, (160, 140, 60), (_wax, _way - max(6, int(6*s))), (_wax, _way + max(6, int(6*s))), max(2, int(2*s)))
        pygame.draw.polygon(surface, (160, 140, 60), [
            (_wax, _way - max(6, int(6*s))),
            (_wax + int(facing * max(8, int(8*s))), _way - max(4, int(4*s))),
            (_wax + int(facing * max(6, int(6*s))), _way + max(2, int(2*s))),
        ])
        # Rage glow
        _wgsurf = pygame.Surface((int(36*s), int(36*s)), pygame.SRCALPHA)
        _wgpulse = abs(math.sin(t * 0.004))
        pygame.draw.circle(_wgsurf, (200, 20, 0, int(50 * _wgpulse)),
                           (int(18*s), int(18*s)), int(16*s), max(1, int(2*s)))
        surface.blit(_wgsurf, (sx - int(18*s), (sy + wy)//2 - int(18*s)))
        # Horned helmet
        for _whd in [-1, 1]:
            pygame.draw.polygon(surface, (80, 8, 8), [
                (hx + int(_whd * hd//2), hy - hd),
                (hx + int(_whd * (hd + max(4, int(6*s)))), hy - hd - max(10, int(12*s))),
                (hx + int(_whd * (hd + max(2, int(2*s)))), hy - hd + max(3, int(3*s))),
            ])
        pygame.draw.rect(surface, (80, 8, 8),
                         (hx - hd, hy - hd, hd * 2, hd),
                         border_radius=max(1, int(s)))

    elif char_name == "Surgeon":
        t = pygame.time.get_ticks()
        # Surgical scrubs — teal/green
        pygame.draw.rect(surface, (50, 130, 120),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (80, 180, 160),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Scalpel in dominant hand
        _sgh = rhx if facing > 0 else lhx
        _sghy = rhy if facing > 0 else lhy
        pygame.draw.line(surface, (200, 200, 210),
                         (_sgh, _sghy), (_sgh + int(facing * 14*s), _sghy - int(3*s)), max(2, int(2*s)))
        pygame.draw.polygon(surface, (220, 220, 230), [
            (_sgh + int(facing * 14*s), _sghy - int(3*s)),
            (_sgh + int(facing * 18*s), _sghy - int(1*s)),
            (_sgh + int(facing * 15*s), _sghy + int(3*s)),
        ])
        # Drain wisps
        _sgphase = t * 0.07
        for _sgi in range(3):
            _sga = math.radians(_sgi * 120) + _sgphase
            _sgsurf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(_sgsurf, (100, 200, 180, 130), (4, 4), 3)
            surface.blit(_sgsurf,
                         (sx + int(math.cos(_sga) * int(14*s)) - 4,
                          (sy + wy)//2 + int(math.sin(_sga) * int(8*s)) - 4))
        # Surgical mask
        pygame.draw.rect(surface, (200, 230, 225),
                         (hx - hd//2, hy, hd, max(4, int(5*s))),
                         border_radius=max(1, int(s)))
        # Surgical cap
        pygame.draw.ellipse(surface, (50, 130, 120),
                            (hx - hd - max(1, int(s)), hy - hd - max(3, int(4*s)),
                             (hd + max(1, int(s))) * 2, max(8, int(9*s))))

    elif char_name == "Cutthroat":
        t = pygame.time.get_ticks()
        # Dark maroon thief outfit
        pygame.draw.rect(surface, (60, 25, 50),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (110, 50, 80),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Throwing knives strapped across chest
        for _cti, _ctoff in enumerate([-6, 0, 6]):
            pygame.draw.line(surface, (180, 170, 160),
                             (sx + int(_ctoff*s), sy + int(4*s)),
                             (sx + int(_ctoff*s), sy + int(14*s)), max(1, int(s)))
            pygame.draw.polygon(surface, (200, 190, 180), [
                (sx + int(_ctoff*s) - max(1, int(s)), sy + int(4*s)),
                (sx + int(_ctoff*s) + max(1, int(s)), sy + int(4*s)),
                (sx + int(_ctoff*s), sy + int(1*s)),
            ])
        # Poison blade in back hand (backstab)
        _ctbh = lhx if facing > 0 else rhx
        _ctbhy = lhy if facing > 0 else rhy
        pygame.draw.line(surface, (80, 160, 80),
                         (_ctbh, _ctbhy),
                         (_ctbh - int(facing * 10*s), _ctbhy - int(8*s)), max(2, int(2*s)))
        pygame.draw.polygon(surface, (120, 200, 100), [
            (_ctbh - int(facing * 10*s), _ctbhy - int(8*s)),
            (_ctbh - int(facing * 14*s), _ctbhy - int(5*s)),
            (_ctbh - int(facing * 11*s), _ctbhy - int(12*s)),
        ])
        # Shadow shimmer
        _ctphase = t * 0.09
        for _ctpi in range(4):
            _ctpa = math.radians(_ctpi * 90) + _ctphase
            _ctpsurf = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(_ctpsurf, (100, 40, 80, 120), (2, 2), 2)
            surface.blit(_ctpsurf,
                         (sx + int(math.cos(_ctpa) * int(12*s)) - 2,
                          (sy + wy)//2 + int(math.sin(_ctpa) * int(7*s)) - 2))
        # Scarf over face
        pygame.draw.arc(surface, (80, 30, 60),
                        (hx - hd, hy - max(2, int(2*s)), hd * 2, max(6, int(7*s))),
                        0, math.pi, max(2, int(3*s)))
        pygame.draw.circle(surface, (150, 80, 120), (hx - hd//3, hy - max(3, int(3*s))), max(2, int(2*s)))
        pygame.draw.circle(surface, (150, 80, 120), (hx + hd//3, hy - max(3, int(3*s))), max(2, int(2*s)))

    elif char_name == "Chef":
        t = pygame.time.get_ticks()
        # White chef's coat
        pygame.draw.rect(surface, (245, 245, 240),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (200, 195, 185),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Double-breast buttons
        for _cbr in [sy + int(6*s), sy + int(13*s), sy + int(20*s)]:
            for _cbc in [-3, 3]:
                pygame.draw.circle(surface, (160, 155, 145),
                                   (sx + int(_cbc*s), _cbr), max(1, int(s)))
        # Tall chef's toque — cylinder + flat top
        _hat_h = max(18, int(22*s))
        _hat_w = max(14, int(16*s))
        pygame.draw.rect(surface, (250, 250, 248),
                         (hx - _hat_w, hy - hd - _hat_h, _hat_w * 2, _hat_h),
                         border_radius=max(2, int(3*s)))
        pygame.draw.ellipse(surface, (230, 228, 220),
                            (hx - _hat_w - max(2, int(2*s)), hy - hd - _hat_h - max(3, int(3*s)),
                             (_hat_w + max(2, int(2*s))) * 2, max(7, int(7*s))))
        pygame.draw.rect(surface, (200, 198, 190),
                         (hx - _hat_w, hy - hd - _hat_h, _hat_w * 2, _hat_h),
                         max(1, int(s)), border_radius=max(2, int(3*s)))
        # Rolling pin in dominant hand
        _rph_x = rhx if facing > 0 else lhx
        _rph_y = rhy if facing > 0 else lhy
        pygame.draw.line(surface, (200, 160, 100),
                         (_rph_x - int(facing * 10*s), _rph_y - int(3*s)),
                         (_rph_x + int(facing * 10*s), _rph_y + int(3*s)),
                         max(4, int(4*s)))
        pygame.draw.circle(surface, (180, 140, 80), (_rph_x - int(facing * 10*s), _rph_y - int(3*s)), max(3, int(3*s)))
        pygame.draw.circle(surface, (180, 140, 80), (_rph_x + int(facing * 10*s), _rph_y + int(3*s)), max(3, int(3*s)))
        # Baking sparkle when blocking — golden particles
        if True:  # always draw subtle steam; bright when baking
            _bkphase = t * 0.1
            for _bki in range(3):
                _bkangle = math.radians(_bki * 120 + _bkphase * 30)
                _bkx = sx + int(math.cos(_bkangle) * int(14*s))
                _bky = sy - max(4, int(5*s)) + int(math.sin(_bkphase * 0.3 + _bki) * int(3*s))
                _bksurf = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(_bksurf, (255, 220, 80, 100), (4, 4), 3)
                surface.blit(_bksurf, (_bkx - 4, _bky - 4))

    elif char_name == "Backstabber":
        t = pygame.time.get_ticks()
        # Dark assassin bodysuit
        pygame.draw.rect(surface, (25, 18, 45),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (70, 50, 110),
                         (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Crossed dagger straps on chest
        pygame.draw.line(surface, (90, 70, 130),
                         (sx - int(8*s), sy + int(4*s)), (sx + int(8*s), sy + int(14*s)), max(1, int(s)))
        pygame.draw.line(surface, (90, 70, 130),
                         (sx + int(8*s), sy + int(4*s)), (sx - int(8*s), sy + int(14*s)), max(1, int(s)))
        # Dagger in back hand (the non-facing hand — ready to backstab)
        _bkh_x = lhx if facing > 0 else rhx
        _bkh_y = lhy if facing > 0 else rhy
        # Blade
        pygame.draw.line(surface, (200, 200, 220),
                         (_bkh_x, _bkh_y),
                         (_bkh_x - int(facing * 12*s), _bkh_y - int(10*s)),
                         max(2, int(2*s)))
        # Tip
        pygame.draw.polygon(surface, (230, 230, 250), [
            (_bkh_x - int(facing * 12*s), _bkh_y - int(10*s)),
            (_bkh_x - int(facing * 16*s), _bkh_y - int(8*s)),
            (_bkh_x - int(facing * 13*s), _bkh_y - int(14*s)),
        ])
        # Guard (cross-piece)
        pygame.draw.line(surface, (120, 90, 60),
                         (_bkh_x - int(facing * 8*s), _bkh_y - int(5*s) - max(2, int(3*s))),
                         (_bkh_x - int(facing * 8*s), _bkh_y - int(5*s) + max(2, int(3*s))),
                         max(2, int(2*s)))
        # Shadow shimmer — stealth particles
        _bphase = t * 0.08
        for _bpi in range(4):
            _bpa = math.radians(_bpi * 90) + _bphase
            _bpsurf = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(_bpsurf, (80, 50, 120, 140), (2, 2), 2)
            surface.blit(_bpsurf,
                         (sx + int(math.cos(_bpa) * int(13*s)) - 2,
                          (sy + wy)//2 + int(math.sin(_bpa) * int(8*s)) - 2))
        # Dark hood / mask
        pygame.draw.arc(surface, (20, 12, 35),
                        (hx - hd - max(1, int(2*s)), hy - hd - max(1, int(2*s)),
                         (hd + max(1, int(2*s))) * 2, (hd + max(1, int(2*s))) * 2),
                        0, math.pi * 2, max(2, int(3*s)))
        # Glinting eyes — narrow slits
        pygame.draw.line(surface, (180, 140, 255),
                         (hx - hd//2, hy), (hx - max(1, int(2*s)), hy), max(1, int(s)))
        pygame.draw.line(surface, (180, 140, 255),
                         (hx + max(1, int(2*s)), hy), (hx + hd//2, hy), max(1, int(s)))

    elif char_name == "Crazy":
        t = pygame.time.get_ticks()
        # Wildly shifting rainbow body
        _chue = (t // 3) % 360
        _cr = int(128 + 127 * math.sin(math.radians(_chue)))
        _cg = int(128 + 127 * math.sin(math.radians(_chue + 120)))
        _cb = int(128 + 127 * math.sin(math.radians(_chue + 240)))
        pygame.draw.rect(surface, (_cr, _cg, _cb),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (255, 255, 255),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)),
                         border_radius=max(2, int(3*s)))
        # Teleport afterimages — 3 ghost copies offset randomly (seeded by time bucket)
        for _cgi in range(3):
            _cgoff_x = int(math.sin(t * 0.007 + _cgi * 2.1) * int(20*s))
            _cgoff_y = int(math.cos(t * 0.009 + _cgi * 1.7) * int(12*s))
            _cgsurf = pygame.Surface((int(24*s), bl), pygame.SRCALPHA)
            pygame.draw.rect(_cgsurf, (255, 80, 220, 45 - _cgi * 12),
                             (0, 0, int(24*s), bl), border_radius=max(1, int(2*s)))
            surface.blit(_cgsurf, (sx - int(12*s) + _cgoff_x, sy + _cgoff_y))
        # Spiral chaos on chest
        _cphase = t * 0.15
        for _csi in range(8):
            _csa = math.radians(_csi * 45) + _cphase
            _csr = max(3, int((3 + _csi)*s))
            _csx2 = sx + int(math.cos(_csa) * _csr)
            _csy2 = sy + bl//3 + int(math.sin(_csa) * _csr)
            _cssurf = pygame.Surface((5, 5), pygame.SRCALPHA)
            _cscol = [(255,50,220),(255,220,50),(50,220,255),(220,255,50),
                      (255,100,50),(50,255,180),(200,50,255),(255,180,50)][_csi]
            pygame.draw.circle(_cssurf, (*_cscol, 200), (2, 2), 2)
            surface.blit(_cssurf, (_csx2 - 2, _csy2 - 2))
        # Zany wide eyes
        pygame.draw.circle(surface, (255, 255, 255), (hx - hd//3, hy), max(4, int(4*s)))
        pygame.draw.circle(surface, (255, 255, 255), (hx + hd//3, hy), max(4, int(4*s)))
        pygame.draw.circle(surface, (_cr, _cg, _cb), (hx - hd//3, hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (_cr, _cg, _cb), (hx + hd//3, hy), max(2, int(2*s)))
        # Question mark above head
        _qfont = pygame.font.SysFont("Arial", max(10, int(14*s)), bold=True)
        _qs = _qfont.render("?", True, (255, 255, 255))
        surface.blit(_qs, (hx - _qs.get_width()//2, hy - hd - max(12, int(14*s))))

    elif char_name == "Leech King":
        # Dark crimson robe with fang crown and drain tendrils
        pygame.draw.rect(surface, (100, 0, 60),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Drain tendrils arcing off shoulders
        for _ti in range(3):
            _ta = math.radians(-30 + _ti * 30)
            _tx = sx + int(math.cos(_ta) * int((12+_ti*4)*s))
            _ty = sy + int(bl * 0.15) + int(math.sin(_ta) * int(6*s))
            pygame.draw.line(surface, (180, 0, 100), (sx, sy + int(bl*0.15)), (_tx, _ty), max(1, int(2*s)))
        # Crown spikes
        for _ki in range(3):
            _kx = hx - int(hd*0.4) + _ki * int(hd*0.4)
            pygame.draw.polygon(surface, (220, 0, 80),
                                [(_kx, hy - hd), (_kx - int(4*s), hy - hd - int(8*s)), (_kx + int(4*s), hy - hd - int(8*s))])
        pygame.draw.circle(surface, (255, 60, 120), (hx, hy), max(2, int(3*s)))

    elif char_name == "Puppeteer":
        # Sandy robe with puppet strings and wide eyes
        pygame.draw.rect(surface, (160, 130, 60),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Strings drooping from hands
        _lh2 = lh; _rh2 = rh
        for _psx, _psy in [_lh2, _rh2]:
            pygame.draw.line(surface, (200, 180, 100),
                             (_psx, _psy), (_psx, _psy + int(10*s)), max(1, int(s)))
            pygame.draw.circle(surface, (220, 150, 80), (_psx, _psy + int(10*s)), max(2, int(2*s)))
        # Jester brim on hat
        pygame.draw.ellipse(surface, (200, 160, 60),
                            (hx - int(hd*0.85), hy - hd - int(5*s), int(hd*1.7), int(5*s)))
        pygame.draw.circle(surface, (255, 200, 80), (hx, hy - hd - int(8*s)), max(3, int(3*s)))

    elif char_name == "Sorcerer":
        # Deep purple robe with star-field shimmer and tall pointy hat
        _t = pygame.time.get_ticks()
        _shue = (_t // 5) % 360
        _sr2 = int(60 + 40 * math.sin(math.radians(_shue)))
        _sg2 = int(30 + 20 * math.sin(math.radians(_shue + 120)))
        _sb2 = int(140 + 80 * math.sin(math.radians(_shue + 240)))
        pygame.draw.rect(surface, (_sr2, _sg2, _sb2),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Stars on robe
        for _si2 in range(5):
            _ssx = sx - int(8*s) + int(_si2 * 4 * s)
            _ssy = sy + int((_si2 % 3 + 1) * bl // 5)
            pygame.draw.circle(surface, (255, 255, 200), (_ssx, _ssy), max(1, int(s)))
        # Tall conical hat
        pygame.draw.polygon(surface, (60, 20, 140),
                            [(hx, hy - hd - int(22*s)), (hx - int(9*s), hy - hd), (hx + int(9*s), hy - hd)])

    elif char_name == "Guardian":
        # Stone-grey plate with cross emblem and glowing shield halo
        pygame.draw.rect(surface, (160, 170, 150),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Cross on chest
        _cx2 = sx; _cy2 = sy + int(bl*0.35)
        pygame.draw.rect(surface, (220, 220, 200),
                         (_cx2 - int(s), _cy2 - int(6*s), int(2*s), int(12*s)))
        pygame.draw.rect(surface, (220, 220, 200),
                         (_cx2 - int(5*s), _cy2 - int(s), int(10*s), int(2*s)))
        # Glowing ring halo
        pygame.draw.circle(surface, (255, 255, 200), (hx, hy - hd + int(2*s)), hd + int(4*s), max(1, int(2*s)))
        # Visor
        pygame.draw.rect(surface, (100, 120, 100),
                         (hx - int(hd*0.7), hy - int(3*s), int(hd*1.4), int(5*s)), border_radius=max(1, int(s)))

    elif char_name == "Iron Maiden":
        # Gunmetal plate with spike tips and red-glow rivets
        pygame.draw.rect(surface, (70, 70, 90),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Shoulder spikes
        for _dx3 in (-int(11*s), int(11*s)):
            pygame.draw.polygon(surface, (160, 160, 180),
                                [(sx + _dx3, sy), (sx + _dx3 + int(math.copysign(4*s, _dx3)), sy - int(8*s)),
                                 (sx + _dx3 + int(math.copysign(2*s, _dx3)), sy + int(6*s))])
        # Red rivets
        for _riy in [0.2, 0.5, 0.8]:
            pygame.draw.circle(surface, (220, 30, 30), (sx, sy + int(bl*_riy)), max(2, int(2*s)))
        # Helmet with red visor slit
        pygame.draw.rect(surface, (80, 80, 100),
                         (hx - hd, hy - hd, int(hd*2), int(hd*2)), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (200, 0, 0),
                         (hx - int(hd*0.8), hy - int(2*s), int(hd*1.6), int(4*s)))

    elif char_name == "Berserker Queen":
        # Bloodred battle-dress with flame shoulders
        pygame.draw.rect(surface, (180, 20, 80),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Flame wisps at shoulders
        _t4 = pygame.time.get_ticks()
        for _fi4 in range(4):
            _fa4 = _fi4 * 0.8 + _t4 * 0.004
            _fx4 = sx - int(13*s) + int(math.cos(_fa4) * int(5*s))
            _fy4 = sy + int(math.sin(_fa4 + 1) * int(4*s))
            _fsurf4 = pygame.Surface((int(6*s)+2, int(6*s)+2), pygame.SRCALPHA)
            pygame.draw.circle(_fsurf4, (255, 80, 0, 160), (int(3*s), int(3*s)), max(2, int(3*s)))
            surface.blit(_fsurf4, (_fx4 - int(3*s), _fy4 - int(3*s)))
        # Crown of horns
        for _hi5 in range(3):
            _hx5 = hx - int(hd*0.5) + _hi5 * int(hd*0.5)
            pygame.draw.polygon(surface, (220, 40, 60),
                                [(_hx5, hy - hd), (_hx5 - int(3*s), hy - hd - int(9*s)),
                                 (_hx5 + int(3*s), hy - hd - int(9*s))])

    elif char_name == "Phantom Lord":
        # Near-black robe with ghostly shimmer and floating crown
        _t5 = pygame.time.get_ticks()
        _pa5 = math.sin(_t5 * 0.003) * int(3*s)
        _psurf5 = pygame.Surface((int(24*s), bl + int(6*s)), pygame.SRCALPHA)
        pygame.draw.rect(_psurf5, (30, 0, 50, 200),
                         (int(2*s), 0, int(20*s), bl + int(6*s)), border_radius=max(2, int(3*s)))
        surface.blit(_psurf5, (sx - int(12*s), sy + int(_pa5)))
        # Glowing eyes
        pygame.draw.circle(surface, (100, 0, 200), (hx - int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (100, 0, 200), (hx + int(hd*0.35), hy), max(3, int(3*s)))
        # Floating crown offset
        _crown_y = hy - hd - int(10*s) + int(math.sin(_t5 * 0.004) * int(3*s))
        pygame.draw.polygon(surface, (60, 0, 100),
                            [(hx - int(9*s), _crown_y + int(6*s)), (hx, _crown_y),
                             (hx + int(9*s), _crown_y + int(6*s)), (hx + int(6*s), _crown_y + int(10*s)),
                             (hx - int(6*s), _crown_y + int(10*s))])

    elif char_name == "Trapper":
        # Brown gear vest with bear-trap silhouette on chest
        pygame.draw.rect(surface, (100, 80, 35),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Trap jaws on chest
        _ty6 = sy + int(bl*0.4)
        pygame.draw.arc(surface, (200, 160, 60),
                        (sx - int(8*s), _ty6 - int(6*s), int(16*s), int(12*s)),
                        0, math.pi, max(1, int(2*s)))
        pygame.draw.arc(surface, (200, 160, 60),
                        (sx - int(8*s), _ty6 - int(6*s), int(16*s), int(12*s)),
                        math.pi, math.pi * 2, max(1, int(2*s)))
        # Camo dots on vest
        for _ci6 in range(5):
            _cx6 = sx - int(7*s) + _ci6 * int(3*s)
            _cy6 = sy + int(bl*0.65)
            pygame.draw.circle(surface, (70, 60, 20), (_cx6, _cy6), max(1, int(s)))
        # Worn hat brim
        pygame.draw.ellipse(surface, (130, 100, 40),
                            (hx - int(hd*0.9), hy - hd - int(4*s), int(hd*1.8), int(6*s)))

    elif char_name == "Dark Knight":
        # Pitch-black plate armor with glowing red slits
        pygame.draw.rect(surface, (20, 15, 30),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Glowing red chest rune
        _rfont7 = pygame.font.SysFont("Arial", max(8, int(10*s)), bold=True)
        _rs7 = _rfont7.render("✦", True, (180, 0, 0))
        surface.blit(_rs7, (sx - _rs7.get_width()//2, sy + int(bl*0.3)))
        # Pauldron edges
        for _dx7 in (-int(11*s), int(11*s)):
            pygame.draw.rect(surface, (40, 30, 50),
                             (sx + _dx7 - int(3*s if _dx7 < 0 else 0), sy - int(4*s),
                              int(6*s), int(10*s)), border_radius=max(1, int(s)))
        # Full-face helmet with red visor line
        pygame.draw.rect(surface, (25, 20, 35),
                         (hx - hd, hy - hd, int(hd*2), int(hd*2)), border_radius=max(1, int(2*s)))
        pygame.draw.line(surface, (200, 0, 0),
                         (hx - int(hd*0.7), hy), (hx + int(hd*0.7), hy), max(1, int(s)))

    elif char_name == "Templar":
        # Cream-white tabard with gold cross and halo ring
        pygame.draw.rect(surface, (210, 200, 160),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Gold cross
        _cx8 = sx; _cy8 = sy + int(bl*0.35)
        pygame.draw.rect(surface, (220, 180, 0),
                         (_cx8 - int(s), _cy8 - int(8*s), int(2*s), int(16*s)))
        pygame.draw.rect(surface, (220, 180, 0),
                         (_cx8 - int(6*s), _cy8 - int(2*s), int(12*s), int(3*s)))
        # Golden halo
        pygame.draw.circle(surface, (255, 220, 0), (hx, hy - hd), hd + int(5*s), max(1, int(2*s)))
        # White veil draping from helm
        pygame.draw.rect(surface, (240, 235, 210),
                         (hx - int(hd*0.6), hy, int(hd*1.2), int(hd*1.5)), border_radius=max(1, int(s)))

    elif char_name == "Hydra":
        # Dark teal scales with three small heads flanking the main
        pygame.draw.rect(surface, (25, 80, 50),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Scale texture
        for _row9 in range(3):
            for _col9 in range(3):
                _hsx = sx - int(7*s) + _col9 * int(7*s)
                _hsy = sy + int(bl*0.2) + _row9 * int(bl*0.25)
                pygame.draw.circle(surface, (40, 120, 80), (_hsx, _hsy), max(2, int(3*s)), max(1, int(s)))
        # Two side necks
        _t9 = pygame.time.get_ticks()
        for _ns9, _na9 in [(-1, 0.3), (1, -0.3)]:
            _nox9 = int(math.sin(_t9*0.003 + _na9) * int(5*s))
            _nneck_x = sx + _ns9 * int(13*s) + _nox9
            pygame.draw.line(surface, (35, 100, 65), (sx + _ns9*int(8*s), sy), (_nneck_x, sy - int(12*s)), max(2, int(2*s)))
            pygame.draw.circle(surface, (50, 140, 80), (_nneck_x, sy - int(12*s)), max(4, int(4*s)))

    elif char_name == "Chimera":
        # Shifting multi-colored patchwork body (lion/goat/snake sections)
        _t10 = pygame.time.get_ticks()
        _ch10 = (_t10 // 10) % 360
        _r10 = int(128 + 100 * math.sin(math.radians(_ch10)))
        _g10 = int(80 + 60 * math.sin(math.radians(_ch10 + 120)))
        _b10 = int(100 + 80 * math.sin(math.radians(_ch10 + 240)))
        pygame.draw.rect(surface, (_r10, _g10, _b10),
                         (sx - int(11*s), sy, int(22*s), bl//2), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (_b10, _r10, _g10),
                         (sx - int(11*s), sy + bl//2, int(22*s), bl//2), border_radius=max(2, int(3*s)))
        # Mixed face: one horn + one ear
        pygame.draw.polygon(surface, (_r10, _g10, 80),
                            [(hx - int(hd*0.3), hy - hd), (hx - int(hd*0.15), hy - hd - int(10*s)),
                             (hx - int(hd*0.0), hy - hd)])
        pygame.draw.ellipse(surface, (_g10, _b10, 120),
                            (hx + int(hd*0.4), hy - int(hd*0.5), int(hd*0.5), int(hd*0.8)))

    elif char_name == "Fortune":
        # Gold and white gambler's jacket with coin-spin aura
        pygame.draw.rect(surface, (210, 170, 0),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # White lapels
        pygame.draw.polygon(surface, (255, 255, 220),
                            [(sx - int(5*s), sy), (sx, sy + int(bl*0.4)), (sx - int(11*s), sy)])
        pygame.draw.polygon(surface, (255, 255, 220),
                            [(sx + int(5*s), sy), (sx, sy + int(bl*0.4)), (sx + int(11*s), sy)])
        # Spinning coin
        _t11 = pygame.time.get_ticks()
        _cw11 = max(2, int(abs(math.cos(_t11 * 0.005)) * int(8*s)))
        pygame.draw.ellipse(surface, (255, 215, 0),
                            (sx - _cw11//2, sy - int(18*s), _cw11, int(8*s)))
        pygame.draw.ellipse(surface, (200, 160, 0),
                            (sx - _cw11//2, sy - int(18*s), _cw11, int(8*s)), max(1, int(s)))
        # Top hat
        pygame.draw.rect(surface, (20, 15, 10),
                         (hx - int(hd*0.55), hy - hd - int(14*s), int(hd*1.1), int(14*s)))
        pygame.draw.ellipse(surface, (20, 15, 10),
                            (hx - int(hd*0.9), hy - hd - int(3*s), int(hd*1.8), int(6*s)))
        # Gold hat band
        pygame.draw.rect(surface, (220, 180, 0),
                         (hx - int(hd*0.55), hy - hd - int(4*s), int(hd*1.1), int(3*s)))

    elif char_name == "Chaos Lord":
        # Pulsing violet-black robe with fractal cracks and crown of chaos
        _t12 = pygame.time.get_ticks()
        _ch12 = (_t12 // 4) % 360
        _r12 = int(80 + 60 * math.sin(math.radians(_ch12)))
        _g12 = int(0 + 20 * math.sin(math.radians(_ch12 + 90)))
        _b12 = int(140 + 80 * math.sin(math.radians(_ch12 + 180)))
        pygame.draw.rect(surface, (_r12, _g12, _b12),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Crack lines on robe
        for _ci12 in range(4):
            _ca12 = math.radians(45 + _ci12 * 45 + _t12 * 0.05)
            _cl12 = int((4 + _ci12 * 2) * s)
            _csx12 = sx + int(math.cos(_ca12) * _cl12)
            _csy12 = sy + int(bl*0.4) + int(math.sin(_ca12) * _cl12)
            pygame.draw.line(surface, (220, 80, 255),
                             (sx, sy + int(bl*0.4)), (_csx12, _csy12), max(1, int(s)))
        # Crown of jagged spikes
        for _ki12 in range(5):
            _kx12 = hx - int(hd*0.8) + _ki12 * int(hd*0.4)
            _kh12 = int((6 + (_ki12 % 2)*4)*s)
            pygame.draw.polygon(surface, (160, 0, 220),
                                [(_kx12, hy - hd), (_kx12 - int(2*s), hy - hd - _kh12),
                                 (_kx12 + int(2*s), hy - hd - _kh12)])
        # Chaos eyes
        pygame.draw.circle(surface, (255, 0, 200), (hx - int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (255, 0, 200), (hx + int(hd*0.35), hy), max(3, int(3*s)))


    elif char_name == "Cannonball":
        # Burnished orange-iron sphere body with rivet bands
        pygame.draw.ellipse(surface, (200, 90, 25),
                            (sx - int(11*s), sy, int(22*s), bl))
        pygame.draw.ellipse(surface, (240, 130, 50),
                            (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)))
        # Horizontal rivet bands
        for _rbi in range(3):
            _rby = sy + int(bl * (0.25 + _rbi * 0.25))
            pygame.draw.line(surface, (150, 60, 15),
                             (sx - int(10*s), _rby), (sx + int(10*s), _rby), max(1, int(2*s)))
            for _rbx in (-int(6*s), 0, int(6*s)):
                pygame.draw.circle(surface, (255, 180, 80), (sx + _rbx, _rby), max(2, int(2*s)))
        # Fuse on top of head
        pygame.draw.line(surface, (60, 40, 20),
                         (hx, hy - hd), (hx + int(4*s), hy - hd - int(10*s)), max(2, int(2*s)))
        _t_cb = pygame.time.get_ticks()
        _spark = int(math.sin(_t_cb * 0.02) * int(2*s))
        pygame.draw.circle(surface, (255, 220, 50),
                           (hx + int(4*s), hy - hd - int(10*s) + _spark), max(2, int(2*s)))

    elif char_name == "Wraith":
        # Translucent silver-purple ghostly robe
        _t_wr = pygame.time.get_ticks()
        _wr_alpha = int(140 + 60 * math.sin(_t_wr * 0.004))
        _wr_surf = pygame.Surface((int(24*s), bl + int(8*s)), pygame.SRCALPHA)
        pygame.draw.ellipse(_wr_surf, (150, 130, 210, _wr_alpha),
                            (0, 0, int(24*s), bl + int(8*s)))
        surface.blit(_wr_surf, (sx - int(12*s), sy))
        # Wispy trailing hem at bottom
        for _wi in range(4):
            _wox = int(math.sin(_t_wr * 0.005 + _wi * 1.2) * int(5*s))
            _wsurf = pygame.Surface((int(8*s), int(12*s)), pygame.SRCALPHA)
            pygame.draw.ellipse(_wsurf, (180, 160, 240, 80),
                                (0, 0, int(8*s), int(12*s)))
            surface.blit(_wsurf, (sx - int(10*s) + _wi * int(6*s) + _wox, sy + bl - int(4*s)))
        # Glowing hollow eyes
        pygame.draw.circle(surface, (200, 180, 255), (hx - int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (200, 180, 255), (hx + int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (30, 20, 60), (hx - int(hd*0.35), hy), max(1, int(s)))
        pygame.draw.circle(surface, (30, 20, 60), (hx + int(hd*0.35), hy), max(1, int(s)))

    elif char_name == "Plaguebringer":
        # Rotting green robe with boils and plague mask
        pygame.draw.rect(surface, (65, 130, 50),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (40, 90, 30),
                         (sx - int(11*s), sy, int(22*s), bl), max(1, int(s)), border_radius=max(2, int(3*s)))
        # Boil dots on robe
        for _bx, _by in [(-6, 0.2), (5, 0.35), (-3, 0.6), (7, 0.7), (-7, 0.82)]:
            pygame.draw.circle(surface, (120, 200, 60),
                               (sx + int(_bx*s), sy + int(bl*_by)), max(2, int(2*s)))
            pygame.draw.circle(surface, (160, 230, 80),
                               (sx + int(_bx*s), sy + int(bl*_by)), max(1, int(s)))
        # Long beaked plague mask
        pygame.draw.ellipse(surface, (60, 50, 30),
                            (hx - hd, hy - hd, int(hd*2), int(hd*2)))
        pygame.draw.polygon(surface, (50, 40, 20),
                            [(hx - int(hd*0.3), hy + int(hd*0.4)),
                             (hx + int(hd*0.3), hy + int(hd*0.4)),
                             (hx, hy + int(hd*1.1))])
        # Red eye lenses
        pygame.draw.circle(surface, (180, 20, 0), (hx - int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (180, 20, 0), (hx + int(hd*0.35), hy), max(3, int(3*s)))

    elif char_name == "Bulwark":
        # Thick fortress plate with embossed tower emblem
        pygame.draw.rect(surface, (110, 120, 100),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (160, 175, 150),
                         (sx - int(11*s), sy, int(22*s), bl), max(2, int(2*s)), border_radius=max(2, int(3*s)))
        # Tower emblem on chest
        _tx, _ty = sx, sy + int(bl*0.35)
        pygame.draw.rect(surface, (80, 90, 70),
                         (_tx - int(5*s), _ty - int(7*s), int(10*s), int(14*s)), border_radius=max(1, int(s)))
        pygame.draw.rect(surface, (80, 90, 70),
                         (_tx - int(7*s), _ty + int(2*s), int(14*s), int(4*s)))
        # Battlements on top of tower
        for _bi in range(3):
            pygame.draw.rect(surface, (80, 90, 70),
                             (_tx - int(6*s) + _bi * int(4*s), _ty - int(10*s), int(3*s), int(4*s)))
        # Full-visor helmet
        pygame.draw.rect(surface, (120, 130, 110),
                         (hx - hd, hy - hd, int(hd*2), int(hd*2)), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (60, 70, 55),
                         (hx - int(hd*0.7), hy - int(hd*0.2), int(hd*1.4), int(hd*0.5)))

    elif char_name == "Assassin":
        # Near-black hooded robe with daggers on belt
        pygame.draw.rect(surface, (25, 15, 40),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Hood shadow over face
        pygame.draw.ellipse(surface, (20, 10, 35),
                            (hx - hd - int(2*s), hy - hd - int(4*s), int(hd*2+4*s), int(hd*1.5)))
        # Crossed daggers on chest
        _ax, _ay = sx, sy + int(bl*0.4)
        pygame.draw.line(surface, (160, 160, 180),
                         (_ax - int(6*s), _ay - int(5*s)), (_ax + int(6*s), _ay + int(5*s)), max(1, int(2*s)))
        pygame.draw.line(surface, (160, 160, 180),
                         (_ax + int(6*s), _ay - int(5*s)), (_ax - int(6*s), _ay + int(5*s)), max(1, int(2*s)))
        # Single glowing red eye under hood
        pygame.draw.circle(surface, (200, 0, 0), (hx, hy), max(2, int(2*s)))

    elif char_name == "Wrecking Ball":
        # Dark brown wrecking ball body with chain at shoulder
        pygame.draw.ellipse(surface, (85, 60, 35),
                            (sx - int(11*s), sy, int(22*s), bl))
        pygame.draw.ellipse(surface, (120, 90, 55),
                            (sx - int(11*s), sy, int(22*s), bl), max(1, int(2*s)))
        # Chain links at top
        for _cli in range(3):
            _cly = sy - int((1 + _cli * 4)*s)
            pygame.draw.ellipse(surface, (80, 80, 80),
                                (sx - int(3*s), _cly, int(6*s), int(4*s)), max(1, int(s)))
        # Spike studs on body
        for _sdi in range(4):
            _sdangle = math.radians(_sdi * 90 + 45)
            _sdx = sx + int(math.cos(_sdangle) * int(8*s))
            _sdy = sy + bl//2 + int(math.sin(_sdangle) * int(7*s))
            pygame.draw.polygon(surface, (140, 110, 70),
                                [(_sdx, _sdy - int(4*s)), (_sdx - int(3*s), _sdy + int(3*s)),
                                 (_sdx + int(3*s), _sdy + int(3*s))])
        # Mean squinting eyes
        pygame.draw.line(surface, (30, 20, 10),
                         (hx - int(hd*0.5), hy - int(hd*0.15)),
                         (hx - int(hd*0.1), hy + int(hd*0.1)), max(1, int(2*s)))
        pygame.draw.line(surface, (30, 20, 10),
                         (hx + int(hd*0.5), hy - int(hd*0.15)),
                         (hx + int(hd*0.1), hy + int(hd*0.1)), max(1, int(2*s)))

    elif char_name == "Bounty Hunter":
        # Dusty tan duster coat with star badge and wide-brim hat
        pygame.draw.rect(surface, (150, 120, 55),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Coat trim lines
        pygame.draw.line(surface, (110, 85, 35),
                         (sx, sy), (sx, sy + bl), max(1, int(s)))
        # Star badge on chest
        _ba = sy + int(bl*0.3)
        for _si2 in range(5):
            _a1 = math.radians(_si2 * 72 - 90)
            _a2 = math.radians(_si2 * 72 + 36 - 90)
            pygame.draw.line(surface, (220, 200, 60),
                             (sx + int(math.cos(_a1)*int(5*s)), _ba + int(math.sin(_a1)*int(5*s))),
                             (sx + int(math.cos(_a2)*int(2*s)), _ba + int(math.sin(_a2)*int(2*s))),
                             max(1, int(s)))
        # Wide-brim hat
        pygame.draw.rect(surface, (100, 75, 30),
                         (hx - int(hd*0.5), hy - hd - int(12*s), int(hd), int(12*s)))
        pygame.draw.ellipse(surface, (100, 75, 30),
                            (hx - int(hd*0.95), hy - hd - int(4*s), int(hd*1.9), int(7*s)))

    elif char_name == "Abyssal":
        # Deep navy body with bioluminescent spots and tentacle fringe
        _t_ab = pygame.time.get_ticks()
        pygame.draw.rect(surface, (18, 35, 70),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Bioluminescent glow spots
        for _bsi, (_bsx, _bsy_f) in enumerate([(-7, 0.2), (5, 0.3), (-3, 0.55), (6, 0.65), (-5, 0.8)]):
            _bpulse = int(abs(math.sin(_t_ab * 0.005 + _bsi)) * 40)
            pygame.draw.circle(surface, (0, 160 + _bpulse, 180 + _bpulse),
                               (sx + int(_bsx*s), sy + int(bl*_bsy_f)), max(2, int(2*s)))
        # Tentacle fringe at bottom
        for _ti2 in range(4):
            _tx2 = sx - int(9*s) + _ti2 * int(6*s)
            _twave = int(math.sin(_t_ab * 0.006 + _ti2 * 0.8) * int(4*s))
            pygame.draw.line(surface, (0, 100, 130),
                             (_tx2, sy + bl), (_tx2 + _twave, sy + bl + int(10*s)), max(2, int(2*s)))
        # Large hollow glowing eyes
        pygame.draw.circle(surface, (0, 200, 220), (hx - int(hd*0.4), hy), max(4, int(4*s)))
        pygame.draw.circle(surface, (0, 200, 220), (hx + int(hd*0.4), hy), max(4, int(4*s)))
        pygame.draw.circle(surface, (10, 20, 50), (hx - int(hd*0.4), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (10, 20, 50), (hx + int(hd*0.4), hy), max(2, int(2*s)))

    elif char_name == "Revenant King":
        # Dark purple burial shroud with crown and phoenix glow
        _t_rk = pygame.time.get_ticks()
        pygame.draw.rect(surface, (65, 25, 85),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Tattered shroud edges
        for _tei in range(5):
            _tex = sx - int(10*s) + _tei * int(5*s)
            _tel = int(4 + _tei % 3)*s
            pygame.draw.line(surface, (45, 15, 60),
                             (_tex, sy + bl), (_tex + int(math.sin(_t_rk*0.004+_tei)*int(3*s)), sy + bl + int(_tel)), max(1, int(s)))
        # Rising phoenix glow on chest
        _rkg = int(abs(math.sin(_t_rk * 0.003)) * 80)
        pygame.draw.circle(surface, (180 + _rkg, 60, 30), (sx, sy + int(bl*0.4)), max(4, int(5*s)), max(1, int(2*s)))
        # Five-spike undead crown
        for _ki2 in range(5):
            _kx2 = hx - int(hd*0.8) + _ki2 * int(hd*0.4)
            _kh2 = int((5 + (_ki2 % 2)*5)*s)
            pygame.draw.polygon(surface, (80, 30, 100),
                                [(_kx2, hy - hd), (_kx2 - int(2*s), hy - hd - _kh2),
                                 (_kx2 + int(2*s), hy - hd - _kh2)])
        # Hollow skull eyes
        pygame.draw.circle(surface, (240, 200, 255), (hx - int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (240, 200, 255), (hx + int(hd*0.35), hy), max(3, int(3*s)))

    elif char_name == "Shadow Lord":
        # Absolute black cloak with dissolving edges and piercing eyes
        _t_sl = pygame.time.get_ticks()
        _sl_surf = pygame.Surface((int(26*s), bl + int(10*s)), pygame.SRCALPHA)
        pygame.draw.rect(_sl_surf, (10, 5, 25, 230),
                         (int(2*s), 0, int(22*s), bl + int(10*s)), border_radius=max(2, int(4*s)))
        surface.blit(_sl_surf, (sx - int(13*s), sy))
        # Dissolving shadow particles
        for _spi in range(6):
            _spa = math.radians(_spi * 60 + _t_sl * 0.1)
            _spd = int(10 + _spi * 2) * s
            _spx = sx + int(math.cos(_spa) * _spd)
            _spy = sy + bl//2 + int(math.sin(_spa) * int(8*s))
            _spsurf = pygame.Surface((int(4*s), int(4*s)), pygame.SRCALPHA)
            pygame.draw.circle(_spsurf, (80, 40, 140, 120), (int(2*s), int(2*s)), max(1, int(2*s)))
            surface.blit(_spsurf, (_spx - int(2*s), _spy - int(2*s)))
        # Twin violet piercing eyes
        pygame.draw.circle(surface, (140, 60, 255), (hx - int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (140, 60, 255), (hx + int(hd*0.35), hy), max(3, int(3*s)))

    elif char_name == "Rune Mage":
        # Deep violet robe with animated rune glyphs
        _t_rm = pygame.time.get_ticks()
        pygame.draw.rect(surface, (100, 65, 180),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Rune glyphs that cycle on the robe
        _rune_chars = ["ᚠ", "ᚢ", "ᚦ", "ᚨ", "ᚱ"]
        _rfont = pygame.font.SysFont("Arial", max(7, int(8*s)), bold=True)
        for _rui, (_rx, _ry_f) in enumerate([(-5, 0.2), (4, 0.4), (-4, 0.65), (5, 0.8)]):
            _rc = (_rui + _t_rm // 800) % len(_rune_chars)
            _rs2 = _rfont.render(_rune_chars[_rc], True, (200, 160, 255))
            surface.blit(_rs2, (sx + int(_rx*s) - _rs2.get_width()//2,
                                sy + int(bl*_ry_f) - _rs2.get_height()//2))
        # Glowing orb orbiting the head
        _orb_a = _t_rm * 0.004
        _orb_x = hx + int(math.cos(_orb_a) * int((hd+6)*s))
        _orb_y = hy - hd//2 + int(math.sin(_orb_a) * int(5*s))
        pygame.draw.circle(surface, (160, 100, 255), (_orb_x, _orb_y), max(3, int(3*s)))
        pygame.draw.circle(surface, (220, 180, 255), (_orb_x, _orb_y), max(1, int(s)))

    elif char_name == "Berserker Monk":
        # Burnt-orange gi with black sash and monk beads
        pygame.draw.rect(surface, (170, 75, 18),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Black sash diagonal
        pygame.draw.polygon(surface, (20, 15, 10),
                            [(sx - int(11*s), sy + int(bl*0.3)),
                             (sx + int(11*s), sy + int(bl*0.5)),
                             (sx + int(11*s), sy + int(bl*0.6)),
                             (sx - int(11*s), sy + int(bl*0.4))])
        # Prayer bead string around neck
        for _bi2 in range(7):
            _ba2 = math.radians(_bi2 * 25 - 45)
            _bx2 = hx + int(math.cos(_ba2) * int((hd+2)*s))
            _by2 = hy + int(hd*0.5) + int(math.sin(_ba2) * int(3*s))
            pygame.draw.circle(surface, (80, 40, 10), (_bx2, _by2), max(2, int(2*s)))
        # Shaved head with furrowed brow lines
        pygame.draw.line(surface, (140, 60, 15),
                         (hx - int(hd*0.4), hy - int(hd*0.2)),
                         (hx - int(hd*0.1), hy - int(hd*0.1)), max(1, int(2*s)))
        pygame.draw.line(surface, (140, 60, 15),
                         (hx + int(hd*0.4), hy - int(hd*0.2)),
                         (hx + int(hd*0.1), hy - int(hd*0.1)), max(1, int(2*s)))

    elif char_name == "Eggshell":
        # Cream-white ovoid body with hairline crack pattern
        pygame.draw.ellipse(surface, (255, 250, 230),
                            (sx - int(10*s), sy, int(20*s), bl))
        pygame.draw.ellipse(surface, (220, 210, 190),
                            (sx - int(10*s), sy, int(20*s), bl), max(1, int(s)))
        # Crack lines — jagged fractures across the shell
        _crack_pts = [
            [(sx - int(2*s), sy + int(bl*0.2)), (sx + int(4*s), sy + int(bl*0.35)),
             (sx + int(1*s), sy + int(bl*0.55)), (sx + int(5*s), sy + int(bl*0.7))],
            [(sx - int(5*s), sy + int(bl*0.4)), (sx - int(2*s), sy + int(bl*0.5)),
             (sx - int(6*s), sy + int(bl*0.65))],
        ]
        for _cpts in _crack_pts:
            for _ci2 in range(len(_cpts) - 1):
                pygame.draw.line(surface, (180, 160, 140),
                                 _cpts[_ci2], _cpts[_ci2 + 1], max(1, int(s)))
        # Tiny wide frightened eyes
        pygame.draw.circle(surface, (50, 50, 50), (hx - int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (50, 50, 50), (hx + int(hd*0.35), hy), max(3, int(3*s)))
        pygame.draw.circle(surface, (255, 255, 255), (hx - int(hd*0.35) + max(1,int(s)), hy - max(1,int(s))), max(1, int(s)))
        pygame.draw.circle(surface, (255, 255, 255), (hx + int(hd*0.35) + max(1,int(s)), hy - max(1,int(s))), max(1, int(s)))

    elif char_name == "Steel Knuckle":
        # Dark brown gi body with brass-coloured sash
        pygame.draw.rect(surface, (80, 50, 20),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (140, 100, 40),
                         (sx - int(3*s), sy, int(6*s), bl))
        # Iron gauntlets — bright brass rectangles over hands
        for _gx in (lhx, rhx):
            pygame.draw.rect(surface, (190, 150, 50),
                             (_gx - int(5*s), lhy - int(4*s), int(10*s), int(8*s)), border_radius=2)
            pygame.draw.rect(surface, (220, 185, 80),
                             (_gx - int(5*s), lhy - int(4*s), int(10*s), int(8*s)), 1, border_radius=2)
        # Stern brow lines on forehead
        pygame.draw.line(surface, (60, 35, 10),
                         (hx - int(hd*0.45), hy - int(hd*0.15)),
                         (hx - int(hd*0.1),  hy + int(hd*0.05)), max(1, int(2*s)))
        pygame.draw.line(surface, (60, 35, 10),
                         (hx + int(hd*0.45), hy - int(hd*0.15)),
                         (hx + int(hd*0.1),  hy + int(hd*0.05)), max(1, int(2*s)))

    elif char_name == "Crystal Bomber":
        # Crystalline amber body with glowing yellow fracture lines
        pygame.draw.rect(surface, (255, 210, 60),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(4*s)))
        pygame.draw.rect(surface, (255, 240, 150),
                         (sx - int(10*s), sy, int(20*s), bl), 1, border_radius=max(2, int(4*s)))
        # Internal fracture glow lines
        _fpts = [(sx - int(4*s), sy + int(bl*0.15)), (sx + int(6*s), sy + int(bl*0.4)),
                 (sx - int(2*s), sy + int(bl*0.6)), (sx + int(5*s), sy + int(bl*0.85))]
        for _fi in range(len(_fpts) - 1):
            pygame.draw.line(surface, (255, 255, 200), _fpts[_fi], _fpts[_fi+1], max(1, int(s)))
        # Faceted crystal helmet shard above head
        _hat_pts = [(hx - int(hd*0.6), hy - int(hd*0.9)),
                    (hx, hy - int(hd*1.7)),
                    (hx + int(hd*0.6), hy - int(hd*0.9))]
        pygame.draw.polygon(surface, (255, 235, 120), _hat_pts)
        pygame.draw.polygon(surface, (255, 255, 200), _hat_pts, 1)

    elif char_name == "Veteran":
        # Olive-drab military jacket body
        pygame.draw.rect(surface, (70, 80, 50),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Gold medals row on chest
        for _mi, _mc in enumerate([(220,180,30),(200,160,20),(180,140,10)]):
            pygame.draw.circle(surface, _mc,
                               (sx - int(6*s) + _mi * int(6*s), sy + int(bl*0.35)),
                               max(2, int(3*s)))
        # Epaulette bars on shoulders
        pygame.draw.rect(surface, (180, 150, 30),
                         (sx - int(12*s), sy - int(2*s), int(6*s), int(4*s)))
        pygame.draw.rect(surface, (180, 150, 30),
                         (sx + int(6*s),  sy - int(2*s), int(6*s), int(4*s)))
        # Grey beard below face
        pygame.draw.ellipse(surface, (160, 160, 160),
                            (hx - int(hd*0.5), hy + int(hd*0.3), int(hd), int(hd*0.7)))
        # Beret — flat cap on top
        pygame.draw.ellipse(surface, (60, 70, 40),
                            (hx - int(hd*0.85), hy - int(hd*1.05), int(hd*1.7), int(hd*0.6)))

    elif char_name == "Strigone":
        # Black caped body with crimson lining
        pygame.draw.rect(surface, (20, 10, 30),
                         (sx - int(13*s), sy, int(26*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.polygon(surface, (120, 0, 30),
                            [(sx - int(13*s), sy + int(bl*0.2)),
                             (sx - int(13*s), sy + bl),
                             (sx - int(3*s), sy + int(bl*0.55))])
        pygame.draw.polygon(surface, (120, 0, 30),
                            [(sx + int(13*s), sy + int(bl*0.2)),
                             (sx + int(13*s), sy + bl),
                             (sx + int(3*s), sy + int(bl*0.55))])
        # Widow's peak hairline
        pygame.draw.polygon(surface, (10, 5, 20),
                            [(hx - int(hd*0.8), hy - int(hd*0.9)),
                             (hx, hy - int(hd*0.5)),
                             (hx + int(hd*0.8), hy - int(hd*0.9))])
        # Glowing red eyes
        pygame.draw.circle(surface, (220, 20, 20), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (220, 20, 20), (hx + int(hd*0.32), hy), max(2, int(3*s)))
        # White fangs
        pygame.draw.polygon(surface, (250, 245, 240),
                            [(hx - int(hd*0.18), hy + int(hd*0.3)),
                             (hx - int(hd*0.06), hy + int(hd*0.55)),
                             (hx - int(hd*0.06), hy + int(hd*0.3))])
        pygame.draw.polygon(surface, (250, 245, 240),
                            [(hx + int(hd*0.06), hy + int(hd*0.3)),
                             (hx + int(hd*0.18), hy + int(hd*0.55)),
                             (hx + int(hd*0.18), hy + int(hd*0.3))])

    elif char_name == "Legionnaire":
        # Bronze leather armour body
        pygame.draw.rect(surface, (160, 110, 30),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Muscle-plate lines on chest
        pygame.draw.arc(surface, (200, 145, 50),
                        (sx - int(9*s), sy + int(bl*0.1), int(18*s), int(bl*0.35)),
                        0, math.pi, max(1, int(2*s)))
        pygame.draw.line(surface, (200, 145, 50),
                         (sx, sy + int(bl*0.1)), (sx, sy + int(bl*0.45)), max(1, int(2*s)))
        # Crested helmet — dome with tall centre fin
        pygame.draw.ellipse(surface, (180, 120, 35),
                            (hx - int(hd*0.95), hy - int(hd*1.1), int(hd*1.9), int(hd*1.1)))
        pygame.draw.rect(surface, (200, 140, 40),
                         (hx - int(2*s), hy - int(hd*2.0), int(4*s), int(hd*0.95)))
        # Visor slit
        pygame.draw.rect(surface, (30, 20, 10),
                         (hx - int(hd*0.6), hy - int(hd*0.15), int(hd*1.2), int(hd*0.3)))

    elif char_name == "Shadowbind":
        # Dark purple robe body with hex sigil
        pygame.draw.rect(surface, (70, 15, 70),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(4*s)))
        # Hex sigil (Star of David style) on chest
        _hcx, _hcy = sx, sy + int(bl*0.4)
        _hr = int(7*s)
        for _ha in range(0, 360, 60):
            _ax = _hcx + int(math.cos(math.radians(_ha)) * _hr)
            _ay = _hcy + int(math.sin(math.radians(_ha)) * _hr)
            _bx = _hcx + int(math.cos(math.radians(_ha + 180)) * _hr)
            _by = _hcy + int(math.sin(math.radians(_ha + 180)) * _hr)
            pygame.draw.line(surface, (200, 100, 200), (_ax, _ay), (_bx, _by), max(1, int(s)))
        # Tall pointed hat
        pygame.draw.polygon(surface, (80, 20, 80),
                            [(hx - int(hd*0.85), hy - int(hd*0.85)),
                             (hx, hy - int(hd*2.5)),
                             (hx + int(hd*0.85), hy - int(hd*0.85))])
        pygame.draw.polygon(surface, (150, 60, 150),
                            [(hx - int(hd*0.85), hy - int(hd*0.85)),
                             (hx, hy - int(hd*2.5)),
                             (hx + int(hd*0.85), hy - int(hd*0.85))], 1)
        # Glowing purple eyes
        pygame.draw.circle(surface, (200, 80, 200), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (200, 80, 200), (hx + int(hd*0.32), hy), max(2, int(3*s)))

    elif char_name == "Stone Golem":
        # Grey stone angular body
        pygame.draw.rect(surface, (90, 85, 75),
                         (sx - int(14*s), sy, int(28*s), bl), border_radius=max(1, int(2*s)))
        # Rock crack lines
        pygame.draw.line(surface, (60, 55, 50),
                         (sx - int(8*s), sy + int(bl*0.2)), (sx + int(5*s), sy + int(bl*0.5)),
                         max(1, int(2*s)))
        pygame.draw.line(surface, (60, 55, 50),
                         (sx + int(8*s), sy + int(bl*0.1)), (sx, sy + int(bl*0.45)),
                         max(1, int(2*s)))
        # Mossy top patches
        for _mx, _my in [(-8, 0.05), (4, 0.08), (-2, 0.02)]:
            pygame.draw.ellipse(surface, (60, 90, 40),
                                (sx + int(_mx*s), sy + int(bl*_my), int(8*s), int(4*s)))
        # Glowing orange eyes embedded in stone head
        pygame.draw.circle(surface, (240, 100, 20), (hx - int(hd*0.35), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (240, 100, 20), (hx + int(hd*0.35), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (255, 200, 80), (hx - int(hd*0.35), hy), max(1, int(2*s)))
        pygame.draw.circle(surface, (255, 200, 80), (hx + int(hd*0.35), hy), max(1, int(2*s)))

    elif char_name == "Storm Rider":
        # Electric blue bodysuit
        pygame.draw.rect(surface, (30, 110, 220),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Lightning bolt stripe down the centre
        _lpts = [(sx, sy), (sx + int(6*s), sy + int(bl*0.35)),
                 (sx - int(4*s), sy + int(bl*0.5)), (sx + int(6*s), sy + bl)]
        for _li in range(len(_lpts) - 1):
            pygame.draw.line(surface, (220, 240, 255), _lpts[_li], _lpts[_li+1], max(1, int(2*s)))
        # Electric sparks at hands
        for _ex, _ey in [(lhx, lhy), (rhx, rhy)]:
            for _ea in range(0, 360, 72):
                _r2 = max(3, int(5*s))
                _epx = _ex + int(math.cos(math.radians(_ea)) * _r2)
                _epy = _ey + int(math.sin(math.radians(_ea)) * _r2)
                pygame.draw.line(surface, (180, 230, 255), (_ex, _ey), (_epx, _epy),
                                 max(1, int(s)))
        # Goggle visor
        pygame.draw.ellipse(surface, (20, 180, 255),
                            (hx - int(hd*0.7), hy - int(hd*0.25), int(hd*1.4), int(hd*0.5)))

    elif char_name == "Frostbite":
        # Icy pale-blue armour body
        pygame.draw.rect(surface, (150, 200, 240),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Frost crystal spikes along shoulders
        for _fi, _fx in enumerate([-10, -5, 0, 5, 10]):
            _fh = int((6 - abs(_fi - 2)) * 3 * s)
            pygame.draw.polygon(surface, (220, 240, 255),
                                [(sx + int(_fx*s), sy),
                                 (sx + int(_fx*s) - int(2*s), sy - _fh),
                                 (sx + int(_fx*s) + int(2*s), sy - _fh)])
        # Icy beard / frost mask under face
        pygame.draw.ellipse(surface, (200, 230, 255),
                            (hx - int(hd*0.55), hy + int(hd*0.15), int(hd*1.1), int(hd*0.65)))
        # Glowing icy eyes
        pygame.draw.circle(surface, (100, 200, 255), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (100, 200, 255), (hx + int(hd*0.32), hy), max(2, int(3*s)))

    elif char_name == "Blood Mage":
        # Deep crimson robe body
        pygame.draw.rect(surface, (130, 10, 40),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(4*s)))
        # Blood-red drip marks down the front
        for _bx, _bfrom, _bto in [(-5, 0.1, 0.4), (1, 0.05, 0.35), (6, 0.15, 0.5)]:
            pygame.draw.line(surface, (200, 10, 30),
                             (sx + int(_bx*s), sy + int(bl*_bfrom)),
                             (sx + int(_bx*s), sy + int(bl*_bto)),
                             max(1, int(2*s)))
            pygame.draw.circle(surface, (200, 10, 30),
                               (sx + int(_bx*s), sy + int(bl*_bto)), max(2, int(2*s)))
        # Blood sigil circle on chest
        pygame.draw.circle(surface, (220, 20, 50),
                           (sx, sy + int(bl*0.35)), max(4, int(5*s)), max(1, int(s)))
        # Glowing red eyes
        pygame.draw.circle(surface, (255, 30, 30), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (255, 30, 30), (hx + int(hd*0.32), hy), max(2, int(3*s)))

    elif char_name == "Mirror Knight":
        # Polished silver chrome body
        pygame.draw.rect(surface, (190, 200, 215),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Chrome shine highlight diagonal
        pygame.draw.polygon(surface, (235, 242, 250),
                            [(sx - int(9*s), sy + int(bl*0.08)),
                             (sx - int(2*s), sy + int(bl*0.08)),
                             (sx - int(6*s), sy + int(bl*0.4)),
                             (sx - int(11*s), sy + int(bl*0.4))])
        # Rivets at armour edges
        for _ry in [0.2, 0.5, 0.8]:
            pygame.draw.circle(surface, (150, 160, 175),
                               (sx - int(10*s), sy + int(bl*_ry)), max(1, int(2*s)))
            pygame.draw.circle(surface, (150, 160, 175),
                               (sx + int(10*s), sy + int(bl*_ry)), max(1, int(2*s)))
        # Chrome visor across face
        pygame.draw.rect(surface, (200, 210, 225),
                         (hx - int(hd*0.75), hy - int(hd*0.2), int(hd*1.5), int(hd*0.4)),
                         border_radius=2)
        pygame.draw.rect(surface, (230, 240, 250),
                         (hx - int(hd*0.75), hy - int(hd*0.2), int(hd*1.5), int(hd*0.4)), 1,
                         border_radius=2)

    elif char_name == "Desperado":
        # Tan poncho body
        pygame.draw.rect(surface, (180, 140, 70),
                         (sx - int(14*s), sy, int(28*s), bl), border_radius=max(2, int(4*s)))
        # Poncho fringe at bottom
        for _pi in range(-12, 13, 4):
            pygame.draw.line(surface, (150, 110, 50),
                             (sx + int(_pi*s), sy + bl),
                             (sx + int(_pi*s), sy + bl + int(6*s)), max(1, int(s)))
        # Holster belt stripe
        pygame.draw.rect(surface, (100, 70, 30),
                         (sx - int(11*s), sy + int(bl*0.65), int(22*s), int(4*s)))
        # Brim of wide cowboy hat
        pygame.draw.ellipse(surface, (100, 70, 30),
                            (hx - int(hd*1.15), hy - int(hd*0.95), int(hd*2.3), int(hd*0.55)))
        pygame.draw.rect(surface, (80, 55, 20),
                         (hx - int(hd*0.8), hy - int(hd*1.55), int(hd*1.6), int(hd*0.7)),
                         border_radius=3)

    elif char_name == "Tomb Raider":
        # Khaki explorer jacket body
        pygame.draw.rect(surface, (120, 100, 60),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Utility belt
        pygame.draw.rect(surface, (80, 60, 30),
                         (sx - int(11*s), sy + int(bl*0.6), int(22*s), int(5*s)))
        # Rope coil on hip
        for _ri in range(4):
            pygame.draw.circle(surface, (160, 130, 70),
                               (sx + int(9*s), sy + int(bl*0.7) + _ri * int(2*s)),
                               max(2, int(2*s)), max(1, int(s)))
        # Headlamp circle on forehead
        pygame.draw.circle(surface, (255, 240, 180),
                           (hx, hy - int(hd*0.55)), max(3, int(4*s)))
        pygame.draw.circle(surface, (255, 255, 220),
                           (hx, hy - int(hd*0.55)), max(1, int(2*s)))
        pygame.draw.rect(surface, (60, 50, 30),
                         (hx - int(hd*0.5), hy - int(hd*1.05), int(hd), int(hd*0.45)),
                         border_radius=2)

    elif char_name == "Chronomancer":
        # Deep burgundy long coat body
        pygame.draw.rect(surface, (90, 20, 50),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(4*s)))
        # Clock face on chest
        pygame.draw.circle(surface, (220, 200, 160),
                           (sx, sy + int(bl*0.38)), max(5, int(6*s)))
        pygame.draw.circle(surface, (60, 20, 40),
                           (sx, sy + int(bl*0.38)), max(5, int(6*s)), 1)
        pygame.draw.line(surface, (60, 20, 40),
                         (sx, sy + int(bl*0.38)),
                         (sx, sy + int(bl*0.38) - int(4*s)), max(1, int(s)))
        pygame.draw.line(surface, (60, 20, 40),
                         (sx, sy + int(bl*0.38)),
                         (sx + int(3*s), sy + int(bl*0.38)), max(1, int(s)))
        # Pocket watch chain
        pygame.draw.arc(surface, (180, 150, 60),
                        (sx - int(6*s), sy + int(bl*0.3), int(12*s), int(bl*0.35)),
                        0, math.pi, max(1, int(s)))
        # Tall collar spikes
        pygame.draw.polygon(surface, (110, 30, 60),
                            [(sx - int(11*s), sy),
                             (sx - int(8*s), sy - int(8*s)),
                             (sx - int(5*s), sy)])
        pygame.draw.polygon(surface, (110, 30, 60),
                            [(sx + int(5*s), sy),
                             (sx + int(8*s), sy - int(8*s)),
                             (sx + int(11*s), sy)])
        # Glowing teal eyes
        pygame.draw.circle(surface, (60, 210, 210), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (60, 210, 210), (hx + int(hd*0.32), hy), max(2, int(3*s)))

    elif char_name == "Boom-Boom-Boomerang":
        # Bright orange jumpsuit body with concentric arc pattern
        pygame.draw.rect(surface, (220, 130, 15),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Boomerang arc symbols on chest — nested arcs
        for _bri in range(3):
            _brad = int((4 + _bri * 4) * s)
            pygame.draw.arc(surface, (255, 200, 50),
                            (sx - _brad, sy + int(bl*0.3) - _brad,
                             _brad * 2, _brad * 2),
                            math.radians(30), math.radians(150), max(1, int(s)))
        # Spinning yellow ring around head to suggest orbit
        for _bni in range(5):
            _bna = math.radians(_bni * 72)
            _bnx = hx + int(math.cos(_bna) * int(hd * 1.15))
            _bny = hy + int(math.sin(_bna) * int(hd * 0.5))
            pygame.draw.circle(surface, (255, 200, 40), (_bnx, _bny), max(2, int(3*s)))
        # Wide grinning mouth
        pygame.draw.arc(surface, (50, 30, 10),
                        (hx - int(hd*0.5), hy + int(hd*0.1), int(hd), int(hd*0.5)),
                        math.radians(200), math.radians(340), max(1, int(2*s)))

    elif char_name == "Behemoth":
        # Blue-grey stone plate armour — wide body
        pygame.draw.rect(surface, (50, 75, 110),
                         (sx - int(15*s), sy, int(30*s), bl), border_radius=max(2, int(3*s)))
        # Plate seam lines
        pygame.draw.line(surface, (40, 60, 90),
                         (sx, sy + int(bl*0.1)), (sx, sy + int(bl*0.9)), max(1, int(2*s)))
        pygame.draw.line(surface, (40, 60, 90),
                         (sx - int(15*s), sy + int(bl*0.5)), (sx + int(15*s), sy + int(bl*0.5)),
                         max(1, int(2*s)))
        # Massive pauldron plates on shoulders
        pygame.draw.ellipse(surface, (60, 90, 130),
                            (sx - int(20*s), sy - int(4*s), int(14*s), int(10*s)))
        pygame.draw.ellipse(surface, (60, 90, 130),
                            (sx + int(6*s), sy - int(4*s), int(14*s), int(10*s)))
        # Glowing blue eyes under heavy brow
        pygame.draw.rect(surface, (30, 50, 80),
                         (hx - int(hd*0.7), hy - int(hd*0.3), int(hd*1.4), int(hd*0.35)))
        pygame.draw.circle(surface, (80, 160, 255), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (80, 160, 255), (hx + int(hd*0.32), hy), max(2, int(3*s)))

    elif char_name == "Marauder":
        # Dark red brigandine — riveted leather plates
        pygame.draw.rect(surface, (140, 30, 30),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(2*s)))
        for _ri in range(3):
            pygame.draw.circle(surface, (100, 15, 15),
                                (sx, sy + int((_ri+1) * bl//4)), max(2, int(3*s)))
        # Raider bandana across lower face
        pygame.draw.rect(surface, (80, 10, 10),
                         (hx - int(hd*0.65), hy + int(hd*0.1), int(hd*1.3), int(hd*0.4)),
                         border_radius=max(1, int(2*s)))
        # Fierce eyes above bandana
        pygame.draw.circle(surface, (255, 80, 0), (hx - int(hd*0.3), hy - int(hd*0.1)), max(1, int(2*s)))
        pygame.draw.circle(surface, (255, 80, 0), (hx + int(hd*0.3), hy - int(hd*0.1)), max(1, int(2*s)))

    elif char_name == "Seraph":
        # White-gold robe with golden trim
        pygame.draw.rect(surface, (245, 240, 200),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (220, 185, 60),
                         (sx - int(9*s), sy, int(18*s), int(5*s)), border_radius=max(1, int(2*s)))
        # Halo above head
        pygame.draw.circle(surface, (255, 215, 0),
                            (hx, hy - int(hd*1.3)), int(hd*0.85), max(2, int(3*s)))
        # Two white wings arcing outward
        pygame.draw.ellipse(surface, (240, 240, 255),
                            (sx - int(22*s), sy + int(4*s), int(16*s), int(bl//2)))
        pygame.draw.ellipse(surface, (240, 240, 255),
                            (sx + int(6*s), sy + int(4*s), int(16*s), int(bl//2)))
        # Serene closed eyes
        pygame.draw.line(surface, (180, 140, 60),
                         (hx - int(hd*0.4), hy), (hx - int(hd*0.1), hy - int(hd*0.1)),
                         max(1, int(2*s)))
        pygame.draw.line(surface, (180, 140, 60),
                         (hx + int(hd*0.1), hy - int(hd*0.1)), (hx + int(hd*0.4), hy),
                         max(1, int(2*s)))

    elif char_name == "Typhoon":
        # Deep blue storm coat with swirling stripe
        pygame.draw.rect(surface, (30, 100, 180),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.arc(surface, (160, 220, 255),
                        (sx - int(8*s), sy + int(bl*0.2), int(16*s), int(bl*0.55)),
                        0.3, 2.8, max(2, int(3*s)))
        # Wind-blown hair streaks on head
        for _wi in range(3):
            pygame.draw.line(surface, (180, 230, 255),
                             (hx + int((_wi-1)*hd*0.3), hy - int(hd*0.9)),
                             (hx + int((_wi-1)*hd*0.3) + int(4*s*facing if facing else 3),
                              hy - int(hd*1.4)), max(1, int(2*s)))
        # Squinting storm eyes
        pygame.draw.line(surface, (200, 240, 255),
                         (hx - int(hd*0.4), hy - int(hd*0.05)),
                         (hx - int(hd*0.1), hy - int(hd*0.05)), max(1, int(2*s)))
        pygame.draw.line(surface, (200, 240, 255),
                         (hx + int(hd*0.1), hy - int(hd*0.05)),
                         (hx + int(hd*0.4), hy - int(hd*0.05)), max(1, int(2*s)))

    elif char_name == "Ironveil":
        # Layered dark-iron full-plate body
        pygame.draw.rect(surface, (60, 60, 70),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(3*s)))
        # Chest plate highlight
        pygame.draw.rect(surface, (80, 85, 95),
                         (sx - int(9*s), sy + int(bl*0.1), int(18*s), int(bl*0.45)),
                         border_radius=max(1, int(2*s)))
        # Horizontal plate seams
        for _pi in range(3):
            pygame.draw.line(surface, (45, 45, 55),
                             (sx - int(12*s), sy + int(bl*(_pi+1)//4)),
                             (sx + int(12*s), sy + int(bl*(_pi+1)//4)),
                             max(1, int(2*s)))
        # Great helm — full head cover
        pygame.draw.rect(surface, (60, 60, 70),
                         (hx - int(hd*1.05), hy - int(hd*1.1), int(hd*2.1), int(hd*2.2)),
                         border_radius=max(2, int(4*s)))
        # Visor slit
        pygame.draw.rect(surface, (30, 30, 35),
                         (hx - int(hd*0.6), hy - int(hd*0.1), int(hd*1.2), int(hd*0.25)))

    elif char_name == "Pulse":
        # Cyan electric bodysuit
        pygame.draw.rect(surface, (20, 180, 200),
                         (sx - int(8*s), sy, int(16*s), bl), border_radius=max(2, int(3*s)))
        # Zigzag lightning stripe down torso
        _pts = [(sx - int(2*s), sy + int(bl*0.1)),
                (sx + int(5*s), sy + int(bl*0.3)),
                (sx - int(5*s), sy + int(bl*0.55)),
                (sx + int(2*s), sy + int(bl*0.8))]
        if len(_pts) >= 2:
            pygame.draw.lines(surface, (255, 255, 100), False, _pts, max(2, int(3*s)))
        # Glowing cyan eyes
        pygame.draw.circle(surface, (120, 255, 255), (hx - int(hd*0.3), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (120, 255, 255), (hx + int(hd*0.3), hy), max(2, int(3*s)))
        # Electric hair sparks
        pygame.draw.line(surface, (255, 255, 80),
                         (hx - int(hd*0.2), hy - int(hd)), (hx - int(hd*0.5), hy - int(hd*1.5)),
                         max(1, int(2*s)))
        pygame.draw.line(surface, (255, 255, 80),
                         (hx + int(hd*0.2), hy - int(hd)), (hx + int(hd*0.5), hy - int(hd*1.5)),
                         max(1, int(2*s)))

    elif char_name == "Gilded":
        # Rich gold-plated armour
        pygame.draw.rect(surface, (200, 165, 40),
                         (sx - int(11*s), sy, int(22*s), bl), border_radius=max(2, int(3*s)))
        # Ornate chest medallion
        pygame.draw.circle(surface, (240, 210, 80), (sx, sy + int(bl*0.35)), int(6*s))
        pygame.draw.circle(surface, (180, 140, 20), (sx, sy + int(bl*0.35)), int(4*s))
        # Gold crown on head
        _cpts = [(hx - int(hd*0.7), hy - int(hd*0.9)),
                 (hx - int(hd*0.7), hy - int(hd*1.3)),
                 (hx - int(hd*0.25), hy - int(hd*0.95)),
                 (hx, hy - int(hd*1.5)),
                 (hx + int(hd*0.25), hy - int(hd*0.95)),
                 (hx + int(hd*0.7), hy - int(hd*1.3)),
                 (hx + int(hd*0.7), hy - int(hd*0.9))]
        pygame.draw.lines(surface, (240, 200, 30), False, _cpts, max(2, int(3*s)))
        # Smug golden eyes
        pygame.draw.circle(surface, (60, 40, 0), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (60, 40, 0), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Dusk":
        # Deep purple twilight cloak
        pygame.draw.rect(surface, (80, 45, 110),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Cloak hem fades darker at bottom
        pygame.draw.rect(surface, (50, 25, 75),
                         (sx - int(10*s), sy + int(bl*0.6), int(20*s), int(bl*0.4)),
                         border_radius=max(2, int(3*s)))
        # Star pattern on cloak
        for _si in range(4):
            _stx = sx + int((_si - 1.5) * 5 * s)
            _sty = sy + int(bl * 0.3)
            pygame.draw.circle(surface, (200, 170, 255), (_stx, _sty), max(1, int(2*s)))
        # Shadowed hood over head
        pygame.draw.ellipse(surface, (60, 30, 90),
                            (hx - int(hd*1.1), hy - int(hd*1.2), int(hd*2.2), int(hd*1.4)))
        # Glowing violet eyes
        pygame.draw.circle(surface, (200, 130, 255), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (200, 130, 255), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Prism":
        # White base suit with rainbow shards overlaid
        pygame.draw.rect(surface, (230, 230, 235),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        _rcolors = [(255,60,60),(255,170,0),(60,200,60),(40,140,255),(180,60,255)]
        for _ri, _rc in enumerate(_rcolors):
            _ry = sy + int(bl * _ri / 5)
            pygame.draw.line(surface, _rc,
                             (sx - int(9*s), _ry), (sx + int(9*s), _ry + int(bl//10)),
                             max(1, int(2*s)))
        # Rainbow ring around head
        import math as _m
        for _ri in range(12):
            _ra = _m.radians(_ri * 30)
            _rx = int(hx + _m.cos(_ra) * hd * 1.2)
            _ry2 = int(hy + _m.sin(_ra) * hd * 1.2)
            pygame.draw.circle(surface, _rcolors[_ri % 5], (_rx, _ry2), max(1, int(2*s)))
        # Bright white pupils
        pygame.draw.circle(surface, (255,255,255), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (255,255,255), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Ashen":
        # Ash-grey padded coat with frost-blue trim
        pygame.draw.rect(surface, (145, 155, 165),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        pygame.draw.rect(surface, (100, 140, 190),
                         (sx - int(9*s), sy, int(18*s), int(5*s)), border_radius=max(1, int(2*s)))
        pygame.draw.rect(surface, (100, 140, 190),
                         (sx - int(9*s), sy + int(bl - 5*s), int(18*s), int(5*s)),
                         border_radius=max(1, int(2*s)))
        # Frost crystals on shoulders
        pygame.draw.polygon(surface, (180, 210, 240),
                            [(sx - int(11*s), sy),
                             (sx - int(8*s), sy - int(6*s)),
                             (sx - int(5*s), sy)])
        pygame.draw.polygon(surface, (180, 210, 240),
                            [(sx + int(5*s), sy),
                             (sx + int(8*s), sy - int(6*s)),
                             (sx + int(11*s), sy)])
        # Cold pale eyes
        pygame.draw.circle(surface, (210, 230, 255), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (210, 230, 255), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Ravager":
        # Blood-red battle-worn vest
        pygame.draw.rect(surface, (140, 20, 15),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(1, int(2*s)))
        # Torn diagonal slash marks on torso
        pygame.draw.line(surface, (90, 5, 5),
                         (sx - int(7*s), sy + int(bl*0.2)), (sx + int(5*s), sy + int(bl*0.5)),
                         max(2, int(3*s)))
        pygame.draw.line(surface, (90, 5, 5),
                         (sx - int(5*s), sy + int(bl*0.4)), (sx + int(7*s), sy + int(bl*0.7)),
                         max(2, int(3*s)))
        # Wild spiked hair
        for _ri in range(5):
            _hx2 = hx + int((_ri - 2) * hd * 0.35)
            pygame.draw.line(surface, (200, 20, 10),
                             (_hx2, hy - int(hd*0.9)), (_hx2 + int((_ri-2)*2*s), hy - int(hd*1.6)),
                             max(1, int(2*s)))
        # Fierce red eyes
        pygame.draw.circle(surface, (255, 60, 0), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (255, 60, 0), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Thornwall":
        # Deep olive armour studded with spines
        pygame.draw.rect(surface, (55, 95, 45),
                         (sx - int(12*s), sy, int(24*s), bl), border_radius=max(2, int(3*s)))
        # Thorn spikes along shoulders
        for _ti in range(4):
            _tx = sx - int(11*s) + int(_ti * 7 * s)
            pygame.draw.polygon(surface, (80, 130, 40),
                                [(_tx, sy), (_tx + int(3*s), sy - int(8*s)),
                                 (_tx + int(6*s), sy)])
        # Bark-textured lines on torso
        pygame.draw.line(surface, (40, 70, 30),
                         (sx - int(3*s), sy + int(bl*0.25)), (sx + int(3*s), sy + int(bl*0.55)),
                         max(1, int(2*s)))
        pygame.draw.line(surface, (40, 70, 30),
                         (sx - int(3*s), sy + int(bl*0.55)), (sx + int(3*s), sy + int(bl*0.8)),
                         max(1, int(2*s)))
        # Mossy green eyes
        pygame.draw.circle(surface, (100, 200, 60), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (100, 200, 60), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Diviner":
        # Dark crimson mage robes
        pygame.draw.rect(surface, (110, 20, 60),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        # Eye-of-fate symbol on chest
        pygame.draw.ellipse(surface, (200, 80, 120),
                            (sx - int(6*s), sy + int(bl*0.2), int(12*s), int(bl*0.3)))
        pygame.draw.circle(surface, (60, 0, 30), (sx, sy + int(bl*0.35)), int(3*s))
        # Flowing sash
        pygame.draw.rect(surface, (80, 10, 40),
                         (sx - int(4*s), sy + int(bl*0.55), int(8*s), int(bl*0.45)),
                         border_radius=max(1, int(2*s)))
        # Third eye on forehead
        pygame.draw.ellipse(surface, (255, 100, 160),
                            (hx - int(hd*0.2), hy - int(hd*0.7), int(hd*0.4), int(hd*0.3)))
        # Normal eyes
        pygame.draw.circle(surface, (220, 60, 100), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (220, 60, 100), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Cutlass":
        # Navy sea-captain coat
        pygame.draw.rect(surface, (20, 80, 140),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        # Gold epaulette strip on shoulder
        pygame.draw.rect(surface, (220, 180, 40),
                         (sx - int(10*s), sy, int(20*s), int(5*s)), border_radius=max(1, int(2*s)))
        # Skull-and-crossbones emblem on chest
        pygame.draw.circle(surface, (220, 220, 220), (sx, sy + int(bl*0.35)), int(4*s))
        pygame.draw.line(surface, (20, 80, 140),
                         (sx - int(4*s), sy + int(bl*0.35)), (sx + int(4*s), sy + int(bl*0.35)),
                         max(1, int(2*s)))
        pygame.draw.line(surface, (20, 80, 140),
                         (sx, sy + int(bl*0.28)), (sx, sy + int(bl*0.42)),
                         max(1, int(2*s)))
        # Tricorn hat
        pygame.draw.polygon(surface, (15, 50, 90),
                            [(hx - int(hd), hy - int(hd*0.85)),
                             (hx, hy - int(hd*1.6)),
                             (hx + int(hd), hy - int(hd*0.85))])
        # Bold eyes
        pygame.draw.circle(surface, (20, 200, 200), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (20, 200, 200), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Oathbreaker":
        # Tarnished dark brown broken-armour look
        pygame.draw.rect(surface, (65, 35, 15),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Cracked plate shards
        pygame.draw.polygon(surface, (90, 55, 20),
                            [(sx - int(10*s), sy + int(bl*0.1)),
                             (sx - int(3*s), sy + int(bl*0.35)),
                             (sx - int(10*s), sy + int(bl*0.5))])
        pygame.draw.polygon(surface, (90, 55, 20),
                            [(sx + int(3*s), sy + int(bl*0.2)),
                             (sx + int(10*s), sy + int(bl*0.1)),
                             (sx + int(10*s), sy + int(bl*0.45))])
        # Broken sigil scar on chest
        pygame.draw.line(surface, (40, 15, 5),
                         (sx - int(5*s), sy + int(bl*0.45)), (sx + int(5*s), sy + int(bl*0.65)),
                         max(2, int(3*s)))
        pygame.draw.line(surface, (40, 15, 5),
                         (sx + int(5*s), sy + int(bl*0.45)), (sx - int(5*s), sy + int(bl*0.65)),
                         max(2, int(3*s)))
        # Hollow dark eyes
        pygame.draw.circle(surface, (180, 100, 30), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (180, 100, 30), (hx + int(hd*0.3), hy), max(2, int(2*s)))

    elif char_name == "Kappa":
        # Deep teal scaly body
        pygame.draw.rect(surface, (25, 115, 80),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(3*s)))
        # Domed shell on back — dark green rounded oval
        pygame.draw.ellipse(surface, (15, 80, 50),
                            (sx - int(12*s), sy + int(bl*0.05), int(24*s), int(bl*0.75)))
        # Shell ridge lines
        pygame.draw.arc(surface, (10, 60, 35),
                        (sx - int(9*s), sy + int(bl*0.1), int(18*s), int(bl*0.6)),
                        0.3, 2.8, max(1, int(2*s)))
        pygame.draw.line(surface, (10, 60, 35),
                         (sx, sy + int(bl*0.1)), (sx, sy + int(bl*0.65)), max(1, int(s)))
        # Water dish on head — small flat blue circle
        pygame.draw.ellipse(surface, (60, 160, 220),
                            (hx - int(hd*0.75), hy - int(hd*1.25), int(hd*1.5), int(hd*0.45)))
        pygame.draw.ellipse(surface, (120, 200, 255),
                            (hx - int(hd*0.5), hy - int(hd*1.2), int(hd), int(hd*0.25)))
        # Beak / bill
        pygame.draw.polygon(surface, (50, 160, 100),
                            [(hx, hy + int(hd*0.3)),
                             (hx + int(hd*0.55) * facing, hy + int(hd*0.1)),
                             (hx + int(hd*0.35) * facing, hy + int(hd*0.5))])
        # Yellow eyes
        pygame.draw.circle(surface, (200, 220, 60), (hx - int(hd*0.3), hy - int(hd*0.1)), max(2, int(3*s)))
        pygame.draw.circle(surface, (200, 220, 60), (hx + int(hd*0.3), hy - int(hd*0.1)), max(2, int(3*s)))
        pygame.draw.circle(surface, (0, 0, 0), (hx - int(hd*0.3), hy - int(hd*0.1)), max(1, int(s)))
        pygame.draw.circle(surface, (0, 0, 0), (hx + int(hd*0.3), hy - int(hd*0.1)), max(1, int(s)))

    elif char_name == "Morrigan":
        # Deep purple-black phantom robes
        pygame.draw.rect(surface, (50, 10, 75),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(4*s)))
        # Jagged hem (crow feather silhouette)
        for _fi in range(5):
            _fx = sx - int(8*s) + int(_fi * 4 * s)
            pygame.draw.polygon(surface, (30, 5, 50),
                                [(_fx, sy + bl),
                                 (_fx + int(2*s), sy + bl + int(8*s)),
                                 (_fx + int(4*s), sy + bl)])
        # Crow-feather collar
        pygame.draw.ellipse(surface, (20, 0, 35),
                            (sx - int(11*s), sy - int(3*s), int(22*s), int(10*s)))
        # Crown of dark feathers
        for _fi in range(5):
            _fa = -60 + _fi * 30
            import math as _m
            _fr = _m.radians(_fa)
            _fpx = int(hx + _m.sin(_fr) * hd * 0.8)
            _fpy = int(hy - hd - int(6*s) - abs(_m.cos(_fr)) * 8 * s)
            pygame.draw.line(surface, (20, 0, 35),
                             (hx, hy - hd), (_fpx, _fpy), max(1, int(2*s)))
        # Glowing red eyes
        pygame.draw.circle(surface, (220, 20, 40), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (220, 20, 40), (hx + int(hd*0.32), hy), max(2, int(3*s)))

    elif char_name == "Badb":
        # Blood-red battle armour, worn and scarred
        pygame.draw.rect(surface, (155, 20, 20),
                         (sx - int(10*s), sy, int(20*s), bl), border_radius=max(2, int(2*s)))
        # Battle scars — diagonal gashes
        pygame.draw.line(surface, (100, 5, 5),
                         (sx - int(8*s), sy + int(bl*0.15)), (sx + int(4*s), sy + int(bl*0.45)),
                         max(2, int(3*s)))
        pygame.draw.line(surface, (100, 5, 5),
                         (sx - int(4*s), sy + int(bl*0.5)), (sx + int(8*s), sy + int(bl*0.75)),
                         max(2, int(3*s)))
        # Crow skull pauldron on shoulder
        pygame.draw.ellipse(surface, (80, 10, 10),
                            (sx - int(15*s), sy - int(2*s), int(12*s), int(9*s)))
        pygame.draw.circle(surface, (200, 180, 160),
                           (sx - int(9*s), sy + int(2*s)), max(2, int(2*s)))
        # Wild matted hair
        for _hi in range(5):
            _hx2 = hx + int((_hi - 2) * hd * 0.4)
            pygame.draw.line(surface, (60, 5, 5),
                             (_hx2, hy - int(hd*0.9)), (_hx2 + int((_hi-2)*2*s), hy - int(hd*1.7)),
                             max(1, int(2*s)))
        # Battle-crazed eyes
        pygame.draw.circle(surface, (255, 80, 0), (hx - int(hd*0.32), hy), max(2, int(3*s)))
        pygame.draw.circle(surface, (255, 80, 0), (hx + int(hd*0.32), hy), max(2, int(3*s)))

    elif char_name == "Nemain":
        # Burnt orange frenzied robes
        pygame.draw.rect(surface, (185, 75, 15),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        # Swirling chaos marks on torso
        import math as _m
        for _ni in range(3):
            _na = _m.radians(_ni * 120 + 30)
            _ncx = sx + int(_m.cos(_na) * 5 * s)
            _ncy = sy + int(bl*0.4) + int(_m.sin(_na) * 5 * s)
            pygame.draw.circle(surface, (230, 130, 30), (_ncx, _ncy), max(2, int(3*s)), max(1, int(s)))
        # Chaotic jagged lines radiating from center
        for _ni in range(6):
            _na2 = _m.radians(_ni * 60)
            _nx2 = sx + int(_m.cos(_na2) * 8 * s)
            _ny2 = sy + int(bl*0.4) + int(_m.sin(_na2) * 7 * s)
            pygame.draw.line(surface, (240, 160, 40), (sx, sy + int(bl*0.4)), (_nx2, _ny2),
                             max(1, int(s)))
        # Spiral eyes — the mark of panic
        pygame.draw.circle(surface, (255, 200, 60), (hx - int(hd*0.32), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (200, 80, 10), (hx - int(hd*0.32), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (255, 200, 60), (hx + int(hd*0.32), hy), max(3, int(4*s)))
        pygame.draw.circle(surface, (200, 80, 10), (hx + int(hd*0.32), hy), max(2, int(2*s)))

    elif char_name == "Anansi":
        # Rich amber-gold chitin body — spider deity
        pygame.draw.rect(surface, (165, 90, 15),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        # Web pattern on chest (5 radial lines from center)
        import math as _m
        _wc = (sx, sy + int(bl*0.35))
        for _wi in range(6):
            _wa = _m.radians(_wi * 30 - 90)
            _wx = int(_wc[0] + _m.cos(_wa) * 8 * s)
            _wy = int(_wc[1] + _m.sin(_wa) * 7 * s)
            pygame.draw.line(surface, (220, 180, 60), _wc, (_wx, _wy), max(1, int(s)))
        # Concentric web ring
        pygame.draw.circle(surface, (220, 180, 60), _wc, int(5*s), max(1, int(s)))
        # 4 spider legs on each side of torso (drawn thin)
        for _li in range(4):
            _ly = sy + int(bl * (_li * 0.22 + 0.1))
            _lx1 = sx - int(9*s)
            _lx2 = sx - int(20*s) + int(_li * 2 * s)
            _ly2 = _ly + int((_li - 1) * 4 * s)
            pygame.draw.line(surface, (130, 70, 10), (_lx1, _ly), (_lx2, _ly2), max(1, int(s)))
            _lx1r = sx + int(9*s)
            _lx2r = sx + int(20*s) - int(_li * 2 * s)
            pygame.draw.line(surface, (130, 70, 10), (_lx1r, _ly), (_lx2r, _ly2), max(1, int(s)))
        # Head — darker amber with 6 gleaming eyes in two rows
        pygame.draw.circle(surface, (145, 80, 10), (hx, hy), hd)
        _eye_cols = [(255, 220, 60), (200, 255, 60), (255, 200, 60)]
        for _ei, _ecol in enumerate(_eye_cols):
            _ex = hx + int((_ei - 1) * hd * 0.4)
            pygame.draw.circle(surface, _ecol, (_ex, hy - int(hd*0.2)), max(1, int(2*s)))
            pygame.draw.circle(surface, _ecol, (_ex, hy + int(hd*0.25)), max(1, int(2*s)))

    elif char_name == "Arcanist":
        # Deep violet mage robes with glowing rune trim
        pygame.draw.rect(surface, (90, 30, 160),
                         (sx - int(9*s), sy, int(18*s), bl), border_radius=max(2, int(3*s)))
        # Rune border down sides
        pygame.draw.line(surface, (180, 100, 255),
                         (sx - int(9*s), sy), (sx - int(9*s), sy + bl), max(1, int(2*s)))
        pygame.draw.line(surface, (180, 100, 255),
                         (sx + int(9*s), sy), (sx + int(9*s), sy + bl), max(1, int(2*s)))
        # Arcane circle on chest
        pygame.draw.circle(surface, (180, 100, 255),
                            (sx, sy + int(bl*0.35)), int(6*s), max(1, int(2*s)))
        pygame.draw.circle(surface, (220, 160, 255),
                            (sx, sy + int(bl*0.35)), int(3*s))
        # Pointed arcane hat
        pygame.draw.polygon(surface, (70, 20, 130),
                            [(hx - int(hd*0.9), hy - int(hd*0.8)),
                             (hx, hy - int(hd*2.0)),
                             (hx + int(hd*0.9), hy - int(hd*0.8))])
        # Star on hat tip
        pygame.draw.circle(surface, (220, 160, 255), (hx, hy - int(hd*2.0)), max(2, int(3*s)))
        # Glowing purple eyes
        pygame.draw.circle(surface, (200, 120, 255), (hx - int(hd*0.3), hy), max(2, int(2*s)))
        pygame.draw.circle(surface, (200, 120, 255), (hx + int(hd*0.3), hy), max(2, int(2*s)))


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

    # ── Snake: draw only classic snake-game blocks, no stickman ─────────────
    if char_name == "Snake":
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


