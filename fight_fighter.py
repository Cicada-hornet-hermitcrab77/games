import pygame
import math
import random
import constants
from constants import *
from fight_data import CHARACTERS, POWERUPS, STAGES, STAGE_MATCHUPS
from fight_drawing import draw_stickman
from fight_stage import ConveyorBelt

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
        self.pending_scroll     = False  # scroll_kick: spawn a growing scroll this frame
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
        # --- new characters ---
        self.kitsune_timer      = FPS * 9 if char_data.get("kitsune_barrage") else 0
        self.pending_kitsune    = False     # Kitsune: fire 9-direction barrage this frame
        self.pending_water_ball = False     # Riptide: spawn a water ball this frame
        self.pending_creator_platform = False  # The Creator: spawn a timed platform this frame
        self.creator_cd         = 0         # cooldown between platform creations
        self.run_streak         = 0         # Whirlpool: consecutive running frames
        self.smoke_particles    = []        # Shadowfax: [[x, y, life, max_life], ...]
        # Snake character
        self.snake_segs         = [[float(x), float(GROUND_Y)] for _ in range(3)] if char_data.get("snake") else []
        self.snake_length       = 3
        self.snake_contact_cd   = 0
        # New characters
        self.undead_used        = False     # Necromancer: has the revive been used
        self.chaos_timer        = FPS * 12 if char_data.get("chaos_timer") else 0
        self.pending_chaos      = False     # Joker: apply random effect this frame
        self.time_freeze_timer  = FPS * 18 if char_data.get("time_freeze") else 0
        self.pending_time_freeze = False    # Time Lord: apply freeze this frame
        self.pending_bee        = False     # Beekeeper: spawn bee swarm this frame
        self.attack_cycle       = 0         # Shifter: 0=normal, 1=whip, 2=snipe
        self.pending_snipe      = False     # Shifter: fire snipe shot this frame
        # Batch 3 characters
        self.kamikaze_exploded  = False
        self.shrink_frames      = 0
        self.sticky_frames      = 0
        self.auto_fire_timer    = FPS * 5  if char_data.get("auto_fire")      else 0
        self.pending_autofire   = False
        self.auto_teleport_timer = FPS * 8 if char_data.get("auto_teleport")  else 0
        self.pending_thunder    = False
        # New batch
        self.pending_storm      = False   # Storm Caller: random lightning bolt
        self.quake_pending      = False   # Quaker: shockwave on heavy landing
        self._prev_vy           = 0.0     # Quaker: track vy before landing
        self.combo_timer        = 0       # Echo: frames since last punch hit
        self.combo_count        = 0       # Echo: consecutive combo count
        self.bomb_spawn_timer   = FPS * 5 if char_data.get("bomb_character") else 0
        self.one_shot_armed     = False   # Godslayer: one-shot primed
        self.one_shot_used      = False   # Godslayer: has it fired this life
        self.punch_seven_count  = 0       # 777: count punch hits for bonus
        self.void_falls         = 0       # Void Master / void death tracking
        self._in_void           = False   # prevent counting same fall multiple times
        self.chainsaw_cd        = 0       # Chainsaw Man: proximity damage cooldown
        self.pending_totem      = False   # Great Totem Spirit: spawn 5 falling totem poles
        self.pending_portal     = False   # Portal Maker: replace the 2 stage portals
        self.prime_index        = 0       # Prime Time: index into prime sequence
        self.pending_remote     = False   # Rage Quitter: fire remote controller
        self.pending_apple      = False   # Gravity: drop 20 apples
        self.pending_venom      = False   # Spitting Cobra: shoot a venom bean
        self._paradox_used      = False   # Paradox: HP swap used this life
        self.rainbow_poop_timer = FPS * 4 if char_data.get("rainbow_poop") else 0
        self.pending_rainbow_poop = False  # Rainbow Man: drop a random powerup this frame
        self.chomp_cooldown     = 0       # Pacman: cooldown between chomps
        self.cb_idle_timer      = FPS * 8 if char_data.get("chicken_banana") else 0  # ChickenBanana: countdown to next ram
        self.cb_ramming         = False   # ChickenBanana: currently ramming
        self.cb_ram_timer       = 0       # ChickenBanana: ram duration frames
        self.soul_switch_timer  = FPS * 5 if char_data.get("soul_master") else 0  # Soul Master
        self.dementor_timer     = FPS * 20 if char_data.get("dementor_heal") else 0  # Dementor
        self.pending_plant      = False   # Druid: spawn a rising plant spike this frame
        # New batch
        self.overdrive_charge   = 0      # Overdrive: hits received toward charge
        self.overdrive_ready    = False  # Overdrive: next attack is 3x
        self.hypno_frames       = 0      # Hypnotist: frames of hypnosis remaining
        self.hypno_source_x     = 0.0   # Hypnotist: x of the hypnotist
        self.pending_quake_wave = False  # Fault Line: spawn ground shockwave this frame
        self.revenant_count     = 0      # Revenant: revivals used (max 2)
        self.shock_aura_timer   = FPS * 3 if char_data.get("shock_aura") else 0
        self.pending_mine       = False  # Trap Master: plant a mine this frame

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
        if self.char.get("rainbow_poop"):
            self.poop_timer = FPS * 999  # Rainbow Man: always active
        elif self.poop_timer > 0:
            self.poop_timer -= 1
        if self.poop_cd > 0:
            self.poop_cd -= 1
        if self.squish_frames > 0:
            self.squish_frames -= 1
        if self.confuse_frames > 0:
            self.confuse_frames -= 1
        if self.hypno_frames > 0:
            self.hypno_frames -= 1
        if self.char.get("shade"):
            self.stealth_frames = 0 if (self.action in ('punch', 'kick') and self.attacking) else 999
        elif self.stealth_frames > 0:
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
        # Kitsune auto barrage — fires every 9 seconds
        if self.char.get("kitsune_barrage"):
            if self.kitsune_timer > 0:
                self.kitsune_timer -= 1
            else:
                self.pending_kitsune = True
                self.kitsune_timer   = FPS * 9
        # Rainbow Man — drops a random powerup every 4 seconds
        if self.char.get("rainbow_poop"):
            if self.rainbow_poop_timer > 0:
                self.rainbow_poop_timer -= 1
            else:
                self.pending_rainbow_poop = True
                self.rainbow_poop_timer   = FPS * 4
        # Freeze laser (Medusa) — same timer logic as laser_eyes
        if self.char.get("freeze_laser"):
            if self.laser_active > 0:
                self.laser_active -= 1
                if self.laser_hit_cd > 0:
                    self.laser_hit_cd -= 1
            elif self.laser_fire_cd > 0:
                self.laser_fire_cd -= 1
            else:
                self.laser_active  = FPS * 2
                self.laser_fire_cd = FPS * 10
                self.laser_hit_cd  = 0
        # The Creator platform cooldown
        if self.creator_cd > 0:
            self.creator_cd -= 1
        # Janitor: instantly clear all negative status effects
        if self.char.get("immune"):
            self.poison_frames = 0; self.fire_frames  = 0
            self.freeze_frames = 0; self.shock_frames = 0
            self.squish_frames = 0; self.confuse_frames = 0
        # Shadowfax smoke particle aging
        self.smoke_particles = [p for p in self.smoke_particles if p[2] > 0]
        for p in self.smoke_particles:
            p[2] -= 1
        # Snake contact cooldown
        if self.snake_contact_cd > 0:
            self.snake_contact_cd -= 1
        # Enraged: always in berserk state
        if self.char.get("always_berserk"):
            self._berserker_active = True
        # Godslayer: arm one-shot when HP falls below 30%
        if (self.char.get("godslayer") and not self.one_shot_used
                and self.hp <= int(self.max_hp * 0.30) and self.hp > 0):
            self.one_shot_armed = True
        # Joker chaos timer
        if self.char.get("chaos_timer"):
            if self.chaos_timer > 0:
                self.chaos_timer -= 1
            else:
                self.pending_chaos = True
                self.chaos_timer   = FPS * 12
        # Shrink frames — restore scale when expiry
        if self.shrink_frames > 0:
            self.shrink_frames -= 1
            if self.shrink_frames == 0 and not self.char.get("tiny"):
                self.draw_scale = 2.0 if self.char.get("giant") else 1.0
        # Sticky frames
        if self.sticky_frames > 0:
            self.sticky_frames -= 1
        # Echo combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_count = 0
        # Pyro auto fire
        if self.char.get("auto_fire"):
            if self.auto_fire_timer > 0:
                self.auto_fire_timer -= 1
            else:
                self.pending_autofire    = True
                self.auto_fire_timer     = FPS * 5
        # Auto teleport
        if self.char.get("auto_teleport"):
            if self.auto_teleport_timer > 0:
                self.auto_teleport_timer -= 1
            else:
                self.x = float(random.randint(80, WIDTH - 80))
                self.flash_timer = 12
                self.auto_teleport_timer = FPS * 8
        # Time Lord freeze timer
        if self.char.get("time_freeze"):
            if self.time_freeze_timer > 0:
                self.time_freeze_timer -= 1
            else:
                self.pending_time_freeze = True
                self.time_freeze_timer   = FPS * 18
        # Dementor: full heal every 20 seconds
        if self.char.get("dementor_heal"):
            if self.dementor_timer > 0:
                self.dementor_timer -= 1
            else:
                self.hp = self.max_hp
                self.dementor_timer = FPS * 20
                self.flash_timer = max(self.flash_timer, 15)

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
            if self.hurt_timer == 0 and self.char.get("rage_build"):
                self.punch_boost = min(self.punch_boost + 1, 15)

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
        self._prev_vy = self.vy   # capture before zeroing (quake_land)
        self.y  += self.vy
        landed = False
        if constants.STAGE_VOID and self.y > HEIGHT + 30:
            if not self._in_void:
                self._in_void = True
                self.void_falls += 1
            if self.char.get("void_immune"):
                self.y = float(GROUND_Y - 70)
                self.vy = 0
                self._in_void = False
            else:
                self.hp = 0   # fell into the void
        elif constants.STAGE_CEILING and self.y < -30:
            self.hp = 0   # hit the ceiling (Under the Void)
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
            if self.char.get("quake_land") and self._prev_vy > 9:
                self.quake_pending = True
        # Jetpack: always has at least 1 jump available
        if self.char.get("jetpack") and not self.on_ground:
            self.jumps_left = max(self.jumps_left, 1)
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
        # Whirlpool momentum: speed scales with consecutive running frames
        if self.char.get("momentum") and self.run_streak > 0:
            spd *= 1.0 + min(self.run_streak, 240) / 240.0 * 1.5

        # Disorientated: build swapped effective controls (W=S, A=D, punch=kick)
        if self.char.get("disorientated") and self.controls:
            _ec = dict(left=self.controls.get('right'), right=self.controls.get('left'),
                       jump=self.controls.get('duck'),  duck=self.controls.get('jump'),
                       punch=self.controls.get('kick'), kick=self.controls.get('punch'),
                       block=self.controls.get('block'))
        else:
            _ec = self.controls

        duck_key  = _ec.get('duck')  if _ec else None
        block_key = _ec.get('block') if _ec else None
        self.ducking  = (bool(duck_key  and keys[duck_key])  and
                         self.on_ground and self.hurt_timer == 0 and not self.attacking
                         and not self.char.get("snake"))
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

        _sticky_save_x = self.x   # captured before key movement for Sticker

        if self.hurt_timer == 0 and self.freeze_frames == 0 and not self.ducking and not self.blocking:
            ctrl = _ec   # use effective controls (swapped if Disorientated)
            can_atk = not self.attacking or self.action in ('idle', 'walk', 'jump')
            # Confuse: swap left/right keys
            _lk = ctrl['right'] if self.confuse_frames > 0 else ctrl['left']
            _rk = ctrl['left']  if self.confuse_frames > 0 else ctrl['right']
            if self.hypno_frames > 0:
                _lk = self.x > self.hypno_source_x
                _rk = self.x < self.hypno_source_x

            if can_atk and keys[ctrl['punch']] and self.punch_cooldown == 0:
                moving_toward = ((keys[_rk] and self.facing == 1) or
                                 (keys[_lk] and self.facing == -1))
                self._start('punch', 0.07)
                self.punch_cooldown = 8 if self.char.get("rapid_fire") else FPS
                self.is_crit = moving_toward or bool(self.char.get("always_crit"))
                if self.char.get("bounce_punch"):
                    self.pending_bounce = True
                if self.char.get("whip_punch") and self.whip_cooldown == 0:
                    self.pending_whip  = True
                    self.whip_cooldown = FPS * 2   # 2-second cooldown
                if self.char.get("bee_punch"):
                    self.pending_bee = True
                if self.char.get("cycle_attack"):
                    if self.attack_cycle == 1:
                        self.pending_whip = True
                    elif self.attack_cycle == 2:
                        self.pending_snipe = True
                    self.attack_cycle = (self.attack_cycle + 1) % 3
                if self.char.get("thunder_punch"):
                    self.pending_thunder = True
                if self.char.get("storm_punch"):
                    self.pending_storm = True
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
                if self.char.get("scroll_kick"):
                    self.pending_scroll = True
                if self.char.get("totem_kick"):
                    self.pending_totem = True
                if self.char.get("portal_kick"):
                    self.pending_portal = True
                if self.char.get("apple_kick"):
                    self.pending_apple = True
                if self.char.get("remote_kick"):
                    self.pending_remote = True
                if self.char.get("venom_kick"):
                    self.pending_venom = True
                if self.char.get("plant_kick"):
                    self.pending_plant = True
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
                if self.char.get("water_kick"):
                    self.pending_water_ball = True
                if self.char.get("creator_kick") and self.creator_cd == 0:
                    self.pending_creator_platform = True
                    self.creator_cd = FPS * 3   # 3-second cooldown
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
                if self.char.get("momentum"):
                    self.run_streak = min(240, self.run_streak + 1)
                if self.char.get("smoke_trail") and random.random() < 0.5:
                    self.smoke_particles.append([self.x + random.randint(-8, 8),
                                                 self.y - 40 + random.randint(-15, 15), 42, 42])
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
                if self.char.get("momentum"):
                    self.run_streak = min(240, self.run_streak + 1)
                if self.char.get("smoke_trail") and random.random() < 0.5:
                    self.smoke_particles.append([self.x + random.randint(-8, 8),
                                                 self.y - 40 + random.randint(-15, 15), 42, 42])
            else:
                if self.on_ground and not self.attacking:
                    self.action = 'idle'
                if self.char.get("momentum") and self.run_streak > 0:
                    self.run_streak = max(0, self.run_streak - 3)
        # Shadowfax smoke during dash
        if self.dash_frames > 0 and self.char.get("smoke_trail") and random.random() < 0.7:
            self.smoke_particles.append([self.x + random.randint(-6, 6),
                                         self.y - 50 + random.randint(-10, 10), 38, 38])

        # Sticker: opponent can't move horizontally while sticky_frames > 0
        if self.sticky_frames > 0:
            self.x = _sticky_save_x

        # Ghost free float: hold jump = rise, hold duck = sink (independent of attack)
        if self.char.get("ghost_float") and _ec and self.hurt_timer == 0:
            jk = _ec.get('jump')
            dk = _ec.get('duck')
            if jk and keys[jk]:
                self.vy = max(self.vy - 1.2, -8)
                self.on_ground = False
                if self.action not in ('punch', 'kick'):
                    self.action = 'jump'
            elif dk and keys[dk]:
                self.vy = min(self.vy + 1.2, 8)
                self.on_ground = False

        self._prev_left  = bool(_ec and keys[_ec.get('left',  0)])
        self._prev_right = bool(_ec and keys[_ec.get('right', 0)])

        # Snake: override physics — free 4-directional movement, no gravity
        if self.char.get("snake"):
            self.vy = 0
            self.on_ground = False
            snk_spd = 3.5
            if _ec:
                jk = _ec.get('jump')
                dk = _ec.get('duck')
                if jk and keys[jk]:
                    self.y -= snk_spd
                elif dk and keys[dk]:
                    self.y += snk_spd
            self.y = max(50.0, min(float(GROUND_Y), self.y))
            self.x = max(50.0, min(float(WIDTH - 50), self.x))
            self.snake_segs.insert(0, [float(self.x), float(self.y)])
            max_segs = self.snake_length * 10
            if len(self.snake_segs) > max_segs:
                self.snake_segs = self.snake_segs[:max_segs]

        # Pacman: chomp nearby enemy for 50 dmg, grow bigger
        if self.char.get("chomp"):
            if self.chomp_cooldown > 0:
                self.chomp_cooldown -= 1
            elif other is not self and abs(self.x - other.x) <= 55:
                other.hp = max(0, other.hp - 50)
                other.flash_timer = 12
                other.knockback = self.facing * 4
                self.draw_scale = min(2.5, self.draw_scale + 0.2)
                self.chomp_cooldown = FPS * 2

        # ChickenBanana: automatically rams in facing direction every 8 seconds
        if self.char.get("chicken_banana"):
            if self.cb_ramming:
                self.x += self.facing * 22
                self.cb_ram_timer -= 1
                if abs(self.x - other.x) <= 55:
                    other.hp = 0
                    self.cb_ramming = False
                    self.cb_idle_timer = FPS * 8  # cooldown before next ram
                elif self.x <= 50 or self.x >= WIDTH - 50:
                    self.hp = max(0, self.hp - 10)
                    self.flash_timer = 15
                    self.cb_ramming = False
                    self.x = max(60.0, min(float(WIDTH - 60), self.x))
                    self.cb_idle_timer = FPS * 8
                elif self.cb_ram_timer <= 0:
                    self.cb_ramming = False
                    self.cb_idle_timer = FPS * 8
            else:
                if self.cb_idle_timer > 0:
                    self.cb_idle_timer -= 1
                else:
                    self.cb_ramming = True
                    self.cb_ram_timer = FPS // 2  # ram lasts 0.5 seconds

        # Soul Master: soul hops to a new position every 5 seconds
        if self.char.get("soul_master"):
            if self.soul_switch_timer > 0:
                self.soul_switch_timer -= 1
            else:
                self.x = float(random.randint(120, WIDTH - 120))
                self.vy = -5
                self.flash_timer = 20
                self.soul_switch_timer = FPS * 5

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
            # Godslayer one-shot fires before normal damage calc
            if self.char.get("godslayer") and self.one_shot_armed and not self.one_shot_used:
                other.hp = max(0, other.hp - 999)
                other.flash_timer = 20
                other.action = 'hurt'
                other.hurt_timer = 30
                other.attacking = False
                other.knockback = self.facing * 20
                self.attack_hit = True
                self.one_shot_armed = False
                self.one_shot_used  = True
                return
            if self.action == 'punch':
                if self.char.get("halves_punch"):
                    dmg = max(1, other.hp // 2)
                elif self.char.get("copy_punch"):
                    dmg = other.char["punch_dmg"] + self.punch_boost
                else:
                    dmg = self.char["punch_dmg"] + self.punch_boost
                    if self.is_crit:
                        dmg += 10
                        other.crit_display_timer = 70
                if self.char.get("seven_punch"):
                    self.punch_seven_count += 1
                    if self.punch_seven_count % 7 == 0:
                        dmg += 7
            else:
                dmg = self.char["kick_dmg"] + self.kick_boost
                if self.char.get("flash_kick"):
                    self.x = max(30.0, min(float(WIDTH - 30), other.x - other.facing * 60))
                    self.facing = other.facing   # face toward opponent's back
            if self.char.get("prime_dmg"):
                _PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71]
                dmg = _PRIMES[self.prime_index % len(_PRIMES)]
                self.prime_index += 1
            if self.char.get("wild_attack"):
                dmg = random.randint(1, 40)
            # Mirage: 35% dodge chance — sidestep and skip all damage
            if other.char.get("mirage") and random.random() < 0.35:
                other.flash_timer = 6
                other.x = max(30.0, min(float(WIDTH - 30), other.x + random.choice([-55, 55])))
                self.attack_hit = True
                return
            if self.char.get("phantom_strike") and self.action == 'punch':
                self.x = max(30.0, min(float(WIDTH - 30), other.x - self.facing * 55))
                self.flash_timer = 8
            if self.char.get("lucky_strike") and random.random() < 0.25:
                dmg *= 3
            if self.char.get("overdrive") and self.overdrive_ready:
                dmg *= 3
                self.overdrive_ready  = False
                self.overdrive_charge = 0
            if other.char.get("stone_skin"):
                dmg = int(dmg * 0.6)
            # Big Bad Critter Clad: only critical punch hits deal full damage; others get ~20%
            if other.char.get("crit_only"):
                if self.action == 'punch' and not self.is_crit:
                    dmg = max(1, int(dmg * 0.2))
                elif self.action == 'kick':
                    dmg = max(1, int(dmg * 0.2))
            # hp_swap (Paradox): swap both HP values once per life, skip normal damage
            if self.char.get("hp_swap") and self.action == 'punch' and not self._paradox_used:
                self.hp, other.hp = other.hp, self.hp
                self._paradox_used = True
                other.flash_timer = 20
                other.action = 'hurt'
                other.hurt_timer = 22
                other.attacking = False
                other.knockback = self.facing * 6
                self.attack_hit = True
                return
            if other.shield:
                dmg = max(1, int(dmg * 0.5))
            if self._berserker_active:
                dmg = int(dmg * 1.5)
            if other.blocking and not (self.char.get("crush_punch") and self.action == 'punch'):
                if other.char.get("absorb_block"):
                    other.hp = min(other.max_hp, other.hp + 6)
                    dmg = 0
                else:
                    bsk = other.char.get("block", 5)
                    perfect_p = bsk * 0.025
                    partial_p = bsk * 0.05
                    r = random.random()
                    if r < perfect_p:
                        dmg = 0
                    elif r < perfect_p + partial_p:
                        dmg = max(1, dmg // 2)
            other.hp = max(0, other.hp - dmg)
            if other.char.get("overdrive") and dmg > 0 and not other.blocking:
                other.overdrive_charge += 1
                if other.overdrive_charge >= 4:
                    other.overdrive_ready  = True
                    other.overdrive_charge = 0
            if other.char.get("juggernaut"):
                other.knockback  = 0
                other.hurt_timer = min(other.hurt_timer, 8)
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
            if self.char.get("slam_kick") and self.action == 'kick':
                other.knockback = self.facing * 48
            if self.char.get("stealth_punch") and self.action == 'punch':
                self.stealth_frames = 120   # 2 seconds invisible
            # Janitor: status effects cannot be applied to him
            if not other.char.get("immune"):
                if self.char.get("fire_punch") and self.action == 'punch':
                    if other.fire_frames == 0:
                        other.fire_tick = 480
                    other.fire_frames = max(other.fire_frames, 960)  # 16 sec burn
                if self.char.get("freeze_kick") and self.action == 'kick':
                    other.freeze_frames = 180  # 3 seconds
                if self.char.get("scorpio_kick") and self.action == 'kick':
                    other.freeze_frames = 180
                    if other.poison_frames == 0: other.poison_tick = 180
                    other.poison_frames = max(other.poison_frames, 180)
                if self.char.get("shock_punch") and self.action == 'punch':
                    other.shock_frames = 480   # 8 seconds
                if self.char.get("shock_kick") and self.action == 'kick':
                    other.shock_frames = max(other.shock_frames, 480)   # 8 seconds
                if self.char.get("hammer_punch") and self.action == 'punch':
                    other.squish_frames = 240  # 4 seconds
                if self.char.get("confuse_kick") and self.action == 'kick':
                    other.confuse_frames = 180  # 3 seconds
                if self.char.get("plague_punch") and self.action == 'punch':
                    if other.fire_frames == 0:    other.fire_tick = 480
                    other.fire_frames    = max(other.fire_frames,    480)
                    if other.poison_frames == 0:  other.poison_tick = 180
                    other.poison_frames  = max(other.poison_frames,  480)
                    other.shock_frames   = max(other.shock_frames,   240)
            if self.char.get("iron_fist") and self.action == 'punch':
                other.knockback  *= 3
                other.hurt_timer  = max(other.hurt_timer, 40)
            if self.char.get("drain_kick") and self.action == 'kick':
                heal = min(20, self.max_hp - self.hp)
                self.hp = min(self.max_hp, self.hp + heal)
            if self.char.get("shrink_kick") and self.action == 'kick':
                if not other.char.get("immune"):
                    other.shrink_frames = 300   # 5 seconds
                    if not other.char.get("giant"):
                        other.draw_scale = 0.45
            if self.char.get("launch_kick") and self.action == 'kick':
                other.vy          = -22
                other.on_ground   = False
            if self.char.get("speed_steal"):
                steal             = 0.08
                other.speed_boost = max(0.3, other.speed_boost - steal)
                self.speed_boost  = min(3.0, self.speed_boost  + steal)
            if self.char.get("sticky_punch") and self.action == 'punch':
                if not other.char.get("immune"):
                    other.sticky_frames = 120   # 2 seconds
            if self.char.get("magnet_punch") and self.action == 'punch':
                pull = 100
                if other.x > self.x:
                    other.x = max(self.x + 30, other.x - pull)
                else:
                    other.x = min(self.x - 30, other.x + pull)
            if self.char.get("combo_punch") and self.action == 'punch':
                if self.combo_timer > 0:
                    self.combo_count = min(self.combo_count + 1, 5)
                    bonus = self.combo_count * 5
                    other.hp = max(0, other.hp - bonus)
                else:
                    self.combo_count = 1
                self.combo_timer = 90   # 1.5s window
            if self.char.get("steal_kick") and self.action == 'kick':
                if other.active_powerups:
                    stolen_name = next(iter(other.active_powerups))
                    stolen_t    = other.active_powerups.pop(stolen_name)
                    self.active_powerups[stolen_name] = stolen_t
            if self.char.get("drain_punch") and self.action == 'punch':
                self.hp = min(self.max_hp, self.hp + 15)
            if self.char.get("sleep_punch") and self.action == 'punch':
                other.hurt_timer = max(other.hurt_timer, 90)
            if self.char.get("reaper_kick") and self.action == 'kick':
                if other.hp > 0 and other.hp <= int(other.max_hp * 0.20):
                    other.hp = 0
            if self.char.get("siphon_leech"):
                self.hp = min(self.max_hp, self.hp + 10)
            if self.char.get("swap_kick") and self.action == 'kick':
                self.x, other.x = other.x, self.x
            if self.char.get("grab_punch") and self.action == 'punch':
                other.x = max(50.0, min(float(WIDTH - 50), self.x + self.facing * 50))
            if not other.char.get("immune"):
                if self.char.get("confuse_punch") and self.action == 'punch':
                    other.confuse_frames = max(other.confuse_frames, 120)
                if self.char.get("slow_punch") and self.action == 'punch':
                    other.shock_frames = max(other.shock_frames, 360)
                if self.char.get("hypno_kick") and self.action == 'kick':
                    other.hypno_frames   = 120
                    other.hypno_source_x = float(self.x)
            if self.char.get("decay_punch") and self.action == 'punch':
                other.max_hp = max(1, other.max_hp - 8)
                other.hp     = min(other.hp, other.max_hp)
            if self.char.get("quake_punch") and self.action == 'punch':
                self.pending_quake_wave = True
            if self.char.get("mine_kick") and self.action == 'kick':
                self.pending_mine = True

    def draw(self, surface):
        _scale = self.draw_scale
        flash = (self.flash_timer % 4) < 2 and self.flash_timer > 0

        # Snake body segments — drawn as blocks like the classic snake game
        if self.char.get("snake") and len(self.snake_segs) > 0:
            bsz = 16   # block size in pixels
            step = 8
            drawn = 0
            for i in range(step, len(self.snake_segs), step):
                seg = self.snake_segs[i]
                bx  = int(seg[0]) - bsz // 2
                by  = int(seg[1]) - bsz // 2
                g   = min(230, 80 + drawn * 18)
                pygame.draw.rect(surface, (10, g, 20),   (bx, by, bsz, bsz))
                pygame.draw.rect(surface, (40, min(255, g + 60), 40), (bx, by, bsz, bsz), 2)
                drawn += 1

        # Shadowfax smoke trail — drawn behind everything
        for sp in self.smoke_particles:
            frac = sp[2] / max(1, sp[3])
            gray = int(55 + 130 * frac)
            r    = max(2, int(3 + 9 * frac))
            pygame.draw.circle(surface, (gray, gray, min(255, gray + 25)), (int(sp[0]), int(sp[1])), r)

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
        elif self.char.get("snake"):
            # Draw snake as a pure block — head block only (body drawn above)
            bsz = 18
            hx2 = int(self.x) - bsz // 2
            hy2 = int(self.y) - bsz - 4
            head_col = (255, 255, 255) if flash else (20, 200, 60)
            pygame.draw.rect(surface, head_col,    (hx2, hy2, bsz, bsz))
            pygame.draw.rect(surface, (40, 255, 80), (hx2, hy2, bsz, bsz), 2)
            # Pixel eyes
            for side in (-1, 1):
                ex2 = int(self.x) + side * 4
                ey2 = hy2 + 5
                pygame.draw.rect(surface, (255, 255, 0), (ex2 - 2, ey2, 3, 3))
            # Forked tongue
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                tx0 = int(self.x) + self.facing * (bsz // 2)
                ty0 = hy2 + bsz // 2
                pygame.draw.line(surface, (220, 30, 30), (tx0, ty0),
                                 (tx0 + self.facing * 9, ty0 - 3), 1)
                pygame.draw.line(surface, (220, 30, 30), (tx0, ty0),
                                 (tx0 + self.facing * 9, ty0 + 3), 1)
            result = (int(self.x + self.facing * (bsz // 2 + 4)), hy2 + bsz // 2)
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
        if self.char.get("cycle_attack"):
            _cycle_labels = ["NRM", "WHP", "SNP"]
            _cycle_colors = [(200, 200, 200), (180, 100, 20), (80, 180, 255)]
            lbl = font_tiny.render(_cycle_labels[self.attack_cycle], True, _cycle_colors[self.attack_cycle])
            surface.blit(lbl, (int(self.x) - lbl.get_width() // 2,
                               int(self.y) - LEG_LEN - BODY_LEN - NECK_LEN - HEAD_R * 2 - 30))
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
            if self.hurt_timer == 0 and self.char.get("rage_build"):
                self.punch_boost = min(self.punch_boost + 1, 15)

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
        self._prev_vy = self.vy
        self.y  += self.vy
        landed = False
        if constants.STAGE_VOID and self.y > HEIGHT + 30:
            if not self._in_void:
                self._in_void = True
                self.void_falls += 1
            if self.char.get("void_immune"):
                self.y = float(GROUND_Y - 70)
                self.vy = 0
                self._in_void = False
            else:
                self.hp = 0   # fell into the void
        elif constants.STAGE_CEILING and self.y < -30:
            self.hp = 0   # hit the ceiling (Under the Void)
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
            if self.char.get("quake_land") and self._prev_vy > 9:
                self.quake_pending = True
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

        # Rainbow Man passive poop timer (AI version)
        if self.char.get("rainbow_poop"):
            if self.rainbow_poop_timer > 0:
                self.rainbow_poop_timer -= 1
            else:
                self.pending_rainbow_poop = True
                self.rainbow_poop_timer   = FPS * 4
        # Pacman chomp (AI version)
        if self.char.get("chomp"):
            if self.chomp_cooldown > 0:
                self.chomp_cooldown -= 1
            elif other is not self and abs(self.x - other.x) <= 55:
                other.hp = max(0, other.hp - 50)
                other.flash_timer = 12
                other.knockback = self.facing * 4
                self.draw_scale = min(2.5, self.draw_scale + 0.2)
                self.chomp_cooldown = FPS * 2
        # ChickenBanana ram (AI version)
        if self.char.get("chicken_banana"):
            if self.cb_ramming:
                self.x += self.facing * 22
                self.cb_ram_timer -= 1
                if abs(self.x - other.x) <= 55:
                    other.hp = 0
                    self.cb_ramming = False
                elif self.x <= 50 or self.x >= WIDTH - 50:
                    self.hp = max(0, self.hp - 10)
                    self.flash_timer = 15
                    self.cb_ramming = False
                    self.x = max(60.0, min(float(WIDTH - 60), self.x))
                elif self.cb_ram_timer <= 0:
                    self.cb_ramming = False
            else:
                if self.action == 'idle' and self.on_ground:
                    self.cb_idle_timer += 1
                else:
                    self.cb_idle_timer = 0
                if self.cb_idle_timer >= FPS * 10:
                    self.cb_ramming = True
                    self.cb_ram_timer = FPS * 2
                    self.cb_idle_timer = 0
        # Soul Master soul hop (AI version)
        if self.char.get("soul_master"):
            if self.soul_switch_timer > 0:
                self.soul_switch_timer -= 1
            else:
                self.x = float(random.randint(120, WIDTH - 120))
                self.vy = -5
                self.flash_timer = 20
                self.soul_switch_timer = FPS * 5

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
                    self.punch_cooldown = 8 if self.char.get("rapid_fire") else FPS
                    self.is_crit = (self.ai_move == self.facing and random.random() > 0.5) or bool(self.char.get("always_crit"))
                    if self.char.get("bounce_punch"):
                        self.pending_bounce = True
                    if self.char.get("whip_punch") and self.whip_cooldown == 0:
                        self.pending_whip  = True
                        self.whip_cooldown = FPS * 2
                    if self.char.get("bee_punch"):
                        self.pending_bee = True
                    if self.char.get("cycle_attack"):
                        if self.attack_cycle == 1:
                            self.pending_whip = True
                        elif self.attack_cycle == 2:
                            self.pending_snipe = True
                        self.attack_cycle = (self.attack_cycle + 1) % 3
                    if self.char.get("thunder_punch"):
                        self.pending_thunder = True
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
                    if self.char.get("venom_kick"):
                        self.pending_venom = True
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
                    if self.char.get("plant_kick"):
                        self.pending_plant = True
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
