"""The Stickman Fight Wiki — the in-game reference everything else feeds.

The wiki has two halves.

THE GENERATED HALF reads the game's own tables. Every character, map, event,
costume, power-up, fuser recipe and achievement in here is built from
fight_data / fight_seasonal / fight_game at the moment you open it, so it can
never drift out of date. Add a character to CHARACTERS and its page is already
written.

THE WRITTEN HALF is for pages a person writes — history, tactics, lore, jokes.
There are two ways to add one, and neither touches any other file:

  0. Press F2 inside the wiki and write it there. It is saved as a file in
     wiki/, exactly as if it had been typed by hand. F3 writes onto the page
     you are already reading — even a generated one. Those notes are a file
     too, with an "attach:" line naming the page they belong to.

  1. Append a dict to PAGES, near the bottom of this file:

         {"section": "lore",
          "title": "Why they fight",
          "subtitle": "nobody remembers",
          "body": ["First paragraph.",
                   ("h", "A heading"),
                   ("b", "a bullet"),
                   ("kv", "Round length", "99 seconds")]}

  2. Drop a plain text file into the wiki/ folder next to this file. No Python
     at all — see wiki/README.txt for the whole format. Anything in there is
     picked up automatically the next time the game starts.

A page's body is a list. A plain string is a paragraph; the tuples are
("h", heading), ("b", bullet), ("kv", key, value), ("bar", label, n, max)
and ("tree", [(depth, text), ...]) for a branching list.
"""
import os
import re

from fight_data import (CHARACTERS, STAGES, STAGE_MATCHUPS, POWERUPS,
                        FUSER_ELEMENTS, FUSER_RECIPES, FUSER_SHOP_CHARS,
                        COSTUMES, ELEMENT_ORDER, ELEMENT_BEATS, ELEMENT_LABEL,
                        ELEMENT_COLOR, ELEMENT_FLAGS, ELEMENT_KIN,
                        ELEMENT_BONUS, ELEMENT_PENALTY, elements_of)
from fight_seasonal import SEASONAL_EVENTS, SEASONAL_SHOP_CHARS
import fight_achievements as _ach

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki")

# ── Sections ────────────────────────────────────────────────────────────────
# The spine of the wiki. Add one here and any page claiming that id lands in
# it; a section with no pages simply does not appear.
SECTIONS = [
    {"id": "basics",       "title": "Basics",       "color": (225, 228, 240)},
    {"id": "characters",   "title": "Characters",   "color": (110, 195, 255)},
    {"id": "maps",         "title": "Maps",         "color": (110, 215, 140)},
    {"id": "events",       "title": "Events",       "color": (255, 200,  60)},
    {"id": "costumes",     "title": "Costumes",     "color": (250, 150, 180)},
    {"id": "fuser",        "title": "The Fuser",    "color": (200, 140, 255)},
    {"id": "modes",        "title": "Modes",        "color": (100, 220, 230)},
    {"id": "powerups",     "title": "Power-ups",    "color": (255, 150,  80)},
    {"id": "achievements", "title": "Achievements", "color": (255, 206,  70)},
    {"id": "lore",         "title": "Hiss-tory",    "color": (175, 165, 205)},
]
SECTION_TITLE = {s["id"]: s["title"] for s in SECTIONS}


# ── Ability names ───────────────────────────────────────────────────────────
# Most flags say what they are once the underscores come out. These are the
# ones that do not.
ABILITY_NAMES = {
    "double_jump": "Double jump",         "glass_jaw": "Glass jaw",
    "glass_cannon": "Glass cannon",       "stone_skin": "Stone skin",
    "iron_fist": "Iron fist",             "iron_block": "Iron block",
    "drain_aura": "Life drain aura",      "toxic_aura": "Toxic aura",
    "fire_aura": "Fire aura",             "shock_aura": "Shock aura",
    "snow_aura": "Freezing aura",         "combat_regen": "Regenerates in combat",
    "regen": "Regenerates",               "undead": "Undead",
    "phoenix_revive": "Rises from the ashes", "death_defyer": "Death defyer",
    "explode_death": "Explodes on death", "contact_dmg": "Hurts on contact",
    "spike_body": "Spiked body",          "shell_body": "Shelled body",
    "anchor_body": "Anchored — cannot be moved",
    "sleep_body": "Sleeps where it stands",
    "water_breathing": "Breathes underwater",
    "lava_immune": "Unburnable",          "void_immune": "Void immune",
    "immune": "Immune to status",         "unhittable": "Hard to hit",
    "mega_unhittable": "Nearly untouchable",
    "ghost_float": "Floats",              "slow_fall": "Falls slowly",
    "anti_gravity": "Anti-gravity",       "wall_cling": "Clings to walls",
    "jetpack": "Jetpack",                 "speedster": "Speedster",
    "heavy": "Heavy",                     "giant": "Giant",
    "tiny": "Tiny",                       "colossus": "Colossus",
    "juggernaut": "Juggernaut",           "berserker": "Berserker",
    "berserk_low": "Berserk at low HP",   "always_berserk": "Always berserk",
    "always_crit": "Always crits",        "crit_only": "Crits only",
    "first_strike": "First strike",       "execute": "Executes the wounded",
    "giant_killer": "Giant killer",       "godslayer": "Godslayer",
    "backstab": "Backstab",               "vampire": "Vampiric",
    "block_break": "Breaks blocks",       "armor_proj": "Armoured against shots",
    "reflect_proj": "Reflects projectiles", "deflect_proj": "Deflects projectiles",
    "reflect_block": "Blocks reflect",    "thorn_block": "Thorned block",
    "absorb_block": "Block absorbs",      "absorb_hit": "Absorbs hits",
    "auto_counter": "Auto-counter",       "stalwart_counter": "Stalwart counter",
    "parry_strike": "Parry strike",       "auto_forcefield": "Auto forcefield",
    "bubble_shield": "Bubble shield",     "auto_teleport": "Teleports away from danger",
    "crazy_teleport": "Teleports at random",
    "shadow_teleport_block": "Teleports when blocking",
    "phase": "Phases",                    "phase_dodge": "Phase dodge",
    "oracle_dodge": "Sees it coming",     "spider_dodge": "Spider dodge",
    "mirage": "Mirage",                   "chameleon": "Chameleon",
    "copycat": "Copies the opponent",     "mimic_move": "Mimics moves",
    "mimic_stats": "Mimics stats",        "shapeshift": "Shapeshifts",
    "random_stats": "Random stats",       "all_or_nothing": "All or nothing",
    "hp_swap": "Swaps HP",                "time_freeze": "Freezes time",
    "chain_hits": "Chains hits",          "combo_punch": "Combo punch",
    "triple_slash": "Triple slash",       "twin_strike": "Twin strike",
    "rapid_fire": "Rapid fire",           "auto_fire": "Fires on its own",
    "long_range": "Long reach",           "wide_punch": "Wide punch",
    "laser_eyes": "Laser eyes",           "orb_shooter": "Orb shooter",
    "sniper_shot": "Sniper shot",         "nuke_bomb": "Nuke",
    "bomb_character": "Living bomb",      "money_hit": "Hits pay out",
    "lucky_strike": "Lucky strike",       "clover_luck": "Four-leaf luck",
    "growing_dmg": "Damage grows",        "rage_build": "Builds rage",
    "rage_damage": "Rage damage",         "rage_stack": "Rage stacks",
    "speed_stack": "Speed stacks",        "speed_steal": "Steals speed",
    "momentum": "Momentum",               "overdrive": "Overdrive",
    "overload": "Overload",               "pacifist": "Pacifist",
    "screentime": "Steals the screen",    "glitch_char": "Glitched",
    "f13_dmg": "Friday the 13th damage",
    "prime_dmg": "Prime-number damage",   "seven_punch": "Lucky seven punch",
    "halves_punch": "Halving punch",      "nick_of_time": "Nick of time",
    "soul_master": "Soul master",         "voodoo": "Voodoo",
    "cursed_drain": "Cursed drain",       "siphon_leech": "Siphons life",
    "dementor_heal": "Feeds on fear",     "revenant": "Revenant",
    "shade": "Shade",                     "disorientated": "Disorientated",
    "feedback": "Feedback",               "buffer_char": "Buffering",
    "stillness_regen": "Heals by standing still",
    "desperation_speed": "Faster when hurt",
    "ngs_dreidel": "Spins the dreidel",
    "chaos_nghs": "Chaotic damage — 200, 25, 0, or heals you 2",
    "titan_grip": "Titan grip",           "quake_land": "Quake landing",
    "smoke_trail": "Smoke trail",         "flame_trail": "Flame trail",
    "wildfire": "Wildfire",               "chaos_strike": "Chaos strike",
    "chaos_timer": "Chaos timer",         "magnet": "Magnetic",
    "snake": "Serpent",                   "chomp": "Chomps",
    "chef": "Cooks",                      "cloned": "Cloned",
    "ai_clones": "Fights with clones",    "armor_threshold": "Armour threshold",
    "peg_leg_balance": "Peg-leg balance",
}

_HIDE_FLAGS = {"shop_only", "costume_variant", "legacy_costume"}


