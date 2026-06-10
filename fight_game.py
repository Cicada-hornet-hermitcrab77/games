import pygame
import sys
import math
import random
import json
import os
import datetime
import constants
from constants import *
from fight_data import CHARACTERS, POWERUPS, STAGES, STAGE_MATCHUPS
from fight_drawing import (draw_bg, draw_health_bars, draw_health_bars_labeled,
                           draw_win_screen, draw_active_powerups)
from fight_entities import (Fighter, AIFighter, Powerup, Platform, StagePencil,
                            StageEraser, DrawnPlatform, TimedPlatform, Portal, ConveyorBelt, SlantedConveyorBelt,
                            Spring, SnakeHook, Pumpkin, FallingSkull, HazardZone,
                            JungleSnake, GoldenJungleSnake, ComputerBug, MousePlatform,
                            Projectile, Orb, BouncingBall, Whip, HotPotato,
                            FallingPot, RollingCoin, FallingMerlin,
                            FlyingBaseball, FlyingBat, KitsuneShot, WaterBall, BeeShot, SnipeShot,
                            FireBall, NianBreath, ThunderBolt, Scroll, TotemPole,
                            RemoteController, Apple, VenomBean, PlantSpike,
                            ChargedOrb, BubbleShot, PoisonOrb, BlackHole, MusicNote, ArcaneOrb,
                            SunBeam, LibertyDove, PumpkinSeed,
                            FruitProj, CoalProj, WildfireBall)
import fight_network as _net
from fight_ui import stage_select, mode_select, character_select, online_menu, _type42_typed, secret_menu, _map_man_flag, TouchControls, touch_p1_enabled, touch_p2_enabled, seasonal_shop
from fight_seasonal import get_active_event, SEASONAL_SHOP_CHARS

# ---------------------------------------------------------------------------
# Unlock system
# ---------------------------------------------------------------------------

_UNLOCK_FILE    = os.path.join(os.path.dirname(__file__), "unlocks.json")
_DEFAULT_UNLOCK = {"Brawler", "Boxer", "Ninja", "Phantom"}
_konami_flag      = [False]   # set True when Konami code entered on Computer stage
_iddqd_flag       = [False]   # set True when IDDQD typed and match won
_ragequit_flag    = [False]   # set True when @#!#*%$ typed on lose screen
_paradox_portals_flag = [False]  # set True when p1 goes through 10 portals in one fight
_totem_kill_flag  = [False]   # set True when a TotemPole kills p1
_everything_flag  = [0]       # count of 'Everything' powerups collected by p1
_void_fall_timer_flag = [False]  # set True when p1 falls in void with 2-7s remaining
_jungle_kills_flag    = [0]      # count of JungleSnakes killed this session
_computer_bug_kills_flag = [0]   # count of ComputerBugs killed this fight
_p1_non_crit_flag = [False]      # True if p1 landed any non-crit punch this fight
_p1_opp_hit_flag  = [False]      # True if opponent ever successfully hit p1 this fight
_p1_powerup_kill_flag = [False]  # True if a damaging powerup killed p1 this fight
_p1_proj_blocked      = [0]       # projectiles p1 blocked this fight
_symbol_char_flag     = [False]   # True when <|-\||>+() typed on Computer stage
_death_defyer_flag    = [False]   # True when death_does_not_exist typed on Graveyard as Reaper
_friday13_flag        = [False]   # True when "13" typed on an actual Friday the 13th
_nick_of_time_flag    = [False]   # True when p1 KO'd p2 with ≤1 second on the clock

_PRIMES_60 = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59}
def _is_prime(n): return n in _PRIMES_60

# Each entry: (type, param, n, hint_text[, secret=True])
# types: wins_total | matches_played | win_with | beat_char | win_on_stage |
#        win_hard_ai | win_streak | win_2p | play_survival | survival_kills |
#        survival_best | perfect_wins | clutch_wins | losses | unique_wins |
#        daily_streak | konami_unlock | void_deaths | played_at_333pm
UNLOCK_CONDITIONS = {
    # ── wins_total ──────────────────────────────────────────────────────────
    "Ares":                ("wins_total",     None,            2,  "Win 2 matches vs AI"),
    "Zephyr":              ("wins_total",     None,            3,  "Win 3 matches vs AI"),
    "Unknown":             ("wins_total",     None,           20,  "Win 20 matches vs AI"),
    "omuS":                ("wins_total",     None,           40,  "Win 40 matches vs AI"),
    "Impossible":          ("wins_total",     None,           50,  "Win 50 matches vs AI"),
    # ── matches_played ──────────────────────────────────────────────────────
    "Dancing Man":         ("matches_played", None,            5,  "Play 5 matches"),
    "Ran-Doom":            ("matches_played", None,           10,  "Play 10 matches"),
    "Cecalia":             ("matches_played", None,           20,  "Play 20 matches"),
    "Morph":               ("matches_played", None,           50,  "Play 50 matches"),
    "Janitor":             ("matches_played", None,           80,  "Play 80 matches"),
    # ── win_with ────────────────────────────────────────────────────────────
    "Titan":               ("win_with",       "Brawler",       1,  "Win 1 match as Brawler"),
    "Tank":                ("win_with",       "Boxer",         1,  "Win 1 match as Boxer"),
    "Rogue":               ("win_with",       "Phantom",       1,  "Win 1 match as Phantom"),
    "Acrobat":             ("win_with",       "Ninja",         1,  "Win 1 match as Ninja"),
    "Charger":             ("win_with",       "Ares",          1,  "Win 1 match as Ares"),
    "Giant":               ("win_with",       "Titan",         1,  "Win 1 match as Titan"),
    "Wrestler":            ("win_with",       "Giant",         1,  "Win 1 match as Giant"),
    "Speedster":           ("win_with",       "Zephyr",        1,  "Win 1 match as Zephyr"),
    "Vampire":             ("win_with",       "Phantom",       3,  "Win 3 matches as Phantom"),
    "Sumo":                ("win_with",       "Titan",         3,  "Win 3 matches as Titan"),
    "Whipper":             ("win_with",       "Gladiator",     1,  "Win 1 match as Gladiator"),
    "Vamp Lord":           ("win_with",       "Vampire",       1,  "Win 1 match as Vampire"),
    "Shifter":             ("win_with",       "Rogue",         1,  "Win 1 match as Rogue"),
    "Shrink Ray":          ("win_with",       "Mouse",         1,  "Win 1 match as Mouse"),
    "Stalker":             ("win_with",       "Rogue",         3,  "Win 3 matches as Rogue"),
    "Outbacker":           ("win_on_stage",   "Desert",        1,  "Win on Desert stage"),
    "Gunner":              ("win_hard_ai",    None,            2,  "Win 2 matches vs Hard AI"),
    "Bazooka Man":         ("win_with",       "Tank",          1,  "Win 1 match as Tank"),
    "Pinball":             ("win_on_stage",   "Circus",        2,  "Win on Circus 2 times"),
    "Hammerhead":          ("wins_total",     None,           15,  "Win 15 matches vs AI"),
    "Kitsune":             ("win_on_stage",   "Dream Land",    1,  "Win on Dream Land stage"),
    "Riptide":             ("win_on_stage",   "Underwater",    1,  "Win on Underwater stage"),
    "Iron Fist":           ("perfect_wins",   None,            3,  "Win 3 matches at full HP"),
    # ── win_on_stage ────────────────────────────────────────────────────────
    "Mighty Medieval Man": ("win_on_stage",   "Medieval Castle", 1, "Win on Medieval Castle"),
    "Samurai":             ("win_on_stage",   "Dojo",          1,  "Win on Dojo stage"),
    "Skeleton":            ("win_on_stage",   "Graveyard",     1,  "Win on Graveyard stage"),
    "Gladiator":           ("win_on_stage",   "Arena",         1,  "Win on Arena stage"),
    "Spring":              ("win_on_stage",   "Grasslands",    1,  "Win on Grasslands stage"),
    "Scarecrow":           ("win_on_stage",   "Jungle",        1,  "Win on Jungle stage"),
    "Cactus":              ("win_on_stage",   "Desert",        3,  "Win on Desert 3 times"),
    "Arsonist":            ("win_on_stage",   "Volcano",       1,  "Win on Volcano stage"),
    "Cryogenisist":        ("win_on_stage",   "Arctic Tundra", 1,  "Win on Arctic Tundra"),
    "Magician":            ("win_on_stage",   "Circus",        1,  "Win on Circus stage"),
    "Headless Horseman":   ("win_on_stage",   "Haunted House", 1,  "Win on Haunted House"),
    "Astronaut":           ("win_on_stage",   "Space",         1,  "Win on Space stage"),
    "Spooderman":          ("win_on_stage",   "City Rooftop",  1,  "Win on City Rooftop"),
    "Wizard":              ("win_on_stage",   "Dream Land",    3,  "Win on Dream Land 3 times"),
    "Lava Man":            ("win_on_stage",   "Volcano Core",  1,  "Win on Volcano Core stage"),
    "Angel":               ("win_on_stage",   "Sky Island",    1,  "Win on Sky Island stage"),
    "Demon":               ("win_on_stage",   "Underworld",    1,  "Win on Underworld stage"),
    "Dark Mage":           ("win_on_stage",   "The Void",      1,  "Win on The Void stage"),
    "Pirate":              ("win_on_stage",   "Pirate Ship",   1,  "Win on Pirate Ship stage"),
    "Medusa":              ("win_on_stage",   "Underwater",    3,  "Win on Underwater 3 times"),
    "The Creator":         ("win_on_stage",   "Computer",      1,  "Win on Computer stage"),
    "Ink Brush":           ("win_on_stage",   "Dojo",          3,  "Win on Dojo 3 times"),
    "Knight":              ("win_on_stage",   "Medieval Castle", 3, "Win on Medieval Castle 3 times"),
    "Necromancer":         ("win_on_stage",   "Graveyard",     3,  "Win on Graveyard 3 times"),
    "Levitator":           ("win_on_stage",   "Sky Island",    3,  "Win on Sky Island 3 times"),
    "Pyro":                ("win_on_stage",   "Volcano",       3,  "Win on Volcano 3 times"),
    # ── win_hard_ai ─────────────────────────────────────────────────────────
    "Hardy":               ("win_hard_ai",    None,            1,  "Win 1 match vs Hard AI"),
    "ASCII":               ("win_on_stage",   "Computer",      2,  "Win on Computer 2 times"),
    "Viking":              ("win_hard_ai",    None,            3,  "Win 3 matches vs Hard AI"),
    "Laser Eyes":          ("win_hard_ai",    None,            5,  "Win 5 matches vs Hard AI"),
    "Mr. Crit":            ("win_hard_ai",    None,            7,  "Win 7 matches vs Hard AI"),
    "Enraged":             ("win_hard_ai",    None,           10,  "Win 10 matches vs Hard AI"),
    # ── win_streak ──────────────────────────────────────────────────────────
    "Psychopath":          ("win_streak",     None,            3,  "Win 3 matches in a row"),
    "Whirlpool":           ("win_streak",     None,            5,  "Win 5 matches in a row"),
    "Shadowfax":           ("win_streak",     None,            7,  "Win 7 matches in a row"),
    "Thunder God":         ("win_streak",     None,           10,  "Win 10 matches in a row"),
    # ── win_2p replaced ─────────────────────────────────────────────────────
    "Oni":                 ("wins_total",     None,            7,  "Win 7 matches vs AI"),
    "Bouncer":             ("win_on_stage",   "Arena",         3,  "Win on Arena 3 times"),
    "Teleporter":          ("win_with",       "Psychopath",    1,  "Win 1 match as Psychopath"),
    # ── play_survival ───────────────────────────────────────────────────────
    "Harpy":               ("play_survival",  None,            3,  "Play survival mode 3 times"),
    "Joker":               ("play_survival",  None,           10,  "Play survival mode 10 times"),
    # ── survival_kills ──────────────────────────────────────────────────────
    "Hooker":              ("survival_kills", None,           10,  "Get 10 kills in survival"),
    "Lumberjack":          ("survival_kills", None,           20,  "Get 20 kills in survival"),
    "Beekeeper":           ("survival_kills", None,           25,  "Get 25 kills in survival"),
    "Plague Doctor":       ("survival_kills", None,           50,  "Get 50 kills in survival"),
    "Blitzer":             ("survival_kills", None,          100,  "Get 100 kills in survival"),
    "Toxic":               ("survival_kills", None,          150,  "Get 150 kills in survival"),
    "Time Lord":           ("survival_kills", None,          200,  "Get 200 kills in survival"),
    "Sticker":             ("survival_kills", None,          300,  "Get 300 kills in survival"),
    # ── survival_best ───────────────────────────────────────────────────────
    "Snake":               ("survival_best",  None,           20,  "Get 20 kills in one survival run"),
    # ── perfect_wins ────────────────────────────────────────────────────────
    "Medic":               ("perfect_wins",   None,            1,  "Win a match at full HP"),
    "Ghost":               ("perfect_wins",   None,            4,  "Win 4 matches at full HP"),
    "Mime":                ("perfect_wins",   None,            5,  "Win 5 matches at full HP"),
    "Chameleon":           ("perfect_wins",   None,            7,  "Win 7 matches at full HP"),
    "Mirror Man":          ("perfect_wins",   None,           10,  "Win 10 matches at full HP"),
    # ── clutch_wins ─────────────────────────────────────────────────────────
    "Mouse":               ("clutch_wins",    None,            3,  "Win 3 matches with ≤10 HP"),
    "Kamikaze":            ("clutch_wins",    None,            5,  "Win 5 matches with ≤10 HP"),
    "Glass Cannon":        ("clutch_wins",    None,            7,  "Win 7 matches with ≤10 HP"),
    # ── losses ──────────────────────────────────────────────────────────────
    "Scarecrow":           ("losses",         None,            3,  "Lose 3 matches"),
    "Clown":               ("losses",         None,            5,  "Lose 5 matches"),
    "Disorientated":       ("losses",         None,           10,  "Lose 10 matches"),
    # ── unique_wins ─────────────────────────────────────────────────────────
    "Shapeshifter":        ("unique_wins",    None,            5,  "Win with 5 different characters"),
    "Elemental":           ("unique_wins",    None,           15,  "Win with 15 different characters"),
    # ── new characters ──────────────────────────────────────────────────────
    "Gargoyle":            ("win_with",            "Wrestler",      1,  "Win 1 match as Wrestler"),
    "Banshee":             ("win_on_stage",        "Haunted House", 3,  "Win on Haunted House 3 times"),
    "Storm Caller":        ("win_hard_ai",         None,            4,  "Win 4 matches vs Hard AI"),
    "Magnetar":            ("win_with",            "Charger",       1,  "Win 1 match as Charger"),
    "Swamp Thing":         ("win_on_stage",        "Jungle",        3,  "Win on Jungle 3 times"),
    "Duelist":             ("win_with",            "Shifter",       1,  "Win 1 match as Shifter"),
    "Polar Bear":          ("win_on_stage",        "Arctic Tundra", 3,  "Win on Arctic Tundra 3 times"),
    "Quaker":              ("win_streak",          None,            4,  "Win 4 matches in a row"),
    "Echo":                ("matches_played",      None,           35,  "Play 35 matches"),
    "Phantom Thief":       ("win_with",            "Rogue",         5,  "Win 5 matches as Rogue"),
    "Cloned":              ("win_super_hard",      None,            1,  "Win 1 match vs Super Hard AI"),
    "Bomb":                ("win_super_super_hard",None,            1,  "Win 1 match vs Super Super Hard AI"),
    "Halves":              ("win_with_all", "Stalker,Laser Eyes,Elemental,Medusa,Wizard,Dark Mage,Sticker,Bomb,Vampire", 1,
                            "Win with Stalker, Laser Eyes, Elemental, Medusa, Wizard, Dark Mage, Sticker, Bomb & Vampire"),
    "Godslayer":           ("win_mega_hard",       None,            1,  "Win 1 match vs Mega Hard AI"),
    "Scrollmaster":        ("secret_chars",         None,            3,  "Unlock 3 secret characters"),
    "Boulder":             ("win_on_stage",         "Volcano Core",  2,  "Win 2 matches on Volcano Core"),
    "Wisp":                ("win_streak",           None,            8,  "Win 8 matches in a row"),
    "Sandman":             ("matches_played",       None,           60,  "Play 60 matches"),
    "Reaper":              ("clutch_wins",          None,           10,  "Win 10 matches with ≤10 HP"),
    "Chainsaw Man":        ("survival_kills",       None,           40,  "Get 40 kills in survival"),
    "Crusher":             ("survival_kills",        None,           30,  "Get 30 kills in survival"),
    "Storm Witch":         ("win_on_stage",         "Arctic Tundra", 5,  "Win 5 matches on Arctic Tundra"),
    "Blood Baron":         ("win_with",             "Vamp Lord",     3,  "Win 3 matches as Vamp Lord"),
    "Drifter":             ("unique_wins",          None,           20,  "Win with 20 different characters"),
    "Warlock":             ("win_hard_ai",          None,           15,  "Win 15 matches vs Hard AI"),
    # ── Secret characters (hint hidden in UI) ───────────────────────────────
    "777":                 ("daily_streak",          None,            7,  "The lucky triple",                   True),
    "Scratch":             ("konami_unlock",        None,            1,  "???",                                True),
    "Void Master":         ("win_on_stage",         "The Void",      5,  "Some masters fear no darkness",      True),
    "Screentime":          ("played_at_noon",       None,            1,  "Timing is everything",               True),
    "God":                 ("perfect_mega_hard_win",None,            1,  "A feat only gods achieve",           True),
    "Nightfall":           ("midnight_wins",        None,            3,  "The night is young",                 True),
    "Lucky":               ("lucky_win",            None,            1,  "Hanging by a thread",                True),
    "Great Totem Spirit":  ("died_from_totem",       None,            1,  "Respect the ancient power",          True),
    # ── Regular new characters ──────────────────────────────────────────────
    "Flash":               ("win_streak",           None,            6,  "Win 6 matches in a row"),
    "Portal Maker":        ("win_on_stage",         "The Void",      3,  "Win on The Void 3 times"),
    "Gravity":             ("matches_played",       None,           90,  "Play 90 matches"),
    "Prime Time":          ("prime_time_win",       None,            1,  "Numbers hold secrets",               True),
    "Rage Quitter":        ("rage_quit_typed",      None,            1,  "Express yourself",                   True),
    # ── new regular characters ───────────────────────────────────────────────
    "Swapper":             ("win_on_stage",         "The Void",      6,  "Win 6 matches on The Void"),
    "Bruiser":             ("survival_kills",       None,           75,  "Get 75 kills in survival"),
    "Grappler":            ("win_streak",           None,           11,  "Win 11 matches in a row"),
    "Trickster":           ("losses",                None,            7,  "Lose 7 matches"),
    "Wildcard":            ("matches_played",       None,           45,  "Play 45 matches"),
    "Ironclad":            ("win_hard_ai",          None,           11,  "Win 11 matches vs Hard AI"),
    "Siphon":              ("win_with",             "Vamp Lord",     5,  "Win 5 matches as Vamp Lord"),
    "Timekeeper":          ("win_on_stage",         "Space",         4,  "Win on Space 4 times"),
    "Rainbow Man":         ("everything_collected", None,           10,  "Collect 10 'Everything' powerups"),
    # ── new secret characters ────────────────────────────────────────────────
    "The One":             ("win_with_all", "777,Scratch,Void Master,Screentime,God,Nightfall,Lucky,Great Totem Spirit,Prime Time,Rage Quitter,Mirror,Paradox", 1, "Collect them all first",               True),
    "Mirror":              ("win_half_hp",           None,            1,  "Survive on less",                    True),
    "Paradox":             ("paradox_portals_done", None,            1,  "Keep going through...",              True),
    "Spitting Cobra":      ("jungle_snake_kills", None,              100, "Kill 100 snakes in the Jungle"),
    "Jetpack":             ("void_fall_at_2_7", None,                1,  "Some falls are perfectly timed",      True),
    "The Impossible Victor": ("win_with",    "Impossible",           1,  "Win 1 match as Impossible"),
    "Pacman":              ("survival_kills",        None,           15,  "Get 15 kills in survival"),
    "ChickenBanana":       ("win_on_stage",          "Computer",      3,  "Something... glitchy",               True),
    "Soul Master":         ("secret_chars",          None,            5,  "Unlock 5 secret characters"),
    # ── new regular characters ───────────────────────────────────────────────
    "Scorpio":             ("computer_bug_kills",   None,          100,  "Kill 100 computer bugs"),
    "Nuke":                ("win_with",             "Bomb",          1,  "Win 1 match as Bomb"),
    "Druid":               ("win_on_stage",          "Jungle",        5,  "Win 5 matches on Jungle"),
    "Big Bad Critter Clad": ("crit_only_win",        None,            1,  "Win a match landing only critical hits"),
    "Life the Universe Everything": ("type42",       None,            1,  "Type the answer to life",            True),
    # ── new regular characters ───────────────────────────────────────────────
    "Shade":               ("win_with",              "Chameleon",     3,  "Win 3 matches as Chameleon"),
    "Decay":               ("win_with",              "Toxic",         3,  "Win 3 matches as Toxic"),
    "Fault Line":          ("win_with",              "Quaker",        3,  "Win 3 matches as Quaker"),
    "Buckler":             ("win_with",              "Knight",        5,  "Win 5 matches as Knight"),
    "Overdrive":           ("losses",                None,           20,  "Lose 20 matches"),
    "Hypnotist":           ("win_with",              "Clown",         3,  "Win 3 matches as Clown"),
    "Revenant":            ("win_with",              "Necromancer",   3,  "Win 3 matches as Necromancer"),
    "Volt":                ("win_on_stage",           "Space",         3,  "Win 3 matches on Space"),
    "Phantom Strike":      ("win_with",              "Flash",         5,  "Win 5 matches as Flash"),
    "Trap Master":         ("win_with",              "Headless Horseman", 3, "Win 3 matches as Headless Horseman"),
    "Juggernaut":          ("win_with",              "Titan",         5,  "Win 5 matches as Titan"),
    "Mirage":              ("win_with",              "Ghost",         3,  "Win 3 matches as Ghost"),
    # ── new secret characters ────────────────────────────────────────────────
    "Dementor":            ("died_by_powerup",       None,            1,  "Not all gifts are gifts",              True),
    "Orb Shooter":         ("projectiles_blocked",   None,          100,  "Block 100 projectiles"),
    "Copycat":             ("win_with",              "Shapeshifter",  5,  "Win 5 matches as Shapeshifter"),
    "Windshield Viper":   ("jungle_snake_kills",    None,           50,  "Kill 50 jungle snakes"),
    "Rainbow Snake":      ("jungle_snake_kills",    None,          150,  "Kill 150 jungle snakes"),
    "Inland Taipan":      ("jungle_snake_kills",    None,          200,  "Kill 200 jungle snakes"),
    "Black Mamba":        ("jungle_snake_kills",    None,          300,  "Kill 300 jungle snakes"),
    "King Cobra":         ("jungle_snake_kills",    None,          500,  "Kill 500 jungle snakes"),
    "Entomologist":       ("computer_bug_kills",    None,           50,  "Kill 50 computer bugs"),
    "Hacker":             ("computer_bug_kills",    None,          150,  "Kill 150 computer bugs"),
    "8-Bit Wasp":         ("computer_bug_kills",    None,          200,  "Kill 200 computer bugs"),
    "Black Widow":        ("computer_bug_kills",    None,          300,  "Kill 300 computer bugs"),
    "AI":                 ("computer_bug_kills",    None,          500,  "Kill 500 computer bugs"),
    "Forcefield":         ("projectiles_blocked",   None,           50,  "Block 50 projectiles"),
    "Poltergeist":        ("projectiles_blocked",   None,          150,  "Block 150 projectiles"),
    "Armor":              ("projectiles_blocked",   None,          200,  "Block 200 projectiles"),
    "Deflector":          ("projectiles_blocked",   None,          300,  "Block 300 projectiles"),
    "Unhittable":         ("projectiles_blocked",   None,          500,  "Block 500 projectiles"),
    "Sniper":             ("win_hard_ai",            None,            9,  "Win 9 matches vs Hard AI"),
    "Mega-Unhittable":    ("projectiles_blocked",   None,       100000,  "Block 100000 projectiles"),
    "Map Man":            ("map_man_unlocked",       None,            1,  "???",                                  True),
    "<|-\\||>+()":         ("symbol_char_typed",     None,            1,  "???",                                  True),
    "Death Defyer":        ("death_defyer_typed",    None,            1,  "???",                                  True),
    "Friday the 13th":     ("friday13_typed",        None,            1,  "???",                                  True),
    # ── 11 new characters ───────────────────────────────────────────────────
    "Bard":                ("win_on_stage",   "Circus",          3,  "Win 3 matches on Circus"),
    "Butcher":             ("win_with",       "Gargoyle",        1,  "Win 1 match as Gargoyle"),
    "Stone Cold":          ("win_hard_ai",    None,              6,  "Win 6 matches vs Hard AI"),
    "Tycoon":              ("matches_played", None,             30,  "Play 30 matches"),
    "Glass Jaw":           ("clutch_wins",    None,              8,  "Win 8 matches with ≤10 HP"),
    "Life Drain":          ("survival_kills", None,             35,  "Get 35 kills in survival"),
    "Lancer":              ("win_on_stage",   "Medieval Castle", 2,  "Win 2 matches on Medieval Castle"),
    "Absorber":            ("perfect_wins",   None,              6,  "Win 6 matches at full HP"),
    "Hexer":               ("win_on_stage",   "The Void",        2,  "Win 2 matches on The Void"),
    "Gambler":             ("matches_played", None,             25,  "Play 25 matches"),
    "Counter":             ("win_with",       "Bouncer",         2,  "Win 2 matches as Bouncer"),
    # ── 10 new characters ───────────────────────────────────────────────────
    "Blazer":              ("win_on_stage",   "Volcano",         4,  "Win 4 matches on Volcano"),
    "Colossus":            ("win_hard_ai",    None,              8,  "Win 8 matches vs Hard AI"),
    "Stomper":             ("win_with",       "Sumo",            3,  "Win 3 matches as Sumo"),
    "Porcupine":           ("win_on_stage",   "Jungle",          4,  "Win 4 matches on Jungle"),
    "Anchor":              ("win_with",       "Sumo",            1,  "Win 1 match as Sumo"),
    "Sleeper":             ("matches_played", None,             40,  "Play 40 matches"),
    "Rager":               ("clutch_wins",    None,             11,  "Win 11 matches with ≤10 HP"),
    "Twin":                ("unique_wins",    None,             10,  "Win with 10 different characters"),
    "Sapper":              ("survival_kills", None,             45,  "Get 45 kills in survival"),
    "Mimic":               ("win_with",       "Copycat",         3,  "Win 3 matches as Copycat"),
    # ── new regular characters ───────────────────────────────────────────────
    "Boomerang":           ("win_with",       "Whipper",         3,  "Win 3 matches as Whipper"),
    "Parry":               ("win_hard_ai",    None,             12,  "Win 12 matches vs Hard AI"),
    "Healer":              ("perfect_wins",   None,              8,  "Win 8 matches at full HP"),
    "Iron Wall":           ("win_with",       "Anchor",          3,  "Win 3 matches as Anchor"),
    "Pierce":              ("win_on_stage",   "Medieval Castle", 4,  "Win 4 matches on Medieval Castle"),
    "Rage Stack":          ("clutch_wins",    None,             12,  "Win 12 matches with ≤10 HP"),
    "Phoenix":             ("win_with",       "Revenant",        3,  "Win 3 matches as Revenant"),
    "Chain Fighter":       ("win_streak",     None,              9,  "Win 9 matches in a row"),
    "Breaker":             ("win_with",       "Stone Cold",      3,  "Win 3 matches as Stone Cold"),
    "Titan Grip":          ("win_with",       "Colossus",        3,  "Win 3 matches as Colossus"),
    # ── batch: Sunderer through Cyclone ──────────────────────────────────────
    "Sunderer":            ("win_with",       "Breaker",         3,  "Win 3 matches as Breaker"),
    "Haunter":             ("win_with",       "Shade",           3,  "Win 3 matches as Shade"),
    "Zeus":                ("win_on_stage",   "Space",           5,  "Win 5 matches on Space"),
    "Glacial":             ("win_on_stage",   "Ice Cave",        5,  "Win 5 matches on Ice Cave"),
    "Soul Eater":          ("win_with",       "Soul Master",     3,  "Win 3 matches as Soul Master"),
    "Frenzy":              ("clutch_wins",    None,             15,  "Win 15 matches with ≤10 HP"),
    "Specter":             ("win_with",       "Mirage",          3,  "Win 3 matches as Mirage"),
    "Demolisher":          ("win_with",       "Quaker",          5,  "Win 5 matches as Quaker"),
    "Feedback":            ("win_with",       "Absorber",        3,  "Win 3 matches as Absorber"),
    "Escalator":           ("matches_played", None,             75,  "Play 75 matches"),
    "Pacifist":            ("perfect_wins",   None,             12,  "Win 12 matches at full HP"),
    "Cyclone":             ("win_with",       "Teleporter",      3,  "Win 3 matches as Teleporter"),
    # ── batch: Phantom Blade through Magma ───────────────────────────────────
    "Phantom Blade":       ("win_with",       "Specter",         3,  "Win 3 matches as Specter"),
    "Inferno":             ("win_on_stage",   "Volcano",         5,  "Win 5 matches on Volcano"),
    "Titan Smash":         ("win_with",       "Juggernaut",      3,  "Win 3 matches as Juggernaut"),
    "Infiltrator":         ("win_with",       "Mimic",           3,  "Win 3 matches as Mimic"),
    "Executioner":         ("wins_total",     None,             55,  "Win 55 matches"),
    "Coldheart":           ("win_with",       "Glacial",         3,  "Win 3 matches as Glacial"),
    "Tempest":             ("win_with",       "Storm Caller",    3,  "Win 3 matches as Storm Caller"),
    "Ancient":             ("matches_played", None,            100,  "Play 100 matches"),
    "Berserk Lord":        ("clutch_wins",    None,             20,  "Win 20 matches with ≤10 HP"),
    "Shadow Dancer":       ("win_with",       "Specter",         5,  "Win 5 matches as Specter"),
    "Voodoo":              ("win_with",       "Pacifist",        3,  "Win 3 matches as Pacifist"),
    "Magma":               ("win_on_stage",   "Volcano Core",    5,  "Win 5 matches on Volcano Core"),
    # ── batch: Minotaur through Abomination ──────────────────────────────────
    "Minotaur":            ("win_with",       "Titan Smash",     3,  "Win 3 matches as Titan Smash"),
    "Puppet Master":       ("win_with",       "Infiltrator",     3,  "Win 3 matches as Infiltrator"),
    "Clockwork":           ("win_with",       "Ancient",         3,  "Win 3 matches as Ancient"),
    "Void Walker":         ("win_with",       "Void Master",     3,  "Win 3 matches as Void Master"),
    "Lich":                ("win_with",       "Soul Eater",      3,  "Win 3 matches as Soul Eater"),
    "Crimson":             ("clutch_wins",    None,             25,  "Win 25 matches with ≤10 HP"),
    "Jester":              ("win_with",       "Glitch",          3,  "Win 3 matches as Glitch"),
    "Golem":               ("win_with",       "Boulder",         3,  "Win 3 matches as Boulder"),
    "Blaze":               ("win_on_stage",   "Volcano Core",    3,  "Win 3 matches on Volcano Core"),
    "Surge":               ("win_with",       "Frenzy",          3,  "Win 3 matches as Frenzy"),
    "Phantom King":        ("win_with",       "Phantom Blade",   5,  "Win 5 matches as Phantom Blade"),
    "Abomination":         ("wins_total",     None,             75,  "Win 75 matches"),
    # ── batch 5 ─────────────────────────────────────────────────────────────
    "Witch":               ("win_with",       "Storm Witch",     3,  "Win 3 matches as Storm Witch"),
    "Giant Killer":        ("win_with",       "Titan Smash",     5,  "Win 5 matches as Titan Smash"),
    "Speed Demon":         ("win_with",       "Crimson",         3,  "Win 3 matches as Crimson"),
    "High Roller":           ("win_with",       "Jester",          3,  "Win 3 matches as Jester"),
    "Ghost Warrior":       ("win_with",       "Phantom Blade",   3,  "Win 3 matches as Phantom Blade"),
    "Suicide King":        ("clutch_wins",    None,             30,  "Win 30 matches with ≤10 HP"),
    "Harbinger":           ("wins_total",     None,            150,  "Win 150 matches"),
    "Hex Doctor":          ("win_with",       "Haunter",         3,  "Win 3 matches as Haunter"),
    "Time Warden":         ("win_with",       "Clockwork",       5,  "Win 5 matches as Clockwork"),
    "Doppelganger":        ("win_with",       "Mimic",           5,  "Win 5 matches as Mimic"),
    "Graverobber":         ("win_with",       "Lich",            3,  "Win 3 matches as Lich"),
    "Brawler King":        ("win_with",       "Surge",           3,  "Win 3 matches as Surge"),
    # ── batch 4 ─────────────────────────────────────────────────────────────
    "Marksman":            ("win_on_stage",   "Space",           6,  "Win 6 matches on Space"),
    "Elder":               ("win_on_stage",   "Grasslands",      5,  "Win 5 matches on Grasslands"),
    "Shade Walker":        ("win_with",       "Backstabber",     3,  "Win 3 matches as Backstabber"),
    "Emperor":             ("wins_total",     None,            120,  "Win 120 matches"),
    "Iron Grappler":       ("win_with",       "Titan Grip",      3,  "Win 3 matches as Titan Grip"),
    "Corsair":             ("win_on_stage",   "Underwater",      4,  "Win 4 matches on Underwater"),
    "Mech":                ("win_with",       "Clockwork",       3,  "Win 3 matches as Clockwork"),
    "Vault":               ("win_with",       "Golem",           3,  "Win 3 matches as Golem"),
    "Shaolin":             ("win_with",       "Parry",           5,  "Win 5 matches as Parry"),
    "Warlord":             ("win_with",       "Berserk Lord",    3,  "Win 3 matches as Berserk Lord"),
    "Surgeon":             ("win_with",       "Healer",          3,  "Win 3 matches as Healer"),
    "Cutthroat":           ("win_with",       "Phantom Thief",   3,  "Win 3 matches as Phantom Thief"),
    "Chef":                ("win_on_stage",   "Jungle",          2,  "Win 2 matches on Jungle"),
    "Backstabber":         ("win_with",       "Shadow Dancer",   3,  "Win 3 matches as Shadow Dancer"),
    "Crazy":               ("matches_played", None,             55,  "Play 55 matches"),
    # ── batch 6 ─────────────────────────────────────────────────────────────
    "Leech King":          ("win_with",       "Vampire",         5,  "Win 5 matches as Vampire"),
    "Puppeteer":           ("win_with",       "Puppet Master",   3,  "Win 3 matches as Puppet Master"),
    "Sorcerer":            ("win_with",       "Wizard",          5,  "Win 5 matches as Wizard"),
    "Guardian":            ("win_with",       "Golem",           5,  "Win 5 matches as Golem"),
    "Iron Maiden":         ("win_with",       "Iron Grappler",   3,  "Win 3 matches as Iron Grappler"),
    "Berserker Queen":     ("win_with",       "Berserk Lord",    5,  "Win 5 matches as Berserk Lord"),
    "Phantom Lord":        ("win_with",       "Phantom King",    5,  "Win 5 matches as Phantom King"),
    "Trapper":             ("win_with",       "Trap Master",     3,  "Win 3 matches as Trap Master"),
    "Dark Knight":         ("win_with",       "Dark Mage",       3,  "Win 3 matches as Dark Mage"),
    "Templar":             ("win_with",       "Shaolin",         5,  "Win 5 matches as Shaolin"),
    "Hydra":               ("win_with",       "Graverobber",     3,  "Win 3 matches as Graverobber"),
    "Chimera":             ("win_with",       "High Roller",       3,  "Win 3 matches as Wild Card"),
    "Fortune":             ("wins_total",     None,             90,  "Win 90 matches"),
    "Chaos Lord":          ("win_with",       "Jester",          5,  "Win 5 matches as Jester"),
    # ── new secret characters ────────────────────────────────────────────────
    "Overload":            ("wins_total",     None,            100,  "Power beyond all limits",         True),
    "Glitch":              ("matches_played", None,            150,  "???",                             True),
    "Nick of Time":        ("nick_of_time_win", None,            1,  "A win against the clock",         True),
    "Buffer":              ("wins_total",      None,            25, "Win 25 matches"),
    "Cursed":              ("losses",          None,           15,  "Lose 15 matches"),
    "Eggshell":            ("clutch_wins",    None,              6,  "Win 6 matches with ≤10 HP"),
    # ── batch 7 ─────────────────────────────────────────────────────────────
    "Cannonball":          ("win_with",       "Charger",         3,  "Win 3 matches as Charger"),
    "Wraith":              ("win_with",       "Ghost Warrior",   3,  "Win 3 matches as Ghost Warrior"),
    "Plaguebringer":       ("win_with",       "Toxic",           5,  "Win 5 matches as Toxic"),
    "Bulwark":             ("win_with",       "Iron Wall",       3,  "Win 3 matches as Iron Wall"),
    "Assassin":            ("win_with",       "Backstabber",     5,  "Win 5 matches as Backstabber"),
    "Wrecking Ball":       ("win_with",       "Juggernaut",      5,  "Win 5 matches as Juggernaut"),
    "Bounty Hunter":       ("win_with",       "Marksman",        3,  "Win 3 matches as Marksman"),
    "Abyssal":             ("win_with",       "Abomination",     3,  "Win 3 matches as Abomination"),
    "Revenant King":       ("win_with",       "Phoenix",         3,  "Win 3 matches as Phoenix"),
    "Shadow Lord":         ("win_with",       "Shadow Dancer",   5,  "Win 5 matches as Shadow Dancer"),
    "Rune Mage":           ("win_with",       "Sorcerer",        3,  "Win 3 matches as Sorcerer"),
    "Berserker Monk":      ("win_with",       "Berserker Queen", 3,  "Win 3 matches as Berserker Queen"),
    # ── batch 8 ─────────────────────────────────────────────────────────────
    "Steel Knuckle":       ("win_with",       "Iron Fist",       3,  "Win 3 matches as Iron Fist"),
    "Crystal Bomber":      ("clutch_wins",    None,             13,  "Win 13 matches with ≤10 HP"),
    "Veteran":             ("matches_played", None,            130,  "Play 130 matches"),
    "Strigone":            ("win_with",       "Blood Baron",     3,  "Win 3 matches as Blood Baron"),
    "Legionnaire":         ("win_on_stage",   "Arena",           5,  "Win 5 matches on Arena"),
    "Shadowbind":          ("win_with",       "Warlock",         3,  "Win 3 matches as Warlock"),
    "Stone Golem":         ("win_with",       "Vault",           3,  "Win 3 matches as Vault"),
    "Storm Rider":         ("win_with",       "Volt",            5,  "Win 5 matches as Volt"),
    "Frostbite":           ("win_on_stage",   "Ice Cave",        3,  "Win 3 matches on Ice Cave"),
    "Blood Mage":          ("win_with",       "Siphon",          3,  "Win 3 matches as Siphon"),
    "Mirror Knight":       ("win_with",       "Mirror Man",      3,  "Win 3 matches as Mirror Man"),
    "Desperado":           ("win_with",       "Gambler",         3,  "Win 3 matches as Gambler"),
    "Tomb Raider":         ("win_with",       "Assassin",        3,  "Win 3 matches as Assassin"),
    "Chronomancer":        ("win_with",       "Time Warden",     3,  "Win 3 matches as Time Warden"),
    "Behemoth":            ("wins_total",     None,            200,  "Win 200 matches"),
    "Boom-Boom-Boomerang": ("secret_chars",   None,             12,  "Unlock 12 secret characters"),
    # ── batch 9 ─────────────────────────────────────────────────────────────
    "Marauder":            ("win_with",       "Desperado",       3,  "Win 3 matches as Desperado"),
    "Seraph":              ("perfect_wins",   None,              9,  "Win 9 matches at full HP"),
    "Typhoon":             ("win_streak",     None,             12,  "Win 12 matches in a row"),
    "Ironveil":            ("win_hard_ai",    None,             13,  "Win 13 matches vs Hard AI"),
    "Pulse":               ("win_with",       "Storm Rider",     3,  "Win 3 matches as Storm Rider"),
    "Gilded":              ("wins_total",     None,            250,  "Win 250 matches"),
    "Dusk":                ("win_with",       "Shadowbind",      3,  "Win 3 matches as Shadowbind"),
    "Chaos":               ("unique_wins",    None,             25,  "Win with 25 different characters"),
    "Ashen":               ("win_with",       "Frostbite",       3,  "Win 3 matches as Frostbite"),
    "Ravager":             ("clutch_wins",    None,             14,  "Win 14 matches with ≤10 HP"),
    "Thornwall":           ("win_with",       "Stone Golem",     3,  "Win 3 matches as Stone Golem"),
    "Diviner":             ("win_with",       "Blood Mage",      3,  "Win 3 matches as Blood Mage"),
    "Cutlass":             ("win_on_stage",   "Pirate Ship",     3,  "Win 3 matches on Pirate Ship"),
    "Oathbreaker":         ("win_with",       "Legionnaire",     3,  "Win 3 matches as Legionnaire"),
    "Arcanist":            ("win_with",       "Chronomancer",    3,  "Win 3 matches as Chronomancer"),
    "Anansi":              ("win_with",       "Trap Master",     5,  "Win 5 matches as Trap Master"),
    "Kappa":               ("win_on_stage",   "Underwater",      5,  "Win 5 matches on Underwater"),
    "Morrigan":            ("win_with",       "Wraith",          3,  "Win 3 matches as Wraith"),
    "Badb":                ("win_with",       "Morrigan",        3,  "Win 3 matches as Morrigan"),
    "Nemain":              ("win_with",       "Badb",            3,  "Win 3 matches as Badb"),
    "Sphinx":             ("win_on_stage",    "Desert",          5,  "Win 5 matches on Desert"),
    "Wendigo":            ("win_on_stage",    "Arctic Tundra",   5,  "Win 5 matches on Arctic Tundra"),
    "Trailblazer":        ("total_wins",      None,              20, "Win 20 total matches"),
    "Aqrabuamelu":        ("win_with",       "Scorpio",         3,  "Win 3 matches as Scorpio"),
    # ── new batch: Blink through Ditto ──────────────────────────────────────
    "Blink":             ("win_with",        "Flash",           3,  "Win 3 matches as Flash"),
    "Sandstorm":         ("win_on_stage",    "Desert",          3,  "Win 3 matches on Desert"),
    "Wail":              ("win_with",        "Banshee",         3,  "Win 3 matches as Banshee"),
    "Fortress":          ("win_with",        "Bulwark",         3,  "Win 3 matches as Bulwark"),
    "Marionette":        ("win_with",        "Puppet Master",   3,  "Win 3 matches as Puppet Master"),
    "Glacier":           ("win_on_stage",    "Ice Cave",        4,  "Win 4 matches on Ice Cave"),
    "Wildfire":          ("win_with",        "Inferno",         3,  "Win 3 matches as Inferno"),
    "Vex":               ("win_with",        "Hexer",           3,  "Win 3 matches as Hexer"),
    "Stalwart":          ("win_with",        "Iron Wall",       5,  "Win 5 matches as Iron Wall"),
    "Ditto":             ("win_with",        "Mimic",           3,  "Win 3 matches as Mimic"),
    # ── Floor is Lava mode drop ──────────────────────────────────────────────
    "Performer Solara":  ("floor_lava_solara",  None, 1,  "Obtainable from Floor is Lava"),
    # ── Chaos Aura mode drop ─────────────────────────────────────────────────
    "Chaos Nun-Gimel-Hei-Shin": ("chaos_aura_nghs", None, 1, "Obtainable from Chaos Aura"),
    # ── Eartha seasonal variants (Giants Among Us only — 0.1% each) ─────────
    "Spring Eartha":     ("giants_eartha_spring", None,  1,  "Obtainable from Giants Among Us"),
    "Summer Eartha":     ("giants_eartha_summer", None,  1,  "Obtainable from Giants Among Us"),
    "Autumn Eartha":     ("giants_eartha_autumn", None,  1,  "Obtainable from Giants Among Us"),
    "Winter Eartha":     ("giants_eartha_winter", None,  1,  "Obtainable from Giants Among Us"),
    # ── Seasonal shop ────────────────────────────────────────────────────────
    "Nian":           ("seasonal_purchased", "Nian",           1, "Buy in Seasonal Shop (New Dynasties)"),
    "Smoochie":       ("seasonal_purchased", "Smoochie",       1, "Buy in Seasonal Shop (Hearts and Harmonies)"),
    "Clover":         ("seasonal_purchased", "Clover",         1, "Buy in Seasonal Shop (Emerald Echoes)"),
    "Baddit":         ("seasonal_purchased", "Baddit",         1, "Buy in Seasonal Shop (April Rain)"),
    "Eartha":         ("seasonal_purchased", "Eartha",         1, "Buy in Seasonal Shop (Bound to the Ground)"),
    "Tombstone":      ("seasonal_purchased", "Tombstone",      1, "Buy in Seasonal Shop (Legacy of Valor)"),
    "Solara":         ("seasonal_purchased", "Solara",         1, "Buy in Seasonal Shop (Summer Solstice)"),
    "Stickman of Liberty": ("seasonal_purchased", "Stickman of Liberty", 1, "Buy in Seasonal Shop (Red White and Boom)"),
    "Bookzworm":      ("seasonal_purchased", "Bookzworm",      1, "Buy in Seasonal Shop (Novel Beginnings)"),
    "Yellowstone":    ("seasonal_purchased", "Yellowstone",    1, "Buy in Seasonal Shop (Project Yellowstone)"),
    "Jack O' Slash":  ("seasonal_purchased", "Jack O' Slash",  1, "Buy in Seasonal Shop (Echoes of the Undying)"),
    "Cornucopia":          ("seasonal_purchased", "Cornucopia",          1, "Buy in Seasonal Shop (Feasterween)"),
    "Nun-Gimel-Hei-Shin":  ("seasonal_purchased", "Nun-Gimel-Hei-Shin",  1, "Buy in Seasonal Shop (Aura of Menorah)"),
    "Saint Nix":           ("seasonal_purchased", "Saint Nix",           1, "Buy in Seasonal Shop (Yuletide Gatherings)"),
}


