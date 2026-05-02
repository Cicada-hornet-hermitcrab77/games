"""
fight_network.py — networking layer for online play.

Architecture
------------
* Direct (host/join): one player hosts (GameServer), the other joins (GameClient).
  Friend code = 10-char alphanumeric encoding of host's public IP + port.
* Matchmaking: both players connect to a central fight_server via LobbyClient.
  The server pairs them, relays game frames, and handles friend / chat messages.
* Messages are length-prefixed JSON frames sent over TCP.
* The host runs the authoritative game simulation; the client sends inputs
  and receives the full game state every frame.
"""
import socket
import select
import json
import struct
import os
import random
import time
import urllib.request

PORT               = 7777
DISCOVER_PORT      = 7778          # UDP LAN discovery
SERVER_PORT        = 7779          # fight_server.py default port
DEFAULT_SERVER_IP  = "bore.pub"    # tunnelled via bore — run start_server.sh
USERDATA_FILE      = os.path.expanduser("~/.fight_userdata.json")

_B36_ID = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_user_code() -> str:
    """Return a random permanent 8-char alphanumeric identity code."""
    return "".join(random.choices(_B36_ID, k=8))


# ── Userdata persistence ──────────────────────────────────────────────────────

def load_userdata():
    data = None
    if os.path.exists(USERDATA_FILE):
        try:
            with open(USERDATA_FILE) as f:
                data = json.load(f)
        except Exception:
            pass
    if data is None:
        data = {"username": "Player", "friends": {}}
    # Auto-generate a permanent identity code on first run
    if "user_code" not in data:
        data["user_code"]  = generate_user_code()
        data["server_ip"]  = data.get("server_ip", "")
        save_userdata(data)
    return data