# ── What kind of fighter is this? ───────────────────────────────────────────
# The leaves of the roster tree, each with a colour. A fighter wears the ones
# it matches; two elements means half and half, three means thirds.
CATEGORIES = [
    ("secret",      "Secret",       (202,  62,  92)),
    ("master",      "Master",       (242, 162,  70)),
    ("pyrokin",     "Pyrokin",      (236,  92,  44)),
    ("fishikin",    "Fishikin",     ( 58, 140, 232)),
    ("cryokin",     "Cryokin",      (150, 226, 246)),
    ("shockkin",    "Shockkin",     (242, 214,  62)),
    ("venomskin",   "Venomskin",    (128, 206,  70)),
    ("jokkin",      "Jokkin",       (226, 102, 210)),
    ("hammerhead",  "Hammerhead",   (154, 162, 178)),
    ("gunners",     "Gunners",      (108, 142, 174)),
    ("explosers",   "Explosers",    (250, 150,  50)),
    ("copycats",    "Copycats",     (190, 170, 232)),
    ("snake",       "Snake clan",   ( 58, 182,  92)),
    ("bug",         "Bug clan",     (154, 172,  62)),
    ("unhittable",  "Unhittables",  (238, 238, 248)),
    ("ghost",       "Ghost clan",   (176, 206, 226)),
    ("major",       "Seasonal major", (255, 200,  60)),
    ("minor",       "Seasonal minor", (206, 166,  72)),
    ("variant",     "Variant",      (192, 132,  82)),
    ("fuser",       "Fuser",        (200, 140, 255)),
    ("default",     "Default",      (142, 146, 162)),
    ("other",       "Other",        (106, 110, 126)),
]
CATEGORY_COLOR = {c[0]: c[2] for c in CATEGORIES}
CATEGORY_LABEL = {c[0]: c[1] for c in CATEGORIES}

# Which flags put a fighter in which family. A fighter with none of them has
# no ability worth the name, and falls through to where it came from instead.
# The kins are elements by another name — fire is pyrokin, ice is cryokin.
# fight_data owns that table so a fight and the wiki can never disagree about
# what a fighter is made of.
_CAT_FLAGS = {ELEMENT_KIN[_e]: _f for _e, _f in ELEMENT_FLAGS.items()}
_CAT_FLAGS.update({
    "gunners":    ("sniper_shot", "rapid_fire", "auto_fire", "shoot_kick",
                   "orb_shooter", "laser_eyes", "sniper_multiply_kick",
                   "arcane_orb", "cobra_orb", "rockball_kick", "seed_rain_punch"),
    "explosers":  ("nuke_bomb", "bomb_character", "explode_death", "mine_kick",
                   "deco_bomb_kick", "slime_bomb_kick", "exploding_tire_kick",
                   "bazooka_kick", "worm_mine_punch", "black_hole_kick"),
    "copycats":   ("copycat", "copy_punch", "mimic_move", "mimic_stats", "chameleon",
                   "bloob_shapeshift", "possess_kick", "swap_kick"),
})

# A clan is not something a fighter can do, it is what you had to do to earn
# him. Snakes in the Jungle, bugs in the Computer, projectiles blocked.
# An element beats a firing pattern: a fighter who throws fire is a pyrokin,
# not a gunner who happens to be warm.
_KINS = ("pyrokin", "fishikin", "cryokin", "shockkin", "venomskin", "jokkin",
         "hammerhead")
_OVERPOWERED_BY_KIN = ("gunners", "explosers")

_CLAN_BY_CONDITION = {
    "jungle_snake_kills":  "snake",
    "computer_bug_kills":  "bug",
    "projectiles_blocked": "unhittable",
    "ghost_snake_kills":   "ghost",
}

# Major or minor is a property of the event, not of the fighter: seven of the
# fourteen are the minor ones, and everybody who comes out of them is minor.
MINOR_EVENTS = {
    "Emerald Echoes",        # St Patrick's
    "Bound to the Ground",   # Earth Day
    "Legacy of Valor",       # Tombstone
    "Summer Solstice",
    "Novel Beginnings",      # the book one
    "Project Yellowstone",
    "Aura of Menorah",
}
MAJOR_EVENTS = {c["event"] for c in SEASONAL_SHOP_CHARS} - MINOR_EVENTS


def event_rank(event_name):
    return "minor" if event_name in MINOR_EVENTS else "major"


def seasonal_only(name, conditions=None):
    """True when the shop window is the only way in.

    Plenty of fighters turn up on a seasonal shelf and can also be won some
    other way — Angel is in the Hearts and Harmonies shop and also comes free
    for winning on Sky Island. Those are not seasonals. A seasonal is one you
    cannot get any other way.
    """
    if name not in _SEASONAL_BY_NAME:
        return False
    cond = (conditions or {}).get(name)
    return not cond or cond[3].startswith("Buy in Seasonal Shop")


# The Fuser trades in six elements, but rock, plant and air are not kins —
# no fighter wears them. A fused fighter is a Fuser and nothing else anyway.
_FUSED_CATS = {_res["name"]: ["fuser"] for _res in FUSER_RECIPES.values()}


def categories_of(ch, conditions=None):
    """The families a fighter belongs to, in the order CATEGORIES lists them."""
    flags = {k for k, v in ch.items() if v is True}
    # Two families beat everything else outright. A variant is a variant
    # whatever the fighter underneath can do; and whatever went into a fused
    # fighter, what comes out is a Fuser first and a Fuser last.
    if ch.get("costume_of") or any(k.endswith("_variant") for k in flags):
        return ["variant"]
    if ch["name"] in _FUSED_CATS or ch["name"] in _FUSER_BY_NAME:
        return ["fuser"]
    # So do secret and master, and they are not the same thing: a secret is
    # hidden until somebody finds it, a master is what finding enough of them
    # earns you.
    _c0 = (conditions or {}).get(ch["name"])
    if _c0:
        if len(_c0) > 4 and _c0[4]:
            return ["secret"]
        if _c0[0] == "secret_chars":
            return ["master"]
    cats = [cid for cid, want in _CAT_FLAGS.items() if flags.intersection(want)]
    if any(c in _KINS for c in cats):
        cats = [c for c in cats if c not in _OVERPOWERED_BY_KIN]
    name = ch["name"]
    # A seasonal — one with no other way in — carries its event's standing
    if seasonal_only(name, conditions):
        cats.append(event_rank(_SEASONAL_BY_NAME[name]["event"]))
    _cond = (conditions or {}).get(name)
    if _cond and _cond[0] in _CLAN_BY_CONDITION:
        cats.append(_CLAN_BY_CONDITION[_cond[0]])
    if cats:
        return [c[0] for c in CATEGORIES if c[0] in cats]
    # No ability of its own — say where it came from instead
    try:
        from fight_game import _DEFAULT_UNLOCK
    except Exception:
        _DEFAULT_UNLOCK = set()
    if name in _DEFAULT_UNLOCK:
        return ["default"]
    return ["other"]

# A bar is only worth drawing against the rest of the roster
def _roster_max(key, default):
    vals = [abs(c.get(key, default)) for c in CHARACTERS]
    return max(vals) or 1


STAT_MAX = {k: _roster_max(k, d) for k, d in
            (("max_hp", 100), ("punch_dmg", 8), ("kick_dmg", 10),
             ("speed", 5), ("jump", 15), ("block", 0.5))}


def ability_label(flag):
    """A flag as a person would say it."""
    if flag in ABILITY_NAMES:
        return ABILITY_NAMES[flag]
    if flag.endswith("_variant"):
        return flag[:-8].replace("_", " ").title() + " variant"
    return flag.replace("_", " ").capitalize()


def abilities_of(ch):
    return [ability_label(k) for k, v in sorted(ch.items())
            if v is True and k not in _HIDE_FLAGS and not k.endswith("_variant")]


# ── Where a thing comes from ────────────────────────────────────────────────
def _unlock_tables():
    """fight_game imports fight_ui, which imports this — so load it late."""
    try:
        import fight_game as _g
        return _g.UNLOCK_CONDITIONS, _g._DEFAULT_UNLOCK, set(_g.ONLINE_STAGES)
    except Exception:
        return {}, set(), set(range(len(STAGES)))


def _casino_odds():
    """Name -> how likely the casino is to hand it over, as a percentage."""
    try:
        from fight_game import CASINO_REWARDS
    except Exception:
        return {}
    _total = sum(w for _, w in CASINO_REWARDS) or 1
    return {n: 100.0 * w / _total for n, w in CASINO_REWARDS}


# What each special mode rolls for on a win, and how often
MODE_REWARDS = {
    "Jack O' Slash":        ("The Crooking Glass", 1.0),
    "Broken Jak 0' Lash":   ("The Crooking Glass", 0.1),
    "Cornucopia":           ("Took the L",         1.0),
    "Sickman Stickman":     ("Took the L",         0.1),
}

_SEASONAL_BY_NAME = {c["name"]: c for c in SEASONAL_SHOP_CHARS}
_FUSER_BY_NAME    = {c["name"]: c for c in FUSER_SHOP_CHARS}
_COSTUME_BY_NAME  = {c["name"]: c for c in COSTUMES}


_VARIANT_OWNERS = (("jack_variant", "Jack O' Slash"), ("jawke_variant", "Jawke"),
                   ("tombstone_variant", "Tombstone"), ("clover_variant", "Clover"),
                   ("eartha_variant", "Eartha"), ("solara_variant", "Solara"),
                   ("nghs_variant", "Nun-Gimel-Hei-Shin"),
                   ("bookzworm_variant", "Bookzworm"),
                   ("yellowstone_variant", "Yellowstone"))

SECRET_LINE = "??? — a secret. Nothing written down."


