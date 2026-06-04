"""
fight_server.py — matchmaking and relay server.

Run:  python3 fight_server.py [port]    (default 7779)

What it does
------------
* Accepts connections from players who HELLO-register with their user code.
* Pairs players who join the matchmaking queue and tells each who they matched
  with, what stage to use, and whether they are the host.
* Relays game state / input frames between matched pairs.
* Relays in-match chat (MATCH_CHAT) and friend-to-friend chat (FRIEND_CHAT).
* Answers FRIEND_INFO requests (is this code online? what name?).
"""

import socket
import select
import json
import struct
import threading
import random
import sys
import os

PORT = 7779

# ── Framing (same format as fight_network.py) ─────────────────────────────────

def _send(sock, obj):
    data = json.dumps(obj).encode()
    try:
        sock.sendall(struct.pack(">I", len(data)) + data)
    except Exception:
        pass


class _Reader:
    def __init__(self):
        self._buf = b""

    def feed(self, data):
        self._buf += data

    def messages(self):
        out = []
        while len(self._buf) >= 4:
            n = struct.unpack(">I", self._buf[:4])[0]
            if len(self._buf) < 4 + n:
                break
            try:
                out.append(json.loads(self._buf[4:4 + n]))
            except Exception:
                pass
            self._buf = self._buf[4 + n:]
        return out


# ── Shared server state ───────────────────────────────────────────────────────

_lock    = threading.Lock()
_clients = {}   # user_code → {sock, reader, username, in_queue, matched_with}
_queue   = []   # [user_code, …] ordered by join time

# Win leaderboard — persisted to disk
_WINS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fight_wins.json")
_wins      = {}   # user_code → {"username": str, "wins": int}


def _load_wins():
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _try_match():
    """Pair the first two queued players and notify them."""
    with _lock:
        available = [c for c in _queue
                     if c in _clients and _clients[c]["matched_with"] is None]
        if len(available) < 2:
            return
        a, b = available[0], available[1]
        _queue.remove(a)
        _queue.remove(b)
        stage = random.randint(0, 29)
        _clients[a]["in_queue"]     = False
        _clients[b]["in_queue"]     = False
        _clients[a]["matched_with"] = b
        _clients[b]["matched_with"] = a
        sa, sb = _clients[a]["sock"], _clients[b]["sock"]
        na, nb = _clients[a]["username"], _clients[b]["username"]

    _send(sa, {"type": "MATCH_FOUND", "opp_code": b,
               "opp_name": nb, "stage": stage, "you_host": True})
    _send(sb, {"type": "MATCH_FOUND", "opp_code": a,
               "opp_name": na, "stage": stage, "you_host": False})
    print(f"[match] {na} vs {nb}  stage={stage}", flush=True)


def _handle(code, msg):
    t = msg.get("type")
    with _lock:
        info = _clients.get(code)
        if not info:
            return
        sock    = info["sock"]
        partner = info.get("matched_with")
        psock   = (_clients[partner]["sock"]
                   if partner and partner in _clients else None)
        pname   = (_clients[partner]["username"]
                   if partner and partner in _clients else None)

    if t == "QUEUE_JOIN":
        with _lock:
            if code not in _queue:
                _clients[code]["in_queue"] = True
                _queue.append(code)
        _try_match()

    elif t == "QUEUE_LEAVE":
        with _lock:
            _clients[code]["in_queue"] = False
            if code in _queue:
                _queue.remove(code)

    elif t == "RELAY":
        if psock:
            _send(psock, {"type": "RELAY", "msg": msg.get("msg")})

    elif t == "MATCH_CHAT":
        if psock:
            with _lock:
                name = _clients[code]["username"]
            _send(psock, {"type": "MATCH_CHAT",
                          "from_name": name, "msg": msg.get("msg", "")})

    elif t == "FRIEND_CHAT":
        to   = msg.get("to_code", "")
        text = msg.get("msg", "")
        with _lock:
            target = _clients.get(to)
            name   = info["username"]
        if target:
            _send(target["sock"], {
                "type":      "FRIEND_CHAT",
                "from_code": code,
                "from_name": name,
                "msg":       text,
            })

    elif t == "FRIEND_INFO":
        query = msg.get("code", "")
        with _lock:
            target = _clients.get(query)
        if target:
            _send(sock, {"type": "FRIEND_INFO", "code": query,
                         "username": target["username"], "online": True})
        else:
            _send(sock, {"type": "FRIEND_INFO", "code": query,
                         "username": None, "online": False})

    elif t == "FRIEND_REQUEST":
        to_code = msg.get("to_code", "")
        with _lock:
            target  = _clients.get(to_code)
            my_name = info["username"]
        if target:
            _send(target["sock"], {
                "type":      "FRIEND_REQUEST",
                "from_code": code,
                "from_name": my_name,
            })
        else:
            _send(sock, {"type": "FRIEND_REQUEST_RESULT",
                         "from_code": to_code, "from_name": "",
                         "result": "offline"})

    elif t == "FRIEND_RESPONSE":
        to_code  = msg.get("to_code", "")
        accepted = msg.get("accepted", False)
        with _lock:
            target  = _clients.get(to_code)
            my_name = info["username"]
        if target:
            _send(target["sock"], {
                "type":      "FRIEND_REQUEST_RESULT",
                "from_code": code,
                "from_name": my_name,
                "result":    "accepted" if accepted else "declined",
            })

    elif t == "MATCH_RESULT":
        if msg.get("won"):
            with _lock:
                name = _clients.get(code, {}).get("username", "Player")
            entry = _wins.setdefault(code, {"username": name, "wins": 0})
            entry["username"] = name   # keep name current
            entry["wins"] += 1
            _save_wins()
            print(f"[win] {name} ({code})  total={entry['wins']}", flush=True)

    elif t == "LEADERBOARD_REQUEST":
        with _lock:
            snapshot = list(_wins.values())
        top = sorted(snapshot, key=lambda x: -x.get("wins", 0))[:25]
        _send(sock, {"type": "LEADERBOARD", "entries": top})

    elif t == "UPDATE_NOTIFY":
        # Broadcast an update notification to all connected clients
        note = msg.get("note", "")
        if note:
            with _lock:
                all_socks = [v["sock"] for v in _clients.values() if v.get("sock")]
            for s in all_socks:
                try:
                    _send(s, {"type": "UPDATE_NOTIFY", "note": note})
                except Exception:
                    pass
            print(f"[notify] {note}", flush=True)


