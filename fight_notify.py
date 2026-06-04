"""
fight_notify.py — automatically sends an update notification to all online players.

Run after git push:
    python3 fight_notify.py
    python3 fight_notify.py "Custom message here"

If no message is given, uses the latest git commit subject line.
Set FIGHT_ADMIN_KEY env var if you changed the server's key (default: kevin_dev).
"""

import socket
import struct
import json
import subprocess
import sys
import os

SERVER_HOST = os.environ.get("FIGHT_SERVER_HOST", "bore.pub")
SERVER_PORT  = int(os.environ.get("FIGHT_SERVER_PORT", "7779"))
ADMIN_KEY    = os.environ.get("FIGHT_ADMIN_KEY", "kevin_dev")


def _get_commit_msg():
    try:
        result = subprocess.run(
            ["git", "log", "--format=%s", "-1"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception:
        return "New update!"


def notify(note: str):
    data = json.dumps({"type": "ADMIN_NOTIFY", "key": ADMIN_KEY, "note": note}).encode()
    with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=8) as s:
        s.sendall(struct.pack(">I", len(data)) + data)
    print(f"Notified players: {note}")


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]).strip() or _get_commit_msg()
    notify(msg)
