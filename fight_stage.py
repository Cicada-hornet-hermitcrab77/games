import pygame
import math
import random
import constants
from constants import *
from fight_data import POWERUPS

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

        if self.name == "Everything":
            # Rainbow: cycle the whole circle through hue over time
            t = self.age * 0.06
            col = (
                int(127 + 127 * math.sin(t)),
                int(127 + 127 * math.sin(t + 2.094)),
                int(127 + 127 * math.sin(t + 4.189)),
            )
            glow = (min(255, col[0] + 60), min(255, col[1] + 60), min(255, col[2] + 60))
            glow_r = PICKUP_RADIUS + 4 + int(math.sin(self.age * 0.12) * 3)
            pygame.draw.circle(surface, glow, (cx, cy), glow_r, 3)
            # Draw striped rainbow ring
            for i in range(6):
                a  = i * math.pi / 3 + t
                rc = (
                    int(127 + 127 * math.sin(a)),
                    int(127 + 127 * math.sin(a + 2.094)),
                    int(127 + 127 * math.sin(a + 4.189)),
                )
                pygame.draw.arc(surface, rc,
                                (cx - PICKUP_RADIUS, cy - PICKUP_RADIUS,
                                 PICKUP_RADIUS * 2, PICKUP_RADIUS * 2),
                                a, a + math.pi / 3 + 0.1, PICKUP_RADIUS)
            pygame.draw.circle(surface, WHITE, (cx, cy), PICKUP_RADIUS, 2)
        else:
            # Standard powerup draw
            glow_r   = PICKUP_RADIUS + 4 + int(math.sin(self.age * 0.12) * 3)
            glow_col = tuple(min(255, c + 60) for c in self.color)
            pygame.draw.circle(surface, glow_col, (cx, cy), glow_r, 3)
            pygame.draw.circle(surface, self.color, (cx, cy), PICKUP_RADIUS)
            pygame.draw.circle(surface, WHITE,      (cx, cy), PICKUP_RADIUS, 2)

        # Label
        lbl = font_tiny.render(self.name[0], True, WHITE)   # first letter
        surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    def collides(self, fighter):
        return math.hypot(self.x - fighter.x, self.y - (fighter.y - 60)) < PICKUP_RADIUS + 22


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


