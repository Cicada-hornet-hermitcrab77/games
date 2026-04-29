import pygame
import sys
import math
import socket
import threading
import fight_network as _net
from constants import *
from fight_data import CHARACTERS, STAGES, STAGE_MATCHUPS
from fight_drawing import draw_bg, draw_stickman

# Shared flag: set True when player types "42" on the main menu
_type42_typed = [False]
# Shared flag: set True when player idles on stage select for 30 seconds
_map_man_flag = [False]
# Touch-control device flags: which players use on-screen buttons (default: both)
touch_p1_enabled = [True]
touch_p2_enabled = [True]

# ---------------------------------------------------------------------------
# TouchControls — on-screen buttons for touch / no-keyboard play
# ---------------------------------------------------------------------------

class _KeysProxy:
    """Wraps pygame's ScancodeWrapper so touch-injected keycodes work alongside
    large SDL arrow-key constants (K_LEFT = 1073741904 etc.) without converting
    to a plain list that would be out-of-bounds.
    When block_real=True, only touch-injected keys register (Buttons mode)."""
    __slots__ = ('_real', '_overrides', '_block_real')

    def __init__(self, real_keys, overrides, block_real=False):
        self._real       = real_keys
        self._overrides  = overrides
        self._block_real = block_real

    def __getitem__(self, key):
        v = self._overrides.get(key)
        if v is not None:
            return v
        return False if self._block_real else self._real[key]