def ways_to_get(name, conditions, default_set, ch=None):
    """Every route to a fighter, not just the first one that fits.

    Plenty of them have two: Angel is in the Hearts and Harmonies shop AND
    comes free for winning on Sky Island. Returns a list of (text, secret)
    pairs — a secret route is one the game itself hides behind "???" on the
    character select, and this keeps that promise.
    """
    ways = []
    if name in default_set:
        ways.append(("Yours from the first match — one of the four you start with", False))
    if name in _COSTUME_BY_NAME:
        c = _COSTUME_BY_NAME[name]
        if c.get("source") == "rack":
            ways.append((f"The costume rack — {c['cost']} coins", False))
        else:
            ways.append((f"Achievement: own every {c['event']} fighter. "
                         f"Earned, never sold", False))
    if name in _SEASONAL_BY_NAME:
        c = _SEASONAL_BY_NAME[name]
        ways.append((f"Seasonal Shop during {c['event']} — {c['cost']} coins", False))
    if name in _FUSER_BY_NAME:
        ways.append((f"The Fuser — {_FUSER_BY_NAME[name]['cost']} coins, plus the elements",
                     False))
    _mode = MODE_REWARDS.get(name)
    if _mode:
        ways.append((f"{_mode[0]} — every ten wins buys one roll, and this "
                     f"one comes up {_mode[1]}% of the time", False))
    _odds = _casino_odds().get(name)
    if _odds is not None:
        ways.append((f"The Casino — every tenth win rolls for one, and this "
                     f"one comes up {_odds:.1f}% of the time", False))
    cond = conditions.get(name)
    if cond:
        text, secret = cond[3], bool(len(cond) > 4 and cond[4])
        # Some conditions only restate the shop, which is already listed
        if not (text.startswith("Buy in Seasonal Shop") and name in _SEASONAL_BY_NAME):
            ways.append((text, secret))
    ch = ch or next((c for c in CHARACTERS if c["name"] == name), None)
    if ch:
        if ch.get("costume_of") and not ways:
            ways.append((f"Comes with {ch['costume_of']} — pick it in his box", False))
        for key, owner in _VARIANT_OWNERS:
            if ch.get(key):
                ways.append((f"A variant of {owner} — pick it in his box", False))
                break
    if not ways:
        ways.append(("Nobody has written this one down yet", False))
    return ways


def is_hidden(name, unlocked, conditions):
    """True when the wiki should not even name this fighter yet.

    Only for fighters whose single route is a secret one. Lucky is flagged
    secret but also sits in a shop window with his name on it, so he is not
    hidden — his secret route is.
    """
    if name in unlocked:
        return False
    cond = conditions.get(name)
    if not (cond and len(cond) > 4 and cond[4]):
        return False
    return not (name in _SEASONAL_BY_NAME or name in _FUSER_BY_NAME
                or name in _COSTUME_BY_NAME)


# ── Generated pages ─────────────────────────────────────────────────────────
def _character_pages(unlocked):
    conditions, default_set, _ = _unlock_tables()
    out = []
    for ch in CHARACTERS:
        name = ch["name"]
        if is_hidden(name, unlocked, conditions):
            # The game shows these as "???" on the character select. So do we.
            out.append({
                "section": "characters", "title": "???",
                "subtitle": "a secret", "color": (90, 90, 108),
                "art": None, "tags": ["secret"], "owned": False,
                "secret": True,
                "body": [SECRET_LINE,
                         "Somebody found this one. They did not write down how.",
                         ("h", "When you find it"),
                         "This page fills itself in the moment the fighter is yours."],
            })
            continue
        abil = abilities_of(ch)
        tags = []
        if ch.get("costume_variant"):
            tags.append("costume")
        if ch.get("legacy_costume"):
            tags.append("legacy")
        if name in _SEASONAL_BY_NAME:
            tags.append("seasonal")
        if name in _FUSER_BY_NAME:
            tags.append("fuser")
        # The description is already the subtitle — no need to say it twice
        body = [("h", "Numbers"),
                ("bar", "Health", ch.get("max_hp", 100), STAT_MAX["max_hp"]),
                ("bar", "Punch",  ch.get("punch_dmg", 8), STAT_MAX["punch_dmg"]),
                ("bar", "Kick",   ch.get("kick_dmg", 10), STAT_MAX["kick_dmg"]),
                ("bar", "Speed",  ch.get("speed", 5), STAT_MAX["speed"]),
                ("bar", "Jump",   abs(ch.get("jump", 15)), STAT_MAX["jump"]),
                ("bar", "Block",  ch.get("block", 0.5), STAT_MAX["block"])]
        if abil:
            body.append(("h", "Abilities"))
            body += [("b", a) for a in abil]
        _els = elements_of(ch)
        if _els:
            body.append(("h", "Made of"))
            for _e in _els:
                _b = ELEMENT_BEATS.get(_e, ())
                body.append(("kv", ELEMENT_LABEL[_e],
                             "beats " + ", ".join(ELEMENT_LABEL[x] for x in _b)
                             if _b else "even against everything"))
        ways = ways_to_get(name, conditions, default_set, ch)
        body.append(("h", "How to get"))
        if len(ways) > 1:
            body.append("Either way works:")
            for text, secret in ways:
                body.append(("b", SECRET_LINE if (secret and name not in unlocked) else text))
        else:
            text, secret = ways[0]
            body.append(SECRET_LINE if (secret and name not in unlocked) else text)
        if ch.get("costume_of"):
            body.append(("h", "Where to find him"))
            body.append(f"In {ch['costume_of']}'s own box on the character select — "
                        f"Q/E for player one, J/L for player two.")
        liked = [s for s, m in STAGE_MATCHUPS.items() if m.get("adv") == name]
        hated = [s for s, m in STAGE_MATCHUPS.items() if m.get("dis") == name]
        if liked or hated:
            body.append(("h", "Ground he knows"))
            for s in liked:
                body.append(("kv", s, "at home"))
            for s in hated:
                body.append(("kv", s, "out of his depth"))
        cats = categories_of(ch, conditions)
        body.insert(0, ("h", "Family"))
        body.insert(1, ("cats", cats))
        out.append({
            "section": "characters", "title": name,
            "subtitle": ch.get("desc", ""), "color": ch["color"],
            "art": ("fighter", name), "tags": tags, "cats": cats,
            "owned": name in unlocked, "body": body,
        })
    return out


def _map_pages(unlocked):
    _, _, online = _unlock_tables()
    out = []
    for i, st in enumerate(STAGES):
        plats   = st.get("platforms", [])
        movers  = [p for p in plats if len(p) > 4 and p[4]]
        body = []
        feats = []
        if movers:
            feats.append("one of the platforms moves" if len(movers) == 1
                         else f"{len(movers)} of the platforms move")
        for key, one, many in (("springs", "a spring", "springs"),
                               ("conveyors", "a conveyor belt", "conveyor belts"),
                               ("portals", "a portal", "portals"),
                               ("hazards", "a hazard", "hazards")):
            if st.get(key):
                feats.append(one if len(st[key]) == 1 else f"{len(st[key])} {many}")
        body.append("A flat floor and "
                    + ("one platform" if len(plats) == 1 else f"{len(plats)} platforms")
                    + (", " + ", ".join(feats) if feats else "") + ".")
        body.append(("h", "What is on it"))
        _n = lambda seq: str(len(seq)) if seq else "none"
        body.append(("kv", "Platforms", _n(plats)))
        body.append(("kv", "Moving platforms", _n(movers)))
        body.append(("kv", "Springs", _n(st.get("springs", []))))
        body.append(("kv", "Conveyors", _n(st.get("conveyors", []))))
        body.append(("kv", "Portals", _n(st.get("portals", []))))
        body.append(("kv", "Hazards", _n(st.get("hazards", []))))
        body.append(("kv", "Online rotation", "yes" if i in online else "no"))
        m = STAGE_MATCHUPS.get(st["name"])
        if m:
            body.append(("h", "Who it suits"))
            if m.get("adv"):
                body.append(("kv", m["adv"], "fights better here"))
            if m.get("dis"):
                body.append(("kv", m["dis"], "fights worse here"))
        out.append({
            "section": "maps", "title": st["name"],
            "subtitle": f"map {i + 1} of {len(STAGES)}",
            "color": (110, 215, 140), "art": ("stage", i),
            "tags": ["online"] if i in online else ["offline only"],
            "body": body,
        })
    return out


