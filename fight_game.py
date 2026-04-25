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
                            StageEraser, DrawnPlatform, TimedPlatform, Portal, ConveyorBelt,
                            Spring, SnakeHook, Pumpkin, FallingSkull,
                            JungleSnake, ComputerBug, MousePlatform,
                            Projectile, Orb, BouncingBall, Whip, HotPotato,
                            FallingPot, RollingCoin, FallingMerlin,
                            FlyingBaseball, FlyingBat, KitsuneShot, WaterBall, BeeShot, SnipeShot,
                            FireBall, ThunderBolt, Scroll, TotemPole,
                            RemoteController, Apple, VenomBean, PlantSpike,
                            ChargedOrb, BubbleShot, PoisonOrb, BlackHole)
import fight_network as _net
from fight_ui import stage_select, mode_select, character_select, online_menu, _type42_typed, secret_menu, _map_man_flag, TouchControls

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
    "Bazooka Man":         ("win_with",       "Titan",         1,  "Win 1 match as Titan"),
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
    "Cactus":              ("win_on_stage",   "Desert",        1,  "Win on Desert stage"),
    "Arsonist":            ("win_on_stage",   "Volcano",       1,  "Win on Volcano stage"),
    "Cryogenisist":        ("win_on_stage",   "Arctic Tundra", 1,  "Win on Arctic Tundra"),
    "Magician":            ("win_on_stage",   "Circus",        1,  "Win on Circus stage"),
    "Headless Horseman":   ("win_on_stage",   "Haunted House", 1,  "Win on Haunted House"),
    "Astronaut":           ("win_on_stage",   "Space",         1,  "Win on Space stage"),
    "Spooderman":          ("win_on_stage",   "City Rooftop",  1,  "Win on City Rooftop"),
    "Wizard":              ("win_on_stage",   "Dream Land",    1,  "Win on Dream Land stage"),
    "Lava Man":            ("win_on_stage",   "Volcano Core",  1,  "Win on Volcano Core stage"),
    "Angel":               ("win_on_stage",   "Sky Island",    1,  "Win on Sky Island stage"),
    "Demon":               ("win_on_stage",   "Underworld",    1,  "Win on Underworld stage"),
    "Dark Mage":           ("win_on_stage",   "The Void",      1,  "Win on The Void stage"),
    "Pirate":              ("win_on_stage",   "Pirate Ship",   1,  "Win on Pirate Ship stage"),
    "Medusa":              ("win_on_stage",   "Underwater",    1,  "Win on Underwater stage"),
    "The Creator":         ("win_on_stage",   "Computer",      1,  "Win on Computer stage"),
    "Ink Brush":           ("win_on_stage",   "Dojo",          3,  "Win on Dojo 3 times"),
    "Knight":              ("win_on_stage",   "Medieval Castle", 3, "Win on Medieval Castle 3 times"),
    "Necromancer":         ("win_on_stage",   "Graveyard",     3,  "Win on Graveyard 3 times"),
    "Levitator":           ("win_on_stage",   "Sky Island",    3,  "Win on Sky Island 3 times"),
    "Pyro":                ("win_on_stage",   "Volcano",       3,  "Win on Volcano 3 times"),
    # ── win_hard_ai ─────────────────────────────────────────────────────────
    "Hardy":               ("win_hard_ai",    None,            1,  "Win 1 match vs Hard AI"),
    "ASCII":               ("win_hard_ai",    None,            2,  "Win 2 matches vs Hard AI"),
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
    "Ghost":               ("perfect_wins",   None,            3,  "Win 3 matches at full HP"),
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
    "777":                 ("daily_streak",          None,            7,  "Play 7 days in a row",               True),
    "Scratch":             ("konami_unlock",        None,            1,  "Enter the secret code",              True),
    "Void Master":         ("win_on_stage",         "The Void",      5,  "Master the void to own it",          True),
    "Screentime":          ("played_at_noon",       None,            1,  "Play at a very specific time",       True),
    "God":                 ("perfect_mega_hard_win",None,            1,  "A godlike feat of perfection",       True),
    "Nightfall":           ("midnight_wins",        None,            3,  "Win matches late into the night",    True),
    "Lucky":               ("lucky_win",            None,            1,  "Win a match with exactly 7 HP",      True),
    "Great Totem Spirit":  ("died_from_totem",       None,            1,  "Die in front of the totem pole",     True),
    # ── Regular new characters ──────────────────────────────────────────────
    "Flash":               ("win_streak",           None,            6,  "Win 6 matches in a row"),
    "Portal Maker":        ("win_on_stage",         "The Void",      3,  "Win on The Void 3 times"),
    "Gravity":             ("matches_played",       None,           90,  "Play 90 matches"),
    "Prime Time":          ("prime_time_win",       None,            1,  "Win at a prime number second",       True),
    "Rage Quitter":        ("rage_quit_typed",      None,            1,  "Type something on the lose screen",  True),
    # ── new regular characters ───────────────────────────────────────────────
    "Swapper":             ("win_on_stage",         "The Void",      5,  "Win 5 matches on The Void"),
    "Bruiser":             ("survival_kills",       None,           75,  "Get 75 kills in survival"),
    "Grappler":            ("win_streak",           None,            5,  "Win 5 matches in a row"),
    "Trickster":           ("losses",                None,            7,  "Lose 7 matches"),
    "Wildcard":            ("matches_played",       None,           45,  "Play 45 matches"),
    "Ironclad":            ("win_hard_ai",          None,           10,  "Win 10 matches vs Hard AI"),
    "Siphon":              ("win_with",             "Vamp Lord",     5,  "Win 5 matches as Vamp Lord"),
    "Timekeeper":          ("win_on_stage",         "Space",         4,  "Win on Space 4 times"),
    "Rainbow Man":         ("everything_collected", None,           10,  "Collect 10 'Everything' powerups"),
    # ── new secret characters ────────────────────────────────────────────────
    "The One":             ("win_with_all", "777,Scratch,Void Master,Screentime,God,Nightfall,Lucky,Great Totem Spirit,Prime Time,Rage Quitter,Mirror,Paradox", 1, "Win with every other secret character", True),
    "Mirror":              ("win_half_hp",           None,            1,  "Win with half your starting health", True),
    "Paradox":             ("paradox_portals_done", None,            1,  "Go through portals... a lot",        True),
    "Spitting Cobra":      ("jungle_snake_kills", None,              100, "Kill 100 snakes in the Jungle"),
    "Jetpack":             ("void_fall_at_2_7", None,                1,  "Fall into the void at just the right moment", True),
    "The Impossible Victor": ("win_with",    "Impossible",           1,  "Win 1 match as Impossible"),
    "Pacman":              ("survival_kills",        None,           15,  "Get 15 kills in survival"),
    "ChickenBanana":       ("win_on_stage",          "Computer",      3,  "Something... glitchy",               True),
    "Soul Master":         ("secret_chars",          None,            5,  "Unlock 5 secret characters"),
    # ── new regular characters ───────────────────────────────────────────────
    "Scorpio":             ("computer_bug_kills",   None,          100,  "Kill 100 computer bugs"),
    "Nuke":                ("win_with",             "Bomb",          1,  "Win 1 match as Bomb"),
    "Druid":               ("win_on_stage",          "Jungle",        3,  "Win 3 matches on Jungle"),
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
    "Dementor":            ("died_by_powerup",       None,            1,  "A painful way to go",                  True),
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
    "Sniper":             ("win_hard_ai",            None,            5,  "Win 5 matches vs Hard AI"),
    "Mega-Unhittable":    ("projectiles_blocked",   None,       100000,  "Block 100000 projectiles"),
    "Map Man":            ("map_man_unlocked",       None,            1,  "???",                                  True),
    "<|-\\||>+()":         ("symbol_char_typed",     None,            1,  "???",                                  True),
    "Death Defyer":        ("death_defyer_typed",    None,            1,  "???",                                  True),
    "Friday the 13th":     ("friday13_typed",        None,            1,  "???",                                  True),
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
    }