def _default_stats():
    return {
        "wins_total":          0,
        "wins_with":           {},
        "wins_on_stage":       {},
        "survival_kills":      0,
        "perfect_wins":        0,
        "clutch_wins":         0,
        "current_streak":      0,
        "best_streak":         0,
        "matches_played":           0,
        "losses":                   0,
        "wins_hard_ai":             0,
        "wins_super_hard":          0,
        "wins_super_super_hard":    0,
        "wins_mega_hard":           0,
        "beaten_chars":             {},
        "unique_wins_chars":        [],
        "survival_runs":            0,
        "survival_best_kills":      0,
        "wins_2p":                  0,
        "void_deaths":              0,
        "daily_play_dates":         [],
        "played_at_333pm":          False,
        "konami_unlocked":          False,
        "iddqd_win":                False,
        "secret_chars_unlocked":    0,
        "played_at_midnight":       False,
        "lucky_win":                False,
        "died_on_void_totem":       False,
        "died_from_totem":          False,
        "prime_time_win":           False,
        "rage_quit_typed":          False,
        "wins_mega_hard_for_rage":  0,    # tracks wins_mega_hard at rage unlock point
        "lost_to_easy_after_mega":  False,
        # new secret unlock stats
        "wins_divisible_by_7":      False,
        "played_at_noon":           False,
        "perfect_mega_hard_win":    False,
        "midnight_wins":            0,
        # evaluated_chars: prevents all new characters unlocking instantly on update
        "evaluated_chars":          [],
        # Rainbow Man: times Everything powerup collected
        "everything_collected":     0,
        # Jetpack: fell into void with 2-7 seconds remaining
        "void_fall_at_2_7":         False,
        # Spitting Cobra: jungle snake kills
        "jungle_snake_kills":       0,
        # Mirror: wins with <= half HP
        "win_half_hp":              0,
        # Paradox: went through 10 portals in one fight
        "paradox_portals_done":     False,
        # Scorpio: computer bugs killed
        "computer_bug_kills":       0,
        # Big Bad Critter Clad: wins where every punch was a crit
        "crit_only_wins":           0,
        # Dementor: killed by a damaging powerup without opponent hitting
        "died_by_powerup":          False,
        # Life the Universe Everything: typed "42" on main screen
        "type42_done":              False,
        # Orb Shooter: cumulative projectiles blocked
        "projectiles_blocked":      0,
        # <|-\||>+(): typed on Computer stage
        "symbol_char_typed":        False,
        # Death Defyer: typed on Graveyard as Reaper
        "death_defyer_typed":       False,
        # Friday the 13th: typed "13" on an actual Friday the 13th
        "friday13_typed":           False,
        # Map Man: idled on stage select for 30 seconds
        "map_man_unlocked":         False,
        # Nick of Time: won by landing final hit with ≤1 second left
        "nick_of_time_win":         False,
        # Seasonal shop
        "seasonal_coins":           0,
        "seasonal_purchased":       [],
    }

def load_save():
    """Returns (unlocked_set, stats_dict)."""
    try:
        with open(_UNLOCK_FILE) as f:
            data = json.load(f)
        s     = set(data.get("unlocked", []))
        s.update(_DEFAULT_UNLOCK)
        # Characters with no unlock condition are always available (skip shop-only)
        for _ch in CHARACTERS:
            if _ch["name"] not in UNLOCK_CONDITIONS and not _ch.get("shop_only"):
                s.add(_ch["name"])
        stats = _default_stats()
        stats.update(data.get("stats", {}))
        # Seed evaluated_chars on first load so existing characters can still unlock normally.
        # Only new characters added in future updates will be gated by the one-fight delay.
        if not stats.get("evaluated_chars"):
            stats["evaluated_chars"] = [ch["name"] for ch in CHARACTERS if ch["name"] in UNLOCK_CONDITIONS]
        return s, stats
    except Exception:
        s = set(_DEFAULT_UNLOCK)
        for _ch in CHARACTERS:
            if _ch["name"] not in UNLOCK_CONDITIONS and not _ch.get("shop_only"):
                s.add(_ch["name"])
        return s, _default_stats()

def _save_data(unlocked, stats):
    with open(_UNLOCK_FILE, 'w') as f:
        json.dump({"unlocked": sorted(unlocked), "stats": stats}, f)

def _count_daily_streak(dates):
    """Count the number of consecutive days (ending today or yesterday) in the date list."""
    if not dates:
        return 0
    unique = sorted(set(dates), reverse=True)
    today     = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if unique[0] not in (today, yesterday):
        return 0
    streak = 1
    for i in range(1, len(unique)):
        prev = datetime.date.fromisoformat(unique[i - 1])
        curr = datetime.date.fromisoformat(unique[i])
        if (prev - curr).days == 1:
            streak += 1
        else:
            break
    return streak

def _meets_condition(cond, stats):
    kind = cond[0]; param = cond[1]; n = cond[2]
    if kind == "wins_total":
        return stats["wins_total"] >= n
    if kind == "win_with":
        return stats["wins_with"].get(param, 0) >= n
    if kind == "win_on_stage":
        return stats["wins_on_stage"].get(param, 0) >= n
    if kind == "survival_kills":
        return stats["survival_kills"] >= n
    if kind == "perfect_wins":
        return stats["perfect_wins"] >= n
    if kind == "clutch_wins":
        return stats["clutch_wins"] >= n
    if kind == "win_streak":
        return stats["best_streak"] >= n
    if kind == "matches_played":
        return stats.get("matches_played", 0) >= n
    if kind == "losses":
        return stats.get("losses", 0) >= n
    if kind == "win_hard_ai":
        return stats.get("wins_hard_ai", 0) >= n
    if kind == "beat_char":
        return stats.get("beaten_chars", {}).get(param, 0) >= n
    if kind == "unique_wins":
        return len(stats.get("unique_wins_chars", [])) >= n
    if kind == "play_survival":
        return stats.get("survival_runs", 0) >= n
    if kind == "survival_best":
        return stats.get("survival_best_kills", 0) >= n
    if kind == "win_2p":
        return stats.get("wins_2p", 0) >= n
    if kind == "win_super_hard":
        return stats.get("wins_super_hard", 0) >= n
    if kind == "win_super_super_hard":
        return stats.get("wins_super_super_hard", 0) >= n
    if kind == "win_mega_hard":
        return stats.get("wins_mega_hard", 0) >= n
    if kind == "win_with_all":
        chars_needed = [c.strip() for c in param.split(',')]
        return all(stats.get("wins_with", {}).get(c, 0) >= 1 for c in chars_needed)
    if kind == "daily_streak":
        return _count_daily_streak(stats.get("daily_play_dates", [])) >= n
    if kind == "konami_unlock":
        return stats.get("konami_unlocked", False)
    if kind == "void_deaths":
        return stats.get("void_deaths", 0) >= n
    if kind == "played_at_333pm":
        return stats.get("played_at_333pm", False)
    if kind == "iddqd_win":
        return stats.get("iddqd_win", False)
    if kind == "secret_chars":
        return stats.get("secret_chars_unlocked", 0) >= n
    if kind == "played_at_midnight":
        return stats.get("played_at_midnight", False)
    if kind == "lucky_win":
        return stats.get("lucky_win", False)
    if kind == "died_on_void_totem":
        return stats.get("died_on_void_totem", False)
    if kind == "prime_time_win":
        return stats.get("prime_time_win", False)
    if kind == "rage_quit_typed":
        return stats.get("rage_quit_typed", False)
    if kind == "wins_divisible_by_7":
        return stats.get("wins_divisible_by_7", False)
    if kind == "played_at_noon":
        return stats.get("played_at_noon", False)
    if kind == "perfect_mega_hard_win":
        return stats.get("perfect_mega_hard_win", False)
    if kind == "midnight_wins":
        return stats.get("midnight_wins", 0) >= n
    if kind == "everything_collected":
        return stats.get("everything_collected", 0) >= n
    if kind == "void_fall_at_2_7":
        return stats.get("void_fall_at_2_7", False)
    if kind == "jungle_snake_kills":
        return stats.get("jungle_snake_kills", 0) >= n
    if kind == "win_half_hp":
        return stats.get("win_half_hp", 0) >= n
    if kind == "paradox_portals_done":
        return stats.get("paradox_portals_done", False)
    if kind == "died_from_totem":
        return stats.get("died_from_totem", False)
    if kind == "computer_bug_kills":
        return stats.get("computer_bug_kills", 0) >= n
    if kind == "crit_only_win":
        return stats.get("crit_only_wins", 0) >= n
    if kind == "died_by_powerup":
        return stats.get("died_by_powerup", False)
    if kind == "type42":
        return stats.get("type42_done", False)
    if kind == "projectiles_blocked":
        return stats.get("projectiles_blocked", 0) >= n
    if kind == "symbol_char_typed":
        return stats.get("symbol_char_typed", False)
    if kind == "death_defyer_typed":
        return stats.get("death_defyer_typed", False)
    if kind == "friday13_typed":
        return stats.get("friday13_typed", False)
    if kind == "map_man_unlocked":
        return stats.get("map_man_unlocked", False)
    if kind == "seasonal_purchased":
        return param in stats.get("seasonal_purchased", [])
    if kind == "nick_of_time_win":
        return stats.get("nick_of_time_win", False)
    return False

def _unlock_progress(stats):
    """Return {char_name: (current, total)} for non-secret locked chars only."""
    result = {}
    for name, cond in UNLOCK_CONDITIONS.items():
        if len(cond) > 4 and cond[4]:   # secret — no progress bar
            continue
        kind = cond[0]; param = cond[1]; n = cond[2]
        if kind == "wins_total":          cur = stats["wins_total"]
        elif kind == "win_with":          cur = stats["wins_with"].get(param, 0)
        elif kind == "win_on_stage":      cur = stats["wins_on_stage"].get(param, 0)
        elif kind == "survival_kills":    cur = stats["survival_kills"]
        elif kind == "perfect_wins":      cur = stats["perfect_wins"]
        elif kind == "clutch_wins":       cur = stats["clutch_wins"]
        elif kind == "win_streak":        cur = stats["best_streak"]
        elif kind == "matches_played":    cur = stats.get("matches_played", 0)
        elif kind == "losses":            cur = stats.get("losses", 0)
        elif kind == "win_hard_ai":       cur = stats.get("wins_hard_ai", 0)
        elif kind == "beat_char":         cur = stats.get("beaten_chars", {}).get(param, 0)
        elif kind == "unique_wins":       cur = len(stats.get("unique_wins_chars", []))
        elif kind == "play_survival":     cur = stats.get("survival_runs", 0)
        elif kind == "survival_best":     cur = stats.get("survival_best_kills", 0)
        elif kind == "win_2p":            cur = stats.get("wins_2p", 0)
        elif kind == "win_super_hard":    cur = stats.get("wins_super_hard", 0)
        elif kind == "win_super_super_hard": cur = stats.get("wins_super_super_hard", 0)
        elif kind == "win_mega_hard":     cur = stats.get("wins_mega_hard", 0)
        elif kind == "secret_chars":      cur = stats.get("secret_chars_unlocked", 0)
        elif kind == "win_with_all":
            chars = [c.strip() for c in param.split(',')]
            cur = sum(1 for c in chars if stats.get("wins_with", {}).get(c, 0) >= 1)
            n   = len(chars)   # override n to show X/total-chars, not X/1
        elif kind == "everything_collected": cur = stats.get("everything_collected", 0)
        elif kind == "jungle_snake_kills":   cur = stats.get("jungle_snake_kills", 0)
        elif kind == "midnight_wins":        cur = stats.get("midnight_wins", 0)
        elif kind == "computer_bug_kills":   cur = stats.get("computer_bug_kills", 0)
        elif kind == "crit_only_win":        cur = stats.get("crit_only_wins", 0)
        elif kind == "projectiles_blocked":  cur = stats.get("projectiles_blocked", 0)
        else:
            cur = 0
        result[name] = (min(cur, n), n)
    return result

def check_and_unlock(unlocked, stats):
    """Check conditions for all locked chars. Returns list of newly unlocked names."""
    newly = []
    evaluated = set(stats.get("evaluated_chars", []))
    for ch in CHARACTERS:
        name = ch["name"]
        if name in unlocked:
            continue
        cond = UNLOCK_CONDITIONS.get(name)
        if not cond:
            continue
        if name not in evaluated:
            # First time this character has ever been seen — register it without unlocking.
            # This prevents a batch of new characters from all unlocking the moment an
            # update is loaded (because conditions were already met before the chars existed).
            evaluated.add(name)
            continue
        if _meets_condition(cond, stats):
            unlocked.add(name)
            newly.append(name)
            # Track secret character unlocks for Scrollmaster condition
            if len(cond) > 4 and cond[4]:
                stats["secret_chars_unlocked"] = stats.get("secret_chars_unlocked", 0) + 1
    stats["evaluated_chars"] = list(evaluated)
    if newly:
        _save_data(unlocked, stats)
    return newly

