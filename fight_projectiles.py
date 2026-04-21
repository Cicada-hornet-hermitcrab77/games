import pygame
import math
import random
import constants
from constants import *

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
# BeeShot  (Beekeeper's bee swarm — small angled projectile with vy support)
# ---------------------------------------------------------------------------

class BeeShot:
    RADIUS = 5
    SPEED  = 8
    DMG    = 5

    def __init__(self, x, y, facing, owner, vy=0.0):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = self.SPEED * facing
        self.vy    = float(vy)
        self.owner = owner
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (230, 200, 0),  (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (30, 20, 0),    (cx, cy), self.RADIUS - 3)

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
# ChargedOrb (Orb Shooter — variable size/damage based on hold time)
# ---------------------------------------------------------------------------

class ChargedOrb:
    SPEED = 9

    def __init__(self, x, y, facing, owner, charge):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = self.SPEED * facing
        self.owner = owner
        self.r     = max(8, 8 + charge // 8)
        self.dmg   = max(10, 10 + charge // 6)
        self.alive = True

    def update(self):
        self.x += self.vx
        if self.x < -self.r or self.x > WIDTH + self.r:
            self.alive = False

    def collides(self, other):
        return (abs(self.x - other.x) < self.r + 22 and
                abs(self.y - (other.y - 60)) < self.r + 35)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (60, 120, 255), (cx, cy), self.r)
        pygame.draw.circle(surface, (160, 210, 255), (cx, cy), max(3, self.r // 2))
        pygame.draw.circle(surface, (220, 240, 255), (cx, cy), max(2, self.r // 4))


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
            self.vy += constants.GRAVITY
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
# FallingSkull
# ---------------------------------------------------------------------------

class FallingSkull:
    RADIUS   = 14
    GRAVITY  = 0.35
    DMG      = 12
    HIT_CD   = 50

    def __init__(self):
        self.x      = float(random.randint(60, WIDTH - 60))
        self.y      = 22.0
        self.vy     = random.uniform(1.5, 3.0)
        self.alive  = True
        self.hit_cd = 0
        self.landed = False
        self.roll   = 0.0   # roll velocity after landing

    def update(self):
        if self.hit_cd > 0:
            self.hit_cd -= 1
        if not self.landed:
            self.vy += self.GRAVITY
            self.y  += self.vy
            if self.y >= GROUND_Y - self.RADIUS:
                self.y      = GROUND_Y - self.RADIUS
                self.landed = True
                self.roll   = random.choice([-1.5, 1.5])
        else:
            self.x    += self.roll
            self.roll *= 0.94
            if self.x < 30 or self.x > WIDTH - 30:
                self.roll *= -1
            if abs(self.roll) < 0.05:
                self.roll = 0

    def collides(self, fighter):
        return math.hypot(fighter.x - self.x, (fighter.y - 40) - self.y) < self.RADIUS + 28

    def draw(self, surface):
        sx, sy = int(self.x), int(self.y)
        r = self.RADIUS
        # Skull cranium
        pygame.draw.circle(surface, (230, 220, 200), (sx, sy), r)
        pygame.draw.circle(surface, (80, 70, 60),    (sx, sy), r, 2)
        # Eye sockets
        for ex in [sx - r//3, sx + r//3]:
            pygame.draw.circle(surface, (20, 10, 30), (ex, sy - 2), r//4)
        # Nose
        pygame.draw.polygon(surface, (20, 10, 30), [
            (sx, sy + r//5), (sx - 3, sy + r//2), (sx + 3, sy + r//2)])
        # Teeth
        for tx in range(sx - r//2, sx + r//2, 6):
            pygame.draw.rect(surface, (20, 10, 30), (tx, sy + r//2, 4, r//3))


# ---------------------------------------------------------------------------
# Whip  (Whipper's long-range attack)
# ---------------------------------------------------------------------------

class Whip:
    """A cracking whip that extends 280 px in the owner's facing direction.

    Timeline (frames):
      0-11  : extending  — tip travels outward
      12-21 : retracting — tip travels back
      Total lifetime: 22 frames

    Damage is dealt once when the tip is fully extended (frame 10-14).
    Visual: a catenary rope drawn as a series of short segments that sag
    in the middle, with a bright tip flash on extension.
    """

    LENGTH      = 280    # max reach in pixels
    DMG         = 14     # tip damage
    LIFETIME    = 22     # total frames alive
    EXTEND_END  = 12     # frame at which tip is fully extended
    HIT_FRAMES  = (8, 16)  # window during which tip can deal damage

    def __init__(self, x, y, facing, owner):
        self.x       = float(x)
        self.y       = float(y)
        self.facing  = facing
        self.owner   = owner
        self.frame   = 0
        self.alive   = True
        self.hit_done = False   # only deal damage once

    def update(self):
        self.frame += 1
        if self.frame >= self.LIFETIME:
            self.alive = False

    def _tip_x(self):
        """Current x position of the whip tip."""
        f = self.frame
        if f <= self.EXTEND_END:
            progress = f / self.EXTEND_END
        else:
            progress = 1.0 - (f - self.EXTEND_END) / (self.LIFETIME - self.EXTEND_END)
        progress = max(0.0, min(1.0, progress))
        return self.x + self.facing * self.LENGTH * progress

    def can_hit(self):
        return self.HIT_FRAMES[0] <= self.frame <= self.HIT_FRAMES[1] and not self.hit_done

    def collides(self, fighter):
        """True if the tip region hits the fighter."""
        tip_x = self._tip_x()
        tip_y = self.y
        # Check several points along the outer third of the whip
        for t in (0.75, 0.85, 1.0):
            f = self.frame
            if f <= self.EXTEND_END:
                progress = f / self.EXTEND_END
            else:
                progress = 1.0 - (f - self.EXTEND_END) / (self.LIFETIME - self.EXTEND_END)
            progress = max(0.0, min(1.0, progress)) * t
            seg_x = self.x + self.facing * self.LENGTH * progress
            sag   = math.sin(progress * math.pi) * 40
            seg_y = self.y + sag
            if math.hypot(seg_x - fighter.x, seg_y - (fighter.y - 60)) < 34:
                return True
        return False

    def draw(self, surface):
        f = self.frame
        if f <= self.EXTEND_END:
            progress = f / self.EXTEND_END
        else:
            progress = 1.0 - (f - self.EXTEND_END) / (self.LIFETIME - self.EXTEND_END)
        progress = max(0.0, min(1.0, progress))

        # Draw rope as 14 segments with catenary sag
        segs = 14
        pts = []
        for i in range(segs + 1):
            t   = (i / segs) * progress
            sx  = self.x + self.facing * self.LENGTH * t
            sag = math.sin(t / progress * math.pi if progress > 0.01 else 0) * 40
            sy  = self.y + sag
            pts.append((int(sx), int(sy)))

        if len(pts) >= 2:
            # Brown rope
            pygame.draw.lines(surface, (110, 60, 20), False, pts, 3)
            pygame.draw.lines(surface, (160, 100, 40), False, pts, 1)

        # Bright crack at tip when fully extended
        if self.EXTEND_END - 3 <= f <= self.EXTEND_END + 2:
            tip_x = int(self.x + self.facing * self.LENGTH * progress)
            tip_y = int(self.y + math.sin(math.pi) * 40)
            pygame.draw.circle(surface, (255, 240, 180), (tip_x, tip_y), 6)
            pygame.draw.circle(surface, (255, 255, 255), (tip_x, tip_y), 3)


# ---------------------------------------------------------------------------
# Hot Potato  (easter egg)
# ---------------------------------------------------------------------------

class HotPotato:
    """
    Sits on the ground for FUSE frames, then explodes dealing EXPLODE_DMG
    to any fighter within EXPLODE_RADIUS.  Glows red and shakes in the
    last 60 frames to warn players.
    """
    FUSE          = 240   # 4 seconds at 60 fps
    EXPLODE_RADIUS = 110
    EXPLODE_DMG    = 50
    EXPLODE_DUR    = 30
    RADIUS         = 18

    def __init__(self):
        self.x             = float(random.randint(120, WIDTH - 120))
        self.y             = float(GROUND_Y - self.RADIUS)
        self.fuse          = self.FUSE
        self.exploding     = False
        self.explode_timer = 0
        self.damaged       = False
        self.alive         = True
        self._t            = 0

    def update(self):
        self._t += 1
        if not self.exploding:
            self.fuse -= 1
            if self.fuse <= 0:
                self.exploding     = True
                self.explode_timer = self.EXPLODE_DUR
        else:
            self.explode_timer -= 1
            if self.explode_timer <= 0:
                self.alive = False

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x,
                          self.y - (fighter.y - 60)) < self.EXPLODE_RADIUS

    def draw(self, surface):
        if not self.exploding:
            r    = self.RADIUS
            # Shake when fuse < 60
            ox = int(math.sin(self._t * 0.8) * min(4, (60 - self.fuse) * 0.08)) if self.fuse < 60 else 0
            cx, cy = int(self.x) + ox, int(self.y)

            # Flash red in last 60 frames
            blink = self.fuse < 60 and (self.fuse // 8) % 2 == 0
            body_col = (255, 80, 0) if blink else (180, 110, 40)

            # Potato body (slightly oval)
            pygame.draw.ellipse(surface, body_col,
                                (cx - r, cy - int(r * 0.85), r * 2, int(r * 1.7)))
            pygame.draw.ellipse(surface, (220, 150, 60),
                                (cx - r, cy - int(r * 0.85), r * 2, int(r * 1.7)), 2)

            # Eyes (menacing)
            for ex in [cx - r//3, cx + r//3]:
                pygame.draw.circle(surface, (20, 10, 0), (ex, cy - 3), 3)

            # Steam puffs above
            prog = 1.0 - self.fuse / self.FUSE
            for i in range(3):
                sx = cx + (i - 1) * 7
                sy = cy - r - int(8 + prog * 14) - i * 4
                alpha_r = max(3, int(6 * (1 - prog * 0.5)))
                pygame.draw.circle(surface, (200, 200, 200), (sx, sy), alpha_r)

            # Fuse timer text
            secs = max(0, self.fuse // 60) + 1
            font_s = pygame.font.SysFont(None, 22)
            lbl = font_s.render(str(secs), True, (255, 255, 0) if not blink else (255, 0, 0))
            surface.blit(lbl, (cx - lbl.get_width() // 2, cy - r - 26))
        else:
            prog = 1.0 - self.explode_timer / self.EXPLODE_DUR
            r_ex = int(self.EXPLODE_RADIUS * prog)
            w    = max(1, int(10 * (1 - prog)))
            cx, cy = int(self.x), int(self.y)
            pygame.draw.circle(surface, (255, 200, 0), (cx, cy), r_ex, w)
            if r_ex > 20:
                pygame.draw.circle(surface, (255, 80, 0),
                                   (cx, cy), max(1, r_ex - 20), max(1, w - 2))
            # Chunk bits
            for angle in range(0, 360, 40):
                a  = math.radians(angle)
                px = cx + int(math.cos(a) * r_ex * 0.6)
                py = cy + int(math.sin(a) * r_ex * 0.6)
                pygame.draw.circle(surface, (180, 110, 40), (px, py),
                                   max(2, int(6 * (1 - prog))))


# ---------------------------------------------------------------------------
# FallingPot  (imcooking easter egg)
# ---------------------------------------------------------------------------

class FallingPot:
    GRAVITY    = 0.55
    MAX_VY     = 15
    SQUISH_DUR = 28
    DAMAGE     = 25
    HIT_RANGE  = 65   # px horizontal distance to deal damage on landing

    def __init__(self):
        self.x          = float(random.randint(100, WIDTH - 100))
        self.y          = float(random.randint(-120, -30))
        self.vy         = 0.0
        self.alive      = True
        self.landed     = False
        self.squish_t   = 0
        self.just_landed = False

    def update(self):
        self.just_landed = False
        if not self.landed:
            self.vy = min(self.vy + self.GRAVITY, self.MAX_VY)
            self.y += self.vy
            if self.y >= GROUND_Y - 10:
                self.y = GROUND_Y - 10.0
                self.landed = True
                self.squish_t = self.SQUISH_DUR
                self.just_landed = True
        else:
            self.squish_t -= 1
            if self.squish_t <= 0:
                self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        if not self.landed:
            # Rim (top ellipse)
            pygame.draw.ellipse(surface, (190, 110, 40),
                                (cx - 22, cy - 32, 44, 14))
            # Body
            pygame.draw.rect(surface, (160, 80, 20),
                             (cx - 18, cy - 26, 36, 32))
            pygame.draw.ellipse(surface, (140, 65, 15),
                                (cx - 18, cy + 4, 36, 12))
            # Handle arc
            pygame.draw.arc(surface, (140, 65, 15),
                            (cx - 12, cy - 44, 24, 20),
                            0, math.pi, 3)
            # Steam lines (wobble as it falls)
            for si, sx in enumerate([cx - 8, cx, cx + 8]):
                swy = cy - 36 - si * 3
                pygame.draw.line(surface, (200, 200, 200),
                                 (sx, swy), (sx + 3, swy - 8), 2)
        else:
            # Squished flat on the ground
            prog = 1.0 - self.squish_t / self.SQUISH_DUR
            h = max(5, int(24 * (1 - prog * 0.75)))
            pygame.draw.ellipse(surface, (160, 80, 20),
                                (cx - 24, cy - h // 2, 48, h))
            pygame.draw.ellipse(surface, (190, 110, 40),
                                (cx - 24, cy - h // 2, 48, h), 2)


# ---------------------------------------------------------------------------
# RollingCoin  (imselling easter egg)
# ---------------------------------------------------------------------------

class RollingCoin:
    RADIUS   = 16
    SPEED    = 6
    DAMAGE   = 8
    HIT_CD   = 30    # frames between hits per fighter
    LIFETIME = 900   # 15 seconds

    def __init__(self):
        self.x      = float(random.randint(150, WIDTH - 150))
        self.y      = float(GROUND_Y - self.RADIUS)
        self.vx     = self.SPEED * random.choice([-1, 1])
        self.age    = 0
        self.alive  = True
        self._cds   = {}   # id(fighter) → cooldown frames remaining

    def update(self, *fighters):
        """Move, bounce walls, hit fighters. Returns list of (fighter, dmg) tuples."""
        self.age += 1
        self.x += self.vx
        if self.x < 50 + self.RADIUS:
            self.x = 50 + self.RADIUS
            self.vx = abs(self.vx)
        elif self.x > WIDTH - 50 - self.RADIUS:
            self.x = WIDTH - 50 - self.RADIUS
            self.vx = -abs(self.vx)

        for fid in list(self._cds):
            if self._cds[fid] > 0:
                self._cds[fid] -= 1

        hits = []
        for f in fighters:
            fid = id(f)
            if self._cds.get(fid, 0) == 0:
                if math.hypot(self.x - f.x, self.y - (f.y - 55)) < self.RADIUS + 28:
                    hits.append(f)
                    self._cds[fid] = self.HIT_CD

        if self.age >= self.LIFETIME:
            self.alive = False
        return hits

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        # Spinning coin (flatten width based on rotation)
        spin = math.cos(self.age * 0.18)
        draw_w = max(4, int(self.RADIUS * 2 * abs(spin)))
        # Gold coin
        coin_rect = (cx - draw_w // 2, cy - self.RADIUS, draw_w, self.RADIUS * 2)
        pygame.draw.ellipse(surface, (220, 185, 0),  coin_rect)
        pygame.draw.ellipse(surface, (255, 220, 40), coin_rect, 2)
        # Dollar sign (only when coin is face-on)
        if abs(spin) > 0.4:
            lbl = font_tiny.render("$", True, (120, 90, 0))
            surface.blit(lbl, (cx - lbl.get_width() // 2,
                               cy - lbl.get_height() // 2))


# ---------------------------------------------------------------------------
# FallingMerlin  (merlin easter egg)
# ---------------------------------------------------------------------------

class FallingMerlin:
    GRAVITY   = 0.45
    MAX_VY    = 12
    STAY_DUR  = 70   # frames before disappearing after landing

    def __init__(self):
        self.x        = float(random.randint(80, WIDTH - 80))
        self.y        = float(random.randint(-200, -40))
        self.vy       = 0.0
        self.alive    = True
        self.landed   = False
        self.stay_t   = 0
        self.angle    = 0.0   # slight wobble while falling

    def update(self):
        if not self.landed:
            self.vy = min(self.vy + self.GRAVITY, self.MAX_VY)
            self.y += self.vy
            self.angle = math.sin(self.y * 0.04) * 8
            if self.y >= GROUND_Y:
                self.y = float(GROUND_Y)
                self.landed = True
                self.stay_t = self.STAY_DUR
        else:
            self.stay_t -= 1
            if self.stay_t <= 0:
                self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        alpha = 255
        if self.landed:
            alpha = max(0, int(255 * self.stay_t / self.STAY_DUR))

        # tmp surface: 80 wide, 120 tall; feet at (tx, ty) = (40, 100)
        tmp = pygame.Surface((80, 120), pygame.SRCALPHA)
        tx, ty = 40, 100

        # Robe (blue triangle body)
        pygame.draw.polygon(tmp, (30, 80, 200, alpha),
                            [(tx, ty), (tx - 18, ty), (tx - 8, ty - 40),
                             (tx + 8, ty - 40), (tx + 18, ty)])
        # Arms
        pygame.draw.line(tmp, (30, 80, 200, alpha),
                         (tx - 8, ty - 32), (tx - 22, ty - 18), 4)
        pygame.draw.line(tmp, (30, 80, 200, alpha),
                         (tx + 8, ty - 32), (tx + 22, ty - 18), 4)
        # Head
        pygame.draw.circle(tmp, (255, 220, 180, alpha), (tx, ty - 50), 11)
        # White beard
        pygame.draw.polygon(tmp, (240, 240, 240, alpha),
                            [(tx - 7, ty - 42), (tx + 7, ty - 42),
                             (tx + 5, ty - 28), (tx, ty - 24), (tx - 5, ty - 28)])
        # Wizard hat (tall purple triangle)
        pygame.draw.polygon(tmp, (100, 0, 180, alpha),
                            [(tx, ty - 90), (tx - 14, ty - 58), (tx + 14, ty - 58)])
        # Hat brim
        pygame.draw.ellipse(tmp, (80, 0, 150, alpha),
                            (tx - 16, ty - 62, 32, 10))
        # Star on hat
        star_cx, star_cy = tx, ty - 80
        for si in range(5):
            a1 = math.radians(si * 72 - 90)
            a2 = math.radians(si * 72 - 90 + 36)
            p1x = star_cx + int(math.cos(a1) * 5)
            p1y = star_cy + int(math.sin(a1) * 5)
            p2x = star_cx + int(math.cos(a2) * 2)
            p2y = star_cy + int(math.sin(a2) * 2)
            pygame.draw.line(tmp, (255, 230, 0, alpha),
                             (star_cx, star_cy), (p1x, p1y), 1)
            pygame.draw.line(tmp, (255, 230, 0, alpha),
                             (star_cx, star_cy), (p2x, p2y), 1)

        surface.blit(tmp, (cx - tx, cy - ty))


# ---------------------------------------------------------------------------
# FlyingBaseball  (strike easter egg)
# ---------------------------------------------------------------------------

class FlyingBaseball:
    RADIUS   = 10
    DAMAGE   = 8
    HIT_CD   = 45
    LIFETIME = 840   # 14 seconds per ball

    def __init__(self):
        self.x    = float(random.randint(80, WIDTH - 80))
        self.y    = float(random.randint(40, 180))
        speed     = random.uniform(5, 9)
        self.vx   = speed * random.choice([-1, 1])
        self.vy   = random.uniform(-2, 3)
        self.spin = 0.0
        self.age  = 0
        self.alive = True
        self._cds  = {}

    def update(self, *fighters):
        self.age  += 1
        self.vy    = min(self.vy + 0.28, 13)
        self.x    += self.vx
        self.y    += self.vy
        self.spin += 0.14

        if self.x < self.RADIUS:
            self.x = float(self.RADIUS);      self.vx = abs(self.vx)
        elif self.x > WIDTH - self.RADIUS:
            self.x = float(WIDTH - self.RADIUS); self.vx = -abs(self.vx)

        if self.y > GROUND_Y - self.RADIUS:
            self.y  = float(GROUND_Y - self.RADIUS)
            self.vy = -abs(self.vy) * 0.70
            if abs(self.vy) < 1.5:
                self.vy = -random.uniform(3, 5)

        for fid in list(self._cds):
            if self._cds[fid] > 0:
                self._cds[fid] -= 1

        hits = []
        for f in fighters:
            fid = id(f)
            if self._cds.get(fid, 0) == 0:
                if math.hypot(self.x - f.x, self.y - (f.y - 60)) < self.RADIUS + 26:
                    hits.append(f)
                    self._cds[fid] = self.HIT_CD

        if self.age >= self.LIFETIME:
            self.alive = False
        return hits

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = self.RADIUS
        pygame.draw.circle(surface, (238, 238, 225), (cx, cy), r)
        pygame.draw.circle(surface, (180, 175, 160), (cx, cy), r, 1)
        # Red stitches — two rows of dots curved around the ball
        for side in (-1, 1):
            for i in range(5):
                t  = self.spin + i * 0.38
                sx = cx + int(side * (r - 2) * 0.55 * math.sin(t))
                sy = cy + int((r - 3) * math.cos(t) * 0.45)
                sx = max(0, min(WIDTH - 1, sx))
                sy = max(0, min(HEIGHT - 1, sy))
                pygame.draw.circle(surface, (200, 25, 25), (sx, sy), 1)


# ---------------------------------------------------------------------------
# FlyingBat  (strike easter egg)
# ---------------------------------------------------------------------------

class FlyingBat:
    DAMAGE = 18
    SPEED  = 9
    HIT_CD = 55

    def __init__(self):
        self._dir = random.choice([-1, 1])          # −1 = enters from right
        self.x    = float(-40 if self._dir == 1 else WIDTH + 40)
        self.y    = float(random.randint(GROUND_Y - 220, GROUND_Y - 70))
        self.vx   = self.SPEED * self._dir
        self.spin = 0.0
        self.alive = True
        self._cds  = {}

    def update(self, *fighters):
        self.x   += self.vx
        self.spin += 0.18

        if self.x < -60 or self.x > WIDTH + 60:
            self.alive = False
            return []

        for fid in list(self._cds):
            if self._cds[fid] > 0:
                self._cds[fid] -= 1

        hits = []
        for f in fighters:
            fid = id(f)
            if self._cds.get(fid, 0) == 0:
                if math.hypot(self.x - f.x, self.y - (f.y - 60)) < 38:
                    hits.append(f)
                    self._cds[fid] = self.HIT_CD
        return hits

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        cos_a  = math.cos(self.spin)
        sin_a  = math.sin(self.spin)
        # Bat = handle (thin) → barrel (thick), 52 px long
        dx = int(cos_a * 26); dy = int(sin_a * 26)
        handle = (cx - dx, cy - dy)
        barrel = (cx + dx, cy + dy)
        pygame.draw.line(surface, (150, 90, 40),  handle, barrel, 5)
        pygame.draw.line(surface, (100, 55, 15),  handle, barrel, 5)
        pygame.draw.circle(surface, (175, 110, 55), barrel, 9)
        pygame.draw.circle(surface, (120, 70, 25),  barrel, 9, 2)
        # Grip tape (dark lines near handle end)
        for t in (0.15, 0.28):
            gx = cx - dx + int(cos_a * 52 * t)
            gy = cy - dy + int(sin_a * 52 * t)
            pygame.draw.circle(surface, (40, 20, 10), (gx, gy), 3)


# ---------------------------------------------------------------------------
# KitsuneShot  (Kitsune 9-direction barrage)
# ---------------------------------------------------------------------------

class KitsuneShot:
    RADIUS = 9
    SPEED  = 9
    DMG    = 9
    LIFE   = 110   # ~1.8 seconds

    def __init__(self, x, y, angle_deg, owner):
        self.x        = float(x)
        self.y        = float(y)
        angle_rad     = math.radians(angle_deg)
        self.vx       = math.cos(angle_rad) * self.SPEED
        self.vy       = math.sin(angle_rad) * self.SPEED
        self.owner    = owner
        self.alive    = True
        self.life     = self.LIFE
        self._spin    = 0.0

    def update(self):
        self.x     += self.vx
        self.y     += self.vy
        self.life  -= 1
        self._spin += 0.2
        if (self.life <= 0 or self.x < -20 or self.x > WIDTH + 20
                or self.y < -20 or self.y > HEIGHT + 20):
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (180, 80, 0),   (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (255, 180, 0),  (cx, cy), self.RADIUS - 3)
        pygame.draw.circle(surface, (255, 240, 120),(cx, cy), self.RADIUS - 6)
        # Small directional flash
        fx = cx + int(math.cos(self._spin) * (self.RADIUS - 1))
        fy = cy + int(math.sin(self._spin) * (self.RADIUS - 1))
        pygame.draw.circle(surface, (255, 255, 200), (fx, fy), 2)

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 28


# ---------------------------------------------------------------------------
# WaterBall  (Riptide kick)
# ---------------------------------------------------------------------------

class WaterBall:
    RADIUS = 10
    SPEED  = 8
    DMG    = 12

    def __init__(self, x, y, facing, owner):
        self.x      = float(x)
        self.y      = float(y)
        self.vx     = self.SPEED * facing
        self.owner  = owner
        self.alive  = True
        self._t     = 0

    def update(self):
        self._t += 1
        self.x  += self.vx
        self.y  += math.sin(self._t * 0.14) * 1.8   # wavy arc
        if self.x < -20 or self.x > WIDTH + 20:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (0, 90, 180),   (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (0, 180, 255),  (cx, cy), self.RADIUS - 3)
        pygame.draw.circle(surface, (160, 235, 255),(cx, cy), self.RADIUS - 6)
        # Highlight droplet
        pygame.draw.circle(surface, (220, 250, 255), (cx - 2, cy - 3), 2)

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 28


# ---------------------------------------------------------------------------
# SnipeShot  (Shifter cycle_attack mode 2 — fast long-range bolt)
# ---------------------------------------------------------------------------

class SnipeShot:
    SPEED  = 22
    DMG    = 22
    RADIUS = 5

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
        x1 = int(self.x)
        x2 = int(self.x - self.vx * 4)   # elongated trail
        y  = int(self.y)
        pygame.draw.line(surface, (80, 160, 255),  (x2, y), (x1, y), 4)
        pygame.draw.line(surface, (200, 230, 255), (x2, y), (x1, y), 1)
        pygame.draw.circle(surface, (255, 255, 255), (x1, y), self.RADIUS - 1)

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 28


# ---------------------------------------------------------------------------
# FireBall  (Pyro auto-fire — applies fire on hit)
# ---------------------------------------------------------------------------

class FireBall:
    RADIUS = 10
    SPEED  = 7
    DMG    = 8

    def __init__(self, x, y, facing, owner):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = self.SPEED * facing
        self.owner = owner
        self.alive = True
        self._t    = 0

    def update(self):
        self._t += 1
        self.x += self.vx
        if self.x < 0 or self.x > WIDTH:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pulse = (self._t // 4) % 2 == 0
        pygame.draw.circle(surface, (255, 60, 0) if pulse else (220, 100, 20), (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (255, 200, 0), (cx, cy), self.RADIUS - 4)
        pygame.draw.circle(surface, (255, 255, 180), (cx, cy), self.RADIUS - 7)

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 28


# ---------------------------------------------------------------------------
# ThunderBolt  (Thunder God punch — falls from above onto opponent)
# ---------------------------------------------------------------------------

class ThunderBolt:
    GRAVITY = 1.4
    DMG     = 20

    def __init__(self, target_x, owner):
        self.x     = float(target_x)
        self.y     = 0.0
        self.vy    = 5.0
        self.owner = owner
        self.alive = True
        self.hit   = False
        self._t    = 0

    def update(self):
        self._t += 1
        self.vy = min(self.vy + self.GRAVITY, 30)
        self.y  += self.vy
        if self.y >= GROUND_Y:
            self.alive = False

    def draw(self, surface):
        cx, bot = int(self.x), int(self.y)
        segs = 6
        pts  = []
        for i in range(segs + 1):
            t  = i / segs
            sy = int(t * bot)
            sx = cx + int(math.sin(t * math.pi * 3 + self._t * 0.4) * 10)
            pts.append((sx, sy))
        if len(pts) >= 2:
            pygame.draw.lines(surface, (180, 180, 255), False, pts, 3)
            pygame.draw.lines(surface, (255, 255, 255), False, pts, 1)
        pygame.draw.circle(surface, (255, 255, 100), (cx, bot), 7)

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 40)) < 40


# ---------------------------------------------------------------------------
# Scroll (Scrollmaster kick) — bounces around, grows every second
# ---------------------------------------------------------------------------

class Scroll:
    BASE_HALF  = 8      # starting half-width (pixels)
    SPEED      = 8
    GROW_EVERY = 60     # frames between size increases
    GROW_BY    = 5      # pixels added each growth tick
    MAX_HALF   = 60
    DMG        = 10
    HIT_CD     = 35     # frames between hits on same target
    LIFETIME   = 1200   # 20 seconds

    def __init__(self, x, y, facing, owner):
        self.x        = float(x)
        self.y        = float(y)
        self.vx       = self.SPEED * facing
        self.vy       = -5.0
        self.owner    = owner
        self.half     = float(self.BASE_HALF)
        self.alive    = True
        self.frames   = 0
        self.grow_t   = self.GROW_EVERY
        self.hit_cd   = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3   # gravity

        # Bounce off walls
        if self.x - self.half < 0:
            self.x  = self.half
            self.vx = abs(self.vx)
        elif self.x + self.half > WIDTH:
            self.x  = float(WIDTH) - self.half
            self.vx = -abs(self.vx)

        # Bounce off ground
        if self.y + self.half >= GROUND_Y:
            self.y  = float(GROUND_Y) - self.half
            self.vy = -abs(self.vy) * 0.80

        # Bounce off ceiling
        if self.y - self.half < 20:
            self.y  = 20.0 + self.half
            self.vy = abs(self.vy)

        # Grow every second
        self.grow_t -= 1
        if self.grow_t <= 0:
            self.grow_t = self.GROW_EVERY
            self.half   = min(self.MAX_HALF, self.half + self.GROW_BY)

        if self.hit_cd > 0:
            self.hit_cd -= 1

        self.frames += 1
        if self.frames >= self.LIFETIME:
            self.alive = False

    def collides(self, fighter):
        h = self.half
        return (abs(self.x - fighter.x) < h + 28 and
                abs(self.y - (fighter.y - 60)) < h + 38)

    def draw(self, surface):
        h  = int(self.half)
        h2 = max(4, h // 2)
        cx = int(self.x)
        cy = int(self.y)
        # Parchment body
        pygame.draw.rect(surface, (220, 200, 130),
                         (cx - h, cy - h2, h * 2, h2 * 2))
        # Rolled left cap
        pygame.draw.ellipse(surface, (190, 165, 95),
                            (cx - h - 5, cy - h2 - 2, 11, h2 * 2 + 4))
        # Rolled right cap
        pygame.draw.ellipse(surface, (190, 165, 95),
                            (cx + h - 5, cy - h2 - 2, 11, h2 * 2 + 4))
        # Text lines on scroll
        line_count = max(1, h2 // 5)
        for i in range(1, line_count + 1):
            ly = cy - h2 + i * (h2 * 2 // (line_count + 1))
            pygame.draw.line(surface, (150, 120, 70),
                             (cx - h + 6, ly), (cx + h - 6, ly), 1)
        # Outline
        pygame.draw.rect(surface, (160, 128, 65),
                         (cx - h, cy - h2, h * 2, h2 * 2), 2)


class TotemPole:
    """Falling totem pole projectile (Great Totem Spirit's kick)."""
    HALF_W  = 10    # half-width
    HEIGHT  = 72    # visual + hitbox height
    SPEED   = 10    # pixels per frame downward
    DMG     = 18
    HIT_CD  = 20

    def __init__(self, x):
        self.x      = float(max(self.HALF_W + 5, min(WIDTH - self.HALF_W - 5, x)))
        self.y      = float(-self.HEIGHT)   # start above screen
        self.alive  = True
        self.hit_cd = 0

    def update(self):
        self.y += self.SPEED
        if self.hit_cd > 0:
            self.hit_cd -= 1
        if self.y > GROUND_Y + 30:
            self.alive = False

    def collides(self, fighter):
        return (abs(self.x - fighter.x) < self.HALF_W + 26 and
                abs((self.y + self.HEIGHT // 2) - (fighter.y - 60)) < self.HEIGHT // 2 + 38)

    def draw(self, surface):
        cx = int(self.x)
        ty = int(self.y)
        w  = self.HALF_W * 2
        h  = self.HEIGHT
        # Pole shaft
        pygame.draw.rect(surface, (100, 62, 20), (cx - self.HALF_W, ty, w, h))
        pygame.draw.rect(surface, (70,  44, 12), (cx - self.HALF_W, ty, w, h), 2)
        # Two carved faces stacked
        face_data = [(ty + 2,   (190, 70,  30)),
                     (ty + h//2, (55,  140, 55))]
        fh = h // 2 - 6
        for fy, fc in face_data:
            pygame.draw.rect(surface, fc, (cx - self.HALF_W + 1, fy, w - 2, fh), border_radius=2)
            # eyes
            pygame.draw.rect(surface, (255, 255, 200), (cx - 7, fy + 4,  5, 4))
            pygame.draw.rect(surface, (255, 255, 200), (cx + 3, fy + 4,  5, 4))
            pygame.draw.rect(surface, (0,   0,   0),   (cx - 6, fy + 5,  3, 2))
            pygame.draw.rect(surface, (0,   0,   0),   (cx + 4, fy + 5,  3, 2))
            # mouth
            pygame.draw.rect(surface, (0, 0, 0), (cx - 5, fy + fh - 8, 10, 5), border_radius=1)
            for tx in (cx - 4, cx - 1, cx + 2):
                pygame.draw.rect(surface, (255, 255, 200), (tx, fy + fh - 7, 2, 4))
        # Pointed top cap
        pygame.draw.polygon(surface, (100, 62, 20),
                            [(cx, ty - 10), (cx - self.HALF_W, ty), (cx + self.HALF_W, ty)])


class RemoteController:
    """Explosive remote controller (Rage Quitter's kick)."""
    SPEED  = 11
    DMG    = 100
    RADIUS = 70   # explosion radius

    def __init__(self, x, y, facing):
        self.x      = float(x)
        self.y      = float(y)
        self.vx     = self.SPEED * facing
        self.facing = facing
        self.alive  = True
        self.hit    = False

    def update(self):
        self.x += self.vx
        if self.x < 0 or self.x > WIDTH:
            self.alive = False

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        # Body
        pygame.draw.rect(surface, (40, 40, 40),   (cx - 14, cy - 8,  28, 16), border_radius=3)
        pygame.draw.rect(surface, (220, 40, 0),   (cx - 14, cy - 8,  28, 16), 2, border_radius=3)
        # Buttons
        for bx in (cx - 7, cx, cx + 7):
            pygame.draw.circle(surface, (220, 40, 0),  (bx, cy - 1), 3)
        # Antenna
        pygame.draw.line(surface, (180, 180, 180), (cx + 10, cy - 8), (cx + 16, cy - 20), 2)
        pygame.draw.circle(surface, (255, 80, 0),  (cx + 16, cy - 21), 3)


class Apple:
    """Falling apple (Gravity's kick — 20 drop down from above)."""
    DMG    = 8
    SPEED  = 9
    HIT_CD = 10

    def __init__(self, x):
        self.x      = float(max(20, min(WIDTH - 20, x)))
        self.y      = float(-random.randint(0, 80))   # staggered starts
        self.alive  = True
        self.hit_cd = 0

    def update(self):
        self.y += self.SPEED
        if self.hit_cd > 0:
            self.hit_cd -= 1
        if self.y > GROUND_Y + 20:
            self.alive = False

    def collides(self, fighter):
        return (abs(self.x - fighter.x) < 22 and
                abs(self.y - (fighter.y - 60)) < 40)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (210, 40, 20),  (cx, cy), 9)
        pygame.draw.circle(surface, (230, 80, 60),  (cx - 3, cy - 3), 4)
        pygame.draw.line(surface,   (80, 50, 10),   (cx, cy - 9), (cx + 3, cy - 16), 2)
        pygame.draw.ellipse(surface, (40, 140, 40), (cx + 2, cy - 18, 10, 7))


class VenomBean:
    """Horizontal venom projectile (Spitting Cobra's kick). Poisons on hit."""
    SPEED  = 10
    DMG    = 8
    RADIUS = 12

    def __init__(self, x, y, facing):
        self.x      = float(x)
        self.y      = float(y)
        self.facing = facing
        self.alive  = True
        self.hit    = False

    def update(self):
        self.x += self.SPEED * self.facing
        if self.x < -20 or self.x > WIDTH + 20:
            self.alive = False

    def collides(self, fighter):
        return (abs(self.x - fighter.x) < self.RADIUS + 20 and
                abs(self.y - (fighter.y - 60)) < self.RADIUS + 28)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        # Oval green bean body
        pygame.draw.ellipse(surface, (60, 180, 40),  (cx - 10, cy - 6, 20, 12))
        pygame.draw.ellipse(surface, (100, 220, 60), (cx - 10, cy - 6, 20, 12), 2)
        # Poison drip
        pygame.draw.circle(surface, (180, 255, 80), (cx + self.facing * 10, cy), 4)
        pygame.draw.circle(surface, (220, 255, 120), (cx + self.facing * 10, cy), 2)


class PlantSpike:
    """Rising plant spike that sprouts from the ground at the opponent (Druid kick)."""
    DMG    = 18
    SPEED  = 9
    RADIUS = 12

    def __init__(self, x, owner):
        self.x     = float(x)
        self.y     = float(GROUND_Y)
        self.vy    = -self.SPEED
        self.owner = owner
        self.alive = True

    def update(self):
        self.y += self.vy
        if self.y < GROUND_Y - 240:
            self.alive = False

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < self.RADIUS + 28

    def draw(self, surface):
        tip_x  = int(self.x)
        tip_y  = int(self.y)
        base_y = min(GROUND_Y, tip_y + 55)
        # Stem
        pygame.draw.line(surface, (30, 140, 40), (tip_x, base_y), (tip_x, tip_y), 5)
        # Spike tip
        pygame.draw.polygon(surface, (50, 220, 60), [
            (tip_x - 10, tip_y + 22),
            (tip_x + 10, tip_y + 22),
            (tip_x, tip_y - 2),
        ])
        # Side leaf
        pygame.draw.ellipse(surface, (40, 180, 50), (tip_x + 4, tip_y + 10, 18, 9))