# ── Per-client thread ─────────────────────────────────────────────────────────

_ADMIN_KEY = os.environ.get("FIGHT_ADMIN_KEY", "kevin_dev")


def _client_thread(sock, addr):
    reader = _Reader()
    code   = None
    try:
        # Registration (blocking with short timeout)
        sock.settimeout(12.0)
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                return
            reader.feed(chunk)
            for m in reader.messages():
                if m.get("type") == "ADMIN_NOTIFY":
                    if m.get("key") == _ADMIN_KEY:
                        note = m.get("note", "").strip()
                        if note:
                            _broadcast_update(note)
                    return   # close connection after handling
                if m.get("type") == "HELLO":
                    code = m.get("code", "")
                    name = m.get("username", "Player")
                    with _lock:
                        _clients[code] = {
                            "sock":         sock,
                            "reader":       reader,
                            "username":     name,
                            "in_queue":     False,
                            "matched_with": None,
                        }
                    _send(sock, {"type": "HELLO_OK"})
                    print(f"[+] {name} ({code})  {addr[0]}", flush=True)
                    break
            if code:
                break

        # Main loop (non-blocking)
        sock.settimeout(None)
        sock.setblocking(False)
        while True:
            r, _, _ = select.select([sock], [], [], 60.0)
            if not r:
                continue
            data = sock.recv(65536)
            if not data:
                break
            with _lock:
                rdr = _clients[code]["reader"]
            rdr.feed(data)
            for m in rdr.messages():
                _handle(code, m)

    except Exception:
        pass
    finally:
        if code:
            with _lock:
                partner = _clients.get(code, {}).get("matched_with")
                name    = _clients.get(code, {}).get("username", "?")
                _clients.pop(code, None)
                if code in _queue:
                    _queue.remove(code)
                psock = (_clients[partner]["sock"]
                         if partner and partner in _clients else None)
                if partner and partner in _clients:
                    _clients[partner]["matched_with"] = None
            if psock:
                _send(psock, {"type": "OPP_LEFT"})
            print(f"[-] {name} ({code})", flush=True)
        try:
            sock.close()
        except Exception:
            pass


# ── Entry point ───────────────────────────────────────────────────────────────

def _broadcast_update(note: str):
    """Broadcast an update notification to all currently connected players."""
    with _lock:
        all_socks = [v["sock"] for v in _clients.values()]
        count     = len(all_socks)
    for s in all_socks:
        try:
            _send(s, {"type": "UPDATE_NOTIFY", "note": note})
        except Exception:
            pass
    print(f"[notify] sent to {count} players: {note}", flush=True)


def _stdin_console():
    """Read admin commands from stdin (run in background thread)."""
    print("Admin console ready.  Commands: notify <message>  |  wins  |  quit", flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line.startswith("notify "):
            msg = line[7:].strip()
            if msg:
                _broadcast_update(msg)
        elif line == "wins":
            with _lock:
                snapshot = sorted(_wins.values(), key=lambda x: -x.get("wins", 0))
            for i, e in enumerate(snapshot[:20], 1):
                print(f"  #{i:2d}  {e.get('username','?'):20s}  {e.get('wins',0)} wins", flush=True)
        elif line == "quit":
            os._exit(0)
        else:
            print("Unknown command.", flush=True)


def main():
    _load_wins()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    srv  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", port))
    srv.listen(64)
    print(f"Fight server listening on port {port}  (wins loaded: {len(_wins)})", flush=True)
    threading.Thread(target=_stdin_console, daemon=True).start()
    try:
        while True:
            sock, addr = srv.accept()
            threading.Thread(target=_client_thread,
                             args=(sock, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server stopped.")


if __name__ == "__main__":
    main()
