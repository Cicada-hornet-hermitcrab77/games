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
assert set(_FP.SickItem.KINDS) == _pulled - {"loser hat"}
for _k in _FP.SickItem.KINDS:
    _p = _FP.SickItem(400, 370, 1, _sf, _k)
    for _ in range(30):
        _p.update()
assert '_target.hp = max(0, _target.hp - 10)' in _g2, "the loser hat costs them ten"
print("Took the L: L platforms, shirts that loser you, and Sickman Stickman's "
      "six-item bag")

print("ALL OK")
