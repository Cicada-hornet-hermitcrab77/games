"""
fight_lobby.py — transport-agnostic lobby core.

Holds everything the fight server does that is not sockets: the client
registry, the matchmaking queue, the message protocol, and the win
leaderboard. Transports (fight_server.py over TCP, fight_server_ws.py
over WebSocket) supply a `send` callable per client and hand incoming
messages to handle(); the protocol lives here once so the two cannot
drift apart.

A transport must:
  1. call register(code, username, send)  when a HELLO arrives,
  2. call handle(code, msg)               for every later message,
  3. call disconnect(code)                when the connection drops.

`send` takes a dict and delivers it to that client. It must not block.
"""

import json
import os
import random
import threading

# Number of entries in STAGES (fight_data.py). Kept as a plain literal because
# importing fight_data would drag pygame — and a display — onto the server.
# Bump this when stages are added, or online play never rolls the new ones.
STAGE_COUNT = 32

_ADMIN_KEY = os.environ.get("FIGHT_ADMIN_KEY", "kevin_dev")

# ── Shared state ──────────────────────────────────────────────────────────────

_lock    = threading.Lock()
_clients = {}   # user_code → {send, username, in_queue, matched_with}
_queue   = []   # [user_code, …] ordered by join time

# Win leaderboard — persisted to disk
_WINS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fight_wins.json")
_wins      = {}   # user_code → {"username": str, "wins": int}


def load_wins():
    global _wins
    try:
        with open(_WINS_FILE) as f:
            _wins = json.load(f)
    except Exception:
        _wins = {}


def _save_wins():
    try:
        with open(_WINS_FILE, "w") as f:
            json.dump(_wins, f, indent=2)
    except Exception:
        pass


def wins_snapshot():
    with _lock:
        return sorted(_wins.values(), key=lambda x: -x.get("wins", 0))


def client_count():
    with _lock:
        return len(_clients)


def _deliver(send, obj):
    """Push one message to a client, ignoring a dead connection."""
    try:
        send(obj)
    except Exception:
        pass


# ── Registration / teardown ───────────────────────────────────────────────────

def register(code: str, username: str, send) -> bool:
    """Add a client. Returns False if the HELLO was malformed."""
    if not code:
        return False
    with _lock:
        _clients[code] = {
            "send":         send,
            "username":     username or "Player",
            "in_queue":     False,
            "matched_with": None,
        }
    _deliver(send, {"type": "HELLO_OK"})
    return True


def disconnect(code: str):
    """Drop a client and tell whoever they were matched with."""
    if not code:
        return
    with _lock:
        info    = _clients.pop(code, None)
        name    = info["username"] if info else "?"
        partner = info["matched_with"] if info else None
        if code in _queue:
            _queue.remove(code)
        psend = None
        if partner and partner in _clients:
            _clients[partner]["matched_with"] = None
            psend = _clients[partner]["send"]
    if psend:
        _deliver(psend, {"type": "OPP_LEFT"})
    return name


def broadcast_update(note: str) -> int:
    """Send an update announcement to everyone connected."""
    with _lock:
        sends = [v["send"] for v in _clients.values()]
    for s in sends:
        _deliver(s, {"type": "UPDATE_NOTIFY", "note": note})
    return len(sends)


def is_admin_key(key) -> bool:
    return key == _ADMIN_KEY


# ── Matchmaking ───────────────────────────────────────────────────────────────

def _try_match():
    """Pair the first two queued players and notify them."""
    with _lock:
        available = [c for c in _queue
                     if c in _clients and _clients[c]["matched_with"] is None]
        if len(available) < 2:
            return None
        a, b = available[0], available[1]
        _queue.remove(a)
        _queue.remove(b)
        stage = random.randint(0, STAGE_COUNT - 1)
        _clients[a]["in_queue"]     = False
        _clients[b]["in_queue"]     = False
        _clients[a]["matched_with"] = b
        _clients[b]["matched_with"] = a
        sa, sb = _clients[a]["send"], _clients[b]["send"]
        na, nb = _clients[a]["username"], _clients[b]["username"]

    _deliver(sa, {"type": "MATCH_FOUND", "opp_code": b,
                  "opp_name": nb, "stage": stage, "you_host": True})
    _deliver(sb, {"type": "MATCH_FOUND", "opp_code": a,
                  "opp_name": na, "stage": stage, "you_host": False})
    return (na, nb, stage)


