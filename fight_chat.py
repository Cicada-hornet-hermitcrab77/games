"""
fight_chat.py — in-match chat, and the typed keyword easter eggs.

Two separate things that share a file because both hang off the fight loop:

* ChatBox — the online match chat line (T to type). Purely a message
  channel; it does not trigger anything.

* EasterEggs — type a phrase during a fight and something happens:
  hot potatoes, pot rain, rolling coins, baseball mode and friends. The
  keywords are typed straight into the game the way "cicada77" is typed
  on the home screen, so they work in every fight, not just online ones.

In a networked fight the host owns the simulation, so a keyword typed by
the client is sent over as an EGG message and applied host-side against
the right fighter.

    chat = ChatBox(net)                 # online only
    eggs = EasterEggs()
    ...
    if not chat.handle_event(event):    # chat swallows keys while typing
        eggs.handle_event(event, ...)
    eggs.update(p1, p2)
    eggs.draw_entities(surface); chat.draw_overlay(surface)
"""

import random

import pygame

from constants import (WIDTH, HEIGHT, GROUND_Y, FPS, WHITE, CYAN, YELLOW,
                       font_small, font_tiny)
from fight_data import POWERUPS
from fight_entities import Powerup
from fight_stage import JungleSnake, ComputerBug
from fight_projectiles import (HotPotato, FallingPot, RollingCoin, FallingMerlin,
                               FlyingBaseball, FlyingBat)

# Phrases typed during a fight. Longest first so "kevin=great" is matched
# before any shorter phrase that might be a suffix of it.
KEYWORDS = sorted(
    ("hotpotato", "wtf", "crazy", "imcooking", "imdead", "imselling",
     "merlin", "randomskin", "kevin=great", "kevin=bad", "strike"),
    key=len, reverse=True)

_MAX_BUF = max(len(k) for k in KEYWORDS)


class ChatBox:
    """Online match chat. Message channel only — triggers nothing."""

    def __init__(self, net):
        self.net    = net
        self.active = False
        self.text   = ""

    def handle_event(self, event, allow_open=True) -> bool:
        """
        Returns True if chat consumed the event.

        `allow_open` is False when the T being pressed is mid-way through an
        easter-egg keyword ("ho-t-potato", "s-t-rike"), so opening chat does
        not swallow the rest of the word.
        """
        if event.type != pygame.KEYDOWN:
            return False
        if self.active:
            if event.key == pygame.K_RETURN:
                if self.text.strip():
                    self.net.send_chat(self.text)
                self.active = False; self.text = ""
            elif event.key == pygame.K_ESCAPE:
                self.active = False; self.text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode
            return True
        if event.key == pygame.K_t and allow_open:
            self.active = True
            return True
        return False

    def draw_overlay(self, surface):
        for i, (sender, text) in enumerate(self.net.chat_log[-5:]):
            col  = CYAN if sender == "You" else YELLOW
            line = font_tiny.render(f"{sender}: {text}", True, col)
            surface.blit(line, (10, HEIGHT - 110 + i * 18))
        if self.active:
            pygame.draw.rect(surface, (30, 30, 50), (0, HEIGHT - 36, WIDTH, 36))
            cur = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            ci  = font_small.render("Say: " + self.text + cur, True, WHITE)
            surface.blit(ci, (10, HEIGHT - 30))
        else:
            ht = font_tiny.render("T = chat", True, (70, 70, 70))
            surface.blit(ht, (10, HEIGHT - 16))


