#!/bin/bash
# Fight server launcher — runs fight_server.py + bore tunnel
# Run this once to make the server reachable by everyone worldwide.
# Players connect to:  bore.pub:7779

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BORE="/tmp/bore"

# Download bore if missing
if [ ! -f "$BORE" ]; then
    echo "Downloading bore tunnel..."
    curl -sL https://github.com/ekzhang/bore/releases/download/v0.5.1/bore-v0.5.1-aarch64-apple-darwin.tar.gz \
         | tar xz -C /tmp
fi

echo "Starting fight server..."
python3 "$SCRIPT_DIR/fight_server.py" &
SERVER_PID=$!

sleep 1

echo "Starting bore tunnel (bore.pub:7779)..."
"$BORE" local 7779 --to bore.pub --port 7779

# If bore exits, kill the server too
kill $SERVER_PID 2>/dev/null
