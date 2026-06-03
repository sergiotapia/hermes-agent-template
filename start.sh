#!/bin/bash
set -e

# Mirror dashboard-ref-only's startup: create every directory hermes expects
# and seed a default config.yaml if the volume is empty. Without these,
# `hermes dashboard` endpoints that hit logs/, sessions/, cron/, etc. can fail
# with opaque errors even though no auth is actually involved.
mkdir -p /data/.hermes/cron /data/.hermes/sessions /data/.hermes/logs \
         /data/.hermes/memories /data/.hermes/skills /data/.hermes/pairing \
         /data/.hermes/hooks /data/.hermes/image_cache /data/.hermes/audio_cache \
         /data/.hermes/workspace /data/.hermes/skins /data/.hermes/plans \
         /data/.hermes/home

if [ ! -f /data/.hermes/config.yaml ] && [ -f /opt/hermes-agent/cli-config.yaml.example ]; then
  cp /opt/hermes-agent/cli-config.yaml.example /data/.hermes/config.yaml
fi

[ ! -f /data/.hermes/.env ] && touch /data/.hermes/.env

for plugin in nabi-care nabi-clinician-tools; do
  if [ -d "/app/plugins/${plugin}" ]; then
    mkdir -p /data/.hermes/plugins
    rm -rf "/data/.hermes/plugins/${plugin}"
    cp -a "/app/plugins/${plugin}" "/data/.hermes/plugins/${plugin}"
  fi
done

python - <<'PY'
from pathlib import Path

import yaml

config_path = Path("/data/.hermes/config.yaml")
config_path.parent.mkdir(parents=True, exist_ok=True)

try:
    loaded = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
except Exception:
    loaded = {}

config = loaded if isinstance(loaded, dict) else {}
required_plugins = ["nabi-care", "nabi-clinician-tools"]

plugins = config.get("plugins")
if not isinstance(plugins, dict):
    plugins = {}

enabled = plugins.get("enabled")
if enabled is True:
    enabled = list(required_plugins)
elif isinstance(enabled, list):
    enabled = [item for item in enabled if item not in required_plugins]
    enabled.extend(required_plugins)
else:
    enabled = list(required_plugins)

plugins["enabled"] = enabled
config["plugins"] = plugins

platform_toolsets = config.get("platform_toolsets")
if not isinstance(platform_toolsets, dict):
    platform_toolsets = {}

api_server_toolsets = platform_toolsets.get("api_server")
if not isinstance(api_server_toolsets, list):
    api_server_toolsets = ["hermes-api-server"]
if "hermes-api-server" not in api_server_toolsets:
    api_server_toolsets.insert(0, "hermes-api-server")

api_server_toolsets = [
    item for item in api_server_toolsets if item not in required_plugins
]
api_server_toolsets.extend(required_plugins)
platform_toolsets["api_server"] = api_server_toolsets
config["platform_toolsets"] = platform_toolsets

config_path.write_text(yaml.safe_dump(config, sort_keys=False, default_flow_style=False))
PY

# Bootstrap OAuth tokens from env var (e.g. xAI Grok SuperGrok).
# Set HERMES_AUTH_JSON_BOOTSTRAP to the contents of a locally-generated
# ~/.hermes/auth.json. Written only once — subsequent token refreshes update
# the file in place on the persistent volume.
if [ ! -f /data/.hermes/auth.json ] && [ -n "${HERMES_AUTH_JSON_BOOTSTRAP}" ]; then
  printf '%s' "${HERMES_AUTH_JSON_BOOTSTRAP}" > /data/.hermes/auth.json
  chmod 600 /data/.hermes/auth.json
fi

# Clear any stale gateway PID file left over from the previous container.
# `hermes gateway` writes /data/.hermes/gateway.pid on start but does not
# remove it on SIGTERM. Since /data is a persistent volume, the file
# survives container restarts and causes every subsequent boot to exit with
# "ERROR gateway.run: PID file race lost to another gateway instance".
# No hermes process can be running at this point (we're pre-exec in a fresh
# container), so removing the file unconditionally is safe.
rm -f /data/.hermes/gateway.pid

exec python /app/server.py