class EasterEggs:
    """Typed-in-game keyword effects. Works in local and online fights."""

    def __init__(self):
        self._buf = ""
        self.hot_potatoes    = []
        self.crazy_snakes    = []
        self.crazy_bugs      = []
        self.crazy_timer     = 0
        self.falling_pots    = []
        self.cooking_timer   = 0
        self.rolling_coins   = []
        self.falling_merlins = []
        self.rain_powerups   = []
        self.rain_timer      = 0
        self.rain_cd         = 0
        self.rain_type       = None
        self.baseballs       = []
        self.flying_bats     = []
        self.baseball_timer  = 0
        self.baseball_cd     = 0

    # ── Typing ────────────────────────────────────────────────────────────────

    def would_extend(self, ch) -> bool:
        """
        True if `ch` continues a keyword already part-typed. Used so the T in
        "hotpotato" / "strike" / "wtf" / "kevin=great" types the word instead
        of opening the chat line. A bare "t" extends nothing (no keyword
        starts with one), so pressing T on its own still opens chat.
        """
        s = (self._buf + ch.lower())
        for n in range(min(len(s), _MAX_BUF), 1, -1):   # n>1: ignore a lone char
            tail = s[-n:]
            if any(k.startswith(tail) for k in KEYWORDS):
                return True
        return False

    def handle_event(self, event):
        """
        Feed a pygame event. Returns the keyword just completed, or None.
        The caller decides what to do with it (apply locally, or send to
        the host in a networked fight).
        """
        if event.type != pygame.KEYDOWN or not event.unicode:
            return None
        ch = event.unicode.lower()
        if not ch.isprintable():
            return None
        self._buf = (self._buf + ch)[-_MAX_BUF:]
        for kw in KEYWORDS:
            if self._buf.endswith(kw):
                self._buf = ""
                return kw
        return None

    # ── Effects ───────────────────────────────────────────────────────────────

    def fire(self, kw, target, other=None):
        """Apply one keyword. `target` is the fighter who typed it."""
        if kw == "hotpotato":
            self.hot_potatoes.append(HotPotato())
        elif kw == "wtf":
            target.hp = max(0, target.hp - 10)
            target.flash_timer = 25
        elif kw == "crazy":
            self.crazy_timer = FPS * 8
        elif kw == "imcooking":
            self.cooking_timer = FPS * 10
        elif kw == "imdead":
            target.hp = 0
        elif kw == "imselling":
            self.rolling_coins.append(RollingCoin())
        elif kw == "merlin":
            for _ in range(8):
                self.falling_merlins.append(FallingMerlin())
        elif kw == "randomskin":
            from fight_data import CHARACTERS
            new_char = random.choice(
                [c for c in CHARACTERS if c['name'] != target.char['name']])
            target.char  = new_char
            target.color = new_char['color']
        elif kw == "kevin=great":
            self.rain_timer = FPS * 8; self.rain_type = 'heal'
        elif kw == "kevin=bad":
            self.rain_timer = FPS * 8; self.rain_type = 'poison'
        elif kw == "strike":
            self.baseball_timer = FPS * 15

    # ── Per-frame ─────────────────────────────────────────────────────────────

    def update(self, p1, p2):
        for hp in self.hot_potatoes:
            hp.update()
            if hp.exploding and not hp.damaged:
                hp.damaged = True
                for f in (p1, p2):
                    if hp.collides(f):
                        f.hp = max(0, f.hp - hp.EXPLODE_DMG)
                        f.flash_timer = 20
        self.hot_potatoes = [hp for hp in self.hot_potatoes if hp.alive]

        if self.crazy_timer > 0:
            self.crazy_timer -= 1
            if self.crazy_timer % 10 == 0:
                self.crazy_snakes.append(JungleSnake())
            if self.crazy_timer % 7 == 0:
                self.crazy_bugs.append(ComputerBug())
        for sn in self.crazy_snakes:
            sn.update(p1, p2)
        self.crazy_snakes = [sn for sn in self.crazy_snakes if sn.alive]
        for cb in self.crazy_bugs:
            cb.update(min((p1, p2), key=lambda f: abs(f.x - cb.x)))
        self.crazy_bugs = [cb for cb in self.crazy_bugs if cb.alive]

        if self.cooking_timer > 0:
            self.cooking_timer -= 1
            if self.cooking_timer % 45 == 0:
                self.falling_pots.append(FallingPot())
        for pot in self.falling_pots:
            pot.update()
            if pot.just_landed:
                for f in (p1, p2):
                    if abs(f.x - pot.x) < pot.HIT_RANGE:
                        f.hp = max(0, f.hp - pot.DAMAGE)
                        f.flash_timer = 20
        self.falling_pots = [pt for pt in self.falling_pots if pt.alive]

        for coin in self.rolling_coins:
            for f in coin.update(p1, p2):
                f.hp = max(0, f.hp - coin.DAMAGE)
                f.flash_timer = 15
        self.rolling_coins = [c for c in self.rolling_coins if c.alive]

        for m in self.falling_merlins:
            m.update()
        self.falling_merlins = [m for m in self.falling_merlins if m.alive]

        if self.rain_timer > 0:
            self.rain_timer -= 1
            if self.rain_cd > 0:
                self.rain_cd -= 1
            else:
                _spec = next((p for p in POWERUPS
                              if p['name'] == ('Heal' if self.rain_type == 'heal'
                                               else 'Poison')), None)
                if _spec:
                    _rpu = Powerup.__new__(Powerup)
                    _rpu.spec = _spec; _rpu.name = _spec['name']
                    _rpu.color = _spec['color']
                    _rpu.x = float(random.randint(80, WIDTH - 80))
                    _rpu.y = float(GROUND_Y - 14)
                    _rpu.age = 0; _rpu.picked_up = False
                    self.rain_powerups.append(_rpu)
                self.rain_cd = 20
        for rpu in self.rain_powerups:
            rpu.update()
            for f in (p1, p2):
                if not rpu.picked_up and rpu.collides(f):
                    f.apply_powerup(rpu.spec)
                    rpu.picked_up = True
        self.rain_powerups = [r for r in self.rain_powerups if not r.picked_up]

        if self.baseball_timer > 0:
            self.baseball_timer -= 1
            if self.baseball_cd > 0:
                self.baseball_cd -= 1
            else:
                self.baseballs.append(FlyingBaseball())
                if random.random() < 0.35:
                    self.flying_bats.append(FlyingBat())
                self.baseball_cd = 80
        for bb in self.baseballs:
            for f in bb.update(p1, p2):
                f.hp = max(0, f.hp - bb.DAMAGE)
                f.flash_timer = 12
        self.baseballs = [bb for bb in self.baseballs if bb.alive]
        for fb in self.flying_bats:
            for f in fb.update(p1, p2):
                f.hp = max(0, f.hp - fb.DAMAGE)
                f.flash_timer = 18
        self.flying_bats = [fb for fb in self.flying_bats if fb.alive]

    def draw_entities(self, surface):
        for group in (self.hot_potatoes, self.crazy_snakes, self.crazy_bugs,
                      self.falling_pots, self.rolling_coins, self.falling_merlins,
                      self.rain_powerups, self.baseballs, self.flying_bats):
            for e in group:
                e.draw(surface)
