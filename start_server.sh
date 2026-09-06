#!/bin/bash
# Fight server launcher — runs fight_server.py + bore tunnel
# Run this once to make the server reachable by everyone worldwide.
# Players connect to:  bore.pub:7779

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BORE="/tmp/bore"

BORE_VERSION="v0.5.1"

# Pick the build for this machine — same detection as _download_bore()
# in fight_network.py. Hardcoding one triple drops a binary of the wrong
# architecture at $BORE, which _bore_path() would then hand to the game.
case "$(uname -s)" in
    Darwin)
        case "$(uname -m)" in
            arm64|aarch64) TRIPLE="aarch64-apple-darwin" ;;
            *)             TRIPLE="x86_64-apple-darwin"  ;;
        esac ;;
    Linux)
        case "$(uname -m)" in
            aarch64|arm64) TRIPLE="aarch64-unknown-linux-musl" ;;
            *)             TRIPLE="x86_64-unknown-linux-musl"  ;;
        esac ;;
    *)
        echo "Unsupported platform: $(uname -s) — install bore manually." >&2
        exit 1 ;;
esac

# Download bore if missing, or if the cached copy is for another platform
if [ ! -x "$BORE" ] || ! "$BORE" --version >/dev/null 2>&1; then
    echo "Downloading bore tunnel ($TRIPLE)..."
    curl -sL "https://github.com/ekzhang/bore/releases/download/${BORE_VERSION}/bore-${BORE_VERSION}-${TRIPLE}.tar.gz" \
         | tar xz -C /tmp
    if ! "$BORE" --version >/dev/null 2>&1; then
        echo "bore download failed or won't run on this machine." >&2
        exit 1
    fi
fi

echo "Starting fight server..."
python3 "$SCRIPT_DIR/fight_server.py" &
SERVER_PID=$!

sleep 1

echo "Starting bore tunnel (bore.pub:7779)..."
"$BORE" local 7779 --to bore.pub --port 7779

# If bore exits, kill the server too
kill $SERVER_PID 2>/dev/null