# ── The world the stages sit in ─────────────────────────────────────────────
# Drawn by hand first. Each entry: the place, what kind of thing it is, who
# lives there, and what was written about it.
WORLD = [
    ("Sea o' Seasons", "sea", ["Seasonals"],
     "Only skilled navigators get past the Sea o' Seasons. Even Honner Cuboto "
     "cannot. The best way through is the west route — which is why, during "
     "the civil war, the majors took the west."),
    ("Crashipine Mountain Range", "mountains", ["Unhittables"],
     "The longest mountain range in the world. It stretches around 2,398 "
     "quilos."),
    ("Mount Crashipine", "mountain", [],
     "The highest mountain in the world, over 3,000,000 quilos."),
    ("Crashipine Sea", "sea", [],
     "The largest freshwater sea in the world, and known to hold the gentle "
     "but humungous Crashipine monster — Crashi, for short."),
    ("Lake Crash", "lake", [],
     "The small one, at the foot of the range that shares its name."),
    ("Tanzono Rainforest", "forest", ["Snake clan", "Bug clan"],
     "Behold: the biggest rainforest in the world. 4,673,219 quilos squared "
     "and over 900 distinct species. Home to many clans and kins."),
    ("The Waterlan Ocean", "ocean", ["Fishikin"],
     "The middle ocean. The north is hot, grassy and a bit glitchy. The south "
     "you do not want to go to — Fishikin will surround your boat like a "
     "doughnut, and strike."),
    ("Ghost clan's ground", "region", ["Ghost clan"],
     "It was said ghost clan had been spotted here a few times, and that of "
     "course there was no such thing. There is. Five of them, and they came "
     "from here."),
    ("The Great Cities of the United States of Lanbo", "country", [],
     "The crowded middle of the map, where most of the stages people actually "
     "fight on are stacked up next to one another."),
    ("City of Lanbo", "city", [],
     "The capital of the USL. Population nineteen million."),
    ("Cipher Island", "island", ["Secret", "Master"],
     "Cipher had a civil war and split into Secret and Masters. ???"),
    ("The Fuser", "wonder", ["Fuser"],
     "The greatest mystery of Stickman Fight is who made the Fuser. Who?"),
    ("The coldest place in the world", "pole", ["Cryokin"],
     "Cryokin survive freezing temperatures. Even the best freezers dodge "
     "this place. It is about as cold as when atoms freeze."),
    ("Land of Hell", "region", ["Pyrokin"],
     "This area is as hot as a humuwave — that is twice a heatwave."),
    ("Sea of Hell", "sea", ["Pyrokin"],
     "The water on the hot side of the map, for a given value of water."),
    ("Volcano Urn", "volcano", ["Pyrokin"],
     "Boom. Boom. Boom."),
    ("Wombrock Town", "town", [],
     "Wombrocks have been invading Tombstone lately. That is why Tombstone "
     "sent two people to ask you: a tombstone called Tombstone, and, uh — a "
     "black and white lunatic?"),
    ("Ares Desert", "desert", ["Venomskin"],
     "Dry, eastern, and nobody's idea of a shortcut."),
    ("Dragon Skull Islands", "islands", [],
     "Not much is known about this. Some people see it but cannot prove it. "
     "Others do not even think it exists."),
    ("a*@#!x", "???", [],
     "g\u20ac@1!2rAO3xxx#Qwerty? Do! I.like-Q_WeRt.y"),
]

_WORLD_LEGEND = [
    ("A plaque", "somewhere worth reading about"),
    ("A square", "a stage you can fight on"),
    ("A ring",   "ground a tribe holds"),
]


def _world_pages(unlocked):
    out = [{
        "section": "maps", "title": "The world", "pin": True,
        "subtitle": "where all thirty-three stages actually are",
        "color": (110, 215, 140), "art": None,
        "tags": ["world", "map", "geography"],
        "body": [
            ("worldmap",),
            "The stages are not floating in nothing. They sit on a map — one "
            "ocean in the middle, mountains and rainforest to the west, the "
            "hot side to the north-east, the cities crowded in the centre, "
            "and islands around the edge nobody can agree exist.",
            ("h", "Reading the map"),
            "Three marks are used on it, and nothing else.",
        ] + [("kv", _k, _v) for _k, _v in _WORLD_LEGEND] + [
            ("h", "Who holds what"),
            "The tribes are drawn as rings. Every kin and every clan has "
            "ground of its own.",
        ] + [("kv", _tribe, _place)
             for _place, _kind, _tribes, _blurb in WORLD
             for _tribe in _tribes] + [
            ("h", "The places"),
        ] + [("b", _place) for _place, _k, _t, _b in WORLD],
    }]
    for place, kind, tribes, blurb in WORLD:
        body = [blurb, ("h", "What it is"), ("kv", "Kind", kind)]
        if tribes:
            body.append(("kv", "Held by", ", ".join(tribes)))
        body.append(("kv", "Part of", "the world map"))
        out.append({
            "section": "maps", "title": place,
            "subtitle": f"{kind} · from the world map",
            "color": (110, 215, 140), "art": None,
            "tags": ["world"] + [t.lower() for t in tribes],
            "body": body,
        })
    return out


_MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


def _event_pages(unlocked):
    out = []
    for ev in SEASONAL_EVENTS:
        sm, sd = ev["start"]
        em, ed = ev["end"]
        when = (f"{_MONTHS[sm]} {sd}" if (sm, sd) == (em, ed)
                else f"{_MONTHS[sm]} {sd} – {_MONTHS[em]} {ed}")
        roster = [c for c in SEASONAL_SHOP_CHARS if c["event"] == ev["name"]]
        cos    = next((c for c in COSTUMES if c["event"] == ev["name"]), None)
        body = [f"{ev['name']} runs {when}. While it is on, the home screen "
                f"changes, the shop opens, and these fighters can be bought — "
                f"and only then.",
                ("cats", [event_rank(ev["name"])])]
        body.append(("h", "Shop roster"))
        for c in roster:
            body.append(("kv", c["name"], f"{c['cost']} coins"
                                          + ("  ·  owned" if c["name"] in unlocked else "")))
        if ev.get("special_mode_label"):
            body.append(("h", "Special mode"))
            body.append(ev["special_mode_label"] + " — playable only during the event.")
        if cos:
            body.append(("h", "Costume"))
            body.append(f"Own every fighter above and {cos['name']} is yours, "
                        f"a new coat for {cos['base']}.")
        owned = roster and all(c["name"] in unlocked for c in roster)
        out.append({
            "section": "events", "title": ev["name"], "subtitle": when,
            "color": (255, 200, 60),
            "art": ("emblem", cos["emblem"], (255, 200, 60)) if cos else ("badge", "saintnix"),
            "tags": [f"{event_rank(ev['name'])} event"] +
                    (["complete"] if owned else []) +
                    (["special mode"] if ev.get("special_mode_label") else []),
            "body": body,
        })
    return out


def _costume_pages(unlocked):
    out = []
    for c in COSTUMES:
        _sold = c.get("source") == "rack"
        out.append({
            "section": "costumes", "title": c["name"],
            "subtitle": f"{c['base']}  ·  {c['event']}",
            "color": c["color"], "art": ("fighter", c["name"]),
            "tags": (["owned"] if c["name"] in unlocked else [])
                    + (["for sale"] if _sold else ["earned"]),
            "owned": c["name"] in unlocked,
            "body": [f"A {c['event']} coat for {c['base']}. Same fighter "
                     f"underneath — same health, same reach, same tricks — "
                     f"wearing something else.",
                     ("h", "How to get it")] +
                    ([f"On the costume rack for {c['cost']} coins at three "
                      f"stars — more if it is better thought of, less if it "
                      f"is not. The rack has its own box on the home screen, "
                      f"and a door round the back of the Seasonal Shop. It is "
                      f"only on sale during {c['event']}."]
                     if _sold else
                     [f"Own every {c['event']} fighter. The achievement hands "
                      f"it straight over — this one is not for sale, and no "
                      f"amount of coins will buy it."]) +
                    [("h", "Where to wear it"),
                     f"Pick {c['base']} on the character select and press "
                     f"Q/E (P1) or J/L (P2) to flip through his costumes."],
        })
    for name, owner in (("Legacy Tombstone", "Tombstone"), ("Legacy Jawke", "Jawke")):
        ch = next((c for c in CHARACTERS if c["name"] == name), None)
        if not ch:
            continue
        out.append({
            "section": "costumes", "title": name,
            "subtitle": f"{owner}  ·  legacy", "color": ch["color"],
            "art": ("fighter", name), "tags": ["legacy"],
            "owned": name in unlocked,
            "body": [f"The look {owner} wore in the Story Mode teaser, kept "
                     f"as a costume. {owner}'s kit, unchanged.",
                     ("h", "Where to wear it"),
                     f"In {owner}'s own box on the character select."],
        })
    return out


def _fuser_pages(unlocked):
    out = []
    body = ["Type \"the fuser\" on the home screen — once Deco & Emoj is "
            "unlocked — and the Fuser opens. You buy elements, pick two, and "
            "it makes something that is both. Sometimes it fails and you lose "
            "the elements. The rarer the pair, the more often it fails."]
    body.append(("h", "Elements"))
    for name, cost, _col in FUSER_ELEMENTS:
        body.append(("kv", name.title(), f"{cost} coins"))
    out.append({"section": "fuser", "title": "How fusing works",
                "subtitle": "two elements, one fighter", "color": (200, 140, 255),
                "art": ("badge", "double_o"), "tags": [], "body": body})
    for combo, res in sorted(FUSER_RECIPES.items(), key=lambda kv: kv[1]["name"]):
        a = " + ".join(sorted(combo))
        cost = next((c["cost"] for c in FUSER_SHOP_CHARS if c["name"] == res["name"]), None)
        ch = next((c for c in CHARACTERS if c["name"] == res["name"]), None)
        pct = int(round(res.get("fail_chance", 0) * 100))
        out.append({
            "section": "fuser", "title": res["name"],
            "subtitle": a, "color": ch["color"] if ch else (200, 140, 255),
            "art": ("fighter", res["name"]) if ch else None,
            "tags": ["owned"] if res["name"] in unlocked else [],
            "owned": res["name"] in unlocked,
            "body": [("h", "Recipe"),
                     ("kv", "Elements", a),
                     ("kv", "Cost", f"{cost} coins" if cost else "—"),
                     ("kv", "Fail chance", f"{pct}%"),
                     ("h", "Abilities")] +
                    [("b", x) for x in (abilities_of(ch) if ch else [])],
        })
    return out