# ── Protocol ──────────────────────────────────────────────────────────────────

def handle(code: str, msg: dict):
    """
    Process one message from `code`. Returns a short log line for the
    transport to print, or None.
    """
    t = msg.get("type")
    with _lock:
        info = _clients.get(code)
        if not info:
            return None
        send    = info["send"]
        partner = info.get("matched_with")
        psend   = (_clients[partner]["send"]
                   if partner and partner in _clients else None)

    if t == "QUEUE_JOIN":
        with _lock:
            if code not in _queue:
                _clients[code]["in_queue"] = True
                _queue.append(code)
        matched = _try_match()
        if matched:
            na, nb, stage = matched
            return f"[match] {na} vs {nb}  stage={stage}"

    elif t == "QUEUE_LEAVE":
        with _lock:
            if code in _clients:
                _clients[code]["in_queue"] = False
            if code in _queue:
                _queue.remove(code)

    elif t == "RELAY":
        if psend:
            _deliver(psend, {"type": "RELAY", "msg": msg.get("msg")})

    elif t == "MATCH_CHAT":
        if psend:
            with _lock:
                name = _clients[code]["username"]
            _deliver(psend, {"type": "MATCH_CHAT",
                             "from_name": name, "msg": msg.get("msg", "")})

    elif t == "FRIEND_CHAT":
        to   = msg.get("to_code", "")
        text = msg.get("msg", "")
        with _lock:
            target = _clients.get(to)
            name   = info["username"]
            tsend  = target["send"] if target else None
        if tsend:
            _deliver(tsend, {"type":      "FRIEND_CHAT",
                             "from_code": code,
                             "from_name": name,
                             "msg":       text})

    elif t == "FRIEND_INFO":
        query = msg.get("code", "")
        with _lock:
            target = _clients.get(query)
            uname  = target["username"] if target else None
        _deliver(send, {"type": "FRIEND_INFO", "code": query,
                        "username": uname, "online": bool(target)})

    elif t == "FRIEND_REQUEST":
        to_code = msg.get("to_code", "")
        with _lock:
            target  = _clients.get(to_code)
            my_name = info["username"]
            tsend   = target["send"] if target else None
        if tsend:
            _deliver(tsend, {"type":      "FRIEND_REQUEST",
                             "from_code": code,
                             "from_name": my_name})
        else:
            _deliver(send, {"type": "FRIEND_REQUEST_RESULT",
                            "from_code": to_code, "from_name": "",
                            "result": "offline"})

    elif t == "FRIEND_RESPONSE":
        to_code  = msg.get("to_code", "")
        accepted = msg.get("accepted", False)
        with _lock:
            target  = _clients.get(to_code)
            my_name = info["username"]
            tsend   = target["send"] if target else None
        if tsend:
            _deliver(tsend, {"type":      "FRIEND_REQUEST_RESULT",
                             "from_code": code,
                             "from_name": my_name,
                             "result":    "accepted" if accepted else "declined"})

    elif t == "MATCH_RESULT":
        if msg.get("won"):
            with _lock:
                name  = _clients.get(code, {}).get("username", "Player")
                entry = _wins.setdefault(code, {"username": name, "wins": 0})
                entry["username"] = name   # keep name current
                entry["wins"] += 1
                total = entry["wins"]
            _save_wins()
            return f"[win] {name} ({code})  total={total}"

    elif t == "LEADERBOARD_REQUEST":
        top = wins_snapshot()[:25]
        _deliver(send, {"type": "LEADERBOARD", "entries": top})

    elif t == "UPDATE_NOTIFY":
        note = msg.get("note", "")
        if note:
            broadcast_update(note)
            return f"[notify] {note}"

    return None
