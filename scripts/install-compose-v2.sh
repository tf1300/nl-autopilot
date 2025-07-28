#!/usr/bin/env bash
set -euo pipefail
VERSION="v2.24.7"
DEST="/usr/local/lib/docker/cli-plugins"
sudo mkdir -p "$DEST"
curl -SL "https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-linux-x86_64" \
  -o "$DEST/docker-compose"
sudo chmod +x "$DEST/docker-compose"
echo "✅ docker compose plugin installed:"
docker compose version