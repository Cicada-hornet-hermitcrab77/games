"""
fight_net_ws.py — WebSocket lobby client.

Drop-in replacement for fight_network.LobbyClient that talks to
fight_server_ws.py instead of the TCP server. Same method names, same
poll() contract, so screens written against LobbyClient work unchanged.

Why it exists: the browser build cannot open raw TCP sockets, so the web
version of online play has to speak WebSocket. On desktop this class is
also the easiest way to test the WebSocket server end to end.

Usage mirrors LobbyClient:
    lc = LobbyClientWS()
    lc.connect_bg("ws://localhost:7780")   # or wss://your-host
    ...poll until lc.connect_done...
    lc.register(code, name); lc.join_queue()
    while lc.match_info is None: lc.poll()
"""

import json
import queue
import threading

DEFAULT_WS_URL = "ws://localhost:7780"


class LobbyClientWS:
    def __init__(self):
        self._ws                  = None
        self._rx                  = queue.Queue()   # decoded dicts from the socket
        self._thread              = None
        self._stop                = threading.Event()
        self.connected            = False
        self.match_info           = None
        self.match_chat_log       = []
        self.friend_msgs          = []
        self.incoming_friend_reqs = []
        self.friend_req_results   = []
        self.pending_msgs         = []
        self.leaderboard          = []
        self.update_notify        = []
        self._conn_done           = False
        self._conn_err            = ""

    # ── Connection ────────────────────────────────────────────────────────────

    def connect_bg(self, url=DEFAULT_WS_URL, timeout=8):
        """Connect on a worker thread. Poll connect_done / connect_error."""
        self._conn_done = False
        self._conn_err  = ""
        self._stop.clear()
        threading.Thread(target=self._run, args=(url, timeout), daemon=True).start()

    def connect(self, url=DEFAULT_WS_URL, timeout=8):
        """Blocking connect, for scripts and tests."""
        self.connect_bg(url, timeout)
        self._wait_connected(timeout + 2)
        if not self.connected:
            raise ConnectionError(self._conn_err or "websocket connect failed")

    def _wait_connected(self, secs):
        import time
        deadline = time.time() + secs
        while time.time() < deadline and not self._conn_done:
            time.sleep(0.01)

    def _run(self, url, timeout):
        try:
            from websockets.sync.client import connect as _ws_connect
        except Exception as e:                      # pragma: no cover
            self._conn_err  = f"websockets package missing: {e}"
            self._conn_done = True
            return
        try:
            ws = _ws_connect(url, open_timeout=timeout, max_size=2 ** 20)
        except Exception as e:
            self._conn_err  = f"{type(e).__name__}: {e}"
            self._conn_done = True
            return
        self._ws        = ws
        self.connected  = True
        self._conn_done = True
        try:
            for raw in ws:
                if self._stop.is_set():
                    break
                try:
                    self._rx.put(json.loads(raw))
                except Exception:
                    continue
        except Exception:
            pass
        finally:
            self.connected = False

    @property
    def connect_done(self) -> bool:
        return self._conn_done

    @property
    def connect_error(self) -> str:
        return self._conn_err

    # ── Sending ───────────────────────────────────────────────────────────────

    def _send(self, obj):
        ws = self._ws
        if not ws:
            return
        try:
            ws.send(json.dumps(obj))
        except Exception:
            self.connected = False

    def register(self, user_code: str, username: str):
        self._send({"type": "HELLO", "code": user_code, "username": username})

    def join_queue(self):
        self._send({"type": "QUEUE_JOIN"})

    def leave_queue(self):
        self._send({"type": "QUEUE_LEAVE"})

    def relay(self, obj):
        self._send({"type": "RELAY", "msg": obj})

    def match_chat(self, text: str):
        self.match_chat_log.append(("You", text))
        self._send({"type": "MATCH_CHAT", "msg": text})

    def friend_chat(self, to_code: str, text: str):
        self._send({"type": "FRIEND_CHAT", "to_code": to_code, "msg": text})

    def lookup_friend(self, code: str):
        self._send({"type": "FRIEND_INFO", "code": code})

    def send_friend_request(self, to_code: str):
        self._send({"type": "FRIEND_REQUEST", "to_code": to_code})

    def respond_friend_request(self, to_code: str, accepted: bool):
        self._send({"type": "FRIEND_RESPONSE", "to_code": to_code,
                    "accepted": accepted})

    def report_result(self, won: bool):
        self._send({"type": "MATCH_RESULT", "won": won})

    def request_leaderboard(self):
        self._send({"type": "LEADERBOARD_REQUEST"})

    # ── Polling ───────────────────────────────────────────────────────────────

    def poll(self):
        """
        Drain received messages and classify them, exactly as
        LobbyClient.poll() does. Returns unwrapped RELAY payloads.
        """
        relays = []
        while True:
            try:
                m = self._rx.get_nowait()
            except queue.Empty:
                break
            t = m.get("type")
            if t == "RELAY":
                relays.append(m.get("msg"))
            elif t == "MATCH_FOUND":
                self.match_info = m
            elif t == "OPP_LEFT":
                self.connected = False
            elif t == "MATCH_CHAT":
                self.match_chat_log.append((m.get("from_name", "Them"),
                                            m.get("msg", "")))
            elif t == "FRIEND_CHAT":
                self.friend_msgs.append((m.get("from_code", ""),
                                         m.get("from_name", "?"),
                                         m.get("msg", "")))
            elif t == "FRIEND_REQUEST":
                self.incoming_friend_reqs.append((m.get("from_code", ""),
                                                  m.get("from_name", "?")))
            elif t == "FRIEND_REQUEST_RESULT":
                self.friend_req_results.append((m.get("from_code", ""),
                                                m.get("from_name", "?"),
                                                m.get("result", "")))
            elif t == "LEADERBOARD":
                self.leaderboard = m.get("entries", [])
            elif t == "UPDATE_NOTIFY":
                self.update_notify.append(m.get("note", ""))
            else:
                self.pending_msgs.append(m)
        return relays

    def take_pending(self):
        out, self.pending_msgs = self.pending_msgs, []
        return out

    def close(self):
        self._stop.set()
        ws, self._ws = self._ws, None
        self.connected = False
        if ws:
            try:
                ws.close()
            except Exception:
                pass
