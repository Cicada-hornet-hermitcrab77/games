"""Story Mode — the Hiss-tory, fought out one chapter at a time.

The chapters follow the wiki: the Last Dessert, the murder, the Great War
the murder started, and what was left of the Seasonals afterwards. Each one
puts you in somebody specific, against somebody specific, somewhere
specific. You do not pick your fighter — the story already knows who you
were that day.

This module owns the data and the screens. It never starts a fight itself;
fight_game does that, because run_fight lives there and importing it back
would close a loop.
"""

import pygame

from constants import *
from fight_data import CHARACTERS, STAGES
from fight_drawing import draw_stickman

# ── The story ───────────────────────────────────────────────────────────────
# "you" and "foe" are roster names; "stage" is a stage name. Both are
# checked against the real tables by selftest, so a typo cannot ship.
CHAPTERS = [
    # ── Act one: the night itself ──────────────────────────────────────────
    {"act": "The Last Dessert",
     "title": "Under the table",
     "you": "Red Herring", "foe": "Nian",
     "stage": "Medieval Castle", "difficulty": "easy",
     "before": [
         "Nineteen Seasonals sat down at one table, which had never happened "
         "and has not happened since. Eighteen of them were invited.",
         "You went in under the cloth before the first of them arrived. It "
         "is the best seat in the hall if you do not mind the dark.",
         "Nian smells fish.",
     ],
     "after": [
         "He lets it go. He has a year to get through and only a week to do "
         "it in.",
     ]},
    {"act": "The Last Dessert",
     "title": "Nobody believes a fish",
     "you": "Red Herring", "foe": "Smoochie",
     "stage": "Medieval Castle", "difficulty": "easy",
     "before": [
         "You have seen the one on Birthalomeu's left take something off the "
         "table and put it in a purse. You say so.",
         "Smoochie points out that you are a red herring, and that this is "
         "the entire thing you are known for.",
     ],
     "after": [
         "She believes you. She is the only one who ever will.",
     ]},
    {"act": "The Last Dessert",
     "title": "The one who left early",
     "you": "Red Herring", "foe": "Tombstone",
     "stage": "Graveyard", "difficulty": "medium",
     "before": [
         "He goes out through the yard before the candles are down. You go "
         "after him and get as far as the gate.",
         "Tombstone is standing in it. Tombstone is always standing in it.",
         "\"Nothing has happened,\" he says. \"Go back inside.\"",
     ],
     "after": [
         "By the time he steps aside the yard is empty and Birthalomeu is "
         "dead. Tombstone does not say sorry. He never does. He does "
         "remember, though, and it is the reason he fights beside you later.",
     ]},

    # ── Act two: the war that came of it ───────────────────────────────────
    {"act": "The Great War",
     "title": "The west route",
     "you": "Clover", "foe": "Stickman of Liberty",
     "stage": "Pirate Ship", "difficulty": "medium",
     "before": [
         "Only skilled navigators get past the Sea o' Seasons, and there is "
         "one good way through it.",
         "The majors took the west. They took it in the first week of the "
         "war and they have held it ever since.",
     ],
     "after": [
         "You hold the deck. You do not hold the crossing. Nobody minor ever "
         "has again.",
     ]},
    {"act": "The Great War",
     "title": "The small weeks",
     "you": "Solara", "foe": "Cornucopia",
     "stage": "Desert", "difficulty": "medium",
     "before": [
         "A major has a fortnight, a shop and a world that plans around him. "
         "A minor has seven days and whoever happens to be awake.",
         "Solara is awake. It is the longest day of the year and she intends "
         "to use all of it.",
     ],
     "after": [
         "She uses all of it. The sun goes down anyway.",
     ]},
    {"act": "The Great War",
     "title": "The lamps go out",
     "you": "Nun-Gimel-Hei-Shin", "foe": "Jack O' Slash",
     "stage": "Haunted House", "difficulty": "hard",
     "before": [
         "Diwali lit the lamps along every road the minors held, which was "
         "how they found each other in the dark.",
         "They go out one road at a time. This is the road they go out on.",
     ],
     "after": [
         "The dreidel lands on Shin, which means you put in rather than take "
         "out. There was nothing left to take.",
     ]},
    {"act": "The Great War",
     "title": "Twin Day counts as one",
     "you": "Bookzworm", "foe": "Baddit",
     "stage": "Booked", "difficulty": "hard",
     "before": [
         "There were two of him and he was one week, which the majors "
         "thought was funny right up until the fighting started.",
         "Afterwards there were none of him and he was still one week.",
     ],
     "after": [
         "You write the pair of them down. It is the only thing you are any "
         "good at and it turns out to be the thing that matters.",
     ]},
    {"act": "The Great War",
     "title": "Hard ground",
     "you": "Eartha", "foe": "Saint Nix",
     "stage": "Arctic Tundra", "difficulty": "hard",
     "before": [
         "The ground is on your side everywhere except here, where it is "
         "three feet of ice and belongs to the other lot.",
     ],
     "after": [
         "Something grows out of it. It should not be able to and it does.",
     ]},
    {"act": "The Great War",
     "title": "Everywhere there was ground",
     "you": "Yellowstone", "foe": "Nian",
     "stage": "Volcano Core", "difficulty": "super_hard",
     "before": [
         "It was not one battle in one place. Every stage, every sea, every "
         "ring of ground a tribe holds — all of it, at once, for as long as "
         "it took.",
         "This is the bit underneath.",
     ],
     "after": [
         "The war ends the way big ones do: not settled, just stopped. "
         "Seven majors. Seven minors. Everybody else on the ceiling.",
     ]},

    # ── Act three: what was left ───────────────────────────────────────────
    {"act": "What Was Left",
     "title": "The stars line up",
     "you": "Volcanis", "foe": "Saint Nix",
     "stage": "Volcano", "difficulty": "super_hard",
     "before": [
         "The dead stay dead except when the sky goes out.",
         "The stars line up for a solar eclipse and Volcanis comes down off "
         "the ceiling with both hammers still up, exactly as he was painted.",
     ],
     "after": [
         "The eclipse ends. He goes back. Nobody has worked out why he gets "
         "to do that and Pi Day does not.",
     ]},
    {"act": "What Was Left",
     "title": "The moon goes dark",
     "you": "Umbra", "foe": "Jack O' Slash",
     "stage": "The Void", "difficulty": "super_super_hard",
     "before": [
         "Hers is the lunar one. She comes down when the moon does and she "
         "comes down for nothing else.",
         "She has been on that ceiling a long time and she has had a long "
         "time to think about who put her there.",
     ],
     "after": [
         "She tells you where he went. Then the moon comes back and so does "
         "the ceiling.",
     ]},
    {"act": "What Was Left",
     "title": "The purse",
     "you": "Red Herring", "foe": "He-Who-Shall-Not-Be-Named",
     "stage": "Graveyard", "difficulty": "mega_hard",
     "before": [
         "Same yard. Same gate. Tombstone steps aside this time without "
         "being asked, which from him is an apology.",
         "He is still leaning back out of the light and he is still holding "
         "the purse. Nobody has said his name since the night he earned it "
         "and nobody is going to start now.",
         "You were under the table. You are the only one who can say what is "
         "in there.",
     ],
     "after": [
         "You take the purse off him.",
         "It settles nothing — the Seasonals are still seven and seven, the "
         "ceiling is still full, and Birthalomeu is still a cake nobody ate. "
         "But somebody finally said what happened, out loud, with the proof "
         "in his hand.",
         "That is what Hiss-tory is for.",
     ]},
]

