"""A compact standing check over everything built so far."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((900, 550))

import fight_data as D
import fight_wiki as W
import fight_achievements as A
import fight_drawing as DR
import fight_game as G
from fight_stage import Platform, ConveyorBelt, SlantedConveyorBelt

CONDS, DEFAULT, _ = W._unlock_tables()
POSES = (("idle", 0.3), ("walk", 0.5), ("punch", 0.5), ("kick", 0.6),
         ("jump", 0.2), ("block", 0.0), ("dead", 1.0))
surf = pygame.Surface((900, 550))

# 1. Every fighter draws, both facings, every pose, two scales
for c in D.CHARACTERS:
    for act, at in POSES:
        for fc in (1, -1):
            DR.draw_stickman(surf, 450, 500, c["color"], fc, act, at, char_name=c["name"])
            DR.draw_stickman(surf, 450, 500, c["color"], fc, act, at, scale=1.8,
                             char_name=c["name"])
print(f"all {len(D.CHARACTERS)} fighters draw in every pose, both facings")

# 2. The five water ones are creatures, not decorated stickmen: their art
#    runs before the skeleton is ever drawn, and returns on its own
WATER = ["Mermaid", "Starfish", "Pufferfish", "Gold Fish", "Octo-Octo"]
src = open("fight_drawing.py").read()
i_water = src.index('if char_name in ("Mermaid", "Starfish", "Pufferfish"')
i_dead = src.index("# ── Dead pose: stickman lying flat on the ground")
i_skel = src.index("    ln(waist, lk); ln(lk, lf)")
assert i_water < i_dead < i_skel, "water art must run before the stickman is drawn"
for n in WATER:
    assert n in D.CHARACTERS_BY_NAME if hasattr(D, "CHARACTERS_BY_NAME") else True
    ch = next(c for c in D.CHARACTERS if c["name"] == n)
    assert ch.get("water_breathing"), n
    # punch and kick must still report where they land
    assert DR.draw_stickman(surf, 450, 500, ch["color"], 1, "punch", 0.5,
                            char_name=n) is not None, n
    assert DR.draw_stickman(surf, 450, 500, ch["color"], 1, "kick", 0.6,
                            char_name=n) is not None, n
    assert DR.draw_stickman(surf, 450, 500, ch["color"], 1, "idle", 0.3,
                            char_name=n) is None, n
print("the five water fighters are drawn as creatures and still land their hits")

# 3. Every costume gets art of its own
plain = []
for c in D.COSTUMES:
    seen = []
    orig = DR.draw_costume_extras
    DR.draw_costume_extras = lambda *a, **k: (seen.append(a[1]), orig(*a, **k))[1]
    try:
        DR.draw_stickman(surf, 450, 500, c["color"], 1, "idle", 0.3, char_name=c["name"])
    finally:
        DR.draw_costume_extras = orig
    if not seen:
        plain.append(c["name"])
assert not plain, plain
print(f"all {len(D.COSTUMES)} costumes have art of their own")

# 4. Costume pricing and the rack
assert len(D.COSTUMES_EARNED) == 14
for c in D.COSTUMES_EARNED:
    assert "cost" not in c and D.costume_price(c, {}) is None, c["name"]
for c in D.COSTUMES_FOR_SALE:
    assert D.costume_price(c, {}) == c["cost"], c["name"]
    hi = D.costume_price(c, {"costume_ratings": {c["name"]: 5}})
    lo = D.costume_price(c, {"costume_ratings": {c["name"]: 1}})
    assert lo < c["cost"] < hi, (c["name"], lo, hi)
print(f"{len(D.COSTUMES_FOR_SALE)} costumes on the rack, each dearer at five stars "
      f"and cheaper at one")

# 5. Every stage builds and every character has a real base
for i, st in enumerate(D.STAGES):
    for key, cls in (("platforms", Platform), ("conveyors", ConveyorBelt),
                     ("slanted_conveyors", SlantedConveyorBelt)):
        for p in st.get(key, []):
            assert isinstance(p, (tuple, list)), (st["name"], key, p)
            cls(*p)
names = {c["name"] for c in D.CHARACTERS}
for c in D.COSTUMES:
    assert c["base"] in names and c["name"] in names, c["name"]
print(f"all {len(D.STAGES)} stages build; every costume's base is a real fighter")

# 6. Achievements still pay out
st, un = {"seasonal_coins": 10, "wins_total": 1}, set()
A.check_achievements(st, un)
assert st["seasonal_coins"] == 15
from fight_seasonal import SEASONAL_SHOP_CHARS
roster = {c["name"] for c in SEASONAL_SHOP_CHARS if c["event"] == "New Dynasties"}
un2 = set(roster)
got = A.check_achievements({}, un2)
assert "Koi-lue" in un2 and got and got[0]["name"] == "Koi-lue"
print(f"{len(A.ACHIEVEMENTS)} achievements: coins pay, earned costumes hand over")

# 7. The wiki builds and covers the roster
w = W.build(unlocked={"Ninja"}, stats={"wins_total": 1})
assert {p["title"] for p in w["characters"] if not p.get("secret")} <= names | {"Taxonomy"}
assert any(p["title"] == "The world" for p in w["maps"])
assert any(p["title"] == "Taxonomy" for p in w["characters"])
for n in WATER:
    p = next(x for x in w["characters"] if x["title"] == n)
    assert p["cats"] == ["fishikin"], (n, p["cats"])
gf = W.ways_to_get("Gold Fish", CONDS, DEFAULT)
assert len(gf) == 2, gf
print(f"wiki: {sum(len(v) for v in w.values())} pages; Gold Fish has "
      f"{len(gf)} ways in")
# 8. The Ice Cave floor cracks, drops away and freezes back
from fight_stage import IceFloorPanel
from constants import GROUND_Y
import constants as _C
CTRL = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w,
        'duck': pygame.K_s, 'punch': pygame.K_f, 'kick': pygame.K_g,
        'block': pygame.K_r}
from fight_fighter import Fighter
_br = next(c for c in D.CHARACTERS if c["name"] == "Brawler")
_keys = [False] * 400
def _mk(x, y):
    _f = Fighter(x, _br, 1, CTRL); _f.y = y; return _f
_ice = next(st for st in D.STAGES if st["name"] == "Ice Cave")
assert not _ice.get("conveyors"), "the ice floor is the floor; no belts on it"
_C.GROUND_HOLES = []
_a, _foe = _mk(400, GROUND_Y - 80), _mk(100, GROUND_Y)
for _ in range(120):
    _a.update(_keys, _foe, [])
assert _a.y == GROUND_Y and _a.hp > 0
_C.GROUND_HOLES = [(350.0, 460.0)]
_b = _mk(400, GROUND_Y - 10)
for _ in range(240):
    _b.update(_keys, _foe, [])
assert _b.hp <= 0, "a hole in the floor has to be a hole"
_c2 = _mk(600, GROUND_Y - 10)
for _ in range(120):
    _c2.update(_keys, _foe, [])
assert _c2.y == GROUND_Y and _c2.hp > 0, "the next slab along still holds"
_C.GROUND_HOLES = []
_p1, _p2 = IceFloorPanel(300, 120), IceFloorPanel(300, 120)
_on, _off = _mk(360, GROUND_Y), _mk(800, GROUND_Y)
for _ in range(60):
    _p1.update((_on,)); _p2.update((_off,))
assert _p1.crack > _p2.crack * 3
_n = 0
while not _p1.fallen and _n < 60 * 40:
    _p1.update((_on,)); _n += 1
assert _p1.fallen
_n2 = 0
while _p1.fallen and _n2 < 60 * 90:
    _p1.update(()); _n2 += 1
assert not _p1.fallen and _p1.crack == 0.0
print(f"Ice Cave: eight slabs, {_n/60:.0f}s under weight, "
      f"{_n2/60:.0f}s to freeze back; a hole is a hole")
_C.GROUND_HOLES = []

# 9. Searching the character select narrows the grid and still returns
#    indices into the real roster
import fight_ui as _UI
pygame.display.flip = lambda: None
def _K(k, u=""):
    return [pygame.event.Event(pygame.KEYDOWN, key=k, unicode=u)]
def _T(txt):
    return [pygame.event.Event(pygame.KEYDOWN, key=0, unicode=ch) for ch in txt]
def _pick(q):
    _it = iter([[], _K(pygame.K_SLASH), _T(q), [], _K(pygame.K_RETURN), [],
                _K(pygame.K_f), []])
    pygame.event.get = lambda *a, **k: next(_it, [])
    return _UI.character_select(vs_ai=True)
for _q, _want in (("mermaid", "Mermaid"), ("octo", "Octo-Octo"),
                  ("arson", "Arsonist"), ("ninja", "Ninja")):
    _p1, _ = _pick(_q)
    assert D.CHARACTERS[_p1]["name"] == _want, (_q, D.CHARACTERS[_p1]["name"])
_p1, _p2 = _pick("zzzzz")
assert 0 <= _p1 < len(D.CHARACTERS) and 0 <= _p2 < len(D.CHARACTERS)
_ui_src = open("fight_ui.py").read()
assert "press  /  to search by name" in _ui_src
print("character select: search narrows the grid, prefix matches first, "
      "and picking still returns the real index")

# 10. "I will fight you with my BEAR hands! Oh deer"
import fight_fighter as _FF
_PB = next(i for i, c in enumerate(D.CHARACTERS) if c["name"] == "Polar Bear")
_WE = next(i for i, c in enumerate(D.CHARACTERS) if c["name"] == "Wendigo")
_BR = next(i for i, c in enumerate(D.CHARACTERS) if c["name"] == "Brawler")

def _bear_fight(a, b, kick=False):
    """Run a real fight, kill the AI off, and see whether it counted."""
    _n = [0]
    pygame.display.flip = lambda: _n.__setitem__(0, _n[0] + 1)
    _orig = _FF.AIFighter.update
    def _drain(self, keys, other, platforms=()):
        if _n[0] > 40:
            self.hp = 0
        if kick and _n[0] == 20:
            G._p1_kick_landed_flag[0] = True
        return _orig(self, keys, other, platforms)
    _FF.AIFighter.update = _drain
    pygame.event.get = lambda *a, **k: (
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)] if _n[0] > 150 else [])
    try:
        G.run_fight(a, b, vs_ai=True, ai_difficulty='easy', stage_idx=0)
    except SystemExit:
        pass
    finally:
        _FF.AIFighter.update = _orig
    return G._bear_hands_flag[0]

assert _bear_fight(_PB, _WE) is True,  "bear beats deer bare-handed: should count"
assert _bear_fight(_PB, _WE, True) is False, "one kick and it should not count"
assert _bear_fight(_PB, _BR) is False, "Brawler is not a deer"
assert _bear_fight(_BR, _WE) is False, "Brawler is not a bear"
_g = open("fight_game.py").read()
assert 'stats["bear_hands_win"] = True' in _g
_ba = A.BY_ID["bear_hands"]
assert _ba["check"]({"bear_hands_win": True}, (), None)
assert not _ba["check"]({}, (), None)
print("bear hands: Polar Bear beating a deer without a single kick, and "
      "nothing else, earns it")

# 11. Took the L — the Feasterween mode
from fight_stage import LoserShirt
import fight_projectiles as _FP
_tl_stage = next(st for st in D.STAGES if st["name"] == "Took the L")
assert _tl_stage.get("special_mode_only")
assert len(_tl_stage["platforms"]) == 7, "three Ls and a shelf"
from fight_seasonal import SEASONAL_EVENTS as _SE
_fw = next(e for e in _SE if e["name"] == "Feasterween")
assert _fw.get("special_mode") == "took_the_l"
_g2 = open("fight_game.py").read()
assert "if mode == 'took_the_l':" in _g2
for _nm in ("Clown", "Hardy", "Impossible", "Mime", "Joker", "Jester",
            "Rage Quitter", "Cornucopia", "Sickman Stickman"):
    assert f'"{_nm}"' in _g2, _nm
assert '_tl_reward = "Sickman Stickman"' in _g2 and '_tl_roll < 0.001' in _g2
assert '_tl_reward = "Cornucopia"' in _g2 and '_tl_roll < 0.011' in _g2

# A Loser shirt losers whoever walks into it, and the debuff bites
_lsf = _mk(400, GROUND_Y)
_shirt = LoserShirt(400, GROUND_Y - 46)
_shirt.update((_lsf, _mk(800, GROUND_Y)))
assert _shirt.taken and _lsf.losered_timer == LoserShirt.LOSERED
_clean, _worn = _mk(400, GROUND_Y), _mk(400, GROUND_Y)
_v1, _v2 = _mk(460, GROUND_Y), _mk(460, GROUND_Y)
_clean._start('punch', 1.0); _clean.check_hit((460, GROUND_Y - 70), _v1)
_worn.losered_timer = 300
_worn._start('punch', 1.0); _worn.check_hit((460, GROUND_Y - 70), _v2)
assert 0 < (_v2.max_hp - _v2.hp) < (_v1.max_hp - _v1.hp), "the shirt must halve damage"
assert open("fight_fighter.py").read().count(
    "0.5 if self.losered_timer > 0 else 1.0") == 2, "and halve speed for both classes"

# Sickman Stickman throws six things, one of which is not thrown
_sick = next(c for c in D.CHARACTERS if c["name"] == "Sickman Stickman")
assert _sick["desc"] == "Made in collaboration with AK47."
_sf = Fighter(400, _sick, 1, CTRL)
_pulled = set()
for _ in range(600):
    _sf._sickman_fire()
    _pulled.add(_sf.pending_sick_item[0])
assert _pulled == set(Fighter._SICK_ITEMS), _pulled
assert len(_pulled) == 8, _pulled
assert {"sword", "wizard hat"} <= _pulled
assert set(_FP.SickItem.KINDS) == _pulled - {"loser hat"}
# the sword is the hardest hit of the lot, the hat the slowest
assert max(_FP.SickItem.KINDS, key=lambda k: _FP.SickItem.KINDS[k][1]) == "sword"
assert min(_FP.SickItem.KINDS, key=lambda k: _FP.SickItem.KINDS[k][0]) == "wizard hat"
for _k in _FP.SickItem.KINDS:
    _p = _FP.SickItem(400, 370, 1, _sf, _k)
    for _ in range(30):
        _p.update()
assert '_target.hp = max(0, _target.hp - 10)' in _g2, "the loser hat costs them ten"
print("Took the L: L platforms, shirts that loser you, and Sickman Stickman's "
      "eight-item bag")

# 12. The ghost clan
_GHOST = ["Da Sik Worm", "Pokerhauntus", "Izic Newt",
          "Darvin de Bread&butterfly", "Old Mr. Eyeingstine"]
_want = {"Da Sik Worm": 10, "Pokerhauntus": 50, "Izic Newt": 100,
         "Darvin de Bread&butterfly": 200, "Old Mr. Eyeingstine": 500}
for _nm2, _n2 in _want.items():
    _c3 = CONDS[_nm2]
    assert _c3[0] == "ghost_snake_kills" and _c3[2] == _n2, (_nm2, _c3)
    _ch3 = next(c for c in D.CHARACTERS if c["name"] == _nm2)
    assert _ch3.get("ghost_float"), _nm2
    assert "ghost" in W.categories_of(_ch3, CONDS), _nm2
assert W.CATEGORY_COLOR.get("ghost"), "the clan needs a colour again"
# the kills are counted and banked
_g3 = open("fight_game.py").read()
assert "_ghost_kills_flag[0] += _prev_gs - len(ghost_snakes)" in _g3
assert _g3.count("_ghost_kills_flag[0] += _prev_gs - len(ghost_snakes)") == 2
assert 'stats["ghost_snake_kills"]' in _g3
# each of the five has its own weapon, and it fires from the right button
_kickers = {"Da Sik Worm": ("sik_laser_kick", "pending_sik_laser"),
            "Pokerhauntus": ("poker_ally_kick", "pending_poker_ally")}
_punchers = {"Izic Newt": ("big_apple_punch", "pending_big_apple"),
             "Old Mr. Eyeingstine": ("uranium_punch", "pending_uranium")}
for _nm2, (_flag, _pend) in _kickers.items():
    _f3 = Fighter(400, next(c for c in D.CHARACTERS if c["name"] == _nm2), 1, CTRL)
    _f3._trigger_kick_abilities(None)
    assert getattr(_f3, _pend), _nm2
    _f4 = Fighter(400, next(c for c in D.CHARACTERS if c["name"] == _nm2), 1, CTRL)
    _f4._trigger_punch_abilities()
    assert not getattr(_f4, _pend), f"{_nm2} should not fire on punch"
for _nm2, (_flag, _pend) in _punchers.items():
    _f3 = Fighter(400, next(c for c in D.CHARACTERS if c["name"] == _nm2), 1, CTRL)
    _f3._trigger_punch_abilities()
    assert getattr(_f3, _pend), _nm2
    _f4 = Fighter(400, next(c for c in D.CHARACTERS if c["name"] == _nm2), 1, CTRL)
    _f4._trigger_kick_abilities(None)
    assert not getattr(_f4, _pend), f"{_nm2} should not fire on kick"
assert next(c for c in D.CHARACTERS
            if c["name"] == "Darvin de Bread&butterfly").get("animal_rain")
# the animals come in seven sizes, and the big ones hurt more
from fight_projectiles import FallingAnimal as _FA
assert len(_FA.KINDS) == 7, _FA.KINDS
_sizes = sorted(_FA.KINDS.values())
assert _sizes[0] < 0.6 and _sizes[-1] > 2.0, _sizes
_small = _FA(); _small.kind, _small.scale = "beetle", _FA.KINDS["beetle"]
_big = _FA(); _big.kind, _big.scale = "elephant", _FA.KINDS["elephant"]
assert _big.dmg > _small.dmg * 4, (_small.dmg, _big.dmg)
_surf2 = pygame.Surface((900, 550))
for _k2 in _FA.KINDS:
    _a3 = _FA(); _a3.kind, _a3.scale = _k2, _FA.KINDS[_k2]
    _a3.x, _a3.y = 450, 300
    _a3.draw(_surf2)
print(f"ghost clan: five fighters at 10/50/100/200/500 banishments, each with "
      f"its own weapon, and {len(_FA.KINDS)} sizes of animal "
      f"({_small.dmg}-{_big.dmg} damage)")

# 13. Halloween extras: the sticky note, no costumes in special modes,
#     and ten wins to a roll
_ui2 = open("fight_ui.py").read()
assert 'if char_filter is not None and _cc0["name"] not in char_filter' in _ui2, \
    "a special mode must only offer the costumes its own roster names"
assert '_sick_note' in _ui2 and '"sick"' in _ui2, "the Feasterween note"
assert "_sick_note[3] = FPS * 5" in _ui2, "pressing it should summon him"
_g4 = open("fight_game.py").read()
for _k3 in ("crooking_glass_wins", "took_the_l_wins"):
    assert f'if stats["{_k3}"] % 10 == 0:' in _g4, _k3
assert "Every ten wins is one roll for a rare fighter:" in _g4
assert _g4.count("Every ten wins is one roll for a rare fighter:") == 2
# the four new Halloween costumes
_hall = [c for c in D.COSTUMES_FOR_SALE if c["event"] == "Echoes of the Undying"]
assert len(_hall) == 12, len(_hall)
for _nm4 in ("Crankystein", "Which witch is which", "Witch's cooldron",
             "Thriller biller"):
    _c4 = next(c for c in D.COSTUMES if c["name"] == _nm4)
    assert _c4["event"] == "Echoes of the Undying"
    assert _c4["base"] in names, _c4["base"]
# A special mode keeps the boxes its own roster names, and nothing else.
# Sickman Stickman has no card; he is reached through Cornucopia's box.
def _fam_for(_filt):
    _f = {}
    for _i4, _c5 in enumerate(D.CHARACTERS):
        _b4 = _c5.get("costume_of")
        if not _b4:
            continue
        if _filt is not None and _c5["name"] not in _filt:
            continue
        _f.setdefault(_b4, []).append(_c5["name"])
    return _f
_TLF = frozenset({"Clown", "Hardy", "Impossible", "Mime", "Joker", "Jester",
                  "Rage Quitter", "Cornucopia", "Sickman Stickman"})
assert _fam_for(_TLF) == {"Cornucopia": ["Sickman Stickman"]}, _fam_for(_TLF)
assert _fam_for(frozenset({"Ghost", "Vampire"})) == {}, "no outside costumes"
assert len(_fam_for(None)) > 50, "the normal select still has all its boxes"
assert 'if c["name"] in char_filter and not c.get("costume_variant")' in _ui2, \
    "a costume belongs in its owner's box, not in the grid"
print(f"Halloween: {len(_hall)} costumes on the rack, the sick note on the "
      f"title, ten wins to a roll, and Sickman Stickman in Cornucopia's box")

# 14. Halloween easter eggs, and all three gated to the event
for _needle, _what in (
        ('_hallow     = bool(_ev_mode_ev and', "the Halloween gate"),
        ('_boo_buf.endswith("boo")', "typing boo"),
        ('if _bat[0] and math.hypot(', "swatting the bat"),
        ('if _pumpkin[1] and _pumpkin[1].collidepoint(_mp):', "pressing the pumpkin"),
        ('_bats_hit[0] += 1', "the bat counter"),
        ('"stop that" if _pumpkin[0] >= 5 else', "the pumpkin getting fed up")):
    assert _needle in _ui2, f"MISSING: {_what}"
# every one of them sits inside the `if _hallow:` block or its key handler
_h_at = _ui2.index("        if _hallow:")
_h_end = _ui2.index("        # Achievements button", _h_at)
_block = _ui2[_h_at:_h_end]
for _needle in ("_bat[0] = [float(", "_pk = pygame.Rect(", "_boo[0] -= 1"):
    assert _needle in _block, _needle
assert "if _hallow and hasattr(event, 'unicode')" in _ui2, "boo is event-gated too"
# B is the wiki key, so during the event it waits to see whether "oo" follows
assert "_wiki_wait[0] = 20" in _ui2, "b must not open the wiki instantly in October"
assert "_wiki_wait[0] = 0       # it was a boo, not the wiki" in _ui2
assert """                    if _hallow:
                        _wiki_wait[0] = 20""" in _ui2
assert "if _wiki_wait[0] == 0:\n                wiki_screen(unlocked, stats)" in _ui2, \
    "and it must still open when nothing follows"
print("Halloween eggs: a bat to swat, a pumpkin to press, and boo for the "
      "lights — none of them outside the event")

# 15. The new fuser group
import fight_projectiles as _FP2
_NEWF = {
    "Pepper & Kettlechip":  ({"fire", "water"},     0.38, 250,
                             ("smoke_bomb_punch", "pepper_flame_kick")),
    "Staticzap & Hibercup": ({"electric", "plant"}, 0.56, 350,
                             ("five_bolt_punch", "hibercup_ram")),
    "Plato & Dookus":       ({"water", "air"},      0.20, 150,
                             ("plate_punch", "duck_spit_kick")),
}
for _nm5, (_els, _fail, _cost, _flags) in _NEWF.items():
    _rec = D.FUSER_RECIPES[frozenset(_els)]
    assert _rec["name"] == _nm5, (_nm5, _rec)
    assert abs(_rec["fail_chance"] - _fail) < 1e-9, (_nm5, _rec)
    assert next(c["cost"] for c in D.FUSER_SHOP_CHARS if c["name"] == _nm5) == _cost
    _ch5 = next(c for c in D.CHARACTERS if c["name"] == _nm5)
    for _fl in _flags:
        assert _ch5.get(_fl), (_nm5, _fl)
# punch flags fire on punch, kick flags on kick, and never the other way
for _nm5, (_e, _f, _c, (_pflag, _kflag)) in _NEWF.items():
    _ch5 = next(c for c in D.CHARACTERS if c["name"] == _nm5)
    _pend = {"smoke_bomb_punch": "pending_smoke_bomb",
             "five_bolt_punch": "pending_five_bolts",
             "plate_punch": "pending_plate",
             "pepper_flame_kick": "pending_pepper_flame",
             "duck_spit_kick": "pending_duck_spit"}
    if _pflag in _pend:
        _f5 = Fighter(400, _ch5, 1, CTRL); _f5._trigger_punch_abilities()
        assert getattr(_f5, _pend[_pflag]), (_nm5, _pflag)
        _f6 = Fighter(400, _ch5, 1, CTRL); _f6._trigger_kick_abilities(None)
        assert not getattr(_f6, _pend[_pflag]), f"{_pflag} fired on a kick"
    if _kflag in _pend:
        _f5 = Fighter(400, _ch5, 1, CTRL); _f5._trigger_kick_abilities(None)
        assert getattr(_f5, _pend[_kflag]), (_nm5, _kflag)
        _f6 = Fighter(400, _ch5, 1, CTRL); _f6._trigger_punch_abilities()
        assert not getattr(_f6, _pend[_kflag]), f"{_kflag} fired on a punch"
# Hibercup shares Torrti's ram but poisons instead of burning
_hib = Fighter(300, next(c for c in D.CHARACTERS if c["name"] == "Staticzap & Hibercup"),
               1, CTRL)
_hib._trigger_kick_abilities(None)
assert _hib.ram_frames > 0, "the ram should start on a kick"
_vic = Fighter(340, next(c for c in D.CHARACTERS if c["name"] == "Brawler"), 1, CTRL)
for _ in range(10):
    _hib._tick_ram(_vic)
assert _vic.poison_frames > 0, "Hibercup's ram should poison"
assert _vic.fire_frames == 0, "and must not burn"
# every new projectile builds, moves and draws
_surf3 = pygame.Surface((900, 550))
for _cls in (_FP2.SmokeBomb, _FP2.PepperFlame, _FP2.FrisbeePlate, _FP2.DuckSpit):
    _pr = _cls(300, 300, 1, _hib)
    for _ in range(40):
        _pr.update()
    _pr.draw(_surf3)
# one costume on Pepper, not two, and one on Plato
assert [c["name"] for c in D.COSTUMES if c["base"] == "Pepper & Kettlechip"] \
    == ["Gift and Stockin'"]
assert [c["name"] for c in D.COSTUMES if c["base"] == "Plato & Dookus"] == ["Turkeybrain"]
print(f"fuser group: {len(_NEWF)} new recipes ({len(D.FUSER_RECIPES)} of 15 now), "
      f"each with its own punch, kick and art")

print("ALL OK")