def _element_pages(unlocked):
    """The matchup chart, and a page for each element in it."""
    out = []
    _beaten_by = {e: [a for a in ELEMENT_ORDER
                      if e in ELEMENT_BEATS.get(a, ())] for e in ELEMENT_ORDER}
    _who = {e: [] for e in ELEMENT_ORDER}
    for ch in CHARACTERS:
        if ch.get("costume_variant"):
            continue          # a costume fights as whatever is under it
        for e in elements_of(ch):
            _who[e].append(ch["name"])

    _up = int(round((ELEMENT_BONUS - 1) * 100))
    _dn = int(round((1 - ELEMENT_PENALTY) * 100))
    body = ["What a fighter is made of changes what his hits are worth. "
            f"Land one on something your element beats and it does {_up}% "
            f"more; land it on something that beats you and it does {_dn}% "
            "less. It counts for punches, kicks and anything thrown.",
            "Fire burns plant, plant drinks water, water puts fire out — and "
            "round it goes. Fire melts ice as well, water rots poison, poison "
            "kills what grows, and electricity runs through water and through "
            "anything green.",
            ("h", "Who beats whom")]
    for e in ELEMENT_ORDER:
        _b = ELEMENT_BEATS.get(e, ())
        body.append(("kv", ELEMENT_LABEL[e],
                     ", ".join(ELEMENT_LABEL[x] for x in _b) if _b
                     else "nothing — even against everything"))
    body += [("h", "Where an element comes from"),
             "Most fighters get theirs from their kin — a pyrokin is fire, a "
             "cryokin is ice, a venomskin is poison. Plant, air and rock "
             "belong to nobody, so the only way to meet one is to fuse it. A "
             "fused fighter carries both of the elements he was made from, "
             "and can hold the advantage and be on the wrong end of it at the "
             "same time — when that happens the two cancel and it is an even "
             "fight.",
             "A costume fights as whatever is underneath it."]
    out.append({"section": "characters", "title": "Elemental advantages",
                "subtitle": "what beats what, and by how much",
                "color": (236, 92, 44), "art": ("badge", "double_o"),
                "tags": [], "body": body})

    for e in ELEMENT_ORDER:
        _b  = [ELEMENT_LABEL[x] for x in ELEMENT_BEATS.get(e, ())]
        _bb = [ELEMENT_LABEL[x] for x in _beaten_by[e]]
        _kin = ELEMENT_KIN.get(e)
        ebody = [("h", "Matchups"),
                 ("kv", "Strong against", ", ".join(_b) if _b else "nothing"),
                 ("kv", "Weak against",   ", ".join(_bb) if _bb else "nothing"),
                 ("kv", "Worth", f"+{_up}% dealing, -{_dn}% taking")]
        if _kin:
            ebody += [("h", "The kin"),
                      f"Fighters who carry it are the "
                      f"{CATEGORY_LABEL.get(_kin, _kin)}.",
                      ("h", "What marks one")]
            ebody += [("b", ABILITY_NAMES.get(fl, fl.replace("_", " ").capitalize()))
                      for fl in ELEMENT_FLAGS.get(e, ())]
        else:
            ebody += [("h", "The kin"),
                      "Nobody wears this one. It only turns up on a fused "
                      "fighter, out of the element you bought to make him."]
        _mine = sorted(_who[e])
        ebody += [("h", f"Who is made of it ({len(_mine)})")]
        ebody += [("b", n + ("" if n in unlocked else "  — locked"))
                  for n in _mine[:40]]
        if len(_mine) > 40:
            ebody.append(f"...and {len(_mine) - 40} more.")
        out.append({"section": "characters", "title": ELEMENT_LABEL[e],
                    "subtitle": "element", "color": ELEMENT_COLOR[e],
                    "art": ("swatch", ELEMENT_COLOR[e]),
                    "tags": [], "body": ebody})
    return out


def _powerup_pages(unlocked):
    out = []
    for p in POWERUPS:
        secs = p.get("duration", 0) / 60.0
        body = [f"Floats in during a match. Walk into it and it is yours."]
        body.append(("h", "Numbers"))
        body.append(("kv", "Effect", p.get("type", "?").replace("_", " ")))
        if p.get("mult") is not None:
            body.append(("kv", "Strength", f"x{p['mult']}"))
        if p.get("amount") is not None:
            body.append(("kv", "Amount", str(p["amount"])))
        if p.get("reduction") is not None:
            body.append(("kv", "Reduction", f"x{p['reduction']}"))
        body.append(("kv", "Lasts", f"{secs:.0f} seconds" if secs else "instant"))
        out.append({"section": "powerups", "title": p["name"],
                    "subtitle": p.get("type", "").replace("_", " "),
                    "color": p.get("color", (255, 150, 80)),
                    "art": ("swatch", p.get("color", (255, 150, 80))),
                    "tags": [], "body": body})
    return out


def _achievement_pages(unlocked, stats):
    have = set(_ach.earned(stats or {}))
    out = []
    for a in _ach.ACHIEVEMENTS:
        got = a["id"] in have
        body = []            # the description is already the subtitle
        reward = _ach.reward_text(a)
        if reward:
            body.append(("h", "Reward"))
            body.append(("kv", "You get", reward))
        if a.get("unlock"):
            body.append(("kv", "Costume", a["unlock"]))
        body.append(("h", "Status"))
        body.append("Earned." if got else "Not earned yet.")
        out.append({"section": "achievements", "title": a["name"],
                    "subtitle": a["desc"], "color": (255, 206, 70),
                    "art": ("badge", a["badge"]),
                    "tags": ["earned"] if got else [], "owned": got, "body": body})
    return out


