"""
fight_server.py — TCP transport for the fight lobby.

Run:  python3 fight_server.py [port]    (default 7779)

This is the transport the desktop game uses. The protocol, matchmaking
and leaderboard live in fight_lobby.py, shared with fight_server_ws.py
(the WebSocket transport the browser build needs) so the two cannot
drift apart.

Wire format: each message is a 4-byte big-endian length followed by that
many bytes of JSON — a TCP stream has no message boundaries of its own.
"""

import socket
import select
import json
import struct
import threading
import sys
import os

import fight_lobby as lobby

PORT = 7779

# Re-exported so existing callers and tests keep working.
STAGE_COUNT = lobby.STAGE_COUNT


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


# ── Per-client thread ─────────────────────────────────────────────────────────

def _client_thread(sock, addr):
    reader = _Reader()
    code   = None
    name   = "?"
    try:
        # Registration (blocking with short timeout)
        sock.settimeout(12.0)
        while code is None:
            chunk = sock.recv(4096)
            if not chunk:
                return
            reader.feed(chunk)
            for m in reader.messages():
                if m.get("type") == "ADMIN_NOTIFY":
                    if lobby.is_admin_key(m.get("key")):
                        note = (m.get("note") or "").strip()
                        if note:
                            n = lobby.broadcast_update(note)
                            print(f"[notify] sent to {n} players: {note}", flush=True)
                    return   # close connection after handling
                if m.get("type") == "HELLO":
                    c    = m.get("code", "")
                    name = m.get("username", "Player")
                    if not lobby.register(c, name, lambda obj: _send(sock, obj)):
                        return
                    code = c
                    print(f"[+] {name} ({code})  {addr[0]}", flush=True)
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
            reader.feed(data)
            for m in reader.messages():
                line = lobby.handle(code, m)
                if line:
                    print(line, flush=True)

    except Exception:
        pass
    finally:
        if code:
            lobby.disconnect(code)
            print(f"[-] {name} ({code})", flush=True)
        try:
            sock.close()
        except Exception:
            pass


# ── Entry point ───────────────────────────────────────────────────────────────

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
                n = lobby.broadcast_update(msg)
                print(f"[notify] sent to {n} players: {msg}", flush=True)
        elif line == "wins":
            for i, e in enumerate(lobby.wins_snapshot()[:20], 1):
                print(f"  #{i:2d}  {e.get('username','?'):20s}  {e.get('wins',0)} wins", flush=True)
        elif line == "quit":
            os._exit(0)
        else:
            print("Unknown command.", flush=True)


def serve(port=PORT):
    """
    Accept TCP clients forever. Split out from main() so fight_server_ws.py
    can run this in a thread and serve both transports from one process —
    same fight_lobby state, so desktop and browser players share one queue.
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", port))
    srv.listen(64)
    print(f"Fight server listening on port {port}  "
          f"(wins loaded: {len(lobby.wins_snapshot())})", flush=True)
    while True:
        sock, addr = srv.accept()
        threading.Thread(target=_client_thread,
                         args=(sock, addr), daemon=True).start()


def main():
    lobby.load_wins()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    threading.Thread(target=_stdin_console, daemon=True).start()
    try:
        serve(port)
    except KeyboardInterrupt:
        print("Server stopped.")


if __name__ == "__main__":
    main()