def load_save():
    """Returns (unlocked_set, stats_dict)."""
    try:
        with open(_UNLOCK_FILE) as f:
            data = json.load(f)
        s     = set(data.get("unlocked", []))
        s.update(_DEFAULT_UNLOCK)
        stats = _default_stats()
        stats.update(data.get("stats", {}))
        # Seed evaluated_chars on first load so existing characters can still unlock normally.
        # Only new characters added in future updates will be gated by the one-fight delay.
        if not stats.get("evaluated_chars"):
            stats["evaluated_chars"] = [ch["name"] for ch in CHARACTERS if ch["name"] in UNLOCK_CONDITIONS]
        return s, stats
    except Exception:
        return set(_DEFAULT_UNLOCK), _default_stats()

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

# ---------------------------------------------------------------------------
# Fight loop
# ---------------------------------------------------------------------------

def run_fight(p1_idx, p2_idx, vs_ai=False, ai_difficulty='medium', stage_idx=0):
    _stage_name = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13   # floaty anti-gravity
    constants.STAGE_VOID    = (_stage_name == "The Void")
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

    _touch = TouchControls(P1_CTRL)

    # Copycat: copy opponent's ability flags at fight start
    _COPY_EXCLUDE = {"name", "color", "speed", "jump", "punch_dmg", "kick_dmg",
                     "max_hp", "block", "desc", "double_jump", "copycat",
                     "snake", "screentime", "chicken_banana", "cloned", "shapeshifter"}
    for _copier, _source in [(p1, p2), (p2, p1)]:
        if _copier.char.get("copycat"):
            for k, v in _source.char.items():
                if k not in _COPY_EXCLUDE and v:
                    _copier.char[k] = v
            _copier._reinit_ability_timers()

    if constants.STAGE_VOID:
        # Spawn on the central platform (GROUND_Y-70), not on the (absent) floor
        p1.x = 380.0; p1.y = float(GROUND_Y - 70); p1.on_ground = True
        p2.x = 520.0; p2.y = float(GROUND_Y - 70); p2.on_ground = True

    stage_data = STAGES[stage_idx % len(STAGES)]
    platforms  = [Platform(*p) for p in stage_data["platforms"]] + [ConveyorBelt(*c) for c in stage_data.get("conveyors", [])]
    springs    = [Spring(*s)   for s in stage_data["springs"]]

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
    stage_pencil = None
    stage_eraser = None
    if is_computer:
        platforms.append(MousePlatform(80, GROUND_Y - 62, travel=720))
        stage_pencil = StagePencil()
        stage_eraser = StageEraser()

    _p1_portals_this_fight = [0]   # count of portals p1 travels through this fight
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
            _touch.handle_event(event)
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

            # Update clones
            new_clones = []
            for cd in clones:
                if not cd.get('permanent'):
                    cd['timer'] -= 1
                if cd['timer'] > 0 and cd['fighter'].hp > 0:
                    cd['fighter'].update(None, cd['target'], platforms)
                    new_clones.append(cd)
            clones = new_clones

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
                        victim.hp = max(0, victim.hp - 8)
                        victim.flash_timer = 6
                        thrower.boomerang_hit_cd = 30   # 0.5s between hits

            # Laser Eyes beam damage
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if (shooter.char.get("laser_eyes") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    correct_side = ((shooter.facing == 1  and victim.x > shooter.x) or
                                    (shooter.facing == -1 and victim.x < shooter.x))
                    if correct_side and abs((victim.y - 60) - laser_y) < 35:
                        victim.hp = max(0, victim.hp - 2)
                        victim.flash_timer = 4
                        shooter.laser_hit_cd = 15  # damage tick every 15 frames

            keys = _touch.inject(pygame.key.get_pressed())
            p1.update(keys, p2, platforms)
            p2.update(keys, p1, platforms)

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
                        constants.STAGE_VOID    = (stage_data["name"] == "The Void")
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
                        elif victim.blocking:
                            b.alive = False
                            if victim is p1:
                                _p1_proj_blocked[0] += 1
                        else:
                            victim.hp = max(0, victim.hp - 10)
                            victim.flash_timer = 8
                            b.alive = False
            balls = [b for b in balls if b.alive]

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
                        victim.hp = max(0, victim.hp - o.EXPLODE_DMG)
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
                        elif victim.blocking:
                            co.alive = False
                            if victim is p1:
                                _p1_proj_blocked[0] += 1
                        else:
                            victim.hp = max(0, victim.hp - co.dmg)
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
                        else:
                            victim.bubble_shield = True
                            victim.active_powerups['Bubble Kick'] = FPS * 3
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
                        else:
                            victim.hp = max(0, victim.hp - 15)
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
                sb['bug'].update(sb['target'])
            spawned_bugs = [sb for sb in spawned_bugs if sb['bug'].alive]
            _computer_bug_kills_flag[0] += _prev_sb - len(spawned_bugs)

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
                        victim.hp = max(0, victim.hp - 10)
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
                            victim.hp = max(0, victim.hp - TotemPole.DMG)
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
                            victim.hp = max(0, victim.hp - RemoteController.DMG)
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
                            victim.hp = max(0, victim.hp - Apple.DMG)
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

            # Update scrolls and check collisions
            for sc in scrolls:
                sc.update()
                if sc.alive and sc.hit_cd == 0:
                    victim = p2 if sc.owner is p1 else p1
                    if sc.collides(victim):
                        victim.hp = max(0, victim.hp - Scroll.DMG)
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
                        victim.knockback = pull_dir * 22
                        victim.hp = max(0, victim.hp - 6)
                        victim.flash_timer = 8
                        h.alive = False
            hooks = [h for h in hooks if h.alive]

            # Pumpkins (Headless Horseman)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(
                        shooter.x + shooter.facing * 24, shooter.y - 80,
                        shooter.facing, shooter))
            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    victim = p2 if pk.owner is p1 else p1
                    if math.hypot(pk.x - victim.x, pk.y - (victim.y - 60)) < pk.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - pk.EXPLODE_DMG)
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
                        victim.hp = max(0, victim.hp - w.DMG)
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
                        else:
                            victim.hp = max(0, victim.hp - BeeShot.DMG)
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
                    victim.hp = max(0, victim.hp - 2)
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
                            victim.hp = max(0, victim.hp - 6)
                            victim.flash_timer = 8
                            snake.snake_contact_cd = 60
                            break

            # Volt: auto-shock nearby opponent every 3 seconds
            for attacker, victim in [(p1, p2), (p2, p1)]:
                if attacker.char.get("shock_aura") and attacker.hp > 0:
                    if attacker.shock_aura_timer > 0:
                        attacker.shock_aura_timer -= 1
                    else:
                        attacker.shock_aura_timer = FPS * 3
                        if abs(attacker.x - victim.x) < 140:
                            victim.hp = max(0, victim.hp - 8)
                            victim.flash_timer = 10
                            if not victim.char.get("immune"):
                                victim.shock_frames = max(victim.shock_frames, 240)

            # Chainsaw Man: rapid proximity damage
            for attacker, victim in [(p1, p2), (p2, p1)]:
                if attacker.char.get("chainsaw") and attacker.hp > 0:
                    if attacker.chainsaw_cd > 0:
                        attacker.chainsaw_cd -= 1
                    elif abs(attacker.x - victim.x) < 50:
                        victim.hp = max(0, victim.hp - 4)
                        victim.flash_timer = 4
                        attacker.chainsaw_cd = 15

            # Necromancer: revive on first death
            for f in (p1, p2):
                if f.hp <= 0 and f.char.get("undead") and not f.undead_used:
                    f.hp          = int(f.max_hp * 0.4)
                    f.undead_used = True
                    f.flash_timer = 30

            # Revenant: revive up to 2 times at 30% HP
            for f in (p1, p2):
                if f.hp <= 0 and f.char.get("revenant") and f.revenant_count < 2:
                    f.hp             = int(f.max_hp * 0.3)
                    f.revenant_count += 1
                    f.flash_timer    = 30

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
                        victim.hp = max(0, victim.hp - 60)
                        victim.flash_timer = 20

            # Pyro auto-fire balls
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_autofire:
                    shooter.pending_autofire = False
                    fire_balls.append(FireBall(shooter.x + shooter.facing * 30,
                                               shooter.y - 60, shooter.facing, shooter))
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
                        victim.hp = max(0, victim.hp - 15)
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
                        victim.hp = max(0, victim.hp - 25)
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
                    victim.hp = max(0, victim.hp - 15)
                    victim.flash_timer = 10
                    qw['hit_cd'] = 30
                if qw['life'] > 0 and 0 <= qw['x'] <= WIDTH:
                    new_qw.append(qw)
            quake_waves = new_qw

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
                                victim.hp = max(0, victim.hp - sk.DMG)
                                victim.flash_timer = 10
                                sk.hit_cd = sk.HIT_CD

            timer -= 1
            if timer <= 0 or p1.hp <= 0 or p2.hp <= 0:
                # Jetpack unlock: p1 fell into void with 2–7 seconds remaining
                if p1.hp <= 0 and constants.STAGE_VOID and FPS * 2 <= timer <= FPS * 7:
                    _void_fall_timer_flag[0] = True
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
                        if pu.spec['type'] == 'clone':
                            cf = AIFighter(fighter.x + 60 * fighter.facing,
                                           fighter.char, fighter.facing, 'hard')
                            cf.hp    = 80
                            cf.color = fighter.color
                            clones.append({'fighter': cf, 'timer': 30 * FPS, 'target': foe})
                        else:
                            fighter.apply_powerup(pu.spec)
                            if (fighter is p1
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

        draw_bg(screen, stage_idx)
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for portal in portals_obj:
            portal.draw(screen)
        for plat in platforms:
            plat.draw(screen, stage_idx)
        for sp in springs:
            sp.draw(screen)
        for pu in powerups:
            pu.draw(screen)
        for b in balls:
            b.draw(screen)
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
        for h in hooks:
            h.draw(screen)
        for pk in pumpkins:
            pk.draw(screen)
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
        for fb in fire_balls:
            fb.draw(screen)
        for tb in thunder_bolts:
            tb.draw(screen)
        for ps in plant_spikes:
            ps.draw(screen)
        for qw in quake_waves:
            t = 1.0 - qw['life'] / 90
            r = max(6, int(18 - t * 8))
            col = (180 + int(t * 60), int(130 - t * 70), 30)
            pygame.draw.ellipse(screen, col, (int(qw['x']) - r, GROUND_Y - r // 2, r * 2, r // 2 + 3))
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
            _touch.draw(screen)

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Survival mode
# ---------------------------------------------------------------------------

def run_survival(p1_idx, p2_idx=None, two_player=False, stage_idx=0):
    _stage_name   = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13
    constants.STAGE_VOID    = (_stage_name == "The Void")
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
    platforms   = [Platform(*p) for p in stage_data["platforms"]]
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
                ci = random.randint(0, len(CHARACTERS) - 1)
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
                            p.hp = max(0, p.hp - 2)
                            p.flash_timer = 4
                            en.laser_hit_cd = 15
                            break

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
            for en in enemies:
                if en.boomerang_timer > 0 and en.boomerang_hit_cd == 0:
                    bx = en.x + math.cos(en.boomerang_angle) * 85
                    by = (en.y - 60) + math.sin(en.boomerang_angle) * 55
                    for p in living:
                        if math.hypot(bx - p.x, by - (p.y - 60)) < 48:
                            p.hp = max(0, p.hp - 8)
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
                            p.hp = max(0, p.hp - 6); p.flash_timer = 8
                            h.alive = False; break
            en_hooks = [h for h in en_hooks if h.alive]

            # Enemy balls → players
            for b in en_balls:
                b.update()
                if b.alive:
                    for p in living:
                        if b.collides(p):
                            p.hp = max(0, p.hp - 10); p.flash_timer = 8
                            b.alive = False; break
            en_balls = [b for b in en_balls if b.alive]

            # Enemy orbs → players
            for o in en_orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    for p in living:
                        if math.hypot(o.x - p.x, o.y - (p.y - 60)) < o.EXPLODE_RADIUS:
                            p.hp = max(0, p.hp - o.EXPLODE_DMG); p.flash_timer = 14
            en_orbs = [o for o in en_orbs if o.alive]

            # Enemy bouncing balls → players
            for bb in en_bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    for p in living:
                        if bb.collides(p):
                            p.hp = max(0, p.hp - 10); p.flash_timer = 8
                            bb.hit_cd = BouncingBall.HIT_CD; break
            en_bounce_balls = [bb for bb in en_bounce_balls if bb.alive]

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
                            p.hp = max(0, p.hp - pk.EXPLODE_DMG); p.flash_timer = 14
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
                            p.hp = max(0, p.hp - w.DMG)
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
                            p.hp = max(0, p.hp - 4)
                            p.flash_timer = 4
                            en.chainsaw_cd = 15
                            break

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
                                victim.hp = max(0, victim.hp - sk.DMG)
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


# ---------------------------------------------------------------------------
# Online fight loop
# ---------------------------------------------------------------------------

def run_online_fight(net, is_host, p1_char_idx, p2_char_idx,
                     stage_idx, my_name, opp_name):
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
    constants.STAGE_VOID    = (_stage_name == "The Void")
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
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(shooter.x + shooter.facing * 24,
                                            shooter.y - 80, shooter.facing, shooter))

            # Update projectiles
            for b in balls:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8; b.alive = False
            balls = [b for b in balls if b.alive]

            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    victim = p2 if o.owner is p1 else p1
                    if math.hypot(o.x - victim.x, o.y - (victim.y - 60)) < o.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - o.EXPLODE_DMG)
                        victim.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    victim = p2 if bb.owner is p1 else p1
                    if bb.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8; bb.hit_cd = BouncingBall.HIT_CD
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            for h in hooks:
                h.update()
                if h.alive:
                    victim = p2 if h.owner is p1 else p1
                    if h.collides(victim):
                        pull = 1 if h.owner.x > victim.x else -1
                        victim.knockback = pull * 22
                        victim.hp = max(0, victim.hp - 6)
                        victim.flash_timer = 8; h.alive = False
            hooks = [h for h in hooks if h.alive]

            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    victim = p2 if pk.owner is p1 else p1
                    if math.hypot(pk.x - victim.x, pk.y - (victim.y - 60)) < pk.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - pk.EXPLODE_DMG)
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
                        victim.hp = max(0, victim.hp - w.DMG)
                        victim.flash_timer = 10
                        victim.knockback = w.facing * 14
                        w.hit_done = True
            whips = [w for w in whips if w.alive]

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
                        victim.hp = max(0, victim.hp - 2)
                        victim.flash_timer = 4; shooter.laser_hit_cd = 15

            # Boomerang
            for thrower, victim in [(p1, p2), (p2, p1)]:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    if math.hypot(bx - victim.x, by - (victim.y - 60)) < 48:
                        victim.hp = max(0, victim.hp - 8)
                        victim.flash_timer = 6; thrower.boomerang_hit_cd = 30

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
                "balls":  [{"x": b.x, "y": b.y, "vx": b.vx} for b in balls],
                "orbs":   [{"x": o.x, "y": o.y, "exp": o.exploding} for o in orbs],
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
                    # Reconstruct ball visuals from state
                    balls = []
                    for bd in m.get("balls", []):
                        b = Projectile.__new__(Projectile)
                        b.x = bd["x"]; b.y = bd["y"]
                        b.vx = bd["vx"]; b.alive = True; b.owner = None
                        balls.append(b)

            # Springs (visual only on client — host is authoritative)
            for sp in springs:
                sp.update()

        # ── Draw ────────────────────────────────────────────────────────────
        draw_bg(screen, stage_idx)
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for plat in platforms: plat.draw(screen, stage_idx)
        for sp   in springs:   sp.draw(screen)
        for b    in balls:     b.draw(screen)
        for o    in orbs:      o.draw(screen)
        for bb   in bounce_balls: bb.draw(screen)
        for h    in hooks:     h.draw(screen)
        for pk   in pumpkins:  pk.draw(screen)
        for w    in whips:     w.draw(screen)

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
                    stage_idx, my_name, opp_name):
    """Wrapper: create a _RelayNet adapter and delegate to run_online_fight."""
    net = _RelayNet(lobby)
    net.opp_name = opp_name
    return run_online_fight(net, is_host, p1_char_idx, p2_char_idx,
                            stage_idx, my_name, opp_name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

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

        # --- Secret menu path ---
        if mode == 'secret_menu':
            newly = secret_menu(unlocked, stats)
            if newly:
                for name in newly:
                    cond = UNLOCK_CONDITIONS.get(name)
                    if cond and len(cond) > 4 and cond[4]:
                        stats["secret_chars_unlocked"] = stats.get("secret_chars_unlocked", 0) + 1
                _save_data(unlocked, stats)
                _show_unlocks(newly)
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
                                s_idx, userdata['username'], opp_name)
            else:
                net, my_char, opp_char, s_idx = info
                if role == 'host':
                    p1_char, p2_char = my_char, opp_char
                else:
                    p1_char, p2_char = opp_char, my_char
                run_online_fight(net, role == 'host', p1_char, p2_char,
                                 s_idx, userdata['username'], net.opp_name)
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
            new_unlocks = check_and_unlock(unlocked, stats)
            if new_unlocks:
                _save_data(unlocked, stats)
                _show_unlocks(new_unlocks)
            if action == 'rematch':
                continue
            break

if __name__ == "__main__":
    main()