# ── Written pages ───────────────────────────────────────────────────────────
# Append to this list to add a page. Nothing else needs to change.
PAGES = [
    {"section": "lore", "title": "The Last Dessert",
     "subtitle": "the night the Seasonals were still one thing",
     "color": (214, 196, 160),
     "body": [
         "There was a time before the majors and the minors. They were all "
         "just Seasonals then, nineteen of them, and the Sea o' Seasons was "
         "one sea with one crossing and nobody had to pick a side of it.",
         "A Seasonal is only ever awake for his own week. Nian wakes in "
         "January and is gone before Smoochie opens her eyes; Saint Nix has "
         "never once met Solara. This is the night the calendar folded over "
         "on itself and put the whole year in one room. It happened once. It "
         "has not happened since, and after what came of it nobody has tried.",
         ("photo", "last-dessert.jpg"),
         ("h", "Why it is called that"),
         "Because of what was at the middle of the table. Nobody ate him. "
         "That was rather the point of the evening.",
         ("h", "Birthalomeu, twice"),
         "He is at the middle of the table — two tiers, two candles, both "
         "arms out along the cloth — and he is above the middle arch as well, "
         "far bigger, reaching down over the hall with both hands. Seasonals "
         "do not agree on which of the two is the real one. The ones who were "
         "there say that is the wrong question.",
         ("h", "The ceiling is the dead"),
         "The vaults are crowded with minor Seasonals and not one of them "
         "was in the room. They are the ones who did not come back from the "
         "Great War, and the Great War came long after this night. Whoever "
         "drew the dessert drew it from memory, years late, and put the dead "
         "up where the ceiling was — so the picture shows a dinner that "
         "happened and a crowd that could not have been watching it.",
         "Most of them are a shape and nothing else by now. Five can still "
         "be put a name to.",
         ("b", "Pi Day — the twenty-second of July, and a pie"),
         ("b", "Diwali — he lit the lamps along the whole vault"),
         ("b", "Twin Day — the two of them count as one week"),
         ("b", "Volcanis — both hammers, still up"),
         ("b", "Umbra — she is nearest the corner, where the light stops"),
         "One of the nameless ones is saying something. It has been copied "
         "out four times and read four different ways, and the only thing "
         "anyone agrees on is that it was not a toast.",
         ("h", "Two of them you can still fight"),
         "The dead stay on the ceiling except when the sky goes out. "
         "Volcanis comes down when the stars line up for a solar eclipse. "
         "Umbra comes down when the moon goes dark, and she comes down for "
         "nothing else. Pi Day, Diwali and Twin Day have no door like that "
         "and have never used one.",
         ("h", "The writing on the piers"),
         "SICKMAN is cut into the left-hand pier and SOFTBALL into the right. "
         "Neither was there when the table was laid.",
         "The stone at the right end reads LOV. The rest of the word is "
         "missing. Tombstone has never said whether it wore away or whether "
         "somebody stopped carving.",
         ("h", "What came of it"),
         "He-Who-Shall-Not-Be-Named murdered Birthalomeu. The Great War "
         "started more or less the moment the news did, and it was fought "
         "everywhere there was ground to fight on.",
         "He did not see much of it. Nian is the oldest of them — the first "
         "week of the year, before anybody else is awake — and Nian found "
         "him and killed him early. You cannot fight him. Nobody can. That "
         "is what being the oldest is for.",
         ("h", "What is left of it"),
         "One picture, in pencil, drawn from memory by somebody who was at "
         "the table and will not say which one he was. The ceiling gives him "
         "away a little: you have to have seen the war to know who to put up "
         "there.",
     ]},
    {"section": "lore", "title": "The eighteen apostles",
     "subtitle": "who sat where, and what it cost them",
     "color": (238, 198, 120),
     "body": [
         "Seating tells you how it ended. Seven down one side, seven down the "
         "other, and the line between them is the line the Seasonals tore "
         "along.",
         "Seven a side is all that was left of them. There were more minors "
         "than that once — the ceiling is full of the rest — but the Great "
         "War came after the split and it went hardest on the small weeks.",
         ("dessert",),
         ("h", "Seven on his left — the majors"),
         "They took the west route through the Sea o' Seasons and they have "
         "held it ever since. Big weeks, full shelves, the events everybody "
         "plans around.",
         ("b", "Nian — New Dynasties"),
         ("b", "Smoochie — Hearts and Harmonies"),
         ("b", "Baddit — April Rain"),
         ("b", "Stickman of Liberty — Red White and Boom"),
         ("b", "Jack O' Slash — Echoes of the Undying"),
         ("b", "Cornucopia — Feasterween"),
         ("b", "Saint Nix — Yuletide Gatherings"),
         ("h", "Seven on his right — the minors"),
         "They did not get the west. They got the long way round and a week "
         "each that most of the world sleeps through.",
         ("b", "Clover — Emerald Echoes"),
         ("b", "Eartha — Bound to the Ground"),
         ("b", "Tombstone — Legacy of Valor"),
         ("b", "Solara — Summer Solstice"),
         ("b", "Bookzworm — Novel Beginnings"),
         ("b", "Yellowstone — Project Yellowstone"),
         ("b", "Nun-Gimel-Hei-Shin — Aura of Menorah"),
         "These seven are the ones who came through the war. Look up at the "
         "ceiling for the ones who did not: Pi Day, Diwali, Twin Day, "
         "Volcanis and Umbra are still recognisable up there, and the "
         "rest have worn down to a shape and a pair of arms.",
         ("h", "One at each far end"),
         "These two never belonged to a shelf and never picked a side. They "
         "hold a single square of the calendar instead, and when it comes "
         "round they take it.",
         ("b", "Amberk — the 11th of July, and old bones"),
         ("b", "Crystallion — the 29th of February, once in four years"),
         ("h", "The two beside him"),
         "Birthalomeu had one on each hand and neither of them left the "
         "table the way they sat down at it.",
         ("b", "Holi, on his right — arms up, still throwing the colour. He "
               "had the shortest week of all of them and he lost it that "
               "night. There is no Holi in the year now and nobody to pick."),
         ("b", "On his left — He-Who-Shall-Not-Be-Named, leaning back out "
               "of the light with the purse under his arm. He is the reason "
               "there are majors and minors, and before the year was out he "
               "was the reason there is no Birthalomeu. Nian killed him for "
               "it. Every Seasonal who was at that table agreed his name "
               "should go nowhere, and it did not."),
         ("h", "And one under it"),
         "Red Herring spent the whole evening under the table and was still "
         "there when it was over, which is how anyone knows what was said. "
         "He is one of three who came through the Great War with a name "
         "still attached — the others being Tombstone, who was at the table, "
         "and Kirin Adler, who was not.",
     ]},
    {"section": "lore", "title": "The Great War",
     "subtitle": "what the dessert turned into",
     "color": (196, 110, 96),
     "body": [
         "He-Who-Shall-Not-Be-Named murdered Birthalomeu, and the world went "
         "to war over it. Not one battle in one place — every stage, every "
         "sea, every ring of ground a tribe holds. The map in the Maps "
         "section is a list of where it happened.",
         ("h", "He was not in it"),
         "Nian got to him first. The oldest Seasonal, the first week of the "
         "year, awake before anybody else — he found the one with the purse "
         "and finished it before the fighting properly started. There is no "
         "He-Who-Shall-Not-Be-Named to fight. There is a hole where he was "
         "and a war that happened anyway.",
         ("h", "Who it killed"),
         "The minor Seasonals, mostly. They had the smallest weeks and the "
         "fewest to call on, and there were a great many more of them before "
         "the war than the seven who are left. The rest are on the ceiling "
         "of the dessert, painted in by somebody who had seen them.",
         ("b", "Pi Day"),
         ("b", "Diwali"),
         ("b", "Twin Day"),
         ("b", "Volcanis"),
         ("b", "Umbra"),
         "Those five you can still put a name to. The others on the vaults "
         "have worn down to a shape and a pair of arms.",
         ("h", "Who came through it"),
         "Three are known by name.",
         ("kv", "Tombstone", "was at the dessert, down the minor side"),
         ("kv", "Red Herring", "was at the dessert, under the table"),
         ("kv", "Kirin Adler", "was not at the dessert at all"),
         ("h", "The two who come back"),
         "The dead stay dead except when the sky goes out. Volcanis comes "
         "down when the stars line up for a solar eclipse. Umbra comes down "
         "when the moon goes dark, and she comes down for nothing else. "
         "Nobody has worked out why those two and not the rest.",
         ("h", "What it settled"),
         "Nothing anybody wanted. The Seasonals were already majors and "
         "minors by then — that split happened at the table. What the war "
         "did was decide how many of each there would be.",
     ]},
    {"section": "basics", "title": "Controls",
     "subtitle": "what every key does",
     "body": [
         "Two players share one keyboard. Player 1 lives on the left of it, "
         "player 2 on the right.",
         ("h", "Player 1"),
         ("kv", "Move", "A / D"),
         ("kv", "Jump", "W"),
         ("kv", "Duck", "S"),
         ("kv", "Punch", "F"),
         ("kv", "Kick", "G"),
         ("kv", "Block", "R"),
         ("h", "Player 2"),
         ("kv", "Move", "Left / Right"),
         ("kv", "Jump", "Up"),
         ("kv", "Duck", "Down"),
         ("kv", "Punch", "K"),
         ("kv", "Kick", "L"),
         ("kv", "Block", "O"),
         ("h", "Everywhere else"),
         ("kv", "Achievements", "V on the home screen"),
         ("kv", "Wiki", "B on the home screen"),
         ("kv", "Touch controls", "T on the home screen"),
         ("kv", "Back out", "ESC"),
     ]},
    {"section": "basics", "title": "Winning a fight",
     "subtitle": "health, blocking, and the clock",
     "body": [
         "Punches are quick and cheap. Kicks hit harder and leave you open. "
         "Blocking cuts the damage you take — including from projectiles, "
         "which is easy to forget when something is flying at you.",
         ("h", "Things worth knowing"),
         ("b", "Every fighter has his own health, reach and block strength — "
               "the Characters section lists them."),
         ("b", "Ducking goes under most projectiles."),
         ("b", "Some stages suit some fighters. Each map page says who."),
         ("b", "Power-ups drop mid-match. Grabbing one you do not want is "
               "still better than letting the other side have it."),
     ]},
    {"section": "basics", "title": "Unlocking fighters",
     "subtitle": "there are a lot of them",
     "body": [
         "You start with four. The rest arrive as you play: win matches, win "
         "with particular fighters, win on particular maps, survive, lose, "
         "come back from almost nothing. Every character page in this wiki "
         "says exactly what its fighter wants from you.",
         ("h", "The other ways in"),
         ("b", "Seasonal Shop — only open while its event is running."),
         ("b", "The Fuser — elements bought with coins, fused in pairs."),
         ("b", "Achievements — some hand over a costume."),
         ("b", "Secrets. Some fighters are not unlocked at all. They are found."),
     ]},
    {"section": "characters", "title": "Taxonomy", "pin": True,
     "subtitle": "how the roster is grouped — every fighter is one of these",
     "tags": ["taxonomy", "tree", "families", "kins", "clans"],
     "body": [
         "Four hundred and thirty-odd fighters sounds like chaos until you "
         "notice they all fall into a handful of families. This is the whole "
         "roster, sorted by what a fighter actually is.",
         ("tree", [
             (0, "Characters"),
             (1, "Seasonal — no way in but the shop window"),
             (2, "Major — out of one of the seven big events"),
             (2, "Minor — out of one of the seven small ones"),
             (2, "Variants — a second form of one you own, and nothing else"),
             (1, "Clans — earned the same hard way, one after another"),
             (2, "Snake clan — killing snakes in the Jungle"),
             (2, "Bug clan — killing bugs in the Computer"),
             (2, "Unhittables — blocking projectiles"),
             (2, "Ghost clan — banishing ghost snakes in the Graveyard"),
             (1, "No ability — the fighting is all there is"),
             (2, "Default — the four you start with"),
             (2, "Other"),
             (1, "Abilitizers — the ones with a trick"),
             (2, "Copycats — they use yours"),
             (2, "Shooters — for the ones with nothing else to them"),
             (3, "Gunners — a steady stream"),
             (3, "Explosers — one loud one"),
             (2, "Elementals"),
             (3, "Pyrokin — fire"),
             (3, "Hydrakin — liquid"),
             (4, "Fishikin — water"),
             (4, "Cryokin — ice"),
             (3, "Shockkin — lightning"),
             (3, "Venomskin — poison"),
             (3, "Jokkin — confusion"),
             (3, "Hammerhead — impact"),
             (1, "Fuser — made, not found, and nothing else besides"),
             (1, "Cipher — typed in, not won"),
             (1, "Secret — hidden until somebody finds it, and nothing else"),
             (1, "Masters — earned by having found enough secrets"),
         ]),
         ("h", "The colours"),
         "Every fighter in this wiki carries its family as a stripe beside its "
         "name, and the same colours again at the top of its page. A fighter "
         "in two families is striped half and half; in three, thirds. The "
         "fused ones are the exception: whatever went into them, they come "
         "out one colour.",
         ] + [("cats", [_c[0]]) for _c in CATEGORIES] + [
         ("h", "Where the edges blur"),
         ("b", "A fighter can sit in two families at once. A seasonal "
               "elemental is still an elemental, and wears both."),
         ("b", "Secret and master beat everything too, and they are not the "
               "same thing. A secret is hidden until somebody finds it; a "
               "master is what finding enough of them earns you."),
         ("b", "Major and minor belong to the event, not the fighter. The "
               "minor seven are Emerald Echoes, Bound to the Ground, Legacy "
               "of Valor, Summer Solstice, Novel Beginnings, Project "
               "Yellowstone and Aura of Menorah; everyone out of them is "
               "minor, and everyone out of the other seven is major."),
         ("b", "Elementals who answer to every element are their own small "
               "club — elemental-all."),
         ("b", "A seasonal is one you cannot get any other way. A fighter "
               "who sits on a seasonal shelf and can also be won on a map is "
               "not a seasonal — he is just also for sale."),
         ("b", "A variant beats everything. Whatever the fighter underneath "
               "can do, a second form of him is a variant and only that."),
         ("b", "The Fuser beats everything. Two elements go in and something "
               "that is neither comes out, so a fused fighter is only ever a "
               "Fuser — never half of what it was made from."),
         ("b", "A kin beats a firing pattern. Somebody who throws fire is a "
               "pyrokin, not a gunner who happens to be warm — so shooters "
               "are only the ones with no element to them at all."),
         ("b", "A clan is not a thing a fighter can do — it is what you had "
               "to do to earn him. Six snakes killed in the Jungle, six bugs "
               "killed in the Computer, seven for blocking projectiles, each "
               "one asking more than the last."),
         ("b", "Ghost clan turned out to be real after all. It is earned in "
               "the Haunted Graveyard, by banishing the flying ghost snakes "
               "that come out of it — ten of them for the first, five hundred "
               "for the last."),
         ("h", "Why it matters"),
         "Mostly it does not — nothing in the game checks these. It is how "
         "to think about a roster this size, and how to guess what a fighter "
         "you have never seen is going to do to you.",
     ]},
    {"section": "modes", "title": "Story Mode",
     "subtitle": "the attack on Wombrock Town — Sundays only",
     "color": (196, 110, 96),
     "body": [
         "Wombrocks have been coming over the ridge into Tombstone for a "
         "while now. Tombstone sent two people to ask you about it — a "
         "tombstone called Tombstone, and a black and white lunatic — which "
         "is Legacy Jawke, the old sketch of him, top hat and all.",
         "They were not asking you to defend anything. They were asking you "
         "to go east and hit the Wombrocks back at home.",
         ("h", "Sundays"),
         "The card is chained shut six days a week and Tombstone is behind "
         "the chain, as he has always been. On a Sunday the chain comes off "
         "and the mode opens. Yank the padlock on any other day and you get "
         "him instead, which is its own kind of answer.",
         ("h", "Where it happens"),
         ("kv", "Wombrock Town", "east side of the world map, and now a stage"),
         "Rooftops to fight across — the low roof by the gate, the hall with "
         "half of it gone, the watch post, and the bell tower walkway over "
         "the top of the lot. The sky is the colour of the smoke and the "
         "street is mostly rubble.",
         ("h", "How it plays"),
         "A map is a yard with things in it, not a duel. You do not pick "
         "your fighter — you are the one Tombstone sent for, which means "
         "you are the Brawler, and the yard is drawn around you at the "
         "size the map was drawn at.",
         ("b", "Beat the boss and the map is yours. The door is not the "
               "win — it is a house, and a house has an inside"),
         ("b", "R on the loss screen puts you straight back in"),
         ("b", "Cleared maps stay open, so any of them can be walked again"),
         ("b", "The story lends you fighters you have not unlocked"),
         ("h", "What is in a yard"),
         ("kv", "Wombrocks", "80 health, hits for 10, speed 6 — headstones "
                              "that grew a mouth and got up. They come "
                              "after you and they never stop. They are only "
                              "slow"),
         ("kv", "Skeletons", "60 health, hits for 8 — up out of the ground "
                             "by the coffin, and that is where they stay"),
         ("kv", "Floaters", "40 health, hits for 9 — strung on a wire, end "
                            "to end for ever, and they do not care where "
                            "you are"),
         ("kv", "The wolf", "100 health, hits for 14, speed 8, and goes "
                            "completely invisible every four seconds. Beat "
                            "it and the map is yours"),
         ("kv", "Portals, springs", "the way up and the way across"),
         ("kv", "A coffin", "put both skeletons down and it opens. 25 coins"),
         ("h", "What it pays"),
         "Tombstone came to ask you for a favour and he is good for it — "
         "250 coins at the end of the road.",
     ]},
    {"section": "modes", "title": "1 Player",
     "subtitle": "versus the computer",
     "body": ["Pick a fighter, pick a map, fight the computer. The difficulty "
              "picker on the card changes how hard it reads you — and how much "
              "unlocking it is worth.",
              ("h", "Note"), "Most unlock conditions count wins here."]},
    {"section": "modes", "title": "2 Players",
     "subtitle": "one keyboard, two people",
     "body": ["Both players on the same keyboard. Both halves of the character "
              "select are live at once, so pick at the same time; READY locks "
              "a choice in."]},
    {"section": "modes", "title": "Survival",
     "subtitle": "they keep coming",
     "body": ["One fighter against an endless queue of them, one or two players. "
              "Your health carries between opponents, so the fight you win "
              "badly is the one that kills you three fights later.",
              ("h", "Worth knowing"),
              ("b", "Survival kills unlock a long list of fighters."),
              ("b", "Lasting two minutes is an achievement of its own.")]},
    {"section": "modes", "title": "Online",
     "subtitle": "against a real person",
     "body": ["Both sides run the same fight and trade inputs every frame; the "
              "host's copy is the one that counts. Matchmaking pairs you with "
              "whoever else is waiting.",
              ("h", "Worth knowing"),
              ("b", "Not every map is in the online rotation — seasonal and "
                    "special-mode stages sit it out."),
              ("b", "R rematches, C goes back to the character select."),
              ("b", "Wins here go on the leaderboard.")]},
    {"section": "modes", "title": "The Seasonal Shop",
     "subtitle": "coins in, fighters out",
     "body": ["Open during an event. Coins come from playing, from achievements, "
              "and from the odd lucky match. What is on the shelf depends on "
              "the date — see the Events section for every roster.",
              ("h", "Worth knowing"),
              "Owning every fighter in an event's shop puts that event's "
              "costume on the costume rack. It does not give it to you."]},
    {"section": "modes", "title": "The Costume Rack",
     "subtitle": "its own box on the home screen",
     "body": ["A rail on castors with every costume in the game hanging off "
              "it. Left and right slide it along; enter buys whatever is in "
              "front of you. There is also a door to it round the back of the "
              "Seasonal Shop.",
              ("h", "Only what is for sale"),
              "The costumes you earn by owning every fighter of an event are "
              "not stock. They go straight into their fighter's box and never "
              "hang here at all.",
              ("h", "Stars set the price"),
              "Every costume carries a rating out of five. Press 1 to 5 while "
              "it is in front of you, or click the stars. Five stars puts "
              "thirty per cent on the ticket price; one star takes thirty per "
              "cent off.",
              ("h", "Worth knowing"),
              ("b", "The rack is open whether or not an event is running."),
              ("b", "A costume is its fighter's whole kit in new colours — "
                    "nothing it can do changes."),
              ("b", "A bought costume says WORN, and you pick it from its "
                    "fighter's own box on the character select with Q/E "
                    "or J/L."),
              ("b", "Legacy Tombstone and Legacy Jawke are not on the rack. "
                    "They live in their owners' boxes already.")]},
    {"section": "modes", "title": "Special modes",
     "subtitle": "one week only",
     "body": ["Some events bring a mode with them, playable only while the "
              "event runs. They have their own rosters, their own stages and "
              "their own rewards — The Crooking Glass at Hallowe'en hands out "
              "Jack O' Slash at one in a hundred and Broken Jak 0' Lash at one "
              "in a thousand.",
              ("h", "Rewards"),
              "Special-mode rewards roll every tenth win, not every win — ten "
              "wins buys you one roll, and the roll is still mostly nothing.",
              ("h", "Costumes"),
              "You cannot wear one in here. A special mode hands you its own "
              "roster and you fight as the fighter, not as a coat."]},
    {"section": "lore", "title": "About this wiki",
     "subtitle": "and how to add to it",
     "body": [
         "Most of what you are reading was not written by hand. The character, "
         "map, event, costume, power-up and achievement pages are built from "
         "the game's own tables every time you open the wiki, so they cannot go "
         "stale — a fighter added to the game is a page added here.",
         ("h", "Adding a page"),
         "Pages like this one are written by people, and you can write one "
         "without leaving the game: press F2 in here, or the WRITE button at "
         "the bottom. Give it a title, pick a section, type. F3 edits a page "
         "somebody wrote, and DELETE throws it away.",
         "F3 also works on the pages the game generates. You cannot change "
         "what Brawler's health is, but you can write underneath it — your "
         "notes land at the bottom of his page and stay there.",
         "What it saves is an ordinary text file in the wiki/ folder next to "
         "the game, so a page written here opens in any text editor, and a "
         "file dropped into that folder shows up here the next time the game "
         "starts. wiki/README.txt has the format, which is about six lines "
         "long.",
         ("h", "What is worth writing"),
         ("b", "Tactics. The generated pages know the numbers, not what to do "
               "with them — which is exactly what F3 on a fighter's page is "
               "for."),
         ("b", "History. Why a fighter exists, who asked for him."),
         ("b", "Secrets you are willing to give away. The generated pages "
               "will not — a fighter the game hides behind \"???\" is hidden "
               "here too, until you have found him."),
     ]},
]


