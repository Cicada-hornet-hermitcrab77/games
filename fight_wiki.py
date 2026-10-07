"""The Stickman Fight Wiki — the in-game reference everything else feeds.

The wiki has two halves.

THE GENERATED HALF reads the game's own tables. Every character, map, event,
costume, power-up, fuser recipe and achievement in here is built from
fight_data / fight_seasonal / fight_game at the moment you open it, so it can
never drift out of date. Add a character to CHARACTERS and its page is already
written.

THE WRITTEN HALF is for pages a person writes — history, tactics, lore, jokes.
There are two ways to add one, and neither touches any other file:

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
("h", heading), ("b", bullet), ("kv", key, value) and ("bar", label, n, max).
"""
import os
import re

from fight_data import (CHARACTERS, STAGES, STAGE_MATCHUPS, POWERUPS,
                        FUSER_ELEMENTS, FUSER_RECIPES, FUSER_SHOP_CHARS,
                        COSTUMES)
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
    {"id": "lore",         "title": "Lore",         "color": (175, 165, 205)},
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
    "ascii_fighter": "Made of text",      "f13_dmg": "Friday the 13th damage",
    "prime_dmg": "Prime-number damage",   "seven_punch": "Lucky seven punch",
    "halves_punch": "Halving punch",      "nick_of_time": "Nick of time",
    "soul_master": "Soul master",         "voodoo": "Voodoo",
    "cursed_drain": "Cursed drain",       "siphon_leech": "Siphons life",
    "dementor_heal": "Feeds on fear",     "revenant": "Revenant",
    "shade": "Shade",                     "disorientated": "Disorientated",
    "feedback": "Feedback",               "buffer_char": "Buffering",
    "stillness_regen": "Heals by standing still",
    "desperation_speed": "Faster when hurt",
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


_SEASONAL_BY_NAME = {c["name"]: c for c in SEASONAL_SHOP_CHARS}
_FUSER_BY_NAME    = {c["name"]: c for c in FUSER_SHOP_CHARS}
_COSTUME_BY_NAME  = {c["name"]: c for c in COSTUMES}


def how_to_get(name, conditions, default_set):
    if name in default_set:
        return "Yours from the first match — one of the four you start with"
    if name in _COSTUME_BY_NAME:
        c = _COSTUME_BY_NAME[name]
        return f"Achievement: own every {c['event']} shop character"
    if name in _SEASONAL_BY_NAME:
        c = _SEASONAL_BY_NAME[name]
        return f"Seasonal Shop during {c['event']} — {c['cost']} coins"
    if name in _FUSER_BY_NAME:
        return f"The Fuser — {_FUSER_BY_NAME[name]['cost']} coins, plus the elements"
    if name in conditions:
        return conditions[name][3]
    base = next((CHARACTERS[i].get("costume_of") for i, c in enumerate(CHARACTERS)
                 if c["name"] == name), None)
    if base:
        return f"Comes with {base} — pick it in his box"
    for key, owner in (("jack_variant", "Jack O' Slash"), ("jawke_variant", "Jawke"),
                       ("tombstone_variant", "Tombstone"), ("clover_variant", "Clover"),
                       ("eartha_variant", "Eartha"), ("solara_variant", "Solara"),
                       ("nghs_variant", "Nun-Gimel-Hei-Shin"),
                       ("bookzworm_variant", "Bookzworm"),
                       ("yellowstone_variant", "Yellowstone")):
        ch = next((c for c in CHARACTERS if c["name"] == name), None)
        if ch and ch.get(key):
            return f"A variant of {owner} — pick it in his box"
    return "Nobody has written this one down yet"


# ── Generated pages ─────────────────────────────────────────────────────────
def _character_pages(unlocked):
    conditions, default_set, _ = _unlock_tables()
    out = []
    for ch in CHARACTERS:
        name = ch["name"]
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
        body.append(("h", "How to get"))
        body.append(how_to_get(name, conditions, default_set))
        liked = [s for s, m in STAGE_MATCHUPS.items() if m.get("adv") == name]
        hated = [s for s, m in STAGE_MATCHUPS.items() if m.get("dis") == name]
        if liked or hated:
            body.append(("h", "Ground he knows"))
            for s in liked:
                body.append(("kv", s, "at home"))
            for s in hated:
                body.append(("kv", s, "out of his depth"))
        out.append({
            "section": "characters", "title": name,
            "subtitle": ch.get("desc", ""), "color": ch["color"],
            "art": ("fighter", name), "tags": tags,
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
                f"and only then."]
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
            "tags": (["complete"] if owned else []) +
                    (["special mode"] if ev.get("special_mode_label") else []),
            "body": body,
        })
    return out


