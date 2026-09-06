"""
fight_server_ws.py — WebSocket transport for the fight lobby.

Run:  python3 fight_server_ws.py [port]      (default 7780)

Same protocol and same matchmaking as fight_server.py — both are thin
transports over fight_lobby.py. This one exists because browsers cannot
open raw TCP sockets, so the pygbag/web build has to speak WebSocket.

Framing note: the TCP transport length-prefixes each JSON message because
a stream has no message boundaries. WebSocket is already message-oriented,
so frames are plain JSON text with no prefix.

Deploying: a browser page served over HTTPS may only open wss://, not ws://.
Terminate TLS in front of this (Fly.io, Railway, Render and friends do it
for you) and point the client at wss://your-host/.
"""

import asyncio
import json
import os
import sys

import websockets

import fight_lobby as lobby

PORT = 7780


async def _handler(ws):
    """One connected client: pump an outbox, read messages, clean up."""
    outbox = asyncio.Queue()
    code   = None
    name   = "?"

    # lobby.handle() is synchronous and must not block, so sends are queued
    # here and drained by the writer task below.
    def send(obj):
        outbox.put_nowait(obj)

    async def _writer():
        while True:
            obj = await outbox.get()
            await ws.send(json.dumps(obj))

    writer = asyncio.create_task(_writer())
    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if not isinstance(msg, dict):
                continue

            # Admin channel: announce, then drop the connection.
            if msg.get("type") == "ADMIN_NOTIFY":
                if lobby.is_admin_key(msg.get("key")):
                    note = (msg.get("note") or "").strip()
                    if note:
                        n = lobby.broadcast_update(note)
                        print(f"[notify] sent to {n} players: {note}", flush=True)
                return

            if code is None:
                # Nothing is accepted before a HELLO.
                if msg.get("type") != "HELLO":
                    continue
                c    = msg.get("code", "")
                name = msg.get("username", "Player")
                if not lobby.register(c, name, send):
                    return
                code = c
                print(f"[+] {name} ({code})  {ws.remote_address[0]}", flush=True)
                continue

            line = lobby.handle(code, msg)
            if line:
                print(line, flush=True)
    except websockets.ConnectionClosed:
        pass
    except Exception as e:
        print(f"[!] {type(e).__name__}: {e}", flush=True)
    finally:
        writer.cancel()
        if code:
            lobby.disconnect(code)
            print(f"[-] {name} ({code})", flush=True)


async def _console():
    """Admin commands on stdin, without blocking the event loop."""
    print("Admin console ready.  Commands: notify <message>  |  wins  |  quit",
          flush=True)
    loop = asyncio.get_running_loop()
    while True:
        line = (await loop.run_in_executor(None, sys.stdin.readline))
        if not line:
            return
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
                print(f"  #{i:2d}  {e.get('username','?'):20s}  {e.get('wins',0)} wins",
                      flush=True)
        elif line == "quit":
            os._exit(0)
        else:
            print("Unknown command.", flush=True)


def _start_tcp(port: int):
    """
    Also serve the desktop TCP transport from this process. Both transports
    share fight_lobby's state, so a browser player and a desktop player land
    in the same matchmaking queue and can be paired with each other.
    """
    import threading
    import fight_server
    threading.Thread(target=fight_server.serve, args=(port,), daemon=True).start()


async def main():
    lobby.load_wins()
    # First bare argument is the port; PORT env var otherwise, since most
    # hosts assign the port that way.
    positional = [a for a in sys.argv[1:] if not a.startswith("-")]
    port = int(positional[0]) if positional else int(os.environ.get("PORT", PORT))

    # --with-tcp[=PORT] (or FIGHT_TCP_PORT) adds the desktop transport.
    tcp_port = os.environ.get("FIGHT_TCP_PORT")
    for a in sys.argv[1:]:
        if a.startswith("--with-tcp"):
            tcp_port = a.split("=", 1)[1] if "=" in a else (tcp_port or "7779")
    if tcp_port:
        _start_tcp(int(tcp_port))

    async with websockets.serve(_handler, "", port, ping_interval=20,
                                ping_timeout=20, max_size=2 ** 20,
                                compression="deflate"):
        print(f"Fight WebSocket server listening on port {port}  "
              f"(wins loaded: {len(lobby.wins_snapshot())})", flush=True)
        asyncio.create_task(_console())
        await asyncio.Future()   # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")