class TouchControls:
    """7-button on-screen overlay. Supports multi-touch via FINGER events
    and single-touch mouse fallback. player=1 or 2; two_player reshuffles P1
    attacks inward so P2 controls fit on the right side."""

    _BTN_R = 28   # button radius in pixels

    # Single-player P1 layout (attacks on far right)
    _LAYOUT_1P = [
        ('jump',  90, 445),
        ('left',  42, 490),
        ('right', 138, 490),
        ('duck',  90, 530),
        ('punch', 755, 458),
        ('kick',  820, 458),
        ('block', 787, 515),
    ]
    # 2-player P1 layout (attacks moved to center-left)
    _LAYOUT_2P_P1 = [
        ('jump',  80, 445),
        ('left',  35, 490),
        ('right', 125, 490),
        ('duck',  80, 530),
        ('punch', 235, 462),
        ('kick',  300, 462),
        ('block', 267, 510),
    ]
    # 2-player P2 layout (attacks center-right, movement far right)
    _LAYOUT_2P_P2 = [
        ('punch', 600, 462),
        ('kick',  665, 462),
        ('block', 632, 510),
        ('jump',  820, 445),
        ('left',  775, 490),
        ('right', 865, 490),
        ('duck',  820, 530),
    ]

    _LABELS = {'left': '<', 'right': '>', 'jump': '^', 'duck': 'v',
               'punch': 'P', 'kick': 'K', 'block': 'B'}
    _COLORS = {
        'left': (60, 80, 180), 'right': (60, 80, 180),
        'jump': (60, 160, 80), 'duck':  (60, 140, 140),
        'punch': (180, 60, 60), 'kick': (180, 120, 30),
        'block': (120, 60, 180),
    }

    def __init__(self, ctrl, player=1, two_player=False):
        self.ctrl = ctrl
        if two_player and player == 2:
            self._layout = self._LAYOUT_2P_P2
        elif two_player:
            self._layout = self._LAYOUT_2P_P1
        else:
            self._layout = self._LAYOUT_1P
        self._finger     = {}
        self._mouse_held = None
        self.held        = set()

    # ── hit-test ──────────────────────────────────────────────────────────────
    def _hit(self, x, y):
        r2 = self._BTN_R ** 2
        for name, cx, cy in self._layout:
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                return name
        return None

    # ── event handler — call once per event in the game loop ─────────────────
    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            fx, fy = int(event.x * WIDTH), int(event.y * HEIGHT)
            btn = self._hit(fx, fy)
            self._finger[event.finger_id] = btn
            if btn:
                self.held.add(btn)
        elif event.type == pygame.FINGERUP:
            btn = self._finger.pop(event.finger_id, None)
            if btn and btn not in self._finger.values():
                self.held.discard(btn)
        elif event.type == pygame.FINGERMOTION:
            fx, fy = int(event.x * WIDTH), int(event.y * HEIGHT)
            old = self._finger.get(event.finger_id)
            new = self._hit(fx, fy)
            self._finger[event.finger_id] = new
            self.held = {v for v in self._finger.values() if v}
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            btn = self._hit(*event.pos)
            self._mouse_held = btn
            if btn:
                self.held.add(btn)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._mouse_held:
                self.held.discard(self._mouse_held)
            self._mouse_held = None

    # ── inject touch state into a real keys snapshot ──────────────────────────
    def inject(self, real_keys):
        overrides = {self.ctrl[a]: True for a in self.held if a in self.ctrl}
        return _KeysProxy(real_keys, overrides, block_real=True)

    # ── draw buttons on surface ───────────────────────────────────────────────
    def draw(self, surface):
        r = self._BTN_R
        for name, cx, cy in self._layout:
            pressed = name in self.held
            base = self._COLORS.get(name, (100, 100, 100))
            fill = tuple(min(255, c + 60) for c in base) if pressed else base
            alpha = 230 if pressed else 150

            s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*fill, alpha),    (r + 2, r + 2), r)
            pygame.draw.circle(s, (255, 255, 255, 90), (r + 2, r + 2), r, 2)
            surface.blit(s, (cx - r - 2, cy - r - 2))

            lbl = font_tiny.render(self._LABELS.get(name, '?'), True,
                                   (255, 255, 255) if pressed else (200, 200, 200))
            surface.blit(lbl, (cx - lbl.get_width() // 2,
                                cy - lbl.get_height() // 2))

# ---------------------------------------------------------------------------
# Secret menu cheat codes
# ---------------------------------------------------------------------------

CHEAT_CODES = {
    # Starter
    "punch_it":           "Brawler",
    "float_sting":        "Boxer",
    "shadow_step":        "Ninja",
    "fade_out":           "Phantom",
    # Win-based
    "god_of_war":         "Ares",
    "west_wind":          "Zephyr",
    "twenty_wins":        "Unknown",
    "flip_sumo":          "omuS",
    "fifty_wins":         "Impossible",
    # Play-based
    "dance_floor":        "Dancing Man",
    "chaos_roll":         "Ran-Doom",
    "cecalia_secret":     "Cecalia",
    "morph_shift":        "Morph",
    "clean_up":           "Janitor",
    # Win-with
    "titan_fist":         "Titan",
    "tank_armor":         "Tank",
    "rogue_run":          "Rogue",
    "flip_through":       "Acrobat",
    "full_charge":        "Charger",
    "giant_mode":         "Giant",
    "body_slam":          "Wrestler",
    "full_speed":         "Speedster",
    "blood_drain":        "Vampire",
    "sumo_slam":          "Sumo",
    "whip_crack":         "Whipper",
    "vamp_lord_rise":     "Vamp Lord",
    "shapeshift_now":     "Shifter",
    "shrink_ray_go":      "Shrink Ray",
    "stalker_mode":       "Stalker",
    # Beat-char
    "outback_rules":      "Outbacker",
    "gun_show":           "Gunner",
    "bazooka_blast":      "Bazooka Man",
    "pinball_wizard":     "Pinball",
    "hammer_time":        "Hammerhead",
    "nine_tails":         "Kitsune",
    "rip_current":        "Riptide",
    "iron_knuckles":      "Iron Fist",
    # Stage-based
    "castle_siege":       "Mighty Medieval Man",
    "dojo_warrior":       "Samurai",
    "bone_yard":          "Skeleton",
    "arena_fighter":      "Gladiator",
    "spring_loaded":      "Spring",
    "jungle_lord":        "Scarecrow",
    "burn_it_all":        "Arsonist",
    "ice_cold":           "Cryogenisist",
    "big_top_show":       "Magician",
    "no_head_needed":     "Headless Horseman",
    "launch_now":         "Astronaut",
    "wall_swing":         "Spooderman",
    "dream_weave":        "Wizard",
    "lava_walk":          "Lava Man",
    "angel_wings":        "Angel",
    "demon_lord":         "Demon",
    "dark_ritual":        "Dark Mage",
    "sail_away":          "Pirate",
    "stone_gaze":         "Medusa",
    "build_mode":         "The Creator",
    "ink_spill":          "Ink Brush",
    "castle_wall":        "Knight",
    "raise_dead":         "Necromancer",
    "float_high":         "Levitator",
    "pyro_man":           "Pyro",
    # Hard AI
    "hard_as_nails":      "Hardy",
    "ascii_draw":         "ASCII",
    "viking_fury":        "Viking",
    "laser_sight":        "Laser Eyes",
    "crit_hit_go":        "Mr. Crit",
    "go_berserk":         "Enraged",
    # Streaks
    "three_peat":         "Psychopath",
    "spinning_top":       "Whirlpool",
    "phantom_horse":      "Shadowfax",
    "thunder_clap":       "Thunder God",
    # Misc
    "seven_wins":         "Oni",
    "door_slam":          "Bouncer",
    "warp_now":           "Teleporter",
    "harpy_screech":      "Harpy",
    "joker_wild":         "Joker",
    "reel_in":            "Hooker",
    "chop_wood":          "Lumberjack",
    "bee_hive":           "Beekeeper",
    "plague_mask":        "Plague Doctor",
    "full_blitz":         "Blitzer",
    "acid_drop":          "Toxic",
    "time_warp":          "Time Lord",
    "sticky_tape":        "Sticker",
    "snake_hiss":         "Snake",
    "full_hp":            "Medic",
    "haunt_mode":         "Ghost",
    "mime_time":          "Mime",
    "blend_in":           "Chameleon",
    "looking_glass":      "Mirror Man",
    "mouse_run":          "Mouse",
    "self_destruct":      "Kamikaze",
    "glass_jaw":          "Glass Cannon",
    "keep_losing":        "Clown",
    "dizzy_spin":         "Disorientated",
    "change_form":        "Shapeshifter",
    "four_elements":      "Elemental",
    "stone_wings":        "Gargoyle",
    "wail_loud":          "Banshee",
    "lightning_call":     "Storm Caller",
    "pull_force":         "Magnetar",
    "bog_monster":        "Swamp Thing",
    "duel_ready":         "Duelist",
    "polar_plunge":       "Polar Bear",
    "shake_ground":       "Quaker",
    "echo_echo":          "Echo",
    "clone_army":         "Cloned",
    "tick_boom":          "Bomb",
    "half_price":         "Halves",
    "god_killer":         "Godslayer",
    "scroll_power":       "Scrollmaster",
    "rock_solid":         "Boulder",
    "will_o_wisp":        "Wisp",
    "sandstorm":          "Sandman",
    "grim_reaper":        "Reaper",
    "rev_up":             "Chainsaw Man",
    "crushing_blow":      "Crusher",
    "blizzard_mode":      "Storm Witch",
    "blood_lord":         "Blood Baron",
    "drift_away":         "Drifter",
    "dark_warlock":       "Warlock",
    "flash_run":          "Flash",
    "open_portal":        "Portal Maker",
    "apple_drop":         "Gravity",
    "prime_number":       "Prime Time",
    "rage_type":          "Rage Quitter",
    "void_swap":          "Swapper",
    "bruiser_hit":        "Bruiser",
    "grip_tight":         "Grappler",
    "trick_em":           "Trickster",
    "wild_play":          "Wildcard",
    "iron_wall":          "Ironclad",
    "hp_drain":           "Siphon",
    "tick_tock":          "Timekeeper",
    "rainbow_run":        "Rainbow Man",
    "shadow_walk":        "Shade",
    "rot_away":           "Decay",
    "fault_line":         "Fault Line",
    "shield_bash":        "Buckler",
    "overdrive_go":       "Overdrive",
    "hypno_eyes":         "Hypnotist",
    "back_again":         "Revenant",
    "shock_wave":         "Volt",
    "ghost_punch":        "Phantom Strike",
    "mine_field":         "Trap Master",
    "unstoppable":        "Juggernaut",
    "desert_mirage":      "Mirage",
    "dementor_kiss":      "Dementor",
    "charge_orb":         "Orb Shooter",
    "copycat_mode":       "Copycat",
    "bubble_pop":         "Windshield Viper",
    "rainbow_venom":      "Rainbow Snake",
    "suppress_all":       "Inland Taipan",
    "mamba_fast":         "Black Mamba",
    "giant_venom":        "King Cobra",
    "bug_expert":         "Entomologist",
    "system_hack":        "Hacker",
    "pixel_bug":          "8-Bit Wasp",
    "widow_web":          "Black Widow",
    "ai_army":            "AI",
    "shield_auto":        "Forcefield",
    "possess_kick":       "Poltergeist",
    "armor_plated":       "Armor",
    "mirror_shot":        "Deflector",
    "phase_out":          "Unhittable",
    "long_shot":          "Sniper",
    "ghost_mode":         "Mega-Unhittable",
    "change_the_map":     "Map Man",
    "binary_code":        "<|-\\||>+()",
    "still_alive":        "Death Defyer",
    "friday_night":       "Friday the 13th",
    # Secret characters
    "triple_seven":       "777",
    "up_up_down_down":    "Scratch",
    "void_ruler":         "Void Master",
    "high_noon":          "Screentime",
    "all_mighty":         "God",
    "dark_night":         "Nightfall",
    "exact_seven_hp":     "Lucky",
    "totem_power":        "Great Totem Spirit",
    "void_jump":          "Jetpack",
    "chicken_slip":       "ChickenBanana",
    "soul_collector":     "Soul Master",
    "the_one_true":       "The One",
    "reflection":         "Mirror",
    "portal_paradox":     "Paradox",
    "cobra_spit":         "Spitting Cobra",
    "pac_dots":           "Pacman",
    "scorpio_rise":       "Scorpio",
    "nuke_launch":        "Nuke",
    "druid_grove":        "Druid",
    "crits_only":         "Big Bad Critter Clad",
    "the_answer":         "Life the Universe Everything",
    "cactus_desert":      "Cactus",
    # 11 new characters
    "play_notes":         "Bard",
    "meat_cleaver":       "Butcher",
    "immovable":          "Stone Cold",
    "money_money":        "Tycoon",
    "glass_face":         "Glass Jaw",
    "drain_life":         "Life Drain",
    "lance_charge":       "Lancer",
    "sponge_mode":        "Absorber",
    "dark_curse":         "Hexer",
    "double_or_nothing":  "Gambler",
    "mirror_punch":       "Counter",
    "fire_ring":          "Blazer",
    "big_guy":            "Colossus",
    "ground_pound":       "Stomper",
    "quill_spike":        "Porcupine",
    "drop_anchor":        "Anchor",
    "night_night":        "Sleeper",
    "rage_mode":          "Rager",
    "double_tap":         "Twin",
    "drain_away":         "Sapper",
    "copy_stats":         "Mimic",
    # new characters
    "throw_rang":         "Boomerang",
    "parry_now":          "Parry",
    "heal_up":            "Healer",
    "iron_fortress":      "Iron Wall",
    "kick_through":       "Pierce",
    "stack_rage":         "Rage Stack",
    "rise_again":         "Phoenix",
    "three_chain":        "Chain Fighter",
    "break_guard":        "Breaker",
    "grip_tight_titan":   "Titan Grip",
    # secret
    "max_everything":     "Overload",
    "system_glitch":      "Glitch",
    "mirror_damage":      "Reflect",
    "one_hit_ko":         "One Punch",
    "last_second":        "Nick of Time",
    "get_big":            "Buffer",
    "be_cursed":          "Cursed",
}

# ---------------------------------------------------------------------------
# Stage select screen
# ---------------------------------------------------------------------------

def stage_select():
    idx = 0
    _map_man_flag[0] = False
    _start_ticks = pygame.time.get_ticks()

    # Touch nav button rects
    _r_left    = pygame.Rect(0,   0, 120, HEIGHT)
    _r_right   = pygame.Rect(WIDTH - 120, 0, 120, HEIGHT)
    _r_confirm = pygame.Rect(WIDTH//2 - 70, HEIGHT - 68, 140, 50)

    def _touch_pos(event):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION):
            return int(event.x * WIDTH), int(event.y * HEIGHT)
        return event.pos

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT,  pygame.K_a): idx = (idx - 1) % len(STAGES)
                if event.key in (pygame.K_RIGHT, pygame.K_d): idx = (idx + 1) % len(STAGES)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE): return idx
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = _touch_pos(event) if event.type == pygame.FINGERDOWN else event.pos
                if _r_confirm.collidepoint(pos): return idx
                if _r_left.collidepoint(pos):    idx = (idx - 1) % len(STAGES)
                if _r_right.collidepoint(pos):   idx = (idx + 1) % len(STAGES)
        if not _map_man_flag[0] and pygame.time.get_ticks() - _start_ticks >= 30000:
            _map_man_flag[0] = True

        draw_bg(screen, idx)
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 120))
        screen.blit(ov, (0, 0))

        title = font_large.render("SELECT STAGE", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        nm = font_medium.render(STAGES[idx]["name"], True, WHITE)
        screen.blit(nm, (WIDTH//2 - nm.get_width()//2, HEIGHT//2 - 30))

        match = STAGE_MATCHUPS.get(STAGES[idx]["name"], {})
        if match:
            adv_s = font_small.render(f"★ ADV: {match['adv']}", True, (100, 255, 100))
            dis_s = font_small.render(f"✗ DIS: {match['dis']}", True, (255, 100, 100))
            screen.blit(adv_s, (WIDTH//2 - adv_s.get_width() - 12, HEIGHT//2 + 12))
            screen.blit(dis_s, (WIDTH//2 + 12, HEIGHT//2 + 12))

        for di in range(len(STAGES)):
            col = WHITE if di == idx else GRAY
            pygame.draw.circle(screen, col, (WIDTH//2 + (di - len(STAGES)//2)*30, HEIGHT//2 + 40), 6)

        # Touch nav arrows
        for _arr, _txt, _rx in (('◄', '◄', 20), ('►', '►', WIDTH - 50)):
            _as = font_large.render(_txt, True, (200, 200, 200))
            screen.blit(_as, (_rx, HEIGHT // 2 - _as.get_height() // 2))
        pygame.draw.rect(screen, (60, 120, 60), _r_confirm, border_radius=10)
        pygame.draw.rect(screen, (120, 220, 120), _r_confirm, 2, border_radius=10)
        _gs = font_medium.render("GO", True, WHITE)
        screen.blit(_gs, (_r_confirm.centerx - _gs.get_width() // 2,
                          _r_confirm.centery - _gs.get_height() // 2))

        hint = font_small.render("◄ ► to browse   ENTER / tap GO to confirm", True, (180, 180, 180))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))
        pygame.display.flip()


# ---------------------------------------------------------------------------
# Mode select screen
# ---------------------------------------------------------------------------

def mode_select():
    """Returns ('1p', difficulty), '2p', 'survival_1p', 'survival_2p', or 'online'."""
    selected = 0   # 0=1P, 1=2P, 2=SURVIVAL, 3=ONLINE
    difficulty_idx = 1
    difficulties = ['easy', 'medium', 'hard', 'super_hard', 'super_super_hard', 'mega_hard']
    diff_colors  = [GREEN, YELLOW, RED, PURPLE, CYAN, ORANGE]
    scroll_offset = 0
    VISIBLE = 3
    survival_players = 0   # 0=1P survival, 1=2P survival
    preview_t = 0.0

    # 4 cards layout
    card_w, card_h = 155, 240
    GAP   = 8
    START = WIDTH // 2 - (4 * card_w + 3 * GAP) // 2
    card_xs = [START + i * (card_w + GAP) for i in range(4)]

    _type42_buf = ""
    _secret_seq = "all_the_secrets_of_the_world"
    _secret_buf = ""
    _confirm_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 52, 160, 44)

    def _mode_confirm():
        if selected == 0:   return ('1p', difficulties[difficulty_idx])
        elif selected == 1: return '2p'
        elif selected == 2: return 'survival_2p' if survival_players else 'survival_1p'
        else:               return 'online'

    while True:
        clock.tick(FPS)
        preview_t = (preview_t + 0.02) % 1.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Touch / click: tap a card to select it; tap confirm to enter
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                _mp = (int(event.x * WIDTH), int(event.y * HEIGHT)) if event.type == pygame.FINGERDOWN else event.pos
                if _confirm_rect.collidepoint(_mp):
                    return _mode_confirm()
                for _ci, _cx in enumerate(card_xs):
                    if pygame.Rect(_cx, 140, card_w, card_h).collidepoint(_mp):
                        selected = _ci
                        break
                # Difficulty ▲/▼ touch (drawn at list_x, list_y area)
                if selected == 0:
                    _lx, _ly = card_xs[0] + 10, 428
                    if pygame.Rect(_lx, _ly - 26, 60, 22).collidepoint(_mp):
                        difficulty_idx = (difficulty_idx - 1) % len(difficulties)
                    if pygame.Rect(_lx, _ly + VISIBLE * 30 + 2, 60, 22).collidepoint(_mp):
                        difficulty_idx = (difficulty_idx + 1) % len(difficulties)
                if selected == 2:
                    _lx2 = card_xs[2] + 8
                    for _oi in range(2):
                        if pygame.Rect(_lx2, 405 + _oi * 30, 120, 26).collidepoint(_mp):
                            survival_players = _oi
                # Touch device toggles
                _tr2 = pygame.Rect(8 + 62, HEIGHT - 54, 74, 22)
                if _tr2.collidepoint(_mp):
                    touch_p1_enabled[0] = not touch_p1_enabled[0]
                    touch_p2_enabled[0] = touch_p1_enabled[0]
            if event.type == pygame.KEYDOWN:
                # Track "42" typed anywhere on main menu
                if hasattr(event, 'unicode') and event.unicode in ('4', '2'):
                    _type42_buf += event.unicode
                    if _type42_buf.endswith('42'):
                        _type42_typed[0] = True
                        _type42_buf = ""
                elif hasattr(event, 'unicode') and event.unicode:
                    _type42_buf = ""
                # Secret menu sequence detection
                if hasattr(event, 'unicode') and event.unicode:
                    _secret_buf += event.unicode.lower()
                    if _secret_seq in _secret_buf:
                        return 'secret_menu'
                    if len(_secret_buf) > len(_secret_seq) + 5:
                        _secret_buf = _secret_buf[-len(_secret_seq):]
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % 4
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % 4
                if selected == 0:   # 1P: difficulty picker
                    if event.key in (pygame.K_UP, pygame.K_w):
                        difficulty_idx = (difficulty_idx - 1) % len(difficulties)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        difficulty_idx = (difficulty_idx + 1) % len(difficulties)
                    if difficulty_idx < scroll_offset:
                        scroll_offset = difficulty_idx
                    elif difficulty_idx >= scroll_offset + VISIBLE:
                        scroll_offset = difficulty_idx - VISIBLE + 1
                if selected == 2:   # Survival: toggle 1P/2P
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                        survival_players = 1 - survival_players
                if event.key == pygame.K_t:
                    touch_p1_enabled[0] = not touch_p1_enabled[0]
                    touch_p2_enabled[0] = touch_p1_enabled[0]
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected == 0:
                        return ('1p', difficulties[difficulty_idx])
                    elif selected == 1:
                        return '2p'
                    elif selected == 2:
                        return 'survival_2p' if survival_players else 'survival_1p'
                    else:
                        return 'online'

        screen.fill(DARK)
        title = font_large.render("STICKMAN FIGHTER", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        cards = [
            (card_xs[0], "1 PLAYER",  "vs CPU",    BLUE),
            (card_xs[1], "2 PLAYERS", "local",      ORANGE),
            (card_xs[2], "SURVIVAL",  "endless",    GREEN),
            (card_xs[3], "ONLINE",    "internet",   CYAN),
        ]
        for ci, (cx, top, sub, col) in enumerate(cards):
            border = WHITE if ci == selected else GRAY
            pygame.draw.rect(screen, (50,50,50), (cx, 140, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, border,     (cx, 140, card_w, card_h), 3, border_radius=12)
            lbl = font_medium.render(top, True, col)
            screen.blit(lbl, (cx + card_w//2 - lbl.get_width()//2, 150))
            sl = font_small.render(sub, True, GRAY)
            screen.blit(sl, (cx + card_w//2 - sl.get_width()//2, 190))
            draw_stickman(screen, cx + card_w//2 - 25, 140 + card_h - 30, BLUE, 1, 'walk', preview_t)
            draw_stickman(screen, cx + card_w//2 + 25, 140 + card_h - 30, RED, -1, 'idle', 0.0)
            if ci == selected:
                sel_txt = font_tiny.render("ENTER / SPACE to select", True, WHITE)
                screen.blit(sel_txt, (cx + card_w//2 - sel_txt.get_width()//2, 390))

        # Difficulty picker (1P mode)
        if selected == 0:
            diff_lbl = font_small.render("Difficulty:", True, WHITE)
            screen.blit(diff_lbl, (card_xs[0], 400))
            list_x, list_y, row_h = card_xs[0] + 10, 428, 30
            if scroll_offset > 0:
                screen.blit(font_small.render("▲", True, GRAY), (list_x, list_y - 22))
            for row, di in enumerate(range(scroll_offset, scroll_offset + VISIBLE)):
                if di >= len(difficulties): break
                dname, dcol = difficulties[di], diff_colors[di]
                marker = "► " if di == difficulty_idx else "  "
                dt = font_small.render(f"{marker}{dname.replace('_', ' ').capitalize()}", True,
                                       dcol if di == difficulty_idx else GRAY)
                screen.blit(dt, (list_x, list_y + row * row_h))
            if scroll_offset + VISIBLE < len(difficulties):
                screen.blit(font_small.render("▼", True, GRAY), (list_x, list_y + VISIBLE * row_h + 2))
            screen.blit(font_tiny.render("↑/↓ or W/S to scroll", True, GRAY),
                        (list_x, list_y + VISIBLE * row_h + 22))

        # Survival 1P/2P toggle
        if selected == 2:
            opts = ["1 PLAYER", "2 PLAYERS"]
            for oi, opt in enumerate(opts):
                col = WHITE if oi == survival_players else GRAY
                ot = font_small.render(("► " if oi == survival_players else "  ") + opt, True, col)
                screen.blit(ot, (card_xs[2] + 8, 405 + oi * 30))
            screen.blit(font_tiny.render("W/S to switch", True, GRAY), (card_xs[2] + 8, 468))

        nav = font_tiny.render("◄ ► to switch mode", True, GRAY)
        screen.blit(nav, (WIDTH//2 - nav.get_width()//2, HEIGHT - 24))
        # Single input mode toggle — bottom left (T to switch)
        _tl = font_tiny.render("Input [T]:", True, GRAY)
        screen.blit(_tl, (8, HEIGHT - 52))
        _tr = pygame.Rect(8 + 62, HEIGHT - 54, 74, 22)
        _ton = touch_p1_enabled[0]
        _mode_lbl = "Buttons" if _ton else "Keyboard"
        _bg  = (40, 100, 180) if _ton else (80, 60, 20)
        _brd = (100, 180, 255) if _ton else (200, 160, 60)
        pygame.draw.rect(screen, _bg,  _tr, border_radius=6)
        pygame.draw.rect(screen, _brd, _tr, 1, border_radius=6)
        _tt = font_tiny.render(_mode_lbl, True, WHITE)
        screen.blit(_tt, (_tr.centerx - _tt.get_width()//2, _tr.centery - _tt.get_height()//2))
        # Touch confirm button
        pygame.draw.rect(screen, (60, 120, 60), _confirm_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 220, 120), _confirm_rect, 2, border_radius=10)
        _ps = font_medium.render("PLAY", True, WHITE)
        screen.blit(_ps, (_confirm_rect.centerx - _ps.get_width() // 2,
                          _confirm_rect.centery - _ps.get_height() // 2))
        pygame.display.flip()

# ---------------------------------------------------------------------------
# Character select screen
# ---------------------------------------------------------------------------

def character_select(vs_ai=False, unlocked=None, unlock_hints=None, unlock_progress=None):
    """Returns (p1_idx, p2_idx). P2 is random if vs_ai."""
    if unlocked is None:
        unlocked = {ch["name"] for ch in CHARACTERS}
    if unlock_hints is None:
        unlock_hints = {}
    if unlock_progress is None:
        unlock_progress = {}
    n     = len(CHARACTERS)
    COLS  = 7
    ROWS  = (n + COLS - 1) // COLS

    # Grid occupies left ~60% of screen
    GX, GY   = 8,  68
    GW, GH   = 540, HEIGHT - GY - 28
    CW       = GW // COLS
    CH       = GH // ROWS

    # Detail panel on the right
    PX       = GX + GW + 10
    PW       = WIDTH - PX - 8
    PY, PH   = GY, GH

    def move(idx, dr, dc):
        r, c = divmod(idx, COLS)
        if dc:
            c = (c + dc) % COLS
            ni = r * COLS + c
            return min(ni, n - 1)
        else:
            r = (r + dr) % ROWS
            ni = r * COLS + c
            return min(ni, n - 1)

    p1_idx, p2_idx = 0, 1
    p1_ready = False
    p2_ready = vs_ai
    preview_t = 0.0
    flash_t   = 0   # for ready flash

    while True:
        clock.tick(FPS)
        preview_t = (preview_t + 0.02) % 1.0
        flash_t   = (flash_t + 1) % 40

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Touch / click: tap a character cell to select, tap READY to confirm
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                _tp = (int(event.x * WIDTH), int(event.y * HEIGHT)) if event.type == pygame.FINGERDOWN else event.pos
                _tx, _ty = _tp
                # Tap inside the character grid
                if GX <= _tx < GX + GW and GY <= _ty < GY + GH:
                    _col = (_tx - GX) // CW
                    _row = (_ty - GY) // CH
                    _ni  = min(_row * COLS + _col, n - 1)
                    if not p1_ready:
                        p1_idx = _ni
                    elif not vs_ai and not p2_ready:
                        p2_idx = _ni
                # Tap READY button (drawn at bottom-right of detail panel)
                _ready_rect = pygame.Rect(PX, PY + PH - 52, PW, 44)
                if _ready_rect.collidepoint(_tp):
                    if not p1_ready:
                        if CHARACTERS[p1_idx]["name"] in unlocked:
                            p1_ready = True
                            if vs_ai:
                                _ul = [i for i, c in enumerate(CHARACTERS) if c["name"] in unlocked]
                                p2_idx = random.choice(_ul) if _ul else random.randint(0, n - 1)
                    elif not vs_ai and not p2_ready:
                        if CHARACTERS[p2_idx]["name"] in unlocked:
                            p2_ready = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None
                # P1 navigation (WASD or arrows while P1 not ready)
                if not p1_ready:
                    if event.key in (pygame.K_a, pygame.K_LEFT):  p1_idx = move(p1_idx, 0, -1)
                    if event.key in (pygame.K_d, pygame.K_RIGHT): p1_idx = move(p1_idx, 0,  1)
                    if event.key in (pygame.K_w, pygame.K_UP):    p1_idx = move(p1_idx, -1, 0)
                    if event.key in (pygame.K_s, pygame.K_DOWN):  p1_idx = move(p1_idx,  1, 0)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
                        if CHARACTERS[p1_idx]["name"] not in unlocked:
                            pass  # locked — do nothing
                        else:
                            p1_ready = True
                            if vs_ai:
                                _ul = [i for i, c in enumerate(CHARACTERS) if c["name"] in unlocked]
                                p2_idx = random.choice(_ul) if _ul else random.randint(0, n - 1)
                # P2 navigation (arrows only, after P1 locked in)
                elif not vs_ai and not p2_ready:
                    if event.key == pygame.K_LEFT:  p2_idx = move(p2_idx, 0, -1)
                    if event.key == pygame.K_RIGHT: p2_idx = move(p2_idx, 0,  1)
                    if event.key == pygame.K_UP:    p2_idx = move(p2_idx, -1, 0)
                    if event.key == pygame.K_DOWN:  p2_idx = move(p2_idx,  1, 0)
                    if event.key in (pygame.K_RETURN, pygame.K_k):
                        if CHARACTERS[p2_idx]["name"] in unlocked:
                            p2_ready = True

        if p1_ready and p2_ready:
            return p1_idx, p2_idx

        # Whose detail to show: the active picker
        detail_idx = p2_idx if (p1_ready and not p2_ready) else p1_idx
        detail_ch  = CHARACTERS[detail_idx]
        active_col = ORANGE if (p1_ready and not p2_ready) else BLUE

        # ── Background ──────────────────────────────────────────────────────
        screen.fill((18, 18, 28))

        # Title bar
        pygame.draw.rect(screen, (30, 30, 48), (0, 0, WIDTH, GY - 2))
        title = font_medium.render("SELECT YOUR FIGHTER", True, YELLOW)
        screen.blit(title, (GX, 10))
        if not vs_ai:
            phase = "P1 choosing" if not p1_ready else "P2 choosing"
            phase_col = BLUE if not p1_ready else ORANGE
            ps = font_small.render(phase, True, phase_col)
            screen.blit(ps, (WIDTH - ps.get_width() - 10, 12))

        # ── Character grid ───────────────────────────────────────────────────
        for i, ch in enumerate(CHARACTERS):
            r, c    = divmod(i, COLS)
            cx      = GX + c * CW
            cy      = GY + r * CH
            color   = ch["color"]
            is_locked = ch["name"] not in unlocked

            # Tinted background from character color (very dark if locked)
            if is_locked:
                bg_col = (14, 14, 18)
            else:
                bg_col = (max(10, color[0]//5), max(10, color[1]//5), max(10, color[2]//5))
            pygame.draw.rect(screen, bg_col, (cx+2, cy+2, CW-4, CH-4), border_radius=6)

            # Selection highlights
            is_p1 = (i == p1_idx)
            is_p2 = (i == p2_idx) and not vs_ai

            if is_p1 and is_p2:
                bord, bw = (180, 100, 255), 3
            elif is_p1:
                bord, bw = BLUE,   3
            elif is_p2:
                bord, bw = ORANGE, 3
            else:
                bord, bw = (55, 55, 70), 1
            pygame.draw.rect(screen, bord, (cx+2, cy+2, CW-4, CH-4), bw, border_radius=6)

            # Character name or lock indicator
            if is_locked:
                nm = font_tiny.render("???", True, (70, 70, 80))
                # small padlock lines
                lx, ly = cx + CW//2, cy + CH//2 - 6
                pygame.draw.rect(screen, (70, 70, 80), (lx - 5, ly + 4, 10, 8), border_radius=2)
                pygame.draw.arc(screen, (70, 70, 80), (lx - 4, ly - 4, 8, 10),
                                math.pi * 0.1, math.pi * 0.9, 2)
            else:
                name_str = ch["name"] if len(ch["name"]) <= 10 else ch["name"][:9] + "."
                nm = font_tiny.render(name_str, True, color if (is_p1 or is_p2) else (160, 160, 160))
            screen.blit(nm, (cx + CW//2 - nm.get_width()//2, cy + CH//2 - 6))

            # Ready badge
            if is_p1 and p1_ready:
                pygame.draw.circle(screen, GREEN, (cx + CW - 8, cy + 8), 5)
            if is_p2 and p2_ready:
                pygame.draw.circle(screen, GREEN, (cx + 8, cy + 8), 5)

            # Player cursor dot(s)
            if is_p1 and not p1_ready:
                pygame.draw.circle(screen, BLUE, (cx + CW - 8, cy + 8), 4)
            if is_p2 and not p2_ready:
                pygame.draw.circle(screen, ORANGE, (cx + 8, cy + 8), 4)

        # Grid border
        pygame.draw.rect(screen, (60, 60, 90), (GX, GY, GW, GH), 1, border_radius=4)

        # ── Detail panel ─────────────────────────────────────────────────────
        detail_locked = detail_ch["name"] not in unlocked
        pygame.draw.rect(screen, (25, 25, 40),    (PX, PY, PW, PH), border_radius=10)
        pygame.draw.rect(screen, active_col,      (PX, PY, PW, PH), 2, border_radius=10)

        if detail_locked:
            # Show locked placeholder
            lbl = font_medium.render("???", True, (80, 80, 100))
            screen.blit(lbl, (PX + PW//2 - lbl.get_width()//2, PY + 8))
            msg = font_small.render("LOCKED", True, (180, 60, 60))
            screen.blit(msg, (PX + PW//2 - msg.get_width()//2, PY + PH//2 - 30))
            cond_text = unlock_hints.get(detail_ch["name"], "???")
            hint2 = font_tiny.render(cond_text, True, YELLOW)
            screen.blit(hint2, (PX + PW//2 - hint2.get_width()//2, PY + PH//2 + 5))
            # Progress bar (only for non-secret chars)
            if detail_ch["name"] in unlock_progress:
                cur, total = unlock_progress[detail_ch["name"]]
                pct = cur / total if total else 0
                bw = PW - 48
                bx = PX + 24
                by = PY + PH//2 + 28
                bh = 10
                pygame.draw.rect(screen, (40, 40, 60),  (bx, by, bw, bh), border_radius=5)
                if pct > 0:
                    fill_col = (
                        (80, 220, 80)  if pct >= 0.75 else
                        (220, 200, 60) if pct >= 0.40 else
                        (220, 90, 60)
                    )
                    pygame.draw.rect(screen, fill_col,
                                     (bx, by, int(bw * pct), bh), border_radius=5)
                pygame.draw.rect(screen, (120, 120, 160), (bx, by, bw, bh), 1, border_radius=5)
                prog_lbl = font_tiny.render(f"{cur}/{total}", True, (200, 200, 200))
                screen.blit(prog_lbl, (PX + PW//2 - prog_lbl.get_width()//2, by + bh + 3))
            # Draw a big padlock shape
            lkcx, lkcy = PX + PW//2, PY + PH//2 - 80
            pygame.draw.rect(screen, (80, 80, 100), (lkcx - 22, lkcy + 8, 44, 34), border_radius=5)
            pygame.draw.arc(screen, (80, 80, 100), (lkcx - 18, lkcy - 22, 36, 40),
                            math.pi * 0.05, math.pi * 0.95, 5)
        else:
            # Large animated stickman
            sm_y = PY + 155
            draw_stickman(screen, PX + PW//2, sm_y, detail_ch["color"], 1, 'walk', preview_t, scale=1.15,
                          char_name=detail_ch["name"])

            # Character name
            nm_big = font_medium.render(detail_ch["name"], True, detail_ch["color"])
            screen.blit(nm_big, (PX + PW//2 - nm_big.get_width()//2, PY + 8))

        if not detail_locked:
            # Description (word-wrap)
            words, line, desc_lines = detail_ch["desc"].split(), "", []
            for w in words:
                test = (line + " " + w).strip()
                if font_tiny.size(test)[0] > PW - 16:
                    desc_lines.append(line); line = w
                else:
                    line = test
            if line: desc_lines.append(line)
            for li, dl in enumerate(desc_lines):
                ds = font_tiny.render(dl, True, YELLOW)
                screen.blit(ds, (PX + PW//2 - ds.get_width()//2, PY + 34 + li * 15))

            # Stat bars
            bar_x  = PX + 10
            bar_y  = PY + 172
            bar_bw = PW - 20
            bar_h  = 14
            bar_gap = 23
            for si, (lbl, val, mx, col) in enumerate([
                ("HP",    detail_ch["max_hp"],              400, (60,  210,  80)),
                ("SPD",   detail_ch["speed"],                10, (80,  170, 255)),
                ("PUNCH", detail_ch["punch_dmg"],            30, (255, 120,  50)),
                ("KICK",  detail_ch["kick_dmg"],             30, (255,  60, 180)),
                ("BLOCK", detail_ch.get("block", 5),         10, (200, 200,  60)),
            ]):
                by  = bar_y + si * bar_gap
                lbs = font_tiny.render(lbl, True, (180, 180, 180))
                screen.blit(lbs, (bar_x, by))
                bx2 = bar_x + 48
                bw2 = bar_bw - 48
                pygame.draw.rect(screen, (50, 50, 65), (bx2, by, bw2, bar_h), border_radius=3)
                fw  = int(bw2 * min(1.0, val / mx))
                if fw > 0:
                    pygame.draw.rect(screen, col, (bx2, by, fw, bar_h), border_radius=3)
                pygame.draw.rect(screen, (90, 90, 110), (bx2, by, bw2, bar_h), 1, border_radius=3)
                vs2 = font_tiny.render(str(val), True, WHITE)
                screen.blit(vs2, (bx2 + bw2 + 5, by))

            # Badges row
            badge_y = bar_y + 5 * bar_gap + 6
            badges  = []
            if detail_ch.get("double_jump"):    badges.append(("2x JUMP",      CYAN))
            if detail_ch.get("giant"):          badges.append(("GIANT",         GREEN))
            if detail_ch.get("tiny"):           badges.append(("TINY",          (220, 200, 180)))
            if detail_ch.get("phase"):          badges.append(("PHASES WALLS",  (200, 200, 255)))
            if detail_ch.get("vampire"):        badges.append(("VAMPIRE",       (200, 0, 80)))
            if detail_ch.get("anti_gravity"):   badges.append(("ANTI-GRAVITY",  (180, 220, 255)))
            if detail_ch.get("wall_cling"):     badges.append(("WALL CLING",    ORANGE))
            if detail_ch.get("regen"):          badges.append(("REGEN",         (120, 255, 120)))
            if detail_ch.get("fire_punch"):     badges.append(("FIRE PUNCH",    (255, 100, 20)))
            if detail_ch.get("freeze_kick"):    badges.append(("FREEZE KICK",   (120, 200, 255)))
            if detail_ch.get("shock_punch"):    badges.append(("SHOCK PUNCH",   YELLOW))
            if detail_ch.get("magnet"):         badges.append(("MAGNET",        PURPLE))
            if detail_ch.get("teleport_kick"):  badges.append(("TELEPORT KICK", (220, 80, 255)))
            if detail_ch.get("random_stats"):   badges.append(("RANDOM STATS",  GRAY))
            if detail_ch.get("shoot_kick"):     badges.append(("SHOOTS BALLS",  (60, 200, 80)))
            if detail_ch.get("bazooka_kick"):   badges.append(("BAZOOKA",       (220, 60, 60)))
            if detail_ch.get("bounce_kick"):    badges.append(("BOUNCE BALL",   (255, 80, 200)))
            if detail_ch.get("size_kick"):      badges.append(("SIZE SHIFT",    (80, 200, 220)))
            if detail_ch.get("grapple_kick"):   badges.append(("SNAKE HOOK",    (40, 200, 60)))
            if detail_ch.get("pumpkin_kick"):   badges.append(("PUMPKIN BOMB",  (215, 118, 0)))
            if detail_ch.get("contact_dmg"):    badges.append(("POISON TOUCH",  (100, 220, 60)))
            if detail_ch.get("hammer_punch"):   badges.append(("HAMMER SMASH",  (160, 120, 60)))
            if detail_ch.get("berserker"):      badges.append(("BERSERKER",      (220, 60, 30)))
            if detail_ch.get("bounce_punch"):   badges.append(("MAGIC ORB",      (160, 80, 255)))
            if detail_ch.get("slam_kick"):      badges.append(("SLAM KICK",      (220, 100, 40)))
            if detail_ch.get("confuse_kick"):   badges.append(("CONFUSE KICK",   (255, 60, 120)))
            if detail_ch.get("speedster"):      badges.append(("SPEED TRAIL",    (255, 220, 0)))
            if detail_ch.get("slow_fall"):      badges.append(("SLOW FALL",      (255, 240, 180)))
            if detail_ch.get("stealth_punch"):  badges.append(("STEALTH",        (200, 200, 220)))
            if detail_ch.get("wide_punch"):     badges.append(("WIDE REACH",     (160, 80, 30)))
            if detail_ch.get("reflect_block"):  badges.append(("REFLECT",        (80, 200, 80)))
            if detail_ch.get("laser_eyes"):     badges.append(("LASER EYES",     (255, 60,  0)))
            if detail_ch.get("whip_punch"):     badges.append(("WHIP",           (160, 90, 20)))
            if detail_ch.get("always_crit"):    badges.append(("ALWAYS CRIT",    (255, 215, 0)))
            if detail_ch.get("chameleon"):      badges.append(("CAMOUFLAGE",     (60, 180, 80)))
            if detail_ch.get("ink_kick"):       badges.append(("INK CLONE",      (20,  20, 40)))
            if detail_ch.get("ghost_float"):    badges.append(("GHOST FLOAT",    (210, 210, 255)))
            # new characters
            if detail_ch.get("kitsune_barrage"): badges.append(("九 BARRAGE",    (255, 160,  0)))
            if detail_ch.get("freeze_laser"):    badges.append(("FREEZE GAZE",   (0,  210, 255)))
            if detail_ch.get("creator_kick"):    badges.append(("CREATES WALLS", (220, 180, 40)))
            if detail_ch.get("disorientated"):   badges.append(("ALL REVERSED",  (200,  80, 255)))
            if detail_ch.get("immune"):          badges.append(("STATUS IMMUNE", (210, 210, 180)))
            if detail_ch.get("water_kick"):      badges.append(("WATER BALL",    (0,  180, 240)))
            if detail_ch.get("momentum"):        badges.append(("MOMENTUM",      (0,  160, 220)))
            if detail_ch.get("smoke_trail"):     badges.append(("SMOKE TRAIL",   (180, 180, 220)))
            if detail_ch.get("snake"):           badges.append(("SNAKE BODY",    (20, 200, 60)))
            if detail_ch.get("always_berserk"):  badges.append(("ALWAYS ENRAGED",(220, 50,  0)))
            if detail_ch.get("bee_punch"):       badges.append(("BEE SWARM",     (220,180,  0)))
            if detail_ch.get("plague_punch"):    badges.append(("PLAGUE",        (120,200, 80)))
            if detail_ch.get("undead"):          badges.append(("REVIVES ONCE",  (80,  40,120)))
            if detail_ch.get("chaos_timer"):     badges.append(("CHAOS MAGIC",   (200, 80,255)))
            if detail_ch.get("rapid_fire"):      badges.append(("RAPID PUNCH",   (255,160,  0)))
            if detail_ch.get("drain_kick"):      badges.append(("DRAIN KICK",    (160,  0,160)))
            if detail_ch.get("iron_fist"):       badges.append(("IRON FIST",     (180,180,200)))
            if detail_ch.get("toxic_aura"):      badges.append(("TOXIC AURA",    (60, 220, 60)))
            if detail_ch.get("time_freeze"):     badges.append(("TIME FREEZE",   (100,180,255)))
            if detail_ch.get("cycle_attack"):    badges.append(("CYCLE ATTACK",  (160,120,255)))
            if detail_ch.get("explode_death"):   badges.append(("DEATH EXPLODE", (255,100,  0)))
            if detail_ch.get("shrink_kick"):     badges.append(("SHRINK KICK",   (120,255,200)))
            if detail_ch.get("launch_kick"):     badges.append(("LAUNCH KICK",   (200,160,255)))
            if detail_ch.get("speed_steal"):     badges.append(("SPEED STEAL",   ( 60, 80, 60)))
            if detail_ch.get("reflect_proj"):    badges.append(("REFLECT PROJ",  (200,220,240)))
            if detail_ch.get("auto_fire"):       badges.append(("AUTO FIRE",     (255, 80,  0)))
            if detail_ch.get("thunder_punch"):   badges.append(("THUNDER",       (255,240, 80)))
            if detail_ch.get("auto_teleport"):   badges.append(("AUTO TELEPORT", ( 80,200,220)))
            if detail_ch.get("sticky_punch"):    badges.append(("STICKY PUNCH",  (200,180, 60)))
            # --- batch: missing mechanics ---
            if detail_ch.get("shock_kick"):      badges.append(("SHOCK KICK",    (255,240, 80)))
            if detail_ch.get("storm_punch"):     badges.append(("STORM PUNCH",   ( 80,120,255)))
            if detail_ch.get("magnet_punch"):    badges.append(("MAGNET PULL",   (160, 80,255)))
            if detail_ch.get("combo_punch"):     badges.append(("COMBO PUNCH",   ( 80,200,180)))
            if detail_ch.get("steal_kick"):      badges.append(("STEAL KICK",    ( 60, 60,100)))
            if detail_ch.get("cloned"):          badges.append(("CLONE",         (100,200,160)))
            if detail_ch.get("bomb_character"):  badges.append(("BOMB SPAWNER",  (200, 80, 20)))
            if detail_ch.get("halves_punch"):    badges.append(("HALVES HP",     (220, 80,220)))
            if detail_ch.get("godslayer"):       badges.append(("GODSLAYER",     (180, 20, 60)))
            if detail_ch.get("scroll_kick"):     badges.append(("SCROLL BOMB",   (180,150, 80)))
            if detail_ch.get("flash_kick"):      badges.append(("FLASH KICK",    (255,200,  0)))
            if detail_ch.get("portal_kick"):     badges.append(("PORTAL KICK",   ( 80,200,255)))
            if detail_ch.get("apple_kick"):      badges.append(("APPLE RAIN",    (120, 80,200)))
            if detail_ch.get("totem_kick"):      badges.append(("TOTEM RAIN",    (190,110, 30)))
            if detail_ch.get("remote_kick"):     badges.append(("REMOTE BOMB",   (220, 40,  0)))
            if detail_ch.get("prime_dmg"):       badges.append(("PRIME DAMAGE",  ( 60,180,255)))
            if detail_ch.get("lucky_strike"):    badges.append(("LUCKY STRIKE",  (255,215,  0)))
            if detail_ch.get("drain_punch"):     badges.append(("DRAIN PUNCH",   ( 20,  0, 60)))
            if detail_ch.get("sleep_punch"):     badges.append(("SLEEP PUNCH",   (220,190,120)))
            if detail_ch.get("reaper_kick"):     badges.append(("REAPER KICK",   ( 40, 40, 40)))
            if detail_ch.get("chainsaw"):        badges.append(("CHAINSAW",      (200, 60, 30)))
            if detail_ch.get("crush_punch"):     badges.append(("BLOCK BREAK",   (140, 80,200)))
            if detail_ch.get("quake_land"):      badges.append(("QUAKE LAND",    (160,120, 60)))
            if detail_ch.get("seven_punch"):     badges.append(("777 PUNCH",     (255,215,  0)))
            if detail_ch.get("void_immune"):     badges.append(("VOID IMMUNE",   ( 30,  0, 60)))
            if detail_ch.get("screentime"):      badges.append(("TIME WARP",     (100,200,255)))
            # --- new characters batch ---
            if detail_ch.get("swap_kick"):       badges.append(("SWAP KICK",     (200,120, 60)))
            if detail_ch.get("rage_build"):      badges.append(("RAGE BUILD",    (180, 60, 60)))
            if detail_ch.get("grab_punch"):      badges.append(("GRAB PUNCH",    ( 80,140,200)))
            if detail_ch.get("confuse_punch"):   badges.append(("CONFUSE PUNCH", (200, 80,200)))
            if detail_ch.get("wild_attack"):     badges.append(("WILD ATTACK",   (255,180,  0)))
            if detail_ch.get("stone_skin"):      badges.append(("ARMOR SKIN",    (150,150,170)))
            if detail_ch.get("siphon_leech"):    badges.append(("SIPHON",        (160, 40,160)))
            if detail_ch.get("slow_punch"):      badges.append(("SLOW PUNCH",    (100,200,240)))
            if detail_ch.get("copy_punch"):      badges.append(("COPY PUNCH",    (180,230,255)))
            if detail_ch.get("hp_swap"):         badges.append(("HP SWAP",       ( 80, 40,200)))
            if detail_ch.get("rainbow_poop"):    badges.append(("POOP POWERUPS", (255,100,180)))
            if detail_ch.get("venom_kick"):      badges.append(("VENOM KICK",    ( 60,180, 40)))
            if detail_ch.get("jetpack"):         badges.append(("JETPACK",       (200,100,255)))
            if detail_ch.get("chomp"):           badges.append(("CHOMP",         (255,220,  0)))
            if detail_ch.get("chicken_banana"):  badges.append(("RAM CHARGE",    (255,180,  0)))
            if detail_ch.get("soul_master"):     badges.append(("SOUL HOP",      ( 80,  0,160)))
            if detail_ch.get("copycat"):         badges.append(("COPYCAT",       (180,180,180)))
            if detail_ch.get("orb_shooter"):     badges.append(("CHARGE ORB",    ( 80,160,255)))
            if detail_ch.get("glitch_strike"):   badges.append(("GLITCH HIT",    (  0,255,180)))
            if detail_ch.get("death_defyer"):    badges.append(("DEATH DEFYER",  (200,230,255)))
            if detail_ch.get("bubble_kick"):     badges.append(("BUBBLE KICK",   ( 80,200,160)))
            if detail_ch.get("rainbow_snake"):   badges.append(("FOREVER POWER", (200,100,255)))
            if detail_ch.get("taipan_punch"):    badges.append(("SUPPRESS PUNCH",(120, 80, 40)))
            if detail_ch.get("cobra_orb"):       badges.append(("POISON ORB",    ( 30,100, 30)))
            if detail_ch.get("giant_bug_kick"):  badges.append(("GIANT BUG",     ( 60,160, 60)))
            if detail_ch.get("black_hole_kick"): badges.append(("BLACK HOLE",    ( 80,  0,180)))
            if detail_ch.get("bug_spawner_kick"):badges.append(("BUG SPAWNER",   (255,200,  0)))
            if detail_ch.get("widow_kick"):      badges.append(("WALL BUGS",     ( 10, 10, 10)))
            if detail_ch.get("ai_clones"):       badges.append(("5 CLONES",      (  0,220,200)))
            if detail_ch.get("auto_forcefield"): badges.append(("FORCEFIELD",    (100,180,255)))
            if detail_ch.get("possess_kick"):    badges.append(("POSSESS",       (180, 80,255)))
            if detail_ch.get("armor_proj"):      badges.append(("PROJ IMMUNE",   (160,160,180)))
            if detail_ch.get("deflect_proj"):    badges.append(("DEFLECT",       (100,220,255)))
            if detail_ch.get("unhittable"):      badges.append(("60% DODGE",     (240,240,100)))
            if detail_ch.get("mega_unhittable"): badges.append(("99.9% DODGE",   (255,255,150)))
            # 11 new characters
            if detail_ch.get("note_kick"):       badges.append(("NOTE KICK",     (180,100,200)))
            if detail_ch.get("cleave_kick"):     badges.append(("CLEAVE KICK",   (140, 60, 40)))
            if detail_ch.get("heavy"):           badges.append(("HEAVY",         (120,110,100)))
            if detail_ch.get("money_hit"):       badges.append(("MONEY HIT",     (220,180,  0)))
            if detail_ch.get("glass_jaw"):       badges.append(("GLASS JAW",     (200,160,200)))
            if detail_ch.get("drain_aura"):      badges.append(("DRAIN AURA",    (160, 20, 80)))
            if detail_ch.get("lance_punch"):     badges.append(("LANCE PUNCH",   (200,160, 60)))
            if detail_ch.get("absorb_hit"):      badges.append(("ABSORB HIT",    (100,200,160)))
            if detail_ch.get("hex_kick"):        badges.append(("HEX KICK",      ( 80, 30,120)))
            if detail_ch.get("gamble_kick"):     badges.append(("GAMBLE KICK",   (100,200, 80)))
            if detail_ch.get("auto_counter"):    badges.append(("AUTO COUNTER",  (180,100, 60)))
            if detail_ch.get("fire_aura"):       badges.append(("FIRE AURA",     (220, 90, 20)))
            if detail_ch.get("colossus"):        badges.append(("COLOSSUS",      (100,130, 70)))
            if detail_ch.get("stomp_punch"):     badges.append(("STOMP PUNCH",   ( 60, 70,180)))
            if detail_ch.get("spike_body"):      badges.append(("SPIKE BODY",    ( 80,160, 60)))
            if detail_ch.get("anchor_body"):     badges.append(("ANCHOR",        ( 60, 60,100)))
            if detail_ch.get("sleep_body"):      badges.append(("SLEEP AURA",    (120, 80,180)))
            if detail_ch.get("berserk_low"):     badges.append(("BERSERK MODE",  (200, 40, 20)))
            if detail_ch.get("twin_strike"):     badges.append(("TWIN STRIKE",   ( 80,180,200)))
            if detail_ch.get("sap_kick"):        badges.append(("SAP KICK",      (120, 60, 30)))
            if detail_ch.get("mimic_stats"):     badges.append(("MIMIC STATS",   (150,150,160)))
            if detail_ch.get("boomerang_kick"):  badges.append(("BOOMERANG",     (200,110, 30)))
            if detail_ch.get("parry_strike"):    badges.append(("PARRY STRIKE",  ( 60,120,200)))
            if detail_ch.get("combat_regen"):    badges.append(("COMBAT REGEN",  (100,200,120)))
            if detail_ch.get("iron_block"):      badges.append(("IRON BLOCK",    ( 80, 80,100)))
            if detail_ch.get("pierce_kick"):     badges.append(("PIERCE KICK",   (160,160,180)))
            if detail_ch.get("rage_stack"):      badges.append(("RAGE STACK",    (180, 50, 50)))
            if detail_ch.get("phoenix_revive"):  badges.append(("PHOENIX",       (220,120, 20)))
            if detail_ch.get("chain_hits"):      badges.append(("CHAIN HITS",    ( 60,160,160)))
            if detail_ch.get("block_break"):     badges.append(("BLOCK BREAK",   (100, 80,160)))
            if detail_ch.get("titan_grip"):      badges.append(("TITAN GRIP",    ( 90, 60,130)))
            if detail_ch.get("overload"):        badges.append(("OVERLOAD",      (255, 80,220)))
            if detail_ch.get("glitch_char"):     badges.append(("GLITCH",        ( 60,255,120)))
            if detail_ch.get("reflect_dmg"):     badges.append(("REFLECT DMG",   (200,200, 80)))
            if detail_ch.get("one_punch_man"):   badges.append(("ONE PUNCH",     (255,255,255)))
            if detail_ch.get("nick_of_time"):    badges.append(("NICK OF TIME",  ( 60,200,255)))
            if detail_ch.get("buffer_char"):     badges.append(("BUFFER",        (100,220,100)))
            if detail_ch.get("cursed_drain"):    badges.append(("CURSED",        ( 80,  0, 80)))
            bx_off = PX + 8
            for btxt, bcol in badges:
                bs = font_tiny.render(btxt, True, bcol)
                if bx_off + bs.get_width() + 10 > PX + PW - 4:
                    bx_off  = PX + 8
                    badge_y += 18
                pygame.draw.rect(screen, (40, 40, 60), (bx_off - 2, badge_y - 1, bs.get_width() + 8, 16), border_radius=3)
                screen.blit(bs, (bx_off + 2, badge_y))
                bx_off += bs.get_width() + 14

        # READY touch button
        _rdy_col = BLUE if not p1_ready else ORANGE
        _rdy_rect = pygame.Rect(PX, PY + PH - 52, PW, 44)
        pygame.draw.rect(screen, tuple(max(0, c - 80) for c in _rdy_col), _rdy_rect, border_radius=8)
        pygame.draw.rect(screen, _rdy_col, _rdy_rect, 2, border_radius=8)
        _rdy_lbl = "READY" if not p1_ready else ("PICK P2" if not vs_ai and not p2_ready else "")
        if _rdy_lbl:
            _rs = font_medium.render(_rdy_lbl, True, WHITE)
            screen.blit(_rs, (_rdy_rect.centerx - _rs.get_width() // 2,
                              _rdy_rect.centery - _rs.get_height() // 2))

        # Controls hint at bottom of panel
        if not p1_ready:
            hint = "tap char + READY   or   WASD + ENTER"
            hcol = BLUE
        elif not vs_ai and not p2_ready:
            hint = "tap char + PICK P2   or   Arrows + ENTER"
            hcol = ORANGE
        else:
            hint, hcol = "", WHITE
        if hint:
            hs = font_tiny.render(hint, True, hcol)
            screen.blit(hs, (PX + PW//2 - hs.get_width()//2, PY + PH - 58))

        # Ready flash on panel border
        if p1_ready and p2_ready:
            if flash_t < 20:
                pygame.draw.rect(screen, GREEN, (PX, PY, PW, PH), 3, border_radius=10)

        esc = font_tiny.render("ESC — back to menu", True, GRAY)
        screen.blit(esc, (GX + 4, HEIGHT - 22))

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Online play helpers
# ---------------------------------------------------------------------------

def _draw_waiting(msg, sub=""):
    screen.fill(DARK)
    t = font_medium.render(msg, True, WHITE)
    screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 28))
    if sub:
        s = font_small.render(sub, True, GRAY)
        screen.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()


def _text_input_screen(prompt, default="", max_len=20):
    """Full-screen text input. Returns entered string, or None on ESC."""
    text = default
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_RETURN:
                    return text.strip() or default
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.unicode.isprintable() and len(text) < max_len:
                    text += event.unicode
        screen.fill(DARK)
        p = font_medium.render(prompt, True, YELLOW)
        screen.blit(p, (WIDTH//2 - p.get_width()//2, HEIGHT//3 - 30))
        box = pygame.Rect(WIDTH//2 - 180, HEIGHT//3 + 20, 360, 48)
        pygame.draw.rect(screen, (60, 60, 60), box, border_radius=8)
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=8)
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        tv = font_medium.render(text + cursor, True, WHITE)
        screen.blit(tv, (box.x + 12, box.y + 8))
        hint = font_tiny.render("ENTER to confirm   ESC to cancel", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//3 + 90))
        pygame.display.flip()


def set_username_screen(userdata):
    name = _text_input_screen("Enter your username:", userdata.get("username", "Player"), max_len=16)
    if name:
        userdata["username"] = name
        _net.save_userdata(userdata)


def server_settings_screen(userdata):
    """Let the player type in the fight_server IP (or blank for localhost)."""
    cur = userdata.get("server_ip", "")
    result = _text_input_screen("Server IP  (blank = localhost):", cur, max_len=48)
    if result is not None:
        userdata["server_ip"] = result.strip()
        _net.save_userdata(userdata)


def _make_lobby(userdata, timeout=6):
    """Connect to the fight_server and register. Returns LobbyClient or None."""
    host = _net.DEFAULT_SERVER_IP
    lc   = _net.LobbyClient()
    try:
        lc.connect(host, timeout=timeout)
    except Exception as e:
        return None
    lc.register(userdata["user_code"], userdata["username"])
    # Wait for HELLO_OK (up to 3 s)
    deadline = pygame.time.get_ticks() + 3000
    while pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        for m in lc.take_pending():
            if m.get("type") == "HELLO_OK":
                return lc
        lc.poll()
    return lc   # return anyway (server might not send HELLO_OK in all builds)


def friend_chat_screen(userdata, to_code, friend_name):
    """
    Open a live chat window with a friend via the fight_server.
    Connects, registers, then lets the user type messages.
    Incoming FRIEND_CHAT messages from to_code are shown in the log.
    """
    _draw_waiting("Connecting to server…")
    lobby = _make_lobby(userdata, timeout=5)
    if lobby is None:
        _draw_waiting("Could not reach server.", "Check Server Settings.  Any key…")
        _wait_key(); return

    log   = []   # [(label, text)]
    inp   = ""
    clock.tick(FPS)

    while True:
        clock.tick(FPS)

        # Drain incoming friend messages
        lobby.poll()
        for fc, fn, txt in lobby.friend_msgs:
            if fc == to_code:
                log.append((fn, txt))
        lobby.friend_msgs.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lobby.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    lobby.close(); return
                elif event.key == pygame.K_RETURN:
                    text = inp.strip()
                    if text:
                        lobby.friend_chat(to_code, text)
                        log.append(("You", text))
                    inp = ""
                elif event.key == pygame.K_BACKSPACE:
                    inp = inp[:-1]
                elif event.unicode.isprintable() and len(inp) < 60:
                    inp += event.unicode

        # Draw
        screen.fill(DARK)
        title = font_medium.render(f"Chat — {friend_name}  [{to_code}]", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 14))

        # Chat log (last lines that fit)
        max_lines = (HEIGHT - 110) // 22
        for i, (sender, text) in enumerate(log[-max_lines:]):
            col  = CYAN if sender == "You" else YELLOW
            line = font_tiny.render(f"{sender}: {text}", True, col)
            screen.blit(line, (16, 60 + i * 22))

        # Input bar
        pygame.draw.rect(screen, (30, 30, 50), (0, HEIGHT - 48, WIDTH, 48))
        cur_sym = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        iv = font_small.render(inp + cur_sym, True, WHITE)
        screen.blit(iv, (14, HEIGHT - 38))

        hint = font_tiny.render("ENTER = send   ESC = back", True, GRAY)
        screen.blit(hint, (WIDTH - hint.get_width() - 10, HEIGHT - 16))
        pygame.display.flip()


def _wait_key():
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return


def _respond_friend_request_screen(name, code):
    """
    Show an incoming friend request popup.
    Returns True (accept) or False (decline).
    """
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN):
                    return True
                if event.key in (pygame.K_n, pygame.K_ESCAPE):
                    return False
        screen.fill(DARK)
        t = font_large.render("Friend Request!", True, CYAN)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//3 - 60))
        n = font_medium.render(name, True, YELLOW)
        screen.blit(n, (WIDTH//2 - n.get_width()//2, HEIGHT//3 + 10))
        c = font_small.render(f"[{code}]", True, GRAY)
        screen.blit(c, (WIDTH//2 - c.get_width()//2, HEIGHT//3 + 55))
        h = font_small.render("wants to be your friend", True, WHITE)
        screen.blit(h, (WIDTH//2 - h.get_width()//2, HEIGHT//3 + 95))
        hint = font_tiny.render("Y / ENTER = Accept     N / ESC = Decline", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 80))
        pygame.display.flip()


def _add_friend_flow(userdata, friends, lobby):
    """
    Send a friend request via the server and wait for the target to accept/decline.
    lobby must already be connected and registered.
    Returns a status message string, or None on silent cancel.
    """
    code = _text_input_screen("Enter their 8-char friend code:", max_len=8)
    if not code:
        return None
    code = code.upper().replace(" ", "").replace("-", "")
    if len(code) != 8:
        return "Invalid code — friend codes are exactly 8 characters."
    if code == userdata.get("user_code", ""):
        return "That's your own code!"
    if not all(c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in code):
        return "Invalid code — letters and numbers only."
    if code in friends:
        return "Already friends!"

    # Look up their name first
    _draw_waiting("Checking if they're online…")
    lobby.lookup_friend(code)
    found_name = None
    deadline   = pygame.time.get_ticks() + 4000
    while pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        lobby.poll()
        for m in lobby.take_pending():
            if m.get("type") == "FRIEND_INFO" and m.get("code") == code:
                if m.get("online") and m.get("username"):
                    found_name = m["username"]
        if found_name is not None:
            break

    if found_name is None:
        return "That person isn't online right now."

    # Send the request and wait for their response
    lobby.send_friend_request(code)

    dots_t = 0
    deadline = pygame.time.get_ticks() + 60_000   # 60 s timeout
    while pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        lobby.poll()
        # Check for result
        for r_code, r_name, r_result in lobby.friend_req_results[:]:
            if r_code == code:
                lobby.friend_req_results.remove((r_code, r_name, r_result))
                if r_result == "accepted":
                    friends[code] = {"name": found_name}
                    return f"{found_name} accepted your friend request!"
                elif r_result == "declined":
                    return f"{found_name} declined your friend request."
                else:
                    return f"{found_name} is not available."
        # Also handle incoming requests while waiting
        _process_incoming_requests(lobby, userdata, friends)

        dots_t += 1
        dots = "." * ((dots_t // 20) % 4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
        screen.fill(DARK)
        tl = font_large.render("Friend Request Sent", True, CYAN)
        screen.blit(tl, (WIDTH//2 - tl.get_width()//2, HEIGHT//3 - 40))
        wl = font_medium.render(f"Waiting for {found_name}{dots}", True, WHITE)
        screen.blit(wl, (WIDTH//2 - wl.get_width()//2, HEIGHT//2 - 10))
        hl = font_tiny.render("ESC to cancel", True, GRAY)
        screen.blit(hl, (WIDTH//2 - hl.get_width()//2, HEIGHT - 28))
        pygame.display.flip()
        if not lobby.connected:
            break

    return "No response — they may have gone offline."


def _process_incoming_requests(lobby, userdata, friends):
    """Check lobby for incoming friend requests and show accept/decline popup."""
    if not lobby or not lobby.connected:
        return
    while lobby.incoming_friend_reqs:
        fc, fn = lobby.incoming_friend_reqs.pop(0)
        if fc in friends:
            lobby.respond_friend_request(fc, True)   # already friends — auto-accept
            continue
        accepted = _respond_friend_request_screen(fn, fc)
        lobby.respond_friend_request(fc, accepted)
        if accepted:
            friends[fc] = {"name": fn}
            _net.save_userdata(userdata)


def friends_screen(userdata):
    friends   = userdata.setdefault("friends", {})   # code → {"name": str}
    user_code = userdata.get("user_code", "????????")
    sel       = 0
    msg       = ""
    msg_t     = 0
    msg_col   = GREEN

    # Keep a live server connection so incoming friend requests can arrive
    _draw_waiting("Connecting to server…")
    lobby = _make_lobby(userdata, timeout=4)

    while True:
        clock.tick(FPS)
        keys_list = list(friends.keys())

        # Poll server — handle incoming friend requests
        if lobby and lobby.connected:
            lobby.poll()
            if lobby.incoming_friend_reqs:
                _process_incoming_requests(lobby, userdata, friends)
                msg = "Friend list updated!"; msg_t = 150; msg_col = GREEN

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if lobby: lobby.close()
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if lobby: lobby.close()
                    _net.save_userdata(userdata); return
                if keys_list:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        sel = (sel - 1) % len(keys_list)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        sel = (sel + 1) % len(keys_list)
                    if event.key == pygame.K_d:
                        del friends[keys_list[sel]]
                        sel = max(0, sel - 1)
                        msg = "Friend removed."; msg_t = 150; msg_col = RED
                        _net.save_userdata(userdata)
                    if event.key == pygame.K_c:
                        fc = keys_list[sel]
                        fn = friends[fc].get("name", fc)
                        friend_chat_screen(userdata, fc, fn)
                if event.key == pygame.K_a:
                    if lobby and lobby.connected:
                        result = _add_friend_flow(userdata, friends, lobby)
                    else:
                        result = "Not connected to server."
                    if result:
                        accepted = "accepted" in result or "Added" in result
                        msg_col = GREEN if accepted else RED
                        msg = result; msg_t = 200
                        if accepted:
                            _net.save_userdata(userdata)

        screen.fill(DARK)
        title = font_large.render("FRIENDS", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

        own = font_small.render(f"Your code:  {user_code}", True, (100, 220, 100))
        screen.blit(own, (WIDTH//2 - own.get_width()//2, 68))

        srv_col = (80, 200, 80) if (lobby and lobby.connected) else (200, 60, 60)
        srv_lbl = font_tiny.render(
            "● Server connected" if (lobby and lobby.connected)
            else "● Server offline — friend requests disabled", True, srv_col)
        screen.blit(srv_lbl, (WIDTH//2 - srv_lbl.get_width()//2, 96))

        if not friends:
            em = font_medium.render("No friends yet.  Press A to add one.", True, GRAY)
            screen.blit(em, (WIDTH//2 - em.get_width()//2, HEIGHT//2 - 18))
        else:
            for i, code in enumerate(keys_list):
                name = friends[code].get("name", "?")
                col  = YELLOW if i == sel else WHITE
                row  = font_small.render(
                    f"{'► ' if i == sel else '  '}{name}   [{code}]", True, col)
                screen.blit(row, (80, 126 + i * 36))

        if msg_t > 0:
            ms = font_small.render(msg, True, msg_col)
            screen.blit(ms, (WIDTH//2 - ms.get_width()//2, HEIGHT - 60))
            msg_t -= 1

        hint = font_tiny.render(
            "A = add friend   C = chat   D = delete   ESC = back", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))
        pygame.display.flip()


def matchmaking_screen(userdata):
    """
    Connect to fight_server, join the matchmaking queue, wait for a random
    opponent, pick a character, exchange picks, and return:
      (lobby, p1_char_idx, p2_char_idx, stage_idx, is_host, opp_name)
    or None on cancel / error.
    """
    # Step 1 — Connect & register
    _draw_waiting("Connecting to server…")
    lobby = _make_lobby(userdata, timeout=6)
    if lobby is None:
        _draw_waiting("Could not reach server.", "Check Server Settings.  Any key…")
        _wait_key(); return None
    if not lobby.connected:
        _draw_waiting("Server refused connection.", "Any key…")
        _wait_key(); return None

    # Step 2 — Join queue
    lobby.join_queue()

    # Step 3 — Wait for MATCH_FOUND
    dots_t = 0
    while lobby.match_info is None:
        clock.tick(FPS)
        lobby.poll()
        dots_t += 1
        dots = "." * ((dots_t // 30) % 4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lobby.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    lobby.leave_queue(); lobby.close(); return None

        screen.fill(DARK)
        t  = font_large.render("QUICK MATCH", True, CYAN)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 60))
        s  = font_medium.render(f"Searching for opponent{dots}", True, WHITE)
        screen.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 - 20))
        ht = font_tiny.render("ESC to cancel", True, GRAY)
        screen.blit(ht, (WIDTH//2 - ht.get_width()//2, HEIGHT - 28))
        pygame.display.flip()

        if not lobby.connected:
            _draw_waiting("Lost connection to server.", "Any key…")
            _wait_key(); return None

    info      = lobby.match_info
    is_host   = info.get("you_host", True)
    stage_idx = info.get("stage", 0)
    opp_name  = info.get("opp_name", "Opponent")
    opp_code  = info.get("opp_code", "")

    # Optionally save opponent as friend (no nickname prompt — just code)
    userdata.setdefault("friends", {}).setdefault(opp_code, {"name": opp_name})
    _net.save_userdata(userdata)

    # Step 4 — Brief "Found!" screen
    found_end = pygame.time.get_ticks() + 1800
    while pygame.time.get_ticks() < found_end:
        clock.tick(FPS)
        lobby.poll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lobby.close(); pygame.quit(); sys.exit()
        screen.fill(DARK)
        ft = font_large.render("MATCH FOUND!", True, GREEN)
        screen.blit(ft, (WIDTH//2 - ft.get_width()//2, HEIGHT//2 - 50))
        vt = font_medium.render(f"vs  {opp_name}", True, YELLOW)
        screen.blit(vt, (WIDTH//2 - vt.get_width()//2, HEIGHT//2 + 10))
        from fight_data import STAGES
        sn = font_small.render(f"Stage: {STAGES[stage_idx % len(STAGES)]['name']}", True, WHITE)
        screen.blit(sn, (WIDTH//2 - sn.get_width()//2, HEIGHT//2 + 55))
        pygame.display.flip()

    # Step 5 — Character select (both players do this simultaneously)
    my_idx, _ = character_select(vs_ai=True)
    if my_idx is None:
        lobby.close(); return None

    # Step 6 — Exchange character picks via relay
    lobby.relay({"type": "PICK", "char_idx": my_idx})
    opp_idx  = None
    deadline = pygame.time.get_ticks() + 20000
    while opp_idx is None and pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        _draw_waiting(f"Waiting for {opp_name} to pick…", "ESC to cancel")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lobby.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    lobby.close(); return None
        for m in lobby.poll():
            if isinstance(m, dict) and m.get("type") == "PICK":
                opp_idx = m["char_idx"]
        if not lobby.connected:
            break

    if opp_idx is None:
        lobby.close(); return None

    if is_host:
        p1_idx, p2_idx = my_idx, opp_idx
    else:
        p1_idx, p2_idx = opp_idx, my_idx

    return lobby, p1_idx, p2_idx, stage_idx, is_host, opp_name


def host_lobby(userdata):
    """
    Start server, show friend codes, wait for connection, do character
    select + stage select, exchange PICK, return (net, p1_char, p2_char, stage).
    Returns None if cancelled.
    """
    net = _net.GameServer()
    net.start()

    # Fetch public IP in background so the screen isn't blocked
    public_ip = [socket.gethostbyname(socket.gethostname())]
    def _fetch():
        public_ip[0] = _net.get_public_ip()
    threading.Thread(target=_fetch, daemon=True).start()

    local_ip = socket.gethostbyname(socket.gethostname())

    # Wait for client to connect
    while not net.connected:
        clock.tick(FPS)
        net.poll_accept()

        code_pub = _net.ip_port_to_code(public_ip[0], _net.PORT)
        code_loc = _net.ip_port_to_code(local_ip,     _net.PORT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                net.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    net.close(); return None

        screen.fill(DARK)
        t = font_large.render("HOST GAME", True, CYAN)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 25))

        y = 110
        for label, code in [("Internet code (share this):", code_pub),
                             ("LAN code:",                   code_loc)]:
            lb = font_small.render(label, True, GRAY)
            screen.blit(lb, (WIDTH//2 - 210, y))
            cb = font_medium.render(code, True, YELLOW)
            screen.blit(cb, (WIDTH//2 - 210, y + 28))
            y += 85

        dots = "." * ((pygame.time.get_ticks() // 500) % 4)
        st = font_small.render(f"Waiting for opponent{dots}", True, WHITE)
        screen.blit(st, (WIDTH//2 - st.get_width()//2, y + 20))
        hint = font_tiny.render("ESC to cancel", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))
        pygame.display.flip()

    # Exchange usernames
    net.send({"type": "HELLO", "username": userdata["username"]})
    deadline = pygame.time.get_ticks() + 5000
    while pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        _draw_waiting(f"Connected!  Exchanging info…")
        for m in net.recv_all():
            if m.get("type") == "HELLO":
                net.opp_name = m.get("username", "Opponent")
                # Save as friend
                code_pub = _net.ip_port_to_code(public_ip[0], _net.PORT)
                userdata.setdefault("friends", {})[code_pub] = {"name": net.opp_name}
                _net.save_userdata(userdata)
                deadline = 0
                break

    # Character select (host only picks for themselves)
    p1_idx, _ = character_select(vs_ai=True)
    if p1_idx is None:
        net.close(); return None

    s_idx = stage_select()

    # Send pick and wait for client's pick
    net.send({"type": "PICK", "char_idx": p1_idx, "stage_idx": s_idx})
    p2_idx  = None
    deadline = pygame.time.get_ticks() + 20000
    while p2_idx is None and pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        _draw_waiting(f"Waiting for {net.opp_name} to pick…", "ESC to cancel")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                net.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    net.close(); return None
        for m in net.recv_all():
            if m.get("type") == "PICK":
                p2_idx = m["char_idx"]

    if p2_idx is None:
        net.close(); return None

    return net, p1_idx, p2_idx, s_idx


def join_lobby(userdata):
    """
    Ask for friend code, connect, exchange PICK, return
    (net, my_char(=p2), host_char(=p1), stage).  Returns None on cancel/error.
    """
    code = _text_input_screen("Enter friend code:", max_len=10)
    if not code:
        return None
    code = code.upper().replace(" ", "").replace("-", "")

    try:
        ip, port = _net.code_to_ip_port(code)
    except Exception:
        _draw_waiting("Invalid code.", "Returning to menu…")
        pygame.time.wait(1800)
        return None

    net = _net.GameClient()
    _draw_waiting(f"Connecting to {ip}:{port}…", "Please wait")
    try:
        net.connect(ip, port, timeout=10)
    except Exception as e:
        _draw_waiting(f"Connection failed.", str(e)[:60])
        pygame.time.wait(2200)
        return None

    # Exchange usernames
    net.send({"type": "HELLO", "username": userdata["username"]})
    deadline = pygame.time.get_ticks() + 5000
    while pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        _draw_waiting("Connected!  Exchanging info…")
        for m in net.recv_all():
            if m.get("type") == "HELLO":
                net.opp_name = m.get("username", "Host")
                userdata.setdefault("friends", {})[code] = {"name": net.opp_name}
                _net.save_userdata(userdata)
                deadline = 0
                break

    # Character select (client only picks for themselves)
    my_idx, _ = character_select(vs_ai=True)
    if my_idx is None:
        net.close(); return None

    # Exchange picks — client sends first, then waits for host's pick (which has stage)
    net.send({"type": "PICK", "char_idx": my_idx})
    p1_idx  = None
    s_idx   = 0
    deadline = pygame.time.get_ticks() + 20000
    while p1_idx is None and pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        _draw_waiting(f"Waiting for {net.opp_name} to pick…", "ESC to cancel")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                net.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    net.close(); return None
        for m in net.recv_all():
            if m.get("type") == "PICK":
                p1_idx = m["char_idx"]
                s_idx  = m.get("stage_idx", 0)

    if p1_idx is None:
        net.close(); return None

    # (net, my_char=p2_char, host_char=p1_char, stage)
    return net, my_idx, p1_idx, s_idx


def secret_menu(unlocked, stats):
    """Terminal-style cheat code menu. Returns list of newly unlocked character names."""
    newly = []
    input_buf = ""
    feedback = ""
    feedback_col = (0, 255, 100)
    feedback_timer = 0
    history = []   # list of (code_str, response_str, col)

    # Find char data for checking if char exists
    from fight_data import CHARACTERS as _CHARS
    _char_names = {ch["name"] for ch in _CHARS}
    _UNLOCK_CONDITIONS_REF = None

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return newly
                elif event.key == pygame.K_RETURN:
                    code = input_buf.strip().lower()
                    input_buf = ""
                    if code in CHEAT_CODES:
                        name = CHEAT_CODES[code]
                        if name in unlocked:
                            feedback = f"{name} already unlocked"
                            feedback_col = (180, 180, 60)
                            history.append((f"> {code}", "already unlocked", (180, 180, 60)))
                        else:
                            unlocked.add(name)
                            newly.append(name)
                            # Ensure evaluated_chars bypass for this char
                            ev = stats.get("evaluated_chars", [])
                            if name not in ev:
                                ev.append(name)
                                stats["evaluated_chars"] = ev
                            feedback = f"UNLOCKED: {name}!"
                            feedback_col = (0, 255, 100)
                            history.append((f"> {code}", f"UNLOCKED: {name}", (0, 255, 100)))
                    elif code == "":
                        pass
                    else:
                        feedback = "UNKNOWN CODE"
                        feedback_col = (255, 80, 80)
                        history.append((f"> {code}", "UNKNOWN CODE", (255, 80, 80)))
                    feedback_timer = FPS * 3
                elif event.key == pygame.K_BACKSPACE:
                    input_buf = input_buf[:-1]
                elif hasattr(event, 'unicode') and event.unicode and event.unicode.isprintable():
                    input_buf += event.unicode

        if feedback_timer > 0:
            feedback_timer -= 1

        # Draw terminal UI
        screen.fill((4, 8, 4))
        # Scanline overlay
        for _sy in range(0, HEIGHT, 4):
            pygame.draw.line(screen, (0, 15, 0), (0, _sy), (WIDTH, _sy), 1)
        # Title
        title = font_large.render("SECRET MENU", True, (0, 200, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        # Horizontal divider
        pygame.draw.line(screen, (0, 120, 0), (40, 90), (WIDTH - 40, 90), 1)

        # Command history (last 7 entries)
        for hi, (inp_txt, resp_txt, resp_col) in enumerate(history[-7:]):
            inp_s = font_small.render(inp_txt, True, (0, 160, 0))
            resp_s = font_small.render("  " + resp_txt, True, resp_col)
            base_y = 105 + hi * 46
            screen.blit(inp_s, (50, base_y))
            screen.blit(resp_s, (50, base_y + 22))

        # Input line
        prompt_y = HEIGHT - 100
        pygame.draw.line(screen, (0, 100, 0), (40, prompt_y - 8), (WIDTH - 40, prompt_y - 8), 1)
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        prompt_s = font_small.render(f"> {input_buf}{cursor}", True, (0, 255, 0))
        screen.blit(prompt_s, (50, prompt_y))

        # Feedback line
        if feedback_timer > 0:
            fb_s = font_medium.render(feedback, True, feedback_col)
            screen.blit(fb_s, (WIDTH // 2 - fb_s.get_width() // 2, HEIGHT - 55))

        # ESC hint
        esc_s = font_tiny.render("ESC to exit", True, (0, 80, 0))
        screen.blit(esc_s, (WIDTH - esc_s.get_width() - 10, HEIGHT - 18))
        pygame.display.flip()


def online_menu(userdata):
    """
    Top-level online menu.
    Returns ('quickmatch', (lobby, p1, p2, stage, is_host, opp_name))
         or ('host',       (net, p1_char, p2_char, stage))
         or ('join',       (net, p2_char, p1_char, stage))
         or None on cancel.
    """
    opts = ["QUICK MATCH", "HOST GAME", "JOIN GAME", "FRIENDS", "SET USERNAME"]
    sel  = 0

    # Keep a background lobby connection for incoming friend requests
    _lobby_bg = _make_lobby(userdata, timeout=3)

    while True:
        clock.tick(FPS)
        user_code = userdata.get("user_code", "????????")

        # Poll for incoming friend requests while idle on this menu
        if _lobby_bg and _lobby_bg.connected:
            _lobby_bg.poll()
            if _lobby_bg.incoming_friend_reqs:
                friends = userdata.setdefault("friends", {})
                _process_incoming_requests(_lobby_bg, userdata, friends)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if _lobby_bg: _lobby_bg.close()
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if _lobby_bg: _lobby_bg.close()
                    return None
                if event.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(opts)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(opts)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if sel == 0:   # QUICK MATCH
                        if _lobby_bg: _lobby_bg.close()
                        result = matchmaking_screen(userdata)
                        if result:
                            return 'quickmatch', result
                        _lobby_bg = _make_lobby(userdata, timeout=3)
                    elif sel == 1:  # HOST GAME
                        if _lobby_bg: _lobby_bg.close()
                        result = host_lobby(userdata)
                        if result:
                            return 'host', result
                        _lobby_bg = _make_lobby(userdata, timeout=3)
                    elif sel == 2:  # JOIN GAME
                        if _lobby_bg: _lobby_bg.close()
                        result = join_lobby(userdata)
                        if result:
                            return 'join', result
                        _lobby_bg = _make_lobby(userdata, timeout=3)
                    elif sel == 3:  # FRIENDS
                        if _lobby_bg: _lobby_bg.close()
                        friends_screen(userdata)
                        _lobby_bg = _make_lobby(userdata, timeout=3)
                    elif sel == 4:  # SET USERNAME
                        set_username_screen(userdata)

        screen.fill(DARK)
        title = font_large.render("ONLINE PLAY", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 18))

        # User identity
        name_lbl = font_small.render(
            f"You: {userdata.get('username', 'Player')}   code: {user_code}",
            True, (100, 220, 100))
        screen.blit(name_lbl, (WIDTH//2 - name_lbl.get_width()//2, 72))
        srv_col = (80, 200, 80) if (_lobby_bg and _lobby_bg.connected) else (160, 60, 60)
        srv_lbl = font_tiny.render(
            "● Connected" if (_lobby_bg and _lobby_bg.connected) else "● Server offline",
            True, srv_col)
        screen.blit(srv_lbl, (WIDTH//2 - srv_lbl.get_width()//2, 98))

        for i, opt in enumerate(opts):
            col = ((0, 255, 180) if i == sel else (0, 200, 140)) if i == 0 else \
                  (CYAN if i == sel else WHITE)
            r = font_medium.render(("► " if i == sel else "  ") + opt, True, col)
            screen.blit(r, (WIDTH//2 - r.get_width()//2, 130 + i * 56))

        hint = font_tiny.render("↑/↓  ENTER to select   ESC = back", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))
        pygame.display.flip()
