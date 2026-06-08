import pygame
import sys
import math
import socket
import threading
import fight_network as _net
from constants import *
from fight_data import CHARACTERS, STAGES, STAGE_MATCHUPS
from fight_drawing import draw_bg, draw_stickman
from fight_seasonal import SEASONAL_EVENTS, SEASONAL_SHOP_CHARS, get_active_event, draw_seasonal_decos

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
    "last_second":        "Nick of Time",
    "get_big":            "Buffer",
    "be_cursed":          "Cursed",
    # batch 1 stragglers
    "pickpocket":         "Phantom Thief",
    "cant_be_done":       "The Impossible Victor",
    # batch 2 — Sunderer through Cyclone
    "split_open":         "Sunderer",
    "bad_dream":          "Haunter",
    "lightning_god":      "Zeus",
    "deep_freeze":        "Glacial",
    "devour_souls":       "Soul Eater",
    "go_berserk_now":     "Frenzy",
    "walk_through":       "Specter",
    "wrecking_ball":      "Demolisher",
    "mirror_damage":      "Feedback",
    "power_surge":        "Escalator",
    "turn_cheek":         "Pacifist",
    "eye_of_storm":       "Cyclone",
    # batch 2 — Phantom Blade through Magma
    "ghost_sword":        "Phantom Blade",
    "hell_fire":          "Inferno",
    "ground_slam":        "Titan Smash",
    "sneak_in":           "Infiltrator",
    "final_blow":         "Executioner",
    "heart_of_ice":       "Coldheart",
    "storm_rage":         "Tempest",
    "old_ways":           "Ancient",
    "war_fury":           "Berserk Lord",
    "night_moves":        "Shadow Dancer",
    "doll_pain":          "Voodoo",
    "lava_flow":          "Magma",
    # batch 3 — Minotaur through Abomination
    "labyrinth_king":     "Minotaur",
    "pull_strings":       "Puppet Master",
    "gear_grind":         "Clockwork",
    "step_through":       "Void Walker",
    "phylactery":         "Lich",
    "blood_lust":         "Crimson",
    "punch_line":         "Jester",
    "clay_form":          "Golem",
    "kindle_fire":        "Blaze",
    "power_spike":        "Surge",
    "ghost_royale":       "Phantom King",
    "grotesque":          "Abomination",
    # batch 5
    "hex_broom":          "Witch",
    "goliath_down":       "Giant Killer",
    "full_throttle":      "Speed Demon",
    "joker_card":         "High Roller",
    "spirit_blade":       "Ghost Warrior",
    "card_king":          "Suicide King",
    "doom_coming":        "Harbinger",
    "hex_master":         "Hex Doctor",
    "clock_stop":         "Time Warden",
    "double_take":        "Doppelganger",
    "dirt_digger":        "Graverobber",
    "punch_king":         "Brawler King",
    # batch 4
    "bull_seye":          "Marksman",
    "wise_one":           "Elder",
    "dark_shadow":        "Shade Walker",
    "all_my_rules":       "Emperor",
    "steel_grip":         "Iron Grappler",
    "pirate_life":        "Corsair",
    "mech_warrior":       "Mech",
    "lock_down":          "Vault",
    "five_point":         "Shaolin",
    "conquest_now":       "Warlord",
    "open_up":            "Surgeon",
    "jugular":            "Cutthroat",
    "well_done":          "Chef",
    "from_behind":        "Backstabber",
    "out_of_mind":        "Crazy",
    # batch 6
    "blood_sucker":       "Leech King",
    "string_puller":      "Puppeteer",
    "arcane_power":       "Sorcerer",
    "steadfast":          "Guardian",
    "spiky_suit":         "Iron Maiden",
    "queen_of_rage":      "Berserker Queen",
    "specter_lord":       "Phantom Lord",
    "caught_ya":          "Trapper",
    "shadow_knight":      "Dark Knight",
    "holy_order":         "Templar",
    "multi_head":         "Hydra",
    "three_in_one":       "Chimera",
    "spin_the_wheel":     "Fortune",
    "pure_entropy":       "Chaos Lord",
    # eggshell
    "handle_with_care":   "Eggshell",
    # batch 7
    "roll_em":            "Cannonball",
    "see_through":        "Wraith",
    "ring_around":        "Plaguebringer",
    "hold_the_line":      "Bulwark",
    "silent_kill":        "Assassin",
    "smash_em_flat":      "Wrecking Ball",
    "on_the_hunt":        "Bounty Hunter",
    "from_the_deep":      "Abyssal",
    "risen_again":        "Revenant King",
    "shade_of_night":     "Shadow Lord",
    "carved_in_stone":    "Rune Mage",
    "monk_of_war":        "Berserker Monk",
    # batch 8
    "iron_hands":         "Steel Knuckle",
    "brittle_dynamite":   "Crystal Bomber",
    "old_soldier":        "Veteran",
    "transylvania":       "Strigone",
    "ave_caesar":         "Legionnaire",
    "dark_contract":      "Shadowbind",
    "rock_golem_rise":    "Stone Golem",
    "ride_the_lightning": "Storm Rider",
    "minus_forty":        "Frostbite",
    "crimson_ritual":     "Blood Mage",
    "shiny_armor":        "Mirror Knight",
    "lucky_draw":         "Desperado",
    "grave_robbing":      "Tomb Raider",
    "rewind_time":        "Chronomancer",
    "big_big_boy":        "Behemoth",
    "it_comes_back":      "Boom-Boom-Boomerang",
    "pillage_and_plunder": "Marauder",
    "holy_wings":          "Seraph",
    "eye_of_the_storm":    "Typhoon",
    "iron_curtain":        "Ironveil",
    "shock_wave":          "Pulse",
    "all_that_glitters":   "Gilded",
    "twilight_strike":     "Dusk",
    "light_refraction":    "Chaos",
    "cold_ashes":          "Ashen",
    "berserker_blood":     "Ravager",
    "wall_of_thorns":      "Thornwall",
    "future_sight":        "Diviner",
    "walk_the_plank":      "Cutlass",
    "sworn_enemy":         "Oathbreaker",
    "spell_weaver":        "Arcanist",
    "golden_thread":       "Anansi",
    "river_yokai":         "Kappa",
    "phantom_queen":       "Morrigan",
    "crow_of_battle":      "Badb",
    "frenzy_spirit":       "Nemain",
    "desert_riddle":        "Sphinx",
    "hunger_of_the_north":  "Wendigo",
    "leave_no_trace":       "Trailblazer",
    "guardian_of_the_gate": "Aqrabuamelu",
    # seasonal / newer characters
    "gobble_time":          "Cornucopia",
    "spin_the_dreidel":     "Nun-Gimel-Hei-Shin",
    "ho_ho_ho":             "Saint Nix",
    "bunny_bandit":         "Baddit",
    "grow_big":             "Eartha",
    "rip_and_rest":         "Tombstone",
    "rise_of_the_sun":      "Solara",
    "land_of_the_free":     "Stickman of Liberty",
    "read_em":              "Bookzworm",
    "geyser_time":          "Yellowstone",
    "pumpkin_carve":        "Jack O' Slash",
    "lion_dance":           "Nian",
    "pucker_up":            "Smoochie",
    "luck_of_the_irish":    "Clover",
    # batch 10 — new unlockable characters
    "blink_out":            "Blink",
    "desert_storm":         "Sandstorm",
    "spirit_wail":          "Wail",
    "iron_keep":            "Fortress",
    "puppet_dance":         "Marionette",
    "ice_wall_go":          "Glacier",
    "burn_bright":          "Wildfire",
    "hex_vex":              "Vex",
    "steadfast_go":         "Stalwart",
    "all_same":             "Ditto",
    # seasonal Eartha variants (Giants Among Us drops)
    "spring_eartha":        "Spring Eartha",
    "summer_eartha":        "Summer Eartha",
    "autumn_eartha":        "Autumn Eartha",
    "winter_eartha":        "Winter Eartha",
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
        draw_seasonal_decos(screen)

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
    """Returns ('1p', difficulty), '2p', 'survival_1p', 'survival_2p', 'online', or 'seasonal_shop'."""
    selected = 0   # 0=1P, 1=2P, 2=SURVIVAL, 3=ONLINE, 4=SHOP
    difficulty_idx = 1
    difficulties = ['easy', 'medium', 'hard', 'super_hard', 'super_super_hard', 'mega_hard']
    diff_colors  = [GREEN, YELLOW, RED, PURPLE, CYAN, ORANGE]
    scroll_offset = 0
    VISIBLE = 3
    survival_players = 0   # 0=1P survival, 1=2P survival
    preview_t = 0.0

    # 5 cards layout
    card_w, card_h = 140, 240
    GAP   = 8
    START = WIDTH // 2 - (5 * card_w + 4 * GAP) // 2
    card_xs = [START + i * (card_w + GAP) for i in range(5)]

    _type42_buf = ""
    _secret_seq = "all_the_secrets_of_the_world"
    _secret_buf = ""
    _confirm_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 52, 160, 44)

    # Background lobby for update notifications (non-blocking, best-effort)
    _home_lobby   = _make_lobby(_net.load_userdata(), timeout=2)
    _home_banners = []   # [[text, frames_remaining], ...]

    def _mode_confirm():
        if selected == 0:   return ('1p', difficulties[difficulty_idx])
        elif selected == 1: return '2p'
        elif selected == 2: return 'survival_2p' if survival_players else 'survival_1p'
        elif selected == 3: return 'online'
        else:               return 'seasonal_shop'

    while True:
        clock.tick(FPS)
        preview_t = (preview_t + 0.02) % 1.0
        _ev_mode_ev = get_active_event()
        _ev_mode    = _ev_mode_ev.get("special_mode") if _ev_mode_ev else None
        _ev_label   = _ev_mode_ev.get("special_mode_label", "Event Mode") if _ev_mode_ev and _ev_mode else None
        _ev_btn_rect = pygame.Rect(WIDTH // 2 - 175, HEIGHT - 92, 350, 38) if _ev_mode else None

        # Poll server for update notifications
        if _home_lobby and _home_lobby.connected:
            _home_lobby.poll()
            for _note in _home_lobby.update_notify:
                _home_banners.append([_note, FPS * 8])
            _home_lobby.update_notify.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if _home_lobby: _home_lobby.close()
                pygame.quit(); sys.exit()
            # Touch / click: tap a card to select it; tap confirm to enter
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                _mp = (int(event.x * WIDTH), int(event.y * HEIGHT)) if event.type == pygame.FINGERDOWN else event.pos
                if _confirm_rect.collidepoint(_mp):
                    if _home_lobby: _home_lobby.close()
                    return _mode_confirm()
                for _ci, _cx in enumerate(card_xs):
                    if pygame.Rect(_cx, 140, card_w, card_h).collidepoint(_mp):
                        selected = _ci
                        break
                # Difficulty ▲/▼ touch (drawn at list_x, list_y area)
                if selected == 0 and len(card_xs) > 0:
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
                    selected = (selected - 1) % 5
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % 5
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
                    if _home_lobby: _home_lobby.close()
                    return _mode_confirm()
                if event.key == pygame.K_e and _ev_mode:
                    if _home_lobby: _home_lobby.close()
                    return _ev_mode

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN) and _ev_btn_rect:
                _mp2 = (int(event.x * WIDTH), int(event.y * HEIGHT)) if event.type == pygame.FINGERDOWN else event.pos
                if _ev_btn_rect.collidepoint(_mp2):
                    if _home_lobby: _home_lobby.close()
                    return _ev_mode

        screen.fill(DARK)
        draw_seasonal_decos(screen)
        title = font_large.render("STICKMAN FIGHTER", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 58))

        # Show active event name if any
        _active_ev = get_active_event()
        if _active_ev:
            _sm, _sd = _active_ev['start']
            _em, _ed = _active_ev['end']
            import calendar
            _smn = calendar.month_abbr[_sm]
            _emn = calendar.month_abbr[_em]
            if (_sm, _sd) == (_em, _ed):
                _date_str = f"{_smn} {_sd}"
            else:
                _date_str = f"{_smn} {_sd} – {_emn} {_ed}"
            _ev_lbl = font_tiny.render(
                f"{_active_ev['name']} is here only during {_date_str}!", True, (255, 200, 0))
            screen.blit(_ev_lbl, (WIDTH//2 - _ev_lbl.get_width()//2, 102))

        cards = [
            (card_xs[0], "1 PLAYER",  "vs CPU",     BLUE),
            (card_xs[1], "2 PLAYERS", "local",       ORANGE),
            (card_xs[2], "SURVIVAL",  "endless",     GREEN),
            (card_xs[3], "ONLINE",    "internet",    CYAN),
            (card_xs[4], "SHOP",      "seasonal",    (255, 200, 0)),
        ]
        for ci, (cx, top, sub, col) in enumerate(cards):
            border = WHITE if ci == selected else GRAY
            bg_col = (50, 45, 10) if ci == 4 else (50, 50, 50)
            pygame.draw.rect(screen, bg_col, (cx, 140, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, border,  (cx, 140, card_w, card_h), 3, border_radius=12)
            lbl = font_medium.render(top, True, col)
            screen.blit(lbl, (cx + card_w//2 - lbl.get_width()//2, 150))
            sl = font_small.render(sub, True, GRAY)
            screen.blit(sl, (cx + card_w//2 - sl.get_width()//2, 190))
            if ci == 4:
                # Draw coin symbol instead of stickman
                pygame.draw.circle(screen, (255, 200, 0), (cx + card_w//2, 140 + card_h - 55), 28)
                pygame.draw.circle(screen, (200, 150, 0), (cx + card_w//2, 140 + card_h - 55), 28, 3)
                _clbl = font_medium.render("$", True, (120, 90, 0))
                screen.blit(_clbl, (cx + card_w//2 - _clbl.get_width()//2, 140 + card_h - 55 - _clbl.get_height()//2))
            else:
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

        # Seasonal event special mode button
        if _ev_btn_rect and _ev_label:
            _pulse = int(abs(math.sin(pygame.time.get_ticks() / 600.0)) * 40)
            _ev_bg  = (20 + _pulse, 80 + _pulse, 20 + _pulse)
            _ev_brd = (80 + _pulse, 220, 80 + _pulse)
            pygame.draw.rect(screen, _ev_bg,  _ev_btn_rect, border_radius=10)
            pygame.draw.rect(screen, _ev_brd, _ev_btn_rect, 2, border_radius=10)
            _ev_txt = font_small.render(f"★ {_ev_label}  [E]", True, (180, 255, 120))
            screen.blit(_ev_txt, (_ev_btn_rect.centerx - _ev_txt.get_width() // 2,
                                  _ev_btn_rect.centery - _ev_txt.get_height() // 2))

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

        # Update notification banners (same style as online menu)
        _home_banners[:] = [[n, t] for n, t in _home_banners if t > 0]
        for _bi, (_bn, _bt) in enumerate(_home_banners):
            _bsurf = pygame.Surface((WIDTH - 40, 36), pygame.SRCALPHA)
            _bsurf.fill((20, 60, 20, min(200, _bt * 6)))
            _btxt  = font_small.render(f"Update: {_bn}", True, (120, 255, 120))
            _bsurf.blit(_btxt, (10, 6))
            screen.blit(_bsurf, (20, 120 + _bi * 42))
            _home_banners[_bi][1] -= 1

        pygame.display.flip()

# ---------------------------------------------------------------------------
# Character select screen
# ---------------------------------------------------------------------------

def character_select(vs_ai=False, unlocked=None, unlock_hints=None, unlock_progress=None,
                     char_filter=None, select_title=None):
    """Returns (p1_idx, p2_idx). P2 is random if vs_ai.
    char_filter: optional set of character names — only those characters are shown.
    Returned indices are always into the global CHARACTERS list.
    """
    # Build eartha variant lookup (Original + 4 seasonal, excluded from main grid)
    _eartha_variant_names   = ["Eartha", "Spring Eartha", "Summer Eartha", "Autumn Eartha", "Winter Eartha"]
    _eartha_variant_labels  = ["Original", "Spring", "Summer", "Autumn", "Winter"]
    _eartha_variant_indices = []
    for _evn in _eartha_variant_names:
        for _evi2, _evc2 in enumerate(CHARACTERS):
            if _evc2["name"] == _evn:
                _eartha_variant_indices.append(_evi2)
                break

    if char_filter is not None:
        _cf_pairs = [(i, c) for i, c in enumerate(CHARACTERS)
                     if c["name"] in char_filter and not c.get("eartha_variant")]
        _CHARS    = [c for _, c in _cf_pairs]
        _orig_idx = [i for i, _ in _cf_pairs]
        COLS      = min(4, max(1, len(_CHARS)))
    else:
        _cf_pairs = [(i, c) for i, c in enumerate(CHARACTERS) if not c.get("eartha_variant")]
        _CHARS    = [c for _, c in _cf_pairs]
        _orig_idx = [i for i, _ in _cf_pairs]
        COLS      = 7
    if unlocked is None:
        unlocked = {ch["name"] for ch in _CHARS}
    if unlock_hints is None:
        unlock_hints = {}
    if unlock_progress is None:
        unlock_progress = {}
    n     = len(_CHARS)
    ROWS  = (n + COLS - 1) // COLS
    VISIBLE_ROWS = 12   # how many card rows show at once

    # Grid occupies left ~60% of screen
    GX, GY   = 8,  68
    GW, GH   = 540, HEIGHT - GY - 28
    CW       = GW // COLS
    CH       = GH // VISIBLE_ROWS   # card height based on viewport, not total rows

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
    scroll_top = 0  # first visible row
    p1_ev = 0   # eartha variant index (0 = Original Eartha)
    p2_ev = 0

    def clip_scroll(idx):
        nonlocal scroll_top
        row = idx // COLS
        if row < scroll_top:
            scroll_top = row
        elif row >= scroll_top + VISIBLE_ROWS:
            scroll_top = row - VISIBLE_ROWS + 1

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
                # Tap scroll buttons above/below grid
                _stbh = 26
                if pygame.Rect(GX, GY - _stbh - 2, GW, _stbh).collidepoint(_tp) and scroll_top > 0:
                    scroll_top -= 1
                if pygame.Rect(GX, GY + GH + 2, GW, _stbh).collidepoint(_tp) and scroll_top + VISIBLE_ROWS < ROWS:
                    scroll_top += 1
                # Tap inside the character grid
                if GX <= _tx < GX + GW and GY <= _ty < GY + GH:
                    _col = (_tx - GX) // CW
                    _row = (_ty - GY) // CH + scroll_top
                    _ni  = min(_row * COLS + _col, n - 1)
                    if not p1_ready:
                        p1_idx = _ni; clip_scroll(p1_idx)
                    elif not vs_ai and not p2_ready:
                        p2_idx = _ni; clip_scroll(p2_idx)
                # Eartha variant tabs
                _td_idx = p2_idx if (p1_ready and not p2_ready) else p1_idx
                _td_ch  = _CHARS[_td_idx]
                if _td_ch["name"] == "Eartha" and _eartha_variant_indices:
                    _vp_ty = PY + PH - 132
                    _vp_tbw = (PW - 20) // len(_eartha_variant_indices)
                    for _vti in range(len(_eartha_variant_indices)):
                        _vtx = PX + 10 + _vti * _vp_tbw
                        if pygame.Rect(_vtx+1, _vp_ty+1, _vp_tbw-2, 28).collidepoint(_tp):
                            if not p1_ready:
                                p1_ev = _vti
                            elif not vs_ai and not p2_ready:
                                p2_ev = _vti
                # Tap READY button (drawn at bottom-right of detail panel)
                _ready_rect = pygame.Rect(PX, PY + PH - 52, PW, 44)
                if _ready_rect.collidepoint(_tp):
                    if not p1_ready:
                        if _CHARS[p1_idx]["name"] in unlocked:
                            _ev_ok_t = True
                            if _CHARS[p1_idx]["name"] == "Eartha" and _eartha_variant_indices:
                                _vnt = CHARACTERS[_eartha_variant_indices[p1_ev]]["name"]
                                if _vnt not in unlocked:
                                    _ev_ok_t = False
                            if _ev_ok_t:
                                p1_ready = True
                                if vs_ai:
                                    _ul = [i for i, c in enumerate(_CHARS) if c["name"] in unlocked]
                                    p2_idx = random.choice(_ul) if _ul else random.randint(0, n - 1)
                    elif not vs_ai and not p2_ready:
                        if _CHARS[p2_idx]["name"] in unlocked:
                            _ev_ok_t2 = True
                            if _CHARS[p2_idx]["name"] == "Eartha" and _eartha_variant_indices:
                                _vnt2 = CHARACTERS[_eartha_variant_indices[p2_ev]]["name"]
                                if _vnt2 not in unlocked:
                                    _ev_ok_t2 = False
                            if _ev_ok_t2:
                                p2_ready = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None
                # P1 navigation (WASD or arrows while P1 not ready)
                if not p1_ready:
                    if event.key in (pygame.K_a, pygame.K_LEFT):  p1_idx = move(p1_idx, 0, -1); clip_scroll(p1_idx); p1_ev = 0
                    if event.key in (pygame.K_d, pygame.K_RIGHT): p1_idx = move(p1_idx, 0,  1); clip_scroll(p1_idx); p1_ev = 0
                    if event.key in (pygame.K_w, pygame.K_UP):    p1_idx = move(p1_idx, -1, 0); clip_scroll(p1_idx); p1_ev = 0
                    if event.key in (pygame.K_s, pygame.K_DOWN):  p1_idx = move(p1_idx,  1, 0); clip_scroll(p1_idx); p1_ev = 0
                    if _CHARS[p1_idx]["name"] == "Eartha" and _eartha_variant_indices:
                        if event.key == pygame.K_e:
                            p1_ev = (p1_ev + 1) % len(_eartha_variant_indices)
                        elif event.key == pygame.K_q:
                            p1_ev = (p1_ev - 1) % len(_eartha_variant_indices)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
                        if _CHARS[p1_idx]["name"] not in unlocked:
                            pass  # locked — do nothing
                        else:
                            _ev_ok = True
                            if _CHARS[p1_idx]["name"] == "Eartha" and _eartha_variant_indices:
                                _vn = CHARACTERS[_eartha_variant_indices[p1_ev]]["name"]
                                if _vn not in unlocked:
                                    _ev_ok = False
                            if _ev_ok:
                                p1_ready = True
                                if vs_ai:
                                    _ul = [i for i, c in enumerate(_CHARS) if c["name"] in unlocked]
                                    p2_idx = random.choice(_ul) if _ul else random.randint(0, n - 1)
                # P2 navigation (arrows only, after P1 locked in)
                elif not vs_ai and not p2_ready:
                    if event.key == pygame.K_LEFT:  p2_idx = move(p2_idx, 0, -1); clip_scroll(p2_idx); p2_ev = 0
                    if event.key == pygame.K_RIGHT: p2_idx = move(p2_idx, 0,  1); clip_scroll(p2_idx); p2_ev = 0
                    if event.key == pygame.K_UP:    p2_idx = move(p2_idx, -1, 0); clip_scroll(p2_idx); p2_ev = 0
                    if event.key == pygame.K_DOWN:  p2_idx = move(p2_idx,  1, 0); clip_scroll(p2_idx); p2_ev = 0
                    if _CHARS[p2_idx]["name"] == "Eartha" and _eartha_variant_indices:
                        if event.key == pygame.K_l:
                            p2_ev = (p2_ev + 1) % len(_eartha_variant_indices)
                        elif event.key == pygame.K_j:
                            p2_ev = (p2_ev - 1) % len(_eartha_variant_indices)
                    if event.key in (pygame.K_RETURN, pygame.K_k):
                        if _CHARS[p2_idx]["name"] in unlocked:
                            _ev_ok2 = True
                            if _CHARS[p2_idx]["name"] == "Eartha" and _eartha_variant_indices:
                                _vn2 = CHARACTERS[_eartha_variant_indices[p2_ev]]["name"]
                                if _vn2 not in unlocked:
                                    _ev_ok2 = False
                            if _ev_ok2:
                                p2_ready = True

        if p1_ready and p2_ready:
            _r1 = _orig_idx[p1_idx]
            _r2 = _orig_idx[p2_idx]
            if _CHARS[p1_idx]["name"] == "Eartha" and _eartha_variant_indices:
                _r1 = _eartha_variant_indices[p1_ev]
            if not vs_ai and _CHARS[p2_idx]["name"] == "Eartha" and _eartha_variant_indices:
                _r2 = _eartha_variant_indices[p2_ev]
            return _r1, _r2

        # Whose detail to show: the active picker
        detail_idx = p2_idx if (p1_ready and not p2_ready) else p1_idx
        detail_ch  = _CHARS[detail_idx]
        active_col = ORANGE if (p1_ready and not p2_ready) else BLUE
        _active_ev = p2_ev if (p1_ready and not p2_ready) else p1_ev
        _detail_display = detail_ch
        if detail_ch["name"] == "Eartha" and detail_ch["name"] in unlocked and _eartha_variant_indices:
            _detail_display = CHARACTERS[_eartha_variant_indices[_active_ev]]

        # ── Background ──────────────────────────────────────────────────────
        screen.fill((18, 18, 28))
        draw_seasonal_decos(screen)

        # Title bar
        pygame.draw.rect(screen, (30, 30, 48), (0, 0, WIDTH, GY - 2))
        _title_str = select_title if select_title else "SELECT YOUR FIGHTER"
        title = font_medium.render(_title_str, True, YELLOW)
        screen.blit(title, (GX, 10))
        if not vs_ai:
            phase = "P1 choosing" if not p1_ready else "P2 choosing"
            phase_col = BLUE if not p1_ready else ORANGE
            ps = font_small.render(phase, True, phase_col)
            screen.blit(ps, (WIDTH - ps.get_width() - 10, 12))

        # ── Character grid ───────────────────────────────────────────────────
        for i, ch in enumerate(_CHARS):
            r, c    = divmod(i, COLS)
            if r < scroll_top or r >= scroll_top + VISIBLE_ROWS:
                continue
            cx      = GX + c * CW
            cy      = GY + (r - scroll_top) * CH
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

        # Scroll buttons — 26px tap targets above and below the grid
        _scroll_btn_h = 26
        _scroll_up_rect   = pygame.Rect(GX, GY - _scroll_btn_h - 2, GW, _scroll_btn_h)
        _scroll_down_rect = pygame.Rect(GX, GY + GH + 2, GW, _scroll_btn_h)
        mid_x = GX + GW // 2
        if scroll_top > 0:
            pygame.draw.rect(screen, (45, 45, 65), _scroll_up_rect, border_radius=4)
            pygame.draw.polygon(screen, (180, 180, 220),
                [(mid_x, _scroll_up_rect.top + 6),
                 (mid_x - 10, _scroll_up_rect.bottom - 6),
                 (mid_x + 10, _scroll_up_rect.bottom - 6)])
        if scroll_top + VISIBLE_ROWS < ROWS:
            pygame.draw.rect(screen, (45, 45, 65), _scroll_down_rect, border_radius=4)
            pygame.draw.polygon(screen, (180, 180, 220),
                [(mid_x, _scroll_down_rect.bottom - 6),
                 (mid_x - 10, _scroll_down_rect.top + 6),
                 (mid_x + 10, _scroll_down_rect.top + 6)])

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
            draw_stickman(screen, PX + PW//2, sm_y, _detail_display["color"], 1, 'walk', preview_t, scale=1.15,
                          char_name=_detail_display["name"])

            # Character name
            nm_big = font_medium.render(_detail_display["name"], True, _detail_display["color"])
            screen.blit(nm_big, (PX + PW//2 - nm_big.get_width()//2, PY + 8))

        if not detail_locked:
            # Description (word-wrap)
            words, line, desc_lines = _detail_display["desc"].split(), "", []
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
                ("HP",    _detail_display["max_hp"],              400, (60,  210,  80)),
                ("SPD",   _detail_display["speed"],                10, (80,  170, 255)),
                ("PUNCH", _detail_display["punch_dmg"],            30, (255, 120,  50)),
                ("KICK",  _detail_display["kick_dmg"],             30, (255,  60, 180)),
                ("BLOCK", _detail_display.get("block", 5),         10, (200, 200,  60)),
            ]):
                by  = bar_y + si * bar_gap
                lbs = font_small.render(lbl, True, (220, 220, 220))
                screen.blit(lbs, (bar_x, by - 1))
                bx2 = bar_x + 58
                bw2 = bar_bw - 80
                pygame.draw.rect(screen, (50, 50, 65), (bx2, by, bw2, bar_h), border_radius=3)
                fw  = int(bw2 * min(1.0, val / mx))
                if fw > 0:
                    pygame.draw.rect(screen, col, (bx2, by, fw, bar_h), border_radius=3)
                pygame.draw.rect(screen, (90, 90, 110), (bx2, by, bw2, bar_h), 1, border_radius=3)
                vs2 = font_small.render(str(val), True, col)
                screen.blit(vs2, (bx2 + bw2 + 6, by - 1))

            # Badges row
            badge_y = bar_y + 5 * bar_gap + 6
            badges  = []
            if _detail_display.get("double_jump"):    badges.append(("2x JUMP",      CYAN))
            if _detail_display.get("giant"):          badges.append(("GIANT",         GREEN))
            if _detail_display.get("tiny"):           badges.append(("TINY",          (220, 200, 180)))
            if _detail_display.get("phase"):          badges.append(("PHASES WALLS",  (200, 200, 255)))
            if _detail_display.get("vampire"):        badges.append(("VAMPIRE",       (200, 0, 80)))
            if _detail_display.get("anti_gravity"):   badges.append(("ANTI-GRAVITY",  (180, 220, 255)))
            if _detail_display.get("wall_cling"):     badges.append(("WALL CLING",    ORANGE))
            if _detail_display.get("regen"):          badges.append(("REGEN",         (120, 255, 120)))
            if _detail_display.get("fire_punch"):     badges.append(("FIRE PUNCH",    (255, 100, 20)))
            if _detail_display.get("freeze_kick"):    badges.append(("FREEZE KICK",   (120, 200, 255)))
            if _detail_display.get("shock_punch"):    badges.append(("SHOCK PUNCH",   YELLOW))
            if _detail_display.get("magnet"):         badges.append(("MAGNET",        PURPLE))
            if _detail_display.get("teleport_kick"):  badges.append(("TELEPORT KICK", (220, 80, 255)))
            if _detail_display.get("random_stats"):   badges.append(("RANDOM STATS",  GRAY))
            if _detail_display.get("shoot_kick"):     badges.append(("SHOOTS BALLS",  (60, 200, 80)))
            if _detail_display.get("bazooka_kick"):   badges.append(("BAZOOKA",       (220, 60, 60)))
            if _detail_display.get("bounce_kick"):    badges.append(("BOUNCE BALL",   (255, 80, 200)))
            if _detail_display.get("size_kick"):      badges.append(("SIZE SHIFT",    (80, 200, 220)))
            if _detail_display.get("grapple_kick"):   badges.append(("SNAKE HOOK",    (40, 200, 60)))
            if _detail_display.get("pumpkin_kick"):   badges.append(("PUMPKIN BOMB",  (215, 118, 0)))
            if _detail_display.get("contact_dmg"):    badges.append(("POISON TOUCH",  (100, 220, 60)))
            if _detail_display.get("hammer_punch"):   badges.append(("HAMMER SMASH",  (160, 120, 60)))
            if _detail_display.get("berserker"):      badges.append(("BERSERKER",      (220, 60, 30)))
            if _detail_display.get("bounce_punch"):   badges.append(("MAGIC ORB",      (160, 80, 255)))
            if _detail_display.get("slam_kick"):      badges.append(("SLAM KICK",      (220, 100, 40)))
            if _detail_display.get("confuse_kick"):   badges.append(("CONFUSE KICK",   (255, 60, 120)))
            if _detail_display.get("speedster"):      badges.append(("SPEED TRAIL",    (255, 220, 0)))
            if _detail_display.get("slow_fall"):      badges.append(("SLOW FALL",      (255, 240, 180)))
            if _detail_display.get("stealth_punch"):  badges.append(("STEALTH",        (200, 200, 220)))
            if _detail_display.get("wide_punch"):     badges.append(("WIDE REACH",     (160, 80, 30)))
            if _detail_display.get("reflect_block"):  badges.append(("REFLECT",        (80, 200, 80)))
            if _detail_display.get("laser_eyes"):     badges.append(("LASER EYES",     (255, 60,  0)))
            if _detail_display.get("whip_punch"):     badges.append(("WHIP",           (160, 90, 20)))
            if _detail_display.get("always_crit"):    badges.append(("ALWAYS CRIT",    (255, 215, 0)))
            if _detail_display.get("chameleon"):      badges.append(("CAMOUFLAGE",     (60, 180, 80)))
            if _detail_display.get("ink_kick"):       badges.append(("INK CLONE",      (20,  20, 40)))
            if _detail_display.get("ghost_float"):    badges.append(("GHOST FLOAT",    (210, 210, 255)))
            # new characters
            if _detail_display.get("kitsune_barrage"): badges.append(("九 BARRAGE",    (255, 160,  0)))
            if _detail_display.get("freeze_laser"):    badges.append(("FREEZE GAZE",   (0,  210, 255)))
            if _detail_display.get("creator_kick"):    badges.append(("CREATES WALLS", (220, 180, 40)))
            if _detail_display.get("disorientated"):   badges.append(("ALL REVERSED",  (200,  80, 255)))
            if _detail_display.get("immune"):          badges.append(("STATUS IMMUNE", (210, 210, 180)))
            if _detail_display.get("water_kick"):      badges.append(("WATER BALL",    (0,  180, 240)))
            if _detail_display.get("momentum"):        badges.append(("MOMENTUM",      (0,  160, 220)))
            if _detail_display.get("smoke_trail"):     badges.append(("SMOKE TRAIL",   (180, 180, 220)))
            if _detail_display.get("snake"):           badges.append(("SNAKE BODY",    (20, 200, 60)))
            if _detail_display.get("always_berserk"):  badges.append(("ALWAYS ENRAGED",(220, 50,  0)))
            if _detail_display.get("bee_punch"):       badges.append(("BEE SWARM",     (220,180,  0)))
            if _detail_display.get("plague_punch"):    badges.append(("PLAGUE",        (120,200, 80)))
            if _detail_display.get("undead"):          badges.append(("REVIVES ONCE",  (80,  40,120)))
            if _detail_display.get("chaos_timer"):     badges.append(("CHAOS MAGIC",   (200, 80,255)))
            if _detail_display.get("rapid_fire"):      badges.append(("RAPID PUNCH",   (255,160,  0)))
            if _detail_display.get("drain_kick"):      badges.append(("DRAIN KICK",    (160,  0,160)))
            if _detail_display.get("iron_fist"):       badges.append(("IRON FIST",     (180,180,200)))
            if _detail_display.get("toxic_aura"):      badges.append(("TOXIC AURA",    (60, 220, 60)))
            if _detail_display.get("time_freeze"):     badges.append(("TIME FREEZE",   (100,180,255)))
            if _detail_display.get("cycle_attack"):    badges.append(("CYCLE ATTACK",  (160,120,255)))
            if _detail_display.get("explode_death"):   badges.append(("DEATH EXPLODE", (255,100,  0)))
            if _detail_display.get("shrink_kick"):     badges.append(("SHRINK KICK",   (120,255,200)))
            if _detail_display.get("launch_kick"):     badges.append(("LAUNCH KICK",   (200,160,255)))
            if _detail_display.get("speed_steal"):     badges.append(("SPEED STEAL",   ( 60, 80, 60)))
            if _detail_display.get("reflect_proj"):    badges.append(("REFLECT PROJ",  (200,220,240)))
            if _detail_display.get("auto_fire"):       badges.append(("AUTO FIRE",     (255, 80,  0)))
            if _detail_display.get("thunder_punch"):   badges.append(("THUNDER",       (255,240, 80)))
            if _detail_display.get("auto_teleport"):   badges.append(("AUTO TELEPORT", ( 80,200,220)))
            if _detail_display.get("sticky_punch"):    badges.append(("STICKY PUNCH",  (200,180, 60)))
            # --- batch: missing mechanics ---
            if _detail_display.get("shock_kick"):      badges.append(("SHOCK KICK",    (255,240, 80)))
            if _detail_display.get("storm_punch"):     badges.append(("STORM PUNCH",   ( 80,120,255)))
            if _detail_display.get("magnet_punch"):    badges.append(("MAGNET PULL",   (160, 80,255)))
            if _detail_display.get("combo_punch"):     badges.append(("COMBO PUNCH",   ( 80,200,180)))
            if _detail_display.get("steal_kick"):      badges.append(("STEAL KICK",    ( 60, 60,100)))
            if _detail_display.get("cloned"):          badges.append(("CLONE",         (100,200,160)))
            if _detail_display.get("bomb_character"):  badges.append(("BOMB SPAWNER",  (200, 80, 20)))
            if _detail_display.get("halves_punch"):    badges.append(("HALVES HP",     (220, 80,220)))
            if _detail_display.get("godslayer"):       badges.append(("GODSLAYER",     (180, 20, 60)))
            if _detail_display.get("scroll_kick"):     badges.append(("SCROLL BOMB",   (180,150, 80)))
            if _detail_display.get("flash_kick"):      badges.append(("FLASH KICK",    (255,200,  0)))
            if _detail_display.get("portal_kick"):     badges.append(("PORTAL KICK",   ( 80,200,255)))
            if _detail_display.get("apple_kick"):      badges.append(("APPLE RAIN",    (120, 80,200)))
            if _detail_display.get("totem_kick"):      badges.append(("TOTEM RAIN",    (190,110, 30)))
            if _detail_display.get("remote_kick"):     badges.append(("REMOTE BOMB",   (220, 40,  0)))
            if _detail_display.get("prime_dmg"):       badges.append(("PRIME DAMAGE",  ( 60,180,255)))
            if _detail_display.get("lucky_strike"):    badges.append(("LUCKY STRIKE",  (255,215,  0)))
            if _detail_display.get("drain_punch"):     badges.append(("DRAIN PUNCH",   ( 20,  0, 60)))
            if _detail_display.get("sleep_punch"):     badges.append(("SLEEP PUNCH",   (220,190,120)))
            if _detail_display.get("reaper_kick"):     badges.append(("REAPER KICK",   ( 40, 40, 40)))
            if _detail_display.get("chainsaw"):        badges.append(("CHAINSAW",      (200, 60, 30)))
            if _detail_display.get("crush_punch"):     badges.append(("BLOCK BREAK",   (140, 80,200)))
            if _detail_display.get("quake_land"):      badges.append(("QUAKE LAND",    (160,120, 60)))
            if _detail_display.get("seven_punch"):     badges.append(("777 PUNCH",     (255,215,  0)))
            if _detail_display.get("void_immune"):     badges.append(("VOID IMMUNE",   ( 30,  0, 60)))
            if _detail_display.get("screentime"):      badges.append(("TIME WARP",     (100,200,255)))
            # --- new characters batch ---
            if _detail_display.get("swap_kick"):       badges.append(("SWAP KICK",     (200,120, 60)))
            if _detail_display.get("rage_build"):      badges.append(("RAGE BUILD",    (180, 60, 60)))
            if _detail_display.get("grab_punch"):      badges.append(("GRAB PUNCH",    ( 80,140,200)))
            if _detail_display.get("confuse_punch"):   badges.append(("CONFUSE PUNCH", (200, 80,200)))
            if _detail_display.get("wild_attack"):     badges.append(("WILD ATTACK",   (255,180,  0)))
            if _detail_display.get("stone_skin"):      badges.append(("ARMOR SKIN",    (150,150,170)))
            if _detail_display.get("siphon_leech"):    badges.append(("SIPHON",        (160, 40,160)))
            if _detail_display.get("slow_punch"):      badges.append(("SLOW PUNCH",    (100,200,240)))
            if _detail_display.get("copy_punch"):      badges.append(("COPY PUNCH",    (180,230,255)))
            if _detail_display.get("hp_swap"):         badges.append(("HP SWAP",       ( 80, 40,200)))
            if _detail_display.get("rainbow_poop"):    badges.append(("POOP POWERUPS", (255,100,180)))
            if _detail_display.get("venom_kick"):      badges.append(("VENOM KICK",    ( 60,180, 40)))
            if _detail_display.get("jetpack"):         badges.append(("JETPACK",       (200,100,255)))
            if _detail_display.get("chomp"):           badges.append(("CHOMP",         (255,220,  0)))
            if _detail_display.get("chicken_banana"):  badges.append(("RAM CHARGE",    (255,180,  0)))
            if _detail_display.get("soul_master"):     badges.append(("SOUL HOP",      ( 80,  0,160)))
            if _detail_display.get("copycat"):         badges.append(("COPYCAT",       (180,180,180)))
            if _detail_display.get("orb_shooter"):     badges.append(("CHARGE ORB",    ( 80,160,255)))
            if _detail_display.get("glitch_strike"):   badges.append(("GLITCH HIT",    (  0,255,180)))
            if _detail_display.get("death_defyer"):    badges.append(("DEATH DEFYER",  (200,230,255)))
            if _detail_display.get("bubble_kick"):     badges.append(("BUBBLE KICK",   ( 80,200,160)))
            # --- mechanics without badges yet ---
            if _detail_display.get("shade"):           badges.append(("SHADE",         ( 80,  0,120)))
            if _detail_display.get("shock_aura"):      badges.append(("SHOCK AURA",    (240,230, 60)))
            if _detail_display.get("mirage"):          badges.append(("35% DODGE",     (160,140,220)))
            if _detail_display.get("quake_punch"):     badges.append(("QUAKE PUNCH",   (160,120, 60)))
            if _detail_display.get("feedback"):        badges.append(("FEEDBACK",      ( 60,200,175)))
            if _detail_display.get("growing_dmg"):     badges.append(("ESCALATES",     (200,145,  0)))
            if _detail_display.get("pacifist"):        badges.append(("REFLECTS 50%",  (235,255,235)))
            if _detail_display.get("execute"):         badges.append(("EXECUTE",       (180, 20, 40)))
            if _detail_display.get("voodoo"):          badges.append(("VOODOO",        (120,  0,200)))
            if _detail_display.get("desperation_speed"): badges.append(("DESPERATION", (220, 40, 40)))
            if _detail_display.get("crazy_teleport"):  badges.append(("1S TELEPORT",  (255, 50,220)))
            if _detail_display.get("giant_killer"):    badges.append(("GIANT KILLER",  ( 80,180,220)))
            if _detail_display.get("speed_stack"):     badges.append(("SPEED STACK",   (255,140,  0)))
            if _detail_display.get("all_or_nothing"):  badges.append(("ALL OR NOTHING",(200, 80,200)))
            if _detail_display.get("long_range"):      badges.append(("LONG RANGE 3×", (180,150, 80)))
            if _detail_display.get("stillness_regen"): badges.append(("STILL = HEAL",  (160,200,130)))
            if _detail_display.get("chef"):            badges.append(("BAKES POWERUP",(255,200, 80)))
            if _detail_display.get("backstab"):        badges.append(("BACKSTAB 3×",  ( 40, 30, 60)))
            if _detail_display.get("rainbow_snake"):   badges.append(("FOREVER POWER", (200,100,255)))
            if _detail_display.get("taipan_punch"):    badges.append(("SUPPRESS PUNCH",(120, 80, 40)))
            if _detail_display.get("cobra_orb"):       badges.append(("POISON ORB",    ( 30,100, 30)))
            if _detail_display.get("giant_bug_kick"):  badges.append(("GIANT BUG",     ( 60,160, 60)))
            if _detail_display.get("black_hole_kick"): badges.append(("BLACK HOLE",    ( 80,  0,180)))
            if _detail_display.get("bug_spawner_kick"):badges.append(("BUG SPAWNER",   (255,200,  0)))
            if _detail_display.get("widow_kick"):      badges.append(("WALL BUGS",     ( 10, 10, 10)))
            if _detail_display.get("ai_clones"):       badges.append(("5 CLONES",      (  0,220,200)))
            if _detail_display.get("auto_forcefield"): badges.append(("FORCEFIELD",    (100,180,255)))
            if _detail_display.get("possess_kick"):    badges.append(("POSSESS",       (180, 80,255)))
            if _detail_display.get("armor_proj"):      badges.append(("PROJ IMMUNE",   (160,160,180)))
            if _detail_display.get("deflect_proj"):    badges.append(("DEFLECT",       (100,220,255)))
            if _detail_display.get("unhittable"):      badges.append(("60% DODGE",     (240,240,100)))
            if _detail_display.get("mega_unhittable"): badges.append(("99.9% DODGE",   (255,255,150)))
            # 11 new characters
            if _detail_display.get("note_kick"):       badges.append(("NOTE KICK",     (180,100,200)))
            if _detail_display.get("cleave_kick"):     badges.append(("CLEAVE KICK",   (140, 60, 40)))
            if _detail_display.get("heavy"):           badges.append(("HEAVY",         (120,110,100)))
            if _detail_display.get("money_hit"):       badges.append(("MONEY HIT",     (220,180,  0)))
            if _detail_display.get("glass_jaw"):       badges.append(("GLASS JAW",     (200,160,200)))
            if _detail_display.get("drain_aura"):      badges.append(("DRAIN AURA",    (160, 20, 80)))
            if _detail_display.get("lance_punch"):     badges.append(("LANCE PUNCH",   (200,160, 60)))
            if _detail_display.get("absorb_hit"):      badges.append(("ABSORB HIT",    (100,200,160)))
            if _detail_display.get("hex_kick"):        badges.append(("HEX KICK",      ( 80, 30,120)))
            if _detail_display.get("gamble_kick"):     badges.append(("GAMBLE KICK",   (100,200, 80)))
            if _detail_display.get("auto_counter"):    badges.append(("AUTO COUNTER",  (180,100, 60)))
            if _detail_display.get("fire_aura"):       badges.append(("FIRE AURA",     (220, 90, 20)))
            if _detail_display.get("colossus"):        badges.append(("COLOSSUS",      (100,130, 70)))
            if _detail_display.get("stomp_punch"):     badges.append(("STOMP PUNCH",   ( 60, 70,180)))
            if _detail_display.get("spike_body"):      badges.append(("SPIKE BODY",    ( 80,160, 60)))
            if _detail_display.get("anchor_body"):     badges.append(("ANCHOR",        ( 60, 60,100)))
            if _detail_display.get("sleep_body"):      badges.append(("SLEEP AURA",    (120, 80,180)))
            if _detail_display.get("berserk_low"):     badges.append(("BERSERK MODE",  (200, 40, 20)))
            if _detail_display.get("twin_strike"):     badges.append(("TWIN STRIKE",   ( 80,180,200)))
            if _detail_display.get("sap_kick"):        badges.append(("SAP KICK",      (120, 60, 30)))
            if _detail_display.get("mimic_stats"):     badges.append(("MIMIC STATS",   (150,150,160)))
            if _detail_display.get("boomerang_kick"):  badges.append(("BOOMERANG",     (200,110, 30)))
            if _detail_display.get("parry_strike"):    badges.append(("PARRY STRIKE",  ( 60,120,200)))
            if _detail_display.get("combat_regen"):    badges.append(("COMBAT REGEN",  (100,200,120)))
            if _detail_display.get("iron_block"):      badges.append(("IRON BLOCK",    ( 80, 80,100)))
            if _detail_display.get("pierce_kick"):     badges.append(("PIERCE KICK",   (160,160,180)))
            if _detail_display.get("rage_stack"):      badges.append(("RAGE STACK",    (180, 50, 50)))
            if _detail_display.get("phoenix_revive"):  badges.append(("PHOENIX",       (220,120, 20)))
            if _detail_display.get("chain_hits"):      badges.append(("CHAIN HITS",    ( 60,160,160)))
            if _detail_display.get("block_break"):     badges.append(("BLOCK BREAK",   (100, 80,160)))
            if _detail_display.get("titan_grip"):      badges.append(("TITAN GRIP",    ( 90, 60,130)))
            if _detail_display.get("overload"):        badges.append(("OVERLOAD",      (255, 80,220)))
            if _detail_display.get("glitch_char"):     badges.append(("GLITCH",        ( 60,255,120)))
            if _detail_display.get("nick_of_time"):    badges.append(("NICK OF TIME",  ( 60,200,255)))
            if _detail_display.get("buffer_char"):     badges.append(("BUFFER",        (100,220,100)))
            if _detail_display.get("cursed_drain"):    badges.append(("CURSED",        ( 80,  0, 80)))
            # --- batch 9 ---
            if _detail_display.get("moving_punch"):    badges.append(("DASH PUNCH",    (200, 60, 60)))
            if _detail_display.get("wind_kick"):       badges.append(("WIND KICK",     ( 80,160,230)))
            if _detail_display.get("phase_dodge"):     badges.append(("PHASE DODGE",   (140, 80,200)))
            if _detail_display.get("chaos_strike"):    badges.append(("CHAOS HIT",     (220, 80,220)))
            if _detail_display.get("rage_damage"):     badges.append(("LOW HP RAGE",   (200, 30, 20)))
            if _detail_display.get("thorn_block"):     badges.append(("THORNS",        ( 80,160, 60)))
            if _detail_display.get("oracle_dodge"):    badges.append(("ORACLE DODGE",  (160, 80,200)))
            if _detail_display.get("triple_slash"):    badges.append(("TRIPLE SLASH",  ( 30,120,170)))
            if _detail_display.get("first_strike"):    badges.append(("FIRST STRIKE",  (160, 80, 30)))
            if _detail_display.get("arcane_orb"):      badges.append(("ARCANE ORB",    (150, 60,220)))
            if _detail_display.get("bbboomerang_kick"):badges.append(("5 BOOMERANGS",  (220,140, 20)))
            if _detail_display.get("web_kick"):        badges.append(("WEB KICK",      (200,160, 40)))
            if _detail_display.get("spider_dodge"):    badges.append(("25% DODGE",     (180,130, 30)))
            if _detail_display.get("river_pull"):      badges.append(("RIVER PULL",    ( 30,160,120)))
            if _detail_display.get("shell_body"):      badges.append(("SHELL -25%",    ( 40,120, 80)))
            if _detail_display.get("poison_kick"):     badges.append(("POISON KICK",   ( 80,160, 40)))
            if _detail_display.get("flame_trail"):     badges.append(("FLAME TRAIL",   (220, 80, 10)))
            # --- seasonal / special characters ---
            if _detail_display.get("nian_breath"):     badges.append(("FIRE BREATH",   (220, 60, 20)))
            if _detail_display.get("saint_nix_coal"):  badges.append(("COAL CYCLE",    (200,  50,  50)))
            if _detail_display.get("scorpio_kick"):    badges.append(("FREEZE+POISON", ( 80, 160, 200)))
            if _detail_display.get("plant_kick"):      badges.append(("PLANT SPIKE",   ( 40, 180,  60)))
            if _detail_display.get("dementor_heal"):   badges.append(("TIMED HEAL",    (120, 100, 200)))
            if _detail_display.get("decay_punch"):     badges.append(("DECAY PUNCH",   (120, 100,  60)))
            if _detail_display.get("f13_dmg"):         badges.append(("×13 MULT",      ( 40,  40,  40)))
            if _detail_display.get("sniper_shot"):     badges.append(("SNIPER SHOT",   (180, 140,  60)))
            if _detail_display.get("map_kick"):        badges.append(("STAGE SWAP",    (180, 140,  80)))
            if _detail_display.get("bookzworm_books"): badges.append(("BOOK ORBIT",    ( 70, 145,  50)))
            if _detail_display.get("yellowstone_kick"):badges.append(("GEYSER KICK",   (118,  98,  72)))
            if _detail_display.get("jack_tank"):       badges.append(("PUMPKIN TANK",  (220, 110,  20)))
            if _detail_display.get("cornucopia_fruits"):badges.append(("FRUIT SHOT",   (180, 140,  55)))
            if _detail_display.get("ngs_dreidel"):     badges.append(("DREIDEL SPIN",  ( 40, 110, 210)))
            if _detail_display.get("smoochie_revivals"):badges.append(("5 REVIVALS",   (255, 100, 180)))
            if _detail_display.get("baddit"):          badges.append(("POWERUP SWAP",  (240, 220, 200)))
            if _detail_display.get("clover_kick"):     badges.append(("SNAKE KICK",    ( 40, 200,  80)))
            if _detail_display.get("clover_luck"):     badges.append(("IMMUNE BAD",    (150, 220, 100)))
            if _detail_display.get("eartha_grow"):     badges.append(("GROWS/SEC",     (120,  80,  40)))
            if _detail_display.get("tombstone_reflect"):badges.append(("99.9% REFLECT", (155, 150, 140)))
            if _detail_display.get("absorb_block"):    badges.append(("HEAL BLOCK",    ( 70, 160, 100)))
            if _detail_display.get("overdrive"):       badges.append(("OVERDRIVE",     (255, 130,   0)))
            if _detail_display.get("crit_only"):       badges.append(("CRIT ONLY",     ( 75,  50,  25)))
            if _detail_display.get("phantom_strike"):  badges.append(("PHANTOM STRIKE", ( 50,  50, 160)))
            if _detail_display.get("mine_kick"):       badges.append(("GROUND MINE",    (110,  85,  40)))
            if _detail_display.get("juggernaut"):      badges.append(("NO KNOCKBACK",   (180,  60,  20)))
            if _detail_display.get("revenant"):        badges.append(("2× REVIVE",      (160,  90, 200)))
            if _detail_display.get("hypno_kick"):      badges.append(("HYPNO KICK",     (140,  60, 200)))
            if _detail_display.get("blink_kick"):      badges.append(("BLINK KICK",     ( 80, 220, 255)))
            if _detail_display.get("sand_punch"):      badges.append(("SAND CLOUD",     (210, 170,  90)))
            if _detail_display.get("poltergeist_fling"):badges.append(("RANDOM FLING",  (200, 195, 230)))
            if _detail_display.get("armor_threshold"): badges.append(("40% ARMOR",     (130, 130, 145)))
            if _detail_display.get("marionette_kick"): badges.append(("PUPPET KICK",   (220, 110, 180)))
            if _detail_display.get("glacier_punch"):   badges.append(("SLOW PUNCH",    (170, 225, 255)))
            if _detail_display.get("wildfire"):        badges.append(("WILDFIRE",      (255,  80,  10)))
            if _detail_display.get("vex_debuff"):      badges.append(("VEX DEBUFF",    (160,  40, 200)))
            if _detail_display.get("stalwart_counter"):badges.append(("COUNTER HIT",   ( 80, 110, 160)))
            if _detail_display.get("mimic_move"):           badges.append(("MIMIC MOVE",     (160, 160, 160)))
            if _detail_display.get("flower_trail_poison"): badges.append(("FLOWER POISON",  (180, 240, 140)))
            if _detail_display.get("summer_wildfire"):     badges.append(("WILDFIRE SHOT",  (255,  90,  10)))
            if _detail_display.get("leaf_rain"):           badges.append(("LEAF RAIN",      (120, 180,  40)))
            if _detail_display.get("snow_aura"):           badges.append(("SNOW AURA",      (175, 215, 250)))
            bx_off = PX + 8
            for btxt, bcol in badges:
                bs = font_tiny.render(btxt, True, bcol)
                if bx_off + bs.get_width() + 10 > PX + PW - 4:
                    bx_off  = PX + 8
                    badge_y += 18
                pygame.draw.rect(screen, (40, 40, 60), (bx_off - 2, badge_y - 1, bs.get_width() + 8, 16), border_radius=3)
                screen.blit(bs, (bx_off + 2, badge_y))
                bx_off += bs.get_width() + 14

        # Eartha variant picker
        if detail_ch["name"] == "Eartha" and detail_ch["name"] in unlocked and _eartha_variant_indices:
            _vp_y   = PY + PH - 132
            _vp_lbl = font_tiny.render("VARIANT  (Q/E  or  J/L)", True, (160, 160, 185))
            screen.blit(_vp_lbl, (PX + PW//2 - _vp_lbl.get_width()//2, _vp_y - 16))
            _vp_bw = (PW - 20) // len(_eartha_variant_indices)
            for _vi3, _vlb3 in enumerate(_eartha_variant_labels):
                _vx3   = PX + 10 + _vi3 * _vp_bw
                _vc3   = CHARACTERS[_eartha_variant_indices[_vi3]]["color"]
                _vn3   = CHARACTERS[_eartha_variant_indices[_vi3]]["name"]
                _vlk3  = _vn3 not in unlocked
                _vsel3 = (_vi3 == _active_ev)
                _vbg3  = tuple(max(8, c // 5) for c in _vc3)
                pygame.draw.rect(screen, _vbg3, (_vx3+1, _vp_y+1, _vp_bw-2, 28), border_radius=4)
                _vbrd3 = _vc3 if _vsel3 else tuple(c // 2 for c in _vc3)
                _vbw3  = 2 if _vsel3 else 1
                pygame.draw.rect(screen, _vbrd3, (_vx3+1, _vp_y+1, _vp_bw-2, 28), _vbw3, border_radius=4)
                _vtc3  = (90, 90, 90) if _vlk3 else (WHITE if _vsel3 else _vc3)
                _vtxt3 = font_tiny.render(("?" + _vlb3[0]) if _vlk3 else _vlb3, True, _vtc3)
                screen.blit(_vtxt3, (_vx3 + _vp_bw//2 - _vtxt3.get_width()//2, _vp_y + 8))

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


def _text_input_screen(prompt, default="", max_len=20,
                       hint_key=None, hint_label=""):
    """
    Full-screen text input.
    Returns entered string, or None on ESC.
    If hint_key is pressed (e.g. pygame.K_s), returns the sentinel '\\x00SCAN'.
    """
    text = default
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if hint_key and event.key == hint_key and not text:
                    return "\x00SCAN"
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
        hint_txt = f"ENTER to confirm   ESC to cancel"
        if hint_key and hint_label:
            hint_txt += f"   {hint_label}"
        hint = font_tiny.render(hint_txt, True, GRAY)
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

    # LAN discovery beacon — lets clients on the same WiFi auto-find us
    beacon = _net.DiscoveryBeacon(_net.PORT, userdata.get("username", "Host"))

    # Bore tunnel — creates a public internet relay, no port forwarding needed
    bore = _net.BoreTunnel(_net.PORT)
    bore.start()

    local_ip = socket.gethostbyname(socket.gethostname())

    # Wait for client to connect
    while not net.connected:
        clock.tick(FPS)
        net.poll_accept()
        beacon.poll()

        code_loc  = _net.ip_port_to_code(local_ip, _net.PORT)
        bore_code = bore.internet_code()   # empty until bore connects (~3 s)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                bore.close(); beacon.close(); net.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    bore.close(); beacon.close(); net.close(); return None

        screen.fill(DARK)
        t = font_large.render("HOST GAME", True, CYAN)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 25))

        y = 90
        # Internet code via bore (works anywhere, no port forwarding)
        lb = font_small.render("Internet code — share with anyone online:", True, GRAY)
        screen.blit(lb, (WIDTH//2 - 210, y))
        if bore_code:
            cb = font_medium.render(bore_code, True, (80, 255, 120))
        else:
            dots = "." * ((pygame.time.get_ticks() // 400) % 4)
            cb = font_medium.render(f"connecting{dots}", True, GRAY)
        screen.blit(cb, (WIDTH//2 - 210, y + 28))
        y += 78

        # LAN code (same WiFi)
        lb2 = font_small.render("LAN / same WiFi code:", True, GRAY)
        screen.blit(lb2, (WIDTH//2 - 210, y))
        cb2 = font_medium.render(code_loc, True, YELLOW)
        screen.blit(cb2, (WIDTH//2 - 210, y + 28))
        y += 72

        lan_hint = font_tiny.render("LAN players can also use SCAN in Join Game", True, (100, 220, 100))
        screen.blit(lan_hint, (WIDTH//2 - lan_hint.get_width()//2, y + 4))

        dots2 = "." * ((pygame.time.get_ticks() // 500) % 4)
        st = font_small.render(f"Waiting for opponent{dots2}", True, WHITE)
        screen.blit(st, (WIDTH//2 - st.get_width()//2, y + 26))
        hint = font_tiny.render("ESC to cancel", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))
        pygame.display.flip()

    bore.close()
    beacon.close()

    # Exchange usernames
    net.send({"type": "HELLO", "username": userdata["username"]})
    deadline = pygame.time.get_ticks() + 5000
    while pygame.time.get_ticks() < deadline:
        clock.tick(FPS)
        _draw_waiting(f"Connected!  Exchanging info…")
        for m in net.recv_all():
            if m.get("type") == "HELLO":
                net.opp_name = m.get("username", "Opponent")
                # Save as friend (use bore internet code if ready, else local)
                _friend_code = bore_code if bore_code else code_loc
                userdata.setdefault("friends", {})[_friend_code] = {"name": net.opp_name}
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


def _lan_scan_screen():
    """
    Show a scanning screen, collect LAN hosts, let user pick one.
    Returns (ip, port) or None if cancelled / none found.
    """
    _draw_waiting("Scanning for games on your network…", "Please wait")
    pygame.display.flip()
    hosts = _net.lan_scan(timeout=1.5)

    if not hosts:
        _draw_waiting("No games found on LAN.", "Make sure host is on same WiFi.  Any key…")
        _wait_key()
        return None

    sel = 0
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(hosts)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(hosts)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    ip, port, _ = hosts[sel]
                    return ip, port

        screen.fill(DARK)
        t = font_large.render("LAN GAMES FOUND", True, CYAN)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 30))
        for i, (ip, port, name) in enumerate(hosts):
            col = YELLOW if i == sel else WHITE
            row = font_medium.render(f"{name}  ({ip})", True, col)
            screen.blit(row, (WIDTH//2 - row.get_width()//2, 130 + i * 48))
        hint = font_tiny.render("ENTER to connect   ESC to cancel", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))
        pygame.display.flip()


def join_lobby(userdata):
    """
    Ask for game code (or LAN scan), connect, exchange PICK.
    Returns (net, my_char, host_char, stage) or None on cancel/error.
    """
    # Let the player choose: enter a code, or scan LAN
    choice = _text_input_screen(
        "Enter game / LAN code  (or press S to scan):", max_len=10,
        hint_key=pygame.K_s, hint_label="S = scan LAN")

    ip, port = None, None

    if choice is None:
        return None
    elif choice == "\x00SCAN":          # sentinel from _text_input_screen
        result = _lan_scan_screen()
        if result is None:
            return None
        ip, port = result
    else:
        code = choice.upper().replace(" ", "").replace("-", "")
        if not code:
            return None
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
                    if code == "money_bags":
                        stats["seasonal_coins"] = stats.get("seasonal_coins", 0) + 1000
                        feedback = "+$1000 added to your wallet!"
                        feedback_col = (255, 215, 0)
                        history.append((f"> {code}", "+$1000!", (255, 215, 0)))
                    elif code in CHEAT_CODES:
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
    opts = ["QUICK MATCH", "HOST GAME", "JOIN GAME", "FRIENDS", "LEADERBOARD", "SET USERNAME"]
    sel  = 0
    _update_banner = []   # server update announcements to show

    # Keep a background lobby connection for incoming friend requests
    _lobby_bg = _make_lobby(userdata, timeout=3)

    while True:
        clock.tick(FPS)
        user_code = userdata.get("user_code", "????????")

        # Poll for incoming friend requests + update notifications
        if _lobby_bg and _lobby_bg.connected:
            _lobby_bg.poll()
            if _lobby_bg.incoming_friend_reqs:
                friends = userdata.setdefault("friends", {})
                _process_incoming_requests(_lobby_bg, userdata, friends)
            for _note in _lobby_bg.update_notify:
                _update_banner.append([_note, FPS * 8])
            _lobby_bg.update_notify.clear()

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
                    elif sel == 4:  # LEADERBOARD
                        leaderboard_screen(userdata)
                    elif sel == 5:  # SET USERNAME
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

        # Local online record
        _ow = userdata.get("online_wins", 0)
        _ol = userdata.get("online_losses", 0)
        _rec = font_tiny.render(f"Your record: {_ow}W – {_ol}L", True, (160, 200, 160))
        screen.blit(_rec, (WIDTH//2 - _rec.get_width()//2, HEIGHT - 52))

        hint = font_tiny.render("↑/↓  ENTER to select   ESC = back", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))

        # Update notification banners
        _update_banner[:] = [[n, t] for n, t in _update_banner if t > 0]
        for _bi, (_bn, _bt) in enumerate(_update_banner):
            _alpha = min(255, _bt * 6)
            _bsurf = pygame.Surface((WIDTH - 40, 36), pygame.SRCALPHA)
            _bsurf.fill((20, 60, 20, min(200, _alpha)))
            _btxt  = font_small.render(f"Update: {_bn}", True, (120, 255, 120))
            _bsurf.blit(_btxt, (10, 6))
            screen.blit(_bsurf, (20, 120 + _bi * 42))
            _update_banner[_bi][1] -= 1

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Leaderboard screen
# ---------------------------------------------------------------------------

def leaderboard_screen(userdata):
    """Fetch and display the global online win leaderboard from the server."""
    import fight_network as _fn
    lobby = None
    entries = []
    status  = "Connecting..."

    try:
        lobby = _fn.LobbyClient()
        lobby.connect(timeout=5)
        lobby.register(userdata.get("user_code", "????????"),
                       userdata.get("username", "Player"))
        lobby.request_leaderboard()
        # Wait up to 3s for the response
        import time as _time
        _deadline = _time.time() + 3.0
        while _time.time() < _deadline:
            lobby.poll()
            if lobby.leaderboard is not None and lobby.leaderboard != []:
                entries = lobby.leaderboard
                status  = f"Top {len(entries)} players"
                break
        else:
            if not entries:
                status = "No data yet — play some online matches!"
    except Exception as e:
        status = f"Server offline ({e})"
    finally:
        if lobby:
            try: lobby.close()
            except Exception: pass

    my_code = userdata.get("user_code", "")
    scroll  = 0

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    scroll = min(scroll + 1, max(0, len(entries) - 14))
                if event.key in (pygame.K_UP, pygame.K_w):
                    scroll = max(0, scroll - 1)

        screen.fill(DARK)
        title = font_large.render("LEADERBOARD", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 16))
        st = font_small.render(status, True, GRAY)
        screen.blit(st, (WIDTH//2 - st.get_width()//2, 68))

        # Local record
        _lw = userdata.get("online_wins", 0)
        _ll = userdata.get("online_losses", 0)
        _lr = font_tiny.render(f"Your local record: {_lw}W – {_ll}L", True, (160, 200, 160))
        screen.blit(_lr, (WIDTH//2 - _lr.get_width()//2, 96))

        # Column headers
        hdr_y = 126
        screen.blit(font_tiny.render("RANK", True, GRAY), (60,  hdr_y))
        screen.blit(font_tiny.render("PLAYER",  True, GRAY), (130, hdr_y))
        screen.blit(font_tiny.render("WINS",    True, GRAY), (WIDTH - 100, hdr_y))
        pygame.draw.line(screen, GRAY, (50, hdr_y + 20), (WIDTH - 50, hdr_y + 20), 1)

        row_h = 32
        for ri, entry in enumerate(entries[scroll:scroll + 14]):
            ry   = 152 + ri * row_h
            rank = scroll + ri + 1
            name = entry.get("username", "?")
            wins = entry.get("wins", 0)
            col  = YELLOW if rank == 1 else (200, 200, 200) if rank == 2 else \
                   (180, 130, 60) if rank == 3 else WHITE
            if rank <= 3:
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
                screen.blit(font_small.render(medal, True, col), (50, ry))
            screen.blit(font_small.render(f"#{rank}", True, col), (60, ry))
            screen.blit(font_small.render(name[:22], True, col), (130, ry))
            screen.blit(font_small.render(str(wins), True, col), (WIDTH - 100, ry))

        hint = font_tiny.render("↑/↓ scroll   ESC / ENTER = back", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 28))
        pygame.display.flip()


# ---------------------------------------------------------------------------
# Seasonal shop
# ---------------------------------------------------------------------------

def seasonal_shop(screen, clock, stats, unlocked):
    """Seasonal shop screen. Modifies stats and unlocked in-place."""
    from fight_data import CHARACTERS as _CHARS

    # Build a quick lookup: char name -> char dict
    _char_map = {c["name"]: c for c in _CHARS}

    COIN_COL  = (255, 200, 0)
    LOCK_COL  = (100, 100, 100)
    BUY_COL   = (60, 180, 60)
    OWNED_COL = (60, 120, 200)

    # Left panel dimensions
    LP_X, LP_W = 10, 210
    # Right panel
    RP_X = LP_X + LP_W + 10
    RP_W = WIDTH - RP_X - 10

    # Character card dimensions inside right panel
    CARD_W, CARD_H = 148, 108
    CARD_GAP = 8
    CARDS_PER_ROW = max(1, (RP_W + CARD_GAP) // (CARD_W + CARD_GAP))

    # Locked section scroll
    locked_scroll = 0

    def _draw_coin(surf, cx, cy, r, alpha=255):
        pygame.draw.circle(surf, (255, 200, 0, alpha) if hasattr(surf, '_pixels_address') else (255, 200, 0),
                           (cx, cy), r)
        pygame.draw.circle(surf, (180, 140, 0, alpha) if hasattr(surf, '_pixels_address') else (180, 140, 0),
                           (cx, cy), r, 2)

    def _draw_char_card(surf, x, y, w, h, shop_item, owned, can_buy, active):
        name  = shop_item["name"]
        cost  = shop_item["cost"]
        ch    = _char_map.get(name, {})
        col   = ch.get("color", GRAY)

        # Card background
        bg = (40, 40, 40) if active else (28, 28, 28)
        border = col if active else (70, 70, 70)
        pygame.draw.rect(surf, bg,     (x, y, w, h), border_radius=8)
        pygame.draw.rect(surf, border, (x, y, w, h), 2, border_radius=8)

        # Stickman color swatch
        pygame.draw.circle(surf, col, (x + w // 2, y + 30), 14)

        # Name
        nm = font_small.render(name, True, WHITE)
        surf.blit(nm, (x + w//2 - nm.get_width()//2, y + 50))

        # Cost line with coin
        cost_txt = font_small.render(str(cost), True, COIN_COL)
        pygame.draw.circle(surf, COIN_COL, (x + w//2 - cost_txt.get_width()//2 - 10, y + 72), 6)
        pygame.draw.circle(surf, (180, 140, 0), (x + w//2 - cost_txt.get_width()//2 - 10, y + 72), 6, 1)
        surf.blit(cost_txt, (x + w//2 - cost_txt.get_width()//2 + 4, y + 65))

        # Status button
        btn_rect = pygame.Rect(x + 10, y + h - 26, w - 20, 20)
        if owned:
            pygame.draw.rect(surf, OWNED_COL, btn_rect, border_radius=5)
            lbl = font_tiny.render("OWNED", True, WHITE)
        elif can_buy:
            pygame.draw.rect(surf, BUY_COL, btn_rect, border_radius=5)
            lbl = font_tiny.render("BUY", True, WHITE)
        else:
            pygame.draw.rect(surf, (60, 60, 60), btn_rect, border_radius=5)
            coins = stats.get("seasonal_coins", 0)
            lbl = font_tiny.render(f"NEED {cost - coins} more", True, GRAY)
        surf.blit(lbl, (btn_rect.centerx - lbl.get_width()//2,
                        btn_rect.centery - lbl.get_height()//2))

    active_ev = get_active_event()
    hovered   = None   # (section, index) of card under cursor
    _yuletide_gift_msg = 0   # frames to show gift notification

    # Yuletide Gatherings: free $20 gift on first visit each year
    import datetime as _dt
    _today = _dt.date.today()
    if active_ev and active_ev["name"] == "Yuletide Gatherings":
        _gift_key = f"yuletide_gift_{_today.year}"
        if not stats.get(_gift_key):
            stats[_gift_key] = True
            stats["seasonal_coins"] = stats.get("seasonal_coins", 0) + 20
            _yuletide_gift_msg = FPS * 4

    while True:
        clock.tick(FPS)
        coins         = stats.get("seasonal_coins", 0)
        purchased     = stats.get("seasonal_purchased", [])
        active_ev     = get_active_event()
        active_ev_name = active_ev["name"] if active_ev else None

        # Partition shop chars into available-now vs locked
        available = [s for s in SEASONAL_SHOP_CHARS if s["event"] == active_ev_name]
        locked    = [s for s in SEASONAL_SHOP_CHARS if s["event"] != active_ev_name]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key in (pygame.K_UP, pygame.K_w):
                    locked_scroll = max(0, locked_scroll - 1)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    max_scroll = max(0, (len(locked) - 1) // CARDS_PER_ROW - 2)
                    locked_scroll = min(max_scroll, locked_scroll + 1)

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                mx, my = (int(event.x * WIDTH), int(event.y * HEIGHT)) if event.type == pygame.FINGERDOWN else event.pos

                # BACK button
                if pygame.Rect(LP_X, HEIGHT - 52, LP_W, 38).collidepoint(mx, my):
                    return

                # Scroll locked section
                _lock_scroll_up   = pygame.Rect(RP_X, 320 - 22, RP_W, 18)
                _lock_scroll_down = pygame.Rect(RP_X, HEIGHT - 52, RP_W // 3, 18)
                if _lock_scroll_up.collidepoint(mx, my):
                    locked_scroll = max(0, locked_scroll - 1)
                if _lock_scroll_down.collidepoint(mx, my):
                    max_scroll = max(0, (len(locked) - 1) // CARDS_PER_ROW - 2)
                    locked_scroll = min(max_scroll, locked_scroll + 1)

                # Available-now cards
                for i, shop_item in enumerate(available):
                    col_idx = i % CARDS_PER_ROW
                    row_idx = i // CARDS_PER_ROW
                    cx = RP_X + col_idx * (CARD_W + CARD_GAP)
                    cy = 130 + row_idx * (CARD_H + CARD_GAP)
                    name = shop_item["name"]
                    cost = shop_item["cost"]
                    owned   = name in unlocked
                    can_buy = not owned and coins >= cost
                    btn_rect = pygame.Rect(cx + 10, cy + CARD_H - 26, CARD_W - 20, 20)
                    if btn_rect.collidepoint(mx, my) and can_buy:
                        stats["seasonal_coins"]    = coins - cost
                        plist = list(stats.get("seasonal_purchased", []))
                        if name not in plist:
                            plist.append(name)
                        stats["seasonal_purchased"] = plist
                        unlocked.add(name)

                # Locked cards (non-interactive, just display)

        # ── Draw ────────────────────────────────────────────────────────────
        screen.fill((12, 12, 20))
        draw_seasonal_decos(screen)

        # ── Left panel ──────────────────────────────────────────────────────
        pygame.draw.rect(screen, (22, 22, 34), (LP_X, 60, LP_W, HEIGHT - 70), border_radius=10)
        pygame.draw.rect(screen, (60, 60, 90), (LP_X, 60, LP_W, HEIGHT - 70), 1, border_radius=10)

        # Speech bubble — how to earn coins
        bub_y = 74
        bub_h = 220
        pygame.draw.rect(screen, (30, 30, 50), (LP_X + 8, bub_y, LP_W - 16, bub_h), border_radius=8)
        pygame.draw.rect(screen, COIN_COL,     (LP_X + 8, bub_y, LP_W - 16, bub_h), 2, border_radius=8)
        _how_lbl = font_small.render("HOW TO EARN", True, COIN_COL)
        screen.blit(_how_lbl, (LP_X + LP_W//2 - _how_lbl.get_width()//2, bub_y + 8))
        pygame.draw.circle(screen, COIN_COL, (LP_X + LP_W//2, bub_y + 42), 16)
        pygame.draw.circle(screen, (180, 140, 0), (LP_X + LP_W//2, bub_y + 42), 16, 2)
        _clbl = font_medium.render("$", True, (80, 60, 0))
        screen.blit(_clbl, (LP_X + LP_W//2 - _clbl.get_width()//2, bub_y + 42 - _clbl.get_height()//2))
        _lines = [
            "Win a match",
            "during any",
            "seasonal event",
            "to earn",
            "1 Seasonal Coin.",
            "",
            "Coins carry over",
            "between events.",
        ]
        for li, line in enumerate(_lines):
            lt = font_tiny.render(line, True, (200, 200, 220))
            screen.blit(lt, (LP_X + LP_W//2 - lt.get_width()//2, bub_y + 70 + li * 18))

        # Coin balance
        _bal_y = bub_y + bub_h + 16
        pygame.draw.rect(screen, (30, 30, 50), (LP_X + 8, _bal_y, LP_W - 16, 44), border_radius=8)
        pygame.draw.rect(screen, COIN_COL,     (LP_X + 8, _bal_y, LP_W - 16, 44), 2, border_radius=8)
        pygame.draw.circle(screen, COIN_COL, (LP_X + 20, _bal_y + 22), 10)
        pygame.draw.circle(screen, (180, 140, 0), (LP_X + 20, _bal_y + 22), 10, 2)
        _bal_txt = font_medium.render(str(stats.get("seasonal_coins", 0)), True, COIN_COL)
        screen.blit(_bal_txt, (LP_X + 34, _bal_y + 22 - _bal_txt.get_height()//2))
        _bal_sub = font_tiny.render("coins", True, (160, 160, 160))
        screen.blit(_bal_sub, (LP_X + 34 + _bal_txt.get_width() + 4, _bal_y + 22 - _bal_sub.get_height()//2))

        # Active event name
        if active_ev_name:
            _ev_t = font_tiny.render(f"Event: {active_ev_name}", True, (150, 220, 150))
            screen.blit(_ev_t, (LP_X + LP_W//2 - _ev_t.get_width()//2, _bal_y + 54))
        else:
            _ev_t = font_tiny.render("No event active", True, LOCK_COL)
            screen.blit(_ev_t, (LP_X + LP_W//2 - _ev_t.get_width()//2, _bal_y + 54))

        # BACK button
        _back_rect = pygame.Rect(LP_X, HEIGHT - 52, LP_W, 38)
        pygame.draw.rect(screen, (60, 30, 30), _back_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 60, 60), _back_rect, 2, border_radius=8)
        _bk = font_small.render("◄ BACK", True, WHITE)
        screen.blit(_bk, (_back_rect.centerx - _bk.get_width()//2,
                          _back_rect.centery - _bk.get_height()//2))

        # ── Right panel: title ───────────────────────────────────────────────
        _title = font_medium.render("SEASONAL SHOP", True, COIN_COL)
        screen.blit(_title, (RP_X, 10))
        _esc_hint = font_tiny.render("ESC to go back", True, GRAY)
        screen.blit(_esc_hint, (WIDTH - _esc_hint.get_width() - 8, 14))

        # ── Available now section ────────────────────────────────────────────
        _sec_y = 36
        if active_ev_name:
            _hdr = font_small.render(f"AVAILABLE NOW — {active_ev_name.upper()}", True, (150, 255, 150))
        else:
            _hdr = font_small.render("AVAILABLE NOW", True, LOCK_COL)
        screen.blit(_hdr, (RP_X, _sec_y))

        _card_start_y = _sec_y + 22
        if not available:
            _no_ev = font_small.render("No characters available — wait for an event!", True, LOCK_COL)
            screen.blit(_no_ev, (RP_X, _card_start_y + 10))
            _avail_end_y = _card_start_y + 44
        else:
            for i, shop_item in enumerate(available):
                col_idx = i % CARDS_PER_ROW
                row_idx = i // CARDS_PER_ROW
                cx = RP_X + col_idx * (CARD_W + CARD_GAP)
                cy = _card_start_y + row_idx * (CARD_H + CARD_GAP)
                name  = shop_item["name"]
                owned   = name in unlocked
                can_buy = not owned and stats.get("seasonal_coins", 0) >= shop_item["cost"]
                _draw_char_card(screen, cx, cy, CARD_W, CARD_H, shop_item, owned, can_buy, True)
            rows_avail  = max(1, (len(available) + CARDS_PER_ROW - 1) // CARDS_PER_ROW)
            _avail_end_y = _card_start_y + rows_avail * (CARD_H + CARD_GAP)

        # ── Divider ──────────────────────────────────────────────────────────
        _div_y = _avail_end_y + 6
        pygame.draw.line(screen, (60, 60, 80), (RP_X, _div_y), (WIDTH - 10, _div_y), 1)

        # ── Locked section ───────────────────────────────────────────────────
        _lock_y = _div_y + 10
        _lock_hdr = font_small.render("LOCKED  (available during their event)", True, LOCK_COL)
        screen.blit(_lock_hdr, (RP_X, _lock_y))
        _lock_y += 22

        if locked:
            # Scroll indicator
            total_locked_rows = (len(locked) + CARDS_PER_ROW - 1) // CARDS_PER_ROW
            visible_h = HEIGHT - _lock_y - 30
            visible_rows = max(1, visible_h // (CARD_H + CARD_GAP))
            max_scroll = max(0, total_locked_rows - visible_rows)
            locked_scroll = min(locked_scroll, max_scroll)

            if locked_scroll > 0:
                _up = font_tiny.render("▲ scroll up", True, GRAY)
                screen.blit(_up, (RP_X, _lock_y - 18))

            # Clip drawing to locked area
            clip_rect = pygame.Rect(RP_X - 4, _lock_y - 2, RP_W + 8, HEIGHT - _lock_y - 28)
            screen.set_clip(clip_rect)

            for i, shop_item in enumerate(locked):
                row_idx = i // CARDS_PER_ROW
                col_idx = i % CARDS_PER_ROW
                draw_row = row_idx - locked_scroll
                if draw_row < 0 or draw_row >= visible_rows:
                    continue
                cx = RP_X + col_idx * (CARD_W + CARD_GAP)
                cy = _lock_y + draw_row * (CARD_H + CARD_GAP)
                name  = shop_item["name"]
                owned = name in unlocked
                # Draw card with event label instead of buy button
                ch    = _char_map.get(name, {})
                col   = ch.get("color", GRAY)
                bg_c  = (25, 25, 35) if owned else (20, 20, 28)
                brd_c = OWNED_COL if owned else (50, 50, 70)
                pygame.draw.rect(screen, bg_c,  (cx, cy, CARD_W, CARD_H), border_radius=8)
                pygame.draw.rect(screen, brd_c, (cx, cy, CARD_W, CARD_H), 2, border_radius=8)
                # Color swatch (dimmed if not owned)
                swatch_col = col if owned else tuple(c // 3 for c in col)
                pygame.draw.circle(screen, swatch_col, (cx + CARD_W//2, cy + 26), 12)
                _nm = font_small.render(name, True, WHITE if owned else LOCK_COL)
                screen.blit(_nm, (cx + CARD_W//2 - _nm.get_width()//2, cy + 44))
                _ev = font_tiny.render(shop_item["event"], True, (120, 180, 120) if not owned else (80, 150, 255))
                screen.blit(_ev, (cx + CARD_W//2 - _ev.get_width()//2, cy + 64))
                if owned:
                    _own = font_tiny.render("OWNED", True, OWNED_COL)
                    screen.blit(_own, (cx + CARD_W//2 - _own.get_width()//2, cy + CARD_H - 20))
                else:
                    _cost = font_tiny.render(f"{shop_item['cost']} coins", True, COIN_COL)
                    screen.blit(_cost, (cx + CARD_W//2 - _cost.get_width()//2, cy + CARD_H - 20))

            screen.set_clip(None)

            if locked_scroll < max_scroll:
                _dn = font_tiny.render("▼ scroll down", True, GRAY)
                screen.blit(_dn, (RP_X, HEIGHT - 24))

        if _yuletide_gift_msg > 0:
            _yuletide_gift_msg -= 1
            _gm = font_small.render("Ho ho ho! +$20 Yuletide gift!", True, (255, 230, 100))
            screen.blit(_gm, (WIDTH//2 - _gm.get_width()//2, HEIGHT - 60))

        pygame.display.flip()