def _costume_pages(unlocked):
    out = []
    for c in COSTUMES:
        out.append({
            "section": "costumes", "title": c["name"],
            "subtitle": f"{c['base']}  ·  {c['event']}",
            "color": c["color"], "art": ("fighter", c["name"]),
            "tags": ["owned"] if c["name"] in unlocked else [],
            "owned": c["name"] in unlocked,
            "body": [f"A {c['event']} coat for {c['base']}. Same fighter "
                     f"underneath — same health, same reach, same tricks — "
                     f"wearing something else.",
                     ("h", "How to get it"),
                     f"Own every {c['event']} shop character. The achievement "
                     f"hands it over the moment the last one is bought.",
                     ("h", "Where to wear it"),
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
              "Buying every fighter in an event's shop earns that event's "
              "costume, permanently."]},
    {"section": "modes", "title": "Special modes",
     "subtitle": "one week only",
     "body": ["Some events bring a mode with them, playable only while the "
              "event runs. They have their own rosters, their own stages and "
              "their own rewards — The Crooking Glass at Hallowe'en hands out "
              "Jack O' Slash at one in a hundred and Broken Jak 0' Lash at one "
              "in a thousand.",
              ("h", "Rewards"),
              "Special-mode rewards roll every tenth win, not every win."]},
    {"section": "lore", "title": "About this wiki",
     "subtitle": "and how to add to it",
     "body": [
         "Most of what you are reading was not written by hand. The character, "
         "map, event, costume, power-up and achievement pages are built from "
         "the game's own tables every time you open the wiki, so they cannot go "
         "stale — a fighter added to the game is a page added here.",
         ("h", "Adding a page"),
         "Pages like this one are written by people. Drop a plain text file "
         "into the wiki/ folder next to the game and it appears here the next "
         "time the game starts. No programming involved — wiki/README.txt has "
         "the format, which is about six lines long.",
         ("h", "What is worth writing"),
         ("b", "Tactics. The generated pages know the numbers, not what to do "
               "with them."),
         ("b", "History. Why a fighter exists, who asked for him."),
         ("b", "Secrets you are willing to give away."),
     ]},
]


# ── Pages dropped in the wiki/ folder ───────────────────────────────────────
def _parse_page(text, fallback_title):
    """Turn one wiki/*.txt file into a page. See wiki/README.txt."""
    head, body_lines = {}, []
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^(section|title|subtitle|color|tags)\s*:\s*(.*)$",
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
    return {"section": (head.get("section") or "lore").lower().strip(),
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
                out.append(_parse_page(fh.read(), os.path.splitext(fn)[0]))
        except Exception:
            continue          # a bad page must never keep the wiki shut
    return out


# ── Putting it together ─────────────────────────────────────────────────────
def _haystack(p):
    bits = [p.get("title", ""), p.get("subtitle", "")] + list(p.get("tags", []))
    for item in p.get("body", []):
        bits.append(item if isinstance(item, str) else " ".join(str(x) for x in item[1:]))
    return " ".join(bits).lower()


def build(unlocked=(), stats=None):
    """The whole wiki, as {section id: [pages]}, in the order SECTIONS lists."""
    unlocked = set(unlocked or ())
    pages = []
    pages += _character_pages(unlocked)
    pages += _map_pages(unlocked)
    pages += _event_pages(unlocked)
    pages += _costume_pages(unlocked)
    pages += _fuser_pages(unlocked)
    pages += _powerup_pages(unlocked)
    pages += _achievement_pages(unlocked, stats)
    pages += [dict(p) for p in PAGES]
    pages += folder_pages()

    out = {s["id"]: [] for s in SECTIONS}
    for p in pages:
        p.setdefault("color", (225, 228, 240))
        p.setdefault("tags", [])
        p.setdefault("art", None)
        p["search"] = _haystack(p)
        out.setdefault(p.get("section", "lore"), []).append(p)
    for extra in [k for k in out if k not in SECTION_TITLE]:
        # A page claiming a section nobody declared still gets read.
        SECTIONS.append({"id": extra, "title": extra.title(), "color": (200, 200, 210)})
        SECTION_TITLE[extra] = extra.title()
    return out


def page_count(unlocked=(), stats=None):
    return sum(len(v) for v in build(unlocked, stats).values())