def save_userdata(data):
    with open(USERDATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Friend codes (10-char alphanumeric) ──────────────────────────────────────

_B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _enc(n, width):
    s = ""
    while n:
        s = _B36[n % 36] + s
        n //= 36
    return s.zfill(width)


def _dec(s):
    n = 0
    for c in s.upper():
        n = n * 36 + _B36.index(c)
    return n


def ip_port_to_code(ip: str, port: int = PORT) -> str:
    """Encode IP + port as a 10-char alphanumeric friend code."""
    parts  = ip.split(".")
    ip_int = (int(parts[0]) << 24 | int(parts[1]) << 16 |
              int(parts[2]) << 8  | int(parts[3]))
    return _enc(ip_int, 7) + _enc(port, 3)


def code_to_ip_port(code: str):
    """Decode a friend code into (ip_str, port_int)."""
    c      = code.upper().replace("-", "").replace(" ", "")
    ip_int = _dec(c[:7])
    port   = _dec(c[7:10])
    ip     = (f"{(ip_int>>24)&0xFF}.{(ip_int>>16)&0xFF}."
              f"{(ip_int>>8)&0xFF}.{ip_int&0xFF}")
    return ip, port


def get_public_ip() -> str:
    """Fetch public IP from ipify; fall back to LAN IP."""
    try:
        return urllib.request.urlopen(
            "https://api.ipify.org", timeout=5).read().decode()
    except Exception:
        return socket.gethostbyname(socket.gethostname())


# ── LAN auto-discovery ────────────────────────────────────────────────────────

class DiscoveryBeacon:
    """
    Listens on UDP DISCOVER_PORT and replies to scan probes while hosting.
    Call poll() each frame; close() when done.
    """
    def __init__(self, tcp_port: int, name: str):
        self._msg  = json.dumps({"type": "FIGHT_HOST",
                                 "port": tcp_port, "name": name}).encode()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._sock.bind(("", DISCOVER_PORT))
        except Exception:
            self._sock = None   # port already in use — silently skip
            return
        self._sock.setblocking(False)

    def poll(self):
        if not self._sock:
            return
        try:
            r, _, _ = select.select([self._sock], [], [], 0)
            if r:
                data, addr = self._sock.recvfrom(256)
                if data == b"FIGHT_DISCOVER":
                    self._sock.sendto(self._msg, addr)
        except Exception:
            pass

    def close(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None


def lan_scan(timeout: float = 1.2) -> list:
    """
    Broadcast a LAN discovery probe and collect host replies.
    Returns list of (ip_str, port_int, host_name) tuples.
    """
    found   = []
    seen    = set()
    sock    = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(0.15)
    try:
        sock.sendto(b"FIGHT_DISCOVER", ("<broadcast>", DISCOVER_PORT))
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                data, addr = sock.recvfrom(512)
                msg = json.loads(data.decode())
                if msg.get("type") == "FIGHT_HOST":
                    key = (addr[0], msg.get("port", PORT))
                    if key not in seen:
                        seen.add(key)
                        found.append((addr[0], msg.get("port", PORT),
                                      msg.get("name", "Host")))
            except socket.timeout:
                pass
            except Exception:
                pass
    finally:
        sock.close()
    return found


# ── Framed TCP messaging ──────────────────────────────────────────────────────

def _send(sock, obj):
    data = json.dumps(obj).encode()
    sock.sendall(struct.pack(">I", len(data)) + data)


class _Reader:
    """Reassembles length-prefixed JSON frames from a TCP byte stream."""
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


# ── Server ────────────────────────────────────────────────────────────────────

class GameServer:
    def __init__(self):
        self._srv      = None
        self._cli      = None
        self._r        = _Reader()
        self.connected = False
        self.opp_name  = "Opponent"
        self.chat_log  = []   # [(sender_label, text), ...]

    def start(self, port=PORT):
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(("", port))
        self._srv.listen(1)
        self._srv.setblocking(False)

    def poll_accept(self) -> bool:
        """Non-blocking check for incoming connection. Returns True once connected."""
        if self.connected:
            return True
        r, _, _ = select.select([self._srv], [], [], 0)
        if r:
            self._cli, _ = self._srv.accept()
            self._cli.setblocking(False)
            self._cli.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.connected = True
        return self.connected

    def send(self, obj):
        if self._cli:
            try:
                _send(self._cli, obj)
            except Exception:
                self.connected = False

    def recv_all(self):
        """Return list of non-CHAT messages; CHAT messages go into chat_log."""
        if not self._cli:
            return []
        r, _, _ = select.select([self._cli], [], [], 0)
        if r:
            try:
                d = self._cli.recv(65536)
                if not d:
                    self.connected = False
                    return []
                self._r.feed(d)
            except Exception:
                self.connected = False
                return []
        out = []
        for m in self._r.messages():
            if m.get("type") == "CHAT":
                self.chat_log.append((self.opp_name, m["msg"]))
            else:
                out.append(m)
        return out

    def send_chat(self, text):
        self.chat_log.append(("You", text))
        self.send({"type": "CHAT", "msg": text})

    def close(self):
        for s in (self._cli, self._srv):
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        self.connected = False


# ── Client ────────────────────────────────────────────────────────────────────

class GameClient:
    def __init__(self):
        self._sock     = None
        self._r        = _Reader()
        self.connected = False
        self.opp_name  = "Host"
        self.chat_log  = []

    def connect(self, ip, port=PORT, timeout=8):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))   # raises on failure
        s.setblocking(False)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._sock     = s
        self.connected = True

    def send(self, obj):
        if self._sock:
            try:
                _send(self._sock, obj)
            except Exception:
                self.connected = False

    def recv_all(self):
        """Return list of non-CHAT messages; CHAT messages go into chat_log."""
        if not self._sock:
            return []
        r, _, _ = select.select([self._sock], [], [], 0)
        if r:
            try:
                d = self._sock.recv(65536)
                if not d:
                    self.connected = False
                    return []
                self._r.feed(d)
            except Exception:
                self.connected = False
                return []
        out = []
        for m in self._r.messages():
            if m.get("type") == "CHAT":
                self.chat_log.append((self.opp_name, m["msg"]))
            else:
                out.append(m)
        return out

    def send_chat(self, text):
        self.chat_log.append(("You", text))
        self.send({"type": "CHAT", "msg": text})

    def close(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        self.connected = False


# ── Lobby / matchmaking client ────────────────────────────────────────────────

class LobbyClient:
    """
    Connects to fight_server.py for matchmaking, relay, and friend chat.

    Typical flow
    ------------
    1.  lc = LobbyClient()
    2.  lc.connect(server_ip)              # raises on failure
    3.  lc.register(user_code, username)   # sends HELLO
    4.  lc.join_queue()                    # sends QUEUE_JOIN
    5.  while lc.match_info is None:
            lc.poll()                      # drives the reader
    6.  # lc.match_info now has opp_name, stage, you_host
    7.  lc.relay({"type": "PICK", ...})    # exchange picks via relay
    8.  # … use in run_relay_fight() via _RelayNet wrapper …
    """

    def __init__(self):
        self._sock                = None
        self._r                   = _Reader()
        self.connected            = False
        self.match_info           = None   # filled when MATCH_FOUND arrives
        self.match_chat_log       = []     # [(sender_label, text)]  in-match chat
        self.friend_msgs          = []     # [(from_code, from_name, text)]
        self.incoming_friend_reqs = []     # [(from_code, from_name)]
        self.friend_req_results   = []     # [(from_code, from_name, result)]
        self.pending_msgs         = []     # non-relay server messages (FRIEND_INFO etc.)

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, host=DEFAULT_SERVER_IP, port=SERVER_PORT, timeout=8):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))   # raises on failure
        s.setblocking(False)
        self._sock     = s
        self.connected = True

    def register(self, user_code: str, username: str):
        self._send({"type": "HELLO", "code": user_code, "username": username})

    # ── Queue / match ─────────────────────────────────────────────────────────

    def join_queue(self):
        self._send({"type": "QUEUE_JOIN"})

    def leave_queue(self):
        self._send({"type": "QUEUE_LEAVE"})

    # ── In-match relay ────────────────────────────────────────────────────────

    def relay(self, obj):
        """Send a game-state or input frame to the matched opponent via the server."""
        self._send({"type": "RELAY", "msg": obj})

    def match_chat(self, text: str):
        self.match_chat_log.append(("You", text))
        self._send({"type": "MATCH_CHAT", "msg": text})

    # ── Friend chat ───────────────────────────────────────────────────────────

    def friend_chat(self, to_code: str, text: str):
        self._send({"type": "FRIEND_CHAT", "to_code": to_code, "msg": text})

    def lookup_friend(self, code: str):
        self._send({"type": "FRIEND_INFO", "code": code})

    def send_friend_request(self, to_code: str):
        self._send({"type": "FRIEND_REQUEST", "to_code": to_code})

    def respond_friend_request(self, to_code: str, accepted: bool):
        self._send({"type": "FRIEND_RESPONSE", "to_code": to_code,
                    "accepted": accepted})

    # ── Polling ───────────────────────────────────────────────────────────────

    def poll(self):
        """
        Drain the socket, classify incoming messages.
        Returns a list of *relay payload dicts* (already unwrapped from RELAY).
        Side effects: populates match_info, match_chat_log, friend_msgs,
        pending_msgs.  Sets connected=False on OPP_LEFT or socket error.
        """
        if not self._sock:
            return []
        r, _, _ = select.select([self._sock], [], [], 0)
        if r:
            try:
                d = self._sock.recv(65536)
                if not d:
                    self.connected = False
                    return []
                self._r.feed(d)
            except Exception:
                self.connected = False
                return []

        relay_out = []
        for m in self._r.messages():
            t = m.get("type")
            if t == "RELAY":
                payload = m.get("msg")
                if payload is not None:
                    relay_out.append(payload)
            elif t == "MATCH_FOUND":
                self.match_info = m
            elif t == "MATCH_CHAT":
                self.match_chat_log.append((m.get("from_name", "?"), m.get("msg", "")))
            elif t == "FRIEND_CHAT":
                self.friend_msgs.append(
                    (m.get("from_code", ""), m.get("from_name", "?"), m.get("msg", "")))
            elif t == "FRIEND_REQUEST":
                self.incoming_friend_reqs.append(
                    (m.get("from_code", ""), m.get("from_name", "?")))
            elif t == "FRIEND_REQUEST_RESULT":
                self.friend_req_results.append(
                    (m.get("from_code", ""), m.get("from_name", "?"),
                     m.get("result", "")))
            elif t == "OPP_LEFT":
                self.connected = False
            else:
                self.pending_msgs.append(m)
        return relay_out

    def take_pending(self):
        """Pop and return all non-relay, non-chat server messages."""
        out = self.pending_msgs[:]
        self.pending_msgs.clear()
        return out

    # ── Misc ──────────────────────────────────────────────────────────────────

    def _send(self, obj):
        if self._sock:
            try:
                _send(self._sock, obj)
            except Exception:
                self.connected = False

    def close(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        self.connected = False