ACTS = []
for _c in CHAPTERS:
    if _c["act"] not in ACTS:
        ACTS.append(_c["act"])

# What finishing the whole thing is worth.
STORY_REWARD = "He-Who-Shall-Not-Be-Named"


def progress(stats):
    """How many chapters are done. Chapters only unlock in order."""
    return int((stats or {}).get("story_progress", 0))


def is_done(stats):
    return progress(stats) >= len(CHAPTERS)


def mark_done(stats, idx):
    """Record a chapter cleared. Returns True if that finished the story."""
    if idx + 1 > progress(stats):
        stats["story_progress"] = idx + 1
    if is_done(stats):
        stats["story_done"] = True
        return True
    return False


# ── Screens ─────────────────────────────────────────────────────────────────
_PAPER   = (232, 226, 210)
_INK     = (38, 34, 32)
_FADED   = (120, 112, 104)
_ACCENT  = (196, 110,  96)


def _wrap(text, font, width):
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if font.size(trial)[0] <= width or not line:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def _char(name):
    return next((c for c in CHARACTERS if c["name"] == name), None)


def _stage_idx(name):
    for i, s in enumerate(STAGES):
        if s["name"] == name:
            return i
    return 0


def narration(lines, title, subtitle, cont="press any key"):
    """A page of story. Returns False if the player quit out of it."""
    shown, hold = 0, 0
    full = "\n".join(lines)
    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN,
                           pygame.FINGERDOWN):
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return False
                if shown < len(full):
                    shown = len(full)        # a key skips the typing
                else:
                    return True
        if shown < len(full):
            shown = min(len(full), shown + 2)
        else:
            hold += 1

        screen.fill((20, 18, 24))
        pygame.draw.rect(screen, (28, 25, 32), (60, 50, WIDTH - 120, HEIGHT - 150))
        pygame.draw.rect(screen, (84, 74, 70), (60, 50, WIDTH - 120, HEIGHT - 150), 2)
        _t = font_medium.render(title, True, _ACCENT)
        screen.blit(_t, (90, 74))
        _s = font_small.render(subtitle, True, _FADED)
        screen.blit(_s, (90, 108))
        pygame.draw.line(screen, (84, 74, 70), (90, 134), (WIDTH - 90, 134), 1)

        _typed = full[:shown].split("\n")
        y = 152
        for para in _typed:
            for ln in _wrap(para, font_small, WIDTH - 200):
                screen.blit(font_small.render(ln, True, (214, 208, 198)), (90, y))
                y += 22
            y += 10
        if shown >= len(full) and (hold // 24) % 2 == 0:
            _c = font_tiny.render(cont, True, (150, 144, 136))
            screen.blit(_c, (WIDTH // 2 - _c.get_width() // 2, HEIGHT - 76))
        pygame.display.flip()


def chapter_select(stats):
    """Pick a chapter. Returns its index, or None to leave."""
    done = progress(stats)
    sel  = min(done, len(CHAPTERS) - 1)
    scroll = 0
    t = 0.0
    ROWH, VISIBLE = 30, 11
    LIST_X, LIST_W = 40, 320
    while True:
        clock.tick(FPS)
        t += 0.02
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                if ev.key in (pygame.K_DOWN, pygame.K_s):
                    sel = min(len(CHAPTERS) - 1, sel + 1)
                if ev.key in (pygame.K_UP, pygame.K_w):
                    sel = max(0, sel - 1)
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if sel <= done:
                        return sel
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                _mp = ((int(ev.x * WIDTH), int(ev.y * HEIGHT))
                       if ev.type == pygame.FINGERDOWN else ev.pos)
                for _i in range(VISIBLE):
                    _ci = scroll + _i
                    if _ci >= len(CHAPTERS):
                        break
                    if pygame.Rect(LIST_X, 96 + _i * ROWH, LIST_W,
                                   ROWH - 2).collidepoint(_mp):
                        if _ci == sel and _ci <= done:
                            return _ci
                        sel = _ci
                if pygame.Rect(WIDTH - 130, HEIGHT - 52, 100, 32).collidepoint(_mp):
                    return None
        scroll = max(0, min(sel - VISIBLE + 2, len(CHAPTERS) - VISIBLE))
        scroll = max(0, min(scroll, sel))

        screen.fill((20, 18, 24))
        _h = font_medium.render("STORY MODE", True, _ACCENT)
        screen.blit(_h, (40, 30))
        _hs = font_small.render(
            f"Hiss-tory, fought out  ·  {done} of {len(CHAPTERS)} chapters done",
            True, _FADED)
        screen.blit(_hs, (40, 62))

        # ── the chapter list ───────────────────────────────────────────────
        _last_act = None
        for _i in range(VISIBLE):
            _ci = scroll + _i
            if _ci >= len(CHAPTERS):
                break
            ch = CHAPTERS[_ci]
            y  = 96 + _i * ROWH
            locked = _ci > done
            if ch["act"] != _last_act:
                pygame.draw.line(screen, (70, 62, 60), (LIST_X, y - 2),
                                 (LIST_X + LIST_W, y - 2), 1)
            _last_act = ch["act"]
            if _ci == sel:
                pygame.draw.rect(screen, (44, 38, 46),
                                 (LIST_X, y, LIST_W, ROWH - 2), border_radius=4)
                pygame.draw.rect(screen, _ACCENT if not locked else (90, 82, 80),
                                 (LIST_X, y, LIST_W, ROWH - 2), 1, border_radius=4)
            _num = font_tiny.render(f"{_ci + 1:2d}", True, (110, 104, 100))
            screen.blit(_num, (LIST_X + 8, y + 9))
            _col = (96, 90, 88) if locked else (
                (150, 200, 150) if _ci < done else (235, 230, 222))
            _nm = ch["title"] if not locked else "— locked —"
            screen.blit(font_small.render(_nm, True, _col), (LIST_X + 32, y + 5))
            if _ci < done:
                pygame.draw.circle(screen, (110, 200, 120),
                                   (LIST_X + LIST_W - 16, y + 14), 4)

        # ── the chapter itself ─────────────────────────────────────────────
        ch = CHAPTERS[sel]
        locked = sel > done
        PX, PW = LIST_X + LIST_W + 30, WIDTH - (LIST_X + LIST_W + 30) - 40
        pygame.draw.rect(screen, (28, 25, 32), (PX, 96, PW, HEIGHT - 170))
        pygame.draw.rect(screen, (84, 74, 70), (PX, 96, PW, HEIGHT - 170), 2)
        screen.blit(font_tiny.render(ch["act"].upper(), True, _ACCENT),
                    (PX + 14, 108))
        screen.blit(font_medium.render(
            ch["title"] if not locked else "???", True,
            (235, 230, 222) if not locked else (110, 104, 100)), (PX + 14, 124))

        if locked:
            _msg = _wrap("Finish the chapter before it. The Hiss-tory does "
                         "not go out of order.", font_small, PW - 28)
            for _k, _ln in enumerate(_msg):
                screen.blit(font_small.render(_ln, True, _FADED),
                            (PX + 14, 170 + _k * 22))
        else:
            screen.blit(font_small.render(f"on {ch['stage']}", True, _FADED),
                        (PX + 14, 158))
            _you, _foe = _char(ch["you"]), _char(ch["foe"])
            _gy = 300
            for _c2, _dx, _face, _lbl in ((_you, PX + 80, 1, "you are"),
                                          (_foe, PX + PW - 80, -1, "against")):
                if _c2 is None:
                    continue
                try:
                    draw_stickman(screen, _dx, _gy, _c2["color"], _face,
                                  "idle", 0.3 + 0.1 * _face, scale=0.72,
                                  char_name=_c2["name"])
                except Exception:
                    pass
                _l1 = font_tiny.render(_lbl, True, _FADED)
                screen.blit(_l1, (_dx - _l1.get_width() // 2, _gy + 10))
                _l2 = font_small.render(_c2["name"], True, (226, 220, 212))
                _l2w = _l2.get_width()
                screen.blit(_l2, (max(PX + 6, min(PX + PW - _l2w - 6,
                                                  _dx - _l2w // 2)), _gy + 26))
            _vs = font_medium.render("vs", True, _ACCENT)
            screen.blit(_vs, (PX + PW // 2 - _vs.get_width() // 2, _gy - 50))
            _d = font_tiny.render(ch["difficulty"].replace("_", " "), True,
                                  (180, 150, 90))
            screen.blit(_d, (PX + PW // 2 - _d.get_width() // 2, _gy + 12))
            _state = ("done — play it again" if sel < done
                      else "press ENTER to begin")
            _s2 = font_small.render(_state, True,
                                    (150, 200, 150) if sel < done else _ACCENT)
            screen.blit(_s2, (PX + PW // 2 - _s2.get_width() // 2, HEIGHT - 110))

        if is_done(stats):
            _fin = font_tiny.render(
                f"Story complete — {STORY_REWARD} is yours", True, (255, 200, 90))
            screen.blit(_fin, (40, HEIGHT - 44))
        _b = pygame.Rect(WIDTH - 130, HEIGHT - 52, 100, 32)
        pygame.draw.rect(screen, (40, 36, 44), _b, border_radius=5)
        pygame.draw.rect(screen, (120, 112, 108), _b, 1, border_radius=5)
        _bt = font_small.render("BACK", True, (220, 214, 206))
        screen.blit(_bt, (_b.centerx - _bt.get_width() // 2, _b.y + 6))
        screen.blit(font_tiny.render("up/down picks  ·  enter plays  ·  esc leaves",
                                     True, (110, 104, 100)), (40, HEIGHT - 24))
        pygame.display.flip()