# ── Pages dropped in the wiki/ folder ───────────────────────────────────────
def _parse_page(text, fallback_title):
    """Turn one wiki/*.txt file into a page. See wiki/README.txt."""
    head, body_lines = {}, []
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^(section|title|subtitle|color|tags|attach|author)\s*:\s*(.*)$",
                     lines[i].strip(), re.I)
        if not m:
            break
        head[m.group(1).lower()] = m.group(2).strip()
        i += 1
    para = []
    for raw in lines[i:]:
        line = raw.rstrip()
        if not line.strip():
            if para:
                body_lines.append(" ".join(para)); para = []
            continue
        if line.startswith("## "):
            if para:
                body_lines.append(" ".join(para)); para = []
            body_lines.append(("h", line[3:].strip()))
        elif line.startswith("- "):
            if para:
                body_lines.append(" ".join(para)); para = []
            body_lines.append(("b", line[2:].strip()))
        elif " = " in line and not line.startswith(" "):
            if para:
                body_lines.append(" ".join(para)); para = []
            k, v = line.split(" = ", 1)
            body_lines.append(("kv", k.strip(), v.strip()))
        else:
            para.append(line.strip())
    if para:
        body_lines.append(" ".join(para))
    col = (225, 228, 240)
    if head.get("color"):
        try:
            parts = [int(x) for x in head["color"].replace(",", " ").split()]
            if len(parts) == 3:
                col = tuple(max(0, min(255, p)) for p in parts)
        except ValueError:
            pass
    # "attach: characters/Brawler" means this is a note written onto a page
    # the game generates, not a page of its own.
    attach = None
    if head.get("attach"):
        _a_sec, _, _a_title = head["attach"].partition("/")
        if _a_title.strip():
            attach = (_a_sec.strip().lower(), _a_title.strip())
            head.setdefault("section", attach[0])
            head.setdefault("title", attach[1])
    return {"raw": text, "attach": attach,
            "author": head.get("author", "").strip(),
            "section": (head.get("section") or "lore").lower().strip(),
            "title": head.get("title") or fallback_title,
            "subtitle": head.get("subtitle", ""), "color": col,
            "art": None, "contributed": True,
            "tags": [t.strip() for t in head.get("tags", "").split(",") if t.strip()],
            "body": body_lines}


