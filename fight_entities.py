import pygame
import sys
import math
import random
import constants
from constants import *
from fight_data import CHARACTERS, POWERUPS, STAGES, STAGE_MATCHUPS
from fight_drawing import draw_stickman

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
        self.shield         = False
        self.leech          = bool(char_data.get("vampire"))
        self.bubble_shield  = False
        self.portal_cooldown = 0
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
        self.squish_frames           = 0      # frames of squish remaining (Hammerhead punch)
        self.confuse_frames          = 0      # frames of reversed controls (Clown kick)
        self._berserker_active       = False  # Viking: berserk when hp <= 50%
        self.trail                   = []     # Speedster: afterimage positions
        self.stealth_frames          = 0      # frames of stealth invisibility (Mime punch)
        self.dash_tap_left      = 0     # frames remaining in double-tap window (left)
        self.dash_tap_right     = 0     # frames remaining in double-tap window (right)
        self.dash_cd            = 0     # cooldown between dashes
        self.dash_frames        = 0     # frames of active dash remaining
        self.dash_dir           = 0     # direction of current dash
        self._prev_left         = False # was left key held last frame
        self._prev_right        = False # was right key held last frame
        self.laser_fire_cd      = FPS * 10  # frames until next laser shot
        self.laser_active       = 0         # frames remaining in current laser burst
        self.laser_hit_cd       = 0         # cooldown between laser damage ticks
        self.pending_whip       = False     # Whipper: spawn a whip this frame
        self.whip_cooldown      = 0         # cooldown between whip attacks
        self.poop_timer         = 0         # Everything: frames of poop powerup remaining
        self.poop_cd            = 0         # cooldown between poop drops

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
        elif t == 'bubble_shield':
            self.bubble_shield = True
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
        elif t == 'poop':
            self.poop_timer = spec['duration']
            self.active_powerups[name] = spec['duration']

    def tick_powerups(self):
        done = [n for n, t in self.active_powerups.items() if t <= 1]
        for name in done:
            spec = next((p for p in POWERUPS if p['name'] == name), None)
            if spec:
                t = spec['type']
                if t == 'speed':     self.speed_boost  = 1.0
                elif t == 'punch_dmg': self.punch_boost = max(0, self.punch_boost - spec['amount'])
                elif t == 'kick_dmg':  self.kick_boost  = max(0, self.kick_boost  - spec['amount'])
                elif t == 'shield':         self.shield        = False
                elif t == 'leech':          self.leech         = False
                elif t == 'bubble_shield':  self.bubble_shield = False
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
        if self.contact_cooldown > 0: self.contact_cooldown  -= 1
        if self.punch_cooldown   > 0: self.punch_cooldown    -= 1
        if self.portal_cooldown  > 0: self.portal_cooldown   -= 1
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
        if self.whip_cooldown > 0:
            self.whip_cooldown -= 1
        if self.poop_timer > 0:
            self.poop_timer -= 1
        if self.poop_cd > 0:
            self.poop_cd -= 1
        if self.squish_frames > 0:
            self.squish_frames -= 1
        if self.confuse_frames > 0:
            self.confuse_frames -= 1
        if self.stealth_frames > 0:
            self.stealth_frames -= 1
        if self.char.get("berserker"):
            self._berserker_active = self.hp > 0 and self.hp <= self.max_hp // 2
        if self.char.get("laser_eyes"):
            if self.laser_active > 0:
                self.laser_active -= 1
                if self.laser_hit_cd > 0:
                    self.laser_hit_cd -= 1
            elif self.laser_fire_cd > 0:
                self.laser_fire_cd -= 1
            else:
                self.laser_active  = FPS * 2   # fire for 2 seconds
                self.laser_fire_cd = FPS * 10  # reload: 10 seconds
                self.laser_hit_cd  = 0
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
        if self.char.get("anti_gravity"):
            eff_grav = 0.13
        elif self.char.get("ghost_float"):
            eff_grav = 0.06   # very slow drift downward
        elif self.char.get("slow_fall") and self.vy > 0:
            eff_grav = constants.GRAVITY * 0.35
        else:
            eff_grav = constants.GRAVITY
        self.vy += eff_grav
        self.y  += self.vy
        landed = False
        if constants.STAGE_VOID and self.y > HEIGHT + 30:
            self.hp = 0   # fell into the void
        elif not constants.STAGE_VOID and self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            landed = True
        elif self.y <= 20:
            self.y = 20
            self.vy = abs(self.vy) * 0.4   # bounce back down
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
        # Conveyor belt push — runs every frame while standing on one
        if self.on_ground:
            for plat in platforms:
                if (isinstance(plat, ConveyorBelt)
                        and abs(self.y - plat.y) <= 2
                        and plat.x - 20 <= self.x <= plat.x + plat.w + 20):
                    self.x += plat.speed
                    break
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
        if constants.GRAVITY < 0.3 or self.char.get("anti_gravity"):
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
        if self._berserker_active:
            spd *= 1.5

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
            # Confuse: swap left/right keys
            _lk = ctrl['right'] if self.confuse_frames > 0 else ctrl['left']
            _rk = ctrl['left']  if self.confuse_frames > 0 else ctrl['right']

            if can_atk and keys[ctrl['punch']] and self.punch_cooldown == 0:
                moving_toward = ((keys[_rk] and self.facing == 1) or
                                 (keys[_lk] and self.facing == -1))
                self._start('punch', 0.07)
                self.punch_cooldown = FPS        # 1 second
                self.is_crit = moving_toward or bool(self.char.get("always_crit"))
                if self.char.get("bounce_punch"):
                    self.pending_bounce = True
                if self.char.get("whip_punch") and self.whip_cooldown == 0:
                    self.pending_whip  = True
                    self.whip_cooldown = FPS * 2   # 2-second cooldown
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
            elif keys[_lk]:
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
            elif keys[_rk]:
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

        # Ghost free float: hold jump = rise, hold duck = sink (independent of attack)
        if self.char.get("ghost_float") and self.controls and self.hurt_timer == 0:
            jk = self.controls.get('jump')
            dk = self.controls.get('duck')
            if jk and keys[jk]:
                self.vy = max(self.vy - 1.2, -8)
                self.on_ground = False
                if self.action not in ('punch', 'kick'):
                    self.action = 'jump'
            elif dk and keys[dk]:
                self.vy = min(self.vy + 1.2, 8)
                self.on_ground = False

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
        if other.bubble_shield:
            other.flash_timer = 6   # visual deflect, no damage
            return
        if other.ducking and self.action == 'punch':
            return  # punches miss ducking opponents
        hit_cy = other.y - 70 * other.draw_scale
        hit_r  = 58 * other.draw_scale
        if self.char.get("wide_punch") and self.action == 'punch':
            hit_r *= 2.2
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
            if self._berserker_active:
                dmg = int(dmg * 1.5)
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
            if other.blocking and other.char.get("reflect_block") and dmg > 0:
                self.hp = max(0, self.hp - dmg // 2)
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
            if self.char.get("hammer_punch") and self.action == 'punch':
                other.squish_frames = 240  # 4 seconds
            if self.char.get("slam_kick") and self.action == 'kick':
                other.knockback = self.facing * 48
            if self.char.get("confuse_kick") and self.action == 'kick':
                other.confuse_frames = 180  # 3 seconds
            if self.char.get("stealth_punch") and self.action == 'punch':
                self.stealth_frames = 120   # 2 seconds invisible

    def draw(self, surface):
        _scale = self.draw_scale
        flash = (self.flash_timer % 4) < 2 and self.flash_timer > 0

        # Speedster: draw afterimage trail before main body
        if self.char.get("speedster"):
            self.trail.append((self.x, self.y))
            if len(self.trail) > 6:
                self.trail.pop(0)
            for i, (tx, ty) in enumerate(self.trail[:-1]):
                fade = (i + 1) / len(self.trail)
                tc = tuple(int(c * fade * 0.5) for c in self.color)
                pygame.draw.circle(surface, tc, (int(tx), int(ty - 60)), max(2, int(8 * fade)))
                pygame.draw.line(surface, tc, (int(tx), int(ty - 60 - 18)), (int(tx), int(ty - 30)), 2)
                pygame.draw.line(surface, tc, (int(tx), int(ty - 30)), (int(tx - 8), int(ty)), 2)
                pygame.draw.line(surface, tc, (int(tx), int(ty - 30)), (int(tx + 8), int(ty)), 2)

        if self.squish_frames > 0:
            # Draw stickman flat on a temp surface, then squish-scale it
            tmp_w = int(260 * _scale)
            tmp_h = int(220 * _scale)
            tmp = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
            cx = tmp_w // 2
            cy = int(tmp_h * 0.88)
            draw_stickman(tmp, cx, cy, self.color, self.facing, self.action, self.action_t,
                          flash=flash, scale=_scale, char_name=self.char["name"])
            sq_w = int(tmp_w * 1.55)
            sq_h = int(tmp_h * 0.35)
            squished = pygame.transform.scale(tmp, (sq_w, sq_h))
            bx = int(self.x) - sq_w // 2
            by = int(self.y) - int(cy * 0.35)
            surface.blit(squished, (bx, by))
            # Stars spinning above squished fighter
            star_cx = int(self.x)
            star_cy = by - 12
            for i in range(5):
                ang = math.radians((self.squish_frames * 7 + i * 72) % 360)
                sx2 = star_cx + int(math.cos(ang) * 18)
                sy2 = star_cy + int(math.sin(ang) * 7)
                pygame.draw.circle(surface, (255, 230, 0), (sx2, sy2), 4)
                pygame.draw.circle(surface, (255, 140, 0), (sx2, sy2), 2)
            result = None
        elif self.angle != 0.0:
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
        elif self.char.get("chameleon"):
            # Camouflage — draw on SRCALPHA surface then blit at low alpha
            tmp_w = int(300 * _scale)
            tmp_h = int(300 * _scale)
            tmp   = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
            cx    = tmp_w // 2
            cy    = int(tmp_h * 0.85)
            draw_stickman(tmp, cx, cy, self.color, self.facing, self.action, self.action_t,
                          flash=flash, scale=_scale, char_name=self.char["name"])
            # More visible when hurt, flashing, or attacking
            if flash or self.hurt_timer > 0:
                alpha = 210
            elif self.attacking:
                alpha = 90
            else:
                alpha = 35
            tmp.set_alpha(alpha)
            surface.blit(tmp, (int(self.x) - cx, int(self.y) - cy))
            result = (int(self.x + self.facing * 40 * _scale), int(self.y - 70 * _scale))
        else:
            _sw = int(50 * _scale)
            _sh = int(12 * _scale)
            if self.stealth_frames > 0 and (self.stealth_frames // 4) % 2 == 1:
                # Invisible phase — skip draw, return estimated attack pos
                result = (int(self.x + self.facing * 40 * _scale), int(self.y - 70 * _scale))
            else:
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
        if self._berserker_active:
            # Pulsing red aura
            pulse_r = 34 + int(math.sin(pygame.time.get_ticks() * 0.015) * 6)
            bsurf = pygame.Surface((pulse_r*2+4, pulse_r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(bsurf, (220, 30, 30, 60), (pulse_r+2, pulse_r+2), pulse_r)
            pygame.draw.circle(bsurf, (255, 80, 0, 120), (pulse_r+2, pulse_r+2), pulse_r, 3)
            surface.blit(bsurf, (int(self.x) - pulse_r - 2, int(self.y) - 80 - pulse_r - 2))
        if self.confuse_frames > 0:
            top_y = int(self.y) - LEG_LEN - BODY_LEN - NECK_LEN - HEAD_R * 2 - 60
            for i in range(5):
                ang = math.radians((self.confuse_frames * 8 + i * 72) % 360)
                cx2 = int(self.x) + int(math.cos(ang) * 16)
                cy2 = top_y + int(math.sin(ang) * 6)
                pygame.draw.circle(surface, (255, 80, 200), (cx2, cy2), 4)
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
        if self.char.get("anti_gravity"):
            eff_grav = 0.13
        elif self.char.get("ghost_float"):
            eff_grav = 0.06   # very slow drift downward
        elif self.char.get("slow_fall") and self.vy > 0:
            eff_grav = constants.GRAVITY * 0.35
        else:
            eff_grav = constants.GRAVITY
        self.vy += eff_grav
        self.y  += self.vy
        landed = False
        if constants.STAGE_VOID and self.y > HEIGHT + 30:
            self.hp = 0   # fell into the void
        elif not constants.STAGE_VOID and self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            landed = True
        elif self.y <= 20:
            self.y = 20
            self.vy = abs(self.vy) * 0.4   # bounce back down
        elif not self.char.get("phase"):
            for plat in platforms:
                if (self.vy >= 0 and prev_y <= plat.y and self.y >= plat.y
                        and plat.x - 25 <= self.x <= plat.x + plat.w + 25):
                    self.y = plat.y
                    self.vy = 0
                    self.x += plat.vx
                    if isinstance(plat, ConveyorBelt):
                        self.x += plat.speed
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
        if constants.GRAVITY < 0.3 or self.char.get("anti_gravity"):
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
                    self.is_crit = (self.ai_move == self.facing) or bool(self.char.get("always_crit"))
                    if self.char.get("bounce_punch"):
                        self.pending_bounce = True
                    if self.char.get("whip_punch") and self.whip_cooldown == 0:
                        self.pending_whip  = True
                        self.whip_cooldown = FPS * 2
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
            self.ai_attack = None
        elif self.ai_move != 0:
            _ai_spd = self.char["speed"] * self.speed_boost * (0.5 if self.shock_frames > 0 else 1.0)
            if self._berserker_active:
                _ai_spd *= 1.5
            self.x += self.ai_move * _ai_spd
            if self.on_ground and not self.attacking:
                self.action = 'walk'
                self.walk_t = (self.walk_t + 0.12) % 1.0
                self.action_t = self.walk_t
        else:
            if self.on_ground and not self.attacking:
                self.action = 'idle'

        # Ghost AI: steer vertically toward the target
        if self.char.get("ghost_float") and other is not None:
            dy = other.y - self.y
            if dy > 15:
                self.vy = min(self.vy + 0.7, 6)
            elif dy < -15:
                self.vy = max(self.vy - 0.7, -6)
            else:
                self.vy *= 0.85   # dampen vertical drift near target height
            self.on_ground = False
            if self.action not in ('punch', 'kick', 'hurt'):
                self.action = 'jump'

    def _decide(self, other):
        dist = abs(other.x - self.x)
        direction = 1 if other.x > self.x else -1

        # Dodge incoming attack
        if other.attacking and random.random() < self.dodge_chance:
            can_dodge = (self.on_ground and self.jumps_left > 0) or self.char.get("ghost_float")
            if can_dodge:
                self.vy = self.char["jump"]
                self.on_ground = False
                if not self.char.get("ghost_float"):
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
# Jungle snake NPC
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