class StagePencil:
    """Computer-map object: drifts around and periodically draws platforms."""
    SPEED         = 1.1
    DRAW_INTERVAL = FPS * 4   # new platform every 4 s
    MAX_PLATS     = 6

    def __init__(self):
        self.x            = float(random.randint(120, WIDTH - 120))
        self.y            = float(random.randint(60, GROUND_Y - 80))
        angle             = random.uniform(0, 2 * math.pi)
        self.vx           = math.cos(angle) * self.SPEED
        self.vy           = math.sin(angle) * self.SPEED
        self.dir_timer    = random.randint(90, 200)
        self.draw_timer   = self.DRAW_INTERVAL
        self.pending_plat = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Bounce off edges
        if self.x > WIDTH - 80:
            self.x = WIDTH - 80; self.vx = -abs(self.vx)
        elif self.x < 80:
            self.x = 80; self.vx = abs(self.vx)
        if self.y > GROUND_Y - 50:
            self.y = GROUND_Y - 50; self.vy = -abs(self.vy)
        elif self.y < 40:
            self.y = 40; self.vy = abs(self.vy)
        # Randomly change direction every so often
        self.dir_timer -= 1
        if self.dir_timer <= 0:
            angle          = random.uniform(0, 2 * math.pi)
            self.vx        = math.cos(angle) * self.SPEED
            self.vy        = math.sin(angle) * self.SPEED
            self.dir_timer = random.randint(90, 200)
        self.draw_timer -= 1
        if self.draw_timer <= 0:
            self.pending_plat = True
            self.draw_timer   = self.DRAW_INTERVAL

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        # Pencil drawn at ~45-degree angle (tip pointing down-right)
        import math as _m
        angle = _m.radians(-40)
        dx = int(_m.cos(angle) * 30); dy = int(_m.sin(angle) * 30)
        # Body
        pygame.draw.line(surface, (245, 220, 50), (px, py), (px + dx*2, py + dy*2), 8)
        # Pink eraser end
        pygame.draw.line(surface, (240, 130, 130), (px - dx//2, py - dy//2), (px, py), 8)
        # Ferrule
        pygame.draw.line(surface, (180, 180, 180), (px, py), (px + dx//3, py + dy//3), 8)
        # Wood cone tip
        tip_x = px + dx*2; tip_y = py + dy*2
        pygame.draw.line(surface, (210, 170, 100), (px + dx + dx//2, py + dy + dy//2), (tip_x, tip_y), 6)
        # Graphite point
        pygame.draw.circle(surface, (40, 40, 40), (tip_x, tip_y), 3)
        # Outline
        pygame.draw.line(surface, (160, 130, 10), (px - dx//2, py - dy//2), (tip_x, tip_y), 2)


class StageEraser:
    """Computer-map object: moves along and wipes out drawn platforms."""
    SPEED = 1.8

    def __init__(self):
        self.x         = float(WIDTH - 150)
        self.y         = float(random.randint(60, GROUND_Y - 30))
        angle          = random.uniform(0, 2 * math.pi)
        self.vx        = math.cos(angle) * self.SPEED
        self.vy        = math.sin(angle) * self.SPEED
        self.dir_timer = random.randint(70, 160)

    def update(self, platforms):
        self.x += self.vx
        self.y += self.vy
        if self.x > WIDTH - 60:
            self.x = WIDTH - 60; self.vx = -abs(self.vx)
        elif self.x < 60:
            self.x = 60; self.vx = abs(self.vx)
        if self.y > GROUND_Y - 20:
            self.y = GROUND_Y - 20; self.vy = -abs(self.vy)
        elif self.y < 40:
            self.y = 40; self.vy = abs(self.vy)
        self.dir_timer -= 1
        if self.dir_timer <= 0:
            angle          = random.uniform(0, 2 * math.pi)
            self.vx        = math.cos(angle) * self.SPEED
            self.vy        = math.sin(angle) * self.SPEED
            self.dir_timer = random.randint(70, 160)
        # Erase any DrawnPlatform whose centre is within 80 px
        return [p for p in platforms
                if not (isinstance(p, DrawnPlatform)
                        and abs((p.x + p.w / 2) - self.x) < 80)]

    def draw(self, surface):
        ex, ey = int(self.x), int(self.y)
        ew, eh = 60, 22
        # Eraser body
        pygame.draw.rect(surface, (240, 160, 150), (ex - ew//2, ey - eh, ew, eh), border_radius=3)
        pygame.draw.rect(surface, (180, 80, 80),   (ex - ew//2, ey - eh, ew, eh), 2, border_radius=3)
        # Blue label stripe
        pygame.draw.rect(surface, (80, 120, 220), (ex - ew//2, ey - eh//2 - 3, ew, 7))
        # Eraser dust trail (particles behind movement)
        trail_dir = 1 if self.vx > 0 else -1
        for i in range(1, 5):
            dx = trail_dir * i * 14
            alpha = 180 - i * 40
            r = max(2, 6 - i)
            c = (min(255, 240 - i*20), min(255, 160 - i*15), min(255, 150 - i*15))
            pygame.draw.circle(surface, c, (ex - dx, ey - 6 + (i % 2)*4), r)


class DrawnPlatform:
    """Temporary platform drawn by the Pencil character."""
    H = 14

    def __init__(self, x, y, w=120):
        self.x     = float(x)
        self.y     = float(y)
        self.w     = w
        self.vx    = 0.0
        self.alive = True

    def update(self):
        pass  # platforms are permanent

    def draw(self, surface, _stage_idx=0):
        rx, ry = int(self.x), int(self.y)
        col = (60, 50, 10)
        import random as _r; _seed = int(self.x + self.y)
        for off in range(3):
            wobble = _r.Random(_seed + off).randint(-2, 2)
            pygame.draw.line(surface, col,
                             (rx + off,          ry + off * 3 + wobble),
                             (rx + self.w - off, ry + off * 3),
                             max(1, 3 - off))
        pygame.draw.line(surface, (200, 180, 20), (rx, ry), (rx + self.w, ry), 2)


class Portal:
    RADIUS = 26

    def __init__(self, x, y, col):
        self.x       = float(x)
        self.y       = float(y)
        self.col     = col
        self.partner = None   # set after both portals are created
        self.anim    = random.randint(0, 59)

    def update(self):
        self.anim = (self.anim + 1) % 60

    def near(self, fighter):
        return (abs(fighter.x - self.x) < self.RADIUS + 10
                and abs(fighter.y - self.y) < self.RADIUS + 20)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = self.RADIUS
        # Outer glow rings
        for i in range(4, 0, -1):
            glow = tuple(min(255, c + i * 14) for c in self.col)
            pygame.draw.circle(surface, glow, (cx, cy), r + i * 5, 2)
        # Main ring
        pygame.draw.circle(surface, self.col, (cx, cy), r, 5)
        # Swirling inner dots
        for i in range(8):
            angle = math.radians(self.anim * 6 + i * 45)
            dx = int(math.cos(angle) * r * 0.55)
            dy = int(math.sin(angle) * r * 0.55)
            pygame.draw.circle(surface, self.col, (cx + dx, cy + dy), 4)
        # Dark centre fill
        dark = tuple(c // 4 for c in self.col)
        pygame.draw.circle(surface, dark, (cx, cy), r - 7)


class ConveyorBelt:
    H = 16

    def __init__(self, x, y, w, speed):
        self.x     = float(x)
        self.y     = float(y)
        self.w     = w
        self.vx    = 0.0          # belt itself doesn't move
        self.speed = speed        # push speed applied to players
        self.anim  = 0

    def update(self):
        self.anim = (self.anim + 1) % 30

    def draw(self, surface, stage_idx=0):
        rx, ry = int(self.x), int(self.y)
        # Dark body
        pygame.draw.rect(surface, (40, 40, 40), (rx, ry, self.w, self.H), border_radius=3)
        # Yellow-black hazard stripes underneath
        stripe_w = 14
        for sx in range(0, self.w, stripe_w * 2):
            pygame.draw.rect(surface, (220, 180, 0),
                             (rx + sx, ry + self.H - 5, stripe_w, 5))
        # Scrolling arrows on top indicating direction
        arrow_char = ">" if self.speed > 0 else "<"
        spacing = 22
        offset  = int(self.anim / 30 * spacing * (1 if self.speed > 0 else -1)) % spacing
        for ax in range(-spacing, self.w + spacing, spacing):
            draw_x = rx + ax + offset
            if rx - 4 <= draw_x <= rx + self.w - 4:
                col = (255, 220, 0) if abs(self.speed) > 2 else (200, 200, 60)
                a = font_tiny.render(arrow_char, True, col)
                surface.blit(a, (draw_x, ry + 1))
        # Border
        pygame.draw.rect(surface, (180, 140, 0), (rx, ry, self.w, self.H), 2, border_radius=3)


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
        self.possessed = False   # Poltergeist: next trigger launches 3x

    def update(self):
        if self.anim     > 0: self.anim     -= 1
        if self.cooldown > 0: self.cooldown -= 1

    def trigger(self, fighter):
        if self.cooldown > 0:
            return
        if fighter.on_ground and fighter.y >= GROUND_Y - 2 and abs(fighter.x - self.x) < self.W:
            bvy = self.bounce_vy * (3.0 if self.possessed else 1.0)
            fighter.vy        = bvy
            fighter.on_ground = False
            fighter.jumps_left = 2 if fighter.char["double_jump"] else 1
            fighter.action    = 'jump'
            fighter.attacking = False
            self.anim     = 25
            self.cooldown = self.COOLDOWN
            self.possessed = False

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
# Jungle snake NPC
# ---------------------------------------------------------------------------

class JungleSnake:
    SPEED        = 2.5
    MAX_HP       = 20
    BITE_DMG     = 3
    BITE_COOLDOWN = 120   # 2 seconds at 60 fps
    BITE_RANGE   = 45

    def __init__(self):
        self.x                = float(random.choice([80, WIDTH - 80]))
        self.y                = float(GROUND_Y)
        self.facing           = 1
        self.bite_cd          = 0
        self.hp               = self.MAX_HP
        self.alive            = True
        self.t                = 0
        self.possessed_timer  = 0
        self.possessed_target = None

    def update(self, p1, p2):
        if not self.alive:
            return
        self.t += 1
        if self.bite_cd > 0:
            self.bite_cd -= 1
        if self.possessed_timer > 0:
            self.possessed_timer -= 1

        # Possessed: always chase the possessed target; normal: chase closest
        if self.possessed_timer > 0 and self.possessed_target is not None:
            target = self.possessed_target
        else:
            d1 = abs(self.x - p1.x) if p1.hp > 0 else 99999
            d2 = abs(self.x - p2.x) if p2.hp > 0 else 99999
            target = p1 if d1 <= d2 else p2

        dx = target.x - self.x
        self.facing = 1 if dx > 0 else -1
        spd = self.SPEED * (2.0 if self.possessed_timer > 0 else 1.0)
        if abs(dx) > self.BITE_RANGE - 5:
            self.x += self.facing * spd
        self.x = max(30.0, min(float(WIDTH - 30), self.x))

        # Bite when in range
        if (abs(self.x - target.x) < self.BITE_RANGE and
                abs(self.y - target.y) < 70 and self.bite_cd == 0):
            dmg = self.BITE_DMG * (3 if self.possessed_timer > 0 else 1)
            target.hp = max(0, target.hp - dmg)
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
# Computer bug NPC
# ---------------------------------------------------------------------------

class ComputerBug:
    SPEED        = 3.8
    MAX_HP       = 15
    BITE_DMG     = 4
    BITE_COOLDOWN = 90   # 1.5 s
    BITE_RANGE   = 42

    def __init__(self):
        self.x                = float(random.choice([80, WIDTH - 80]))
        self.y                = float(GROUND_Y)
        self.vx               = random.choice([-1, 1]) * self.SPEED
        self.hp               = self.MAX_HP
        self.bite_timer       = 0
        self.leg_t            = 0.0
        self.alive            = True
        self.possessed_timer  = 0
        self.possessed_target = None

    def update(self, target):
        if not self.alive:
            return
        self.leg_t += 0.2
        if self.possessed_timer > 0:
            self.possessed_timer -= 1
        actual_target = self.possessed_target if self.possessed_timer > 0 and self.possessed_target else target
        spd = self.SPEED * (2.0 if self.possessed_timer > 0 else 1.0)
        if actual_target:
            self.vx = spd if actual_target.x > self.x else -spd
        self.x += self.vx
        if self.x < 30:          self.x = 30;          self.vx =  abs(self.vx)
        if self.x > WIDTH - 30:  self.x = WIDTH - 30;  self.vx = -abs(self.vx)
        if self.bite_timer > 0:
            self.bite_timer -= 1
        if (actual_target and self.bite_timer == 0
                and abs(actual_target.x - self.x) < self.BITE_RANGE
                and abs(actual_target.y - self.y) < 60):
            dmg = self.BITE_DMG * (3 if self.possessed_timer > 0 else 1)
            actual_target.hp = max(0, actual_target.hp - dmg)
            actual_target.flash_timer = 8
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
        self.x         = float(x)
        self.y         = float(y)
        self.w         = self.W
        angle          = random.uniform(0, 2 * math.pi)
        self.vx        = math.cos(angle) * self.SPEED
        self.vy        = math.sin(angle) * self.SPEED
        self.dir_timer = random.randint(80, 180)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x > WIDTH - self.W - 20:
            self.x = WIDTH - self.W - 20; self.vx = -abs(self.vx)
        elif self.x < 20:
            self.x = 20; self.vx = abs(self.vx)
        if self.y > GROUND_Y - 30:
            self.y = GROUND_Y - 30; self.vy = -abs(self.vy)
        elif self.y < 40:
            self.y = 40; self.vy = abs(self.vy)
        self.dir_timer -= 1
        if self.dir_timer <= 0:
            angle          = random.uniform(0, 2 * math.pi)
            self.vx        = math.cos(angle) * self.SPEED
            self.vy        = math.sin(angle) * self.SPEED
            self.dir_timer = random.randint(80, 180)

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
# TimedPlatform  (The Creator kick)
# ---------------------------------------------------------------------------

class TimedPlatform(DrawnPlatform):
    """Temporary platform created by The Creator's kick — expires after a set time."""

    def __init__(self, x, y, w=120, lifetime=300):
        super().__init__(x, y, w)
        self._lifetime     = lifetime
        self._max_lifetime = lifetime

    def update(self):
        self._lifetime -= 1
        if self._lifetime <= 0:
            self.alive = False

    def draw(self, surface, _stage_idx=0):
        if not self.alive:
            return
        frac = self._lifetime / max(1, self._max_lifetime)
        # Fades yellow → orange → red as it expires
        r = min(255, int(200 + 55 * (1 - frac)))
        g = max(0,   int(200 * frac))
        col = (r, g, 30)
        rx, ry = int(self.x), int(self.y)
        pygame.draw.rect(surface, col, (rx, ry, self.w, self.H), border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), (rx, ry, self.w, self.H), 1, border_radius=4)
        # Countdown bar beneath
        bar_w = int(self.w * frac)
        pygame.draw.rect(surface, (255, 255, 100), (rx, ry + self.H, bar_w, 3))


# ---------------------------------------------------------------------------
# HazardZone  (ground hazard — damages players standing on it)
# ---------------------------------------------------------------------------

class HazardZone:
    """Spike, lava, electric, or ice zone on the ground. Damages on contact."""
    TICK = 30   # damage every 30 frames

    _STYLES = {
        "spike":    ((140, 30, 30),  (220, 60,  60)),
        "lava":     ((180, 60,  0),  (255, 140, 20)),
        "electric": (( 30, 30, 80),  (200, 200, 60)),
        "ice":      (( 60,140,200),  (180, 230,255)),
    }

    def __init__(self, x, w, htype="spike"):
        self.x      = float(x)
        self.w      = w
        self.htype  = htype
        self._t     = 0
        self.p1_cd  = 0
        self.p2_cd  = 0

    def update(self):
        self._t = (self._t + 1) % 60
        if self.p1_cd > 0: self.p1_cd -= 1
        if self.p2_cd > 0: self.p2_cd -= 1

    def contains(self, fighter):
        return (fighter.on_ground and
                self.x <= fighter.x <= self.x + self.w)

    def draw(self, surface):
        col1, col2 = self._STYLES.get(self.htype, self._STYLES["spike"])
        y = GROUND_Y - 12
        pygame.draw.rect(surface, col1, (int(self.x), y, self.w, 12))
        if self.htype == "spike":
            n = self.w // 10
            for i in range(n):
                sx = int(self.x) + i * 10 + 5
                pygame.draw.polygon(surface, col2,
                    [(sx-4, y+12), (sx+4, y+12), (sx, y-4)])
        elif self.htype == "lava":
            t = self._t * 0.2
            for i in range(0, self.w, 9):
                fh = int(5 + 3 * math.sin(t + i * 0.35))
                pygame.draw.ellipse(surface, col2,
                    (int(self.x)+i, y - fh, 8, fh+4))
        elif self.htype == "electric":
            for i in range(0, self.w, 10):
                if (self._t + i // 10) % 4 < 2:
                    pygame.draw.line(surface, col2,
                        (int(self.x)+i+4, y), (int(self.x)+i+1, y-8), 2)
        elif self.htype == "ice":
            pygame.draw.rect(surface, col2, (int(self.x), y, self.w, 4))