def update_stats(stats, p1_won, p1_char, stage, p1_full_hp, p1_low_hp, p2_char=None, ai_difficulty=None, p1_void_falls=0, p1_hp_remaining=None, p1_half_hp=False):
    """Update stats dict after a vs-AI fight."""
    stats["matches_played"] = stats.get("matches_played", 0) + 1
    # Track daily play date
    today = datetime.date.today().isoformat()
    dates = stats.get("daily_play_dates", [])
    if today not in dates:
        dates.append(today)
    stats["daily_play_dates"] = dates
    # Track 3:33 PM (legacy)
    now = datetime.datetime.now()
    if now.hour == 15 and now.minute == 33:
        stats["played_at_333pm"] = True
    # Track noon (12:xx)
    if now.hour == 12:
        stats["played_at_noon"] = True
    # Track midnight (12am–4am)
    if now.hour < 4:
        stats["played_at_midnight"] = True
    # Track prime-second win
    if p1_won and _is_prime(now.second):
        stats["prime_time_win"] = True
    # Track wins when total is divisible by 7
    if p1_won and stats["wins_total"] % 7 == 0:
        stats["wins_divisible_by_7"] = True
    # Track midnight wins
    if p1_won and now.hour < 4:
        stats["midnight_wins"] = stats.get("midnight_wins", 0) + 1
    # Track death on The Nether
    if not p1_won and stage == "The Nether":
        stats["died_on_void_totem"] = True
    # Track losing to easy after 10 mega hard wins
    if p1_won and ai_difficulty == 'mega_hard':
        stats["wins_mega_hard_for_rage"] = stats.get("wins_mega_hard_for_rage", 0) + 1
    if (not p1_won and ai_difficulty == 'easy'
            and stats.get("wins_mega_hard_for_rage", 0) >= 10):
        stats["lost_to_easy_after_mega"] = True
    # Accumulate void deaths
    stats["void_deaths"] = stats.get("void_deaths", 0) + p1_void_falls
    if p1_won:
        stats["wins_total"]   += 1
        stats["wins_with"][p1_char]   = stats["wins_with"].get(p1_char, 0) + 1
        stats["wins_on_stage"][stage] = stats["wins_on_stage"].get(stage, 0) + 1
        if p1_full_hp:
            stats["perfect_wins"] += 1
        if p1_low_hp:
            stats["clutch_wins"]  += 1
        if p1_half_hp:
            stats["win_half_hp"] = stats.get("win_half_hp", 0) + 1
        if p1_hp_remaining is not None and p1_hp_remaining == 7:
            stats["lucky_win"] = True
        stats["current_streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
        if ai_difficulty in ('hard', 'super_hard', 'super_super_hard', 'mega_hard'):
            stats["wins_hard_ai"] = stats.get("wins_hard_ai", 0) + 1
        if ai_difficulty in ('super_hard', 'super_super_hard', 'mega_hard'):
            stats["wins_super_hard"] = stats.get("wins_super_hard", 0) + 1
        if ai_difficulty in ('super_super_hard', 'mega_hard'):
            stats["wins_super_super_hard"] = stats.get("wins_super_super_hard", 0) + 1
        if ai_difficulty == 'mega_hard':
            stats["wins_mega_hard"] = stats.get("wins_mega_hard", 0) + 1
        if p1_full_hp and ai_difficulty == 'mega_hard':
            stats["perfect_mega_hard_win"] = True
        if p2_char:
            bc = stats.get("beaten_chars", {})
            bc[p2_char] = bc.get(p2_char, 0) + 1
            stats["beaten_chars"] = bc
        uwc = stats.get("unique_wins_chars", [])
        if p1_char not in uwc:
            uwc.append(p1_char)
            stats["unique_wins_chars"] = uwc
    else:
        stats["current_streak"] = 0
        stats["losses"] = stats.get("losses", 0) + 1

def _show_unlocks(new_names):
    """Show animated unlock screens for each newly unlocked character."""
    for char_name in new_names:
        ch  = next((c for c in CHARACTERS if c["name"] == char_name), None)
        col = ch["color"] if ch else WHITE
        cond      = UNLOCK_CONDITIONS.get(char_name)
        is_secret = cond is not None and len(cond) > 4 and cond[4]
        duration  = 5000 if is_secret else 3000
        start = pygame.time.get_ticks()
        done  = False
        while not done and pygame.time.get_ticks() - start < duration:
            clock.tick(FPS)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    done = True; break
            if done:
                break
            elapsed = (pygame.time.get_ticks() - start) / duration
            alpha   = int(220 * (1.0 - max(0, elapsed - 0.7) / 0.3)) if elapsed > 0.7 else 220
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, alpha))
            screen.blit(ov, (0, 0))
            if is_secret:
                # Glitch-style secret reveal
                for _ in range(6):
                    gx = random.randint(0, WIDTH - 200)
                    gy = random.randint(0, HEIGHT - 20)
                    gw = random.randint(30, 220)
                    gh = random.randint(2, 14)
                    gc = random.choice([(255,0,80),(0,255,120),(0,100,255),(255,220,0)])
                    pygame.draw.rect(screen, gc, (gx, gy, gw, gh))
                t1 = font_large.render("??? SECRET UNLOCKED ???", True, (255, 50, 80))
                t2 = font_medium.render(char_name, True, col)
                t3 = font_small.render("you found a secret character", True, (200, 200, 200))
            else:
                t1 = font_large.render("CHARACTER UNLOCKED!", True, YELLOW)
                t2 = font_medium.render(char_name, True, col)
                hint = cond[3] if cond else ""
                t3 = font_small.render(hint, True, (180, 200, 160))
                t4 = font_small.render("press any key to continue", True, (130, 130, 130))
            screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 70))
            screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
            if is_secret:
                screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 60))
            else:
                screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 55))
                screen.blit(t4, (WIDTH//2 - t4.get_width()//2, HEIGHT//2 + 90))
            pygame.display.flip()

def _show_seasonal_coin_earned(total):
    """Briefly shows a coin-earned notification in the corner."""
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1800:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                return
        elapsed = (pygame.time.get_ticks() - start) / 1800
        alpha = int(255 * (1.0 - max(0, elapsed - 0.6) / 0.4)) if elapsed > 0.6 else 255
        ov = pygame.Surface((260, 56), pygame.SRCALPHA)
        ov.fill((20, 20, 20, min(220, alpha)))
        pygame.draw.rect(ov, (255, 200, 0, alpha), (0, 0, 260, 56), 2, border_radius=8)
        t1 = font_small.render("+ 1 Seasonal Coin!", True, (255, 200, 0))
        t2 = font_tiny.render(f"Total: {total}  (check the Seasonal Shop)", True, (200, 200, 200))
        ov.blit(t1, (12, 8))
        ov.blit(t2, (12, 34))
        screen.blit(ov, (WIDTH - 268, HEIGHT - 64))
        pygame.display.flip()

# ---------------------------------------------------------------------------
# Fruit / Coal hit helpers (Cornucopia + Saint Nix)
# ---------------------------------------------------------------------------

def _apply_fruit_hit(target, fp):
    target.take_proj_dmg(fp.dmg)
    if fp.effect == 'slow':
        target.shock_frames = max(target.shock_frames, 180)
    elif fp.effect == 'fire':
        if target.fire_frames == 0: target.fire_tick = 300
        target.fire_frames = max(target.fire_frames, 180)
    elif fp.effect == 'shock':
        target.shock_frames = max(target.shock_frames, 240)
    elif fp.effect == 'freeze':
        target.freeze_frames = max(target.freeze_frames, 180)
    elif fp.effect == 'acid':
        if target.poison_frames == 0: target.poison_tick = 60
        target.poison_frames = max(target.poison_frames, 240)
    elif fp.effect == 'slip':
        target.shock_frames = max(target.shock_frames, 90)
    elif fp.effect == 'explode':
        target.knockback = (1 if target.x > fp.x else -1) * 12
    target.flash_timer = max(target.flash_timer, 10)


def _apply_coal_hit(target, cp):
    target.take_proj_dmg(cp.dmg)
    if cp.effect == 'fire':
        if target.fire_frames == 0: target.fire_tick = 300
        target.fire_frames = max(target.fire_frames, 240)
    elif cp.effect == 'freeze':
        target.freeze_frames = max(target.freeze_frames, 240)
    target.flash_timer = max(target.flash_timer, 12)


# ---------------------------------------------------------------------------
# Fight loop
# ---------------------------------------------------------------------------

def run_fight(p1_idx, p2_idx, vs_ai=False, ai_difficulty='medium', stage_idx=0, giant_mode=False):
    _stage_name = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13   # floaty anti-gravity
    constants.STAGE_VOID    = (_stage_name in ("The Void", "Conveyor World"))
    constants.STAGE_CEILING = (_stage_name == "The Nether")

    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g, duck=pygame.K_s, block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l, duck=pygame.K_DOWN, block=pygame.K_o)

    p1 = Fighter(200, CHARACTERS[p1_idx],  1, P1_CTRL)
    if vs_ai:
        p2 = AIFighter(700, CHARACTERS[p2_idx], -1, ai_difficulty)
    else:
        p2 = Fighter(700, CHARACTERS[p2_idx], -1, P2_CTRL)

    _touch  = TouchControls(P1_CTRL, player=1, two_player=not vs_ai) if touch_p1_enabled[0] else None
    _touch2 = TouchControls(P2_CTRL, player=2, two_player=True) if (not vs_ai and touch_p2_enabled[0]) else None

    # Giants Among Us: everyone grows to 2x scale, extra HP, slower speed
    if giant_mode:
        for _gf in (p1, p2):
            _gf.draw_scale = max(_gf.draw_scale, 2.0)
            _gf.max_hp  = int(_gf.max_hp * 1.5)
            _gf.hp      = _gf.max_hp
            _gf.char    = dict(_gf.char)
            _gf.char["speed"] = max(1, int(_gf.char.get("speed", 4) * 0.65))
    _gnpc_spawn_cd = 600   # 10 s at 60 fps until first giant NPC appears
    _gnpc          = None  # dict when active, None otherwise

    # Copycat: copy opponent's ability flags at fight start
    _COPY_EXCLUDE = {"name", "color", "speed", "jump", "punch_dmg", "kick_dmg",
                     "max_hp", "block", "desc", "double_jump", "copycat",
                     "snake", "screentime", "chicken_banana", "cloned", "shapeshifter"}
    for _copier, _source in [(p1, p2), (p2, p1)]:
        if _copier.char.get("copycat"):
            _copier.char = dict(_copier.char)  # don't mutate the shared CHARACTERS entry
            for k, v in _source.char.items():
                if k not in _COPY_EXCLUDE and v:
                    _copier.char[k] = v
            _copier._reinit_ability_timers()

    # Mimic: copy opponent's speed and max HP at fight start
    for _mimic, _target in [(p1, p2), (p2, p1)]:
        if _mimic.char.get("mimic_stats"):
            _mimic.char = dict(_mimic.char)
            _mimic.char["speed"] = _target.char["speed"]
            _mimic.max_hp = _target.char["max_hp"]
            _mimic.hp     = _mimic.max_hp

    if constants.STAGE_VOID:
        # Spawn on the central platform (GROUND_Y-70), not on the (absent) floor
        p1.x = 380.0; p1.y = float(GROUND_Y - 70); p1.on_ground = True
        p2.x = 520.0; p2.y = float(GROUND_Y - 70); p2.on_ground = True

    stage_data = STAGES[stage_idx % len(STAGES)]
    platforms  = [Platform(*p) for p in stage_data["platforms"]] + [ConveyorBelt(*c) for c in stage_data.get("conveyors", [])] + [SlantedConveyorBelt(*c) for c in stage_data.get("slanted_conveyors", [])]
    springs    = [Spring(*s)   for s in stage_data["springs"]]
    hazards    = [HazardZone(*h) for h in stage_data.get("hazards", [])]

    # Apply stage advantage / disadvantage stat modifiers
    matchup = STAGE_MATCHUPS.get(stage_data["name"], {})
    for f in (p1, p2):
        if f.char["name"] == matchup.get("adv"):
            f.speed_boost *= 1.25
            f.punch_boost += f.char["punch_dmg"] // 4
            f.kick_boost  += f.char["kick_dmg"]  // 4
        elif f.char["name"] == matchup.get("dis"):
            f.speed_boost *= 0.8
            f.punch_boost -= f.char["punch_dmg"] // 5
            f.kick_boost  -= f.char["kick_dmg"]  // 5

    def _stage_tag(fighter):
        name = fighter.char["name"]
        if name == matchup.get("adv"): return ("★ ADVANTAGE", (100, 255, 100))
        if name == matchup.get("dis"): return ("✗ DISADVANTAGE", (255, 100, 100))
        return (None, None)

    p1_stag, p1_stag_col = _stage_tag(p1)
    p2_stag, p2_stag_col = _stage_tag(p2)
    announce_timer = 180   # 3 seconds

    _p1_non_crit_flag[0]     = False
    _p1_opp_hit_flag[0]      = False
    _p1_powerup_kill_flag[0] = False
    _computer_bug_kills_flag[0] = 0
    _p1_proj_blocked[0]      = 0
    _symbol_char_flag[0]     = False
    _death_defyer_flag[0]    = False
    _friday13_flag[0]        = False
    _nick_of_time_flag[0]    = False

    game_over          = False
    winner             = None
    timer              = 90 * FPS
    p1_ever_below_max  = False   # for perfect-win tracking
    powerups     = []
    clones       = []   # list of {'fighter': AIFighter, 'timer': int, 'target': Fighter}
    active_bombs = []   # list of {'x': float, 'y': float, 'fuse': int}
    bomb_pops    = []   # list of {'x': float, 'y': float, 't': int}
    scrolls      = []   # active Scroll objects (Scrollmaster)
    totems       = []   # active TotemPole objects (Great Totem Spirit)
    remotes      = []   # active RemoteController objects (Rage Quitter)
    apples       = []   # active Apple objects (Gravity)
    venoms       = []   # active VenomBean objects (Spitting Cobra)
    notes        = []   # active MusicNote objects (Bard)
    balls         = []   # active Projectile objects
    orbs          = []   # active Orb objects (bazooka)
    charged_orbs  = []   # active ChargedOrb objects (Orb Shooter)
    bubble_shots  = []   # active BubbleShot objects (Windshield Viper)
    poison_orbs   = []   # active PoisonOrb objects (King Cobra)
    giant_bugs    = []   # giant roaming bugs (Entomologist)
    black_holes   = []   # active BlackHole objects (Hacker)
    bug_spawners  = []   # static bug spawners (8-Bit Wasp)
    spawned_bugs  = []   # {'bug': ComputerBug, 'target': Fighter} (8-Bit Wasp / Black Widow)
    bounce_balls  = []   # active BouncingBall objects (Pinball)
    hooks         = []   # active SnakeHook objects (Hooker)
    pumpkins      = []   # active Pumpkin objects (Headless Horseman)
    whips         = []   # active Whip objects (Whipper)
    kitsune_shots = []   # active KitsuneShot objects (Kitsune barrage)
    water_balls   = []   # active WaterBall objects (Riptide)
    bee_shots     = []   # active BeeShot objects (Beekeeper)
    snipe_shots   = []   # active SnipeShot objects (Shifter)
    fire_balls    = []   # active FireBall objects (Pyro)
    thunder_bolts = []   # active ThunderBolt objects (Thunder God)
    plant_spikes  = []   # active PlantSpike objects (Druid)
    quake_waves   = []   # active ground shockwaves (Fault Line)
    mines         = []   # active ground mines (Trap Master)
    arcane_orbs   = []   # active ArcaneOrb objects (Arcanist)
    wildfire_balls = []  # active WildfireBall objects (Summer Eartha)
    sun_beams     = []   # active SunBeam objects (Solara)
    nian_breaths  = []   # active NianBreath cones (Nian)
    liberty_doves      = []   # active LibertyDove companions (Stickman of Liberty)
    liberty_bombs      = []   # falling bombs dropped by LibertyDoves
    yellowstone_geysers = []  # active geysers (Yellowstone kick)
    jack_seeds    = []   # PumpkinSeed projectiles (Jack O' Slash tank kick)
    fruit_projs   = []   # FruitProj projectiles (Cornucopia)
    coal_projs    = []   # CoalProj projectiles (Saint Nix)
    spawn_timer   = 300   # first spawn after 5 seconds
    is_jungle      = stage_data["name"] == "Jungle"
    is_computer    = stage_data["name"] == "Computer"
    is_underworld  = stage_data["name"] == "Underworld"
    jungle_snakes      = []
    snake_spawn_timer  = 180
    computer_bugs      = []
    bug_spawn_timer    = 150
    falling_skulls     = []
    skull_spawn_timer  = 200
    casino_coins     = []   # falling coins on The Casino stage
    casino_coin_cd   = 90
    is_casino        = stage_data["name"] == "The Casino"
    _lava_burn_p1_cd = 0
    _lava_burn_p2_cd = 0
    stage_pencil = None
    stage_eraser = None
    if is_computer:
        platforms.append(MousePlatform(80, GROUND_Y - 62, travel=720))
        stage_pencil = StagePencil()
        stage_eraser = StageEraser()

    _p1_portals_this_fight = [0]   # count of portals p1 travels through this fight
    if stage_data["name"] == "Portal World":
        _pw_cols = [
            (80, 100, 220),   # pair 0 — blue
            (220, 120, 20),   # pair 1 — orange
            (20, 200, 80),    # pair 2 — green
            (180, 40, 220),   # pair 3 — purple
            (220, 40, 40),    # pair 4 — red
        ]
        _pw_pos = stage_data.get("portals", [])
        portals_obj = []
        for _pi in range(0, min(len(_pw_pos), 10), 2):
            _col = _pw_cols[_pi // 2]
            _pa = Portal(_pw_pos[_pi][0],   _pw_pos[_pi][1],   _col)
            _pb = Portal(_pw_pos[_pi+1][0], _pw_pos[_pi+1][1], _col)
            _pa.partner = _pb
            _pb.partner = _pa
            portals_obj.extend([_pa, _pb])
    else:
        _portal_cols = [(80, 100, 220), (220, 120, 20)]
        _px1 = random.randint(80, WIDTH // 2 - 60)
        _px2 = random.randint(WIDTH // 2 + 60, WIDTH - 80)
        _py1 = random.randint(GROUND_Y - 280, GROUND_Y - 80)
        _py2 = random.randint(GROUND_Y - 280, GROUND_Y - 80)
        portals_obj  = [Portal(_px1, _py1, _portal_cols[0]), Portal(_px2, _py2, _portal_cols[1])]
        portals_obj[0].partner = portals_obj[1]
        portals_obj[1].partner = portals_obj[0]

    # Cloned: spawn permanent AI clones at fight start
    for _p, _opp in [(p1, p2), (p2, p1)]:
        if _p.char.get("cloned"):
            _cx = 350.0 if _p is p1 else 550.0
            _cf = AIFighter(_cx, dict(_p.char), 1 if _p is p1 else -1, 'medium')
            _cf.hp = 999999; _cf.max_hp = 999999
            clones.append({'fighter': _cf, 'timer': 999999, 'target': _opp, 'permanent': True})

    # AI character: spawn 5 mortal AI clones at fight start
    for _p, _opp in [(p1, p2), (p2, p1)]:
        if _p.char.get("ai_clones"):
            _clone_char = {"name": "AI Clone", "color": (0, 180, 160),
                           "speed": 4, "jump": -12, "punch_dmg": 6, "kick_dmg": 6,
                           "max_hp": 40, "block": 2, "desc": "", "double_jump": False}
            for _i in range(5):
                _cx = random.randint(100, WIDTH - 100)
                _cf = AIFighter(float(_cx), _clone_char, 1 if _p is p1 else -1, 'easy')
                clones.append({'fighter': _cf, 'timer': 999999, 'target': _opp, 'permanent': True})

    # Konami code tracking (for Scratch unlock on Computer stage)
    _KONAMI = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
               pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
               pygame.K_a, pygame.K_b]
    _konami_idx = 0
    _konami_unlocked_this_fight = False

    # IDDQD tracking (for God unlock: type IDDQD and win the match)
    _IDDQD = [pygame.K_i, pygame.K_d, pygame.K_d, pygame.K_q, pygame.K_d]
    _iddqd_idx  = 0
    _iddqd_done = False

    # Rage Quitter unlock: type @#!#*%$ on the lose screen
    _RAGEQUIT_SEQ = "@#!#*%$"
    _ragequit_buf = ""

    # <|-\||>+() unlock: type that string on Computer stage
    _SYMBOL_SEQ = "<|-\\||>+()"
    _symbol_buf = ""

    # Death Defyer unlock: type death_does_not_exist on Graveyard as Reaper
    _DEATH_SEQ   = "death_does_not_exist"
    _death_buf   = ""
    _is_graveyard = stage_data["name"] == "Graveyard"
    _p1_is_reaper = p1.char["name"] == "Reaper"
    # Friday the 13th unlock: type "13" on a real Friday the 13th
    _f13_buf = ""

    # Screentime: track whether a Screentime fighter is playing
    _screentime_active = (p1.char.get("screentime") or p2.char.get("screentime"))
    _screentime_skip = False  # toggle for slow-mode frame skip

    while True:
        clock.tick(FPS)
        # Screentime: 1v1 runs at half speed — skip every other update frame
        if _screentime_active and not game_over:
            _screentime_skip = not _screentime_skip
            if _screentime_skip:
                pygame.event.pump()
                pygame.display.flip()
                continue
        if p1.hp < p1.max_hp:
            p1_ever_below_max = True

        for event in pygame.event.get():
            if _touch: _touch.handle_event(event)
            if _touch2: _touch2.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    _p1w  = vs_ai and winner is p1
                    if _p1w and _iddqd_done:
                        _iddqd_flag[0] = True
                    # Rage Quitter: track *@#!$%%! typed while on lose screen
                    if not _p1w and hasattr(event, 'unicode') and event.unicode:
                        _ragequit_buf += event.unicode
                        if _RAGEQUIT_SEQ in _ragequit_buf:
                            _ragequit_flag[0] = True
                            _ragequit_buf = ""
                        if len(_ragequit_buf) > len(_RAGEQUIT_SEQ) + 5:
                            _ragequit_buf = _ragequit_buf[-len(_RAGEQUIT_SEQ):]
                    _info = (_p1w, p1.char["name"], _stage_name,
                             not p1_ever_below_max, p1.hp <= 10,
                             p2.char["name"], ai_difficulty, p1.void_falls,
                             p1.hp, p1.hp <= p1.max_hp // 2)
                    if event.key == pygame.K_r:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False; return ('rematch', _info)
                    if event.key == pygame.K_c:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False; return ('select',  _info)
                    if event.key == pygame.K_ESCAPE:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False; return ('select', _info)
                else:
                    if event.key == pygame.K_ESCAPE:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False
                        return ('select', (False, p1.char["name"], _stage_name, False, False, p2.char["name"], ai_difficulty, p1.void_falls))
                    # Konami code tracking (only on Computer stage)
                    if is_computer and not _konami_unlocked_this_fight:
                        if event.key == _KONAMI[_konami_idx]:
                            _konami_idx += 1
                            if _konami_idx == len(_KONAMI):
                                _konami_unlocked_this_fight = True
                                _konami_flag[0] = True
                        else:
                            _konami_idx = 1 if event.key == _KONAMI[0] else 0
                    # IDDQD tracking (any stage, any time during the match)
                    if not _iddqd_done:
                        if event.key == _IDDQD[_iddqd_idx]:
                            _iddqd_idx += 1
                            if _iddqd_idx == len(_IDDQD):
                                _iddqd_done = True
                        else:
                            _iddqd_idx = 1 if event.key == _IDDQD[0] else 0
                    # <|-\||>+() tracking (Computer stage)
                    if is_computer and hasattr(event, 'unicode') and event.unicode:
                        _symbol_buf += event.unicode
                        if _SYMBOL_SEQ in _symbol_buf:
                            _symbol_char_flag[0] = True
                            _symbol_buf = ""
                        if len(_symbol_buf) > len(_SYMBOL_SEQ) + 5:
                            _symbol_buf = _symbol_buf[-len(_SYMBOL_SEQ):]
                    # Death Defyer: type death_does_not_exist on Graveyard as Reaper
                    if _is_graveyard and _p1_is_reaper and hasattr(event, 'unicode') and event.unicode:
                        _death_buf += event.unicode.lower()
                        if _DEATH_SEQ in _death_buf:
                            _death_defyer_flag[0] = True
                            _death_buf = ""
                        if len(_death_buf) > len(_DEATH_SEQ) + 5:
                            _death_buf = _death_buf[-len(_DEATH_SEQ):]
                    # Friday the 13th: type "13" on an actual Friday the 13th
                    if hasattr(event, 'unicode') and event.unicode:
                        _f13_buf += event.unicode
                        if "13" in _f13_buf:
                            _now = datetime.datetime.now()
                            if _now.weekday() == 4 and _now.day == 13:
                                _friday13_flag[0] = True
                            _f13_buf = ""
                        if len(_f13_buf) > 4:
                            _f13_buf = _f13_buf[-2:]

        if not game_over:
            # Portal Maker: replace portals on kick
            for shooter in (p1, p2):
                if shooter.pending_portal:
                    shooter.pending_portal = False
                    _cols = _portal_cols if shooter is p1 else list(reversed(_portal_cols))
                    _new1 = Portal(shooter.x, shooter.y - 80, _cols[0])
                    _new2 = Portal(
                        random.randint(100, WIDTH - 100),
                        random.randint(GROUND_Y - 280, GROUND_Y - 60),
                        _cols[1])
                    _new1.partner = _new2
                    _new2.partner = _new1
                    portals_obj[:] = [_new1, _new2]

            for portal in portals_obj:
                portal.update()
            for fighter in (p1, p2):
                for portal in portals_obj:
                    if portal.partner and fighter.portal_cooldown == 0 and portal.near(fighter):
                        fighter.x = portal.partner.x
                        fighter.y = portal.partner.y
                        fighter.vy = 0
                        fighter.portal_cooldown = FPS * 2
                        if fighter is p1:
                            _p1_portals_this_fight[0] += 1
                            if _p1_portals_this_fight[0] >= 10:
                                _paradox_portals_flag[0] = True
                        break

            for plat in platforms:
                plat.update()
            for sp in springs:
                sp.update()
                sp.trigger(p1)
                sp.trigger(p2)
                for cd in clones:
                    sp.trigger(cd['fighter'])

            # Update hazard zones and apply damage
            for hz in hazards:
                hz.update()
                for fi, fighter in enumerate([p1, p2]):
                    if not fighter.char.get("immune") and hz.contains(fighter):
                        cd_attr = 'p1_cd' if fi == 0 else 'p2_cd'
                        if getattr(hz, cd_attr) == 0:
                            setattr(hz, cd_attr, HazardZone.TICK)
                            dmg = 8 if hz.htype == "lava" else 6 if hz.htype == "electric" else 5
                            fighter.take_proj_dmg(dmg, flash=False)
                            fighter.flash_timer = max(fighter.flash_timer, 6)
                            if hz.htype == "lava" and fighter.fire_frames == 0:
                                fighter.fire_tick = 60
                                fighter.fire_frames = max(fighter.fire_frames, 120)
                            if hz.htype == "ice":
                                fighter.shock_frames = max(fighter.shock_frames, 45)

            # Floor is Lava: ground contact burns
            if stage_data["name"] == "Floor is Lava":
                if _lava_burn_p1_cd > 0: _lava_burn_p1_cd -= 1
                if _lava_burn_p2_cd > 0: _lava_burn_p2_cd -= 1
                if p1.y >= GROUND_Y - 8 and _lava_burn_p1_cd == 0 and not p1.bubble_shield:
                    p1.hp = max(0, p1.hp - 3)
                    p1.flash_timer = max(p1.flash_timer, 6)
                    if p1.fire_frames == 0: p1.fire_tick = 240
                    p1.fire_frames = max(p1.fire_frames, 90)
                    _lava_burn_p1_cd = 45
                if p2.y >= GROUND_Y - 8 and _lava_burn_p2_cd == 0 and not p2.bubble_shield:
                    p2.hp = max(0, p2.hp - 3)
                    p2.flash_timer = max(p2.flash_timer, 6)
                    if p2.fire_frames == 0: p2.fire_tick = 240
                    p2.fire_frames = max(p2.fire_frames, 90)
                    _lava_burn_p2_cd = 45

            # Update clones
            new_clones = []
            for cd in clones:
                if not cd.get('permanent'):
                    cd['timer'] -= 1
                if cd['timer'] > 0 and cd['fighter'].hp > 0:
                    _psr = next((_pf for _pf in (p1, p2) if _pf.possess_timer > 0 and _pf.possess_entity and _pf.possess_entity[0] == 'clone' and _pf.possess_entity[1] is cd['fighter']), None)
                    if _psr:
                        _pc = P1_CTRL if _psr is p1 else P2_CTRL
                        _opc = p2 if _psr is p1 else p1
                        _cl_keys = _KeyProxy({_pc[a]: bool(keys[_pc[a]]) for a in _pc})
                        Fighter.update(cd['fighter'], _cl_keys, _opc, platforms)
                    else:
                        cd['fighter'].update(None, cd['target'], platforms)
                    new_clones.append(cd)
            clones = new_clones

            # Flame trail damage — 2P mode (each player's trail can burn the opponent)
            def _flame_trail_hit(trail_owner, victim):
                if (trail_owner.char.get("flame_trail") and trail_owner.trail_dmg_cd == 0
                        and trail_owner.flame_trail):
                    for tx, ty, _ in trail_owner.flame_trail:
                        if abs(victim.x - tx) < 28 and abs(victim.y - ty) < 40:
                            if not victim.char.get("immune"):
                                victim.hp = max(0, victim.hp - 3)
                                victim.flash_timer = max(victim.flash_timer, 6)
                            if victim.fire_frames == 0: victim.fire_tick = 480
                            victim.fire_frames = max(victim.fire_frames, 120)
                            trail_owner.trail_dmg_cd = 30
                            break
            for blazer, opp in [(p1, p2), (p2, p1)]:
                _flame_trail_hit(blazer, opp)

            # Autumn Eartha: leaf rain — area damage within 140px
            for _lr_owner, _lr_vic in [(p1, p2), (p2, p1)]:
                if (_lr_owner.char.get("leaf_rain") and _lr_owner.flower_dmg_cd == 0
                        and abs(_lr_owner.x - _lr_vic.x) < 140):
                    if not _lr_vic.bubble_shield:
                        _lr_vic.hp = max(0, _lr_vic.hp - 2)
                        _lr_vic.flash_timer = max(_lr_vic.flash_timer, 4)
                    _lr_owner.flower_dmg_cd = 30  # reuse existing cd field

            # Winter Eartha: snow aura — slows opponent within 130px
            for _sa_owner, _sa_vic in [(p1, p2), (p2, p1)]:
                if (_sa_owner.char.get("snow_aura") and _sa_owner.flower_dmg_cd == 0
                        and abs(_sa_owner.x - _sa_vic.x) < 130):
                    _sa_vic.speed_boost = max(0.45, _sa_vic.speed_boost - 0.08)
                    _sa_owner.flower_dmg_cd = 45

            # Flower trail poison — Spring Eartha
            def _flower_trail_hit(owner, victim):
                if owner.char.get("flower_trail_poison") and owner.flower_dmg_cd == 0:
                    for fx, fy, _ in owner.flower_trail:
                        if abs(victim.x - fx) < 30 and abs(victim.y - fy) < 40:
                            if victim.poison_frames == 0: victim.poison_tick = 180
                            victim.poison_frames = max(victim.poison_frames, 240)
                            owner.flower_dmg_cd = 60
                            break
            for _f_owner, _f_vic in [(p1, p2), (p2, p1)]:
                _flower_trail_hit(_f_owner, _f_vic)

            # Cactus contact damage + poison
            for cactus, victim in [(p1, p2), (p2, p1)]:
                if (cactus.char.get("contact_dmg") and
                        victim.contact_cooldown == 0 and
                        abs(cactus.x - victim.x) < 55):
                    victim.hp = max(0, victim.hp - cactus.char["contact_dmg"])
                    victim.contact_cooldown = 60
                    victim.flash_timer = 8
                    if victim.poison_frames == 0:
                        victim.poison_tick = 180
                    victim.poison_frames = max(victim.poison_frames, 600)  # 10 sec

            # Boomerang collision
            for thrower, victim in [(p1, p2), (p2, p1)]:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    if math.hypot(bx - victim.x, by - (victim.y - 60)) < 48:
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(8)
                        victim.flash_timer = 6
                        thrower.boomerang_hit_cd = 30   # 0.5s between hits
                if thrower.bbboomerang_timer > 0 and thrower.bbboomerang_hit_cd == 0:
                    _bbe = (300 - thrower.bbboomerang_timer) // 60
                    _bbrx = 70 + _bbe * 10;  _bbry = 45 + _bbe * 7
                    _bbhr = 28 + _bbe * 4
                    for _bbi in range(5):
                        _bba = thrower.bbboomerang_angle + math.radians(_bbi * 72)
                        _bbx = thrower.x + math.cos(_bba) * _bbrx
                        _bby = (thrower.y - 60) + math.sin(_bba) * _bbry
                        if math.hypot(_bbx - victim.x, _bby - (victim.y - 60)) < _bbhr:
                            if not victim.bubble_shield:
                                victim.take_proj_dmg(6)
                            victim.flash_timer = 6
                            thrower.bbboomerang_hit_cd = 30
                            break

            # Laser Eyes beam damage
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if (shooter.char.get("laser_eyes") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    correct_side = ((shooter.facing == 1  and victim.x > shooter.x) or
                                    (shooter.facing == -1 and victim.x < shooter.x))
                    if correct_side and abs((victim.y - 60) - laser_y) < 35:
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(2)
                        victim.flash_timer = 4
                        shooter.laser_hit_cd = 15  # damage tick every 15 frames

            keys = _touch.inject(pygame.key.get_pressed()) if _touch else pygame.key.get_pressed()
            if _touch2: keys = _touch2.inject(keys)

            # Poltergeist possession: decrement timer, apply player input to entity
            def _polt_ai_keys(fighter, opp, ctrl):
                m = {v: False for v in ctrl.values()}
                if opp.x > fighter.x + 80:   m[ctrl['right']] = True
                elif opp.x < fighter.x - 80: m[ctrl['left']]  = True
                if fighter.on_ground and opp.y < fighter.y - 80: m[ctrl['jump']] = True
                if abs(opp.x - fighter.x) < 90: m[ctrl['punch']] = True
                return _KeyProxy(m)

            for _pf, _oc in [(p1, p2), (p2, p1)]:
                if _pf.possess_timer > 0:
                    _pf.possess_timer -= 1
                    _pc = P1_CTRL if _pf is p1 else P2_CTRL
                    _ent = _pf.possess_entity
                    if _ent:
                        if _ent[0] == 'platform':
                            _plat = _ent[1]
                            _spd = 6.0
                            if keys[_pc['left']]:  _plat.x = max(0.0, _plat.x - _spd)
                            if keys[_pc['right']]: _plat.x = min(float(WIDTH - _plat.w), _plat.x + _spd)
                        elif _ent[0] == 'spring':
                            _sp = _ent[1]
                            _spd = 6.0
                            if keys[_pc['left']]:  _sp.x = max(30.0, _sp.x - _spd)
                            if keys[_pc['right']]: _sp.x = min(float(WIDTH - 30), _sp.x + _spd)
                    if _pf.possess_timer <= 0:
                        _pf.possess_entity = None

            p1_keys = _polt_ai_keys(p1, p2, P1_CTRL) if p1.possess_timer > 0 else keys
            p2_keys = _polt_ai_keys(p2, p1, P2_CTRL) if p2.possess_timer > 0 else keys
            p1.update(p1_keys, p2, platforms)
            p2.update(p2_keys, p1, platforms)

            # Map Man: swap to a random stage on kick
            for _swapper in (p1, p2):
                if _swapper.pending_stage_swap:
                    _swapper.pending_stage_swap = False
                    _new_stages = [i for i in range(len(STAGES)) if i != stage_idx]
                    if _new_stages:
                        stage_idx    = random.choice(_new_stages)
                        stage_data   = STAGES[stage_idx]
                        platforms    = [Platform(*_p) for _p in stage_data["platforms"]]
                        springs      = [Spring(*_s)   for _s in stage_data["springs"]]
                        is_jungle     = stage_data["name"] == "Jungle"
                        is_computer   = stage_data["name"] == "Computer"
                        is_underworld = stage_data["name"] == "Underworld"
                        _is_graveyard = stage_data["name"] == "Graveyard"
                        constants.STAGE_VOID    = (stage_data["name"] in ("The Void", "Conveyor World"))
                        constants.STAGE_CEILING = (stage_data["name"] == "The Nether")
                        jungle_snakes.clear()
                        computer_bugs.clear()
                        falling_skulls.clear()

            # Spawn balls from shoot_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing * 30,
                                            shooter.y - 60, shooter.facing, shooter))

            # Update balls and check collisions
            for b in balls:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        if victim.char.get("armor_proj"):
                            b.alive = False
                        elif victim.char.get("deflect_proj") or (victim.blocking and victim.char.get("reflect_proj")):
                            b.vx    = -b.vx
                            b.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; b.alive = False
                        elif victim.blocking:
                            b.alive = False
                            if victim is p1:
                                _p1_proj_blocked[0] += 1
                        else:
                            victim.take_proj_dmg(10)
                            victim.flash_timer = 8
                            b.alive = False
            balls = [b for b in balls if b.alive]

            # Arcanist: arcane orbs (1v1)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_arcane_orb:
                    shooter.pending_arcane_orb = False
                    arcane_orbs.append(ArcaneOrb(shooter.x + shooter.facing * 30,
                                                  shooter.y - 60, shooter.facing, shooter))
            for ao in arcane_orbs:
                ao.update()
                if ao.alive:
                    victim = p2 if ao.owner is p1 else p1
                    if ao.collides(victim):
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(ArcaneOrb.DMG)
                        victim.flash_timer = 8
                        ao.alive = False
            arcane_orbs = [ao for ao in arcane_orbs if ao.alive]

            # Summer Eartha: WildfireBall on punch
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_wildfire:
                    shooter.pending_wildfire = False
                    wildfire_balls.append(WildfireBall(
                        shooter.x + shooter.facing * 40, shooter.y - 55, shooter.facing, shooter))
            for wb in wildfire_balls:
                wb.update()
                if wb.alive:
                    victim = p2 if wb.owner is p1 else p1
                    if wb.collides(victim) and not victim.bubble_shield:
                        victim.take_proj_dmg(WildfireBall.DMG)
                        victim.flash_timer = 14
                        if victim.fire_frames == 0: victim.fire_tick = 480
                        victim.fire_frames = max(victim.fire_frames, 300)
                        wb.alive = False
                wb.draw(screen)
            wildfire_balls = [wb for wb in wildfire_balls if wb.alive]

            # Spawn orbs from bazooka_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing * 30,
                                    shooter.y - 60, shooter.facing, shooter))

            # Update orbs and apply explosion damage
            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    victim = p2 if o.owner is p1 else p1
                    if math.hypot(o.x - victim.x, o.y - (victim.y - 60)) < o.EXPLODE_RADIUS:
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(o.EXPLODE_DMG)
                        victim.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            # Spawn charged orbs from Orb Shooter
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_charged_orb:
                    charge = shooter.pending_charged_orb
                    shooter.pending_charged_orb = 0
                    charged_orbs.append(ChargedOrb(
                        shooter.x + shooter.facing * 30,
                        shooter.y - 60, shooter.facing, shooter, charge))

            # Update charged orbs and check collisions
            for co in charged_orbs:
                co.update()
                if co.alive:
                    victim = p2 if co.owner is p1 else p1
                    if co.collides(victim):
                        if victim.char.get("armor_proj"):
                            co.alive = False
                        elif victim.char.get("deflect_proj"):
                            co.vx = -co.vx; co.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; co.alive = False
                        elif victim.blocking:
                            co.alive = False
                            if victim is p1:
                                _p1_proj_blocked[0] += 1
                        else:
                            victim.take_proj_dmg(co.dmg)
                            victim.flash_timer = max(victim.flash_timer, 12)
                            co.alive = False
            charged_orbs = [co for co in charged_orbs if co.alive]

            # Spawn bubble shots from bubble_kick (Windshield Viper)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bubble_shot:
                    shooter.pending_bubble_shot = False
                    bubble_shots.append(BubbleShot(
                        shooter.x + shooter.facing * 30,
                        shooter.y - 60, shooter.facing, shooter))

            # Update bubble shots
            for bs in bubble_shots:
                bs.update()
                if bs.alive:
                    victim = p2 if bs.owner is p1 else p1
                    if bs.collides(victim):
                        if victim.char.get("armor_proj"):
                            bs.alive = False
                        elif victim.char.get("deflect_proj"):
                            bs.vx = -bs.vx; bs.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; bs.alive = False
                        else:
                            victim.take_proj_dmg(10)
                            victim.flash_timer = 8
                            bs.alive = False
            bubble_shots = [bs for bs in bubble_shots if bs.alive]

            # Spawn poison orbs from cobra_orb (King Cobra)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_poison_orb:
                    shooter.pending_poison_orb = False
                    poison_orbs.append(PoisonOrb(
                        shooter.x + shooter.facing * 30,
                        shooter.y - 60, shooter.facing, shooter))

            # Update poison orbs
            for po in poison_orbs:
                po.update()
                if po.alive:
                    victim = p2 if po.owner is p1 else p1
                    if po.collides(victim):
                        if victim.char.get("armor_proj"):
                            po.alive = False
                        elif victim.char.get("deflect_proj"):
                            po.vx = -po.vx; po.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; po.alive = False
                        else:
                            victim.take_proj_dmg(15)
                            victim.poison_frames = max(victim.poison_frames, FPS * 6)
                            victim.poison_tick   = min(victim.poison_tick if victim.poison_tick > 0 else 999, 60)
                            victim.flash_timer   = 15
                            po.alive = False
            poison_orbs = [po for po in poison_orbs if po.alive]

            # Entomologist: spawn giant bug (once per fight)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_giant_bug and not shooter.entomologist_bug_used:
                    shooter.pending_giant_bug    = False
                    shooter.entomologist_bug_used = True
                    giant_bugs.append({'x': float(shooter.x), 'y': float(GROUND_Y),
                                       'vx': 0.0, 'life': FPS * 8, 'leg_t': 0.0,
                                       'bite_cd': {id(p1): 0, id(p2): 0}})
                else:
                    shooter.pending_giant_bug = False

            # Update giant bugs
            for gb in giant_bugs:
                gb['life'] -= 1
                gb['leg_t'] += 0.2
                nearest = min((p1, p2), key=lambda f: abs(f.x - gb['x']))
                gb['vx'] = 3.0 if nearest.x > gb['x'] else -3.0
                gb['x']   = max(30.0, min(float(WIDTH - 30), gb['x'] + gb['vx']))
                for f in (p1, p2):
                    fid = id(f)
                    if gb['bite_cd'][fid] > 0:
                        gb['bite_cd'][fid] -= 1
                    if gb['bite_cd'][fid] == 0 and abs(f.x - gb['x']) < 52 and f.hp > 0:
                        f.hp = max(0, f.hp - 25)
                        f.flash_timer = 15
                        gb['bite_cd'][fid] = 90
            giant_bugs = [gb for gb in giant_bugs if gb['life'] > 0]

            # Hacker: spawn black hole
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_black_hole:
                    shooter.pending_black_hole = False
                    black_holes.append(BlackHole(
                        shooter.x + shooter.facing * 30,
                        shooter.y - 60, shooter.facing, shooter))

            # Update black holes
            for bh in black_holes:
                bh.update()
                if bh.alive:
                    victim = p2 if bh.owner is p1 else p1
                    bh.pull_toward(victim)
                    if bh.collides(victim):
                        if victim.char.get("armor_proj"):
                            bh.alive = False
                        elif victim.char.get("deflect_proj"):
                            bh.vx = -bh.vx; bh.owner = victim
                        else:
                            victim.hp = 0
                            bh.alive  = False
            black_holes = [bh for bh in black_holes if bh.alive]

            # 8-Bit Wasp: place bug spawner
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bug_spawner:
                    shooter.pending_bug_spawner = False
                    bug_spawners.append({'x': float(shooter.x), 'owner': shooter,
                                         'life': FPS * 10, 'spawn_cd': FPS * 3})

            # Update bug spawners
            for bsp in bug_spawners:
                bsp['life'] -= 1
                if bsp['spawn_cd'] > 0:
                    bsp['spawn_cd'] -= 1
                elif bsp['life'] > 0:
                    victim = p2 if bsp['owner'] is p1 else p1
                    nb = ComputerBug()
                    nb.x = float(bsp['x'])
                    spawned_bugs.append({'bug': nb, 'target': victim})
                    bsp['spawn_cd'] = FPS * 3
            bug_spawners = [bsp for bsp in bug_spawners if bsp['life'] > 0]

            # Black Widow: spawn wall-crawling bugs
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_widow_bugs:
                    shooter.pending_widow_bugs = False
                    for _wx in (40.0, float(WIDTH - 40)):
                        nb = ComputerBug()
                        nb.x = _wx
                        spawned_bugs.append({'bug': nb, 'target': victim})

            # Update spawned bugs
            _prev_sb = len(spawned_bugs)
            for sb in spawned_bugs:
                _psr = next((_pf for _pf in (p1, p2) if _pf.possess_timer > 0 and _pf.possess_entity and _pf.possess_entity[0] == 'bug' and _pf.possess_entity[1] is sb['bug']), None)
                if _psr:
                    _pc = P1_CTRL if _psr is p1 else P2_CTRL
                    _opc = p2 if _psr is p1 else p1
                    b = sb['bug']
                    b.leg_t += 0.2
                    if b.bite_timer > 0: b.bite_timer -= 1
                    spd = ComputerBug.SPEED * 2.5
                    if keys[_pc['left']]:  b.vx = -spd; b.x -= spd
                    if keys[_pc['right']]: b.vx =  spd; b.x += spd
                    b.x = max(30.0, min(float(WIDTH - 30), b.x))
                    if (keys[_pc['punch']] or keys[_pc['kick']]) and b.bite_timer == 0:
                        if abs(b.x - _opc.x) < ComputerBug.BITE_RANGE + 20 and abs(b.y - _opc.y) < 70:
                            _opc.hp = max(0, _opc.hp - ComputerBug.BITE_DMG * 3)
                            _opc.flash_timer = 8
                            b.bite_timer = ComputerBug.BITE_COOLDOWN // 2
                else:
                    sb['bug'].update(sb['target'])
            spawned_bugs = [sb for sb in spawned_bugs if sb['bug'].alive]
            _computer_bug_kills_flag[0] += _prev_sb - len(spawned_bugs)

            # Poltergeist: player takes direct control of nearest entity for 5s
            for _possessor, _victim in [(p1, p2), (p2, p1)]:
                if not _possessor.pending_possess:
                    continue
                _possessor.pending_possess = False
                _possessed = False
                for _sn in jungle_snakes:
                    if _sn.alive:
                        _possessor.possess_entity = ('snake', _sn)
                        _possessor.possess_timer  = FPS * 5
                        _possessed = True
                        break
                if not _possessed:
                    for _be in spawned_bugs + [{'bug': b} for b in computer_bugs if b.alive]:
                        _possessor.possess_entity = ('bug', _be['bug'])
                        _possessor.possess_timer  = FPS * 5
                        _possessed = True
                        break
                if not _possessed:
                    for _cl in clones:
                        _possessor.possess_entity = ('clone', _cl['fighter'])
                        _possessor.possess_timer  = FPS * 5
                        _possessed = True
                        break
                if not _possessed:
                    _sp_list = sorted(springs, key=lambda s: abs(s.x - _victim.x))
                    if _sp_list:
                        _possessor.possess_entity = ('spring', _sp_list[0])
                        _possessor.possess_timer  = FPS * 5
                        _possessed = True
                if not _possessed:
                    if platforms:
                        _possessor.possess_entity = ('platform', min(platforms, key=lambda p: abs(p.x - _victim.x)))
                        _possessor.possess_timer  = FPS * 5
                        _possessed = True
                if not _possessed:
                    _victim.confuse_frames = max(_victim.confuse_frames, FPS * 3)

            # Spawn bouncing balls from bounce_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing * 30,
                                                     shooter.y - 60, shooter.facing, shooter))

            # Update bouncing balls and check collisions
            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    victim = p2 if bb.owner is p1 else p1
                    if bb.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6
                        else:
                            victim.take_proj_dmg(10)
                            victim.flash_timer = 8
                        bb.hit_cd = BouncingBall.HIT_CD
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            # Spawn scrolls from scroll_kick (Scrollmaster)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_scroll:
                    shooter.pending_scroll = False
                    scrolls.append(Scroll(shooter.x + shooter.facing * 30,
                                          shooter.y - 60, shooter.facing, shooter))

            # Spawn totem poles from totem_kick (Great Totem Spirit)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_totem:
                    shooter.pending_totem = False
                    for dx in (-160, -80, 0, 80, 160):
                        totems.append(TotemPole(victim.x + dx))
            for t in totems:
                t.update()
                if t.hit_cd == 0:
                    for victim in (p1, p2):
                        if t.collides(victim):
                            victim.take_proj_dmg(TotemPole.DMG)
                            victim.flash_timer = 8
                            t.hit_cd = TotemPole.HIT_CD
                            if victim is p1 and p1.hp <= 0:
                                _totem_kill_flag[0] = True
                            break
            totems = [t for t in totems if t.alive]

            # Spawn remote controllers from remote_kick (Rage Quitter)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_remote:
                    shooter.pending_remote = False
                    remotes.append(RemoteController(shooter.x + shooter.facing * 30,
                                                    shooter.y - 60, shooter.facing))
            for r in remotes:
                r.update()
                if not r.hit:
                    for victim in (p1, p2):
                        if r.collides(victim):
                            victim.take_proj_dmg(RemoteController.DMG)
                            victim.flash_timer = 20
                            r.hit = True; r.alive = False; break
            remotes = [r for r in remotes if r.alive]

            # Spawn apples from apple_kick (Gravity)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_apple:
                    shooter.pending_apple = False
                    for i in range(20):
                        apples.append(Apple(victim.x + random.randint(-200, 200)))
            for ap in apples:
                ap.update()
                if ap.hit_cd == 0:
                    for victim in (p1, p2):
                        if ap.collides(victim):
                            victim.take_proj_dmg(Apple.DMG)
                            victim.flash_timer = 6
                            ap.hit_cd = Apple.HIT_CD; break
            apples = [ap for ap in apples if ap.alive]

            # Spawn venom beans from venom_kick (Spitting Cobra)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_venom:
                    shooter.pending_venom = False
                    venoms.append(VenomBean(shooter.x + shooter.facing * 30,
                                            shooter.y - 60, shooter.facing, shooter))
            for vb in venoms:
                vb.update()
                if not vb.hit:
                    victim = p2 if vb.owner is p1 else p1
                    if vb.collides(victim):
                        if victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4; vb.alive = False
                        elif victim.char.get("armor_proj"):
                            vb.alive = False
                        elif victim.char.get("deflect_proj"):
                            vb.vx = -vb.vx; vb.owner = victim
                        else:
                            victim.hp = max(0, victim.hp - VenomBean.DMG)
                            victim.flash_timer = 8
                            if not victim.char.get("immune"):
                                if victim.poison_frames == 0: victim.poison_tick = 180
                                victim.poison_frames = max(victim.poison_frames, 360)
                            vb.hit = True; vb.alive = False
            venoms = [vb for vb in venoms if vb.alive]

            # Spawn and update music notes (Bard)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_note:
                    shooter.pending_note = False
                    notes.append(MusicNote(shooter.x + shooter.facing * 30,
                                           shooter.y - 60, shooter.facing, shooter))
            for nt in notes:
                nt.update()
                if nt.alive:
                    victim = p2 if nt.owner is p1 else p1
                    if nt.collides(victim):
                        if victim.char.get("armor_proj"):
                            nt.alive = False
                        elif victim.char.get("deflect_proj"):
                            nt.vx = -nt.vx; nt.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; nt.alive = False
                        else:
                            victim.take_proj_dmg(MusicNote.DMG)
                            victim.flash_timer = 8
                            if not victim.char.get("immune"):
                                victim.hurt_timer = max(victim.hurt_timer, 120)
                            nt.alive = False
            notes = [nt for nt in notes if nt.alive]

            # Update scrolls and check collisions
            for sc in scrolls:
                sc.update()
                if sc.alive and sc.hit_cd == 0:
                    victim = p2 if sc.owner is p1 else p1
                    if sc.collides(victim):
                        victim.take_proj_dmg(Scroll.DMG)
                        victim.flash_timer = 8
                        sc.hit_cd = Scroll.HIT_CD
            scrolls = [sc for sc in scrolls if sc.alive]

            # Spawn snake hooks from grapple_kick (Hooker)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_hook:
                    shooter.pending_hook = False
                    hooks.append(SnakeHook(
                        shooter.x + shooter.facing * 20, shooter.y - 60,
                        victim.x, victim.y - 60, shooter))

            # Update snake hooks and pull on hit
            for h in hooks:
                h.update()
                if h.alive:
                    victim = p2 if h.owner is p1 else p1
                    if h.collides(victim):
                        pull_dir = 1 if h.owner.x > victim.x else -1
                        if not victim.bubble_shield:
                            victim.knockback = pull_dir * 22
                            victim.take_proj_dmg(6)
                        victim.flash_timer = 8
                        h.alive = False
            hooks = [h for h in hooks if h.alive]

            # Pumpkins (Headless Horseman)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_pumpkin or shooter.pending_jack_pumpkin:
                    shooter.pending_pumpkin = False
                    shooter.pending_jack_pumpkin = False
                    pumpkins.append(Pumpkin(
                        shooter.x + shooter.facing * 24, shooter.y - 80,
                        shooter.facing, shooter))
                if shooter.pending_jack_seed:
                    shooter.pending_jack_seed = False
                    jack_seeds.append(PumpkinSeed(shooter.x + shooter.facing * 24,
                                                  shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_fruit_attack:
                    fa = shooter.pending_fruit_attack
                    shooter.pending_fruit_attack = None
                    _fx = shooter.x + shooter.facing * 30
                    _fy = shooter.y - 60
                    if fa[0] == 'cranberry_burst':
                        for _ci in range(4):
                            fruit_projs.append(FruitProj(_fx, _fy + _ci * 5,
                                               shooter.facing, shooter, 'cranberry'))
                    elif fa[0] == 'grape_rain':
                        for _gi in range(7):
                            gx = random.randint(50, WIDTH - 50)
                            fruit_projs.append(FruitProj(gx, -20, shooter.facing,
                                               shooter, 'grape', vy=4.0 + random.random() * 2))
                    elif fa[0] == 'coal':
                        coal_projs.append(CoalProj(_fx, _fy, shooter.facing, shooter, fa[1]))
                    else:
                        fruit_projs.append(FruitProj(_fx, _fy, shooter.facing, shooter, fa[0]))
            for js in jack_seeds:
                js.update()
                if js.alive:
                    victim = p2 if js.owner is p1 else p1
                    if js.collides(victim):
                        victim.take_proj_dmg(PumpkinSeed.DMG)
                        victim.flash_timer = max(victim.flash_timer, 8)
                        js.alive = False
            jack_seeds = [js for js in jack_seeds if js.alive]
            for fp in fruit_projs:
                fp.update()
                if fp.alive:
                    victim = p2 if fp.owner is p1 else p1
                    if fp.collides(victim):
                        _apply_fruit_hit(victim, fp)
                        fp.alive = False
            fruit_projs = [fp for fp in fruit_projs if fp.alive]
            for cp in coal_projs:
                cp.update()
                if cp.alive:
                    victim = p2 if cp.owner is p1 else p1
                    if cp.collides(victim):
                        _apply_coal_hit(victim, cp)
                        cp.alive = False
            coal_projs = [cp for cp in coal_projs if cp.alive]
            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    victim = p2 if pk.owner is p1 else p1
                    if math.hypot(pk.x - victim.x, pk.y - (victim.y - 60)) < pk.EXPLODE_RADIUS:
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(pk.EXPLODE_DMG)
                        victim.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    victim = p2 if pk.owner is p1 else p1
                    if pk.collides(victim):
                        pk._explode()
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Whips (Whipper)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_whip:
                    shooter.pending_whip = False
                    whips.append(Whip(
                        shooter.x + shooter.facing * 28, shooter.y - 60,
                        shooter.facing, shooter))
            for w in whips:
                w.update()
                if w.can_hit():
                    victim = p2 if w.owner is p1 else p1
                    if w.collides(victim):
                        victim.take_proj_dmg(w.DMG)
                        victim.flash_timer = 10
                        victim.knockback = w.facing * 14
                        w.hit_done = True
            whips = [w for w in whips if w.alive]

            # Ink Brush clones
            for shooter, foe in [(p1, p2), (p2, p1)]:
                if shooter.pending_ink_clone:
                    shooter.pending_ink_clone = False
                    cf = AIFighter(shooter.x + shooter.facing * 55, shooter.char, -shooter.facing, 'medium')
                    cf.hp = max(1, shooter.hp)
                    cf.color = shooter.color
                    cf.no_attack = True
                    clones.append({'fighter': cf, 'timer': FPS * 8, 'target': foe, 'ink': True})

            # Kitsune barrage — 9 shots in 9 directions
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_kitsune:
                    shooter.pending_kitsune = False
                    for i in range(9):
                        angle = i * 40.0   # 40-degree spacing
                        kitsune_shots.append(KitsuneShot(shooter.x, shooter.y - 70, angle, shooter))
            for ks in kitsune_shots:
                ks.update()
                if ks.alive:
                    victim = p2 if ks.owner is p1 else p1
                    if ks.collides(victim):
                        if victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4; ks.alive = False
                        elif victim.char.get("armor_proj"):
                            ks.alive = False
                        elif victim.char.get("deflect_proj"):
                            ks.vx = -ks.vx; ks.vy = -ks.vy; ks.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; ks.alive = False
                        else:
                            victim.hp = max(0, victim.hp - KitsuneShot.DMG)
                            victim.flash_timer = 8
                            ks.alive = False
            kitsune_shots = [ks for ks in kitsune_shots if ks.alive]

            # Riptide water balls
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_water_ball:
                    shooter.pending_water_ball = False
                    water_balls.append(WaterBall(shooter.x + shooter.facing * 30,
                                                 shooter.y - 60, shooter.facing, shooter))
            for wb in water_balls:
                wb.update()
                if wb.alive:
                    victim = p2 if wb.owner is p1 else p1
                    if wb.collides(victim):
                        if victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4; wb.alive = False
                        elif victim.char.get("armor_proj"):
                            wb.alive = False
                        elif victim.char.get("deflect_proj"):
                            wb.vx = -wb.vx; wb.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; wb.alive = False
                        else:
                            victim.hp = max(0, victim.hp - WaterBall.DMG)
                            victim.flash_timer = 8
                            wb.alive = False
            water_balls = [wb for wb in water_balls if wb.alive]

            # The Creator — spawn timed platform on kick
            for shooter in (p1, p2):
                if shooter.pending_creator_platform:
                    shooter.pending_creator_platform = False
                    px = int(shooter.x + shooter.facing * 80) - 60
                    py = int(shooter.y) - 60
                    py = max(60, min(GROUND_Y - 20, py))
                    platforms.append(TimedPlatform(px, py, w=120, lifetime=FPS * 5))

            # Medusa freeze laser — applies freeze instead of damage
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if (shooter.char.get("freeze_laser") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    correct_side = ((shooter.facing == 1  and victim.x > shooter.x) or
                                    (shooter.facing == -1 and victim.x < shooter.x))
                    if correct_side and abs((victim.y - 60) - laser_y) < 35:
                        if not victim.char.get("immune"):
                            victim.freeze_frames = max(victim.freeze_frames, 180)  # 3s freeze
                        victim.flash_timer = 4
                        shooter.laser_hit_cd = 30   # 0.5s between freeze applications

            # Beekeeper bee swarm
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bee:
                    shooter.pending_bee = False
                    for dvy in (-4, -2, 0, 2, 4):
                        bee_shots.append(BeeShot(shooter.x + shooter.facing * 30,
                                                 shooter.y - 60, shooter.facing, shooter, vy=dvy))
            for b in bee_shots:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        if victim.char.get("armor_proj"):
                            b.alive = False
                        elif victim.char.get("deflect_proj"):
                            b.vx = -b.vx; b.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; b.alive = False
                        else:
                            victim.take_proj_dmg(BeeShot.DMG)
                            victim.flash_timer = 6
                            b.alive = False
            bee_shots = [b for b in bee_shots if b.alive]

            # Shifter snipe shots
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_snipe:
                    shooter.pending_snipe = False
                    snipe_shots.append(SnipeShot(shooter.x + shooter.facing * 30,
                                                 shooter.y - 80, shooter.facing, shooter))
            for s in snipe_shots:
                s.update()
                if s.alive:
                    victim = p2 if s.owner is p1 else p1
                    if s.collides(victim):
                        if victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4; s.alive = False
                        elif victim.char.get("armor_proj"):
                            s.alive = False
                        elif victim.char.get("deflect_proj"):
                            s.vx = -s.vx; s.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; s.alive = False
                        else:
                            victim.hp = max(0, victim.hp - SnipeShot.DMG)
                            victim.flash_timer = 10
                            s.alive = False
            snipe_shots = [s for s in snipe_shots if s.alive]

            # Joker chaos effect
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_chaos:
                    shooter.pending_chaos = False
                    if not victim.char.get("immune"):
                        effect = random.choice(['freeze', 'fire', 'shock', 'confuse', 'squish'])
                        if effect == 'freeze':
                            victim.freeze_frames = max(victim.freeze_frames, 180)
                        elif effect == 'fire':
                            if victim.fire_frames == 0: victim.fire_tick = 480
                            victim.fire_frames   = max(victim.fire_frames, 480)
                        elif effect == 'shock':
                            victim.shock_frames  = max(victim.shock_frames, 240)
                        elif effect == 'confuse':
                            victim.confuse_frames = max(victim.confuse_frames, 180)
                        elif effect == 'squish':
                            victim.squish_frames  = max(victim.squish_frames, 180)
                        victim.flash_timer = 20

            # Time Lord freeze
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_time_freeze:
                    shooter.pending_time_freeze = False
                    if not victim.char.get("immune"):
                        victim.freeze_frames = max(victim.freeze_frames, 240)  # 4 seconds
                        victim.flash_timer   = 20

            # Toxic aura — proximity poison
            for toxic, victim in [(p1, p2), (p2, p1)]:
                if (toxic.char.get("toxic_aura") and victim.contact_cooldown == 0
                        and math.hypot(toxic.x - victim.x, (toxic.y - 60) - (victim.y - 60)) < 80):
                    victim.take_proj_dmg(2)
                    victim.flash_timer = 4
                    victim.contact_cooldown = 90
                    if not victim.char.get("immune"):
                        if victim.poison_frames == 0: victim.poison_tick = 180
                        victim.poison_frames = max(victim.poison_frames, 360)

            # Snake body segment contact damage
            for snake, victim in [(p1, p2), (p2, p1)]:
                if snake.char.get("snake") and snake.snake_contact_cd == 0:
                    for seg in snake.snake_segs[8:]:   # skip the head region
                        if math.hypot(seg[0] - victim.x, seg[1] - (victim.y - 60)) < 30:
                            victim.take_proj_dmg(6)
                            victim.flash_timer = 8
                            snake.snake_contact_cd = 60
                            break

            # Life Drain: passive HP drain from nearby opponent every 2 seconds
            for attacker, victim in [(p1, p2), (p2, p1)]:
                if attacker.char.get("drain_aura") and attacker.hp > 0:
                    if attacker.drain_aura_timer > 0:
                        attacker.drain_aura_timer -= 1
                    elif abs(attacker.x - victim.x) < 130:
                        attacker.drain_aura_timer = FPS * 2
                        if not victim.char.get("immune"):
                            victim.take_proj_dmg(1, flash=False)
                            attacker.hp = min(attacker.max_hp, attacker.hp + 1)

            # Blazer: fire aura burns nearby opponent every 2 seconds
            for attacker, victim in [(p1, p2), (p2, p1)]:
                if attacker.char.get("fire_aura") and attacker.hp > 0:
                    if attacker.fire_aura_timer > 0:
                        attacker.fire_aura_timer -= 1
                    elif abs(attacker.x - victim.x) < 80:
                        attacker.fire_aura_timer = FPS * 2
                        if not victim.char.get("immune"):
                            victim.take_proj_dmg(6)
                            if victim.fire_frames == 0: victim.fire_tick = 120
                            victim.fire_frames = max(victim.fire_frames, 180)

            # Volt: auto-shock nearby opponent every 3 seconds
            for attacker, victim in [(p1, p2), (p2, p1)]:
                if attacker.char.get("shock_aura") and attacker.hp > 0:
                    if attacker.shock_aura_timer > 0:
                        attacker.shock_aura_timer -= 1
                    else:
                        attacker.shock_aura_timer = FPS * 3
                        if abs(attacker.x - victim.x) < 140:
                            victim.take_proj_dmg(8)
                            victim.flash_timer = 10
                            if not victim.char.get("immune"):
                                victim.shock_frames = max(victim.shock_frames, 240)

            # Nick of Time: becomes mega-unhittable with 10 seconds remaining
            for f in (p1, p2):
                if f.char.get("nick_of_time"):
                    f.nick_dodge_active = (timer <= FPS * 10)

            # Buffer: gains +1 speed/HP/damage every second
            for f in (p1, p2):
                if f.char.get("buffer_char") and f.hp > 0:
                    if f.buffer_timer > 0:
                        f.buffer_timer -= 1
                    else:
                        f.buffer_timer = FPS
                        f.speed_boost  = getattr(f, 'speed_boost', 1.0) + 0.05
                        f.hp           = min(f.hp + 1, f.max_hp + f.buffer_stacks)
                        f.punch_boost  = getattr(f, 'punch_boost', 0) + 1
                        f.kick_boost   = getattr(f, 'kick_boost',  0) + 1
                        f.buffer_stacks = getattr(f, 'buffer_stacks', 0) + 1

            # Cursed: loses 1 HP every second
            for f in (p1, p2):
                if f.char.get("cursed_drain") and f.hp > 0:
                    if f.cursed_timer > 0:
                        f.cursed_timer -= 1
                    else:
                        f.cursed_timer = FPS
                        f.hp = max(1, f.hp - 1)

            # Chainsaw Man: rapid proximity damage
            for attacker, victim in [(p1, p2), (p2, p1)]:
                if attacker.char.get("chainsaw") and attacker.hp > 0:
                    if attacker.chainsaw_cd > 0:
                        attacker.chainsaw_cd -= 1
                    elif abs(attacker.x - victim.x) < 50:
                        victim.take_proj_dmg(4)
                        victim.flash_timer = 4
                        attacker.chainsaw_cd = 15

            # Necromancer: revive on first death
            for f in (p1, p2):
                if f.hp <= 0 and f.char.get("undead") and not f.undead_used:
                    f.hp          = int(f.max_hp * 0.4)
                    f.undead_used = True
                    f.flash_timer = 30

            # Smoochie: revive up to 5 times at 25% HP
            for f in (p1, p2):
                if f.hp <= 0 and f.char.get("smoochie_revivals") and f.smoochie_revivals < 5:
                    f.hp                 = int(f.max_hp * 0.25)
                    f.smoochie_revivals += 1
                    f.flash_timer        = 35

            # Revenant: revive up to 2 times at 30% HP
            for f in (p1, p2):
                if f.hp <= 0 and f.char.get("revenant") and f.revenant_count < 2:
                    f.hp             = int(f.max_hp * 0.3)
                    f.revenant_count += 1
                    f.flash_timer    = 30

            # Phoenix: revive once at 30 HP
            for f in (p1, p2):
                if f.hp <= 0 and f.char.get("phoenix_revive") and not f.phoenix_used:
                    f.hp          = 30
                    f.phoenix_used = True
                    f.flash_timer = 40

            # Death Defyer: 75% chance to respawn at full HP (once per life)
            for f in (p1, p2):
                if f.hp <= 0 and f.char.get("death_defyer") and not f.death_defyer_used:
                    f.death_defyer_used = True
                    if random.random() < 0.75:
                        f.hp          = f.max_hp
                        f.flash_timer = 40

            # Kamikaze: explode on first death
            for kamikaze, victim in [(p1, p2), (p2, p1)]:
                if (kamikaze.char.get("explode_death") and kamikaze.hp <= 0
                        and not kamikaze.kamikaze_exploded):
                    kamikaze.kamikaze_exploded = True
                    if math.hypot(kamikaze.x - victim.x,
                                  (kamikaze.y - 60) - (victim.y - 60)) < 150:
                        victim.take_proj_dmg(60)
                        victim.flash_timer = 20

            # Pyro auto-fire balls
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_autofire:
                    shooter.pending_autofire = False
                    fire_balls.append(FireBall(shooter.x + shooter.facing * 30,
                                               shooter.y - 60, shooter.facing, shooter))
            # Nian — wide fire breath cone
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_nian_breath:
                    shooter.pending_nian_breath = False
                    nian_breaths.append(NianBreath(shooter.x + shooter.facing * 18,
                                                   shooter.y - 60, shooter.facing, shooter))
            for nb in nian_breaths:
                nb.update()
                for shooter, victim in [(p1, p2), (p2, p1)]:
                    if nb.owner is shooter and id(victim) not in nb._hit and nb.in_cone(victim):
                        nb._hit.add(id(victim))
                        victim.take_proj_dmg(NianBreath.DMG)
                        if not victim.char.get("immune"):
                            victim.fire_frames = max(victim.fire_frames, NianBreath.FIRE_FRAMES)
                        victim.flash_timer = max(victim.flash_timer, 12)
            nian_breaths = [nb for nb in nian_breaths if nb.alive]

            # Clover — kick summons a snake
            for fighter in (p1, p2):
                if fighter.pending_clover_snake:
                    fighter.pending_clover_snake = False
                    jungle_snakes.append(JungleSnake())
                if fighter.pending_golden_snake:
                    fighter.pending_golden_snake = False
                    jungle_snakes.append(GoldenJungleSnake())
            # Solara — sun beams (shock + burn)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_sun_beam:
                    shooter.pending_sun_beam = False
                    sun_beams.append(SunBeam(shooter.x + shooter.facing * 30,
                                             shooter.y - 60, shooter.facing, shooter))
            for sb in sun_beams:
                sb.update()
                if sb.alive:
                    victim = p2 if sb.owner is p1 else p1
                    if sb.collides(victim):
                        if victim.char.get("tombstone_reflect"):
                            victim.flash_timer = 4
                            sb.owner.hp = max(0, sb.owner.hp - SunBeam.DMG)
                            sb.owner.flash_timer = max(sb.owner.flash_timer, 14)
                        elif victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4
                        elif victim.char.get("deflect_proj"):
                            sb.vx = -sb.vx; sb.owner = victim; continue
                        elif victim.bubble_shield:
                            victim.flash_timer = 6
                        else:
                            victim.take_proj_dmg(SunBeam.DMG)
                            victim.shock_frames = max(victim.shock_frames, 120)
                            if not victim.char.get("immune"):
                                if victim.fire_frames == 0: victim.fire_tick = 480
                                victim.fire_frames = max(victim.fire_frames, 300)
                            if sb.owner.char.get("performer_beam") and not victim.char.get("immune"):
                                if victim.poison_frames == 0: victim.poison_tick = 240
                                victim.poison_frames = max(victim.poison_frames, 180)
                                victim.freeze_frames = max(victim.freeze_frames, 60)
                        sb.alive = False
            sun_beams = [sb for sb in sun_beams if sb.alive]
            # Stickman of Liberty — dove companion + bombs
            for shooter in (p1, p2):
                if shooter.pending_liberty_dove:
                    shooter.pending_liberty_dove = False
                    liberty_doves.append(LibertyDove(shooter.x, shooter.y, shooter))
            for dove in liberty_doves:
                dove.update()
                if dove.pending_bomb:
                    dove.pending_bomb = False
                    liberty_bombs.append({'x': dove.x, 'y': dove.y, 'vy': 0.0, 'alive': True, 'owner': dove.owner})
            liberty_doves = [d for d in liberty_doves if d.alive]
            for lb in liberty_bombs:
                lb['vy'] = min(lb['vy'] + 0.9, 22)
                lb['y'] += lb['vy']
                if lb['y'] >= GROUND_Y - 4:
                    for victim in (p1, p2):
                        if victim is not lb['owner'] and abs(victim.x - lb['x']) < 65:
                            victim.take_proj_dmg(15)
                            victim.flash_timer = max(victim.flash_timer, 14)
                    lb['alive'] = False
            liberty_bombs = [lb for lb in liberty_bombs if lb['alive']]
            # Bookzworm — orbiting book aura
            for bz, victim in [(p1, p2), (p2, p1)]:
                if bz.char.get("bookzworm_books") and bz.hp > 0 and bz.bookzworm_book_cd <= 0:
                    dist = math.hypot(victim.x - bz.x, (victim.y - 60) - (bz.y - 60))
                    if dist < int(85 * bz.draw_scale):
                        victim.take_proj_dmg(6)
                        victim.flash_timer = max(victim.flash_timer, 10)
                        bz.bookzworm_book_cd = 50
            for fb in fire_balls:
                fb.update()
                if fb.alive:
                    victim = p2 if fb.owner is p1 else p1
                    if fb.collides(victim):
                        if victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4; fb.alive = False
                        elif victim.char.get("armor_proj"):
                            fb.alive = False
                        elif victim.char.get("deflect_proj"):
                            fb.vx = -fb.vx; fb.owner = victim
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; fb.alive = False
                        else:
                            victim.hp = max(0, victim.hp - FireBall.DMG)
                            victim.flash_timer = 8
                            if not victim.char.get("immune"):
                                if victim.fire_frames == 0: victim.fire_tick = 480
                                victim.fire_frames = max(victim.fire_frames, 480)
                            fb.alive = False
            fire_balls = [fb for fb in fire_balls if fb.alive]

            # Thunder God bolts + Storm Caller random bolts
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_thunder:
                    shooter.pending_thunder = False
                    thunder_bolts.append(ThunderBolt(victim.x, shooter))
                if shooter.pending_storm:
                    shooter.pending_storm = False
                    thunder_bolts.append(ThunderBolt(random.randint(80, WIDTH - 80), shooter))
            # Quaker shockwave — landing deals area damage
            for attacker, victim in [(p1, p2), (p2, p1)]:
                if attacker.quake_pending:
                    attacker.quake_pending = False
                    if abs(attacker.x - victim.x) < 140 and victim.hp > 0:
                        victim.take_proj_dmg(15)
                        victim.flash_timer = 12
                        victim.knockback = (1 if victim.x > attacker.x else -1) * 8
            for tb in thunder_bolts:
                tb.update()
                if tb.alive and not tb.hit:
                    victim = p2 if tb.owner is p1 else p1
                    if tb.collides(victim):
                        if victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4
                        elif victim.char.get("armor_proj"):
                            pass
                        elif victim.bubble_shield:
                            victim.flash_timer = 6
                        else:
                            victim.hp = max(0, victim.hp - ThunderBolt.DMG)
                            victim.flash_timer = 12
                            if not victim.char.get("immune"):
                                victim.shock_frames = max(victim.shock_frames, 180)
                        tb.hit = True
            thunder_bolts = [tb for tb in thunder_bolts if tb.alive]

            # Trap Master mines
            for planter, victim in [(p1, p2), (p2, p1)]:
                if planter.pending_mine:
                    planter.pending_mine = False
                    mines.append({'x': float(planter.x), 'y': float(GROUND_Y),
                                  'owner': planter, 'life': FPS * 8, 'arm': 25})
            new_mines = []
            for mn in mines:
                if mn['arm'] > 0: mn['arm'] -= 1
                mn['life'] -= 1
                if mn['arm'] == 0:
                    victim = p2 if mn['owner'] is p1 else p1
                    if abs(mn['x'] - victim.x) < 28 and victim.hp > 0:
                        victim.take_proj_dmg(25)
                        victim.flash_timer = 15
                        mn['life'] = 0
                if mn['life'] > 0:
                    new_mines.append(mn)
            mines = new_mines

            # Fault Line ground shockwaves
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_quake_wave:
                    shooter.pending_quake_wave = False
                    quake_waves.append({'x': shooter.x + shooter.facing * 30,
                                        'y': float(GROUND_Y), 'vx': shooter.facing * 7,
                                        'life': 90, 'owner': shooter, 'hit_cd': 0})
            new_qw = []
            for qw in quake_waves:
                qw['x'] += qw['vx']
                qw['life'] -= 1
                if qw['hit_cd'] > 0:
                    qw['hit_cd'] -= 1
                victim = p2 if qw['owner'] is p1 else p1
                if qw['hit_cd'] == 0 and abs(qw['x'] - victim.x) < 32 and victim.hp > 0:
                    victim.take_proj_dmg(15)
                    victim.flash_timer = 10
                    qw['hit_cd'] = 30
                if qw['life'] > 0 and 0 <= qw['x'] <= WIDTH:
                    new_qw.append(qw)
            quake_waves = new_qw

            # Yellowstone — kick spawns 10 geysers across the stage
            for shooter in (p1, p2):
                if shooter.pending_yellowstone_geysers:
                    shooter.pending_yellowstone_geysers = False
                    for i in range(10):
                        gx = 60 + (WIDTH - 120) * i / 9 + random.uniform(-25, 25)
                        gx = max(60.0, min(float(WIDTH - 60), gx))
                        yellowstone_geysers.append({'x': gx, 'age': 0, 'alive': True,
                                                    'owner': shooter, 'hit': False})
            new_gy = []
            for gy in yellowstone_geysers:
                gy['age'] += 1
                if gy['age'] <= 60:
                    new_gy.append(gy)
                    victim = p2 if gy['owner'] is p1 else p1
                    if not gy['hit'] and 22 <= gy['age'] <= 40:
                        if abs(victim.x - gy['x']) < 52 and victim.hp > 0:
                            victim.take_proj_dmg(12)
                            victim.flash_timer = max(victim.flash_timer, 10)
                            gy['hit'] = True
            yellowstone_geysers = new_gy

            # Druid plant spikes
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_plant:
                    shooter.pending_plant = False
                    plant_spikes.append(PlantSpike(victim.x, shooter))
            for ps in plant_spikes:
                ps.update()
                if ps.alive:
                    victim = p2 if ps.owner is p1 else p1
                    if ps.collides(victim):
                        if victim.char.get("mega_unhittable") and random.random() < 0.999:
                            victim.flash_timer = 4; ps.alive = False
                        elif victim.char.get("armor_proj"):
                            ps.alive = False
                        elif victim.bubble_shield:
                            victim.flash_timer = 6; ps.alive = False
                        else:
                            victim.hp = max(0, victim.hp - PlantSpike.DMG)
                            victim.flash_timer = 12
                            ps.alive = False
            plant_spikes = [ps for ps in plant_spikes if ps.alive]

            # Bomb character: spawn a center-screen bomb every 5 seconds
            for _p in (p1, p2):
                if _p.char.get("bomb_character") and _p.hp > 0:
                    _p.bomb_spawn_timer -= 1
                    if _p.bomb_spawn_timer <= 0:
                        _bdmg = 200 if _p.char.get("nuke_bomb") else 100
                        active_bombs.append({'x': float(WIDTH // 2), 'y': float(GROUND_Y - 80), 'fuse': 120, 'dmg': _bdmg})
                        _p.bomb_spawn_timer = FPS * 5
            new_bombs = []
            for _bom in active_bombs:
                _bom['fuse'] -= 1
                if _bom['fuse'] <= 0:
                    for _victim in (p1, p2):
                        if math.hypot(_victim.x - _bom['x'], (_victim.y - 60) - _bom['y']) < 180:
                            _victim.hp = max(0, _victim.hp - _bom.get('dmg', 100))
                            _victim.flash_timer = 20
                    bomb_pops.append({'x': _bom['x'], 'y': _bom['y'], 't': 25})
                else:
                    new_bombs.append(_bom)
            active_bombs = new_bombs
            for _bp in bomb_pops:
                _bp['t'] -= 1
            bomb_pops = [bp for bp in bomb_pops if bp['t'] > 0]

            # Jungle snakes
            if is_jungle:
                snake_spawn_timer -= 1
                if snake_spawn_timer <= 0 and len(jungle_snakes) < 4:
                    jungle_snakes.append(JungleSnake())
                    snake_spawn_timer = random.randint(300, 480)
                for sn in jungle_snakes:
                    _psr = next((_pf for _pf in (p1, p2) if _pf.possess_timer > 0 and _pf.possess_entity and _pf.possess_entity[0] == 'snake' and _pf.possess_entity[1] is sn), None)
                    if _psr:
                        _pc = P1_CTRL if _psr is p1 else P2_CTRL
                        _opc = p2 if _psr is p1 else p1
                        sn.t += 1
                        if sn.bite_cd > 0: sn.bite_cd -= 1
                        if keys[_pc['left']]:  sn.x -= JungleSnake.SPEED * 2.5; sn.facing = -1
                        if keys[_pc['right']]: sn.x += JungleSnake.SPEED * 2.5; sn.facing =  1
                        sn.x = max(30.0, min(float(WIDTH - 30), sn.x))
                        if (keys[_pc['punch']] or keys[_pc['kick']]) and sn.bite_cd == 0:
                            if abs(sn.x - _opc.x) < JungleSnake.BITE_RANGE + 20 and abs(sn.y - _opc.y) < 80:
                                _opc.hp = max(0, _opc.hp - JungleSnake.BITE_DMG * 3)
                                _opc.flash_timer = 6
                                sn.bite_cd = JungleSnake.BITE_COOLDOWN // 2
                    else:
                        sn.update(p1, p2)
                _prev_sn = len(jungle_snakes)
                jungle_snakes = [sn for sn in jungle_snakes if sn.alive]
                _jungle_kills_flag[0] += _prev_sn - len(jungle_snakes)

            # Computer bugs
            if is_computer:
                bug_spawn_timer -= 1
                if bug_spawn_timer <= 0 and len(computer_bugs) < 5:
                    computer_bugs.append(ComputerBug())
                    bug_spawn_timer = random.randint(200, 360)
                for b in computer_bugs:
                    _psr = next((_pf for _pf in (p1, p2) if _pf.possess_timer > 0 and _pf.possess_entity and _pf.possess_entity[0] == 'bug' and _pf.possess_entity[1] is b), None)
                    if _psr:
                        _pc = P1_CTRL if _psr is p1 else P2_CTRL
                        _opc = p2 if _psr is p1 else p1
                        b.leg_t += 0.2
                        if b.bite_timer > 0: b.bite_timer -= 1
                        spd = ComputerBug.SPEED * 2.5
                        if keys[_pc['left']]:  b.vx = -spd; b.x -= spd
                        if keys[_pc['right']]: b.vx =  spd; b.x += spd
                        b.x = max(30.0, min(float(WIDTH - 30), b.x))
                        if (keys[_pc['punch']] or keys[_pc['kick']]) and b.bite_timer == 0:
                            if abs(b.x - _opc.x) < ComputerBug.BITE_RANGE + 20 and abs(b.y - _opc.y) < 70:
                                _opc.hp = max(0, _opc.hp - ComputerBug.BITE_DMG * 3)
                                _opc.flash_timer = 8
                                b.bite_timer = ComputerBug.BITE_COOLDOWN // 2
                    else:
                        target = min([p1, p2], key=lambda p: abs(p.x - b.x))
                        b.update(target)
                _prev_cb = len(computer_bugs)
                computer_bugs = [b for b in computer_bugs if b.alive]
                _computer_bug_kills_flag[0] += _prev_cb - len(computer_bugs)
                # Pencil: draw new platforms
                stage_pencil.update()
                drawn_count = sum(1 for p in platforms if isinstance(p, DrawnPlatform))
                if stage_pencil.pending_plat and drawn_count < StagePencil.MAX_PLATS:
                    stage_pencil.pending_plat = False
                    platforms.append(DrawnPlatform(int(stage_pencil.x) - 50, int(stage_pencil.y) + 20, w=100))
                # Eraser: wipe platforms it passes
                platforms = stage_eraser.update(platforms)
                # Update / expire DrawnPlatforms
                for p in platforms:
                    if isinstance(p, DrawnPlatform): p.update()
                platforms = [p for p in platforms if not (isinstance(p, DrawnPlatform) and not p.alive)]
                # Eraser contact damage
                for pf in (p1, p2):
                    if pf.hp > 0 and pf.contact_cooldown == 0:
                        if math.hypot(pf.x - stage_eraser.x, pf.y - stage_eraser.y) < 50:
                            pf.hp = max(0, pf.hp - 5)
                            pf.flash_timer = 8
                            pf.contact_cooldown = 60

            # Falling skulls (Underworld)
            if is_underworld:
                skull_spawn_timer -= 1
                if skull_spawn_timer <= 0 and len(falling_skulls) < 8:
                    falling_skulls.append(FallingSkull())
                    skull_spawn_timer = random.randint(120, 280)
                for sk in falling_skulls:
                    sk.update()
                    if sk.hit_cd == 0:
                        for victim in (p1, p2):
                            if sk.collides(victim):
                                victim.take_proj_dmg(sk.DMG)
                                victim.flash_timer = 10
                                sk.hit_cd = sk.HIT_CD

            timer -= 1
            if timer <= 0 or p1.hp <= 0 or p2.hp <= 0:
                # Jetpack unlock: p1 fell into void with 2–7 seconds remaining
                if p1.hp <= 0 and constants.STAGE_VOID and FPS * 2 <= timer <= FPS * 7:
                    _void_fall_timer_flag[0] = True
                # Nick of Time: p1 KO'd p2 with ≤1 second remaining
                if p2.hp <= 0 and p1.hp > 0 and 0 < timer <= FPS:
                    _nick_of_time_flag[0] = True
                game_over = True
                winner = p1 if p1.hp >= p2.hp else p2

            # Spawn powerups
            spawn_timer -= 1
            if spawn_timer <= 0 and len(powerups) < 3:
                powerups.append(Powerup())
                spawn_timer = random.randint(480, 720)   # 8-12 seconds

            # Everything powerup — poop out random powerups
            for f in (p1, p2):
                if f.poop_timer > 0 and f.poop_cd == 0:
                    pu = Powerup()
                    pu.x = f.x - f.facing * 20   # drop behind the player
                    pu.y = float(GROUND_Y - 14)
                    powerups.append(pu)
                    f.poop_cd = 30   # one poop every 0.5 seconds
            # Rainbow Man — drop a random powerup every 4 seconds
            for f in (p1, p2):
                if f.pending_rainbow_poop:
                    f.pending_rainbow_poop = False
                    pu = Powerup()
                    pu.x = f.x + random.choice((-30, 30))
                    pu.y = float(GROUND_Y - 14)
                    powerups.append(pu)

            # Magician attraction: pull all powerups slowly toward Magician fighters
            for f in (p1, p2):
                if f.char.get("magnet"):
                    for pu in powerups:
                        if not pu.picked_up:
                            dx = f.x - pu.x
                            dy = (f.y - 60) - pu.y
                            dist = math.hypot(dx, dy) or 1
                            speed = min(2.5, 300 / dist)   # faster when closer
                            pu.x += (dx / dist) * speed
                            pu.y += (dy / dist) * speed

            # Update & pickup
            for pu in powerups:
                pu.update()
                for fighter, foe in [(p1, p2), (p2, p1)]:
                    if not pu.picked_up and pu.collides(fighter):
                        _pu_target = foe if fighter.char.get("baddit") else fighter
                        if pu.spec['type'] == 'clone':
                            _clone_src = foe if fighter.char.get("baddit") else fighter
                            cf = AIFighter(_clone_src.x + 60 * _clone_src.facing,
                                           _clone_src.char, _clone_src.facing, 'hard')
                            cf.hp    = 80
                            cf.color = _clone_src.color
                            _clone_foe = fighter if fighter.char.get("baddit") else foe
                            clones.append({'fighter': cf, 'timer': 30 * FPS, 'target': _clone_foe})
                        else:
                            _pu_target.apply_powerup(pu.spec)
                            if (_pu_target is p1
                                    and pu.spec['type'] == 'heal'
                                    and pu.spec.get('amount', 0) < 0
                                    and p1.hp <= 0):
                                _p1_powerup_kill_flag[0] = True
                        if fighter.char.get("snake"):
                            fighter.snake_length += 2
                            fighter.kick_boost   += 2
                        # Track Everything powerup collections for Rainbow Man unlock
                        if pu.spec['name'] == 'Everything' and fighter is p1:
                            _everything_flag[0] += 1
                        pu.picked_up = True
                        break
            powerups = [pu for pu in powerups if not pu.picked_up]

        # Giant NPC hazard (Giants Among Us stage only)
        if giant_mode and not game_over:
            if _gnpc is None:
                _gnpc_spawn_cd -= 1
                if _gnpc_spawn_cd <= 0:
                    _from_left = random.choice([True, False])
                    _gnpc = {
                        "x":       float(-130 if _from_left else WIDTH + 130),
                        "facing":  1 if _from_left else -1,
                        "target_x": float(random.randint(WIDTH // 4, 3 * WIDTH // 4)),
                        "phase":   "walk",
                        "timer":   0,
                        "attack":  random.choice(["stomp", "sweep", "slam"]),
                        "hit_done": False,
                        "flash":   0,
                    }
            else:
                _gnpc["timer"] += 1
                _gspd = 4.5
                if _gnpc["phase"] == "walk":
                    _gnpc["x"] += _gspd * _gnpc["facing"]
                    if abs(_gnpc["x"] - _gnpc["target_x"]) < _gspd * 2:
                        _gnpc["phase"] = "attack"
                        _gnpc["timer"] = 0
                elif _gnpc["phase"] == "attack":
                    if _gnpc["timer"] == 28 and not _gnpc["hit_done"]:
                        for _af in (p1, p2):
                            if abs(_af.x - _gnpc["x"]) < 210:
                                _af.hp  = max(0, _af.hp - 22)
                                _af.vx += (_af.x - _gnpc["x"]) / 25
                                _af.vy  = -9
                                _af.flash_timer = max(_af.flash_timer, 14)
                        _gnpc["hit_done"] = True
                        _gnpc["flash"] = 14
                    if _gnpc["flash"] > 0:
                        _gnpc["flash"] -= 1
                    if _gnpc["timer"] >= 85:
                        _gnpc["phase"]   = "retreat"
                        _gnpc["facing"]  = -_gnpc["facing"]
                        _gnpc["timer"]   = 0
                elif _gnpc["phase"] == "retreat":
                    _gnpc["x"] += _gspd * _gnpc["facing"]
                    if _gnpc["x"] < -160 or _gnpc["x"] > WIDTH + 160:
                        _gnpc          = None
                        _gnpc_spawn_cd = 600

        # Casino coin rain
        if is_casino and not game_over:
            casino_coin_cd -= 1
            if casino_coin_cd <= 0:
                casino_coins.append({
                    "x": float(random.randint(60, WIDTH - 60)),
                    "y": 0.0, "vy": 3.0 + random.random() * 2,
                    "hit": set()
                })
                casino_coin_cd = random.randint(60, 120)
            for _cc in casino_coins:
                _cc["y"] += _cc["vy"]
                _cc["vy"] = min(10.0, _cc["vy"] + 0.15)
                for _cf2 in (p1, p2):
                    if id(_cf2) not in _cc["hit"] and abs(_cf2.x - _cc["x"]) < 30 and abs((_cf2.y - 60) - _cc["y"]) < 30:
                        _cf2.hp = max(0, _cf2.hp - 5)
                        _cf2.flash_timer = max(_cf2.flash_timer, 6)
                        _cc["hit"].add(id(_cf2))
            casino_coins = [c for c in casino_coins if c["y"] < GROUND_Y + 30]

        draw_bg(screen, stage_idx)
        # Draw giant NPC (Giants Among Us)
        if giant_mode and _gnpc is not None:
            _gn_act = 'walk' if _gnpc["phase"] in ("walk", "retreat") else 'punch'
            _gn_col = (255, 120, 30) if _gnpc["flash"] > 0 else (60, 160, 60)
            _gn_pt  = pygame.time.get_ticks() / 1000.0 * 0.15
            draw_stickman(screen, int(_gnpc["x"]), GROUND_Y, _gn_col,
                          _gnpc["facing"], _gn_act, _gn_pt, scale=4.2, char_name="Giant")
            if _gnpc["phase"] == "attack" and not _gnpc["hit_done"]:
                _warn_prog = min(1.0, _gnpc["timer"] / 28)
                _warn_r    = int(210 * _warn_prog)
                if _warn_r > 4:
                    _wsurf = pygame.Surface((_warn_r*2+4, _warn_r*2+4), pygame.SRCALPHA)
                    pygame.draw.circle(_wsurf, (255, 100, 0, 70),
                                       (_warn_r+2, _warn_r+2), _warn_r, 4)
                    screen.blit(_wsurf, (int(_gnpc["x"]) - _warn_r - 2,
                                         GROUND_Y - _warn_r - 2))
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for portal in portals_obj:
            portal.draw(screen)
        for plat in platforms:
            plat.draw(screen, stage_idx)
        for sp in springs:
            sp.draw(screen)
        for hz in hazards:
            hz.draw(screen)
        for pu in powerups:
            pu.draw(screen)
        for b in balls:
            b.draw(screen)
        for ao in arcane_orbs:
            ao.draw(screen)
        for o in orbs:
            o.draw(screen)
        for co in charged_orbs:
            co.draw(screen)
        for bs in bubble_shots:
            bs.draw(screen)
        for po in poison_orbs:
            po.draw(screen)
        for bh in black_holes:
            bh.draw(screen)
        for gb in giant_bugs:
            gx, gy = int(gb['x']), GROUND_Y
            lt = gb['leg_t']
            pygame.draw.ellipse(screen, (0, 180, 40),  (gx - 30, gy - 28, 50, 24))
            pygame.draw.ellipse(screen, (0, 140, 30),  (gx - 12, gy - 32, 34, 28))
            _fx = 1 if gb['vx'] >= 0 else -1
            pygame.draw.circle(screen, (0, 200, 50),   (gx + _fx * 26, gy - 20), 13)
            pygame.draw.circle(screen, (255, 30, 30),  (gx + _fx * 31, gy - 25), 5)
            pygame.draw.circle(screen, (255, 30, 30),  (gx + _fx * 31, gy - 15), 5)
            for _i in range(3):
                _w = int(math.sin(lt + _i * 1.1) * 10)
                _ly = gy - 20 + _i * 7
                pygame.draw.line(screen, (0, 140, 30), (gx - 5, _ly), (gx - 34, _ly + _w + 14), 2)
                pygame.draw.line(screen, (0, 140, 30), (gx + 5, _ly), (gx + 34, _ly - _w + 14), 2)
            _lp = gb['life'] / (FPS * 8)
            pygame.draw.rect(screen, (40, 40, 40), (gx - 24, gy - 46, 48, 6))
            pygame.draw.rect(screen, (0, 220, 60),  (gx - 24, gy - 46, int(48 * _lp), 6))
        for bsp in bug_spawners:
            _bx, _by = int(bsp['x']), GROUND_Y - 10
            pygame.draw.rect(screen, (40, 160, 60),  (_bx - 14, _by - 18, 28, 28), border_radius=4)
            pygame.draw.rect(screen, (80, 220, 100), (_bx - 14, _by - 18, 28, 28), 2, border_radius=4)
            _lp = bsp['life'] / (FPS * 10)
            pygame.draw.rect(screen, (40, 40, 40), (_bx - 14, _by - 24, 28, 4))
            pygame.draw.rect(screen, (0, 220, 60),  (_bx - 14, _by - 24, int(28 * _lp), 4))
        for sb in spawned_bugs:
            sb['bug'].draw(screen)
        for bb in bounce_balls:
            bb.draw(screen)
        for sc in scrolls:
            sc.draw(screen)
        for t in totems:
            t.draw(screen)
        for r in remotes:
            r.draw(screen)
        for ap in apples:
            ap.draw(screen)
        for vb in venoms:
            vb.draw(screen)
        for nt in notes:
            nt.draw(screen)
        for h in hooks:
            h.draw(screen)
        for pk in pumpkins:
            pk.draw(screen)
        for js in jack_seeds:
            js.draw(screen)
        for fp in fruit_projs:
            fp.draw(screen)
        for cp in coal_projs:
            cp.draw(screen)
        for w in whips:
            w.draw(screen)
        for ks in kitsune_shots:
            ks.draw(screen)
        for wb in water_balls:
            wb.draw(screen)
        for b in bee_shots:
            b.draw(screen)
        for s in snipe_shots:
            s.draw(screen)
        for sb in sun_beams:
            sb.draw(screen)
        for dove in liberty_doves:
            dove.draw(screen)
        for lb in liberty_bombs:
            bx, by = int(lb['x']), int(lb['y'])
            pygame.draw.circle(screen, (255, 255, 255), (bx, by), 7)
            pygame.draw.circle(screen, (200, 220, 200), (bx, by), 4)
        for fb in fire_balls:
            fb.draw(screen)
        for nb in nian_breaths:
            nb.draw(screen)
        for tb in thunder_bolts:
            tb.draw(screen)
        for ps in plant_spikes:
            ps.draw(screen)
        for qw in quake_waves:
            t = 1.0 - qw['life'] / 90
            r = max(6, int(18 - t * 8))
            col = (180 + int(t * 60), int(130 - t * 70), 30)
            pygame.draw.ellipse(screen, col, (int(qw['x']) - r, GROUND_Y - r // 2, r * 2, r // 2 + 3))
        for gy in yellowstone_geysers:
            gx, age = int(gy['x']), gy['age']
            if age <= 22:
                h = min(age * 6, 130)
                pygame.draw.rect(screen, (160, 220, 255), (gx - 7, GROUND_Y - h, 14, h))
                pygame.draw.circle(screen, (220, 240, 255), (gx, GROUND_Y - h), 10)
            elif age <= 40:
                r = int((age - 22) * 5) + 8
                pygame.draw.circle(screen, (255, 255, 255), (gx, GROUND_Y - 110), r)
                pygame.draw.circle(screen, (180, 230, 255), (gx, GROUND_Y - 110), r + 4, 3)
            else:
                fade = max(0, 60 - age)
                a = int(fade * 4)
                if a > 0:
                    _gs = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(_gs, (200, 200, 200, a), (20, 20), 18)
                    screen.blit(_gs, (gx - 20, GROUND_Y - 130))
        for mn in mines:
            armed = mn['arm'] == 0
            blink = armed and (mn['life'] // 8) % 2 == 0
            pygame.draw.circle(screen, (200, 60, 20) if armed else (130, 110, 60),
                               (int(mn['x']), GROUND_Y - 7), 9)
            if blink:
                pygame.draw.circle(screen, (255, 220, 0), (int(mn['x']), GROUND_Y - 7), 5)
        # Draw active bombs (pulsing circle)
        for _bom in active_bombs:
            pulse = abs(math.sin(_bom['fuse'] * 0.13)) * 8
            _br = int(16 + pulse)
            pygame.draw.circle(screen, (200, 80, 20), (int(_bom['x']), int(_bom['y'])), _br)
            pygame.draw.circle(screen, (255, 220, 60), (int(_bom['x']), int(_bom['y'])), _br, 3)
            _fuse_pct = _bom['fuse'] / 120
            _fc = (int(255 * (1 - _fuse_pct)), int(255 * _fuse_pct), 0)
            _ft = font_tiny.render(f"BOMB {_bom['fuse']//FPS+1}s", True, _fc)
            screen.blit(_ft, (int(_bom['x']) - _ft.get_width()//2, int(_bom['y']) - _br - 16))
        # Draw bomb explosion rings
        for _bp in bomb_pops:
            _prog = 1.0 - _bp['t'] / 25
            _r = max(1, int(15 + _prog * 165))
            _a = max(0, int(220 * (1.0 - _prog)))
            _bsurf = pygame.Surface((_r*2+4, _r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(_bsurf, (255, 140, 20, _a), (_r+2, _r+2), _r, 5)
            screen.blit(_bsurf, (int(_bp['x']) - _r - 2, int(_bp['y']) - _r - 2))
        for sn in jungle_snakes:
            sn.draw(screen)
        for sk in falling_skulls:
            sk.draw(screen)
        for b in computer_bugs:
            b.draw(screen)
        # Draw casino coins
        for _cc2 in casino_coins:
            pygame.draw.circle(screen, (255, 210, 0), (int(_cc2["x"]), int(_cc2["y"])), 8)
            pygame.draw.circle(screen, (200, 160, 0), (int(_cc2["x"]), int(_cc2["y"])), 8, 2)
            _cdollar = font_tiny.render("$", True, (180, 130, 0))
            screen.blit(_cdollar, (int(_cc2["x"]) - _cdollar.get_width()//2, int(_cc2["y"]) - _cdollar.get_height()//2))
        if is_computer and stage_pencil:
            stage_pencil.draw(screen)
            stage_eraser.draw(screen)
        # Draw Laser Eyes beam
        for f in (p1, p2):
            if f.char.get("laser_eyes") and f.laser_active > 0:
                eye_x = int(f.x)
                eye_y = int(f.y - 100)
                end_x = WIDTH if f.facing == 1 else 0
                x = eye_x
                while (f.facing == 1 and x < end_x) or (f.facing == -1 and x > end_x):
                    dash_end = x + f.facing * 18
                    dash_end = min(dash_end, end_x) if f.facing == 1 else max(dash_end, end_x)
                    pygame.draw.line(screen, (255, 40, 0),  (x, eye_y),     (dash_end, eye_y), 3)
                    pygame.draw.line(screen, (255, 160, 80), (x, eye_y),    (dash_end, eye_y), 1)
                    x = dash_end + f.facing * 6  # 6-pixel gap between dashes
        # Draw Medusa freeze laser beam (cyan)
        for f in (p1, p2):
            if f.char.get("freeze_laser") and f.laser_active > 0:
                eye_x = int(f.x)
                eye_y = int(f.y - 100)
                end_x = WIDTH if f.facing == 1 else 0
                x = eye_x
                while (f.facing == 1 and x < end_x) or (f.facing == -1 and x > end_x):
                    dash_end = x + f.facing * 18
                    dash_end = min(dash_end, end_x) if f.facing == 1 else max(dash_end, end_x)
                    pygame.draw.line(screen, (0, 200, 255),  (x, eye_y), (dash_end, eye_y), 3)
                    pygame.draw.line(screen, (180, 240, 255), (x, eye_y), (dash_end, eye_y), 1)
                    x = dash_end + f.facing * 6
        # Draw magnet beams from powerups to any Magician fighter
        for f in (p1, p2):
            if f.char.get("magnet"):
                for pu in powerups:
                    if not pu.picked_up:
                        pygame.draw.line(screen, (140, 60, 220),
                                         (int(pu.x), int(pu.y)),
                                         (int(f.x), int(f.y - 60)), 1)
        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen)
        # Orb Shooter: draw charging orb on fighter
        for _f in (p1, p2):
            if _f.char.get("orb_shooter") and _f._kick_held and _f.orb_charge > 0:
                _cr = max(8, 8 + _f.orb_charge // 8)
                _cx = int(_f.x + _f.facing * (_cr + 20))
                _cy = int(_f.y - 60)
                pygame.draw.circle(screen, (60, 120, 255), (_cx, _cy), _cr)
                pygame.draw.circle(screen, (160, 210, 255), (_cx, _cy), max(3, _cr // 2))
        # Bubble shield visuals
        for f in (p1, p2):
            if f.bubble_shield:
                bsurf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(bsurf, (100, 200, 255, 70), (50, 50), 48)
                pygame.draw.circle(bsurf, (100, 200, 255, 160), (50, 50), 48, 3)
                screen.blit(bsurf, (int(f.x) - 50, int(f.y) - 90))
        clone_draws = [(cd, cd['fighter'].draw(screen)) for cd in clones]

        if not game_over:
            if p1.attacking and not p1.attack_hit:
                p1.check_hit(p1_hit, p2)
                if p1.attack_hit and p1.action == 'punch' and not p1.is_crit:
                    _p1_non_crit_flag[0] = True
            if p2.attacking and not p2.attack_hit:
                p2.check_hit(p2_hit, p1)
                if p2.attack_hit:
                    _p1_opp_hit_flag[0] = True
            # Fighter attacks hit jungle snakes
            for attacker, hit_pos in [(p1, p1_hit), (p2, p2_hit)]:
                if attacker.attacking and hit_pos:
                    for sn in jungle_snakes:
                        if math.hypot(hit_pos[0] - sn.x, hit_pos[1] - (sn.y - 8)) < 44:
                            dmg = (attacker.char["punch_dmg"] if attacker.action == 'punch'
                                   else attacker.char["kick_dmg"])
                            sn.take_damage(dmg)
            # Fighter attacks hit computer bugs
            if is_computer:
                for attacker, hit_pos in [(p1, p1_hit), (p2, p2_hit)]:
                    if attacker.attacking and hit_pos:
                        for b in computer_bugs:
                            if math.hypot(hit_pos[0]-b.x, hit_pos[1]-(b.y-8)) < 40:
                                dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                       else attacker.char["kick_dmg"])
                                b.take_damage(dmg)
            for cd, cf_hit in clone_draws:
                cf = cd['fighter']
                # clone attacks its target (ink clones can't attack)
                if not cd.get('ink') and cf.attacking and not cf.attack_hit:
                    cf.check_hit(cf_hit, cd['target'])
                # opponent can hit the clone
                if cd['target'] is p2:
                    if p2.attacking and not p2.attack_hit:
                        p2.check_hit(p2_hit, cf)
                else:
                    if p1.attacking and not p1.attack_hit:
                        p1.check_hit(p1_hit, cf)
            # draw clone timer above each clone (ink clones and permanent clones get no label)
            for cd in clones:
                if cd.get('ink') or cd.get('permanent'):
                    continue
                cf = cd['fighter']
                secs = cd['timer'] // FPS
                tag = font_tiny.render(f"2x [{secs}s]", True, (255, 80, 200))
                screen.blit(tag, (int(cf.x) - tag.get_width()//2,
                                  int(cf.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        # Draw AI tag above CPU fighter
        if vs_ai:
            diff_col = {
                'easy': GREEN, 'medium': YELLOW, 'hard': RED,
                'super_hard': PURPLE, 'super_super_hard': CYAN, 'mega_hard': ORANGE
            }[ai_difficulty]
            cpu_tag = font_tiny.render(f"CPU [{ai_difficulty.upper()}]", True, diff_col)
            screen.blit(cpu_tag, (int(p2.x) - cpu_tag.get_width()//2,
                                  int(p2.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        p2_label = f"CPU — {p2.char['name']}" if vs_ai else f"P2 — {p2.char['name']}"
        draw_health_bars_labeled(screen, p1, p2, p2_label)
        draw_active_powerups(screen, p1, 'left')
        draw_active_powerups(screen, p2, 'right')

        secs = max(0, timer // FPS)
        t_surf = font_medium.render(str(secs), True, RED if secs <= 10 else WHITE)
        screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 40))

        if vs_ai:
            hint  = font_tiny.render("WASD + F punch  G kick  S duck  R block", True, (140, 140, 140))
        else:
            hint  = font_tiny.render(
                "P1: WASD F punch G kick S duck R block        P2: Arrows K punch L kick ↓ duck O block",
                True, (140, 140, 140))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 22))

        # Stage advantage / disadvantage announcement (first 3 seconds)
        if announce_timer > 0 and not game_over:
            announce_timer -= 1
            if p1_stag:
                s = font_small.render(p1_stag, True, p1_stag_col)
                screen.blit(s, (10, 80))
            if p2_stag:
                s = font_small.render(p2_stag, True, p2_stag_col)
                screen.blit(s, (WIDTH - s.get_width() - 10, 80))

        if game_over:
            draw_win_screen(screen, winner, p1, p2, vs_ai=vs_ai)

        if not game_over:
            if _touch:  _touch.draw(screen)
            if _touch2: _touch2.draw(screen)

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Survival mode
# ---------------------------------------------------------------------------

def run_survival(p1_idx, p2_idx=None, two_player=False, stage_idx=0):
    _stage_name   = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13
    constants.STAGE_VOID    = (_stage_name in ("The Void", "Conveyor World"))
    constants.STAGE_CEILING = (_stage_name == "The Nether")

    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g, duck=pygame.K_s, block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l, duck=pygame.K_DOWN, block=pygame.K_o)

    p1      = Fighter(250, CHARACTERS[p1_idx],  1, P1_CTRL)
    p2      = Fighter(650, CHARACTERS[p2_idx], -1, P2_CTRL) if two_player else None
    if constants.STAGE_VOID:
        p1.x = 400.0; p1.y = float(GROUND_Y - 70); p1.on_ground = True
        if p2:
            p2.x = 500.0; p2.y = float(GROUND_Y - 70); p2.on_ground = True
    players = [p1, p2] if two_player else [p1]

    stage_data  = STAGES[stage_idx % len(STAGES)]
    platforms   = [Platform(*p) for p in stage_data["platforms"]] + [ConveyorBelt(*c) for c in stage_data.get("conveyors", [])] + [SlantedConveyorBelt(*c) for c in stage_data.get("slanted_conveyors", [])]
    springs     = [Spring(*s)   for s in stage_data["springs"]]
    is_jungle     = stage_data["name"] == "Jungle"
    is_computer   = stage_data["name"] == "Computer"
    is_underworld = stage_data["name"] == "Underworld"
    stage_pencil = None
    stage_eraser = None
    if is_computer:
        platforms.append(MousePlatform(80, GROUND_Y - 62, travel=720))
        stage_pencil = StagePencil()
        stage_eraser = StageEraser()

    _portal_cols_s = [(80, 100, 220), (220, 120, 20)]
    _px1s = random.randint(80, WIDTH // 2 - 60)
    _px2s = random.randint(WIDTH // 2 + 60, WIDTH - 80)
    _py1s = random.randint(GROUND_Y - 280, GROUND_Y - 80)
    _py2s = random.randint(GROUND_Y - 280, GROUND_Y - 80)
    portals_obj_s  = [Portal(_px1s, _py1s, _portal_cols_s[0]), Portal(_px2s, _py2s, _portal_cols_s[1])]
    portals_obj_s[0].partner = portals_obj_s[1]
    portals_obj_s[1].partner = portals_obj_s[0]

    # Cloned: spawn permanent AI clones alongside players at survival start
    for _sp in list(players):
        if _sp.char.get("cloned"):
            _scx = _sp.x + 80 if _sp.facing == 1 else _sp.x - 80
            _scf = AIFighter(_scx, dict(_sp.char), _sp.facing, 'medium')
            _scf.hp = 999999; _scf.max_hp = 999999
            ink_clones.append({'fighter': _scf, 'timer': 999999, 'target': None, 'permanent': True})

    enemies           = []
    death_pops        = []   # [{x,y,color,t}] death burst particles
    kamikaze_pops     = []   # [{x,y,t}] kamikaze explosion ring
    balls             = []   # Projectile (shoot_kick)
    orbs              = []   # Orb (bazooka_kick)
    bounce_balls      = []   # BouncingBall (bounce_kick)
    hooks             = []   # SnakeHook (grapple_kick)
    pumpkins          = []   # Pumpkin (pumpkin_kick)
    whips             = []   # Whip (whip_punch)
    arcane_orbs       = []   # ArcaneOrb (Arcanist)
    sun_beams         = []   # SunBeam (Solara)
    nian_breaths      = []   # NianBreath cone (Nian)
    liberty_doves       = []   # LibertyDove (Stickman of Liberty)
    liberty_bombs       = []   # bombs dropped by dove
    yellowstone_geysers = []   # Yellowstone kick geysers
    jack_seeds          = []   # PumpkinSeed (Jack O' Slash)
    fruit_projs         = []   # FruitProj (Cornucopia)
    coal_projs          = []   # CoalProj (Saint Nix)
    thunder_bolts       = []   # ThunderBolt (Thunder God / Storm Caller)
    survival_widow_bugs = []  # Black Widow wall bugs
    ink_clones        = []   # Ink Brush clones
    survival_bombs    = []   # Bomb character active bombs
    survival_bomb_pops = []  # explosion rings
    survival_scrolls   = []  # Scroll projectiles (Scrollmaster)
    survival_totems    = []  # TotemPole projectiles (Great Totem Spirit)
    survival_remotes   = []  # RemoteController projectiles (Rage Quitter)
    survival_apples    = []  # Apple projectiles (Gravity)
    survival_plants    = []  # PlantSpike projectiles (Druid)
    en_balls          = []
    en_orbs           = []
    en_bounce_balls   = []
    en_pumpkins       = []
    en_hooks          = []
    en_whips          = []
    powerups          = []
    jungle_snakes     = []
    computer_bugs     = []
    bug_spawn_timer   = 150
    falling_skulls    = []
    skull_spawn_timer = 200
    survival_timer    = 0
    enemies_killed    = 0
    enemy_spawn_timer = 180
    snake_spawn_timer = 180
    powerup_timer     = 480
    game_over         = False

    def wave_info():
        s = survival_timer // FPS
        if   s <  30: return 1, 'easy'
        elif s <  60: return 2, 'easy'
        elif s <  90: return 2, 'medium'
        elif s < 120: return 3, 'medium'
        elif s < 180: return 3, 'hard'
        elif s < 240: return 4, 'hard'
        else:         return 4, 'super_hard'

    def _draw_survival_hud():
        # HP bars for players
        bw = 240
        pygame.draw.rect(screen, (60,60,60), (10, 10, bw, 20), border_radius=4)
        fw = int(bw * max(0, p1.hp / p1.max_hp))
        pygame.draw.rect(screen, p1.char["color"], (10, 10, fw, 20), border_radius=4)
        pygame.draw.rect(screen, WHITE, (10, 10, bw, 20), 2, border_radius=4)
        ht = font_tiny.render(f"P1 {p1.char['name']}  {max(0,p1.hp)}/{p1.max_hp}", True, WHITE)
        screen.blit(ht, (14, 13))
        if two_player:
            pygame.draw.rect(screen, (60,60,60), (WIDTH-bw-10, 10, bw, 20), border_radius=4)
            fw2 = int(bw * max(0, p2.hp / p2.max_hp))
            pygame.draw.rect(screen, p2.char["color"], (WIDTH-bw-10+bw-fw2, 10, fw2, 20), border_radius=4)
            pygame.draw.rect(screen, WHITE, (WIDTH-bw-10, 10, bw, 20), 2, border_radius=4)
            ht2 = font_tiny.render(f"{max(0,p2.hp)}/{p2.max_hp}  P2 {p2.char['name']}", True, WHITE)
            screen.blit(ht2, (WIDTH-bw-10 + bw - ht2.get_width() - 4, 13))
        # Timer (counting up)
        elapsed = survival_timer // FPS
        mins, secs = divmod(elapsed, 60)
        t_surf = font_medium.render(f"{mins}:{secs:02d}", True, YELLOW)
        screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 6))
        # Kills
        k_surf = font_tiny.render(f"Kills: {enemies_killed}", True, (200, 200, 200))
        screen.blit(k_surf, (WIDTH//2 - k_surf.get_width()//2, 38))
        # Wave
        max_en, diff = wave_info()
        w_surf = font_tiny.render(f"Wave difficulty: {diff.replace('_',' ')}  |  Max enemies: {max_en}", True, GRAY)
        screen.blit(w_surf, (WIDTH//2 - w_surf.get_width()//2, HEIGHT - 22))

    def _draw_game_over():
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))
        go = font_large.render("GAME OVER", True, RED)
        screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//3 - 40))
        elapsed = survival_timer // FPS
        mins, secs = divmod(elapsed, 60)
        ts = font_medium.render(f"Survived: {mins}:{secs:02d}", True, WHITE)
        screen.blit(ts, (WIDTH//2 - ts.get_width()//2, HEIGHT//3 + 40))
        ks = font_medium.render(f"Kills: {enemies_killed}", True, YELLOW)
        screen.blit(ks, (WIDTH//2 - ks.get_width()//2, HEIGHT//3 + 90))
        hint = font_small.render("R — restart     C — menu     ESC — quit", True, (200,200,200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT*2//3 + 30))

    _survival_screentime = any(p.char.get("screentime") for p in players)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False; return ('rematch', enemies_killed)
                    if event.key == pygame.K_c:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False; return ('select',  enemies_killed)
                    if event.key == pygame.K_ESCAPE:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False; return ('select', enemies_killed)
                else:
                    if event.key == pygame.K_ESCAPE:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; constants.STAGE_CEILING = False; return ('select', enemies_killed)

        if not game_over:
            # Screentime 2x speed: advance an extra tick
            if _survival_screentime:
                survival_timer += 1
                enemy_spawn_timer = max(0, enemy_spawn_timer - 1)
            survival_timer += 1
            max_en, diff = wave_info()

            # Platforms & springs
            for plat in platforms:
                plat.update()
            for sp in springs:
                sp.update()
                sp.trigger(p1)
                if two_player: sp.trigger(p2)
                for en in enemies: sp.trigger(en)

            # Portals
            for portal in portals_obj_s:
                portal.update()
            for fighter in players:
                for portal in portals_obj_s:
                    if portal.partner and fighter.portal_cooldown == 0 and portal.near(fighter):
                        fighter.x = portal.partner.x
                        fighter.y = portal.partner.y
                        fighter.vy = 0
                        fighter.portal_cooldown = FPS * 2
                        break

            # Spawn enemies
            enemy_spawn_timer -= 1
            if enemy_spawn_timer <= 0 and len(enemies) < max_en:
                _ai_pool = [i for i, c in enumerate(CHARACTERS) if not c.get("shop_only")]
                ci = random.choice(_ai_pool)
                if constants.STAGE_VOID:
                    # Spawn on the central platform so they don't fall into the void
                    sx = float(random.randint(330, 570))
                    sy = float(GROUND_Y - 70)
                else:
                    sx = float(random.choice([60, WIDTH - 60]))
                    sy = float(GROUND_Y)
                en    = AIFighter(sx, CHARACTERS[ci], -1 if sx > WIDTH // 2 else 1, diff)
                en.x  = sx; en.y = sy; en.on_ground = True
                en.hp = en.char["max_hp"]
                enemies.append(en)
                interval          = max(60, 300 - survival_timer // (2 * FPS))
                enemy_spawn_timer = random.randint(max(30, interval // 2), interval)

            # Update enemies — each targets nearest living player
            living = [p for p in players if p.hp > 0]
            for en in enemies:
                if living:
                    target = min(living, key=lambda p: abs(p.x - en.x))
                    en.update(None, target, platforms)
                    if en.pending_ball:
                        en.pending_ball = False
                        en_balls.append(Projectile(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_orb and en.bazooka_cooldown == 0:
                        en.pending_orb = False
                        en_orbs.append(Orb(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_bounce:
                        en.pending_bounce = False
                        en_bounce_balls.append(BouncingBall(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_hook and living:
                        en.pending_hook = False
                        tgt = min(living, key=lambda p: abs(p.x - en.x))
                        en_hooks.append(SnakeHook(en.x + en.facing*20, en.y-60,
                                                   tgt.x, tgt.y-60, en))

            # Mark newly dead players and freeze them
            for p in players:
                if p.hp <= 0 and p.action != 'dead':
                    p.action     = 'dead'
                    p.action_t   = 0
                    p.flash_timer = 0
                    p.vx = 0
                    p.vy = 0

            # Update players (skip dead ones)
            keys     = pygame.key.get_pressed()
            other_p1 = p2 if two_player else (enemies[0] if enemies else p1)
            if p1.hp > 0:
                p1.update(keys, other_p1, platforms)
            if two_player and p2.hp > 0:
                p2.update(keys, p1, platforms)

            # Storm Caller + Quaker (survival)
            for p in players:
                if p.pending_storm:
                    p.pending_storm = False
                    sx = random.randint(80, WIDTH - 80)
                    for en in enemies:
                        if abs(en.x - sx) < 80:
                            en.hp = max(0, en.hp - ThunderBolt.DMG)
                            en.flash_timer = 12
                            if not en.char.get("immune"):
                                en.shock_frames = max(en.shock_frames, 180)
                if p.quake_pending:
                    p.quake_pending = False
                    for en in enemies:
                        if abs(p.x - en.x) < 140:
                            en.hp = max(0, en.hp - 15)
                            en.flash_timer = 10
                            en.knockback = (1 if en.x > p.x else -1) * 8

            # Spawn player projectiles
            for shooter in players:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing*30, shooter.y-60,
                                            shooter.facing, shooter))
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing*30, shooter.y-60,
                                    shooter.facing, shooter))
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing*30, shooter.y-60,
                                                     shooter.facing, shooter))
                if shooter.pending_hook and enemies:
                    shooter.pending_hook = False
                    tgt = min(enemies, key=lambda e: abs(e.x - shooter.x))
                    hooks.append(SnakeHook(shooter.x + shooter.facing*20, shooter.y-60,
                                           tgt.x, tgt.y-60, shooter))
                else:
                    shooter.pending_hook = False

            # Laser Eyes beam damage (survival)
            for shooter in players:
                if (shooter.char.get("laser_eyes") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    for en in enemies:
                        correct_side = ((shooter.facing == 1  and en.x > shooter.x) or
                                        (shooter.facing == -1 and en.x < shooter.x))
                        if correct_side and abs((en.y - 60) - laser_y) < 35:
                            en.hp = max(0, en.hp - 2)
                            en.flash_timer = 4
                            shooter.laser_hit_cd = 15
                            break
            for en in enemies:
                if (en.char.get("laser_eyes") and en.laser_active > 0
                        and en.laser_hit_cd == 0):
                    laser_y = en.y - 100
                    for p in living:
                        correct_side = ((en.facing == 1  and p.x > en.x) or
                                        (en.facing == -1 and p.x < en.x))
                        if correct_side and abs((p.y - 60) - laser_y) < 35:
                            p.take_proj_dmg(2, flash=False)
                            p.flash_timer = 4
                            en.laser_hit_cd = 15
                            break

            # Flame trail damage — survival (player trails hit enemies only, enemy trails hit players)
            def _flame_trail_hit_surv(trail_owner, victims):
                if (trail_owner.char.get("flame_trail") and trail_owner.trail_dmg_cd == 0
                        and trail_owner.flame_trail):
                    for victim in victims:
                        if victim.hp <= 0:
                            continue
                        for tx, ty, _ in trail_owner.flame_trail:
                            if abs(victim.x - tx) < 28 and abs(victim.y - ty) < 40:
                                if not victim.char.get("immune"):
                                    victim.hp = max(0, victim.hp - 3)
                                    victim.flash_timer = max(victim.flash_timer, 6)
                                if victim.fire_frames == 0: victim.fire_tick = 480
                                victim.fire_frames = max(victim.fire_frames, 120)
                                trail_owner.trail_dmg_cd = 30
                                break
            for blazer in players:
                _flame_trail_hit_surv(blazer, enemies)
            for blazer in enemies:
                _flame_trail_hit_surv(blazer, living)

            # Flower trail poison — survival
            def _flower_trail_hit_surv(owner, victims):
                if owner.char.get("flower_trail_poison") and owner.flower_dmg_cd == 0:
                    for victim in victims:
                        if victim.hp <= 0:
                            continue
                        for fx, fy, _ in owner.flower_trail:
                            if abs(victim.x - fx) < 30 and abs(victim.y - fy) < 40:
                                if victim.poison_frames == 0: victim.poison_tick = 180
                                victim.poison_frames = max(victim.poison_frames, 240)
                                owner.flower_dmg_cd = 60
                                break
            for _sfl in players:
                _flower_trail_hit_surv(_sfl, enemies)
            for _sfl in enemies:
                _flower_trail_hit_surv(_sfl, living)

            # Boomerang damage: player boomerangs hit enemies, enemy boomerangs hit players
            for thrower in players:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    for en in enemies:
                        if math.hypot(bx - en.x, by - (en.y - 60)) < 48:
                            en.hp = max(0, en.hp - 8)
                            en.flash_timer = 6
                            thrower.boomerang_hit_cd = 30
                            break
                if thrower.bbboomerang_timer > 0 and thrower.bbboomerang_hit_cd == 0:
                    _bbe = (300 - thrower.bbboomerang_timer) // 60
                    _bbrx = 70 + _bbe * 10;  _bbry = 45 + _bbe * 7
                    _bbhr = 28 + _bbe * 4
                    for en in enemies:
                        for _bbi in range(5):
                            _bba = thrower.bbboomerang_angle + math.radians(_bbi * 72)
                            _bbx = thrower.x + math.cos(_bba) * _bbrx
                            _bby = (thrower.y - 60) + math.sin(_bba) * _bbry
                            if math.hypot(_bbx - en.x, _bby - (en.y - 60)) < _bbhr:
                                en.hp = max(0, en.hp - 6)
                                en.flash_timer = 6
                                thrower.bbboomerang_hit_cd = 30
                                break
            for en in enemies:
                if en.boomerang_timer > 0 and en.boomerang_hit_cd == 0:
                    bx = en.x + math.cos(en.boomerang_angle) * 85
                    by = (en.y - 60) + math.sin(en.boomerang_angle) * 55
                    for p in living:
                        if math.hypot(bx - p.x, by - (p.y - 60)) < 48:
                            p.take_proj_dmg(8, flash=False)
                            p.flash_timer = 6
                            en.boomerang_hit_cd = 30
                            break

            # Player balls → enemies
            for b in balls:
                b.update()
                if b.alive:
                    for en in enemies:
                        if b.collides(en):
                            en.hp = max(0, en.hp - 10); en.flash_timer = 8
                            b.alive = False; break
            balls = [b for b in balls if b.alive]

            # Black Widow: wall bugs (survival — player → enemies)
            for p in players:
                if p.pending_widow_bugs:
                    p.pending_widow_bugs = False
                    for _wx in (40.0, float(WIDTH - 40)):
                        nb = ComputerBug(); nb.x = _wx
                        survival_widow_bugs.append({'bug': nb, 'enemies': enemies})
            _prev_swb = len(survival_widow_bugs)
            for swb in survival_widow_bugs:
                swb['bug'].leg_t += 0.2
                closest = min(swb['enemies'], key=lambda e: abs(e.x - swb['bug'].x), default=None)
                if closest:
                    swb['bug'].vx = ComputerBug.SPEED if closest.x > swb['bug'].x else -ComputerBug.SPEED
                    swb['bug'].x += swb['bug'].vx
                    swb['bug'].x = max(30.0, min(float(WIDTH - 30), swb['bug'].x))
                    if swb['bug'].bite_timer > 0:
                        swb['bug'].bite_timer -= 1
                    elif abs(closest.x - swb['bug'].x) < ComputerBug.BITE_RANGE and abs(closest.y - swb['bug'].y) < 60:
                        closest.take_proj_dmg(ComputerBug.BITE_DMG)
                        swb['bug'].bite_timer = ComputerBug.BITE_COOLDOWN
            survival_widow_bugs = [swb for swb in survival_widow_bugs if swb['bug'].alive]

            # Arcanist: arcane orbs (survival — player → enemies)
            for p in players:
                if p.pending_arcane_orb:
                    p.pending_arcane_orb = False
                    arcane_orbs.append(ArcaneOrb(p.x + p.facing * 30, p.y - 60, p.facing, p))
            for ao in arcane_orbs:
                ao.update()
                if ao.alive:
                    for en in enemies:
                        if ao.collides(en):
                            en.hp = max(0, en.hp - ArcaneOrb.DMG)
                            en.flash_timer = 8
                            ao.alive = False; break
            arcane_orbs = [ao for ao in arcane_orbs if ao.alive]

            # Stickman of Liberty dove (survival)
            for p in players:
                if p.pending_liberty_dove:
                    p.pending_liberty_dove = False
                    liberty_doves.append(LibertyDove(p.x, p.y, p))
            for dove in liberty_doves:
                dove.update()
                if dove.pending_bomb:
                    dove.pending_bomb = False
                    liberty_bombs.append({'x': dove.x, 'y': dove.y, 'vy': 0.0, 'alive': True, 'owner': dove.owner})
            liberty_doves = [d for d in liberty_doves if d.alive]
            for lb in liberty_bombs:
                lb['vy'] = min(lb['vy'] + 0.9, 22)
                lb['y'] += lb['vy']
                if lb['y'] >= GROUND_Y - 4:
                    for en in enemies:
                        if abs(en.x - lb['x']) < 65:
                            en.take_proj_dmg(15)
                            en.flash_timer = max(en.flash_timer, 14)
                    lb['alive'] = False
            liberty_bombs = [lb for lb in liberty_bombs if lb['alive']]
            # Yellowstone geysers (survival)
            for p in players:
                if p.pending_yellowstone_geysers:
                    p.pending_yellowstone_geysers = False
                    for i in range(10):
                        gx = 60 + (WIDTH - 120) * i / 9 + random.uniform(-25, 25)
                        gx = max(60.0, min(float(WIDTH - 60), gx))
                        yellowstone_geysers.append({'x': gx, 'age': 0, 'alive': True,
                                                    'owner': p, 'hit': set()})
            new_gy = []
            for gy in yellowstone_geysers:
                gy['age'] += 1
                if gy['age'] <= 60:
                    new_gy.append(gy)
                    if 22 <= gy['age'] <= 40:
                        for en in enemies:
                            if id(en) not in gy['hit'] and abs(en.x - gy['x']) < 52:
                                en.take_proj_dmg(12)
                                en.flash_timer = max(en.flash_timer, 10)
                                gy['hit'].add(id(en))
            yellowstone_geysers = new_gy
            # Bookzworm aura (survival — player hits enemies)
            for p in players:
                if p.char.get("bookzworm_books") and p.hp > 0 and p.bookzworm_book_cd <= 0:
                    _bz_r = int(18 * 4.5 * p.draw_scale) + 30   # match visual orbit + hitbox
                    for en in enemies:
                        if math.hypot(en.x - p.x, (en.y - p.y)) < _bz_r:
                            en.take_proj_dmg(6)
                            en.flash_timer = max(en.flash_timer, 10)
                            p.bookzworm_book_cd = 50
                            break
            # Solara sun beams (survival — player → enemies)
            for p in players:
                if p.pending_sun_beam:
                    p.pending_sun_beam = False
                    sun_beams.append(SunBeam(p.x + p.facing * 30, p.y - 60, p.facing, p))
            for sb in sun_beams:
                sb.update()
                if sb.alive:
                    for en in enemies:
                        if sb.collides(en):
                            en.take_proj_dmg(SunBeam.DMG)
                            en.shock_frames = max(en.shock_frames, 120)
                            if en.fire_frames == 0: en.fire_tick = 480
                            en.fire_frames = max(en.fire_frames, 300)
                            sb.alive = False; break
            sun_beams = [sb for sb in sun_beams if sb.alive]

            # Nian breath cone (survival — player breath hits enemies only)
            for p in players:
                if p.pending_nian_breath:
                    p.pending_nian_breath = False
                    nian_breaths.append(NianBreath(p.x + p.facing * 18, p.y - 60, p.facing, p))
            for nb in nian_breaths:
                nb.update()
                targets = enemies if nb.owner in players else living
                for victim in targets:
                    if victim.hp > 0 and id(victim) not in nb._hit and nb.in_cone(victim):
                        nb._hit.add(id(victim))
                        victim.take_proj_dmg(NianBreath.DMG)
                        if not victim.char.get("immune"):
                            victim.fire_frames = max(victim.fire_frames, NianBreath.FIRE_FRAMES)
                        victim.flash_timer = max(victim.flash_timer, 12)
            nian_breaths = [nb for nb in nian_breaths if nb.alive]

            # Player orbs → enemies
            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    for en in enemies:
                        if math.hypot(o.x - en.x, o.y - (en.y - 60)) < o.EXPLODE_RADIUS:
                            en.hp = max(0, en.hp - o.EXPLODE_DMG); en.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            # Player bouncing balls → enemies
            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    for en in enemies:
                        if bb.collides(en):
                            en.hp = max(0, en.hp - 10); en.flash_timer = 8
                            bb.hit_cd = BouncingBall.HIT_CD; break
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            # Player scrolls → enemies (Scrollmaster survival)
            for p in players:
                if p.pending_scroll:
                    p.pending_scroll = False
                    survival_scrolls.append(Scroll(p.x + p.facing * 30,
                                                   p.y - 60, p.facing, p))
            for sc in survival_scrolls:
                sc.update()
                if sc.alive and sc.hit_cd == 0:
                    for en in enemies:
                        if sc.collides(en):
                            en.hp = max(0, en.hp - Scroll.DMG)
                            en.flash_timer = 8
                            sc.hit_cd = Scroll.HIT_CD
                            break
            survival_scrolls = [sc for sc in survival_scrolls if sc.alive]

            # Player totems → enemies (Great Totem Spirit survival)
            for p in players:
                if p.pending_totem:
                    p.pending_totem = False
                    tgt = min(enemies, key=lambda e: abs(e.x - p.x)) if enemies else p
                    for dx in (-160, -80, 0, 80, 160):
                        survival_totems.append(TotemPole(tgt.x + dx))
            for t in survival_totems:
                t.update()
                if t.hit_cd == 0:
                    for en in enemies:
                        if t.collides(en):
                            en.hp = max(0, en.hp - TotemPole.DMG)
                            en.flash_timer = 8
                            t.hit_cd = TotemPole.HIT_CD
                            break
            survival_totems = [t for t in survival_totems if t.alive]

            # Player remotes → enemies (Rage Quitter survival)
            for p in players:
                if p.pending_remote:
                    p.pending_remote = False
                    survival_remotes.append(RemoteController(p.x + p.facing * 30,
                                                             p.y - 60, p.facing))
            for r in survival_remotes:
                r.update()
                if not r.hit:
                    for en in enemies:
                        if r.collides(en):
                            en.hp = max(0, en.hp - RemoteController.DMG)
                            en.flash_timer = 20
                            r.hit = True; r.alive = False; break
            survival_remotes = [r for r in survival_remotes if r.alive]

            # Player apples → enemies (Gravity survival)
            for p in players:
                if p.pending_apple:
                    p.pending_apple = False
                    tgt = min(enemies, key=lambda e: abs(e.x - p.x)) if enemies else p
                    for i in range(20):
                        survival_apples.append(Apple(tgt.x + random.randint(-200, 200)))
            for ap in survival_apples:
                ap.update()
                if ap.hit_cd == 0:
                    for en in enemies:
                        if ap.collides(en):
                            en.hp = max(0, en.hp - Apple.DMG)
                            en.flash_timer = 6
                            ap.hit_cd = Apple.HIT_CD; break
            survival_apples = [ap for ap in survival_apples if ap.alive]

            # Player plant spikes → enemies (Druid survival)
            for p in players:
                if p.pending_plant:
                    p.pending_plant = False
                    tgt = min(enemies, key=lambda e: abs(e.x - p.x)) if enemies else None
                    if tgt:
                        survival_plants.append(PlantSpike(tgt.x, p))
            for ps in survival_plants:
                ps.update()
                if ps.alive:
                    for en in enemies:
                        if ps.collides(en):
                            en.hp = max(0, en.hp - PlantSpike.DMG)
                            en.flash_timer = 10
                            ps.alive = False; break
            survival_plants = [ps for ps in survival_plants if ps.alive]

            # Player hooks → enemies
            for h in hooks:
                h.update()
                if h.alive:
                    for en in enemies:
                        if h.collides(en):
                            pull = 1 if h.owner.x > en.x else -1
                            en.knockback = pull * 22
                            en.hp = max(0, en.hp - 6); en.flash_timer = 8
                            h.alive = False; break
            hooks = [h for h in hooks if h.alive]

            # Enemy hooks → players
            for h in en_hooks:
                h.update()
                if h.alive:
                    for p in living:
                        if h.collides(p):
                            pull = 1 if h.owner.x > p.x else -1
                            p.knockback = pull * 22
                            p.take_proj_dmg(6, flash=False); p.flash_timer = 8
                            h.alive = False; break
            en_hooks = [h for h in en_hooks if h.alive]

            # Enemy balls → players
            for b in en_balls:
                b.update()
                if b.alive:
                    for p in living:
                        if b.collides(p):
                            p.take_proj_dmg(10, flash=False); p.flash_timer = 8
                            b.alive = False; break
            en_balls = [b for b in en_balls if b.alive]

            # Enemy orbs → players
            for o in en_orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    for p in living:
                        if math.hypot(o.x - p.x, o.y - (p.y - 60)) < o.EXPLODE_RADIUS:
                            p.take_proj_dmg(o.EXPLODE_DMG, flash=False); p.flash_timer = 14
            en_orbs = [o for o in en_orbs if o.alive]

            # Enemy bouncing balls → players
            for bb in en_bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    for p in living:
                        if bb.collides(p):
                            p.take_proj_dmg(10, flash=False); p.flash_timer = 8
                            bb.hit_cd = BouncingBall.HIT_CD; break
            en_bounce_balls = [bb for bb in en_bounce_balls if bb.alive]

            # Jack O' Slash seeds (survival)
            for p in players:
                if p.pending_jack_pumpkin:
                    p.pending_jack_pumpkin = False
                    pumpkins.append(Pumpkin(p.x + p.facing * 24, p.y - 80, p.facing, p))
                if p.pending_jack_seed:
                    p.pending_jack_seed = False
                    jack_seeds.append(PumpkinSeed(p.x + p.facing * 24, p.y - 60, p.facing, p))
            for js in jack_seeds:
                js.update()
                if js.alive:
                    for en in enemies:
                        if js.collides(en):
                            en.take_proj_dmg(PumpkinSeed.DMG)
                            en.flash_timer = max(en.flash_timer, 8)
                            js.alive = False; break
            jack_seeds = [js for js in jack_seeds if js.alive]
            # Player fruit projectiles + coal + thunder (survival)
            for shooter in players:
                if shooter.pending_fruit_attack:
                    fa = shooter.pending_fruit_attack
                    shooter.pending_fruit_attack = None
                    _fx = shooter.x + shooter.facing * 30
                    _fy = shooter.y - 60
                    if fa[0] == 'cranberry_burst':
                        for _ci in range(4):
                            fruit_projs.append(FruitProj(_fx, _fy + _ci * 5,
                                               shooter.facing, shooter, 'cranberry'))
                    elif fa[0] == 'grape_rain':
                        for _gi in range(7):
                            gx = random.randint(50, WIDTH - 50)
                            fruit_projs.append(FruitProj(gx, -20, shooter.facing,
                                               shooter, 'grape', vy=4.0 + random.random() * 2))
                    elif fa[0] == 'coal':
                        coal_projs.append(CoalProj(_fx, _fy, shooter.facing, shooter, fa[1]))
                    else:
                        fruit_projs.append(FruitProj(_fx, _fy, shooter.facing, shooter, fa[0]))
                if shooter.pending_thunder:
                    shooter.pending_thunder = False
                    tgt_x = min(enemies, key=lambda e: abs(e.x - shooter.x)).x if enemies else random.randint(80, WIDTH-80)
                    thunder_bolts.append(ThunderBolt(tgt_x, shooter))
            for fp in fruit_projs:
                fp.update()
                if fp.alive:
                    for en in enemies:
                        if fp.collides(en):
                            _apply_fruit_hit(en, fp)
                            fp.alive = False; break
            fruit_projs = [fp for fp in fruit_projs if fp.alive]
            for cp in coal_projs:
                cp.update()
                if cp.alive:
                    for en in enemies:
                        if cp.collides(en):
                            _apply_coal_hit(en, cp)
                            cp.alive = False; break
            coal_projs = [cp for cp in coal_projs if cp.alive]
            for tb in thunder_bolts:
                tb.update()
                if tb.alive:
                    for en in enemies:
                        if tb.collides(en):
                            en.hp = max(0, en.hp - ThunderBolt.DMG)
                            en.flash_timer = 12
                            if not en.char.get("immune"):
                                en.shock_frames = max(en.shock_frames, 180)
                            tb.alive = False; break
            thunder_bolts = [tb for tb in thunder_bolts if tb.alive]
            # Player pumpkins → enemies
            for shooter in players:
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(
                        shooter.x + shooter.facing * 24, shooter.y - 80,
                        shooter.facing, shooter))
            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    for en in enemies:
                        if math.hypot(pk.x - en.x, pk.y - (en.y - 60)) < pk.EXPLODE_RADIUS:
                            en.hp = max(0, en.hp - pk.EXPLODE_DMG); en.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    for en in enemies:
                        if pk.collides(en):
                            pk._explode(); break
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Enemy pumpkins → players
            for en in enemies:
                if en.pending_pumpkin:
                    en.pending_pumpkin = False
                    en_pumpkins.append(Pumpkin(
                        en.x + en.facing * 24, en.y - 80, en.facing, en))
            for pk in en_pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    for p in living:
                        if math.hypot(pk.x - p.x, pk.y - (p.y - 60)) < pk.EXPLODE_RADIUS:
                            p.take_proj_dmg(pk.EXPLODE_DMG, flash=False); p.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    for p in living:
                        if pk.collides(p):
                            pk._explode(); break
            en_pumpkins = [pk for pk in en_pumpkins if pk.alive]

            # Player whips → enemies
            for shooter in players:
                if shooter.pending_whip:
                    shooter.pending_whip = False
                    whips.append(Whip(
                        shooter.x + shooter.facing * 28, shooter.y - 60,
                        shooter.facing, shooter))
            for w in whips:
                w.update()
                if w.can_hit():
                    for en in enemies:
                        if w.collides(en):
                            en.hp = max(0, en.hp - w.DMG)
                            en.flash_timer = 10
                            en.knockback = w.facing * 14
                            w.hit_done = True
                            break
            whips = [w for w in whips if w.alive]

            # Enemy whips → players
            for en in enemies:
                if en.pending_whip:
                    en.pending_whip = False
                    en_whips.append(Whip(
                        en.x + en.facing * 28, en.y - 60,
                        en.facing, en))
            for w in en_whips:
                w.update()
                if w.can_hit():
                    for p in living:
                        if w.collides(p):
                            p.take_proj_dmg(w.DMG, flash=False)
                            p.flash_timer = 10
                            p.knockback = w.facing * 14
                            w.hit_done = True
                            break
            en_whips = [w for w in en_whips if w.alive]

            # Ink Brush clones (survival)
            for shooter in players:
                if shooter.pending_ink_clone:
                    shooter.pending_ink_clone = False
                    tgt = min(enemies, key=lambda e: abs(e.x - shooter.x)) if enemies else None
                    if tgt:
                        cf = AIFighter(shooter.x + shooter.facing * 55, shooter.char, -shooter.facing, 'medium')
                        cf.hp = max(1, shooter.hp)
                        cf.color = shooter.color
                        cf.no_attack = True
                        ink_clones.append({'fighter': cf, 'timer': FPS * 100, 'target': tgt})
            for en in enemies:
                if en.pending_ink_clone and living:
                    en.pending_ink_clone = False
                    tgt2 = min(living, key=lambda p: abs(p.x - en.x))
                    cf2 = AIFighter(en.x + en.facing * 55, en.char, -en.facing, 'medium')
                    cf2.hp = max(1, en.hp)
                    cf2.color = en.color
                    cf2.no_attack = True
                    ink_clones.append({'fighter': cf2, 'timer': FPS * 8, 'target': tgt2})
            new_ink = []
            for ic in ink_clones:
                if not ic.get('permanent'):
                    ic['timer'] -= 1
                # Permanent clones (Cloned char) target nearest enemy
                _ic_tgt = ic['target']
                if ic.get('permanent') and enemies:
                    _ic_tgt = min(enemies, key=lambda e: abs(e.x - ic['fighter'].x))
                if ic['timer'] > 0 and ic['fighter'].hp > 0:
                    ic['fighter'].update(None, _ic_tgt, platforms)
                    new_ink.append(ic)
            ink_clones = new_ink

            # Chainsaw Man: rapid proximity damage (survival)
            for attacker in [p for p in players if p.char.get("chainsaw") and p.hp > 0]:
                if attacker.chainsaw_cd > 0:
                    attacker.chainsaw_cd -= 1
                else:
                    for en in enemies:
                        if abs(attacker.x - en.x) < 50:
                            en.hp = max(0, en.hp - 4)
                            en.flash_timer = 4
                            attacker.chainsaw_cd = 15
                            break
            for en in [e for e in enemies if e.char.get("chainsaw") and e.hp > 0]:
                if en.chainsaw_cd > 0:
                    en.chainsaw_cd -= 1
                else:
                    for p in living:
                        if abs(en.x - p.x) < 50:
                            p.take_proj_dmg(4, flash=False)
                            p.flash_timer = 4
                            en.chainsaw_cd = 15
                            break

            # Toxic aura — proximity poison (survival)
            for toxic in [p for p in players if p.char.get("toxic_aura") and p.hp > 0]:
                for en in enemies:
                    if (en.contact_cooldown == 0 and
                            math.hypot(toxic.x - en.x, (toxic.y - 60) - (en.y - 60)) < 80):
                        en.take_proj_dmg(2)
                        en.flash_timer = 4
                        en.contact_cooldown = 90
                        if en.poison_frames == 0: en.poison_tick = 180
                        en.poison_frames = max(en.poison_frames, 360)
            for en in [e for e in enemies if e.char.get("toxic_aura") and e.hp > 0]:
                for p in living:
                    if (p.contact_cooldown == 0 and
                            math.hypot(en.x - p.x, (en.y - 60) - (p.y - 60)) < 80):
                        p.take_proj_dmg(2)
                        p.flash_timer = 4
                        p.contact_cooldown = 90
                        if not p.char.get("immune"):
                            if p.poison_frames == 0: p.poison_tick = 180
                            p.poison_frames = max(p.poison_frames, 360)

            # Death pops: spawn burst when enemy hp hits 0, then remove enemy
            for en in enemies:
                if en.hp <= 0:
                    death_pops.append({'x': en.x, 'y': en.y - 60,
                                       'color': en.char["color"], 't': 22})
            for dp in death_pops:
                dp['t'] -= 1
            death_pops = [dp for dp in death_pops if dp['t'] > 0]

            # Count kills, remove dead enemies
            before         = len(enemies)
            enemies        = [en for en in enemies if en.hp > 0]
            enemies_killed += before - len(enemies)

            # Jungle snakes
            if is_jungle:
                snake_spawn_timer -= 1
                if snake_spawn_timer <= 0 and len(jungle_snakes) < 4:
                    jungle_snakes.append(JungleSnake())
                    snake_spawn_timer = random.randint(300, 480)
                for sn in jungle_snakes:
                    all_targets = players + enemies
                    living_targets = [t for t in all_targets if t.hp > 0]
                    if living_targets:
                        closest = min(living_targets, key=lambda t: abs(t.x - sn.x))
                        sn.update(closest, closest)
                jungle_snakes = [sn for sn in jungle_snakes if sn.alive]

            if is_underworld:
                skull_spawn_timer -= 1
                if skull_spawn_timer <= 0 and len(falling_skulls) < 8:
                    falling_skulls.append(FallingSkull())
                    skull_spawn_timer = random.randint(120, 280)
                for sk in falling_skulls:
                    sk.update()
                    if sk.hit_cd == 0:
                        for victim in [p for p in players if p.hp > 0] + enemies:
                            if sk.collides(victim):
                                victim.take_proj_dmg(sk.DMG)
                                victim.flash_timer = 10
                                sk.hit_cd = sk.HIT_CD

            if is_computer:
                bug_spawn_timer -= 1
                if bug_spawn_timer <= 0 and len(computer_bugs) < 5:
                    computer_bugs.append(ComputerBug())
                    bug_spawn_timer = random.randint(200, 360)
                for b in computer_bugs:
                    all_targets = [p for p in players if p.hp > 0] + enemies
                    target = min(all_targets, key=lambda t: abs(t.x - b.x)) if all_targets else None
                    b.update(target)
                computer_bugs = [b for b in computer_bugs if b.alive]
                stage_pencil.update()
                drawn_count = sum(1 for p in platforms if isinstance(p, DrawnPlatform))
                if stage_pencil.pending_plat and drawn_count < StagePencil.MAX_PLATS:
                    stage_pencil.pending_plat = False
                    platforms.append(DrawnPlatform(int(stage_pencil.x) - 50, int(stage_pencil.y) + 20, w=100))
                platforms = stage_eraser.update(platforms)
                for p in platforms:
                    if isinstance(p, DrawnPlatform): p.update()
                platforms = [p for p in platforms if not (isinstance(p, DrawnPlatform) and not p.alive)]
                for pf in [p for p in players if p.hp > 0]:
                    if pf.contact_cooldown == 0:
                        if math.hypot(pf.x - stage_eraser.x, pf.y - stage_eraser.y) < 50:
                            pf.hp = max(0, pf.hp - 5)
                            pf.flash_timer = 8
                            pf.contact_cooldown = 60

            # Powerups (no clone type in survival)
            _survival_pool = [p for p in POWERUPS if p['type'] != 'clone']
            powerup_timer -= 1
            if powerup_timer <= 0 and len(powerups) < 3:
                pu_new = Powerup.__new__(Powerup)
                pu_new.spec = random.choice(_survival_pool)
                pu_new.name = pu_new.spec['name']
                pu_new.color = pu_new.spec['color']
                pu_new.x = float(random.randint(80, WIDTH - 80))
                pu_new.y = float(GROUND_Y - 14)
                pu_new.age = 0
                pu_new.picked_up = False
                powerups.append(pu_new)
                powerup_timer = random.randint(480, 720)
            for pu in powerups:
                pu.update()
                for p in players:
                    if p.hp > 0 and not pu.picked_up and pu.collides(p):
                        p.apply_powerup(pu.spec)
                        pu.picked_up = True; break
                if not pu.picked_up:
                    for en in enemies:
                        if pu.collides(en):
                            en.apply_powerup(pu.spec)
                            pu.picked_up = True; break
            powerups = [pu for pu in powerups if not pu.picked_up]

            # Everything powerup — poop out random powerups (survival)
            for f in players:
                if f.poop_timer > 0 and f.poop_cd == 0:
                    pu_p = Powerup.__new__(Powerup)
                    pu_p.spec = random.choice(_survival_pool)
                    pu_p.name = pu_p.spec['name']
                    pu_p.color = pu_p.spec['color']
                    pu_p.x = f.x - f.facing * 20
                    pu_p.y = float(GROUND_Y - 14)
                    pu_p.age = 0
                    pu_p.picked_up = False
                    powerups.append(pu_p)
                    f.poop_cd = 30

            # Kamikaze death explosion (survival)
            for p in players:
                if (p.char.get("explode_death") and p.hp <= 0
                        and not p.kamikaze_exploded):
                    p.kamikaze_exploded = True
                    kamikaze_pops.append({'x': p.x, 'y': p.y - 60, 't': 20})
                    for en in enemies:
                        if math.hypot(p.x - en.x, (p.y - 60) - (en.y - 60)) < 150:
                            en.hp = max(0, en.hp - 60)
                            en.flash_timer = 20
                            # Enemy had < 60 HP — explosion kills them; kamikaze survives
                            if en.hp <= 0:
                                p.hp = 1
                                p.action = 'idle'
                                p.flash_timer = 20
            for kp in kamikaze_pops:
                kp['t'] -= 1
            kamikaze_pops = [kp for kp in kamikaze_pops if kp['t'] > 0]

            # Bomb character: spawn center-screen bomb every 5 seconds (survival)
            for _sp in players:
                if _sp.char.get("bomb_character") and _sp.hp > 0:
                    _sp.bomb_spawn_timer -= 1
                    if _sp.bomb_spawn_timer <= 0:
                        _sbdmg = 200 if _sp.char.get("nuke_bomb") else 100
                        survival_bombs.append({'x': float(WIDTH // 2), 'y': float(GROUND_Y - 80), 'fuse': 120, 'dmg': _sbdmg})
                        _sp.bomb_spawn_timer = FPS * 5
            _new_sbombs = []
            for _sb in survival_bombs:
                _sb['fuse'] -= 1
                if _sb['fuse'] <= 0:
                    for _victim in list(players) + enemies:
                        if math.hypot(_victim.x - _sb['x'], (_victim.y - 60) - _sb['y']) < 180:
                            _victim.hp = max(0, _victim.hp - _sb.get('dmg', 100))
                            _victim.flash_timer = 20
                    survival_bomb_pops.append({'x': _sb['x'], 'y': _sb['y'], 't': 25})
                else:
                    _new_sbombs.append(_sb)
            survival_bombs = _new_sbombs
            for _sbp in survival_bomb_pops:
                _sbp['t'] -= 1
            survival_bomb_pops = [bp for bp in survival_bomb_pops if bp['t'] > 0]

            # Game over when all players dead
            if all(p.hp <= 0 for p in players):
                game_over = True

        # --- Draw ---
        draw_bg(screen, stage_idx)
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for portal in portals_obj_s: portal.draw(screen)
        for plat in platforms:     plat.draw(screen, stage_idx)
        for sp   in springs:       sp.draw(screen)
        for pu   in powerups:      pu.draw(screen)
        for b    in balls:         b.draw(screen)
        for ao   in arcane_orbs:   ao.draw(screen)
        for sb   in sun_beams:     sb.draw(screen)
        for nb   in nian_breaths:  nb.draw(screen)
        for dove in liberty_doves: dove.draw(screen)
        for lb in liberty_bombs:
            bx, by = int(lb['x']), int(lb['y'])
            pygame.draw.circle(screen, (255, 255, 255), (bx, by), 7)
            pygame.draw.circle(screen, (200, 220, 200), (bx, by), 4)
        for gy in yellowstone_geysers:
            gx, age = int(gy['x']), gy['age']
            if age <= 22:
                h = min(age * 6, 130)
                pygame.draw.rect(screen, (160, 220, 255), (gx - 7, GROUND_Y - h, 14, h))
                pygame.draw.circle(screen, (220, 240, 255), (gx, GROUND_Y - h), 10)
            elif age <= 40:
                r = int((age - 22) * 5) + 8
                pygame.draw.circle(screen, (255, 255, 255), (gx, GROUND_Y - 110), r)
                pygame.draw.circle(screen, (180, 230, 255), (gx, GROUND_Y - 110), r + 4, 3)
        for swb  in survival_widow_bugs: swb['bug'].draw(screen)
        for b    in en_balls:      b.draw(screen)
        for o    in orbs:          o.draw(screen)
        for o    in en_orbs:       o.draw(screen)
        for bb   in bounce_balls:  bb.draw(screen)
        for bb   in en_bounce_balls: bb.draw(screen)
        for sc   in survival_scrolls: sc.draw(screen)
        for t    in survival_totems:  t.draw(screen)
        for r    in survival_remotes: r.draw(screen)
        for ap   in survival_apples:  ap.draw(screen)
        for ps   in survival_plants:  ps.draw(screen)
        for h    in hooks:         h.draw(screen)
        for h    in en_hooks:      h.draw(screen)
        for pk   in pumpkins:      pk.draw(screen)
        for js   in jack_seeds:    js.draw(screen)
        for fp   in fruit_projs:   fp.draw(screen)
        for cp   in coal_projs:    cp.draw(screen)
        for tb   in thunder_bolts: tb.draw(screen)
        for pk   in en_pumpkins:   pk.draw(screen)
        for w    in whips:         w.draw(screen)
        for w    in en_whips:      w.draw(screen)
        for sn   in jungle_snakes: sn.draw(screen)
        for sk   in falling_skulls: sk.draw(screen)
        for b    in computer_bugs: b.draw(screen)
        if is_computer and stage_pencil:
            stage_pencil.draw(screen)
            stage_eraser.draw(screen)
        for ic   in ink_clones:    ic['fighter'].draw(screen)

        # Draw Laser Eyes beams (survival)
        for f in list(players) + enemies:
            if f.char.get("laser_eyes") and f.laser_active > 0:
                eye_x = int(f.x)
                eye_y = int(f.y - 100)
                end_x = WIDTH if f.facing == 1 else 0
                x = eye_x
                while (f.facing == 1 and x < end_x) or (f.facing == -1 and x > end_x):
                    dash_end = x + f.facing * 18
                    dash_end = min(dash_end, end_x) if f.facing == 1 else max(dash_end, end_x)
                    pygame.draw.line(screen, (255, 40, 0),   (x, eye_y), (dash_end, eye_y), 3)
                    pygame.draw.line(screen, (255, 160, 80), (x, eye_y), (dash_end, eye_y), 1)
                    x = dash_end + f.facing * 6

        # Death burst particles
        for dp in death_pops:
            prog  = 1.0 - dp['t'] / 22
            r     = int(4 + prog * 28)
            col   = dp['color']
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                px  = int(dp['x'] + math.cos(rad) * r * 1.4)
                py  = int(dp['y'] + math.sin(rad) * r)
                cr  = max(1, int(6 * (1.0 - prog)))
                pygame.draw.circle(screen, col, (px, py), cr)
            pygame.draw.circle(screen, WHITE, (int(dp['x']), int(dp['y'])), max(1, int(10 * (1.0 - prog))))
        # Kamikaze explosion ring
        for kp in kamikaze_pops:
            prog = 1.0 - kp['t'] / 20
            r    = max(1, int(10 + prog * 140))
            col  = (255, max(0, int(180 - prog * 180)), 0)
            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                px  = int(kp['x'] + math.cos(rad) * r)
                py  = int(kp['y'] + math.sin(rad) * r)
                cr  = max(1, int(7 * (1.0 - prog)))
                pygame.draw.circle(screen, col, (px, py), cr)
            if prog < 0.35:
                inner = max(1, int(28 * (0.35 - prog) / 0.35))
                pygame.draw.circle(screen, (255, 255, 180), (int(kp['x']), int(kp['y'])), inner)
        # Draw survival bombs and explosion rings
        for _sb in survival_bombs:
            _pulse = abs(math.sin(_sb['fuse'] * 0.13)) * 8
            _br = int(16 + _pulse)
            pygame.draw.circle(screen, (200, 80, 20), (int(_sb['x']), int(_sb['y'])), _br)
            pygame.draw.circle(screen, (255, 220, 60), (int(_sb['x']), int(_sb['y'])), _br, 3)
            _fuse_pct = _sb['fuse'] / 120
            _fc = (int(255 * (1 - _fuse_pct)), int(255 * _fuse_pct), 0)
            _ft = font_tiny.render(f"BOMB {_sb['fuse']//FPS+1}s", True, _fc)
            screen.blit(_ft, (int(_sb['x']) - _ft.get_width()//2, int(_sb['y']) - _br - 16))
        for _sbp in survival_bomb_pops:
            _prog = 1.0 - _sbp['t'] / 25
            _r = max(1, int(15 + _prog * 165))
            _a = max(0, int(220 * (1.0 - _prog)))
            _bsurf2 = pygame.Surface((_r*2+4, _r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(_bsurf2, (255, 140, 20, _a), (_r+2, _r+2), _r, 5)
            screen.blit(_bsurf2, (int(_sbp['x']) - _r - 2, int(_sbp['y']) - _r - 2))

        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen) if two_player else None
        en_hits = [(en, en.draw(screen)) for en in enemies]
        # Bubble shield visuals (survival)
        for f in players:
            if f.bubble_shield:
                bsurf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(bsurf, (100, 200, 255, 70), (50, 50), 48)
                pygame.draw.circle(bsurf, (100, 200, 255, 160), (50, 50), 48, 3)
                screen.blit(bsurf, (int(f.x) - 50, int(f.y) - 90))

        if not game_over:
            # Player attacks hit enemies
            for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                if attacker.attacking and not attacker.attack_hit and hit_pos:
                    for en in enemies:
                        attacker.check_hit(hit_pos, en)
            # Enemy attacks hit players — 2P players can't hurt each other
            for en, en_hit in en_hits:
                if en.attacking and not en.attack_hit and en_hit:
                    for p in players:
                        en.check_hit(en_hit, p)
            # Fighter attacks on jungle snakes
            for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                if attacker.attacking and hit_pos:
                    for sn in jungle_snakes:
                        if math.hypot(hit_pos[0]-sn.x, hit_pos[1]-(sn.y-8)) < 44:
                            dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                   else attacker.char["kick_dmg"])
                            sn.take_damage(dmg)
            # Fighter attacks on computer bugs
            if is_computer:
                for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                    if attacker.attacking and hit_pos:
                        for b in computer_bugs:
                            if math.hypot(hit_pos[0]-b.x, hit_pos[1]-(b.y-8)) < 40:
                                dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                       else attacker.char["kick_dmg"])
                                b.take_damage(dmg)

        # Enemy name tags
        for en in enemies:
            tag = font_tiny.render(en.char["name"], True, en.char["color"])
            screen.blit(tag, (int(en.x) - tag.get_width()//2,
                               int(en.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        _draw_survival_hud()
        draw_active_powerups(screen, p1, 'left')
        if two_player:
            draw_active_powerups(screen, p2, 'right')
        if game_over:
            _draw_game_over()

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Online fight helpers
# ---------------------------------------------------------------------------

class _KeyProxy:
    """Lets Fighter.update() accept a dict instead of pygame.key.get_pressed()."""
    def __init__(self, mapping):
        self._m = mapping   # {pygame_key_const: bool}
    def __getitem__(self, k): return self._m.get(k, False)
    def get(self, k, d=False): return self._m.get(k, d)


def _f2s(f):
    """Serialize the fields a remote client needs to render a fighter."""
    return {
        'x': f.x, 'y': f.y, 'hp': f.hp,
        'action': f.action, 'action_t': f.action_t,
        'facing': f.facing, 'vy': f.vy, 'on_ground': f.on_ground,
        'knockback': f.knockback,
        'hurt_timer': f.hurt_timer, 'flash_timer': f.flash_timer,
        'draw_scale': f.draw_scale,
        'attacking': f.attacking, 'attack_hit': f.attack_hit,
        'laser_active': f.laser_active,
        'boomerang_timer': f.boomerang_timer,
        'boomerang_angle': f.boomerang_angle,
        'stealth_frames': f.stealth_frames,
        'bubble_shield': f.bubble_shield,
        'fire_frames': f.fire_frames, 'fire_tick': f.fire_tick,
        'shock_frames': f.shock_frames,
        'freeze_frames': f.freeze_frames,
        'poison_frames': f.poison_frames, 'poison_tick': f.poison_tick,
        'confuse_frames': f.confuse_frames,
        'squish_frames': f.squish_frames,
    }


def _s2f(f, s):
    """Apply a serialized state dict to a fighter (client-side rendering)."""
    f.x = s['x']; f.y = s['y']; f.hp = s['hp']
    f.action = s['action']; f.action_t = s['action_t']
    f.facing = s['facing']; f.vy = s['vy']
    f.on_ground = s.get('on_ground', True)
    f.knockback = s['knockback']
    f.hurt_timer = s['hurt_timer']; f.flash_timer = s['flash_timer']
    f.draw_scale = s.get('draw_scale', 1.0)
    f.attacking = s.get('attacking', False)
    f.attack_hit = s.get('attack_hit', False)
    f.laser_active = s.get('laser_active', 0)
    f.boomerang_timer = s.get('boomerang_timer', 0)
    f.boomerang_angle = s.get('boomerang_angle', 0.0)
    f.stealth_frames = s.get('stealth_frames', 0)
    f.bubble_shield = s.get('bubble_shield', False)
    f.fire_frames = s.get('fire_frames', 0); f.fire_tick = s.get('fire_tick', 0)
    f.shock_frames = s.get('shock_frames', 0)
    f.freeze_frames = s.get('freeze_frames', 0)
    f.poison_frames = s.get('poison_frames', 0); f.poison_tick = s.get('poison_tick', 0)
    f.confuse_frames = s.get('confuse_frames', 0)
    f.squish_frames = s.get('squish_frames', 0)


# ---------------------------------------------------------------------------
# Online fight loop
# ---------------------------------------------------------------------------

def run_online_fight(net, is_host, p1_char_idx, p2_char_idx,
                     stage_idx, my_name, opp_name, userdata=None):
    """
    Networked 1v1 fight.
    * Host (is_host=True)  runs the authoritative sim and sends STATE each frame.
    * Client (is_host=False) sends INPUT each frame and renders received STATE.
    * p1 = host's fighter (left), p2 = client's fighter (right) on both screens.
    * Both players use P1_CTRL (WASD/FG) on their own machines; the client's
      inputs are remapped to P2_CTRL by the host before simulation.
    """
    _stage_name   = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13
    constants.STAGE_VOID    = (_stage_name in ("The Void", "Conveyor World"))
    constants.STAGE_CEILING = (_stage_name == "The Nether")

    P1_CTRL = dict(left=pygame.K_a,     right=pygame.K_d,     jump=pygame.K_w,
                   punch=pygame.K_f,    kick=pygame.K_g,      duck=pygame.K_s,
                   block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT,  right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k,    kick=pygame.K_l,      duck=pygame.K_DOWN,
                   block=pygame.K_o)

    p1 = Fighter(200, CHARACTERS[p1_char_idx],  1, P1_CTRL)
    p2 = Fighter(700, CHARACTERS[p2_char_idx], -1, {})

    if constants.STAGE_VOID:
        p1.x = 380.0; p1.y = float(GROUND_Y - 70); p1.on_ground = True
        p2.x = 520.0; p2.y = float(GROUND_Y - 70); p2.on_ground = True

    stage_data   = STAGES[stage_idx % len(STAGES)]
    platforms    = [Platform(*p) for p in stage_data["platforms"]]
    springs      = [Spring(*s)   for s in stage_data["springs"]]
    balls        = []; orbs = []; bounce_balls = []; hooks = []; pumpkins = []; whips = []
    charged_orbs = []; bubble_shots = []; poison_orbs = []; scrolls = []; venoms = []
    notes        = []; kitsune_shots = []; water_balls = []; bee_shots = []; snipe_shots = []
    fire_balls   = []; thunder_bolts = []; plant_spikes = []; arcane_orbs = []; sun_beams = []
    nian_breaths = []
    liberty_doves = []; liberty_bombs = []; yellowstone_geysers = []; jack_seeds = []
    fruit_projs   = []   # FruitProj (Cornucopia)
    coal_projs    = []   # CoalProj (Saint Nix)

    # Easter eggs
    hot_potatoes   = []
    crazy_snakes   = []
    crazy_bugs     = []
    crazy_timer    = 0
    falling_pots   = []
    rolling_coins  = []
    falling_merlins = []
    cooking_timer  = 0   # frames remaining of pot rain
    rain_powerups  = []
    rain_timer     = 0   # frames remaining of powerup rain
    rain_cd        = 0
    rain_type      = None  # 'heal' or 'poison'
    baseballs      = []
    flying_bats    = []
    baseball_timer = 0
    baseball_cd    = 0   # cooldown between ball/bat spawns
    _chat_done     = 0   # index into net.chat_log already processed for easter eggs

    game_over    = False
    winner       = None
    timer        = 90 * FPS
    _remote_keys = {}   # action → bool  (latest from opponent; host uses for p2)

    # Chat
    chat_active  = False
    chat_input   = ""

    def _local_actions(keys, ctrl):
        return {a: bool(keys[ctrl[a]]) for a in ctrl}

    def _proxy(actions, ctrl):
        """Map {action: bool} through ctrl keys into a _KeyProxy."""
        return _KeyProxy({ctrl[a]: actions.get(a, False) for a in ctrl})

    while True:
        clock.tick(FPS)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                constants.GRAVITY = _orig_gravity
                constants.STAGE_VOID = False; constants.STAGE_CEILING = False
                net.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if chat_active:
                    if event.key == pygame.K_RETURN:
                        if chat_input.strip():
                            net.send_chat(chat_input)
                        chat_active = False; chat_input = ""
                    elif event.key == pygame.K_ESCAPE:
                        chat_active = False; chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    elif event.unicode.isprintable():
                        chat_input += event.unicode
                else:
                    if event.key == pygame.K_t:
                        chat_active = True
                    if game_over and event.key in (pygame.K_q, pygame.K_ESCAPE,
                                                   pygame.K_RETURN, pygame.K_r):
                        constants.GRAVITY = _orig_gravity
                        constants.STAGE_VOID = False; constants.STAGE_CEILING = False
                        net.close(); return 'select'

        if not net.connected and not game_over:
            game_over = True
            winner    = "disconnect"

        # ── Network ─────────────────────────────────────────────────────────
        msgs = net.recv_all()
        keys = pygame.key.get_pressed()

        # ── Easter eggs (host-authoritative; triggered by chat keywords) ────
        if is_host and not game_over:
            while _chat_done < len(net.chat_log):
                sender, text = net.chat_log[_chat_done]
                kw = text.strip().lower()
                if kw == "hotpotato":
                    hot_potatoes.append(HotPotato())
                elif kw == "wtf":
                    target = p1 if sender == "You" else p2
                    target.hp = max(0, target.hp - 10)
                    target.flash_timer = 25
                elif kw == "crazy":
                    crazy_timer = FPS * 8   # 8 seconds of chaos
                elif kw == "imcooking":
                    cooking_timer = FPS * 10  # pots rain for 10 seconds
                elif kw == "imdead":
                    target = p1 if sender == "You" else p2
                    target.hp = 0
                elif kw == "imselling":
                    rolling_coins.append(RollingCoin())
                elif kw == "merlin":
                    for _ in range(8):
                        falling_merlins.append(FallingMerlin())
                elif kw == "randomskin":
                    target = p1 if sender == "You" else p2
                    new_char = random.choice(
                        [c for c in CHARACTERS if c['name'] != target.char['name']])
                    target.char = new_char
                    target.color = new_char['color']
                elif kw == "kevin=great":
                    rain_timer = FPS * 8
                    rain_type  = 'heal'
                elif kw == "kevin=bad":
                    rain_timer = FPS * 8
                    rain_type  = 'poison'
                elif kw == "strike":
                    baseball_timer = FPS * 15   # 15 seconds of baseball chaos
                _chat_done += 1

        if is_host and not game_over:
            # Collect latest client input
            for m in msgs:
                if m.get("type") == "INPUT":
                    _remote_keys = m

            # Simulate p1 (local)
            p1.update(keys, p2, platforms)

            # Simulate p2 using client's inputs remapped through P2_CTRL
            p2.update(_proxy(_remote_keys, P2_CTRL), p1, platforms)

            # Spawn projectiles for both fighters
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing * 30,
                                            shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing * 30,
                                    shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing * 30,
                                                     shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_hook:
                    shooter.pending_hook = False
                    hooks.append(SnakeHook(shooter.x + shooter.facing * 20, shooter.y - 60,
                                           victim.x, victim.y - 60, shooter))
                if shooter.pending_pumpkin or shooter.pending_jack_pumpkin:
                    shooter.pending_pumpkin = False
                    shooter.pending_jack_pumpkin = False
                    pumpkins.append(Pumpkin(shooter.x + shooter.facing * 24,
                                            shooter.y - 80, shooter.facing, shooter))
                if shooter.pending_jack_seed:
                    shooter.pending_jack_seed = False
                    jack_seeds.append(PumpkinSeed(shooter.x + shooter.facing * 24,
                                                  shooter.y - 60, shooter.facing, shooter))
            for js in jack_seeds:
                js.update()
                if js.alive:
                    victim = p2 if js.owner is p1 else p1
                    if js.collides(victim):
                        victim.take_proj_dmg(PumpkinSeed.DMG)
                        victim.flash_timer = max(victim.flash_timer, 8)
                        js.alive = False
            jack_seeds = [js for js in jack_seeds if js.alive]
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_fruit_attack:
                    fa = shooter.pending_fruit_attack
                    shooter.pending_fruit_attack = None
                    _fx = shooter.x + shooter.facing * 30
                    _fy = shooter.y - 60
                    if fa[0] == 'cranberry_burst':
                        for _ci in range(4):
                            fruit_projs.append(FruitProj(_fx, _fy + _ci * 5,
                                               shooter.facing, shooter, 'cranberry'))
                    elif fa[0] == 'grape_rain':
                        for _gi in range(7):
                            gx = random.randint(50, WIDTH - 50)
                            fruit_projs.append(FruitProj(gx, -20, shooter.facing,
                                               shooter, 'grape', vy=4.0 + random.random() * 2))
                    elif fa[0] == 'coal':
                        coal_projs.append(CoalProj(_fx, _fy, shooter.facing, shooter, fa[1]))
                    else:
                        fruit_projs.append(FruitProj(_fx, _fy, shooter.facing, shooter, fa[0]))
            for fp in fruit_projs:
                fp.update()
                if fp.alive:
                    victim = p2 if fp.owner is p1 else p1
                    if fp.collides(victim):
                        _apply_fruit_hit(victim, fp)
                        fp.alive = False
            fruit_projs = [fp for fp in fruit_projs if fp.alive]
            for cp in coal_projs:
                cp.update()
                if cp.alive:
                    victim = p2 if cp.owner is p1 else p1
                    if cp.collides(victim):
                        _apply_coal_hit(victim, cp)
                        cp.alive = False
            coal_projs = [cp for cp in coal_projs if cp.alive]

            # Update projectiles
            for b in balls:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        victim.take_proj_dmg(10)
                        victim.flash_timer = 8; b.alive = False
            balls = [b for b in balls if b.alive]

            # Arcanist: arcane orbs (network)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_arcane_orb:
                    shooter.pending_arcane_orb = False
                    arcane_orbs.append(ArcaneOrb(shooter.x + shooter.facing * 30,
                                                  shooter.y - 60, shooter.facing, shooter))
            for ao in arcane_orbs:
                ao.update()
                if ao.alive:
                    victim = p2 if ao.owner is p1 else p1
                    if ao.collides(victim):
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(ArcaneOrb.DMG)
                        victim.flash_timer = 8
                        ao.alive = False
            arcane_orbs = [ao for ao in arcane_orbs if ao.alive]

            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    victim = p2 if o.owner is p1 else p1
                    if math.hypot(o.x - victim.x, o.y - (victim.y - 60)) < o.EXPLODE_RADIUS:
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(o.EXPLODE_DMG)
                        victim.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    victim = p2 if bb.owner is p1 else p1
                    if bb.collides(victim):
                        victim.take_proj_dmg(10)
                        victim.flash_timer = 8; bb.hit_cd = BouncingBall.HIT_CD
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            for h in hooks:
                h.update()
                if h.alive:
                    victim = p2 if h.owner is p1 else p1
                    if h.collides(victim):
                        pull = 1 if h.owner.x > victim.x else -1
                        victim.knockback = pull * 22
                        victim.take_proj_dmg(6)
                        victim.flash_timer = 8; h.alive = False
            hooks = [h for h in hooks if h.alive]

            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    victim = p2 if pk.owner is p1 else p1
                    if math.hypot(pk.x - victim.x, pk.y - (victim.y - 60)) < pk.EXPLODE_RADIUS:
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(pk.EXPLODE_DMG)
                        victim.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    victim = p2 if pk.owner is p1 else p1
                    if pk.collides(victim): pk._explode()
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Whips
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_whip:
                    shooter.pending_whip = False
                    whips.append(Whip(
                        shooter.x + shooter.facing * 28, shooter.y - 60,
                        shooter.facing, shooter))
            for w in whips:
                w.update()
                if w.can_hit():
                    victim = p2 if w.owner is p1 else p1
                    if w.collides(victim):
                        victim.take_proj_dmg(w.DMG)
                        victim.flash_timer = 10
                        victim.knockback = w.facing * 14
                        w.hit_done = True
            whips = [w for w in whips if w.alive]

            # Charged orbs (Orb Shooter)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_charged_orb:
                    charge = shooter.pending_charged_orb
                    shooter.pending_charged_orb = 0
                    charged_orbs.append(ChargedOrb(
                        shooter.x + shooter.facing * 30,
                        shooter.y - 60, shooter.facing, shooter, charge))
            for co in charged_orbs:
                co.update()
                if co.alive:
                    victim = p2 if co.owner is p1 else p1
                    if co.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; co.alive = False
                        else:
                            victim.take_proj_dmg(co.dmg)
                            victim.flash_timer = max(victim.flash_timer, 12); co.alive = False
            charged_orbs = [co for co in charged_orbs if co.alive]

            # Bubble shots (Windshield Viper)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bubble_shot:
                    shooter.pending_bubble_shot = False
                    bubble_shots.append(BubbleShot(
                        shooter.x + shooter.facing * 30,
                        shooter.y - 60, shooter.facing, shooter))
            for bs in bubble_shots:
                bs.update()
                if bs.alive:
                    victim = p2 if bs.owner is p1 else p1
                    if bs.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; bs.alive = False
                        else:
                            victim.take_proj_dmg(10)
                            victim.flash_timer = 8; bs.alive = False
            bubble_shots = [bs for bs in bubble_shots if bs.alive]

            # Poison orbs (King Cobra)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_poison_orb:
                    shooter.pending_poison_orb = False
                    poison_orbs.append(PoisonOrb(
                        shooter.x + shooter.facing * 30,
                        shooter.y - 60, shooter.facing, shooter))
            for po in poison_orbs:
                po.update()
                if po.alive:
                    victim = p2 if po.owner is p1 else p1
                    if po.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; po.alive = False
                        else:
                            victim.take_proj_dmg(15)
                            victim.poison_frames = max(victim.poison_frames, FPS * 6)
                            victim.poison_tick   = min(victim.poison_tick if victim.poison_tick > 0 else 999, 60)
                            victim.flash_timer   = 15; po.alive = False
            poison_orbs = [po for po in poison_orbs if po.alive]

            # Scrolls (Scrollmaster)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_scroll:
                    shooter.pending_scroll = False
                    scrolls.append(Scroll(shooter.x + shooter.facing * 30,
                                          shooter.y - 60, shooter.facing, shooter))
            for sc in scrolls:
                sc.update()
                if sc.alive and sc.hit_cd == 0:
                    victim = p2 if sc.owner is p1 else p1
                    if sc.collides(victim):
                        victim.take_proj_dmg(Scroll.DMG)
                        victim.flash_timer = 8; sc.hit_cd = Scroll.HIT_CD
            scrolls = [sc for sc in scrolls if sc.alive]

            # Venom beans (Spitting Cobra)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_venom:
                    shooter.pending_venom = False
                    venoms.append(VenomBean(shooter.x + shooter.facing * 30,
                                            shooter.y - 60, shooter.facing, shooter))
            for vb in venoms:
                vb.update()
                if not vb.hit:
                    victim = p2 if vb.owner is p1 else p1
                    if vb.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; vb.alive = False
                        else:
                            victim.take_proj_dmg(VenomBean.DMG)
                            victim.flash_timer = 8
                            if victim.poison_frames == 0: victim.poison_tick = 180
                            victim.poison_frames = max(victim.poison_frames, 360)
                            vb.hit = True; vb.alive = False
            venoms = [vb for vb in venoms if vb.alive]

            # Music notes (Bard)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_note:
                    shooter.pending_note = False
                    notes.append(MusicNote(shooter.x + shooter.facing * 30,
                                           shooter.y - 60, shooter.facing, shooter))
            for nt in notes:
                nt.update()
                if nt.alive:
                    victim = p2 if nt.owner is p1 else p1
                    if nt.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; nt.alive = False
                        else:
                            victim.take_proj_dmg(MusicNote.DMG)
                            victim.flash_timer = 8
                            victim.hurt_timer = max(victim.hurt_timer, 120)
                            nt.alive = False
            notes = [nt for nt in notes if nt.alive]

            # Kitsune barrage (9 shots)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_kitsune:
                    shooter.pending_kitsune = False
                    for i in range(9):
                        kitsune_shots.append(KitsuneShot(shooter.x, shooter.y - 70, i * 40.0, shooter))
            for ks in kitsune_shots:
                ks.update()
                if ks.alive:
                    victim = p2 if ks.owner is p1 else p1
                    if ks.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; ks.alive = False
                        else:
                            victim.take_proj_dmg(KitsuneShot.DMG)
                            victim.flash_timer = 8; ks.alive = False
            kitsune_shots = [ks for ks in kitsune_shots if ks.alive]

            # Water balls (Riptide)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_water_ball:
                    shooter.pending_water_ball = False
                    water_balls.append(WaterBall(shooter.x + shooter.facing * 30,
                                                 shooter.y - 60, shooter.facing, shooter))
            for wb in water_balls:
                wb.update()
                if wb.alive:
                    victim = p2 if wb.owner is p1 else p1
                    if wb.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; wb.alive = False
                        else:
                            victim.take_proj_dmg(WaterBall.DMG)
                            victim.flash_timer = 8; wb.alive = False
            water_balls = [wb for wb in water_balls if wb.alive]

            # Bee shots (Beekeeper — 5 spread)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bee:
                    shooter.pending_bee = False
                    for dvy in (-4, -2, 0, 2, 4):
                        bee_shots.append(BeeShot(shooter.x + shooter.facing * 30,
                                                 shooter.y - 60, shooter.facing, shooter, vy=dvy))
            for b in bee_shots:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; b.alive = False
                        else:
                            victim.take_proj_dmg(BeeShot.DMG)
                            victim.flash_timer = 6; b.alive = False
            bee_shots = [b for b in bee_shots if b.alive]

            # Snipe shots (Shifter)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_snipe:
                    shooter.pending_snipe = False
                    snipe_shots.append(SnipeShot(shooter.x + shooter.facing * 30,
                                                 shooter.y - 80, shooter.facing, shooter))
            for s in snipe_shots:
                s.update()
                if s.alive:
                    victim = p2 if s.owner is p1 else p1
                    if s.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; s.alive = False
                        else:
                            victim.take_proj_dmg(SnipeShot.DMG)
                            victim.flash_timer = 10; s.alive = False
            snipe_shots = [s for s in snipe_shots if s.alive]

            # Fire balls (Pyro + Nian breath)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_autofire:
                    shooter.pending_autofire = False
                    fire_balls.append(FireBall(shooter.x + shooter.facing * 30,
                                               shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_nian_breath:
                    shooter.pending_nian_breath = False
                    nian_breaths.append(NianBreath(shooter.x + shooter.facing * 18,
                                                   shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_sun_beam:
                    shooter.pending_sun_beam = False
                    sun_beams.append(SunBeam(shooter.x + shooter.facing * 30,
                                             shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_liberty_dove:
                    shooter.pending_liberty_dove = False
                    liberty_doves.append(LibertyDove(shooter.x, shooter.y, shooter))
            for dove in liberty_doves:
                dove.update()
                if dove.pending_bomb:
                    dove.pending_bomb = False
                    liberty_bombs.append({'x': dove.x, 'y': dove.y, 'vy': 0.0, 'alive': True, 'owner': dove.owner})
            liberty_doves = [d for d in liberty_doves if d.alive]
            for lb in liberty_bombs:
                lb['vy'] = min(lb['vy'] + 0.9, 22)
                lb['y'] += lb['vy']
                if lb['y'] >= GROUND_Y - 4:
                    for victim in (p1, p2):
                        if victim is not lb['owner'] and abs(victim.x - lb['x']) < 65:
                            victim.take_proj_dmg(15)
                            victim.flash_timer = max(victim.flash_timer, 14)
                    lb['alive'] = False
            liberty_bombs = [lb for lb in liberty_bombs if lb['alive']]
            for shooter in (p1, p2):
                if shooter.pending_yellowstone_geysers:
                    shooter.pending_yellowstone_geysers = False
                    for i in range(10):
                        gx = 60 + (WIDTH - 120) * i / 9 + random.uniform(-25, 25)
                        gx = max(60.0, min(float(WIDTH - 60), gx))
                        yellowstone_geysers.append({'x': gx, 'age': 0, 'alive': True,
                                                    'owner': shooter, 'hit': False})
            new_gy = []
            for gy in yellowstone_geysers:
                gy['age'] += 1
                if gy['age'] <= 60:
                    new_gy.append(gy)
                    victim = p2 if gy['owner'] is p1 else p1
                    if not gy['hit'] and 22 <= gy['age'] <= 40:
                        if abs(victim.x - gy['x']) < 52 and victim.hp > 0:
                            victim.take_proj_dmg(12)
                            victim.flash_timer = max(victim.flash_timer, 10)
                            gy['hit'] = True
            yellowstone_geysers = new_gy
            for bz, victim in [(p1, p2), (p2, p1)]:
                if bz.char.get("bookzworm_books") and bz.hp > 0 and bz.bookzworm_book_cd <= 0:
                    if math.hypot(victim.x - bz.x, (victim.y - 60) - (bz.y - 60)) < int(85 * bz.draw_scale):
                        victim.take_proj_dmg(6)
                        victim.flash_timer = max(victim.flash_timer, 10)
                        bz.bookzworm_book_cd = 50
            for fb in fire_balls:
                fb.update()
                if fb.alive:
                    victim = p2 if fb.owner is p1 else p1
                    if fb.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; fb.alive = False
                        else:
                            victim.take_proj_dmg(FireBall.DMG)
                            victim.flash_timer = 8
                            if victim.fire_frames == 0: victim.fire_tick = 480
                            victim.fire_frames = max(victim.fire_frames, 480)
                            fb.alive = False
            fire_balls = [fb for fb in fire_balls if fb.alive]
            # Nian breath — wide cone, hits players and enemies
            for nb in nian_breaths:
                nb.update()
                for victim in living + enemies:
                    if nb.owner is not victim and id(victim) not in nb._hit and nb.in_cone(victim):
                        nb._hit.add(id(victim))
                        victim.take_proj_dmg(NianBreath.DMG)
                        if not victim.char.get("immune"):
                            victim.fire_frames = max(victim.fire_frames, NianBreath.FIRE_FRAMES)
                        victim.flash_timer = max(victim.flash_timer, 12)
            nian_breaths = [nb for nb in nian_breaths if nb.alive]
            for sb in sun_beams:
                sb.update()
                if sb.alive:
                    victim = p2 if sb.owner is p1 else p1
                    if sb.collides(victim):
                        if victim.char.get("tombstone_reflect"):
                            victim.flash_timer = 4
                            sb.owner.hp = max(0, sb.owner.hp - SunBeam.DMG)
                            sb.owner.flash_timer = max(sb.owner.flash_timer, 14)
                        elif victim.char.get("deflect_proj"):
                            sb.vx = -sb.vx; sb.owner = victim; continue
                        elif victim.bubble_shield:
                            victim.flash_timer = 6
                        else:
                            victim.take_proj_dmg(SunBeam.DMG)
                            victim.shock_frames = max(victim.shock_frames, 120)
                            if not victim.char.get("immune"):
                                if victim.fire_frames == 0: victim.fire_tick = 480
                                victim.fire_frames = max(victim.fire_frames, 300)
                        sb.alive = False
            sun_beams = [sb for sb in sun_beams if sb.alive]

            # Thunder bolts (Thunder God + Storm Caller)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_thunder:
                    shooter.pending_thunder = False
                    thunder_bolts.append(ThunderBolt(victim.x, shooter))
                if shooter.pending_storm:
                    shooter.pending_storm = False
                    thunder_bolts.append(ThunderBolt(random.randint(80, WIDTH - 80), shooter))
            for tb in thunder_bolts:
                tb.update()
                if tb.alive and not tb.hit:
                    victim = p2 if tb.owner is p1 else p1
                    if tb.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6
                        else:
                            victim.take_proj_dmg(ThunderBolt.DMG)
                            victim.flash_timer = 12
                            victim.shock_frames = max(victim.shock_frames, 180)
                        tb.hit = True
            thunder_bolts = [tb for tb in thunder_bolts if tb.alive]

            # Plant spikes (Druid)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_plant:
                    shooter.pending_plant = False
                    plant_spikes.append(PlantSpike(victim.x, shooter))
            for ps in plant_spikes:
                ps.update()
                if ps.alive:
                    victim = p2 if ps.owner is p1 else p1
                    if ps.collides(victim):
                        if victim.bubble_shield:
                            victim.flash_timer = 6; ps.alive = False
                        else:
                            victim.take_proj_dmg(PlantSpike.DMG)
                            victim.flash_timer = 12; ps.alive = False
            plant_spikes = [ps for ps in plant_spikes if ps.alive]

            # Hot potatoes
            for hp in hot_potatoes:
                hp.update()
                if hp.exploding and not hp.damaged:
                    hp.damaged = True
                    for f in (p1, p2):
                        if hp.collides(f):
                            f.hp = max(0, f.hp - hp.EXPLODE_DMG)
                            f.flash_timer = 20
            hot_potatoes = [hp for hp in hot_potatoes if hp.alive]

            # Crazy mode — rapid snake & bug spawning
            if crazy_timer > 0:
                crazy_timer -= 1
                if crazy_timer % 10 == 0:
                    crazy_snakes.append(JungleSnake())
                if crazy_timer % 7 == 0:
                    crazy_bugs.append(ComputerBug())
            for sn in crazy_snakes:
                sn.update(p1, p2)   # biting handled internally
            crazy_snakes = [sn for sn in crazy_snakes if sn.alive]
            for cb in crazy_bugs:
                target = min((p1, p2), key=lambda f: abs(f.x - cb.x))
                cb.update(target)   # biting handled internally
            crazy_bugs = [cb for cb in crazy_bugs if cb.alive]

            # Falling pots (imcooking)
            if cooking_timer > 0:
                cooking_timer -= 1
                if cooking_timer % 45 == 0:
                    falling_pots.append(FallingPot())
            for pot in falling_pots:
                pot.update()
                if pot.just_landed:
                    for f in (p1, p2):
                        if abs(f.x - pot.x) < pot.HIT_RANGE:
                            f.hp = max(0, f.hp - pot.DAMAGE)
                            f.flash_timer = 20
            falling_pots = [pt for pt in falling_pots if pt.alive]

            # Rolling coins (imselling)
            for coin in rolling_coins:
                hits = coin.update(p1, p2)
                for f in hits:
                    f.hp = max(0, f.hp - coin.DAMAGE)
                    f.flash_timer = 15
            rolling_coins = [c for c in rolling_coins if c.alive]

            # Falling merlins (merlin) — no damage
            for m in falling_merlins:
                m.update()
            falling_merlins = [m for m in falling_merlins if m.alive]

            # Powerup rain (kevin=great / kevin=bad)
            if rain_timer > 0:
                rain_timer -= 1
                if rain_cd > 0:
                    rain_cd -= 1
                else:
                    _spec = next((p for p in POWERUPS
                                  if p['name'] == ('Heal' if rain_type == 'heal'
                                                   else 'Poison')), None)
                    if _spec:
                        _rpu = Powerup.__new__(Powerup)
                        _rpu.spec = _spec; _rpu.name = _spec['name']
                        _rpu.color = _spec['color']
                        _rpu.x = float(random.randint(80, WIDTH - 80))
                        _rpu.y = float(GROUND_Y - 14)
                        _rpu.age = 0; _rpu.picked_up = False
                        rain_powerups.append(_rpu)
                    rain_cd = 20
            for rpu in rain_powerups:
                rpu.update()
                for f in (p1, p2):
                    if not rpu.picked_up and rpu.collides(f):
                        f.apply_powerup(rpu.spec)
                        rpu.picked_up = True
            rain_powerups = [rpu for rpu in rain_powerups if not rpu.picked_up]

            # Baseball mode (strike)
            if baseball_timer > 0:
                baseball_timer -= 1
                if baseball_cd > 0:
                    baseball_cd -= 1
                else:
                    baseballs.append(FlyingBaseball())
                    if random.random() < 0.35:
                        flying_bats.append(FlyingBat())
                    baseball_cd = 80
            for bb in baseballs:
                for f in bb.update(p1, p2):
                    f.hp = max(0, f.hp - bb.DAMAGE)
                    f.flash_timer = 12
            baseballs = [bb for bb in baseballs if bb.alive]
            for fb in flying_bats:
                for f in fb.update(p1, p2):
                    f.hp = max(0, f.hp - fb.DAMAGE)
                    f.flash_timer = 18
                    f.knockback = fb._dir * 10
            flying_bats = [fb for fb in flying_bats if fb.alive]

            # Laser eyes
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if (shooter.char.get("laser_eyes") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    side_ok  = ((shooter.facing ==  1 and victim.x > shooter.x) or
                                (shooter.facing == -1 and victim.x < shooter.x))
                    if side_ok and abs((victim.y - 60) - laser_y) < 35:
                        victim.take_proj_dmg(2)
                        victim.flash_timer = 4; shooter.laser_hit_cd = 15

            # Boomerang
            for thrower, victim in [(p1, p2), (p2, p1)]:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    if math.hypot(bx - victim.x, by - (victim.y - 60)) < 48:
                        if not victim.bubble_shield:
                            victim.take_proj_dmg(8)
                        victim.flash_timer = 6; thrower.boomerang_hit_cd = 30
                if thrower.bbboomerang_timer > 0 and thrower.bbboomerang_hit_cd == 0:
                    _bbe = (300 - thrower.bbboomerang_timer) // 60
                    _bbrx = 70 + _bbe * 10;  _bbry = 45 + _bbe * 7
                    _bbhr = 28 + _bbe * 4
                    for _bbi in range(5):
                        _bba = thrower.bbboomerang_angle + math.radians(_bbi * 72)
                        _bbx = thrower.x + math.cos(_bba) * _bbrx
                        _bby = (thrower.y - 60) + math.sin(_bba) * _bbry
                        if math.hypot(_bbx - victim.x, _bby - (victim.y - 60)) < _bbhr:
                            if not victim.bubble_shield:
                                victim.take_proj_dmg(6)
                            victim.flash_timer = 6
                            thrower.bbboomerang_hit_cd = 30
                            break

            # Springs
            for sp in springs:
                sp.update(); sp.trigger(p1); sp.trigger(p2)

            # Timer / game over
            timer -= 1
            if p1.hp <= 0 or p2.hp <= 0 or timer <= 0:
                game_over = True
                if   p1.hp > p2.hp: winner = "p1"
                elif p2.hp > p1.hp: winner = "p2"
                else:               winner = "draw"

            # Send authoritative state to client
            net.send({
                "type":   "STATE",
                "p1":     _f2s(p1),
                "p2":     _f2s(p2),
                "balls":        [{"x": b.x,  "y": b.y,  "vx": b.vx} for b in balls],
                "orbs":         [{"x": o.x,  "y": o.y,  "exp": o.exploding, "et": o.explode_timer} for o in orbs],
                "bounce_balls": [{"x": bb.x, "y": bb.y} for bb in bounce_balls],
                "hooks":        [{"x": h.x, "y": h.y, "ox": h.ox, "oy": h.oy, "vx": h.vx, "vy": h.vy, "t": h.t} for h in hooks],
                "pumpkins":     [{"x": pk.x, "y": pk.y, "exp": pk.exploding, "et": pk.explode_timer if pk.exploding else 0} for pk in pumpkins],
                "whips":        [{"x": w.x,  "y": w.y,  "facing": w.facing, "frame": w.frame} for w in whips],
                "charged_orbs": [{"x": co.x, "y": co.y, "r": co.r} for co in charged_orbs],
                "bubble_shots": [{"x": bs.x, "y": bs.y} for bs in bubble_shots],
                "poison_orbs":  [{"x": po.x, "y": po.y, "pulse": po._pulse} for po in poison_orbs],
                "scrolls":      [{"x": sc.x, "y": sc.y, "half": sc.half} for sc in scrolls],
                "venoms":       [{"x": vb.x, "y": vb.y, "facing": vb.facing} for vb in venoms],
                "notes":        [{"x": nt.x, "y": nt.y, "t": nt._t} for nt in notes],
                "kitsune_shots":[{"x": ks.x, "y": ks.y, "spin": ks._spin} for ks in kitsune_shots],
                "water_balls":  [{"x": wb.x, "y": wb.y} for wb in water_balls],
                "bee_shots":    [{"x": b.x,  "y": b.y} for b in bee_shots],
                "snipe_shots":  [{"x": s.x,  "y": s.y,  "vx": s.vx} for s in snipe_shots],
                "fire_balls":   [{"x": fb.x, "y": fb.y, "t": fb._t} for fb in fire_balls],
                "thunder_bolts":[{"x": tb.x, "y": tb.y, "t": tb._t} for tb in thunder_bolts],
                "plant_spikes": [{"x": ps.x, "y": ps.y} for ps in plant_spikes],
                "winner": winner,
            })

        elif not is_host:
            # Send our (client's) inputs as action booleans
            if not game_over:
                net.send({"type": "INPUT",
                          **_local_actions(keys, P1_CTRL)})

            # Apply received state
            for m in msgs:
                if m.get("type") == "STATE":
                    _s2f(p1, m["p1"]); _s2f(p2, m["p2"])
                    winner = m.get("winner")
                    if winner:
                        game_over = True
                    # Reconstruct projectile visuals from state
                    balls = []
                    for bd in m.get("balls", []):
                        b = Projectile.__new__(Projectile)
                        b.x = bd["x"]; b.y = bd["y"]
                        b.vx = bd["vx"]; b.alive = True; b.owner = None
                        balls.append(b)
                    orbs = []
                    for od in m.get("orbs", []):
                        o = Orb.__new__(Orb)
                        o.x = od["x"]; o.y = od["y"]; o.exploding = od["exp"]
                        o.explode_timer = od.get("et", 0); o.alive = True
                        orbs.append(o)
                    bounce_balls = []
                    for bbd in m.get("bounce_balls", []):
                        bb = BouncingBall.__new__(BouncingBall)
                        bb.x = bbd["x"]; bb.y = bbd["y"]; bb.alive = True
                        bounce_balls.append(bb)
                    hooks = []
                    for hd in m.get("hooks", []):
                        h = SnakeHook.__new__(SnakeHook)
                        h.x = hd["x"]; h.y = hd["y"]; h.alive = True
                        h.ox = hd.get("ox", hd["x"]); h.oy = hd.get("oy", hd["y"])
                        h.vx = hd.get("vx", 0.0); h.vy = hd.get("vy", 0.0)
                        h.t  = hd.get("t", 0)
                        hooks.append(h)
                    pumpkins = []
                    for pkd in m.get("pumpkins", []):
                        pk = Pumpkin.__new__(Pumpkin)
                        pk.x = pkd["x"]; pk.y = pkd["y"]; pk.exploding = pkd["exp"]
                        pk.explode_timer = pkd.get("et", 0); pk.alive = True
                        pumpkins.append(pk)
                    whips = []
                    for wd in m.get("whips", []):
                        w = Whip.__new__(Whip)
                        w.x = wd["x"]; w.y = wd["y"]; w.facing = wd["facing"]
                        w.frame = wd["frame"]; w.alive = True
                        whips.append(w)
                    charged_orbs = []
                    for cod in m.get("charged_orbs", []):
                        co = ChargedOrb.__new__(ChargedOrb)
                        co.x = cod["x"]; co.y = cod["y"]; co.r = cod["r"]; co.alive = True
                        charged_orbs.append(co)
                    bubble_shots = []
                    for bsd in m.get("bubble_shots", []):
                        bs = BubbleShot.__new__(BubbleShot)
                        bs.x = bsd["x"]; bs.y = bsd["y"]; bs.alive = True
                        bubble_shots.append(bs)
                    poison_orbs = []
                    for pod in m.get("poison_orbs", []):
                        po = PoisonOrb.__new__(PoisonOrb)
                        po.x = pod["x"]; po.y = pod["y"]; po._pulse = pod.get("pulse", 0); po.alive = True
                        poison_orbs.append(po)
                    scrolls = []
                    for scd in m.get("scrolls", []):
                        sc = Scroll.__new__(Scroll)
                        sc.x = scd["x"]; sc.y = scd["y"]; sc.half = scd["half"]; sc.alive = True
                        scrolls.append(sc)
                    venoms = []
                    for vbd in m.get("venoms", []):
                        vb = VenomBean.__new__(VenomBean)
                        vb.x = vbd["x"]; vb.y = vbd["y"]; vb.facing = vbd["facing"]; vb.alive = True
                        venoms.append(vb)
                    notes = []
                    for ntd in m.get("notes", []):
                        nt = MusicNote.__new__(MusicNote)
                        nt.x = ntd["x"]; nt.y = ntd["y"]; nt._t = ntd.get("t", 0); nt.alive = True
                        notes.append(nt)
                    kitsune_shots = []
                    for ksd in m.get("kitsune_shots", []):
                        ks = KitsuneShot.__new__(KitsuneShot)
                        ks.x = ksd["x"]; ks.y = ksd["y"]; ks._spin = ksd.get("spin", 0.0); ks.alive = True
                        kitsune_shots.append(ks)
                    water_balls = []
                    for wbd in m.get("water_balls", []):
                        wb = WaterBall.__new__(WaterBall)
                        wb.x = wbd["x"]; wb.y = wbd["y"]; wb.alive = True
                        water_balls.append(wb)
                    bee_shots = []
                    for bbd in m.get("bee_shots", []):
                        bsh = BeeShot.__new__(BeeShot)
                        bsh.x = bbd["x"]; bsh.y = bbd["y"]; bsh.alive = True
                        bee_shots.append(bsh)
                    snipe_shots = []
                    for ssd in m.get("snipe_shots", []):
                        s = SnipeShot.__new__(SnipeShot)
                        s.x = ssd["x"]; s.y = ssd["y"]; s.vx = ssd.get("vx", 0.0); s.alive = True
                        snipe_shots.append(s)
                    fire_balls = []
                    for fbd in m.get("fire_balls", []):
                        fb2 = FireBall.__new__(FireBall)
                        fb2.x = fbd["x"]; fb2.y = fbd["y"]; fb2._t = fbd.get("t", 0); fb2.alive = True
                        fire_balls.append(fb2)
                    thunder_bolts = []
                    for tbd in m.get("thunder_bolts", []):
                        tb2 = ThunderBolt.__new__(ThunderBolt)
                        tb2.x = tbd["x"]; tb2.y = tbd["y"]; tb2._t = tbd.get("t", 0); tb2.alive = True
                        thunder_bolts.append(tb2)
                    plant_spikes = []
                    for psd in m.get("plant_spikes", []):
                        ps2 = PlantSpike.__new__(PlantSpike)
                        ps2.x = psd["x"]; ps2.y = psd["y"]; ps2.alive = True
                        plant_spikes.append(ps2)

            # Springs (visual only on client — host is authoritative)
            for sp in springs:
                sp.update()

        # ── Draw ────────────────────────────────────────────────────────────
        draw_bg(screen, stage_idx)
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for plat in platforms: plat.draw(screen, stage_idx)
        for sp   in springs:   sp.draw(screen)
        for b    in balls:          b.draw(screen)
        for ao   in arcane_orbs:    ao.draw(screen)
        for o    in orbs:           o.draw(screen)
        for bb   in bounce_balls:   bb.draw(screen)
        for h    in hooks:          h.draw(screen)
        for pk   in pumpkins:       pk.draw(screen)
        for js   in jack_seeds:     js.draw(screen)
        for fp   in fruit_projs:    fp.draw(screen)
        for cp   in coal_projs:     cp.draw(screen)
        for w    in whips:          w.draw(screen)
        for co   in charged_orbs:   co.draw(screen)
        for bs   in bubble_shots:   bs.draw(screen)
        for po   in poison_orbs:    po.draw(screen)
        for sc   in scrolls:        sc.draw(screen)
        for vb   in venoms:         vb.draw(screen)
        for nt   in notes:          nt.draw(screen)
        for ks   in kitsune_shots:  ks.draw(screen)
        for wb   in water_balls:    wb.draw(screen)
        for bsh  in bee_shots:      bsh.draw(screen)
        for s    in snipe_shots:    s.draw(screen)
        for sb   in sun_beams:      sb.draw(screen)
        for dove in liberty_doves:  dove.draw(screen)
        for lb in liberty_bombs:
            bx, by = int(lb['x']), int(lb['y'])
            pygame.draw.circle(screen, (255, 255, 255), (bx, by), 7)
            pygame.draw.circle(screen, (200, 220, 200), (bx, by), 4)
        for gy in yellowstone_geysers:
            gx, age = int(gy['x']), gy['age']
            if age <= 22:
                h = min(age * 6, 130)
                pygame.draw.rect(screen, (160, 220, 255), (gx - 7, GROUND_Y - h, 14, h))
                pygame.draw.circle(screen, (220, 240, 255), (gx, GROUND_Y - h), 10)
            elif age <= 40:
                r = int((age - 22) * 5) + 8
                pygame.draw.circle(screen, (255, 255, 255), (gx, GROUND_Y - 110), r)
                pygame.draw.circle(screen, (180, 230, 255), (gx, GROUND_Y - 110), r + 4, 3)
        for fb   in fire_balls:     fb.draw(screen)
        for nb   in nian_breaths:   nb.draw(screen)
        for tb   in thunder_bolts:  tb.draw(screen)
        for ps   in plant_spikes:   ps.draw(screen)

        # Laser beams
        for f in (p1, p2):
            if f.char.get("laser_eyes") and f.laser_active > 0:
                ex, ey  = int(f.x), int(f.y - 100)
                end_x   = WIDTH if f.facing == 1 else 0
                x = ex
                while (f.facing == 1 and x < end_x) or (f.facing == -1 and x > end_x):
                    de = x + f.facing * 18
                    de = min(de, end_x) if f.facing == 1 else max(de, end_x)
                    pygame.draw.line(screen, (255, 40, 0),   (x, ey), (de, ey), 3)
                    pygame.draw.line(screen, (255, 160, 80), (x, ey), (de, ey), 1)
                    x = de + f.facing * 6

        for hp  in hot_potatoes:   hp.draw(screen)
        for sn  in crazy_snakes:   sn.draw(screen)
        for cb  in crazy_bugs:     cb.draw(screen)
        for pot in falling_pots:   pot.draw(screen)
        for c   in rolling_coins:  c.draw(screen)
        for m   in falling_merlins: m.draw(screen)
        for rpu in rain_powerups:  rpu.draw(screen)
        for bb  in baseballs:      bb.draw(screen)
        for fb  in flying_bats:    fb.draw(screen)

        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen)

        # Baseball caps on both fighters during strike mode
        if baseball_timer > 0:
            _CAP_BLUE  = (20, 60, 180)
            _CAP_DARK  = (10, 35, 120)
            for f in (p1, p2):
                hx = int(f.x)
                hy = int(f.y) - 118   # head centre y  (HEAD_R=18, NECK=5, BODY=50, LEG=45)
                hd = 18
                # Crown — dome covering top of head
                pygame.draw.ellipse(screen, _CAP_BLUE,
                                    (hx - hd, hy - hd - 8, hd * 2, hd + 10))
                # Brim — flat rectangle extending in facing direction
                if f.facing == 1:
                    brim_rect = (hx - hd + 4, hy - 2, hd * 2 + 14, 7)
                else:
                    brim_rect = (hx - hd - 14, hy - 2, hd * 2 + 14, 7)
                pygame.draw.rect(screen, _CAP_BLUE, brim_rect, border_radius=3)
                # Cap button on top
                pygame.draw.circle(screen, _CAP_DARK, (hx, hy - hd - 6), 3)
                # Outline
                pygame.draw.ellipse(screen, _CAP_DARK,
                                    (hx - hd, hy - hd - 8, hd * 2, hd + 10), 2)

        # Bubble shields
        for f in (p1, p2):
            if f.bubble_shield:
                bsurf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(bsurf, (100, 200, 255, 70),  (50, 50), 48)
                pygame.draw.circle(bsurf, (100, 200, 255, 160), (50, 50), 48, 3)
                screen.blit(bsurf, (int(f.x) - 50, int(f.y) - 90))

        # Melee hit detection (authoritative — host only)
        if is_host and not game_over:
            for attacker, hit_pos, other in [(p1, p1_hit, p2), (p2, p2_hit, p1)]:
                if attacker.attacking and not attacker.attack_hit and hit_pos:
                    attacker.check_hit(hit_pos, other)

        # HUD — health bars + names + timer
        p1_label = my_name  if is_host else opp_name
        p2_label = opp_name if is_host else my_name
        draw_health_bars_labeled(screen, p1, p2, f"{p2_label} — {p2.char['name']}")
        for f, lbl in [(p1, p1_label), (p2, p2_label)]:
            ns = font_tiny.render(lbl, True, f.char["color"])
            screen.blit(ns, (int(f.x) - ns.get_width()//2, int(f.y) - 148))

        if not game_over:
            secs = max(0, timer // FPS)
            tc = WHITE if secs > 10 else RED
            ts = font_medium.render(str(secs), True, tc)
            screen.blit(ts, (WIDTH//2 - ts.get_width()//2, 25))

        # Chat overlay
        recent = net.chat_log[-5:]
        for i, (sender, text) in enumerate(recent):
            col  = CYAN if sender == "You" else YELLOW
            line = font_tiny.render(f"{sender}: {text}", True, col)
            screen.blit(line, (10, HEIGHT - 110 + i * 18))
        if chat_active:
            pygame.draw.rect(screen, (30, 30, 50), (0, HEIGHT - 36, WIDTH, 36))
            cur = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            ci  = font_small.render("Say: " + chat_input + cur, True, WHITE)
            screen.blit(ci, (10, HEIGHT - 30))
        else:
            ht = font_tiny.render("T = chat", True, (70, 70, 70))
            screen.blit(ht, (10, HEIGHT - 16))

        # Win / disconnect screen
        if game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            if winner == "disconnect":
                wt = font_large.render("DISCONNECTED", True, RED)
            elif winner == "draw":
                wt = font_large.render("DRAW!", True, YELLOW)
            elif (winner == "p1") == is_host:
                wt = font_large.render("YOU WIN!", True, GREEN)
            else:
                wt = font_large.render("YOU LOSE!", True, RED)
            screen.blit(wt, (WIDTH//2 - wt.get_width()//2, HEIGHT//3))
            ht = font_small.render("Any key — back to menu", True, WHITE)
            screen.blit(ht, (WIDTH//2 - ht.get_width()//2, HEIGHT//2 + 40))

        pygame.display.flip()

    constants.GRAVITY    = _orig_gravity
    constants.STAGE_VOID = False; constants.STAGE_CEILING = False

    # Report win to server (relay fights) and save locally
    if winner and winner not in ("disconnect", "draw"):
        _i_won = (winner == "p1") == is_host
        if userdata is not None:
            if _i_won:
                userdata["online_wins"]   = userdata.get("online_wins",   0) + 1
            else:
                userdata["online_losses"] = userdata.get("online_losses", 0) + 1
            _net.save_userdata(userdata)
        # Report to relay server for global leaderboard
        if isinstance(net, _RelayNet):
            try:
                net._lobby.report_result(_i_won)
            except Exception:
                pass

    net.close()
    return 'select'


# ---------------------------------------------------------------------------
# Relay fight (matchmaking via fight_server.py)
# ---------------------------------------------------------------------------

class _RelayNet:
    """
    Thin adapter so run_online_fight() can drive a LobbyClient with the
    same send / recv_all / send_chat / chat_log / close interface it uses
    for GameServer / GameClient.
    """
    def __init__(self, lobby):
        self._lobby   = lobby
        self.chat_log = lobby.match_chat_log   # shared reference
        self.opp_name = (lobby.match_info or {}).get("opp_name", "Opponent")

    @property
    def connected(self):
        return self._lobby.connected

    def send(self, obj):
        self._lobby.relay(obj)

    def recv_all(self):
        return self._lobby.poll()   # already returns unwrapped relay payloads

    def send_chat(self, text):
        self._lobby.match_chat(text)

    def close(self):
        self._lobby.close()


def run_relay_fight(lobby, is_host, p1_char_idx, p2_char_idx,
                    stage_idx, my_name, opp_name, userdata=None):
    """Wrapper: create a _RelayNet adapter and delegate to run_online_fight."""
    net = _RelayNet(lobby)
    net.opp_name = opp_name
    return run_online_fight(net, is_host, p1_char_idx, p2_char_idx,
                            stage_idx, my_name, opp_name, userdata=userdata)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _show_intro():
    """One-time intro screen shown at game start. Skip with any key or tap."""
    lines = [
        ("STICKMAN FIGHTER",        font_large,  YELLOW,         -120),
        ("In a world made of lines and circles,",   font_small, (200, 200, 220),  -40),
        ("warriors rise from every corner of the",  font_small, (200, 200, 220),  -20),
        ("earth to prove who is the greatest",      font_small, (200, 200, 220),    0),
        ("fighter of them all.",                    font_small, (200, 200, 220),   20),
        ("Punch, kick, and outsmart your rivals.", font_small, (180, 220, 180),    60),
        ("Unlock new challengers.  Master every",  font_small, (180, 220, 180),    80),
        ("stage.  Become a legend.",               font_small, (180, 220, 180),   100),
        ("press any key to begin",                 font_tiny,  (120, 120, 120),   160),
    ]
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                return
        elapsed = pygame.time.get_ticks() - start
        if elapsed > 12000:
            return
        # fade in over 800 ms
        alpha = min(255, int(elapsed / 800 * 255))
        screen.fill((10, 10, 18))
        cy = HEIGHT // 2
        for text, fnt, col, dy in lines:
            surf = fnt.render(text, True, col)
            surf.set_alpha(alpha)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, cy + dy))
        pygame.display.flip()


def main():
    unlocked, stats = load_save()
    hints = {name: ("???" if (len(cond) > 4 and cond[4]) else cond[3])
             for name, cond in UNLOCK_CONDITIONS.items()}

    while True:
        mode = mode_select()
        if _type42_typed[0]:
            stats["type42_done"] = True
            _type42_typed[0] = False
            new_unlocks = check_and_unlock(unlocked, stats)
            if new_unlocks:
                _save_data(unlocked, stats)
                _show_unlocks(new_unlocks)

        # --- Seasonal shop path ---
        if mode == 'seasonal_shop':
            seasonal_shop(screen, clock, stats, unlocked)
            _save_data(unlocked, stats)
            continue

        # --- Secret menu path ---
        if mode == 'secret_menu':
            newly = secret_menu(unlocked, stats)
            if newly:
                for name in newly:
                    cond = UNLOCK_CONDITIONS.get(name)
                    if cond and len(cond) > 4 and cond[4]:
                        stats["secret_chars_unlocked"] = stats.get("secret_chars_unlocked", 0) + 1
                _show_unlocks(newly)
            _save_data(unlocked, stats)   # always save (coins may have changed)
            continue

        # --- Online path ---
        if mode == 'online':
            userdata = _net.load_userdata()
            result   = online_menu(userdata)
            if result is None:
                continue
            role, info = result
            if role == 'quickmatch':
                lobby, p1_char, p2_char, s_idx, is_host, opp_name = info
                run_relay_fight(lobby, is_host, p1_char, p2_char,
                                s_idx, userdata['username'], opp_name,
                                userdata=userdata)
            else:
                net, my_char, opp_char, s_idx = info
                if role == 'host':
                    p1_char, p2_char = my_char, opp_char
                else:
                    p1_char, p2_char = opp_char, my_char
                run_online_fight(net, role == 'host', p1_char, p2_char,
                                 s_idx, userdata['username'], net.opp_name,
                                 userdata=userdata)
            continue

        # --- Survival path ---
        if mode in ('survival_1p', 'survival_2p'):
            two_player = (mode == 'survival_2p')
            p1_idx, p2_idx = character_select(vs_ai=not two_player,
                                              unlocked=unlocked, unlock_hints=hints,
                                              unlock_progress=_unlock_progress(stats))
            if p1_idx is None:
                continue
            s_idx = stage_select()
            while True:
                result = run_survival(p1_idx, p2_idx if two_player else None,
                                      two_player=two_player, stage_idx=s_idx)
                action, kills = result if isinstance(result, tuple) else (result, 0)
                stats["survival_kills"] += kills
                stats["survival_runs"] = stats.get("survival_runs", 0) + 1
                stats["survival_best_kills"] = max(stats.get("survival_best_kills", 0), kills)
                # Track daily date and 3:33pm for survival too
                _today = datetime.date.today().isoformat()
                _dates = stats.get("daily_play_dates", [])
                if _today not in _dates:
                    _dates.append(_today)
                    stats["daily_play_dates"] = _dates
                _now = datetime.datetime.now()
                if _now.hour == 15 and _now.minute == 33:
                    stats["played_at_333pm"] = True
                if _konami_flag[0]:
                    stats["konami_unlocked"] = True
                    _konami_flag[0] = False
                if _map_man_flag[0]:
                    stats["map_man_unlocked"] = True
                    _map_man_flag[0] = False
                new_unlocks = check_and_unlock(unlocked, stats)
                if new_unlocks:
                    _save_data(unlocked, stats)
                    _show_unlocks(new_unlocks)
                if action == 'rematch':
                    continue
                break
            continue

        # --- The Casino (Emerald Echoes event) path ---
        if mode == 'the_casino':
            # Mode intro screen
            _cas_lines = [
                ("THE CASINO",              font_large,  (255, 200, 0),    -130),
                ("The house always wins — or does it?",
                                            font_small,  (230, 210, 180),   -60),
                ("Only the luckiest and most cunning",
                                            font_small,  (230, 210, 180),   -40),
                ("fighters are welcome at this table.",
                                            font_small,  (230, 210, 180),   -20),
                ("Pick from 7 high-stakes brawlers and",
                                            font_small,  (255, 220, 120),    20),
                ("gamble everything on every hit.",
                                            font_small,  (255, 220, 120),    40),
                ("Win 10 matches and a random casino",
                                            font_small,  (255, 220, 120),    80),
                ("fighter joins your full roster.",
                                            font_small,  (255, 220, 120),   100),
                ("Available during Emerald Echoes only.",
                                            font_small,  (160, 220, 160),   140),
                ("press any key to continue",font_tiny,  (110, 110, 110),   190),
            ]
            _cas_start = pygame.time.get_ticks()
            _cas_done  = False
            while not _cas_done:
                clock.tick(FPS)
                for _cev in pygame.event.get():
                    if _cev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if _cev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                        _cas_done = True
                if pygame.time.get_ticks() - _cas_start > 10000:
                    _cas_done = True
                _ca = min(255, int((pygame.time.get_ticks() - _cas_start) / 600 * 255))
                screen.fill((15, 10, 5))
                _ccy = HEIGHT // 2
                for _ct, _cf, _cc, _cdy in _cas_lines:
                    _cs = _cf.render(_ct, True, _cc)
                    _cs.set_alpha(_ca)
                    screen.blit(_cs, (WIDTH // 2 - _cs.get_width() // 2, _ccy + _cdy))
                pygame.display.flip()

            _CASINO_FILTER = frozenset({
                "Wildcard", "Tycoon", "Gambler", "Fortune",
                "High Roller", "Lucky", "Clover",
            })
            p1_idx, p2_idx = character_select(
                vs_ai=False, unlocked=_CASINO_FILTER,
                char_filter=_CASINO_FILTER,
                select_title="THE CASINO",
            )
            if p1_idx is None:
                continue
            _cas_stage_idx = next((i for i, st in enumerate(STAGES) if st["name"] == "The Casino"), 0)
            while True:
                result = run_fight(p1_idx, p2_idx, vs_ai=False, stage_idx=_cas_stage_idx)
                action, info = result if isinstance(result, tuple) else (result, (False,)*5 + (None, None, 0, 0))
                p1_won = info[0] if isinstance(info, tuple) else False
                if p1_won:
                    stats["casino_wins"] = stats.get("casino_wins", 0) + 1
                    if stats["casino_wins"] % 10 == 0:
                        _casino_weights = [
                            ("Clover",        8),
                            ("Tycoon",      250),
                            ("Gambler",     200),
                            ("Fortune",     150),
                            ("High Roller",  80),
                            ("Lucky",        40),
                            ("Wildcard",     20),
                            ("Gilded Clover", 1),
                        ]
                        _casino_pool_w = [n for n, w in _casino_weights for _ in range(w)]
                        _cas_locked = [n for n in {n for n, _ in _casino_weights} if n not in unlocked]
                        _cas_locked_w = [n for n in _casino_pool_w if n in set(_cas_locked)]
                        _cas_reward = random.choice(_cas_locked_w) if _cas_locked_w else random.choice(_casino_pool_w)
                        if _cas_reward not in unlocked:
                            unlocked.add(_cas_reward)
                            _save_data(unlocked, stats)
                            _show_unlocks([_cas_reward])
                        else:
                            _save_data(unlocked, stats)
                if _konami_flag[0]:
                    stats["konami_unlocked"] = True
                    _konami_flag[0] = False
                if action == 'rematch':
                    continue
                break
            continue

        # --- Floor is Lava (Summer Solstice event) ---
        if mode == 'floor_is_lava':
            _fil_lines = [
                ("FLOOR IS LAVA",           font_large,  (255, 120, 20),  -130),
                ("The ground itself is your enemy here.",
                                            font_small,  (255, 200, 150),  -60),
                ("Choose from 8 fire-type fighters and",
                                            font_small,  (255, 200, 150),  -40),
                ("battle over a pool of molten rock.",
                                            font_small,  (255, 200, 150),  -20),
                ("The lava floor burns anyone who",
                                            font_small,  (255, 220, 100),   20),
                ("touches it — even you. Stay airborne.",
                                            font_small,  (255, 220, 100),   40),
                ("Win 10 matches and a rare fighter",
                                            font_small,  (255, 220, 100),   80),
                ("may join your roster.",
                                            font_small,  (255, 220, 100),  100),
                ("Available during Summer Solstice only.",
                                            font_small,  (160, 220, 160),  140),
                ("press any key to continue",
                                            font_tiny,  (110, 110, 110),  190),
            ]
            _fil_start = pygame.time.get_ticks()
            _fil_done  = False
            while not _fil_done:
                clock.tick(FPS)
                for _fev in pygame.event.get():
                    if _fev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if _fev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                        _fil_done = True
                if pygame.time.get_ticks() - _fil_start > 10000:
                    _fil_done = True
                _fa = min(255, int((pygame.time.get_ticks() - _fil_start) / 600 * 255))
                screen.fill((20, 8, 5))
                _fcy = HEIGHT // 2
                for _ft, _ff, _fc, _fdy in _fil_lines:
                    _fs = _ff.render(_ft, True, _fc)
                    _fs.set_alpha(_fa)
                    screen.blit(_fs, (WIDTH // 2 - _fs.get_width() // 2, _fcy + _fdy))
                pygame.display.flip()

            _FIL_FILTER = frozenset({
                "Arsonist", "Lava Man", "Pyro", "Blazer",
                "Inferno",  "Magma",    "Trailblazer", "Solara",
            })
            p1_idx, p2_idx = character_select(
                vs_ai=False, unlocked=_FIL_FILTER,
                char_filter=_FIL_FILTER,
                select_title="FLOOR IS LAVA",
            )
            if p1_idx is None:
                continue
            _fil_stage_idx = next((i for i, st in enumerate(STAGES) if st["name"] == "Floor is Lava"), 0)
            while True:
                result = run_fight(p1_idx, p2_idx, vs_ai=False, stage_idx=_fil_stage_idx)
                action, info = result if isinstance(result, tuple) else (result, (False,)*5 + (None, None, 0, 0))
                p1_won = info[0] if isinstance(info, tuple) else False
                if p1_won:
                    stats["floor_lava_wins"] = stats.get("floor_lava_wins", 0) + 1
                    if stats["floor_lava_wins"] % 10 == 0:
                        _lava_weights = [
                            ("Arsonist",         220),
                            ("Inferno",          200),
                            ("Blazer",           180),
                            ("Pyro",             160),
                            ("Magma",            140),
                            ("Lava Man",         120),
                            ("Trailblazer",       80),
                            ("Solara",            40),
                            ("Performer Solara",   1),
                        ]
                        _lava_pool = [n for n, w in _lava_weights for _ in range(w)]
                        _lava_locked = [n for n in {n for n, _ in _lava_weights} if n not in unlocked]
                        _lava_locked_w = [n for n in _lava_pool if n in set(_lava_locked)]
                        _lava_reward = random.choice(_lava_locked_w) if _lava_locked_w else random.choice(_lava_pool)
                        if _lava_reward not in unlocked:
                            unlocked.add(_lava_reward)
                            _save_data(unlocked, stats)
                            _show_unlocks([_lava_reward])
                        else:
                            _save_data(unlocked, stats)
                if _konami_flag[0]:
                    stats["konami_unlocked"] = True
                    _konami_flag[0] = False
                if action == 'rematch':
                    continue
                break
            continue

        # --- Chaos Aura (Aura of Menorah event) ---
        if mode == 'chaos_aura':
            _cau_lines = [
                ("CHAOS AURA",              font_large,  (255, 80, 200),   -130),
                ("Order has no place here.",
                                            font_small,  (255, 200, 255),   -60),
                ("Choose from 11 chaotic fighters and",
                                            font_small,  (255, 200, 255),   -40),
                ("clash on a stage of pure mayhem.",
                                            font_small,  (255, 200, 255),   -20),
                ("Springs, conveyors, and portals",
                                            font_small,  (255, 220, 100),    20),
                ("fill the arena — nothing is safe.",
                                            font_small,  (255, 220, 100),    40),
                ("Win 10 matches and a rare fighter",
                                            font_small,  (255, 220, 100),    80),
                ("may join your roster.",
                                            font_small,  (255, 220, 100),   100),
                ("Available during Aura of Menorah only.",
                                            font_small,  (160, 200, 255),   140),
                ("press any key to continue",font_tiny,  (110, 110, 110),   190),
            ]
            _cau_start = pygame.time.get_ticks()
            _cau_done  = False
            while not _cau_done:
                clock.tick(FPS)
                for _caev in pygame.event.get():
                    if _caev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if _caev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                        _cau_done = True
                if pygame.time.get_ticks() - _cau_start > 10000:
                    _cau_done = True
                _caa = min(255, int((pygame.time.get_ticks() - _cau_start) / 600 * 255))
                screen.fill((18, 5, 28))
                _caucy = HEIGHT // 2
                for _caut, _cauf, _cauc, _caudy in _cau_lines:
                    _caus = _cauf.render(_caut, True, _cauc)
                    _caus.set_alpha(_caa)
                    screen.blit(_caus, (WIDTH // 2 - _caus.get_width() // 2, _caucy + _caudy))
                pygame.display.flip()

            _CAU_FILTER = frozenset({
                "Elemental", "Disorientated", "Joker", "Swapper",
                "Rainbow Man", "Soul Master", "Crazy", "Chaos", "Nun-Gimel-Hei-Shin",
            })
            p1_idx, p2_idx = character_select(
                vs_ai=False, unlocked=_CAU_FILTER,
                char_filter=_CAU_FILTER,
                select_title="CHAOS AURA",
            )
            if p1_idx is None:
                continue
            _cau_stage_idx = next((i for i, st in enumerate(STAGES) if st["name"] == "Chaos Arena"), 0)
            while True:
                result = run_fight(p1_idx, p2_idx, vs_ai=False, stage_idx=_cau_stage_idx)
                action, info = result if isinstance(result, tuple) else (result, (False,)*5 + (None, None, 0, 0))
                p1_won = info[0] if isinstance(info, tuple) else False
                if p1_won:
                    stats["chaos_aura_wins"] = stats.get("chaos_aura_wins", 0) + 1
                    if stats["chaos_aura_wins"] % 10 == 0:
                        _cau_weights = [
                            ("Crazy",                   220),
                            ("Joker",                   200),
                            ("Swapper",                 180),
                            ("Chaos",                   160),
                            ("Disorientated",           140),
                            ("Elemental",               120),
                            ("Soul Master",             100),
                            ("Rainbow Man",              80),
                            ("Nun-Gimel-Hei-Shin",       12),
                            ("Chaos Nun-Gimel-Hei-Shin",  1),
                        ]
                        _cau_pool = [n for n, w in _cau_weights for _ in range(w)]
                        _cau_locked = [n for n in {n for n, _ in _cau_weights} if n not in unlocked]
                        _cau_locked_w = [n for n in _cau_pool if n in set(_cau_locked)]
                        _cau_reward = random.choice(_cau_locked_w) if _cau_locked_w else random.choice(_cau_pool)
                        if _cau_reward not in unlocked:
                            unlocked.add(_cau_reward)
                            _save_data(unlocked, stats)
                            _show_unlocks([_cau_reward])
                        else:
                            _save_data(unlocked, stats)
                if _konami_flag[0]:
                    stats["konami_unlocked"] = True
                    _konami_flag[0] = False
                if action == 'rematch':
                    continue
                break
            continue

        # --- Giants Among Us (seasonal event) path ---
        if mode == 'giants_among_us':
            # Mode intro screen
            _gau_lines = [
                ("GIANTS AMONG US",         font_large,  (100, 220, 100),  -130),
                ("Only the mightiest beings are allowed here.",
                                            font_small,  (200, 230, 200),   -60),
                ("Choose from 12 colossal fighters and battle",
                                            font_small,  (200, 230, 200),   -40),
                ("your opponent in an all-out clash of giants.",
                                            font_small,  (200, 230, 200),   -20),
                ("Win 10 matches and a powerful new",
                                            font_small,  (255, 220, 100),    20),
                ("fighter will be added to your roster —",
                                            font_small,  (255, 220, 100),    40),
                ("rarer ones are much harder to get.",
                                            font_small,  (255, 220, 100),    60),
                ("Available during Giants Among Us only.",
                                            font_small,  (160, 220, 160),   140),
                ("press any key to continue",
                                            font_tiny,  (110, 110, 110),   170),
            ]
            _gau_start = pygame.time.get_ticks()
            _gau_done  = False
            while not _gau_done:
                clock.tick(FPS)
                for _gev in pygame.event.get():
                    if _gev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if _gev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                        _gau_done = True
                if pygame.time.get_ticks() - _gau_start > 10000:
                    _gau_done = True
                _ga = min(255, int((pygame.time.get_ticks() - _gau_start) / 600 * 255))
                screen.fill((8, 20, 8))
                _cy = HEIGHT // 2
                for _gt, _gf, _gc, _gdy in _gau_lines:
                    _gs = _gf.render(_gt, True, _gc)
                    _gs.set_alpha(_ga)
                    screen.blit(_gs, (WIDTH // 2 - _gs.get_width() // 2, _cy + _gdy))
                pygame.display.flip()

            _GIANTS_FILTER = frozenset({
                "Giant", "Minotaur", "Colossus", "Eartha",
                "Morph", "Titan Smash", "Abomination", "Emperor",
            })
            p1_idx, p2_idx = character_select(
                vs_ai=False, unlocked=_GIANTS_FILTER,
                char_filter=_GIANTS_FILTER,
                select_title="GIANTS AMONG US",
            )
            if p1_idx is None:
                continue
            _gau_stage_idx = next((i for i, st in enumerate(STAGES) if st["name"] == "Giants Among Us"), 0)
            while True:
                result = run_fight(p1_idx, p2_idx, vs_ai=False, stage_idx=_gau_stage_idx, giant_mode=True)
                action, info = result if isinstance(result, tuple) else (result, (False,)*5 + (None, None, 0, 0))
                p1_won = info[0] if isinstance(info, tuple) else False
                if p1_won:
                    stats["giants_wins"] = stats.get("giants_wins", 0) + 1
                    if stats["giants_wins"] % 10 == 0:
                        # Weighted drop table — rarer characters have lower odds
                        _giant_weights = [
                            ("Giant",          220),
                            ("Morph",          200),
                            ("Minotaur",       180),
                            ("Titan Smash",    150),
                            ("Colossus",       120),
                            ("Abomination",     80),
                            ("Emperor",         40),
                            ("Eartha",          10),
                            ("Spring Eartha",    1),
                            ("Summer Eartha",    1),
                            ("Autumn Eartha",    1),
                            ("Winter Eartha",    1),
                        ]
                        _pool = [n for n, w in _giant_weights for _ in range(w)]
                        _reward = random.choice(_pool)
                        if _reward not in unlocked:
                            unlocked.add(_reward)
                            _save_data(unlocked, stats)
                            _show_unlocks([_reward])
                        else:
                            _save_data(unlocked, stats)
                if _konami_flag[0]:
                    stats["konami_unlocked"] = True
                    _konami_flag[0] = False
                if action == 'rematch':
                    continue
                break
            continue

        # --- Normal fight path ---
        if mode == '2p':
            vs_ai, difficulty = False, 'medium'
        else:
            vs_ai, difficulty = True, mode[1]

        p1_idx, p2_idx = character_select(vs_ai=vs_ai, unlocked=unlocked, unlock_hints=hints,
                                          unlock_progress=_unlock_progress(stats))
        if p1_idx is None:
            continue

        s_idx = stage_select()
        while True:
            result = run_fight(p1_idx, p2_idx, vs_ai=vs_ai, ai_difficulty=difficulty, stage_idx=s_idx)
            action, info = result if isinstance(result, tuple) else (result, (False,)*5 + (None, None, 0, 0))
            p1_won, p1_char, stage, is_perfect, is_clutch, p2_char, ai_diff, p1_void_falls = info[:8]
            p1_hp_rem   = info[8] if len(info) > 8 else 0
            p1_half_hp  = info[9] if len(info) > 9 else False
            if vs_ai:
                update_stats(stats, p1_won, p1_char, stage, is_perfect, is_clutch, p2_char, ai_diff, p1_void_falls, p1_hp_rem, p1_half_hp)
            else:
                if p1_won:
                    stats["wins_2p"] = stats.get("wins_2p", 0) + 1
                stats["void_deaths"] = stats.get("void_deaths", 0) + p1_void_falls
            # Track daily date and 3:33pm even outside vs-AI fights
            today = datetime.date.today().isoformat()
            dates = stats.get("daily_play_dates", [])
            if today not in dates:
                dates.append(today)
                stats["daily_play_dates"] = dates
            now = datetime.datetime.now()
            if now.hour == 15 and now.minute == 33:
                stats["played_at_333pm"] = True
            if _konami_flag[0]:
                stats["konami_unlocked"] = True
                _konami_flag[0] = False
            if _iddqd_flag[0]:
                stats["iddqd_win"] = True
                _iddqd_flag[0] = False
            if _ragequit_flag[0]:
                stats["rage_quit_typed"] = True
                _ragequit_flag[0] = False
            if _everything_flag[0]:
                stats["everything_collected"] = stats.get("everything_collected", 0) + _everything_flag[0]
                _everything_flag[0] = 0
            if _void_fall_timer_flag[0]:
                stats["void_fall_at_2_7"] = True
                _void_fall_timer_flag[0] = False
            if _jungle_kills_flag[0]:
                stats["jungle_snake_kills"] = stats.get("jungle_snake_kills", 0) + _jungle_kills_flag[0]
                _jungle_kills_flag[0] = 0
            if _paradox_portals_flag[0]:
                stats["paradox_portals_done"] = True
                _paradox_portals_flag[0] = False
            if _totem_kill_flag[0]:
                stats["died_from_totem"] = True
                _totem_kill_flag[0] = False
            if _computer_bug_kills_flag[0]:
                stats["computer_bug_kills"] = stats.get("computer_bug_kills", 0) + _computer_bug_kills_flag[0]
                _computer_bug_kills_flag[0] = 0
            if vs_ai and p1_won and not _p1_non_crit_flag[0]:
                stats["crit_only_wins"] = stats.get("crit_only_wins", 0) + 1
            if vs_ai and not p1_won and not _p1_opp_hit_flag[0] and _p1_powerup_kill_flag[0]:
                stats["died_by_powerup"] = True
            if _type42_typed[0]:
                stats["type42_done"] = True
                _type42_typed[0] = False
            if _p1_proj_blocked[0]:
                stats["projectiles_blocked"] = stats.get("projectiles_blocked", 0) + _p1_proj_blocked[0]
                _p1_proj_blocked[0] = 0
            if _symbol_char_flag[0]:
                stats["symbol_char_typed"] = True
                _symbol_char_flag[0] = False
            if _death_defyer_flag[0]:
                stats["death_defyer_typed"] = True
                _death_defyer_flag[0] = False
            if _friday13_flag[0]:
                stats["friday13_typed"] = True
                _friday13_flag[0] = False
            if _map_man_flag[0]:
                stats["map_man_unlocked"] = True
                _map_man_flag[0] = False
            if _nick_of_time_flag[0]:
                stats["nick_of_time_win"] = True
                _nick_of_time_flag[0] = False
            # Award seasonal coin for winning during an active event
            if p1_won and get_active_event() is not None:
                stats["seasonal_coins"] = stats.get("seasonal_coins", 0) + 1
                _show_seasonal_coin_earned(stats["seasonal_coins"])
            new_unlocks = check_and_unlock(unlocked, stats)
            if new_unlocks:
                _save_data(unlocked, stats)
                _show_unlocks(new_unlocks)
            if action == 'rematch':
                continue
            break

if __name__ == "__main__":
    main()