def folder_pages():
    """Every .txt page a person has dropped into wiki/. Never raises."""
    out = []
    try:
        names = sorted(os.listdir(WIKI_DIR))
    except OSError:
        return out
    for fn in names:
        if not fn.lower().endswith(".txt") or fn.lower() == "readme.txt":
            continue
        try:
            with open(os.path.join(WIKI_DIR, fn), encoding="utf-8") as fh:
                    _pg = _parse_page(fh.read(), os.path.splitext(fn)[0])
            _pg["file"] = fn
            out.append(_pg)
        except Exception:
            continue          # a bad page must never keep the wiki shut
    return out


# ── Writing pages from inside the game ──────────────────────────────────────
def _slug(title):
    out = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out[:48] or "page"


def compose(section, title, subtitle, body_text, attach=None, author=""):
    """The text of a page file, exactly as a person would have typed it."""
    if attach:
        head = [f"attach: {attach[0]}/{attach[1]}"]
    else:
        head = [f"section: {section}", f"title: {title}"]
        if subtitle.strip():
            head.append(f"subtitle: {subtitle.strip()}")
    if author.strip():
        head.append(f"author: {author.strip()}")
    return "\n".join(head) + "\n\n" + body_text.rstrip() + "\n"


def note_filename(section, title):
    """Where a note on a generated page lives."""
    return f"note-{_slug(section)}-{_slug(title)}.txt"


def find_note(section, title):
    """The note already written on a page, if there is one."""
    fn = note_filename(section, title)
    return fn if os.path.exists(os.path.join(WIKI_DIR, fn)) else None


def save_page(section, title, subtitle, body_text, filename=None, attach=None,
              author=""):
    """Write a page into wiki/. Returns its filename, or None if it failed.

    Pages written in game are ordinary files in the same folder people drop
    theirs into — nothing about them is special, and they can be opened in a
    text editor afterwards.
    """
    try:
        os.makedirs(WIKI_DIR, exist_ok=True)
        if attach and not filename:
            filename = note_filename(*attach)
        if not filename:
            base = _slug(title)
            filename = base + ".txt"
            _i = 2
            while os.path.exists(os.path.join(WIKI_DIR, filename)):
                filename = f"{base}-{_i}.txt"
                _i += 1
        with open(os.path.join(WIKI_DIR, filename), "w", encoding="utf-8") as fh:
            fh.write(compose(section, title, subtitle, body_text, attach, author))
        return filename
    except Exception:
        return None


def delete_page(filename):
    try:
        os.remove(os.path.join(WIKI_DIR, filename))
        return True
    except Exception:
        return False


def body_source(page):
    """The body of a written page, back as editable text."""
    if page.get("raw"):
        lines = page["raw"].replace("\r\n", "\n").split("\n")
        i = 0
        while i < len(lines) and re.match(
                r"^(section|title|subtitle|color|tags|attach|author)\s*:",
                lines[i].strip(), re.I):
            i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        return "\n".join(lines[i:]).rstrip()
    out = []
    for item in page.get("body", []):
        if isinstance(item, str):
            out.append(item)
        elif item[0] == "h":
            out.append("## " + item[1])
        elif item[0] == "b":
            out.append("- " + item[1])
        elif item[0] == "kv":
            out.append(f"{item[1]} = {item[2]}")
        out.append("")
    return "\n".join(out).rstrip()


# ── Putting it together ─────────────────────────────────────────────────────
def _haystack(p):
    bits = [p.get("title", ""), p.get("subtitle", "")] + list(p.get("tags", []))
    for item in p.get("body", []):
        if isinstance(item, str):
            bits.append(item)
        elif item[0] == "tree":
            bits += [t for _d, t in item[1]]
        elif item[0] == "cats":
            bits += [CATEGORY_LABEL.get(c, c) for c in item[1]]
        else:
            bits.append(" ".join(str(x) for x in item[1:]))
    return " ".join(bits).lower()


def build(unlocked=(), stats=None):
    """The whole wiki, as {section id: [pages]}, in the order SECTIONS lists."""
    unlocked = set(unlocked or ())
    pages = []
    pages += _character_pages(unlocked)
    pages += _map_pages(unlocked)
    pages += _world_pages(unlocked)
    pages += _event_pages(unlocked)
    pages += _costume_pages(unlocked)
    pages += _element_pages(unlocked)
    pages += _fuser_pages(unlocked)
    pages += _powerup_pages(unlocked)
    pages += _achievement_pages(unlocked, stats)
    pages += [dict(p) for p in PAGES]
    pages += folder_pages()

    out = {s["id"]: [] for s in SECTIONS}
    # Maps keep their map order and events their calendar order, but five
    # hundred fighters in the order they happened to be written is a list
    # nobody can find anything in. Secrets stay together at the end.
    pages.sort(key=lambda _p: (_p.get("section") == "characters"
                               and (_p.get("title") == "???",
                                    _p.get("title", "").lower())) or (0, ""))
    notes = [p for p in pages if p.get("attach")]
    pages = [p for p in pages if not p.get("attach")]
    for p in pages:
        p.setdefault("color", (225, 228, 240))
        p.setdefault("tags", [])
        p.setdefault("art", None)
        p["search"] = _haystack(p)
        out.setdefault(p.get("section", "lore"), []).append(p)
    # A note goes onto the page it names. If that page does not exist — the
    # fighter was renamed, say — it stands on its own rather than vanishing.
    for note in notes:
        sec, title = note["attach"]
        target = next((p for p in out.get(sec, [])
                       if p["title"].lower() == title.lower()), None)
        if target is None:
            note["contributed"] = True
            out.setdefault(sec, []).append(note)
            continue
        _by = note.get("author")
        target["body"] = (list(target["body"])
                          + [("h", f"Notes from {_by}" if _by else "Notes")]
                          + list(note["body"]))
        target["notes_file"] = note.get("file")
        target["notes_author"] = _by
        target["tags"] = list(target.get("tags", [])) + ["has notes"]
        target["search"] = _haystack(target)

    for _sid in out:
        out[_sid].sort(key=lambda p: 0 if p.get("pin") else 1)

    for extra in [k for k in out if k not in SECTION_TITLE]:
        # A page claiming a section nobody declared still gets read.
        SECTIONS.append({"id": extra, "title": extra.title(), "color": (200, 200, 210)})
        SECTION_TITLE[extra] = extra.title()
    return out


def page_count(unlocked=(), stats=None):
    return sum(len(v) for v in build(unlocked, stats).values())
